import socket
from bencoding import decode
import requests
from struct import unpack


class Tracker(object):
    def __init__(self, url, torrent, peer_id):
        self.url = url
        self.torrent = torrent
        self.peer_id = peer_id
        self.peers = []

    def make_tracker_request(self):
        """ Given a torrent info, and tracker_url, returns the tracker
        response. """
        payload = {'info_hash': self.torrent.info_hash,
                   'peer_id': self.peer_id,
                   'length': self.torrent.length,
                   'uploaded': 0,
                   'downloaded': 0,
                   'compact': 1}

        # switch to http protocol if necessary
        if self.url[:3] == 'udp':
            self.url = 'http' + self.url[3:]

        # Send the request
        r = requests.get(self.url, params=payload, timeout=.5, verify=False)
        return decode(r.content)

    def decode_expanded_peers(self, peers):
        """ Return a list of IPs and ports, given an expanded list of
        peers, from a tracker response. """
        return [(p["ip"], p["port"]) for p in peers]

    def decode_binary_peers(self, peers):
        """ Return a list of IPs and ports, given a binary list of
        peers, from a tracker response. """
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)]
        return [(socket.inet_ntoa(p[:4]), self.decode_port(p[4:]))
                for p in peers]

    def get_peers(self):
        """ Update tracker peers, each call adds new peers. """
        try:
            request = self.make_tracker_request()
        except Exception:
            return self.peers
        peers = request[b'peers']
        if type(peers) == bytes:
            self.peers = list(set(self.peers) |
                              set(self.decode_binary_peers(peers)))
        elif type(peers) == list:
            self.peers = list(set(self.peers) |
                              set(self.decode_expanded_peers(peers)))
        return self.peers

    def decode_port(self, port):
        """ Given a big-endian encoded port, returns the numerical
        port. """
        return unpack(">H", port)[0]

    def __str__(self):
        return self.url
