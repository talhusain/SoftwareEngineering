"""
This file will load the controllers and pass the flask app so they can
setup requests that will be expected
"""

from flask import Flask
from flask import send_from_directory
from controllers.index import IndexController, index_page
from controllers.torrent import TorrentController, torrent_page
from controllers.admin import AdminController, admin_page
from controllers.login import LoginController, login_page

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(index_page)
app.register_blueprint(torrent_page)
app.register_blueprint(admin_page)
app.register_blueprint(login_page)


class RequestHandler(object):

    def __init__(self, db):
        self.db = db
        self.index_controller = IndexController(db)
        self.login_controller = LoginController(db)
        self.admin_controller = AdminController(db)
        self.torrent_controller = TorrentController(db, None)
        app.run()


# serve static files from flask for dev purposes, nginx will be
# configured later to serve them
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
