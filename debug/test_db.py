import unittest
import datetime
import os
import shutil
from db import Database
from torrent import Torrent
import psycopg2
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class TestGetTorrent(unittest.TestCase):

    def setUp(self):
        
        normal_settings_file = 'settings.conf'
        test_settings_file = 'test_settings.conf'
        normal_db_config = """
                           [DATABASE]
                           username = postgres
                           password = Um]Y3{R;5YnYp#2`
                           db = slothtorrent
                           ip = 52.55.147.141
                           port = 5432

                           [PLUGINS]
                           directory=/Users/Shared
                           """
        test_db_config = """
                         [DATABASE]
                         username = postgres
                         password = Um]Y3{R;5YnYp#2`
                         db = test_slothtorrent
                         ip = 52.55.147.141
                         port = 5432

                         [PLUGINS]
                         directory=/Users/Shared
                         """
        
        with open(test_settings_file, 'w') as file:
            file.write(test_db_config)
        
        self.db = Database(normal_settings_file)

        self.connection = self.db.get_connection()
        self.cursor = self.connection.cursor()

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        self.cursor.execute("SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = %s)", ('test_slothtorrent',))
        if not self.cursor.fetchone()[0]:
            try:
                self.cursor.execute("CREATE DATABASE test_slothtorrent")
            except psycopg2.ProgrammingError as e:
                print(e)
        self.cursor.close()
        self.connection.close()

        self.db = Database(test_settings_file)

        self.connection = self.db.get_connection()
        self.cursor = self.connection.cursor()

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS plugins"
                                "(url TEXT PRIMARY KEY, last_run TIMESTAMP)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS torrents "
                                "(info_hash BYTEA PRIMARY KEY,"
                                "name TEXT,"
                                "comment TEXT,"
                                "created_by TEXT,"
                                "creation_time TIMESTAMP,"
                                "piece_length INT,"
                                "pieces BYTEA,"
                                "provider TEXT REFERENCES plugins (url))")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS announcers "
                                "(url TEXT,"
                                "info_hash BYTEA REFERENCES torrents (info_hash),"
                                "PRIMARY KEY (url, info_hash))")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS torrent_files "
                                "(file_path TEXT,"
                                "length TEXT,"
                                "info_hash BYTEA REFERENCES torrents (info_hash),"
                                "PRIMARY KEY (file_path, info_hash))")
        except psycopg2.ProgrammingError as e:
            print(e)
        
        # Populate test torrent dict
        self.torrent_dict = { b'info_hash': b'asdfasdf',
                              b'info': { 
                                         b'name': b'slooooothtorrent',
                                         b'piece length': '5',
                                         b'pieces': b'asdfasdf',
                                         b'md5sum': b'asdfasdf',
                                         b'files': [ { b'path': 'WOW' },
                                                     { b'length': '5' } ] 
                                       },
                              b'name': 'GOATS',
                              b'comment': b'WOW',
                              b'created_by': b'OMG',
                              b'creation_date': datetime.datetime.now(),
                              b'piece length': '5',
                              b'pieces': b'asdfasdf' }
        
        try:
            self.cursor.execute( ("INSERT INTO torrents VALUES "
                                  "(%s, %s, %s, %s, %s, %s, %s) "
                                  "ON CONFLICT (info_hash) DO NOTHING"),
                                  (b'asdfasdf',
                                   b'fake name',
                                   b'fake comment',
                                   b'some fake created by',
                                   datetime.datetime.now(),
                                   '5',
                                   b'fake pieces yo') )
        except psycopg2.ProgrammingError as e:
            print(e)
        self.cursor.close()
        self.connection.close()

    def test_get_torrent(self):
        """ Test the get_torrent() function. """

        ret = self.db.get_torrent(b'asdfasdf')
        self.assertEqual(ret, Torrent(self.torrent_dict))

    def test_add_plugin(self):
        url_1 = 'https://github.com/BadStreff/slothtorrent_yts'
        ret = self.db.add_plugin(url_1)
        self.assertEqual(ret, True)

    def tearDown(self):
        print("wow")
        os.remove('test_settings.conf')
        shutil.rmtree('test_db/', ignore_errors=True)

if __name__ == '__main__':
    unittest.main()