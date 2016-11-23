"""
All plugin related logic should go here.
This file might eventually need broken into a seperate package,
depending on how complex it gets.
"""

from db import Database
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
from functools import partial


# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

# Setup a plugin base for "example.modules" and make sure to load
# all the default built-in plugins from the builtin_plugins folder.
plugin_base = PluginBase(package='slothtorrent_plugins')


def run_init(app, queue):
    """Shows all formatters in demo mode of an application."""
    for name, init in sorted(app.initializers.items()):
        init(queue)


class Plugin(object):
    """Represents a simple application that loads torrents."""

    def __init__(self, path):
        # Each plugin has a name
        self.name = os.path.basename(path)

        # And a dictionary where it stores "initializers".  These will
        # be functions provided by plugins which queue torrents.
        self.initializers = {}

        # and a source which loads the plugins from the "app_name/plugins"
        # folder.  We also pass the application name as identifier.  This
        # is optional but by doing this out plugins have consistent
        # internal module names which allows pickle to work.
        self.source = plugin_base.make_plugin_source(
            searchpath=[get_path(path)])

        # Here we list all the plugins the source knows about, load them
        # and the use the "setup" function provided by the plugin to
        # initialize the plugin.
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            plugin.setup(self)

    def register_init(self, name, init):
        """A function a plugin can use to register a formatter."""
        self.initializers[name] = init


class Loader(object):
    def __init__(self, db, settings_file):
        self._db = db
        self.settings_file = settings_file
        self._parse_config()
        threading.Thread(target=self._load_plugins).start()

    def _load_plugins(self):
        plugins = self._db.get_all_plugins()
        for plugin, last_run in plugins:
            try:
                print('attempting to clone plugin %s...' % plugin)
                path = self.clone_plugin(plugin)
            except:
                continue
            print('running plugin %s...' % path)
            p = Plugin(path)
            q = queue.Queue()
            threading.Thread(target=run_init,
                             args=(p, q,)).start()
            threading.Thread(target=self._process_queue,
                             args=(q, plugin)).start()

    def _process_queue(self, q, provider):
        while True:
            if not q.empty():
                url = q.get()
                # print('got url %s' % url)
                r = requests.get(url)
                try:
                    r = self._db.import_torrent(Torrent(decode(r.content)),
                                                provider)
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


if __name__ == '__main__':
    db = Database('settings.conf')
    Loader(db, 'settings.conf')
