import time

from flox import Flox
from parse_args import parse_args
from cider_api.cider import Cider
from cider_api.media import Media
from results import (search_results, argument_results,
                     exception_results, now_playing, context_menu_results)


class FlowCider(Flox):

    def __init__(self):
        super().__init__()
        self.cider = Cider()

    def query(self, query: str):
        try:
            if query.strip():
                # Need to delay the search to allow the user to type.
                time.sleep(0.5)
                args, actions = parse_args(query)
                if " ".join(args.query).endswith(":"):
                    return argument_results(self, args, actions)
                results = self.cider.search(
                    " ".join(args.query), limit=args.limit)
                return search_results(self, args, results)
            else:
                return now_playing(self)
        except Exception as e:
            return exception_results(self, e)

    def context_menu(self, data):
        try:
            return context_menu_results(self, data)
        except Exception as e:
            return exception_results(self, e)

    def play_media(self, result):
        media = Media(result)
        self.cider.play_media(media)

    def play_pause(self):
        self.cider.play_pause()

    def open_cider(self):
        self.cider.open()

    def play_media_next(self, result):
        media = Media(result)
        self.cider.play_media_next(media)

    def play_media_last(self, result):
        media = Media(result)
        self.cider.play_media_last(media)

    def like_media(self, result):
        media = Media(result)
        self.cider.rate_media(media, "like")

    def dislike_media(self, result):
        media = Media(result)
        self.cider.rate_media(media, "dislike")

    def unrate_media(self, result):
        media = Media(result)
        self.cider.rate_media(media, "unrate")

    def toggle_library(self, result):
        media = Media(result)
        self.cider.toggle_library(media)
