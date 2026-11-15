from typing import Any, Dict

from pyflowlauncher import FlowLauncherV2, Plugin

from cider_api.cider import Cider
from cider_api.media import Media

plugin = Plugin(launcher=FlowLauncherV2())


def client() -> Cider:
    return Cider()


@plugin.on_method
def play_media(attributes: Dict[str, Any]) -> None:
    client().play_media(Media(attributes))


@plugin.on_method
def play_pause() -> None:
    client().play_pause()


@plugin.on_method
def open_cider() -> None:
    client().open()


@plugin.on_method
def play_media_next(attributes: Dict[str, Any]) -> None:
    client().play_media_next(Media(attributes))


@plugin.on_method
def play_media_last(attributes: Dict[str, Any]) -> None:
    client().play_media_last(Media(attributes))


@plugin.on_method
def like_media(attributes: Dict[str, Any]) -> None:
    client().rate_media(Media(attributes), "like")


@plugin.on_method
def dislike_media(attributes: Dict[str, Any]) -> None:
    client().rate_media(Media(attributes), "dislike")


@plugin.on_method
def unrate_media(attributes: Dict[str, Any]) -> None:
    client().rate_media(Media(attributes), "unrate")


@plugin.on_method
def toggle_library(attributes: Dict[str, Any]) -> None:
    client().toggle_library(Media(attributes))
