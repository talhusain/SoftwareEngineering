from bencoding import decode
from tracker import Tracker
from util import generate_peer_id
from message import *
import socket
import threading
from struct import pack
import time
from bitstring import BitArray
from math import ceil

class Piece(object):
    def __init__(self, index, length, block_length=16384):
        self.index = index
        self.length = length
        self.block_length = block_length
        self.piece = bytes(b'\x00' * length)
        self.bitfield = BitArray(ceil(length/(self.block_length)) * '0b0')

    def complete(self):
        return self.bitfield == BitArray(len(self.bitfield) * '0b1')

    def add_block(self, index, block):
        self.bitfield[index] = True
        self.piece[index:self.block_length] = block

    def __str__(self):
        return str(self.piece)



class Session(threading.Thread):
    def __init__(self, peer, torrent, observer=None):
        self.peer = peer  # of the format tuple(str(ip), int(port))
        self.torrent = torrent
        self.active_requests = 0
        self.bitfield = None  # bitfield the peer maintains
        self.peer_id = generate_peer_id()
        self.observer = None
        self.choked = True
        self.recv_socket = None
        self.recv_thread = None
        self.send_socket = None
        self.socket = None
        self.alive = True
        self.current_piece = None
        self.lock = threading.Lock()
        self.message_queue = MessageQueue()

        threading.Thread.__init__(self)

        # go ahead and allow registering the observer now if passed
        if observer:
            self.observer = observer

    def register_observer(self, observer):
        self.observer = observer

    def run(self):
        '''Send the handshake and spawn a thread to start monitoring
        incoming messages, also spawn a thread to send the keep-alive
        message every minute.
        '''
        # if port0 or handshake fails close the thread
        if self.peer[1] == 0 or not self.send_recv_handshake():
            self.observer.close_session(self)
            return

        # spawn thread to start receiving messages and queueing them up
        # for processing
        incoming_t = threading.Thread(target=self.receive_incoming)
        incoming_t.daemon = True
        incoming_t.start()

        # spawn thread to start processing the incoming messages
        process_inc_t = threading.Thread(target=self.process_incoming_messages)
        process_inc_t.daemon = True
        process_inc_t.start()

        # go ahead and send them our empty bitfield message to let them know
        # that we have no pieces
        self.send_message(Message.get_message('bitfield', bitfield=self.torrent.bitfield.tobytes()))

        # send our interested message to let it know we would like
        #to be unchoked
        self.send_message(Message.get_message('interested'))

        # schedule the keep-alive, in the future this will need
        # refactored to close the session on failure, but for now
        # brute force is good enough
        keepalive = Message.get_message('keep-alive')
        ka_t = threading.Timer(60, self.send_message, args=(keepalive,))
        ka_t.daemon = True
        ka_t.start()

        # schedule the piece requests
        req_t = threading.Timer(5, self.request_pieces)
        req_t.daemon = True
        req_t.start()

        while self.alive:
            continue


    def generate_handshake(self):
        """ Returns a handshake. """
        handshake = pack('!1s', bytearray(chr(19), 'utf8'))
        handshake += pack('!19s', bytearray('BitTorrent protocol', 'utf-8'))
        handshake += pack('!q', 0)
        handshake += pack('!20s', self.torrent.info_hash)
        handshake += pack('!20s', bytearray(self.peer_id, 'utf8'))
        return handshake

    def send_recv_handshake(self):
        """ Establishes the socket connection and sends the handshake"""
        handshake = self.generate_handshake()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1)
        try:
            self.socket.connect(self.peer)
        except Exception as e:
            if str(e) != 'timed out':
                print(self.peer, e)
            return None
        try:
            self.socket.send(handshake)
            data = self.socket.recv(len(handshake))
            if len(data) == len(handshake):
                print('establish connection with %s' % self.peer[0])
                return data
        except Exception as e:
            if str(e) != 'timed out':
                print(self.peer, e)
            return None

    def receive_incoming(self):
        while True:
            try:
                self.lock.acquire()
                data = self.socket.recv(2**15)
                self.lock.release()
                for byte in data:
                    self.message_queue.put(byte)
            except Exception as e:
                self.lock.release()
                if str(e) == 'timed out':
                    continue
                self.observer.close_session(self)
                self.alive = False
                break

    def process_incoming_messages(self):
        while True:
            msg = self.message_queue.get_message()
            if msg:
                print('got message %s' % (msg))
            else:
                continue
            if isinstance(msg, UnChoke):
                self.choked = False
            elif isinstance(msg, Choke):
                self.choked = True
                self.send_message(Message.get_message('interested'))
            elif isinstance(msg, Have):
                if not self.bitfield:
                    self.bitfield = self.torrent.bitfield  # temporary hack for 0 bitfield
                self.bitfield[msg.index] = True
            elif isinstance(msg, BitField):
                # print(bytes(msg.bitfield))
                self.bitfield = BitArray(bytes(msg.bitfield))
                # print('got bitfield %s' % self.bitfield.bin)
            elif isinstance(msg, Interested):
                self.send_message(Message.get_message('unchoke'))
            elif isinstance(msg, Piece):
                if self.active_requests > 0:
                    self.active_requests -= 1
                print(msg.block)
                self.current_piece.add_block(msg.begin, msg.block)

    def request_pieces(self):
        # select a piece of we aren't already working on one
        if not self.current_piece:
            for index in range(len(self.bitfield)):
                if (self.torrent.bitfield[index] == False and
                    self.bitfield[index] == True):
                    self.current_piece = Piece(index,
                                               self.torrent.piece_length)
                    break
        # if choked go ahead and return
        if self.choked == True:
            return
        # if not choked go ahead and start getting a block of our piece
        if self.current_piece:
            for offset in range(len(self.current_piece.bitfield)):
                if (self.current_piece.bitfield[offset] == False and
                    self.active_requests < 3):
                    req = Message.get_message('request',
                                              self.current_piece.index,
                                              offset * (2**14),
                                              2**14)
                    threading.Thread(target=self.send_message,
                                     args=(req,)).start()
                    self.active_requests += 1




    def send_message(self, message):
        """ Sends a message """
        # messages that can be sent while choked
        if self.choked and not (isinstance(message, Interested) or
                                isinstance(message, KeepAlive) or
                                isinstance(message, BitField) or
                                isinstance(message, UnChoke)):
            return
        # print('sending message %s - %s to %s' % (message, message.to_bytes(), self.peer[0]))
        try:
            self.lock.acquire()
            print('sending message %s to %s...' % (message, self.peer[0]))
            self.socket.sendall(message.to_bytes())
            self.lock.release()
        except Exception as e:
            self.lock.release()
            if str(e) != 'timed out':
                print(self.peer, e)
                print(('Error getting incoming message from %s: %s' %
                      (self.peer[0], e)))
                self.observer.close_session(self)
                self.alive = False

    def __eq__(self, other):
        return (self.torrent == other.torrent and
                self.peer == other.peer)

    def __hash__(self):
        return hash(self.peer)


if __name__ == '__main__':
    from os import listdir
    from torrent import Torrent
    for file in listdir('sample_torrents'):
        with open('sample_torrents/' + file, 'rb') as f:
            t = Torrent(decode(f.read()))
            print("processing: ", t)
            for tracker in t.trackers:
                trk = Tracker(tracker, t, generate_peer_id())
                print(trk)
                peers = trk.get_peers()
                for peer in peers:
                    session = Session(peer, t, None)
                    session.send_recv_handshake()
                    session.send_message(Message.get_message('keep-alive'))
