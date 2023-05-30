import json
import time
from tracemalloc import start
import webbrowser
from typing import Any, Dict, List, Optional, Union

import websocket
from .media import Media


BASE_HOST = "127.0.0.1"
BASE_PORT = 26369


class Cider:

    def __init__(self, host: str = BASE_HOST, port: int = BASE_PORT):
        self._host = host
        self._port = port
        self._ws = websocket.WebSocket()

    def _action(self, action: str, status: str = "generic", timeout: int = 30, **kwargs) -> Dict:
        self._ws.connect(f"ws://{self._host}:{self._port}")
        message = {"action": action, **kwargs}
        self._ws.send(json.dumps(message))
        start = time.time()
        while True:
            response = json.loads(self._ws.recv())
            if response["type"] == status:
                break
            if time.time() - start > timeout:
                raise TimeoutError("Timed out waiting for response")
        self._ws.close()
        return response

    def open(self) -> None:
        """Opens the Cider application"""
        webbrowser.open("cider://start")

    def search(self, term: str, limit: int = 20) -> List[Media]:
        r = self._action("search", "searchResults", term=term, limit=limit)
        media_items = []
        if r["data"].get("songs") and r["data"].get("albums"):
            media_items = r["data"]["songs"]["data"] + \
                r["data"]["albums"]["data"]
        return [Media(media_item["attributes"]) for media_item in media_items]

    def media_status(self) -> Dict[str, Any]:
        return self._action("get-currentmediaitem", "playbackStateUpdate")

    def play(self) -> None:
        """Starts playback"""
        self._action("play")

    def pause(self) -> None:
        """Pauses playback"""
        self._action("pause")

    def play_pause(self) -> None:
        """Toggles play/pause"""
        if self.media_status()["data"]["status"]:
            self.pause()
        else:
            self.play()

    def play_media_by_id(self, id: str, kind: str = "song") -> None:
        self._action("play-mediaitem", id=id, kind=kind)

    def play_media(self, media: Media) -> None:
        """Plays the given media item"""
        self.play_media_by_id(media.id, media.play_params["kind"])

    def play_media_next(self, media: Media) -> None:
        """Adds media as next in the queue"""
        self._action("play-next", id=media.id, type=media.kind)

    def play_media_last(self, media: Media) -> None:
        """Adds media as last in the queue"""
        self._action("play-later", id=media.id, type=media.kind)

    def rate(self, type: str, id: str, rating: int) -> None:
        """Rate a media item"""
        valid_ratings = [-1, 0, 1]
        if rating not in valid_ratings:
            raise ValueError(f"Rating must be one of {valid_ratings}")
        self._action("rating", "rate", type=type, id=id, rating=rating)

    def rate_media(self, media: Media, rating: str) -> None:
        """Rate a media item"""
        rating_map = {"dislike": -1, "unrate": 0, "like": 1}
        if rating not in rating_map:
            raise ValueError(
                f"Rating must be one of {list(rating_map.keys())}")
        self.rate(media.play_params["kind"], media.id, rating_map[rating])

    def library_status(self, media: Media) -> Dict:
        """Checks if a media item is in the library"""
        r = self._action("library-status", "libraryStatus",
                         type=media.play_params["kind"], id=media.id)
        return r

    def _library(self, type: str, id: str, add: bool) -> None:
        """Adds/removes a media item from the library"""
        self._action("change-library", "change-library",
                     type=type, id=id, add=add)

    def add_to_library(self, media: Media) -> None:
        """Adds a media item to the library"""
        self._library(media.play_params["kind"], media.id, True)

    def remove_from_library(self, media: Media) -> None:
        """Removes a media item from the library"""
        self._library(media.play_params["kind"], media.id, False)

    def toggle_library(self, media: Media) -> None:
        """Toggles a media item in the library"""
        self._library(media.play_params["kind"], media.id, not self.library_status(
            media)["data"]["inLibrary"])


if __name__ == '__main__':
    cider = Cider()
    cider.open()
