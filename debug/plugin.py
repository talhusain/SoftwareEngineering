"""
All plugin related logic should go here.
This file might eventually need broken into a seperate package,
depending on how complex it gets.
"""

import configparser
import os
import threading
import queue
from git import Repo
from urllib.parse import urlparse
import requests
from torrent import Torrent
from bencoding.bencode import decode
from pluginbase import PluginBase


class Loader(object):
    def __init__(self, db, settings_file):
        self._db = db
        self._queue = queue.Queue()
        self.settings_file = settings_file
        self.sample_plugin = 'https://github.com/BadStreff/slothtorrent_yts'

        self._parse_config()
        threading.Thread(target=self._process_queue).start()
        threading.Thread(target=self._load_plugins).start()

    def _load_plugins(self):
        path = self.clone_plugin(self.sample_plugin)
        plugin_base = PluginBase(package='test')
        plugin_source = plugin_base.make_plugin_source(searchpath=[path])
        with plugin_source:
            src = plugin_source.load_plugin('main')
        t = threading.Thread(target=src.init, args=(self._queue,))
        t.start()
        t.join()

    def _process_queue(self):
        while True:
            if not self._queue.empty():
                url = self._queue.get()
                # print('got url %s' % url)
                r = requests.get(url)
                try:
                    r = self._db.import_torrent(Torrent(decode(r.content)),
                                                self.sample_plugin)
                    if not r:
                        print('Error importing %s' % url)
                except Exception as e:
                    print(e)
                    print('Encountered an exception importing %s' % url)
                    pass

    def _parse_config(self):
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        self.plugin_dir = config['PLUGINS']['directory']

    def clone_plugin(self, url):
        path = urlparse(url).path
        path = os.path.join(self.plugin_dir, path[1:])
        if not os.path.exists(path):
            Repo.clone_from(url, path)
        return path
