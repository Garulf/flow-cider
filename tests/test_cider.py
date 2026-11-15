import json

import pytest

from cider_api.cider import Cider


class ChattySocket:
    """Cider keeps broadcasting playback updates to every client."""

    closed = False

    def send(self, payload):
        pass

    def recv(self):
        return json.dumps({"status": 0, "data": {}, "message": "OK", "type": "playbackStateUpdate"})

    def close(self):
        self.closed = True


def test_broadcasts_do_not_keep_a_request_waiting_forever():
    socket = ChattySocket()
    cider = Cider(connect=lambda url, timeout: socket, timeout=0.05)
    with pytest.raises(TimeoutError, match="library-status"):
        cider._action("library-status", "libraryStatus", type="song", id="1")
    assert socket.closed
