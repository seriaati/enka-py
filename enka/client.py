from typing import Any

import aiohttp

from .exceptions import raise_for_retcode
from .models.response import ShowcaseResponse

BASE_URL = "https://enka.network/api/uid/{uid}/"


class EnkaNetworkAPI:
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
