"""
Controller will be responsible for serving the index/search main page.
It is expects a query and returns a list of torrents.
"""

from flask import Flask, Blueprint

from db import Database

index_page = Blueprint('index_page', __name__)

class IndexController(object):
    def __init__(self, db):
        self.db = db

    @index_page.route('/')
    def index():
        return "You are looking at the index page</br>This is where the search  field will be displayed"
