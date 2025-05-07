from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Final, Literal, overload

from loguru import logger

from ..assets.data import TextMap
from ..assets.hsr.manager import HSR_ASSETS
from ..calc.hsr import LayerGenerator, PropState
from ..enums.enum import Game
from ..enums.hsr import Element, Language, Path, StatType, TraceType
from ..models.hsr import CharacterIcon, LightConeIcon, Player, ShowcaseResponse, Stat
from ..models.hsr.build import Build
from ..models.hsr.character import Eidolon
from .base import BaseClient

if TYPE_CHECKING:
    from ..models.enka.owner import Owner
    from ..models.hsr.character import Character, LightCone, Relic, Trace
    from .cache import BaseTTLCache

__all__ = ("HSRClient",)

API_URL: Final[str] = "https://enka.network/api/hsr/uid/{uid}"


class HSRClient(BaseClient):
    """The main client to interact with the Enka Network Honkai Star Rail API.

    Args:
        lang (Language | str): The language to use for the client, defaults to Language.ENGLISH.
        headers (dict[str, Any] | None): The headers to use for the client, defaults to None.
        cache (BaseTTLCache | None): The cache to use for the client, defaults to None.
        use_enka_icons (bool): Whether to get stat icons from Enka, defaults to True.
    """

    def __init__(
        self,
        lang: Language | str = Language.ENGLISH,
        *,
        headers: dict[str, Any] | None = None,
        cache: BaseTTLCache | None = None,
        use_enka_icons: bool = True,
    ) -> None:
        super().__init__(Game.HSR, headers=headers, cache=cache)

        self._lang = self._convert_lang(lang)
        self._use_enka_icons = use_enka_icons
        self._assets = HSR_ASSETS

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

    async def __aenter__(self) -> HSRClient:
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    def _post_process_relic(self, relic: Relic) -> None:
        text_map = self._text_map
        relic.set_name = text_map[relic.set_name]

        relic_data = self._assets.relic_data[str(relic.id)]
        relic.icon = self._get_icon(relic_data["Icon"])
        relic.rarity = relic_data["Rarity"]

        for stat in relic.stats:
            stat.name = text_map[stat.type.value]
            stat.icon = self._get_icon(
                self._assets.property_config_data[stat.type.value], enka=self._use_enka_icons
            )

    def _post_process_light_cone(self, light_cone: LightCone) -> None:
        text_map = self._text_map
        data = self._assets.light_cones_data[str(light_cone.id)]

        light_cone.name = text_map[light_cone.name]
        light_cone.rarity = data["Rarity"]
        light_cone.icon = LightConeIcon(light_cone_id=light_cone.id)
        light_cone.path = Path(data["AvatarBaseType"])

        for stat in light_cone.stats:
            stat.name = text_map[stat.type.value]
            stat.icon = self._get_icon(
                self._assets.property_config_data[stat.type.value], enka=self._use_enka_icons
            )

    def _post_process_trace(self, trace: Trace, unlocked_eidolon_ids: list[int]) -> None:
        skill_tree_data = self._assets.skill_tree_data
        trace_data = skill_tree_data[str(trace.id)]

        try:
            skill_ids: list[int] = trace_data["skillIds"]
        except KeyError as e:
            msg = "Skill IDs not found in trace data, please update the assets with `update_assets`"
            raise RuntimeError(msg) from e

        trace.anchor = trace_data["anchor"]
        trace.icon = self._get_icon(
            trace_data["icon"], enka=self._use_enka_icons or "SkillIcons" in trace_data["icon"]
        )
        trace.type = TraceType(trace_data["pointType"])
        trace.max_level = trace_data["maxLevel"]

        for eidolon_id in unlocked_eidolon_ids:
            eidolon_data = self._assets.eidolon_data[str(eidolon_id)]

            for skill_id in skill_ids:
                if str(skill_id) in eidolon_data["SkillAddLevelList"]:
                    trace.level += eidolon_data["SkillAddLevelList"][str(skill_id)]
                    trace.boosted = True
                    break

    def _post_process_character(self, character: Character) -> None:
        character.icon = CharacterIcon(character_id=character.id)

        character_data = self._assets.character_data[str(character.id)]
        text_map_hash = character_data["AvatarName"]["Hash"]
        character.name = self._text_map[text_map_hash]
        character.rarity = character_data["Rarity"]
        character.element = Element(character_data["Element"])
        character.path = Path(character_data["AvatarBaseType"])

        # Eidolons
        eidolon_ids: list[int] = character_data["RankIDList"]
        for i, eidolon_id in enumerate(eidolon_ids, start=1):
            eidolon_data = self._assets.eidolon_data[str(eidolon_id)]
            character.eidolons.append(
                Eidolon(
                    id=eidolon_id,
                    icon=self._get_icon(eidolon_data["IconPath"]),
                    unlocked=i <= character.eidolons_unlocked,
                )
            )

        for trace in character.traces:
            self._post_process_trace(
                trace, [e.id for e in character.eidolons[: character.eidolons_unlocked]]
            )
        for relic in character.relics:
            self._post_process_relic(relic)
        if character.light_cone is not None:
            self._post_process_light_cone(character.light_cone)

        # Credit to Enka Network for the following code
        generator = LayerGenerator(self._assets)
        prop_state = PropState()

        prop_state.add(generator.character(character))
        if character.light_cone is not None:
            prop_state.add(generator.light_cone(character.light_cone))

            if character.light_cone.path == character.path:
                prop_state.add(generator.light_cone_skill(character.light_cone))

        prop_state.add(generator.relics(character.relics))
        prop_state.add(generator.relic_set(character.relics))
        prop_state.add(generator.skill_tree(character))

        props = prop_state.sum()

        final_stats: dict[StatType, float] = {
            StatType.MAX_HP: props.hp,
            StatType.ATK: props.attack,
            StatType.DEF: props.defence,
            StatType.SPD: props.speed,
            StatType.CRIT_RATE: props.critical_chance,
            StatType.CRIT_DMG: props.critical_damage,
            StatType.BREAK_EFFECT: props.break_damage,
            StatType.HEALING_BOOST: props.heal_ratio,
            StatType.ENERGY_REGEN_RATE: props.sp_ratio,
            StatType.EFFECT_HIT_RATE: props.status_probability,
            StatType.EFFECT_RES: props.status_resistance,
            StatType.PHYSICAL_DMG_BOOST: props.physical_damage,
            StatType.FIRE_DMG_BOOST: props.fire_damage,
            StatType.ICE_DMG_BOOST: props.ice_damage,
            StatType.LIGHTNING_DMG_BOOST: props.thunder_damage,
            StatType.WIND_DMG_BOOST: props.wind_damage,
            StatType.QUANTUM_DMG_BOOST: props.quantum_damage,
            StatType.IMAGINARY_DMG_BOOST: props.imaginary_damage,
        }

        character.stats = {
            stat_type: Stat(
                type=stat_type,
                value=value,
                name=self._text_map[stat_type.value],
                icon=self._get_icon(
                    self._assets.property_config_data[stat_type.value], enka=self._use_enka_icons
                ),
            )
            for stat_type, value in final_stats.items()
        }

    def _post_process_player(self, player: Player) -> None:
        player.icon = self._get_icon(self._assets.avatar_data[player.icon]["Icon"])

    def _post_process_showcase(self, showcase: ShowcaseResponse) -> None:
        for character in showcase.characters:
            self._post_process_character(character)
        self._post_process_player(showcase.player)

    def _get_icon(self, icon: str, *, enka: bool = True) -> str:
        icon = icon.replace(".png", "")
        if enka:
            return f"https://enka.network/ui/hsr/{icon}.png"
        return f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/property/{icon.split('/')[-1]}.png"

    async def start(self) -> None:
        await super().start()
        await self._assets.load(self.session)
        self._text_map = TextMap(self.lang, self._assets.text_map)

    async def update_assets(self) -> None:
        """Update game assets."""
        logger.info("Updating HSR assets")
        await self._assets.update(self.session)
        self._text_map = TextMap(self.lang, self._assets.text_map)
        logger.info("HSR assets updated")

    @overload
    async def fetch_showcase(
        self, uid: str | int, *, raw: Literal[False] = False
    ) -> ShowcaseResponse: ...
    @overload
    async def fetch_showcase(
        self, uid: str | int, *, raw: Literal[True] = True
    ) -> dict[str, Any]: ...
    async def fetch_showcase(
        self, uid: str | int, *, raw: bool = False
    ) -> ShowcaseResponse | dict[str, Any]:
        """Fetch the player showcase of the given UID.

        Args:
            uid: The UID of the user.
            raw: Whether to return the raw data, defaults to False.

        Returns:
            The parsed or raw showcase data.
        """
        url = API_URL.format(uid=uid)

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
