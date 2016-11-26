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
    
    test_info_hash = b'\xf7\xfb\xaa\x14\x90\x97yE\xcf\xd5\xb8\x18\xb3\xcd\xb16\xce\xfd\xcb\x8e'
    db.get_torrent(test_info_hash)

    # Initialize the request handler and start taking http requests
    RequestHandler(db)

if __name__ == '__main__':
    main()
