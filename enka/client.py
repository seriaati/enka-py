from enum import StrEnum
from typing import Any, Final

import aiohttp

from .exceptions import raise_for_retcode
from .models.response import GenshinShowcaseResponse


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


class EnkaNetworkAPI:
    def __init__(
        self, language: Language = Language.ENGLISH, headers: dict[str, Any] | None = None
    ) -> None:
        self.language = language
        self.headers = headers

        self.GENSHIN_API_URL: Final[str] = "https://enka.network/api/uid/{uid}"
        self.HSR_API_URL: Final[str] = "https://enka.network/api/hsr/uid/{uid}"

    async def __aenter__(self) -> "EnkaNetworkAPI":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _request(self, url: str) -> dict[str, Any]:
        async with self.session.get(url) as resp:
            if resp.status != 200:
                raise_for_retcode(resp.status)

            return await resp.json()

    async def start(self) -> None:
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def close(self) -> None:
        await self.session.close()

    async def fetch_genshin_showcase(
        self, uid: str, *, info_only: bool = False
    ) -> GenshinShowcaseResponse:
        url = self.GENSHIN_API_URL.format(uid=uid)
        if info_only:
            url += "?info"

        data = await self._request(url)
        return GenshinShowcaseResponse(**data)
