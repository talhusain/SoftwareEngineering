"""
This module will handle establishing the connection to the database
and pass the connection to objects that use it.
"""

import configparser
import pg8000

class Database(object):
    '''
    Note that no calls to the self._connection should be made directly.
    If a method needs called it should be called on the instance of this class.
    If it only exists for the _connection object a wrapper will need created.
    '''
    def __init__(self, settings_file):
        config = configparser.ConfigParser()
        config.read(settings_file)
        username = config['DATABASE']['username']
        password = config['DATABASE']['password']
        ip = config['DATABASE']['ip']
        port = config['DATABASE']['port']
        #self._db = postgresql.open("pq://" + username + ":" + password + "@" + ip + ":" + port + "/slothtorrent")
        self._connection = pg8000.connect(user=username, password=password, host=ip, port=int(port))

    def execute(self, statement):
        return self._connection.execute(statement)