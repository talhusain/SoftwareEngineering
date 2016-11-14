import unittest
import plugin
import os
import shutil


class TestLoader(unittest.TestCase):

    def setUp(self):
        plugin_config = """[PLUGINS]
                        directory=test_plugins
                        """
        with open('test_plugin_settings.conf', 'w') as file:
            file.write(plugin_config)
        self.loader = plugin.Loader(None, 'test_plugin_settings.conf')

    def test_clone_plugin_none(self):
        with self.assertRaises(Exception):
            self.loader.clone_plugin(None)

    def test_clone_plugin(self):
        url = 'https://github.com/BadStreff/slothtorrent_yts'
        ret = self.loader.clone_plugin(url)
        self.assertEqual(ret, 'test_plugins/BadStreff/slothtorrent_yts')

    def test_clone_plugin_already_exists(self):
        url = 'https://github.com/BadStreff/slothtorrent_yts'
        ret = self.loader.clone_plugin(url)
        self.assertEqual(ret, 'test_plugins/BadStreff/slothtorrent_yts')

    def tearDown(self):
        os.remove('test_plugin_settings.conf')
        shutil.rmtree('test_plugins/', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
