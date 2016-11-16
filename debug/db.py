"""
This module will handle establishing the connection to the database
and pass the connection to objects that use it.
"""

import configparser
import psycopg2
import os
from bencode import encode, decode
from bencoding.bencode import decode
from torrent import Torrent
import datetime

DEBUG = True


class Database(object):
    '''
    Note that no calls to the self._connection should be made directly.
    If a method needs called it should be called on the instance of this
    class. If it only exists for the _connection object a wrapper will
    need created.
    '''

    def __init__(self, settings_file):

        # Parse config file to read in settings
        config = configparser.ConfigParser()
        config.read(settings_file)
        self.username = config['DATABASE']['username']
        self.password = config['DATABASE']['password']
        self.ip = config['DATABASE']['ip']
        self.port = config['DATABASE']['port']
        self.db_name = config['DATABASE']['db']

        # Establish connection object initialize tables
        self._connection = psycopg2.connect(user=username,
                                            password=password,
                                            host=ip,
                                            port=int(port),
                                            database=db_name)
        #self._initialize_tables()
        #self._add_fake_torrents()
        #self._add_sample_torrents()
        self._initialize_tables()
        # self._add_fake_torrents()
        # self._add_sample_torrents()
        self._connection.close()

    def _initialize_tables(self):
        self._connection = self.get_connection()
        cursor = self._connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS plugins"
                       "(id TEXT PRIMARY KEY, url TEXT, last_run TIMESTAMP)"
                       "(url TEXT PRIMARY KEY, last_run TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS torrents "
                       "(info_hash BYTEA PRIMARY KEY,"
                       "name TEXT,"
                       "comment TEXT,"
                       "created_by TEXT,"
                       "creation_time TIMESTAMP,"
                       "piece_length INT,"
                       "pieces BYTEA)"
                       "pieces BYTEA,"
                       "provider TEXT REFERENCES plugins (url))")
        cursor.execute("CREATE TABLE IF NOT EXISTS announcers "
                       "(url TEXT,"
                       "info_hash BYTEA REFERENCES torrents (info_hash),"
                       "PRIMARY KEY (url, info_hash))")
        cursor.execute("CREATE TABLE IF NOT EXISTS torrent_files "
                       "(file_path TEXT,"
                       "length INT,"
                       "length TEXT,"
                       "info_hash BYTEA REFERENCES torrents (info_hash),"
                       "PRIMARY KEY (file_path, info_hash))")
        self._connection.commit()
        self._connection.close()

    def _add_fake_torrents(self):
        self._connection = self.get_connection()
        cursor = self._connection.cursor()
        dt = datetime.datetime.now()
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s) "
        cursor.execute(("INSERT INTO plugins VALUES "
                        "(%s, %s) "
                        "ON CONFLICT (url) DO NOTHING"),
                       ('None', dt))
        cursor.execute(("INSERT INTO plugins VALUES "
                        "(%s, %s) "
                        "ON CONFLICT (url) DO NOTHING"),
                       ('https://github.com/BadStreff/slothtorrent_yts', dt))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s) "
                        "ON CONFLICT (info_hash) DO NOTHING"),
                       (b'0000',
                        'sample0',
                        'sample comment',
                        'sample creator',
                        dt,
                        0,
                        b'0000'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s) "
                        b'0000',
                        'None'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s) "
                        "ON CONFLICT (info_hash) DO NOTHING"),
                       (b'0001',
                        'sample1',
                        'sample comment',
                        'sample creator',
                        dt,
                        0,
                        b'0000'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s) "
                        b'0000',
                        'None'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s) "
                        "ON CONFLICT (info_hash) DO NOTHING"),
                       (b'0002',
                        'sample2',
                        'sample comment',
                        'sample creator',
                        dt,
                        0,
                        b'0000'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s) "
                        b'0000',
                        'None'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s) "
                        "ON CONFLICT (info_hash) DO NOTHING"),
                       (b'0003',
                        'sample4',
                        'sample comment',
                        'sample creator',
                        dt,
                        0,
                        b'0000'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s) "
                        b'0000',
                        'None'))
        cursor.execute(("INSERT INTO torrents VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s) "
                        "ON CONFLICT (info_hash) DO NOTHING"),
                       (b'0005',
                        'sample5',
                        'sample comment',
                        'sample creator',
                        dt,
                        0,
                        b'0000'))
                        b'0000',
                        'None'))
        self._connection.commit()
        self._connection.close()

    def _add_sample_torrents(self):
        print('importing sample torrents...')
        for file in os.listdir('sample_torrents'):
            with open('sample_torrents/' + file, 'rb') as f:
                torrent_dict = decode(f.read())
                torrent = Torrent(torrent_dict)
                self.import_torrent(torrent)

    def execute(self, statement):
        return self._connection.execute(statement)
                self.import_torrent(torrent, 'None')

    def get_recent_torrents(self, number):
        """Returns a list of the most recently added torrents. If the
        number exceeds the total number of torrents in the database all
        torrents will be returned.
        Args:
            number (int): The maximum number of torrents to return

        Args:
            number (int): The maximum number of torrents to return

        Returns:
            list: A list of Torrent objects
        """
        pass

    def get_popular_torrents(self, number):
        """Returns torrents with the most seeders. If the number exceeds
        the total number of torrents in the database all torrents will
        be returned.
        Args:
            number (int): The maximum number of torrents to return

        Args:
            number (int): The maximum number of torrents to return

        Returns:
            list: A list of Torrent objects
        """
        pass

    def search_torrents(self, search_string):
        """Searches through all torrents based on a string
        Args:
            search_string (string): The string that determines the
            query.

        Args:
            search_string (string): The string that determines the
            query.

        Returns:
            list: A list of Torrent objects
        """
        pass

    def import_torrent(self, torrent, provider):
        """Imports a torrent object into the database. This function
        should only be called by the plugin module once in production
        Args:
            torrent (Torrent): Torrent object see torrent.py for more
            information
            provider (string): The url of the plugin that created the
            torrent
        Returns:
            BOOL: success or failure
        """
        print(torrent)
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(("INSERT INTO torrents VALUES "
                            "(%s, %s, %s, %s, %s, %s, %s, %s) "
                            "ON CONFLICT (info_hash) DO NOTHING"),
                           (torrent.info_hash,
                            torrent.name,
                            torrent.comment,
                            torrent.created_by,
                            torrent.creation_date,
                            torrent.piece_length,
                            torrent.pieces,
                            provider))
            for tracker in torrent.trackers:
                cursor.execute(("INSERT INTO announcers VALUES (%s, %s) "
                                "ON CONFLICT (url, info_hash) DO NOTHING"),
                               (tracker, torrent.info_hash))
            for file in torrent.files:
                cursor.execute(("INSERT INTO torrent_files VALUES "
                                "(%s, %s, %s) "
                                "ON CONFLICT (file_path, info_hash) "
                                "DO NOTHING"),
                               (file['path'],
                                str(file['length']),
                                torrent.info_hash))
            ret = True
        except psycopg2.ProgrammingError as e:
            print(e)
            connection.rollback()
            ret = False
        cursor.close()
        connection.commit()
        connection.close()
        return ret

    def get_torrent(self, info_hash):
        """Returns a torrent from the database given an info_hash
        Args:
            info_hash (bytes): The info_hash of the torrent we want
            ret = True
        except psycopg2.ProgrammingError as e:
            print(e)
            connection.rollback()
            ret = False
        cursor.close()
        connection.commit()
        connection.close()
        return ret

    def get_torrent(self, info_hash):
        """Returns a torrent from the database given an info_hash

        Args:
            info_hash (bytes): The info_hash of the torrent we want

        Returns:
            Torrent (see torrent.py for more information) or None if no matching info_hash
        """

        """
        info_hash BYTEA PRIMARY KEY,
        name TEXT,
        comment TEXT,
        created_by TEXT,
        creation_time TIMESTAMP,
        piece_length INT,
        pieces BYTEA
        """
        
        cursor = self._connection.cursor()
        try:
            cursor.execute( ("SELECT * FROM torrents WHERE info_hash = 'asdfasdf'") )
            tup = cursor.fetchone()
        except psycopg2.ProgrammingError as e:
            print(e)
            return None
        cursor.close()
        
        info_hash = bytes(tup[0])
        name = tup[1]
        comment = tup[2]
        created_by = tup[3]
        creation_time = tup[4]
        piece_length = tup[5]
        pieces = bytes(tup[6])

        torrent = {}
        torrent[b'info hash'] = info_hash
        torrent[b'name'] = str.encode(name)
        torrent[b'comment'] = str.encode(comment)
        torrent[b'created by'] = str.encode(created_by)
        torrent[b'creation time'] = creation_time
        torrent[b'piece length'] = piece_length
        torrent[b'pieces'] = pieces
        torrent[b'files'] = []
        torrent[b'info'] = { 
                             b'name': str.encode(name),
                             b'piece length': piece_length,
                             b'pieces': pieces,
                             b'files': [
                                        { b'path': [ str.encode('a'), 
                                                     str.encode('fake'), 
                                                     str.encode('path') ] },
                                        { b'length': 43 }
                                       ]
                           }

        return Torrent(torrent)

    def add_plugin(self, url):
        """Add a plugin URL to the database
        Args:
            url (string): Full patch a .git repo that is the plugin

        Args:
            url (string): Full patch a .git repo that is the plugin

        Returns:
            BOOL: success or failure
        """
        
        cursor = self._connection.cursor()
        try:
            cursor.execute( ("INSERT INTO plugins VALUES (%s, %s, %s) "
                             "ON CONFLICT (id) DO NOTHING"),
                             ('001', 'some/url/and/some/goats.txt', datetime.datetime.now()) )
        except psycopg2.ProgrammingError as e:
            print(e)
            return False
        cursor.close()
        return True

    def remove_plugin(self, url):
        """Remove a plugin from the database
<<<<<<< HEAD
        Args:
            url (string): Removes the specified plugin url from the
            database
=======

        Args:
            url (string): Removes the specified plugin url from the
            database

>>>>>>> 7f53710bed8128ecbb99c37ebd94066da5b8aac9
        Returns:
            BOOL: success or failure
        """
        pass

<<<<<<< HEAD
if __name__ == '__main__':
    pass  
=======
    def get_all_plugin(self):
        """Returns a list of tuples of all plugins in the database

        Returns:
            list: List of tuples in the format (URL, LAST_RUN_DATE)
        """
        pass

    def get_connection(self):
        return psycopg2.connect(user=self.username,
                                password=self.password,
                                host=self.ip,
                                port=int(self.port),
                                database=self.db_name)
>>>>>>> 7f53710bed8128ecbb99c37ebd94066da5b8aac9
