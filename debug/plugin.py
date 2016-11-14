"""
All plugin related logic should go here.
This file might eventually need broken into a seperate package,
depending on how complex it gets.
"""

import configparser
import os
from git import Repo
from urllib.parse import urlparse
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

    def clone_plugin(self, url):
        path = urlparse(url).path
        print(path)
        print(os.path.join('plugins/', path[1:]))
        Repo.clone_from(url, os.path.join(self.plugin_dir, path[1:]))

if __name__ == '__main__':
    print('running')
    loader = Loader(None, 'settings.conf')
    
loader.clone_plugin('https://github.com/BadStreff/SlothTorrent-yts')
