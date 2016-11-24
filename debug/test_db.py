import unittest
from db import Database
import psycopg2
import datetime
from torrent import Torrent

class TestGetTorrent(unittest.TestCase):

    def setUp(self):
        
        # Connect to database and instantiate a cursor
        self.db = Database('settings.conf')
        self.cursor = self.db._connection.cursor()
        
        # Data to test db.get_torrent()
        self.fake_info_hash = b'asdfasdf'
        self.fake_piece_length = '5'
        self.fake_comment = self.fake_info_hash
        self.fake_name = 'GOATS'
        self.fake_created_by = self.fake_info_hash
        self.fake_creation_date = datetime.datetime.now()
        self.fake_pieces = self.fake_info_hash
        self.fake_info = { b'name': self.fake_info_hash,
                           b'piece length': self.fake_piece_length,
                           b'pieces': self.fake_info_hash,
                           b'md5sum': self.fake_info_hash }
        self.fake_files = [ { b'length': self.fake_piece_length },
                            { b'path': self.fake_comment } ]
        
        # Populate torrent dict
        self.torrent_dict = { b'info_hash': self.fake_info_hash,
                              b'info': self.fake_info,
                              b'files': self.fake_files,
                              b'name': self.fake_name,
                              b'comment': self.fake_comment,
                              b'created_by': self.fake_created_by,
                              b'creation_date': self.fake_creation_date,
                              b'piece length': self.fake_piece_length,
                              b'pieces': self.fake_pieces }
        
        # Insert test data into the torrents table
        try:
            self.cursor.execute( ("INSERT INTO torrents VALUES "
                                  "(%s, %s, %s, %s, %s, %s, %s) "
                                  "ON CONFLICT (info_hash) DO NOTHING"),
                                  (self.fake_info_hash,
                                   self.fake_name,
                                   self.fake_comment,
                                   self.fake_created_by,
                                   self.fake_creation_date,
                                   self.fake_piece_length,
                                   self.fake_pieces) )
        except psycopg2.ProgrammingError as e:
            print(e)
        cursor.close()

    def test_get_torrent(self):
        """ Test the get_torrent() function. """

        ret = self.db.get_torrent(self.fake_info_hash)
        self.assertEqual(ret, Torrent(self.torrent_dict))

    def test_add_plugin(self):
        url_1 = 'https://github.com/BadStreff/slothtorrent_yts'
        ret = self.db.add_plugin(url)
        self.assertEqual(ret, True)

    def tearDown(self):
        print("wow")

if __name__ == '__main__':
    unittest.main()