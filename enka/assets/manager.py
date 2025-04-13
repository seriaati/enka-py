from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    import aiohttp

    from .data import AssetData

__all__ = ("AssetManager",)


class AssetManager:
    """Base asset manager."""

    def __init__(self) -> None:
        self._assets: Sequence[AssetData] = ()

    async def load(self, session: aiohttp.ClientSession) -> None:
        tasks: list[asyncio.Task[None]] = [
            asyncio.create_task(asset.load(session)) for asset in self._assets
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    def clear(self) -> None:
        for asset in self._assets:
            asset._data = None

    async def update(self, session: aiohttp.ClientSession) -> None:
        tasks: list[asyncio.Task[None]] = [
            asyncio.create_task(asset.update(session)) for asset in self._assets
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
