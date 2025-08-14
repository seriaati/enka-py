from __future__ import annotations

import copy
import math
from typing import TYPE_CHECKING, Any, Literal, overload

from loguru import logger

from ..assets.data import TextMap
from ..assets.zzz.manager import ZZZ_ASSETS
from ..calc.zzz import LayerGenerator, PropState
from ..constants.common import DEFAULT_TIMEOUT, ZZZ_API_URL
from ..enums import zzz as enums
from ..errors import AssetKeyError, WrongUIDFormatError
from ..models import zzz as models
from ..models.zzz.build import Build
from .base import BaseClient

if TYPE_CHECKING:
    from ..models.enka.owner import Owner, OwnerInput
    from .cache import BaseTTLCache

__all__ = ("ZZZClient",)


class ZZZClient(BaseClient):
    """The main client to interact with the Enka Network Zenless Zone Zero API.

    Args:
        lang (Language | str): The language to use for the client, defaults to Language.ENGLISH.
        headers (dict[str, Any] | None): The headers to use for the client, defaults to None.
        cache (BaseTTLCache | None): The cache to use for the client, defaults to None.
        timeout (int): The timeout for the client, defaults to DEFAULT_TIMEOUT.
    """

    def __init__(
        self,
        lang: enums.Language | str = enums.Language.ENGLISH,
        *,
        headers: dict[str, Any] | None = None,
        cache: BaseTTLCache | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(headers=headers, cache=cache, timeout=timeout)

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
        agent.specialty = enums.ProfessionType(data["ProfessionType"])

        for disc in agent.discs:
            self._post_process_disc(disc)

        if agent.w_engine is not None:
            self._post_process_engine(agent.w_engine)

        # Credit to Enka Network for the stats calculation logic
        generator = LayerGenerator(self._assets)
        prop_state = PropState()

        prop_state.add(generator.character(agent))
        prop_state.add(generator.core(agent))
        if agent.w_engine is not None:
            prop_state.add(generator.weapon(agent.w_engine))

        prop_state.add(generator.discs(agent.discs))
        prop_state.add(generator.disc_sets(agent.discs))
        prop_state.add(generator.corrections(agent, prop_state))

        props = prop_state.sum()

        final_stats: dict[enums.AgentStatType, float] = {
            enums.AgentStatType.MAX_HP: props.max_hp,
            enums.AgentStatType.ATK: props.atk,
            enums.AgentStatType.DEF: props.defense,
            enums.AgentStatType.IMPACT: props.break_stun,
            enums.AgentStatType.CRIT_RATE: props.crit,
            enums.AgentStatType.CRIT_DMG: props.crit_dmg,
            enums.AgentStatType.PEN_RATIO: props.pen_ratio,
            enums.AgentStatType.PEN: props.pen_delta,
            enums.AgentStatType.ENERGY_REGEN: props.sp_recover,
            enums.AgentStatType.SHEER_FORCE: props.skip_def_atk,
            enums.AgentStatType.AAA: props.rp_recover,
            enums.AgentStatType.ANOMALY_PROFICIENCY: props.element_mystery,
            enums.AgentStatType.ANOMALY_MASTERY: props.element_abnormal_power,
            enums.AgentStatType.PHYSICAL_DMG_BONUS: props.added_damage_ratio_physics,
            enums.AgentStatType.FIRE_DMG_BONUS: props.added_damage_ratio_fire,
            enums.AgentStatType.ICE_DMG_BONUS: props.added_damage_ratio_ice,
            enums.AgentStatType.ELECTRIC_DMG_BONUS: props.added_damage_ratio_elec,
            enums.AgentStatType.ETHER_DMG_BONUS: props.added_damage_ratio_ether,
            enums.AgentStatType.SHEER_DMG_BONUS: props.skip_def_damage_ratio,
        }

        agent.stats = {
            stat_type: models.AgentStat(
                type=stat_type,
                value=math.floor(value),
                name=self._text_map[self._assets.property[str(stat_type.value)]["Name"]],
                format=self._assets.property[str(stat_type.value)]["Format"],
            )
            for stat_type, value in final_stats.items()
        }

    def _post_process_title(self, title: models.Title) -> None:
        title_data = self._assets.titles[str(title.id)]
        title.text = self._text_map[title_data["TitleText"]]
        title.color1 = f"#{title_data['ColorA']}"
        title.color2 = f"#{title_data['ColorB']}"

    def _post_process_player(self, player: models.Player) -> None:
        if player.title is not None:
            self._post_process_title(player.title)

        # Avatar
        pfp_data = self._assets.pfps.get(str(player.id))
        if pfp_data:
            player.avatar = f"https://enka.network{pfp_data['Icon']}"

        # Namecard
        namecard_id = player.namecard_id
        try:
            icon_path = self._assets.namecards[str(namecard_id)]["Icon"]
            icon_url = f"https://enka.network{icon_path}"
        except AssetKeyError:
            icon_url = ""
        else:
            player.namecard = models.Namecard(id=namecard_id, icon=icon_url)

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
        if not str(uid).isdigit():
            raise WrongUIDFormatError

        url = ZZZ_API_URL.format(uid)
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

    async def fetch_builds(self, owner: Owner | OwnerInput) -> dict[str, list[Build]]:
        """Fetch the character builds of the given owner.

        Args:
            owner: The owner of the builds.

        Returns:
            Character ID to list of builds mapping.
        """
        data = await self._request_profile(owner)
        result: dict[str, list[Build]] = {}

        for key, builds in data.items():
            result[key] = []
            for build in builds:
                build_ = Build(**build)
                self._post_process_agent(build_.character)
                result[key].append(build_)

        return result
