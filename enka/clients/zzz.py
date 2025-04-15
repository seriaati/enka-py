from __future__ import annotations

from collections import defaultdict
import copy
import math
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
    """The main client to interact with the Enka Network Honkai Star Rail API.

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

    def _calc_agent_stats(self, agent: models.Agent) -> None:
        # See https://api.enka.network/#/docs/zzz/api?id=agent-stats for the formula

        data = self._assets.avatars[str(agent.id)]

        base_props: dict[str, int] = data["BaseProps"]
        growth_props: dict[str, int] = data["GrowthProps"]
        promotion_props: list[dict[str, int]] = data["PromotionProps"]
        core_enhancement_props: list[dict[str, int]] = data["CoreEnhancementProps"]

        # Additional stats from engine and discs
        engine = agent.w_engine
        discs = agent.discs

        stats: list[dict[int, int]] = [engine.main_stat.as_dict(), engine.sub_stat.as_dict()]
        stats.extend(disc.main_stat.as_dict() for disc in discs)

        # Set bonus
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
            stats.extend({int(prop_id): prop_val} for prop_id, prop_val in set_effect.items())

        percent_add_stats = [s for s in add_stats if "%" in s.format]
        flat_add_stats = [s for s in add_stats if "%" not in s.format]

        for prop_id, prop_val in base_props.items():
            growth_val = (growth_props.get(prop_id, 0) * (agent.level - 1)) / 10000
            promotion_val = promotion_props[agent.promotion - 1].get(prop_id, 0)
            core_enhancement_val = core_enhancement_props[agent.core_skill_level_num].get(
                prop_id, 0
            )
            base_total_val = (
                prop_val + math.floor(growth_val) + promotion_val + core_enhancement_val
            )

            stat_type = enums.StatType(int(prop_id))

            prop_data = self._assets.property[prop_id]
            stat = agent.stats[stat_type] = models.Stat(
                type=stat_type,
                value=base_total_val,
                name=self._text_map[prop_data["Name"]],
                format=prop_data["Format"],
            )

            total_add_percent = 0
            for add_stat in percent_add_stats:
                if str(add_stat.type.value)[:3] == str(stat.type.value)[:3]:
                    total_add_percent += add_stat.value

            total_add_flat = 0
            for flat_add_stat in flat_add_stats:
                if str(flat_add_stat.type.value)[:3] == str(stat.type.value)[:3]:
                    total_add_flat += flat_add_stat.value

            stat.value = math.floor(stat.value * (1 + total_add_percent / 10000) + total_add_flat)

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

        self._post_process_engine(agent.w_engine)
        self._calc_agent_stats(agent)

    def _post_process_showcase(self, showcase: models.ShowcaseResponse) -> None:
        """Post-process the showcase data.

        Args:
            showcase : The showcase data to post-process.
        """
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
        """Fetches the ZZZ character showcase of the given UID.

        Args:
            uid (str | int): The UID of the player.
            raw (bool): Whether to return the raw data or not, defaults to False.

        Returns:
            ShowcaseResponse | dict[str, Any]: The parsed or raw showcase data.
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
        """Parses the given showcase data.

        Args:
            data (dict[str, Any]): The showcase data.

        Returns:
            ShowcaseResponse: The parsed showcase data.
        """
        data = copy.deepcopy(data)
        showcase = models.ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase
