"""
This file will be the entry point of the programs. It will handle events that
should happen only once on start up and initializing the Request Handlerobject.
"""

from db import Database
from request_handler import RequestHandler
import plugin

def main():
    # Initialize db handler with settings file
    db = Database('settings.conf')

    connection = db.get_connection()
    cursor = connection.cursor()

    # Initialize the request handler and start taking http requests
    RequestHandler(db)

if __name__ == '__main__':
    main()
