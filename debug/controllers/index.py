from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

index_page = Blueprint('index_page', __name__)
db = None


class IndexController(object):
    def __init__(self, database):
        global db
        db = database


@index_page.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # get search string from post data
        # search db for torrents
        # render template and pass it the returned torrents
        return render_template('index.html')
    else:
        torrents = db.get_recent_torrents(25)
        return render_template('index.html', torrents=torrents)
