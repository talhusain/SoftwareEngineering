from bencoding import decode
from tracker import Tracker
from message import *
import socket
from struct import pack
from enum import Enum
import random
from string import ascii_letters, digits


class Status(Enum):
    paused = 1
    downloading = 2
    seeding = 3


class Session(object):
    def __init__(self, torrent, location):
        self.peers = []     # [(ip, port), ...]
        self.torrent = torrent
        self.location = location
        self.status = Status.downloading
        self.peer_id = self.generate_peer_id()

    def start(self):
        self.status = Status.downloading

    def pause(self):
        self.status = Status.paused

    def resume(self):
        self.status = Status.downloading

    def cancel(self):
        pass

    def generate_peer_id(self):
        """ Returns a 20-byte peer id. """
        CLIENT_ID = "ST"
        CLIENT_VERSION = "0001"
        ALPHANUM = ascii_letters + digits
        random_string = ''.join(random.sample(ALPHANUM, 13))
        return "-" + CLIENT_ID + CLIENT_VERSION + random_string

    def generate_handshake(self):
        """ Returns a handshake. """
        handshake = pack('!1s', bytearray(chr(19), 'utf8'))
        handshake += pack('!19s', bytearray('BitTorrent protocol', 'utf-8'))
        handshake += pack('!q', 0)
        handshake += pack('!20s', self.torrent.info_hash)
        handshake += pack('!20s', bytearray(self.peer_id, 'utf8'))
        return handshake

    def send_recv_handshake(self, peer):
        """ Sends a handshake, returns the data we get back. """
        handshake = self.generate_handshake()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(peer)
        except Exception as e:
            print(peer, e)
            return None
        try:
            s.send(handshake)
            data = s.recv(len(handshake))
            s.close()
            return data
        except Exception as e:
            print(peer, e)
            return None

    def send_message(self, peer, message):
        """ Sends a message"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(peer)
        except Exception as e:
            print(peer, e)
            return None
        try:
            s.send(message.to_bytes())
            s.close()
        except Exception as e:
            print(peer, e)
            return None


if __name__ == '__main__':
    from os import listdir
    from torrent import Torrent
    for file in listdir('sample_torrents'):
        with open('sample_torrents/' + file, 'rb') as f:
            t = Torrent(decode(f.read()))
            print("processing: ", t)
            session = Session(t, None)
            for tracker in t.trackers:
                trk = Tracker(tracker, t, session.generate_peer_id())
                print(trk)
                peers = trk.get_peers()
                for peer in peers:
                    session.send_recv_handshake(peer)
