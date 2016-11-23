"""
Controller will be responsible for serving the index/search main page.
It is expects a query and returns a list of torrents.
"""

from flask import Flask, Blueprint, render_template, request, redirect, url_for

index_page = Blueprint('index_page', __name__)

db = None

class IndexController(object):
    def __init__(self, database):
        db = database

@index_page.route('/')
def index():
    return render_template('index.html')

@index_page.route('/hello/')
@index_page.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)








@index_page.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        return redirect(url_for('index_page.hello', name=username))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''