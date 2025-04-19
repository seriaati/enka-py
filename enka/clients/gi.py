from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Final, Literal, overload

from loguru import logger

from ..assets.data import TextMap
from ..assets.gi.manager import GI_ASSETS
from ..constants.gi import CHARACTER_RARITY_MAP
from ..enums.enum import Game
from ..enums.gi import Element, FightPropType, Language
from ..models.gi import Constellation, Costume, Icon, Namecard, ShowcaseResponse
from ..models.gi.build import Build
from .base import BaseClient

if TYPE_CHECKING:
    from ..models.enka.owner import Owner
    from ..models.gi.character import Character
    from ..models.gi.player import Player, ShowcaseCharacter
    from .cache import BaseTTLCache

__all__ = ("GenshinClient",)

API_URL: Final[str] = "https://enka.network/api/uid/{uid}"


class GenshinClient(BaseClient):
    """The main client to interact with the Enka Network Genshin Impact API.

    Args:
        lang: The language to use for the client, defaults to Language.ENGLISH.
        headers: The headers to use for the client, defaults to None.
        cache: The cache to use for the client, defaults to None.
    """

    def __init__(
        self,
        lang: Language | str = Language.ENGLISH,
        *,
        headers: dict[str, Any] | None = None,
        cache: BaseTTLCache | None = None,
    ) -> None:
        super().__init__(Game.GI, headers=headers, cache=cache)

        self._lang = self._convert_lang(lang)
        self._assets = GI_ASSETS

    def _convert_lang(self, lang: Language | str) -> Language:
        if not isinstance(lang, Language):
            try:
                lang = Language(lang)
            except ValueError as e:
                available_langs = ", ".join(lang.value for lang in Language)
                msg = f"Invalid language: {lang}, must be one of {available_langs}"
                raise ValueError(msg) from e

        return lang

    @property
    def lang(self) -> Language:
        return self._lang

    @lang.setter
    def lang(self, lang: Language | str) -> None:
        self._lang = self._convert_lang(lang)
        self._text_map = TextMap(self._lang, self._assets.text_map)

    async def __aenter__(self) -> GenshinClient:
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    def _post_process_player(self, player: Player) -> None:
        # namecard
        namecard_icon = self._assets.namecard_data[str(player.namecard_id)]["icon"]
        player.namecard = Namecard(ui_path=namecard_icon)

        # profile picture
        profile_picture_id = str(player.profile_picture_id)
        if len(profile_picture_id) == 8:
            profile_picture_icon = self._assets.character_data[profile_picture_id]["SideIconName"]
        else:
            # pfps data always return circle icon, so we need to process it to side icon for the `Icon` object.
            profile_picture_icon = (
                self._assets.pfps_data[profile_picture_id]["iconPath"]
                .replace("AvatarIcon", "AvatarIcon_Side")
                .replace("_Circle", "")
            )
        player.profile_picture_icon = Icon(
            side_icon_ui_path=profile_picture_icon, is_costume="Costume" in profile_picture_icon
        )

    def _post_process_showcase_character(self, showcase_character: ShowcaseCharacter) -> None:
        if showcase_character.costume_id is None:
            return

        # costume
        costume_data = self._assets.character_data[str(showcase_character.id)]["Costumes"]
        if costume_data is not None:
            showcase_character.costume = Costume(
                id=showcase_character.costume_id,
                data=costume_data[str(showcase_character.costume_id)],
            )

    def _post_process_character(self, character: Character) -> None:  # noqa: PLR0912
        characer_id = (
            f"{character.id}-{character.skill_depot_id}"
            if character.id in {10000005, 10000007}
            else str(character.id)
        )

        character_data = self._assets.character_data[characer_id]
        # name
        character_name_text_map_hash = character_data["NameTextMapHash"]
        character.name = self._text_map[character_name_text_map_hash]

        # icon
        side_icon_name = character_data["SideIconName"]
        character.icon = Icon(side_icon_ui_path=side_icon_name)

        # weapon
        weapon = character.weapon
        weapon.name = self._text_map[weapon.name]
        for stat in weapon.stats:
            stat.name = self._text_map[stat.type.value]

        # artifacts
        for artifact in character.artifacts:
            artifact.name = self._text_map[artifact.name]
            artifact.set_name = self._text_map[artifact.set_name]
            artifact.main_stat.name = self._text_map[artifact.main_stat.type.value]
            for stat in artifact.sub_stats:
                stat.name = self._text_map[stat.type.value]

        # stats
        for stat_type, stat in character.stats.items():
            if not isinstance(stat_type, FightPropType):
                continue
            stat.name = self._text_map.get(stat_type.name)

        # constellations
        all_consts: list[dict[str, str]] = []
        for const_id, const in self._assets.consts_data.items():
            if const["icon"] not in character_data["Consts"]:
                continue
            const["id"] = const_id
            all_consts.append(const)

        consts: list[Constellation] = [
            Constellation(
                id=int(const["id"]),
                name=self._text_map[const["nameTextMapHash"]],
                icon=f"https://enka.network/ui/{const['icon']}.png",
                unlocked=any(const["id"] == str(c.id) for c in character.constellations),
            )
            for const in all_consts
        ]
        character.constellations = consts

        # talents
        for talent in character.talents:
            talent_data = self._assets.talents_data[str(talent.id)]
            talent.name = self._text_map[talent_data["nameTextMapHash"]]
            talent.icon = f"https://enka.network/ui/{talent_data['icon']}.png"
            if character.talent_extra_level_map:
                proud_map: dict[str, int] = character_data["ProudMap"]
                proud_id = proud_map.get(str(talent.id))
                if proud_id is None:
                    continue
                if extra_level := character.talent_extra_level_map.get(str(proud_id), 0):
                    talent.level += extra_level
                    talent.is_upgraded = True

        # talent order
        character.talent_order = character_data["SkillOrder"]

        # element
        element = character_data["Element"]
        character.element = Element(element)

        # rarity
        character.rarity = CHARACTER_RARITY_MAP[character_data["QualityType"]]

        # namecard
        ui_path = character_data.get("NamecardIcon")
        if ui_path is not None:
            character.namecard = Namecard(ui_path=ui_path)

        # costume
        if character.costume_id is not None:
            costume_data = character_data.get("Costumes")
            if costume_data is not None:
                character.costume = Costume(
                    id=character.costume_id, data=costume_data[str(character.costume_id)]
                )

    def _post_process_showcase(self, showcase: ShowcaseResponse) -> None:
        # player
        self._post_process_player(showcase.player)

        # showcase characters
        for character in showcase.player.showcase_characters:
            self._post_process_showcase_character(character)

        # characters
        for character in showcase.characters:
            self._post_process_character(character)

    async def start(self) -> None:
        await super().start()
        await self._assets.load(self.session)
        self._text_map = TextMap(self.lang, self._assets.text_map)

    async def update_assets(self) -> None:
        """Update game assets."""
        logger.info("Updating GI assets")
        await self._assets.update(self.session)
        self._text_map = TextMap(self.lang, self._assets.text_map)
        logger.info("GI assets updated")

    @overload
    async def fetch_showcase(
        self, uid: str | int, *, info_only: bool = False, raw: Literal[False] = False
    ) -> ShowcaseResponse: ...
    @overload
    async def fetch_showcase(
        self, uid: str | int, *, info_only: bool = False, raw: Literal[True] = True
    ) -> dict[str, Any]: ...
    async def fetch_showcase(
        self, uid: str | int, *, info_only: bool = False, raw: bool = False
    ) -> ShowcaseResponse | dict[str, Any]:
        """Fetch the player showcase of the given UID.

        Args:
            uid: The UID of the user.
            info_only: Whether to only fetch player info, defaults to False.
            raw: Whether to return the raw data, defaults to False.

        Returns:
            The parsed or raw showcase data.
        """
        url = API_URL.format(uid=uid)
        if info_only:
            url += "?info"

        data = await self._request(url)
        if raw:
            return data

        data = copy.deepcopy(data)
        showcase = ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase

    def parse_showcase(self, data: dict[str, Any]) -> ShowcaseResponse:
        """Parse the given showcase data.

        Args:
            data: The showcase data.

        Returns:
            The parsed showcase response.
        """
        data = copy.deepcopy(data)
        showcase = ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase

    async def fetch_builds(self, owner: Owner) -> dict[str, list[Build]]:
        """Fetch the character builds of the given owner.

        Args:
            owner: The owner of the builds.

        Returns:
            Character ID to list of builds mapping.
        """
        url = f"https://enka.network/api/profile/{owner.username}/hoyos/{owner.hash}/builds/"
        data = await self._request(url)
        result: dict[str, list[Build]] = {}

        for key, builds in data.items():
            result[key] = []
            for build in builds:
                build_ = Build(**build)
                self._post_process_character(build_.character)
                result[key].append(build_)

        return result
