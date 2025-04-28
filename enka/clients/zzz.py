from __future__ import annotations

import copy
import math
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Final, Literal, overload

from loguru import logger

from ..assets.data import TextMap
from ..assets.zzz.manager import ZZZ_ASSETS
from ..enums import zzz as enums
from ..enums.enum import Game
from ..models import zzz as models
from .base import BaseClient

if TYPE_CHECKING:
    from .cache import BaseTTLCache

__all__ = ("ZZZClient",)

API_URL: Final[str] = "https://enka.network/api/zzz/uid/{uid}"


class ZZZClient(BaseClient):
    """The main client to interact with the Enka Network Zenless Zone Zero API.

    Args:
        lang (Language | str): The language to use for the client, defaults to Language.ENGLISH.
        headers (dict[str, Any] | None): The headers to use for the client, defaults to None.
        cache (BaseTTLCache | None): The cache to use for the client, defaults to None.
    """

    def __init__(
        self,
        lang: enums.Language | str = enums.Language.ENGLISH,
        *,
        headers: dict[str, Any] | None = None,
        cache: BaseTTLCache | None = None,
    ) -> None:
        super().__init__(Game.ZZZ, headers=headers, cache=cache)

        self._lang = self._convert_lang(lang)
        self._assets = ZZZ_ASSETS

    def _convert_lang(self, lang: enums.Language | str) -> enums.Language:
        if isinstance(lang, str):
            try:
                lang = enums.Language(lang)
            except ValueError as e:
                available_langs = ", ".join(lang.value for lang in enums.Language)
                msg = f"Invalid language: {lang}, must be one of {available_langs}"
                raise ValueError(msg) from e

        return lang

    @property
    def lang(self) -> enums.Language:
        return self._lang

    @lang.setter
    def lang(self, lang: enums.Language | str) -> None:
        self._lang = self._convert_lang(lang)
        self._text_map = TextMap(self._lang, self._assets.text_map)

    async def __aenter__(self) -> ZZZClient:
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    async def start(self) -> None:
        await super().start()
        await self._assets.load(self.session)
        self._text_map = TextMap(self.lang, self._assets.text_map)

    async def update_assets(self) -> None:
        """Update game assets."""
        logger.info("Updating ZZZ assets")
        await self._assets.update(self.session)
        self._text_map = TextMap(self.lang, self._assets.text_map)
        logger.info("ZZZ assets updated")

    def _calc_disc_stats(self, disc: models.DriveDisc) -> None:
        # See https://api.enka.network/#/docs/zzz/api?id=drive-disc for the formula
        disc_level_data = next(
            (
                d
                for d in self._assets.equipment_level["Items"]
                if d["Level"] == disc.level and d["Rarity"] == disc.rarity_num
            ),
            None,
        )
        if disc_level_data is None:
            logger.warning(
                f"Drive disc level data not found for level={disc.level} and rarity={disc.rarity_num}"
            )
            return

        main_stat_val = disc.main_stat.value * (1 + disc_level_data["EnhanceRate"] / 10000)
        disc.main_stat.value = math.floor(main_stat_val)

        main_stat_data = self._assets.property[str(disc.main_stat.type.value)]
        disc.main_stat.name = self._text_map[main_stat_data["Name"]]
        disc.main_stat.format = main_stat_data["Format"]

        for sub in disc.sub_stats:
            sub.value *= sub.roll_times

            sub_data = self._assets.property[str(sub.type.value)]
            sub.name = self._text_map[sub_data["Name"]]
            sub.format = sub_data["Format"]

    def _get_agent_base_stats(self, agent: models.Agent) -> defaultdict[int, int]:
        stats: defaultdict[int, int] = defaultdict(int)
        data = self._assets.avatars[str(agent.id)]
        base_props: dict[str, int] = data["BaseProps"]
        growth_props: dict[str, int] = data["GrowthProps"]
        promotion_props: list[dict[str, int]] = data["PromotionProps"]
        core_enhancement_props: list[dict[str, int]] = data["CoreEnhancementProps"]

        for prop_id_str, prop_val in base_props.items():
            prop_id = int(prop_id_str)
            growth_val = (growth_props.get(prop_id_str, 0) * (agent.level - 1)) / 10000
            promotion_val = promotion_props[agent.promotion - 1].get(prop_id_str, 0)
            core_enhancement_val = core_enhancement_props[agent.core_skill_level_num].get(
                prop_id_str, 0
            )
            base_total_val = (
                prop_val + math.floor(growth_val) + promotion_val + core_enhancement_val
            )
            stats[prop_id] += base_total_val

        return stats

    def _add_engine_stats(self, stats: defaultdict[int, int], engine: models.WEngine) -> None:
        stats[engine.main_stat.type.value] += engine.main_stat.value
        stats[engine.sub_stat.type.value] += engine.sub_stat.value

    def _add_disc_stats(self, stats: defaultdict[int, int], discs: list[models.DriveDisc]) -> None:
        for disc in discs:
            stats[disc.main_stat.type.value] += disc.main_stat.value
            for sub in disc.sub_stats:
                stats[sub.type.value] += sub.value

    def _add_disc_set_bonus_stats(
        self, stats: defaultdict[int, int], discs: list[models.DriveDisc]
    ) -> None:
        sets: defaultdict[int, int] = defaultdict(int)
        for disc in discs:
            sets[disc.set_id] += 1

        for set_id, count in sets.items():
            if count < 2:
                continue

            set_data = self._assets.equipments["Suits"].get(str(set_id))
            if set_data is None:
                logger.warning(f"Set data not found for {set_id=}")
                continue

            set_effect: dict[str, int] = set_data["SetBonusProps"]
            for prop_id_str, prop_val in set_effect.items():
                stats[int(prop_id_str)] += prop_val

    def _calculate_final_stats(self, raw_stats: defaultdict[int, int]) -> dict[int, int]:
        final_stats: dict[int, int] = {
            stat_type.value: 0
            for stat_type in enums.StatType
            if str(stat_type.value).endswith("01")  # Initialize base stats
        }

        # Apply base stats first
        for prop_id, prop_val in raw_stats.items():
            if str(prop_id).endswith("01"):
                if prop_id not in final_stats:
                    final_stats[prop_id] = 0
                final_stats[prop_id] += prop_val

        # Apply percentage stats
        for prop_id, prop_val in raw_stats.items():
            if str(prop_id).endswith("02"):
                base_prop_id = prop_id - 1
                base_stat = final_stats.get(base_prop_id, 0)
                stat = base_stat * (1 + prop_val / 10000)
                # Max HP is rounded up, others down
                rounded = math.ceil(stat) if base_prop_id == 11101 else math.floor(stat)
                final_stats[base_prop_id] = rounded

        # Apply flat stats
        for prop_id, prop_val in raw_stats.items():
            if str(prop_id).endswith("03"):
                base_prop_id = prop_id - 2
                base_stat = final_stats.get(base_prop_id, 0)
                final_stats[base_prop_id] += prop_val

        return final_stats

    def _apply_special_agent_passives(
        self, final_stats: dict[int, int], agent: models.Agent
    ) -> None:
        if agent.id == 1121:  # Ben
            # Ben's initial ATK increases along with his initial DEF. He gains X% of his initial DEF as ATK.
            scalings = (0.4, 0.46, 0.52, 0.6, 0.66, 0.72, 0.8)
            def_stat_id = 13101
            atk_stat_id = 11101

            if def_stat_id in final_stats and atk_stat_id in final_stats:
                final_stats[atk_stat_id] += math.floor(
                    final_stats[def_stat_id] * scalings[agent.core_skill_level_num]
                )

    def _assign_final_stats_to_agent(
        self, final_stats: dict[int, int], agent: models.Agent
    ) -> None:
        for prop_id, prop_val in final_stats.items():
            stat_type = enums.StatType(prop_id)
            prop_data = self._assets.property[str(prop_id)]
            agent.stats[stat_type] = models.Stat(
                type=stat_type,
                value=prop_val,
                name=self._text_map[prop_data["Name"]],
                format=prop_data["Format"],
            )

    def _calc_agent_stats(self, agent: models.Agent) -> None:
        # See https://api.enka.network/#/docs/zzz/api?id=agent-stats for the formula

        # 1. Get base stats from agent level, promotion, core skills
        raw_stats = self._get_agent_base_stats(agent)

        # 2. Add engine stats
        if agent.w_engine is not None:
            self._add_engine_stats(raw_stats, agent.w_engine)

        # 3. Add disc stats
        self._add_disc_stats(raw_stats, agent.discs)

        # 4. Add disc set bonus stats
        self._add_disc_set_bonus_stats(raw_stats, agent.discs)

        # 5. Calculate final stats (applying %, flat bonuses)
        final_stats = self._calculate_final_stats(raw_stats)

        # 6. Apply special agent passives
        self._apply_special_agent_passives(final_stats, agent)

        # 7. Assign final stats to agent object
        self._assign_final_stats_to_agent(final_stats, agent)

    def _calc_engine_stats(self, engine: models.WEngine) -> None:
        # See https://api.enka.network/#/docs/zzz/api?id=w-engine for the formula

        level_data = next(
            (
                d
                for d in self._assets.weapon_level["Items"]
                if d["Level"] == engine.level and d["Rarity"] == engine.rarity_num
            ),
            None,
        )
        if level_data is None:
            logger.warning(
                f"W-Engine level data not found for level={engine.level} and rarity={engine.rarity_num}"
            )
            return

        enhance_rate = level_data["EnhanceRate"]

        star_data = next(
            (
                d
                for d in self._assets.weapon_star["Items"]
                if d["Rarity"] == engine.rarity_num and d["BreakLevel"] == engine.modification
            ),
            None,
        )
        if star_data is None:
            logger.warning(f"W-Engine star data not found for rarity={engine.rarity_num}")
            return

        star_rate = star_data["StarRate"]
        rand_rate = star_data["RandRate"]

        main_stat_val = engine.main_stat.value * (1 + enhance_rate / 10000 + star_rate / 10000)
        engine.main_stat.value = math.floor(main_stat_val)

        sub_stat_val = engine.sub_stat.value * (1 + rand_rate / 10000)
        engine.sub_stat.value = math.floor(sub_stat_val)

    def _post_process_engine(self, engine: models.WEngine) -> None:
        engine_data = self._assets.weapons[str(engine.id)]
        engine.name = self._text_map[engine_data["ItemName"]]
        engine.rarity_num = engine_data["Rarity"]
        engine.specialty = enums.ProfessionType(engine_data["ProfessionType"])
        engine.icon = f"https://enka.network{engine_data['ImagePath']}"

        main_stat = engine_data["MainStat"]
        main_stat_data = self._assets.property[str(main_stat["PropertyId"])]
        engine.main_stat = models.Stat(
            type=enums.StatType(main_stat["PropertyId"]),
            value=main_stat["PropertyValue"],
            name=self._text_map[main_stat_data["Name"]],
            format=main_stat_data["Format"],
        )

        sub_stat = engine_data["SecondaryStat"]
        sub_stat_data = self._assets.property[str(sub_stat["PropertyId"])]
        engine.sub_stat = models.Stat(
            type=enums.StatType(sub_stat["PropertyId"]),
            value=sub_stat["PropertyValue"],
            name=self._text_map[sub_stat_data["Name"]],
            format=sub_stat_data["Format"],
        )

        self._calc_engine_stats(engine)

    def _post_process_disc(self, disc: models.DriveDisc) -> None:
        disc_data = self._assets.equipments["Items"][str(disc.id)]
        disc.rarity_num = disc_data["Rarity"]
        disc.set_id = disc_data["SuitId"]
        self._calc_disc_stats(disc)

    def _post_process_agent(self, agent: models.Agent) -> None:
        data = self._assets.avatars[str(agent.id)]
        agent.name = self._text_map[data["Name"]]
        agent.rarity_num = data["Rarity"]
        agent.elements = [enums.Element(e) for e in data["ElementTypes"]]
        agent.icon = models.AgentIcon(
            filename=data["Image"].removeprefix("/ui/zzz/").removesuffix(".png")
        )
        agent.sig_engine_id = data["WeaponId"]
        agent.color = models.AgentColor(**data["Colors"])
        agent.highlight_stats = [enums.StatType(stat) for stat in data["HighlightProps"]]

        for disc in agent.discs:
            self._post_process_disc(disc)

        if agent.w_engine is not None:
            self._post_process_engine(agent.w_engine)
        self._calc_agent_stats(agent)

    def _post_process_title(self, title: models.Title) -> None:
        title_data = self._assets.titles[str(title.id)]
        title.text = self._text_map[title_data["TitleText"]]
        title.color1 = f"#{title_data['ColorA']}"
        title.color2 = f"#{title_data['ColorB']}"

    def _post_process_player(self, player: models.Player) -> None:
        self._post_process_title(player.title)

        # Namecard
        namecard_id = player.namecard_id
        player.namecard = models.Namecard(
            id=namecard_id, icon=self._assets.namecards[str(namecard_id)]["Icon"]
        )

    def _post_process_showcase(self, showcase: models.ShowcaseResponse) -> None:
        self._post_process_player(showcase.player)
        for agent in showcase.agents:
            self._post_process_agent(agent)

    @overload
    async def fetch_showcase(
        self, uid: str | int, *, raw: Literal[False] = False
    ) -> models.ShowcaseResponse: ...
    @overload
    async def fetch_showcase(
        self, uid: str | int, *, raw: Literal[True] = True
    ) -> dict[str, Any]: ...
    async def fetch_showcase(
        self, uid: str | int, *, raw: bool = False
    ) -> models.ShowcaseResponse | dict[str, Any]:
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
        showcase = models.ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase

    def parse_showcase(self, data: dict[str, Any]) -> models.ShowcaseResponse:
        """Parse the given showcase data.

        Args:
            data: The showcase data.

        Returns:
            The parsed showcase response.
        """
        data = copy.deepcopy(data)
        showcase = models.ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase
