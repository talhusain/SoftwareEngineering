"""
All plugin related logic should go here.
This file might eventually need broken into a seperate package,
depending on how complex it gets.
"""

import configparser
from db import Database

class Loader(object):
    def __init__(self, db, settings_file):
        self._db = db
        self.settings_file = settings_file
        self._parse_config()
        self._load_plugins()

    def _load_plugins(self):
        pass

    def _parse_config(self):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        self.plugin_dir = config['PLUGINS']['directory']