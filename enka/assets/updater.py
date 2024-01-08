import os
from typing import TYPE_CHECKING, Any, Final

import aiofiles
import orjson

from ..exceptions import AssetUpdateError
from .file_paths import CHARACTER_DATA_PATH, TEXT_MAP_PATH

if TYPE_CHECKING:
    import aiohttp

__all__ = ("AssetUpdater",)


class AssetUpdater:
    def __init__(self, session: "aiohttp.ClientSession") -> None:
        self._session = session

        self.TEXT_MAP: Final[
            str
        ] = "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/text_map.json"
        self.CHARACTER_DATA: Final[
            str
        ] = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json"

    async def _fetch_json(self, url: str) -> Any:
        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise AssetUpdateError(resp.status, url)

            return orjson.loads(await resp.read())

    async def update(self) -> None:
        text_map = await self._fetch_json(self.TEXT_MAP)
        characters = await self._fetch_json(self.CHARACTER_DATA)

        data_to_save: dict[str, str] = {
            TEXT_MAP_PATH: text_map,
            CHARACTER_DATA_PATH: characters,
        }
        for path, data in data_to_save.items():
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                bytes_ = orjson.dumps(data)
                await f.write(bytes_.decode())
