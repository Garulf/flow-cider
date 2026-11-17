import copy
import json

import pytest
import websocket

import actions
import main
from cider_api.cider import Cider

ARTWORK = "https://is1-ssl.mzstatic.com/image/thumb/Music/v4/1a/2b/3c/cover.jpg/{w}x{h}bb.jpg"
SONG = {
    "name": "Midnight City",
    "artistName": "M83",
    "albumName": "Hurry Up, We're Dreaming",
    "artwork": {"url": ARTWORK, "width": 1400, "height": 1400},
    "playParams": {"id": "1440845291", "kind": "song"},
}
ALBUM = {
    "name": "Hurry Up, We're Dreaming",
    "artistName": "M83",
    "artwork": {"url": ARTWORK, "width": 1400, "height": 1400},
    "playParams": {"id": "1440845086", "kind": "album"},
}
OTHER_SONG = {
    "name": "Midnight Train",
    "artistName": "Sam Smith",
    "artwork": {"url": ARTWORK, "width": 1400, "height": 1400},
    "playParams": {"id": "1440889024", "kind": "song"},
}


class FakeSocket:
    """One websocket connection to Cider 1, which answers every action with a
    "generic" message and broadcasts typed messages for the ones that return data."""

    def __init__(self, server, timeout=None):
        self.server = server
        self.timeout = timeout
        self.inbox = []
        self.closed = False

    def send(self, payload):
        message = json.loads(payload)
        self.server.sent.append(message)
        self.inbox.append({"status": 0, "data": {}, "message": "OK", "type": "generic"})
        self.inbox.extend(self.server.replies(message))

    def recv(self):
        if not self.inbox:
            if self.timeout is None:
                raise AssertionError("recv() without a timeout would block forever")
            raise websocket.WebSocketTimeoutException("timed out")
        return json.dumps(self.inbox.pop(0))

    def close(self):
        self.closed = True


class FakeCiderServer:
    def __init__(self):
        self.sent = []
        self.sockets = []
        self.search_data = {
            "songs": {"data": [{"attributes": SONG}, {"attributes": OTHER_SONG}]},
            "albums": {"data": [{"attributes": ALBUM}]},
        }
        self.playback = dict(copy.deepcopy(SONG), status=True)
        self.library = {"inLibrary": False, "rating": 0}

    def connect(self, url, timeout=None):
        self.url = url
        socket = FakeSocket(self, timeout)
        self.sockets.append(socket)
        return socket

    def replies(self, message):
        typed = {
            "search": ("searchResults", self.search_data),
            "get-currentmediaitem": ("playbackStateUpdate", self.playback),
            "library-status": ("libraryStatus", self.library),
            "rating": ("rate", {"rating": message.get("rating")}),
            "change-library": ("change-library", {"add": message.get("add")}),
        }
        if message["action"] not in typed or message.get("id") == "no-id-found":
            return []
        kind, data = typed[message["action"]]
        return [{"status": 0, "data": copy.deepcopy(data), "message": "OK", "type": kind}]

    def actions(self):
        return [message["action"] for message in self.sent]


@pytest.fixture
def server(monkeypatch):
    fake = FakeCiderServer()
    monkeypatch.setattr(actions, "client", lambda: Cider(connect=fake.connect))
    monkeypatch.setattr(main, "SEARCH_DELAY", 0)
    return fake
