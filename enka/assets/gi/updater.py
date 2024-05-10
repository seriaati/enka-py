from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Final

import aiofiles
import orjson

from ...exceptions import AssetUpdateError
from .file_paths import (
    CHARACTER_DATA_PATH,
    CONSTS_DATA_PATH,
    NAMECARD_DATA_PATH,
    PFPS_DATA_PATH,
    TALENTS_DATA_PATH,
    TEXT_MAP_PATH,
)

if TYPE_CHECKING:
    import aiohttp

__all__ = ("AssetUpdater",)

SOURCE_TO_PATH: Final[dict[str, str]] = {
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/text_map.json": TEXT_MAP_PATH,
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/characters.json": CHARACTER_DATA_PATH,
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/namecards.json": NAMECARD_DATA_PATH,
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/consts.json": CONSTS_DATA_PATH,
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/talents.json": TALENTS_DATA_PATH,
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/pfps.json": PFPS_DATA_PATH,
}

LOGGER_ = logging.getLogger("enka.assets.updater")


class AssetUpdater:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _fetch_json(self, url: str) -> Any:
        LOGGER_.debug("Fetching %s", url)

        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise AssetUpdateError(resp.status, url)

            return orjson.loads(await resp.read())

    async def update(self) -> None:
        for source, path in SOURCE_TO_PATH.items():
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            data = await self._fetch_json(source)

            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                bytes_ = orjson.dumps(data)
                await f.write(bytes_.decode())
