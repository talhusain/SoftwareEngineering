from bencoding import decode
from tracker import Tracker
from util import generate_peer_id
from message import *
import socket
import threading
from struct import pack
from bitstring import BitArray
import random


class Session(threading.Thread):
    def __init__(self, peer, torrent, observer=None):
        self.peer = peer  # of the format tuple(str(ip), int(port))
        self.torrent = torrent
        self.requesting_block = False
        self.bitfield = None  # bitfield the peer maintains
        self.peer_id = generate_peer_id()
        self.observer = observer
        self.choked = True
        self.socket = None
        self.alive = True
        self.interested = False
        self.current_piece = None
        self.lock = threading.Lock()
        self.message_queue = MessageQueue()

        threading.Thread.__init__(self)

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

        # spawn thread to start receiving messages
        threading.Thread(target=self.receive_incoming).start()

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
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(True)
        try:
            self.socket.connect(self.peer)
        except Exception:
            return None
        try:
            self.socket.send(handshake)
            data = self.socket.recv(len(handshake))
            if len(data) == len(handshake):
                print('[%s] Established Connection' % self.peer[0])
                return data
        except Exception:
            return None

    def receive_incoming(self):
        while self.alive:
            try:
                self.lock.acquire()
                data = self.socket.recv(2**14)
                self.lock.release()
                if data:
                    for byte in data:
                        self.message_queue.put(byte)
                    self.process_incoming()
            except Exception as e:
                self.lock.release()
                print('[%s] receive_incoming() - %s' % (self.peer[0], e))
                self.observer.close_session(self)
                self.alive = False

    def process_incoming(self):
        while not self.message_queue.empty():
            msg = self.message_queue.get_message()
            if not msg:
                break
            else:
                print('[%s] Received Message %s' % (self.peer[0], msg))
            if isinstance(msg, UnChoke):
                if self.choked:  # ignore duplicate unchokes
                    self.choked = False
                    self.request_piece()
            elif isinstance(msg, Choke):
                self.choked = True
                self.requesting_block = False
                self.send_message(Message.get_message('interested'))
            elif isinstance(msg, Have):
                if not self.bitfield:
                    self.bitfield = BitArray(self.torrent.total_pieces * '0b0')
                self.bitfield[msg.index] = True
                if not self.interested:
                    self.interested = True
                    self.send_message(Message.get_message('interested'))
            elif isinstance(msg, BitField):
                self.bitfield = BitArray(bytes(msg.bitfield))
                if not self.interested:
                    self.interested = True
                    self.send_message(Message.get_message('interested'))
            elif isinstance(msg, Piece):
                self.requesting_block = False
                self.current_piece.add_block(int(msg.begin), msg.block)
                if self.current_piece.complete():
                    print('FINISHED DOWNLOADING A PIECE')
                    print('Total Progress: %s' %
                          self.torrent.get_percent_complete())
                    self.torrent.bitfield[self.current_piece.index] = True
                    self.current_piece = None
                if self.torrent.complete():
                    print('FINISHED DOWNLOADING ENTIRE TORRENT')
                    self.alive = False
                self.request_piece()

    def request_piece(self):
        if (not self.bitfield) or self.requesting_block:
            return
        if not self.current_piece:
            r = list(range(len(self.bitfield)))
            random.shuffle(r)
            for index in r:
                if (self.bitfield[index] and
                        not self.torrent.bitfield[index]):
                    self.current_piece = self.torrent.piece[index]
                    break
        r = list(range(len(self.current_piece.bitfield)))
        random.shuffle(r)
        for offset in r:
            if not self.current_piece.bitfield[offset]:
                req = Message.get_message('request',
                                          self.current_piece.index,
                                          offset * (2**14),
                                          2**14)
                self.send_message(req)
                self.requesting_block = True
                return

    def send_message(self, message):
        """ Sends a message """
        if self.choked and isinstance(message, Request):
            return
        try:
            print('[%s] Sent Message %s' % (self.peer[0], message, ))
            self.lock.acquire()
            self.socket.send(message.to_bytes())
            self.lock.release()
        except Exception as e:
            self.lock.release()
            print('[%s] send_message() - %s' % (self.peer[0], e))
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
