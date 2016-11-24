from bencoding import encode, decode
from datetime import datetime as dt
from hashlib import sha1
from math import ceil
import os
from enum import Enum


class Status(Enum):
    paused = 1
    downloading = 2
    seeding = 3
    choked = 4


class Torrent(object):

    def __init__(self,
                 torrent_dict,
                 status=Status.paused,
                 root_path=None):

        self._status = status
        if root_path is None:
            self._root_path = os.getcwd()
        else:
            self._root_path = root_path

        # populate torrent variables
        self.parse_torrent_dict(torrent_dict)

    # needs refactored per @squidmin's suggestions, may require
    # changes to existing code since this is such a widely used object.
    def parse_torrent_dict(self, torrent_dict):
        '''Constructs a torrent objects from a decoded torrent
           dictionary, populates the following member variables.
           files [{path: path(str), length: length(int)}...]
           trackers [url(str)...]
           length (int)
           comment (str) (optional)
           created_by (str) (optional)
           creation_date (datetime.datetime) (optional)
           encoding (str) (optional)
           name (str)
           piece_length (int)
           pieces (bytes)
           info_hash (bytes)

        Args:
            torrent_dict (dict): Decoded torrent file, all strings are
            expected to b byte strings and will be decoded into regular
            strings.
        '''
        self.files = []
        self.trackers = []
        self._torrent_dict = torrent_dict
        self.length = 0

        # Populate Optional Fields
        if b'comment' in self._torrent_dict:
            self.comment = self._torrent_dict[b'comment'].decode('utf-8')
        else:
            self.comment = ''
        if b'created by' in self._torrent_dict:
            self.created_by = self._torrent_dict[b'created by'].decode('utf-8')
        else:
            self.created_by = ''
        if b'creation date' in self._torrent_dict:
            creation_date_timestamp = self._torrent_dict[b'creation date']
            self.creation_date = dt.fromtimestamp(creation_date_timestamp)
        else:
            self.creation_date = dt.fromtimestamp(0)
        if b'encoding' in self._torrent_dict:
            self.encoding = self._torrent_dict[b'encoding'].decode('utf-8')
        else:
            self.encoding = ''

        # Populate required fields
        self.name = self._torrent_dict[b'info'][b'name'].decode('utf-8')
        self.piece_length = self._torrent_dict[b'info'][b'piece length']
        self.pieces = self._torrent_dict[b'info'][b'pieces']
        self.info_hash = sha1(encode(self._torrent_dict[b'info'])).digest()

        # Add single file(s)
        if b'length' in self._torrent_dict[b'info']:
            path = self._torrent_dict[b'info'][b'name'].decode('utf-8')
            length = self._torrent_dict[b'info'][b'length']
            self.length = length
            self.files.append({'path': path, 'length': length})
        else:
            for file in self._torrent_dict[b'info'][b'files']:
                path = [path.decode('utf-8') for path in file[b'path']]
                length = file[b'length']
                self.length += length
                self.files.append({'path': os.path.join(*path),
                                   'length': length})

        # add tracker(s)
        if b'announce-list' in self._torrent_dict:
            for trackers in self._torrent_dict[b'announce-list']:
                for tracker in trackers:
                    self.trackers.append(tracker.decode('utf-8'))
        elif b'announce' in self._torrent_dict:
            self.trackers.append(self._torrent_dict[b'announce'])

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in Status.__members__:
            raise ValueError('Unknown status \'%s\'' % value)
        self._status = value

    def __eq__(self, other):
        ''' Torrents are considered equal if their info_hashes are the same'''
        return self.info_hash == other.info_hash

    def __hash__(self):
        return hash(self.info_hash)

    def __str__(self):
        return self.name

    def __enter__(self):
        pass

    def __exit__(self):
        pass


if __name__ == '__main__':
    for file in os.listdir('sample_torrents'):
        with open('sample_torrents/' + file, 'rb') as f:
            torrent_dict = decode(f.read())
            torrent = Torrent(torrent_dict)
            print(ceil(len(torrent.pieces)/20.0))
