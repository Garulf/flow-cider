from __future__ import annotations
from typing import Union

from .artwork import get_artwork
from ._responses.search_response import song, album, play_params


class Media:

    def __init__(self, attributes: Union[song.Attributes, album.Attributes]):
        self._attributes = attributes

    def __repr__(self) -> str:
        return f"<Media name={self.name} artist={self.artist_name}>"

    def __str__(self) -> str:
        return f"{self.name} by {self.artist_name}"

    @property
    def id(self) -> str:
        return self._attributes["playParams"]["id"]

    @property
    def name(self) -> str:
        return self._attributes["name"]

    @property
    def artist_name(self) -> str:
        return self._attributes["artistName"]

    @property
    def play_params(self) -> play_params.PlayParams:
        return self._attributes["playParams"]

    @property
    def kind(self) -> str:
        return self.play_params["kind"]

    def artwork(self, width: int = 32, height: int = 32) -> str:
        url = self._attributes["artwork"]["url"]
        return get_artwork(url, width, height)
