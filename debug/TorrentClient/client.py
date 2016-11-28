from bencoding import decode
from session import Session
from tracker import Tracker
from util import generate_peer_id
import threading


class Client(object):
    def __init__(self, download_location=None):
        self._sessions = {}  # 'torrent: [session1, session2]'
        self._torrent_status = {}  # '{torrent: status...}'
        if download_location is None:
            self.download_location = 'torrent_downloads/'
        else:
            self.download_location = download_location
        threading.Timer(1, self._keepalive_peers).start()

    def start(self, torrent):
        for t in torrent.trackers:
            tracker = Tracker(t, torrent, generate_peer_id())
            for peer in tracker.get_peers():
                session = Session(peer, torrent, self)
                # session.register_observer(self)
                if torrent not in self._sessions:
                    self._sessions[torrent] = []
                self._sessions[torrent].append(session)
                session.start()

    def _keepalive_peers(self):
        for torrent, sessions in self._sessions.items():
            for t in torrent.trackers:
                tracker = Tracker(t, torrent, generate_peer_id())
                for peer in tracker.get_peers():
                    if peer not in [p.peer for p in sessions]:
                        print('adding new peer %s' % peer[0])
                        session = Session(peer, torrent, self)
                        self._sessions[torrent].append(session)
                        session.start()


    def start_from_file(self, path):
        with open(path, 'rb') as f:
            self.start(Torrent(decode(f.read())))

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

    # not really ment to be called by the client, but is left public
    # incase it is usefull
    def close_session(self, session):
        try:
            self._sessions[session.torrent].remove(session)
        except:
            pass


if __name__ == '__main__':
    # for temporary debugging
    import pprint
    from os import listdir
    from torrent import Torrent
    from bencoding import decode
    pp = pprint.PrettyPrinter(indent=2)
    torrent_client = Client()
    for file in listdir('sample_torrents'):
        torrent_client.start_from_file('sample_torrents/' + file)

    # print('overview of active torrents per session: ')
    # pp.pprint(torrent_client._sessions)
