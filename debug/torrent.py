"""
FILE: torrent.py
CLASS PROVIDED: Torrent
"""

import bencoding.bencode
import requests
import hashlib
import peer
import time
import os
import random
import json
from string import ascii_letters, digits

class TorrentClient(object):
    # def

class Torrent(object):

    def __init__(self, torrent_path, directory='', port=55308, download_all=False, visualizer=None):
        torrent_dict = bencode.decode(torrent_path)
        self.torrent_dict = torrent_dict   # I (tentatively) preserved the way @jefflovejapan handled the torrent dictionary in his implementation.
        self.peer_dict = {}
        self.peer_ips = []
        self.port = port
        self.download_all = download_all  # Presumably a boolean indicating whether to download all files associated with a multifile torrent?
        self.r = None    # Tracker requests?
        self.tracker_response = None
        self.hash_string = None    # SHA-1 ?
        self.queued_requests = []

        file_list = []

    @property
    def piece_length(self):
        pass

    @property
    def num_pieces(self):
        pass

    @property
    def length(self):
        pass

    @property
    def last_piece_length(self):
        pass

    @property
    def last_piece(self):
        pass

    def build_payload(self):
        '''
        Builds the payload that will be sent in tracker_request
        '''
        pass

    def tracker_request(self):
        '''
        Sends the initial request to the tracker, compiling list of all peers
        announcing to the tracker
        '''
        pass

    def get_peer_ips(self):
        '''
        Generates list of peer IPs from tracker response. Note: not all of
        these IPs might be good, which is why we only init peer objects for
        the subset that respond to handshake
        '''
        pass


    def handshake_peers(self):
        pass

    def initpeer(self, sock):
        '''
        Creates a new peer object for a valid socket and adds it to reactor's
        listen list
        '''
        pass

    def add_peer(self, socket):
        pass

    def kill_peer(self, tpeer):
        pass

    def set_socket(self, socket):
        pass

    def __enter__(self):
        pass

    def __exit__(self):
        pass
