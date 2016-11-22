"""
This file will load the controllers and pass the flask app so they can
setup requests that will be expected
"""

from flask import Flask
from flask import send_from_directory
from controllers.index import IndexController, index_page
from controllers.torrent import torrent_page

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(index_page)
app.register_blueprint(torrent_page)


class RequestHandler(object):

    def __init__(self, db):
        self.db = db
        self.index_controller = IndexController(db)
        app.run()

    @app.route('/admin')
    def admin_page():
        return "Hello, world! This is the admin page"


# serve static files from flask for dev purposes, nginx will be
# configured later to serve them
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
