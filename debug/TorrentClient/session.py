from bencoding import decode
from tracker import Tracker
from util import generate_peer_id
from message import *
import socket
import threading
from struct import pack
import time


class Session(threading.Thread):
    def __init__(self, peer, torrent, observer=None):
        self.peer = peer  # of the format tuple(str(ip), int(port))
        self.torrent = torrent
        self.peer_id = generate_peer_id()
        self.observer = None
        self.choked = True
        self.recv_socket = None
        self.recv_thread = None
        self.send_socket = None
        self.socket = None
        self.alive = True
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
        # if handshake fails close the thread
        if not self.send_recv_handshake():
            self.observer.close_session(self)
            return
        # start processing messages from the peer if the handshake
        # was successful, this thread is a daemon so it can be
        # closed when the session ends
        incoming_t = threading.Thread(target=self.process_incoming_messages)
        # print('started incoming thread %s' % incoming_t)
        incoming_t.daemon = True
        incoming_t.start()
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

    def process_incoming_messages(self):
        loop = True
        self.have = []
        while loop:
            try:
                self.lock.acquire()
                data = self.socket.recv(2**17)
                self.lock.release()
                for byte in data:
                    # print('%s sent byte %s' % (self.peer[0], byte))
                    self.message_queue.put(byte)
                msg = self.message_queue.get_message()
                if msg:
                    print('got message %s - %s from %s' % (msg, msg.to_bytes(), self.peer[0]))
                if isinstance(msg, UnChoke):
                    self.choked = False
                    if len(self.have) > 0:
                        self.send_message(Message.get_message('request', self.have[0].index, 0, 16384))
                elif isinstance(msg, Choke):
                    self.choked = True
                    self.send_message(Message.get_message('interested'))
                elif isinstance(msg, Have):
                    self.have += [msg]
                elif isinstance(msg, BitField):
                    self.send_message(msg)
            except Exception as e:
                self.lock.release()
                # ignore time outs
                if str(e) == 'timed out':
                    continue
                print(('Error getting incoming message from %s: %s' %
                      (self.peer[0], e)))
                self.observer.close_session(self)
                self.alive = False
                loop = False

    def send_message(self, message):
        """ Sends a message """
        # We should only send interested and keep-alive messages if
        # choked
        if self.choked and not (isinstance(message, Interested) or
                                isinstance(message, KeepAlive) or
                                isinstance(message, BitField)):
            return
        print('sending message %s - %s to %s' % (message, message.to_bytes(), self.peer[0]))
        try:
            self.lock.acquire()
            self.socket.send(message.to_bytes())
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
