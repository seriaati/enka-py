import logging
from typing import Any, Final

import aiohttp
import cachetools

from .assets.manager import AssetManager
from .assets.updater import AssetUpdater
from .enums import Language
from .exceptions import raise_for_retcode
from .models.character import CharacterCostume
from .models.response import GenshinShowcaseResponse

__all__ = ("EnkaAPI",)

LOGGER_ = logging.getLogger("enka-py.client")


class EnkaAPI:
    def __init__(
        self,
        lang: Language = Language.ENGLISH,
        headers: dict[str, Any] | None = None,
        cache_maxsize: int = 100,
        cache_ttl: int = 60,
    ) -> None:
        self._lang = lang
        self._headers = headers
        self._cache_maxsize = cache_maxsize
        self._cache_ttl = cache_ttl

        self.GENSHIN_API_URL: Final[str] = "https://enka.network/api/uid/{uid}"
        self.HSR_API_URL: Final[str] = "https://enka.network/api/hsr/uid/{uid}"

    async def __aenter__(self) -> "EnkaAPI":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _request(self, url: str) -> dict[str, Any]:
        LOGGER_.debug("Requesting %s", url)

        if url in self._cache:
            LOGGER_.debug("Using cache for %s", url)
            return self._cache[url]

        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise_for_retcode(resp.status)

            data: dict[str, Any] = await resp.json()
            self._cache[url] = data
            return data

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(headers=self._headers)
        self._cache: cachetools.TTLCache[str, dict[str, Any]] = cachetools.TTLCache(
            maxsize=self._cache_maxsize, ttl=self._cache_ttl
        )

        self._asset_manager = AssetManager(self._lang)
        self._asset_updater = AssetUpdater(self._session)

        loaded = await self._asset_manager.load()
        if not loaded:
            await self.update_assets()

        self._text_map = self._asset_manager.text_map
        self._character_data = self._asset_manager.character_data

    async def close(self) -> None:
        await self._session.close()
        self._cache.clear()

    async def update_assets(self) -> None:
        LOGGER_.info("Updating assets...")

        await self._asset_updater.update()
        await self._asset_manager.load()

        LOGGER_.info("Assets updated")

    async def fetch_genshin_showcase(
        self, uid: str | int, *, info_only: bool = False
    ) -> GenshinShowcaseResponse:
        url = self.GENSHIN_API_URL.format(uid=uid)
        if info_only:
            url += "?info"

        data = await self._request(url)
        showcase_response = GenshinShowcaseResponse(**data)

        # Post-processing
        for character in showcase_response.characters:
            character_name_text_map_hash = self._character_data[str(character.id)][
                "NameTextMapHash"
            ]
            character.name = self._text_map[character_name_text_map_hash]
            side_icon_name = self._character_data[str(character.id)]["SideIconName"]
            character.side_icon = f"https://enka.network/ui/{side_icon_name}.png"
            character.costumes = [
                CharacterCostume(
                    id=costume_id,
                    side_icon=f"https://enka.network/ui/{costume_data['sideIconName']}.png",
                )
                for costume_id, costume_data in self._character_data[str(character.id)]
                .get("Costumes", {})
                .items()
            ]

            weapon = character.weapon
            weapon.name = self._text_map[weapon.name]
            for stat in weapon.stats:
                stat.name = self._text_map[stat.type.value]

            for artifact in character.artifacts:
                artifact.name = self._text_map[artifact.name]
                artifact.set_name = self._text_map[artifact.set_name]
                artifact.main_stat.name = self._text_map[artifact.main_stat.type.value]
                for stat in artifact.sub_stats:
                    stat.name = self._text_map[stat.type.value]

        return showcase_response
