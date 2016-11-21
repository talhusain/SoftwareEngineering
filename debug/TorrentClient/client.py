from session import Session


class Client(object):
    def __init__(self, download_location=None):
        self._sessions = []
        if download_location is None:
            self.download_location = 'torrent_downloads/'
        else:
            self.download_location = download_location

    def start(self, torrent):
        self.sessions += Session(torrent, self.download_location)

    def start_from_file(self, path):
        pass

    def pause(self, torrent):
        pass

    def resume(self, torrent):
        pass

    def cancel(self, torrent):
        pass

    def set_upload_limit(self, limit):
        pass

    def set_download_limit(self, limit):
        pass

    def set_seed_ratio(self, ratio):
        pass

    def get_sessions(self):
        return self.sessions
