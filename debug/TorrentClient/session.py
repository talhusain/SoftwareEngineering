from bencoding import decode
from tracker import Tracker
from util import generate_peer_id
from message import *
import socket
import threading
from struct import pack


class Session(object):
    def __init__(self, peer, torrent):
        self.peer = peer  # of the format tuple(str(ip), int(port))
        self.torrent = torrent
        self.peer_id = generate_peer_id()
        self.observer = None
        self.choked = False
        self.socket_recv = None
        self.socket_send = None
        self.message_queue = MessageQueue()

    def register_observer(self, observer):
        self.observer = observer

    def kickstart(self):
        '''Send the handshake and spawn a thread to start monitoring
        incoming messages.
        '''
        data = self.send_recv_handshake()
        if data:
            threading.Thread(target=self.process_incoming_messages).start()

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
        self.socket_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_recv.settimeout(1)
        try:
            self.socket_recv.connect(self.peer)
        except Exception as e:
            print(self.peer, e)
            self.observer.close_session(self)
            return None
        try:
            self.socket_recv.send(handshake)
            data = self.socket_recv.recv(len(handshake))
            if len(data) == len(handshake):
                return data
        except Exception as e:
            print(self.peer, e)
            self.observer.close_session(self)
            return None

    def process_incoming_messages(self):
        while True:
            try:
                data = self.socket_recv.recv(2**14 + 32)
                for byte in data:
                    self.message_queue.put(byte)
                msg = self.message_queue.get_message()
                if msg:
                    print('got msg %s' % msg.to_bytes())
            except Exception as e:
                print(self.peer, e)

    def send_message(self, message):
        """ Sends a message """
        if not self.socket_send:
            self.socket_send = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
            self.socket_send.settimeout(1)
            try:
                self.socket_send.connect(self.peer)
            except Exception as e:
                print(self.peer, e)
                # self.observer.close_session(self)
                return
        try:
            self.socket_send.send(message.to_bytes())
        except Exception as e:
            print(self.peer, e)

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
