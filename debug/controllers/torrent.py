"""
This class will be responsible for serving the status page of torrents that are in progress.

It will also be responsible for handling request that come in that perform an action on torrents,
each torrent session is expect to exist in it's own thread, a private class may be needed for this.
"""

"""
Controller will be responsible for serving the index/search main page.
It is expects a query and returns a list of torrents.
"""

from flask import Flask, Blueprint

from db import Database

torrent_page = Blueprint('torrent_page', __name__)

class TorrentController(object):
    def __init__(self, db):
        self.db = db

    @torrent_page.route('/torrent')
    def index():
        return "You is where torrents will be handled"