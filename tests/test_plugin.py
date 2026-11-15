import asyncio
import json
from pathlib import Path

from pyflowlauncher.jsonrpc import JsonRPCV2Client

import main
from conftest import ALBUM, SONG
from main import plugin

ROOT = Path(__file__).resolve().parents[1]


def call(method, *params):
    return asyncio.run(plugin._event_handler.trigger_event(method, *params))


def results(method, *params):
    return call(method, *params)["Result"]


def titles(method, *params):
    return [result["Title"] for result in results(method, *params)]


def test_manifest_keeps_id_and_keyword_on_python_v2():
    manifest = json.loads((ROOT / "data" / "plugin.json").read_text())
    assert manifest["ID"] == "552e8fc4a1674f04a2e78f821d3a252c"
    assert manifest["ActionKeyword"] == "fc"
    assert manifest["Language"] == "python_v2"
    assert manifest["ExecuteFileName"] == "run.py"


def test_empty_query_shows_now_playing(server):
    (result,) = results("query", "")
    assert result["Title"] == "Midnight City by M83"
    assert result["SubTitle"] == "Now playing"
    assert result["IcoPath"] == SONG["artwork"]["url"].format(w=32, h=32)
    assert result["JsonRPCAction"]["Method"] == "play_pause"
    assert result["ContextData"][0]["playParams"]["id"] == "1440845291"


def test_paused_track_says_paused(server):
    server.playback["status"] = False
    assert results("query", "")[0]["SubTitle"] == "Paused"


def test_search_lists_songs_then_albums(server):
    found = results("query", "midnight")
    assert [r["Title"] for r in found] == ["Midnight City", "Midnight Train", "Hurry Up, We're Dreaming"]
    assert found[0]["SubTitle"] == "by M83 (song)"
    assert found[0]["JsonRPCAction"] == {
        "Method": "play_media", "Parameters": [SONG], "DontHideAfterAction": False,
    }
    assert found[0]["ContextData"] == [SONG]
    assert found[0]["Preview"]["PreviewImagePath"].endswith("512x512bb.jpg")
    assert server.sent == [{"action": "search", "term": "midnight", "limit": 20}]
    assert server.url == "ws://127.0.0.1:26369"
    assert all(socket.closed for socket in server.sockets)


def test_limit_and_artist_filter(server):
    assert titles("query", "midnight :limit 5 :by m83") == ["Midnight City", "Hurry Up, We're Dreaming"]
    assert server.sent[0]["limit"] == 5


def test_type_filter(server):
    assert titles("query", "midnight :type songs") == ["Midnight City", "Midnight Train"]
    assert titles("query", "midnight :type albums") == ["Hurry Up, We're Dreaming"]


def test_filters_that_match_nothing_say_so(server):
    assert titles("query", "midnight :by nobody") == ["No results found"]


def test_search_with_only_songs(server):
    del server.search_data["albums"]
    assert titles("query", "midnight") == ["Midnight City", "Midnight Train"]


def test_search_with_only_albums(server):
    del server.search_data["songs"]
    assert titles("query", "midnight") == ["Hurry Up, We're Dreaming"]


def test_no_results(server):
    server.search_data = {}
    assert titles("query", "zzzz") == ["No results found"]


def test_trailing_colon_lists_options(server):
    assert titles("query", "midnight :") == [":limit", ":by", ":type"]
    assert server.sent == []


def test_context_menu_for_unrated_song_not_in_library(server):
    assert titles("context_menu", [SONG]) == [
        "Play next", "Play later", "Love", "Dislike", "Add to library", "Midnight City by M83",
    ]
    assert server.sent[0] == {"action": "library-status", "type": "song", "id": "1440845291"}


def test_context_menu_for_disliked_song(server):
    server.library = {"inLibrary": False, "rating": -1}
    assert titles("context_menu", [SONG])[2:4] == ["Love", "Remove rating"]


def test_context_menu_for_loved_song_in_library(server):
    server.library = {"inLibrary": True, "rating": 1}
    assert titles("context_menu", [SONG]) == [
        "Play next", "Play later", "Dislike", "Remove rating", "Remove from library", "Midnight City by M83",
    ]


def test_actions_send_cider_commands(server):
    call("play_media", ALBUM)
    call("play_media_next", SONG)
    call("play_media_last", SONG)
    call("like_media", SONG)
    call("dislike_media", SONG)
    call("unrate_media", SONG)
    call("toggle_library", SONG)
    assert server.sent == [
        {"action": "play-mediaitem", "id": "1440845086", "kind": "album"},
        {"action": "play-next", "id": "1440845291", "type": "song"},
        {"action": "play-later", "id": "1440845291", "type": "song"},
        {"action": "rating", "type": "song", "id": "1440845291", "rating": 1},
        {"action": "rating", "type": "song", "id": "1440845291", "rating": -1},
        {"action": "rating", "type": "song", "id": "1440845291", "rating": 0},
        {"action": "library-status", "type": "song", "id": "1440845291"},
        {"action": "change-library", "type": "song", "id": "1440845291", "add": True},
    ]


def test_play_pause_toggles(server):
    call("play_pause")
    server.playback["status"] = False
    call("play_pause")
    assert server.actions() == ["get-currentmediaitem", "pause", "get-currentmediaitem", "play"]


def test_cider_not_running_offers_to_open_it(monkeypatch, server):
    def refuse(url, **kwargs):
        raise ConnectionRefusedError(111, "Connection refused")

    monkeypatch.setattr(main.actions, "client", lambda: main.actions.Cider(connect=refuse))
    (result,) = results("query", "midnight")
    assert result["Title"] == "Connection Refused: Could not connect to Cider"
    assert result["JsonRPCAction"]["Method"] == "open_cider"


def test_other_errors_are_shown(monkeypatch, server):
    server.search_data = {"songs": {"data": [{"attributes": {}}]}, "albums": {"data": [{}]}}
    (result,) = results("query", "midnight")
    assert result["Title"] == "KeyError"


def test_unanswered_request_times_out_and_closes_the_socket(server):
    nothing_playing = dict(SONG, playParams={"id": "no-id-found", "kind": "song"})
    (result, *_) = results("context_menu", [nothing_playing])
    assert result["Title"] == "TimeoutError"
    assert server.sockets[0].timeout == main.actions.Cider().timeout
    assert server.sockets[0].closed


def test_python_v2_round_trip(monkeypatch, server):
    requests = [
        {"id": 1, "method": "query", "params": [{"search": "midnight", "actionKeyword": "fc"}, {}]},
        {"id": 2, "method": "context_menu", "params": [[SONG]]},
        {"id": 3, "method": "play_media", "params": [[SONG]]},
        {"id": 4, "method": "close", "params": []},
    ]

    async def messages(self):
        for request in requests:
            yield request
            await asyncio.sleep(0.05)

    sent = []
    monkeypatch.setattr(JsonRPCV2Client, "messages", messages)
    monkeypatch.setattr(plugin.launcher._client, "send", sent.append)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        plugin.run()
    finally:
        asyncio.set_event_loop(None)
        loop.close()
    replies = {reply["id"]: reply["result"] for reply in sent}
    assert [r["Title"] for r in replies[1]["result"]][0] == "Midnight City"
    assert replies[2]["result"][0]["Title"] == "Play next"
    assert replies[3] == {}
    assert {"action": "play-mediaitem", "id": "1440845291", "kind": "song"} in server.sent
