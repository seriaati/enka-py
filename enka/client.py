from enum import StrEnum
from typing import Any

import aiohttp

from .exceptions import raise_for_retcode
from .models.response import ShowcaseResponse

BASE_URL = "https://enka.network/api/uid/{uid}/"


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
    def __init__(self, language: Language = Language.ENGLISH) -> None:
        self.language = language

    @classmethod
    async def fetch_showcase(cls, uid: str) -> ShowcaseResponse:
        url = BASE_URL.format(uid=uid)
        async with aiohttp.ClientSession(
            headers={"User-Agent": "Enka to GO"}
        ) as session, session.get(url) as resp:
            if resp.status != 200:
                raise_for_retcode(resp.status)

            data: dict[str, Any] = await resp.json()
            return ShowcaseResponse(**data)
