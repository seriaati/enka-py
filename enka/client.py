import copy
import logging
from typing import TYPE_CHECKING, Any, Final

import aiohttp
import cachetools

from .assets.manager import AssetManager
from .assets.updater import AssetUpdater
from .enums import Element, Language
from .exceptions import raise_for_retcode
from .models.icon import Icon, Namecard
from .models.response import ShowcaseResponse

if TYPE_CHECKING:
    from .models.character import Character
    from .models.player import Player, ShowcaseCharacter

__all__ = ("EnkaAPI",)

LOGGER_ = logging.getLogger("enka.client")


class EnkaAPI:
    """
    The main client for interacting with the Enka Network API.

    Parameters
    ----------
    lang: :class:`Language`
        The language to use for the client, defaults to :attr:`Language.ENGLISH`.
    headers: :class:`dict`[:class:`str`, :class:`Any`] | :class:`None`
        The headers to use for the client, defaults to ``None``.
    cache_maxsize: :class:`int`
        The maximum size of the cache, defaults to ``100``.
    cache_ttl: :class:`int`
        The time to live of the cache, defaults to ``60``.
    """

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

        self._session: aiohttp.ClientSession | None = None
        self._cache: cachetools.TTLCache[str, dict[str, Any]] = cachetools.TTLCache(
            maxsize=self._cache_maxsize, ttl=self._cache_ttl
        )
        self._assets: AssetManager | None = None
        self._asset_updater: AssetUpdater | None = None

        self.GENSHIN_API_URL: Final[str] = "https://enka.network/api/uid/{uid}"
        self.HSR_API_URL: Final[str] = "https://enka.network/api/hsr/uid/{uid}"

    async def __aenter__(self) -> "EnkaAPI":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _request(self, url: str) -> dict[str, Any]:
        if self._session is None:
            msg = "Client is not started, call `EnkaNetworkAPI.start` first"
            raise RuntimeError(msg)

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

    def _post_process_player(self, player: "Player") -> "Player":
        if self._assets is None:
            msg = "Client is not started, call `EnkaNetworkAPI.start` first"
            raise RuntimeError(msg)

        # namecard
        namecard_icon = self._assets.namecard_data[str(player.namecard_id)]["icon"]
        player.namecard = Namecard(namecard_icon)

        # profile picture
        profile_picture_id = str(player.profile_picture_id)
        if len(profile_picture_id) == 8:
            profile_picture_icon = self._assets.character_data[profile_picture_id]["SideIconName"]
        else:
            profile_picture_icon = self._assets.pfps_data[profile_picture_id]["iconPath"]
        player.profile_picture_icon = Icon(profile_picture_icon)

        return player

    def _post_process_showcase_character(
        self, showcase_character: "ShowcaseCharacter"
    ) -> "ShowcaseCharacter":
        if self._assets is None:
            msg = "Client is not started, call `EnkaNetworkAPI.start` first"
            raise RuntimeError(msg)

        if showcase_character.costume_id is None:
            return showcase_character

        costume_data = self._assets.character_data[str(showcase_character.id)]["Costumes"]
        if costume_data is not None:
            showcase_character.costuime_icon = Icon(
                costume_data[str(showcase_character.costume_id)]["sideIconName"]
            )

        return showcase_character

    def _post_process_character(self, character: "Character") -> "Character":
        if self._assets is None:
            msg = "Client is not started, call `EnkaNetworkAPI.start` first"
            raise RuntimeError(msg)

        characer_id = (
            f"{character.id}-{character.skill_depot_id}"
            if character.id in {10000005, 10000007}
            else str(character.id)
        )

        character_data = self._assets.character_data[characer_id]
        # name
        character_name_text_map_hash = character_data["NameTextMapHash"]
        character.name = self._assets.text_map[character_name_text_map_hash]

        # icon
        side_icon_name = character_data["SideIconName"]
        character.icon = Icon(side_icon_name)

        # weapon
        weapon = character.weapon
        weapon.name = self._assets.text_map[weapon.name]
        for stat in weapon.stats:
            stat.name = self._assets.text_map[stat.type.value]

        # artifacts
        for artifact in character.artifacts:
            artifact.name = self._assets.text_map[artifact.name]
            artifact.set_name = self._assets.text_map[artifact.set_name]
            artifact.main_stat.name = self._assets.text_map[artifact.main_stat.type.value]
            for stat in artifact.sub_stats:
                stat.name = self._assets.text_map[stat.type.value]

        # stats
        for stat in character.stats:
            stat.name = self._assets.text_map.get(stat.type.name)

        # constellations
        for constellation in character.constellations:
            const_data = self._assets.consts_data[str(constellation.id)]
            constellation.name = self._assets.text_map[const_data["nameTextMapHash"]]
            constellation.icon = f"https://enka.network/ui/{const_data['icon']}.png"

        # talents
        for talent in character.talents:
            talent_data = self._assets.talents_data[str(talent.id)]
            talent.name = self._assets.text_map[talent_data["nameTextMapHash"]]
            talent.icon = f"https://enka.network/ui/{talent_data['icon']}.png"
            if character.talent_extra_level_map:
                proud_map: dict[str, int] = character_data["ProudMap"]
                proud_id = proud_map.get(str(talent.id))
                if proud_id is None:
                    continue
                talent.level += character.talent_extra_level_map.get(str(proud_id), 0)

        # talent order
        character.talent_order = character_data["SkillOrder"]

        # element
        element = character_data["Element"]
        character.element = Element(element)

        return character

    def _post_process_showcase(self, showcase: ShowcaseResponse) -> ShowcaseResponse:
        showcase.player = self._post_process_player(showcase.player)

        # costume
        showcase_characters: list[ShowcaseCharacter] = []
        for character in showcase.player.showcase_characters:
            showcase_characters.append(self._post_process_showcase_character(character))
        showcase.player.showcase_characters = showcase_characters

        # characters
        characters: list[Character] = []
        for character in showcase.characters:
            characters.append(self._post_process_character(character))

        return showcase

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(headers=self._headers)

        self._assets = AssetManager(self._lang)
        self._asset_updater = AssetUpdater(self._session)

        loaded = await self._assets.load()
        if not loaded:
            await self.update_assets()

    async def close(self) -> None:
        if self._session is None:
            msg = "Client is not started, call `EnkaNetworkAPI.start` first"
            raise RuntimeError(msg)

        await self._session.close()
        self._cache.clear()

    async def update_assets(self) -> None:
        if self._asset_updater is None or self._assets is None:
            msg = "Client is not started, call `EnkaNetworkAPI.start` first"
            raise RuntimeError(msg)

        LOGGER_.info("Updating assets...")

        await self._asset_updater.update()
        await self._assets.load()

        LOGGER_.info("Assets updated")

    async def fetch_showcase(  # noqa: C901, PLR0912
        self, uid: str | int, *, info_only: bool = False
    ) -> ShowcaseResponse:
        """
        Fetches the  Impact character showcase of the given UID.

        Parameters
        ----------
        uid: :class:`str` | :class:`int`
            The UID of the user.
        info_only: :class:`bool`
            Whether to only fetch player info, defaults to ``False``.

        Returns
        -------
        :class:`ShowcaseResponse`
            The response of the showcase.
        """

        url = self.GENSHIN_API_URL.format(uid=uid)
        if info_only:
            url += "?info"

        data = await self._request(url)
        data = copy.deepcopy(data)
        showcase = ShowcaseResponse(**data)
        return self._post_process_showcase(showcase)
