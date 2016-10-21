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

        # Parse config file to read in settings
        config = configparser.ConfigParser()
        config.read(settings_file)
        username = config['DATABASE']['username']
        password = config['DATABASE']['password']
        ip = config['DATABASE']['ip']
        port = config['DATABASE']['port']
        db_name = config['DATABASE']['db']

        # Establish connection object initialize tables
        self._connection = pg8000.connect(user=username, 
                                          password=password,
                                          host=ip,
                                          port=int(port),
                                          database=db_name)
        self._initialize_tables()

    def _initialize_tables(self):
        cursor = self._connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS plugins (url TEXT, last_run TIMESTAMP)")
        self._connection.commit()

    def execute(self, statement):
        return self._connection.execute(statement)