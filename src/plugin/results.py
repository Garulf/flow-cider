from __future__ import annotations

import argparse
from typing import Any, List

from pyflowlauncher import Result
from pyflowlauncher.models.result import PreviewInfo

import actions
from cider_api.cider import Cider
from cider_api.media import Media
from parse_args import CHOICES, QueryError


def preview(image_path: str) -> PreviewInfo:
    return PreviewInfo(PreviewImagePath=image_path, Description=None, IsMedia=False, PreviewDeligate=None)


def error_results(exception: Exception) -> List[Result]:
    if isinstance(exception, ConnectionRefusedError):
        return [
            Result(
                title="Connection Refused: Could not connect to Cider",
                subtitle="Please make sure Cider is open and running",
            ).add_action(actions.open_cider)
        ]
    if isinstance(exception, QueryError):
        return [Result(title="Invalid search", subtitle=str(exception))]
    return [Result(title=exception.__class__.__name__, subtitle=str(exception))]


def media_result(media: Media) -> Result:
    return Result(
        title=media.name,
        subtitle=f"by {media.artist_name} ({media.kind})",
        icon=media.artwork(32, 32),
        context_data=[media.attributes],
        preview=preview(media.artwork(512, 512)),
    ).add_action(actions.play_media, [media.attributes])


def search_results(args: argparse.Namespace, results: List[Media]) -> List[Result]:
    if args.type in CHOICES:
        results = [result for result in results if f"{result.kind}s" == args.type]
    if args.by:
        results = [result for result in results if result.artist_name.lower() == args.by.lower()]
    if not results:
        return [Result(title="No results found")]
    return [media_result(result) for result in results]


def argument_results(options: List[argparse.Action]) -> List[Result]:
    return [
        Result(title=option.option_strings[0], subtitle=option.help or "")
        for option in options
        if option.option_strings
    ]


def now_playing(cider: Cider) -> List[Result]:
    data = cider.media_status().get("data")
    if not data:
        return []
    media = Media(data)
    return [
        Result(
            title=str(media),
            subtitle="Now playing" if data.get("status") else "Paused",
            icon=media.artwork(32, 32),
            context_data=[data],
        ).add_action(actions.play_pause)
    ]


def context_menu_results(cider: Cider, data: List[Any]) -> List[Result]:
    if not data:
        return []
    attributes = data[0]
    results = [
        Result(title="Play next", subtitle="Add media to queue").add_action(actions.play_media_next, [attributes]),
        Result(title="Play later", subtitle="Add media to end of queue").add_action(actions.play_media_last, [attributes]),
    ]
    library_status = cider.library_status(Media(attributes))["data"]
    rating = library_status["rating"]
    if rating != 1:
        results.append(Result(title="Love", subtitle="Love this song").add_action(actions.like_media, [attributes]))
    elif rating != -1:
        results.append(Result(title="Dislike", subtitle="Dislike this song").add_action(actions.dislike_media, [attributes]))
    if rating != 0:
        results.append(
            Result(title="Remove rating", subtitle="Remove rating from this song").add_action(actions.unrate_media, [attributes])
        )
    if library_status["inLibrary"]:
        results.append(
            Result(title="Remove from library", subtitle="Remove media from library").add_action(actions.toggle_library, [attributes])
        )
    else:
        results.append(
            Result(title="Add to library", subtitle="Add media to library").add_action(actions.toggle_library, [attributes])
        )
    return results + now_playing(cider)
