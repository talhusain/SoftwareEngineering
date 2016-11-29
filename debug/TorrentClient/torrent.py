from bencoding import encode, decode
from datetime import datetime
from hashlib import sha1
from math import ceil
from bitstring import BitArray
import os
from enum import Enum
import threading


class Piece(object):
    def __init__(self, length, p_hash, index=None, block_length=16384):
        self.length = length
        self.block_length = block_length
        self.piece = None
        self.bitfield = BitArray(ceil(length / (self.block_length)) * '0b0')
        self.lock = threading.Lock()
        self._in_progress = False
        self._hash = p_hash
        self._index = index

    def complete(self):
        return self.bitfield == BitArray(len(self.bitfield) * '0b1')

    def get_percent_complete(self):
        count = 0
        for b in self.bitfield:
            if b:
                count += 1
        return 100.0 * count / len(self.bitfield)

    def add_block(self, offset, block):
        # we only need the actual space allocated if we are going to add
        # a block
        if not self.piece:
            self.piece = bytes(b'\x00' * self.length)
        self.bitfield[int(offset / self.block_length)] = True
        piece = bytearray(self.piece)
        piece[offset:self.block_length] = bytearray(block)
        self.piece = bytes(piece)
        if self.complete():
            print('Finished downloading piece %s' % self.index)
            if sha1(self.piece).digest() == self.hash:
                print('INFO HASH VERIFIED!!!')
            else:
                print('Error: Expected piece hash does not match')
                print('%s != %s' % (sha1(self.piece).digest(), self.hash))
        print("Percent complete (Piece %s): %s" % (str(self.index),
                                                   str(self.get_percent_complete())))

    @property
    def in_progress(self):
        self.lock.acquire()
        in_progress = self._in_progress
        self.lock.release()
        return in_progress

    @in_progress.setter
    def in_progress(self, value):
        self.lock.acquire()
        self.in_progress = value
        self.lock.release()

    @property
    def index(self):
        return self._index

    @property
    def hash(self):
        return self._hash

    def __str__(self):
        return str(self.piece)

    def __hash__(self):
        return hash(self.piece)


class Status(Enum):
    paused = 1
    downloading = 2
    seeding = 3


class Torrent(object):

    def __init__(self,
                 torrent_dict,
                 info_hash=None,
                 root_path=None,
                 status=Status.paused):

        self._dict = torrent_dict
        self._status = status
        self._info_hash = info_hash
        self._bitfield = BitArray(self.total_pieces * '0b0')
        self._root_path = root_path
        self._piece = []

        for index in range(self.total_pieces):
            piece_hash = bytes([self.pieces[i] for i in range(index * 20, index * 20 + 20)])
            # print('got hash: %s' % piece_hash)
            self._piece += [Piece(self.piece_length, piece_hash, index)]

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in Status.__members__:
            raise ValueError('Unknown status \'%s\'' % value)
        self._status = value

    @property
    def pieces(self):
        return self._dict[b'info'][b'pieces']

    @property
    def piece_length(self):
        return self._dict[b'info'][b'piece length']

    @property
    def name(self):
        return self._dict[b'info'][b'name'].decode('utf-8')

    @property
    def info_hash(self):
        if self._info_hash:
            return self._info_hash
        else:
            return sha1(encode(self._dict[b'info'])).digest()

    @property
    def comment(self):
        if b'comment' in self._dict:
            return self._dict[b'comment'].decode('utf-8')
        return ''

    @property
    def created_by(self):
        if b'created by' in self._dict:
            return self._dict[b'created by'].decode('utf-8')
        return ''

    @property
    def creation_date(self):
        if b'creation date' in self._dict:
            return datetime.fromtimestamp(self._dict[b'creation date'])
        else:
            return datetime.fromtimestamp(0)

    @property
    def encoding(self):
        if b'encoding' in self._dict:
            return self._dict[b'encoding'].decode('utf-8')
        return ''

    @property
    def files(self):
        files = []
        if b'length' in self._dict[b'info']:
            path = self._dict[b'info'][b'name'].decode('utf-8')
            length = self._dict[b'info'][b'length']
            files.append({'path': path, 'length': length})
        else:
            for file in self._dict[b'info'][b'files']:
                path = [path.decode('utf-8') for path in file[b'path']]
                length = file[b'length']
                files.append({'path': os.path.join(*path),
                              'length': length})
        return files

    @property
    def length(self):
        length = 0
        for file in self.files:
            length += file['length']
        return length

    @property
    def trackers(self):
        ret = []
        if b'announce-list' in self._dict:
            for trackers in self._dict[b'announce-list']:
                for tracker in trackers:
                    ret.append(tracker.decode('utf-8'))
        elif b'announce' in self._dict:
            ret.append(self._dict[b'announce'])
        return ret

    @property
    def total_pieces(self):
        return int(len(self.pieces) / 20)

    @property
    def bitfield(self):
        return self._bitfield

    @property
    def piece(self):
        return self._piece

    def get_percent_complete(self):
        count = 0
        for b in self.bitfield:
            if b:
                count += 1
        return 100.0 * count / len(self.bitfield)

    def complete(self):
        return self.bitfield == BitArray(len(self.bitfield) * '0b1')

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
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    for file in os.listdir('sample_torrents'):
        with open('sample_torrents/' + file, 'rb') as f:
            torrent_dict = decode(f.read())
            torrent = Torrent(torrent_dict)
            pp.pprint('name: %s' % torrent.name)
            pp.pprint('info_hash: %s' % torrent.info_hash)
            pp.pprint('comment: %s' % torrent.comment)
            pp.pprint('status: %s' % torrent.status)
            pp.pprint('pieces: %s' % torrent.pieces)
            pp.pprint('piece_length: %s' % torrent.piece_length)
            pp.pprint('created_by: %s' % torrent.created_by)
            pp.pprint('creation_date: %s' % torrent.creation_date)
            pp.pprint('encoding: %s' % torrent.encoding)
            pp.pprint('files: %s' % torrent.files)
            pp.pprint('length: %s' % torrent.length)
            pp.pprint('trackers: %s' % torrent.trackers)
            pp.pprint('total_pieces: %s' % torrent.total_pieces)
            pp.pprint('bitfield: %s' % torrent.bitfield)
        print()
