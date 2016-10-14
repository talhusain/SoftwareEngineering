"""
This file will be the entry point of the programs.
It will handle events that should happen only once on start up
and initializing the Request Handlerobject
"""

import configparser

from db import Database
from request_handler import RequestHandler


def main():
    # Initialize db handler with settings file
    db = Database('settings.conf')

    # Initialize the request handler and start taking http requests
    rh = RequestHandler(db)


if __name__ == '__main__':
    main()