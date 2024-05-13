from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Final

import aiofiles
import orjson

from ..errors import AssetUpdateError
from .hsr.file_paths import CHARACTER_DATA_PATH, SKILL_TREE_DATA_PATH, TEXT_MAP_PATH

if TYPE_CHECKING:
    import aiohttp

__all__ = ("AssetUpdater",)

SOURCE_TO_PATH: Final[dict[str, str]] = {
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/hsr/hsr.json": TEXT_MAP_PATH,
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/hsr/honker_characters.json": CHARACTER_DATA_PATH,
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/hsr/skill_tree.json": SKILL_TREE_DATA_PATH,
}

LOGGER_ = logging.getLogger(__name__)


class AssetUpdater:
    """Game asset updater."""

    def __init__(self, session: aiohttp.ClientSession, source_to_path: dict[str, str]) -> None:
        self._session = session
        self._source_to_path = source_to_path

    async def _fetch_json(self, url: str) -> Any:
        LOGGER_.debug("Fetching %s", url)

        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise AssetUpdateError(resp.status, url)

            return orjson.loads(await resp.read())

    async def update(self) -> None:
        """Update all assets."""
        for source, path in self._source_to_path.items():
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            data = await self._fetch_json(source)

            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                bytes_ = orjson.dumps(data)
                await f.write(bytes_.decode())
