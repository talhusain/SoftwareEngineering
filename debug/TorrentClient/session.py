import socket
from struct import pack, unpack
from bencoding import decode
from enum import Enum
from os import urandom
from urllib.parse import urlencode
from urllib.request import urlopen

CLIENT_NAME = b"slothtorrent"
CLIENT_ID = b"sT"
CLIENT_VERSION = b"0001"


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
        random_string = urandom(12)
        return b"-" + CLIENT_ID + CLIENT_VERSION + b"-" + random_string

    def make_tracker_request(self, tracker_url):
        """ Given a torrent info, and tracker_url, returns the tracker
        response. """
        # Generate a tracker GET request.
        payload = {"info_hash" : self.torrent.info_hash,
                "peer_id" : self.peer_id,
                "port" : 6881,
                "uploaded" : 0,
                "downloaded" : 0,
                "left" : 1000,
                "compact" : 1}

        # switch to http protocol if necessary
        if tracker_url[:3] == 'udp':
            tracker_url = 'http' + tracker_url[3:]
        payload = urlencode(payload)

        # Send the request
        response = urlopen(tracker_url + "?" + payload, timeout=.25).read()
        print(response)
        return decode(response)

    def decode_expanded_peers(self, peers):
        """ Return a list of IPs and ports, given an expanded list of
        peers, from a tracker response. """
        return [(p["ip"], p["port"]) for p in peers]

    def decode_binary_peers(self, peers):
        """ Return a list of IPs and ports, given a binary list of
        peers, from a tracker response. """
        peers = [peers[i:i+6] for i in range(0, len(peers), 6)]
        return [(socket.inet_ntoa(p[:4]), self.decode_port(p[4:]))
                for p in peers]

    def get_peers(self, peers):
        """ Dispatches peer list to decode binary or expanded peer
        list. """
        print('decoding peers:')
        print(peers)
        if type(peers) == bytes:
            print('type bytes')
            return self.decode_binary_peers(peers)
        elif type(peers) == list:
            return self.decode_expanded_peers(peers)

    def decode_port(self, port):
        """ Given a big-endian encoded port, returns the numerical
        port. """
        return unpack(">H", port)[0]

    def generate_handshake(info_hash, peer_id):
        """ Returns a handshake. """
        protocol_id = "BitTorrent protocol"
        len_id = str(len(protocol_id))
        reserved = "00000000"
        return len_id + protocol_id + reserved + info_hash + peer_id

    def send_recv_handshake(handshake, host, port):
        """ Sends a handshake, returns the data we get back. """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(handshake)
        data = s.recv(len(handshake))
        s.close()
        return data

if __name__ == '__main__':
    from os import listdir
    from torrent import Torrent
    for file in listdir('sample_torrents'):
        with open('sample_torrents/' + file, 'rb') as f:
            t = Torrent(decode(f.read()))
            print(t)
            session = Session(t, None)
            for tracker in t.trackers:
                try:
                    response = session.make_tracker_request(tracker)
                    print(session.get_peers(response[b'peers']))
                except:
                    pass