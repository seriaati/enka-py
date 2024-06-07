from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

import aiofiles
import orjson

from ..errors import AssetUpdateError

if TYPE_CHECKING:
    import aiohttp

    from ..enums import gi, hsr

__all__ = ("AssetUpdater",)

LOGGER_ = logging.getLogger(__name__)


class AssetUpdater:
    """Game asset updater."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        source_to_path: dict[str, str],
        lang: gi.Language | hsr.Language,
    ) -> None:
        self._session = session
        self._source_to_path = source_to_path
        self._lang = lang

    async def _fetch_json(self, url: str) -> Any:
        LOGGER_.debug("Fetching %s", url)

        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise AssetUpdateError(resp.status, url)

            return orjson.loads(await resp.read())

    async def update(self) -> None:
        """Update all assets."""
        for source, path in self._source_to_path.items():
            path_ = path.format(lang=self._lang.value)
            if not os.path.exists(os.path.dirname(path_)):
                os.makedirs(os.path.dirname(path_))

            data = await self._fetch_json(source.format(lang=self._lang.value))

            async with aiofiles.open(path_, "w", encoding="utf-8") as f:
                bytes_ = orjson.dumps(data)
                await f.write(bytes_.decode())
