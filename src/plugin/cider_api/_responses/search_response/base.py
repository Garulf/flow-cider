from typing import List, Dict, TypedDict

from . import song
from . import album


class Albums(TypedDict):
    href: str
    next: str
    data: List[album.Album]


class Songs(TypedDict):
    href: str
    next: str
    data: List[song.Song]


class Data(TypedDict):
    songs: Songs
    albums: Albums
    playlists: Dict
    artists: Dict
    meta: Dict


class SearchResponse(TypedDict):
    status: int
    data: Data
    message: str
    type: str
