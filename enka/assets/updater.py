import os
from typing import TYPE_CHECKING, Final

import aiofiles
import orjson

from .file_paths import TEXT_MAP_PATH

if TYPE_CHECKING:
    import aiohttp


class AssetUpdater:
    def __init__(self, session: "aiohttp.ClientSession") -> None:
        self.session = session

        self.TEXT_MAP: Final[
            str
        ] = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json"

    async def fetch_text_map(self) -> dict[str, dict[str, str]]:
        async with self.session.get(self.TEXT_MAP) as resp:
            return orjson.loads(await resp.read())

    async def update(self) -> None:
        text_map = await self.fetch_text_map()

        if not os.path.exists(os.path.dirname(TEXT_MAP_PATH)):
            os.makedirs(os.path.dirname(TEXT_MAP_PATH))

        async with aiofiles.open(TEXT_MAP_PATH, "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(text_map)
            await f.write(bytes_.decode())
