"""Utilities for watching line movement."""

import asyncio
from typing import Awaitable, Callable


async def watch_line(
    get_line: Callable[[], Awaitable[float]],
    threshold: float,
    callback: Callable[[float], Awaitable[None]],
):
    """Poll get_line until the line crosses the threshold."""
    while True:
        line = await get_line()
        if line >= threshold:
            await callback(line)
            break
        await asyncio.sleep(60)
