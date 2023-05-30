from typing import TypedDict, List

from . import artwork
from . import play_params


class EditorialNotes(TypedDict):
    short: str
    standard: str


class Attributes(TypedDict):
    copyright: str
    genreNames: List[str]
    releaseDate: str
    isMasteredForItunes: bool
    upc: str
    artwork: artwork.Artwork
    playParams: play_params.PlayParams
    url: str
    recordLabel: str
    isCompilation: bool
    trackCount: int
    isPrerelease: bool
    audioTraits: List[str]
    isSingle: bool
    name: str
    artistName: str
    editorialNotes: EditorialNotes
    isComplete: bool



class Album(TypedDict):
    id: str
    type: str
    href: str
    attributes: Attributes
