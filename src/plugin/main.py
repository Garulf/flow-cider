import asyncio
import functools
from typing import Any, Callable, List, TypeVar

import actions
import results
from actions import plugin
from parse_args import parse_args

SEARCH_DELAY = 0.5

T = TypeVar("T")


async def in_thread(func: Callable[..., T], *args: Any) -> T:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args))


@plugin.on_method
async def query(query: str):
    cider = actions.client()
    if not query.strip():
        return await in_thread(results.now_playing, cider)
    await asyncio.sleep(SEARCH_DELAY)
    args, options = parse_args(query)
    if " ".join(args.query).endswith(":"):
        return results.argument_results(options)
    found = await in_thread(cider.search, " ".join(args.query), args.limit)
    return results.search_results(args, found)


@plugin.on_method
async def context_menu(data: List[Any]):
    return await in_thread(results.context_menu_results, actions.client(), data)


@plugin.on_except(Exception)
def show_error(exception: Exception):
    return results.error_results(exception)
