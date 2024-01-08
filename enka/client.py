import logging
from enum import StrEnum
from typing import Any, Final

import aiohttp

from .assets.text_map import TextMap
from .assets.updater import AssetUpdater
from .exceptions import raise_for_retcode
from .models.response import GenshinShowcaseResponse

LOGGER_ = logging.getLogger("enka-py.client")


class Language(StrEnum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    VIETNAMESE = "vi"
    THAI = "th"
    PORTUGUESE = "pt"
    KOREAN = "ko"
    JAPANESE = "ja"
    INDONESIAN = "id"
    FRENCH = "fr"
    SPANISH = "es"
    GERMAN = "de"
    TRADITIONAL_CHINESE = "zh-tw"
    SIMPLIFIED_CHINESE = "zh-cn"
    ITALIAN = "it"
    TURKISH = "tr"


class EnkaAPI:
    def __init__(
        self, language: Language = Language.ENGLISH, headers: dict[str, Any] | None = None
    ) -> None:
        self.language = language
        self.headers = headers

        self.GENSHIN_API_URL: Final[str] = "https://enka.network/api/uid/{uid}"
        self.HSR_API_URL: Final[str] = "https://enka.network/api/hsr/uid/{uid}"

    async def __aenter__(self) -> "EnkaAPI":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _request(self, url: str) -> dict[str, Any]:
        LOGGER_.debug("Requesting %s", url)

        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise_for_retcode(resp.status)

            return await resp.json()

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(headers=self.headers)

        self.text_map = TextMap(self.language)
        self.asset_updater = AssetUpdater(self._session)

        await self.text_map.load()
        if self.text_map.text_map is None:
            await self.update_assets()

    async def close(self) -> None:
        await self._session.close()

    async def update_assets(self) -> None:
        LOGGER_.info("Updating assets...")

        await self.asset_updater.update()
        await self.text_map.load()

        LOGGER_.info("Assets updated")

    async def fetch_genshin_showcase(
        self, uid: str, *, info_only: bool = False
    ) -> GenshinShowcaseResponse:
        url = self.GENSHIN_API_URL.format(uid=uid)
        if info_only:
            url += "?info"

        data = await self._request(url)
        return GenshinShowcaseResponse(**data)
