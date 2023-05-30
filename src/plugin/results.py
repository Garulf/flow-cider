from __future__ import annotations
from typing import TYPE_CHECKING, Any, List
import argparse


from parse_args import CHOICES
from cider_api.media import Media
if TYPE_CHECKING:
    from main import FlowCider


def exception_results(plugin: FlowCider, exception: Exception):
    if isinstance(exception, ConnectionRefusedError):
        plugin.add_item(
            title="Connection Refused: Could not connect to Cider",
            subtitle="Please make sure Cider is open and running",
            method=plugin.open_cider,
        )
        return
    raise exception


def search_results(plugin: FlowCider, args: argparse.Namespace, results: List[Media]):
    if not results:
        plugin.add_item(
            title="No results found"
        )
        return
    if args.type in CHOICES:
        results = [
            result for result in results if result.kind == args.type]
    if args.by:
        results = [
            result for result in results if result.artist_name.lower() == args.by.lower()]
    for result in results:
        plugin.add_item(
            title=result.name,
            subtitle=f"by {result.artist_name} ({result.kind})",
            icon=result.artwork(32, 32),
            method=plugin.play_media,
            parameters=[result._attributes],
            context=[result._attributes],
            Preview={
                "PreviewImagePath": result.artwork(512, 512),
            }
        )


def argument_results(plugin: FlowCider, args: argparse.Namespace, actions: List[argparse.Action]):
    if " ".join(args.query).endswith(":"):
        for action in actions:
            if action.option_strings:
                plugin.add_item(
                    title=action.option_strings[0],
                    subtitle=action.help or "",
                )
        return


def now_playing(plugin: FlowCider):
    media_status = plugin.cider.media_status()
    data = media_status.get("data")
    if data:
        media = Media(data)
        plugin.add_item(
            title=str(media),
            subtitle="Now playing" if data.get("status") else "Paused",
            icon=media.artwork(32, 32),
            method=plugin.play_pause,
            context=[data],
        )


def context_menu_results(plugin: FlowCider, data: List[Any]):
    if data:
        plugin.add_item(
            title="Play next",
            subtitle="Add media to queue",
            method=plugin.play_media_next,
            parameters=[data[0]]
        )
        plugin.add_item(
            title="Play later",
            subtitle="Add media to end of queue",
            method=plugin.play_media_last,
            parameters=[data[0]]
        )
        media = Media(data[0])
        library_status = plugin.cider.library_status(media)
        rating = library_status["data"]["rating"]
        if rating != 1:
            plugin.add_item(
                title="Love",
                subtitle="Love this song",
                method=plugin.like_media,
                parameters=[data[0]]
            )
        elif (rating != -1):
            plugin.add_item(
                title="Dislike",
                subtitle="Dislike this song",
                method=plugin.dislike_media,
                parameters=[data[0]]
            )
        if rating != 0:
            plugin.add_item(
                title="Remove rating",
                subtitle="Remove rating from this song",
                method=plugin.unrate_media,
                parameters=[data[0]]
            )
        if library_status["data"]["inLibrary"]:
            plugin.add_item(
                title="Remove from library",
                subtitle="Remove media from library",
                method=plugin.cider.toggle_library,
                parameters=[data[0]]
            )
        else:
            plugin.add_item(
                title="Add to library",
                subtitle="Add media to library",
                method=plugin.cider.toggle_library,
                parameters=[data[0]]
            )
        now_playing(plugin)
