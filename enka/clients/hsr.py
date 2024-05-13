from __future__ import annotations

import copy
import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Final

from ..assets.hsr.file_paths import SOURCE_TO_PATH
from ..assets.hsr.manager import AssetManager
from ..assets.updater import AssetUpdater
from ..constants.hsr import DEFAULT_STATS
from ..enums.enum import Game
from ..enums.hsr import Element, Language, Path, StatType, TraceType
from ..models.hsr import CharacterIcon, LightConeIcon, Player, ShowcaseResponse, Stat
from ..utils import update_stats
from .base import BaseClient

if TYPE_CHECKING:
    from ..models.hsr.character import Character, LightCone, Relic, Trace

__all__ = ("HSRClient",)

LOGGER_ = logging.getLogger(__name__)
API_URL: Final[str] = "https://enka.network/api/hsr/uid/{uid}"


class HSRClient(BaseClient):
    """The main client to interact with the Enka Network Honkai Star Rail API.

    Args:
        lang (Language): The language to use for the client, defaults to Language.ENGLISH.
        headers (dict[str, Any] | None): The headers to use for the client, defaults to None.
        cache_ttl (int): The time to live of the cache, defaults to 60.
    """

    def __init__(
        self,
        lang: Language = Language.ENGLISH,
        *,
        headers: dict[str, Any] | None = None,
        cache_ttl: int = 60,
    ) -> None:
        super().__init__(Game.GI, headers=headers, cache_ttl=cache_ttl)
        self._lang = lang

    async def __aenter__(self) -> HSRClient:
        await self.start()
        return self

    def _check_assets(self) -> None:
        if self._assets is None:
            msg = f"Client is not started, call `{self.__class__.__name__}.start` first"
            raise RuntimeError(msg)

    def _post_process_relic(self, relic: Relic) -> None:
        text_map = self._assets.text_map
        relic.set_name = text_map[relic.set_name]

        relic_data = self._assets.relic_data[str(relic.id)]
        relic.icon = self._get_icon(relic_data["Icon"])
        relic.rarity = relic_data["Rarity"]

        for stat in relic.stats:
            stat.name = text_map[stat.type.value]
            stat.icon = self._get_icon(self._assets.property_config_data[stat.type.value])

    def _post_process_light_cone(self, light_cone: LightCone) -> None:
        text_map = self._assets.text_map
        light_cone.name = text_map[light_cone.name]
        light_cone.rarity = self._assets.light_cones_data[str(light_cone.id)]["Rarity"]
        light_cone.icon = LightConeIcon(light_cone.id)

        for stat in light_cone.stats:
            stat.name = text_map[stat.type.value]
            stat.icon = self._get_icon(self._assets.property_config_data[stat.type.value])

    def _post_process_trace(self, trace: Trace) -> None:
        skill_tree_data = self._assets.skill_tree_data
        trace_data = skill_tree_data[str(trace.id)]

        trace.anchor = trace_data["anchor"]
        trace.icon = self._get_icon(trace_data["icon"])
        trace.type = TraceType(trace_data["pointType"])
        trace.max_level = trace_data["maxLevel"]

    def _post_process_character(self, character: Character) -> None:
        self._check_assets()

        for trace in character.traces:
            self._post_process_trace(trace)
        for relic in character.relics:
            self._post_process_relic(relic)
        if character.light_cone is not None:
            self._post_process_light_cone(character.light_cone)

        character.icon = CharacterIcon(character.id)

        character_data = self._assets.character_data[str(character.id)]
        text_map_hash: int = character_data["AvatarName"]["Hash"]
        character.name = self._assets.text_map[str(text_map_hash)]
        character.rarity = character_data["Rarity"]
        character.element = Element(character_data["Element"])
        character.path = Path(character_data["AvatarBaseType"])

        # Credits to Algoinde for the following code
        chara_stats = self._add_up_character_stats(character)
        final_stats: dict[StatType, float] = {
            StatType.MAX_HP: (
                chara_stats["BaseHP"]
                + chara_stats["HPBase"]
                + chara_stats["HPAdd"] * (character.level - 1)
            )
            * (1 + chara_stats["HPAddedRatio"])
            + chara_stats["HPDelta"]
            + chara_stats["HPConvert"],
            StatType.ATK: (
                chara_stats["BaseAttack"]
                + chara_stats["AttackBase"]
                + chara_stats["AttackAdd"] * (character.level - 1)
            )
            * (1 + chara_stats["AttackAddedRatio"])
            + chara_stats["AttackDelta"]
            + chara_stats["AttackConvert"],
            StatType.DEF: (
                chara_stats["BaseDefence"]
                + chara_stats["DefenceBase"]
                + chara_stats["DefenceAdd"] * (character.level - 1)
            )
            * (1 + chara_stats["DefenceAddedRatio"])
            + chara_stats["DefenceDelta"]
            + chara_stats["DefenceConvert"],
            StatType.SPD: (chara_stats["BaseSpeed"] + chara_stats["SpeedBase"])
            * (1 + chara_stats["SpeedAddedRatio"])
            + chara_stats["SpeedDelta"]
            + chara_stats["SpeedConvert"],
            StatType.CRIT_RATE: chara_stats["CriticalChanceBase"] + chara_stats["CriticalChance"],
            StatType.CRIT_DMG: chara_stats["CriticalDamageBase"] + chara_stats["CriticalDamage"],
            StatType.BREAK_EFFECT: chara_stats["BreakDamageAddedRatioBase"]
            + chara_stats["BreakDamageAddedRatio"],
            StatType.HEALING_BOOST: chara_stats["HealRatioBase"] + chara_stats["HealRatioConvert"],
            StatType.ENERGY_REGEN_RATE: chara_stats["SPRatioBase"]
            + chara_stats["SPRatio"]
            + chara_stats["SPRatioConvert"]
            + 1,
            StatType.EFFECT_HIT_RATE: chara_stats["StatusProbabilityBase"]
            + chara_stats["StatusProbability"]
            + chara_stats["StatusProbabilityConvert"],
            StatType.EFFECT_RES: chara_stats["StatusResistanceBase"]
            + chara_stats["StatusResistance"]
            + chara_stats["StatusResistanceConvert"],
            StatType.FIRE_DMG_BOOST: chara_stats["FireAddedRatio"],
            StatType.ICE_DMG_BOOST: chara_stats["IceAddedRatio"],
            StatType.LIGHTNING_DMG_BOOST: chara_stats["ThunderAddedRatio"],
            StatType.WIND_DMG_BOOST: chara_stats["WindAddedRatio"],
            StatType.QUANTUM_DMG_BOOST: chara_stats["QuantumAddedRatio"],
            StatType.IMAGINARY_DMG_BOOST: chara_stats["ImaginaryAddedRatio"],
            StatType.PHYSICAL_DMG_BOOST: chara_stats["PhysicalAddedRatio"],
        }

        character.stats = [
            Stat(
                type=stat_type,
                value=value,
                name=self._assets.text_map[stat_type.value],
                icon=self._get_icon(self._assets.property_config_data[stat_type.value]),
            )
            for stat_type, value in final_stats.items()
        ]

    def _add_up_character_stats(self, character: Character) -> dict[str, float]:  # noqa: C901
        chara_stats = DEFAULT_STATS.copy()

        # Add base stats
        chara_meta: dict[str, float] = self._assets.meta_data["avatar"][str(character.id)][
            str(character.ascension)
        ]
        update_stats(chara_stats, chara_meta)

        # Add light cone stats
        if character.light_cone is not None:
            lc = character.light_cone

            lc_meta: dict[str, float] = self._assets.meta_data["equipment"][str(lc.id)][
                str(lc.ascension)
            ]
            update_stats(chara_stats, lc_meta)

            # Add light cone skill stats
            lc_skill_meta_ = self._assets.meta_data["equipmentSkill"]
            if str(lc.id) in lc_skill_meta_:
                lc_skill_meta: dict[str, float] = lc_skill_meta_[str(lc.id)][str(lc.superimpose)][
                    "props"
                ]
                update_stats(chara_stats, lc_skill_meta)

        # Add relic stats
        relic_sets: defaultdict[int, int] = defaultdict(int)
        for relic in character.relics:
            relic_sets[relic.set_id] += 1

            for stat in relic.stats:
                update_stats(chara_stats, {stat.type.value: stat.value})

        # Add relic set stats
        for relic_set_id, count in relic_sets.items():
            if count not in {2, 4}:
                continue

            relic_set_meta: dict[str, float] = self._assets.meta_data["relic"]["setSkill"][
                str(relic_set_id)
            ][str(count)]["props"]
            if relic_set_meta is not None:
                update_stats(chara_stats, relic_set_meta)

        # Add trace stats
        for trace in character.traces:
            trace_meta_ = self._assets.meta_data["tree"]
            if str(trace.id) in trace_meta_:
                trace_meta: dict[str, float] = trace_meta_[str(trace.id)][str(trace.level)]["props"]
                update_stats(chara_stats, trace_meta)

        return chara_stats

    def _post_process_player(self, player: Player) -> None:
        self._check_assets()

        player.icon = self._get_icon(self._assets.avatar_data[player.icon]["Icon"])

    def _post_process_showcase(self, showcase: ShowcaseResponse) -> None:
        for character in showcase.characters:
            self._post_process_character(character)
        self._post_process_player(showcase.player)

    def _get_icon(self, icon: str) -> str:
        icon = icon.replace(".png", "")
        return f"https://enka.network/ui/hsr/{icon}.png"

    async def start(self) -> None:
        """Start the client."""
        await super().start()
        assert self._session is not None

        self._assets = AssetManager(self._lang)
        self._asset_updater = AssetUpdater(self._session, SOURCE_TO_PATH)

        loaded = await self._assets.load()
        if not loaded:
            await self.update_assets()

    async def update_assets(self) -> None:
        """Update game assets."""
        if self._asset_updater is None or self._assets is None:
            msg = f"Client is not started, call `{self.__class__.__name__}.start` first"
            raise RuntimeError(msg)

        LOGGER_.info("Updating assets...")

        await self._asset_updater.update()
        await self._assets.load()

        LOGGER_.info("Assets updated")

    async def fetch_showcase(self, uid: str | int) -> ShowcaseResponse:
        """Fetches the Impact character showcase of the given UID.

        Args:
            uid (str | int): The UID of the user.

        Returns:
            ShowcaseResponse: The response of the showcase.
        """
        url = API_URL.format(uid=uid)

        data = await self._request(url)
        data = copy.deepcopy(data)
        showcase = ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase
