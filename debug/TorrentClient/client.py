from session import Session
from tracker import Tracker
from util import generate_peer_id


class Client(object):
    def __init__(self, download_location=None):
        self._sessions = {}  # 'torrent: [session1, session2]'
        if download_location is None:
            self.download_location = 'torrent_downloads/'
        else:
            self.download_location = download_location

    def start(self, torrent):
        for t in torrent.trackers:
                tracker = Tracker(t, torrent, generate_peer_id())
                for peer in tracker.get_peers():
                    session = Session(peer, torrent, self.download_location)
                    session.register_observer(self)
                    if torrent not in self._sessions:
                        self._sessions[torrent] = []
                    self._sessions[torrent].append(session)
                    session.send_recv_handshake()

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

    def close_session(self, session):
        self._sessions[session.torrent].remove(session)


if __name__ == '__main__':
    from os import listdir
    from torrent import Torrent
    from bencoding import decode
    torrent_client = Client()
    for file in listdir('sample_torrents'):
        with open('sample_torrents/' + file, 'rb') as f:
            t = Torrent(decode(f.read()))
            torrent_client.start(t)
    print(torrent_client._sessions)
