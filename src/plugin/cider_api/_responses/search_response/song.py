from typing import Dict, List, TypedDict

from . import artwork
from . import play_params


class Attributes(TypedDict):
    hasTimeSyncedLyrics: bool
    albumName: str
    genreNames: List[str]
    trackNumber: int
    releaseDate: str
    durationInMillis: int
    isVocalAttenuationAllowed: bool
    isMasteredForItunes: bool
    isrc: str
    artwork: artwork.Artwork
    audioLocale: str
    composerName: str
    playParams: play_params.PlayParams
    url: str
    discNumber: int
    hasLyrics: bool
    isAppleDigitalMaster: bool
    audioTraits: Dict
    name: str
    previews: List[Dict[str, str]]
    artistName: str


class Song(TypedDict):
    id: str
    type: str
    href: str
    attributes: Dict
