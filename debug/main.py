"""
This file will be the entry point of the programs. It will handle events that
should happen only once on start up and initializing the Request Handlerobject.
"""

import configparser

from db import Database
from request_handler import RequestHandler
import plugin

# TESTING
import datetime

def main():
    # Initialize db handler with settings file
    db = Database('settings.conf')

    ############################ TESTING #############################

    connection = db.get_connection()
    cursor = connection.cursor()

    SQL = "SELECT info_hash FROM torrent_files"
    hash_val = None

    try:
        cursor.execute(SQL)
        hash_val = cursor.fetchone()
    except psycopg2.ProgrammingError as e:
    	print(e)

    print(db.get_torrent(hash_val))

    ############################ TESTING #############################

    # Initialize the request handler and start taking http requests
    rh = RequestHandler(db)

if __name__ == '__main__':
    main()