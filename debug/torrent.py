"""
FILE: torrent.py
CLASS PROVIDED: Torrent
"""
from bencoding.bencode import encode, decode
from datetime import datetime as dt
from hashlib import sha1
import os


class Torrent(object):

    def __init__(self, torrent_dict):
        """Constructs a torrent objects from a decoded torrent
           dictionary.

        Args:
            torrent_dict (dict): Decoded torrent file, all strings are
            expected to b byte strings and will be decoded into regular
            strings.
        """
        self.files = []
        self.trackers = []
        self._torrent_dict = torrent_dict

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
            self.files.append({'path': path, 'length': length})
        else:
            for file in self._torrent_dict[b'info'][b'files']:
                path = [path.decode('utf-8') for path in file[b'path']]
                self.files.append({'path': os.path.join(*path),
                                   'length': file[b'length']})

        # add tracker(s)
        if b'announce' in self._torrent_dict:
            self.trackers.append(self._torrent_dict[b'announce'])
        if b'announce-list' in self._torrent_dict:
            for trackers in self._torrent_dict[b'announce-list']:
                for tracker in trackers:
                    self.trackers.append(tracker.decode('utf-8'))

    def get_comment(self):
        return self.comment

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
            print(torrent)
