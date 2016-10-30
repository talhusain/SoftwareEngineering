"""
This file will load the controllers and pass the flask app so they can setup
requests that will be expected
"""

from flask import Flask

from db import Database

from controllers.index import IndexController, index_page
from controllers.torrent import TorrentController, torrent_page

app = Flask(__name__)
app.register_blueprint(index_page)
app.register_blueprint(torrent_page)

class RequestHandler(object):

    def __init__(self, db):
        self.db = db
        app.run()
        self.index_controller = IndexController(db)

    @app.route('/admin')
    def admin_page():
        return "Hello, world! This is the admin page"
