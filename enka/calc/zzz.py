from __future__ import annotations

import math
from collections import defaultdict
from typing import TYPE_CHECKING, Final

from ..enums.zzz import ProfessionType

if TYPE_CHECKING:
    from enka.assets.zzz.manager import ZZZAssetManager
    from enka.models.zzz.character import Agent, DriveDisc, WEngine

DEFAULT_PROPS: Final[dict[str, float]] = {
    "HpMax_Base": 0,
    "HpMax_Ratio": 0,
    "HpMax_Delta": 0,
    "Atk_Base": 0,
    "Atk_Ratio": 0,
    "Atk_Delta": 0,
    "BreakStun_Base": 0,
    "BreakStun_Ratio": 0,
    "SkipDefAtk_Base": 0,
    "SkipDefAtk_Delta": 0,
    "Def_Base": 0,
    "Def_Ratio": 0,
    "Def_Delta": 0,
    "Crit_Base": 0,
    "Crit_Delta": 0,
    "CritDmg_Base": 0,
    "CritDmg_Delta": 0,
    "PenRatio_Base": 0,
    "PenRatio_Delta": 0,
    "PenDelta_Base": 0,
    "PenDelta_Delta": 0,
    "SpRecover_Base": 0,
    "SpRecover_Ratio": 0,
    "SpRecover_Delta": 0,
    "ElementMystery_Base": 0,
    "ElementMystery_Delta": 0,
    "ElementAbnormalPower_Base": 0,
    "ElementAbnormalPower_Ratio": 0,
    "ElementAbnormalPower_Delta": 0,
    "AddedDamageRatio_Physics_Base": 0,
    "AddedDamageRatio_Physics_Delta": 0,
    "AddedDamageRatio_Fire_Base": 0,
    "AddedDamageRatio_Fire_Delta": 0,
    "AddedDamageRatio_Ice_Base": 0,
    "AddedDamageRatio_Ice_Delta": 0,
    "AddedDamageRatio_Elec_Base": 0,
    "AddedDamageRatio_Elec_Delta": 0,
    "AddedDamageRatio_Ether_Base": 0,
    "AddedDamageRatio_Ether_Delta": 0,
    "RpRecover_Base": 0,
    "RpRecover_Ratio": 0,
    "RpRecover_Delta": 0,
    "SkipDefDamageRatio_Base": 0,
    "SkipDefDamageRatio_Delta": 0,
}

PROP_ID_TO_NAME: Final[dict[int, str]] = {
    11101: "HpMax_Base",
    11102: "HpMax_Ratio",
    11103: "HpMax_Delta",
    12101: "Atk_Base",
    12102: "Atk_Ratio",
    12103: "Atk_Delta",
    12201: "BreakStun_Base",
    12202: "BreakStun_Ratio",
    12301: "SkipDefAtk_Base",
    12303: "SkipDefAtk_Delta",
    13101: "Def_Base",
    13102: "Def_Ratio",
    13103: "Def_Delta",
    20101: "Crit_Base",
    20103: "Crit_Delta",
    21101: "CritDmg_Base",
    21103: "CritDmg_Delta",
    23101: "PenRatio_Base",
    23103: "PenRatio_Delta",
    23201: "PenDelta_Base",
    23203: "PenDelta_Delta",
    30501: "SpRecover_Base",
    30502: "SpRecover_Ratio",
    30503: "SpRecover_Delta",
    31201: "ElementMystery_Base",
    31203: "ElementMystery_Delta",
    31401: "ElementAbnormalPower_Base",
    31402: "ElementAbnormalPower_Ratio",
    31403: "ElementAbnormalPower_Delta",
    31501: "AddedDamageRatio_Physics_Base",
    31503: "AddedDamageRatio_Physics_Delta",
    31601: "AddedDamageRatio_Fire_Base",
    31603: "AddedDamageRatio_Fire_Delta",
    31701: "AddedDamageRatio_Ice_Base",
    31703: "AddedDamageRatio_Ice_Delta",
    31801: "AddedDamageRatio_Elec_Base",
    31803: "AddedDamageRatio_Elec_Delta",
    31901: "AddedDamageRatio_Ether_Base",
    31903: "AddedDamageRatio_Ether_Delta",
    32001: "RpRecover_Base",
    32002: "RpRecover_Ratio",
    32003: "RpRecover_Delta",
    32201: "SkipDefDamageRatio_Base",
    32203: "SkipDefDamageRatio_Delta",
}


class LayerGenerator:
    def __init__(self, assets: ZZZAssetManager) -> None:
        self._assets = assets

    def character(self, a: Agent) -> PropLayer:
        layer = PropLayer()
        excel = self._assets.avatars.data[str(a.id)]

        for prop_id, base in excel["BaseProps"].items():
            growth = (excel["GrowthProps"].get(prop_id, 0) / 10000) * (a.level - 1)
            try:
                promotion = excel["PromotionProps"][a.promotion - 1][prop_id]
            except (IndexError, KeyError):
                promotion = 0

            computed = base + growth + promotion
            layer.add(PROP_ID_TO_NAME[int(prop_id)], computed)

        return layer

    def core(self, a: Agent) -> PropLayer:
        layer = PropLayer()
        excel = self._assets.avatars.data[str(a.id)]
        props = excel["CoreEnhancementProps"][a.core_skill_level_num]

        for prop_id, core in props.items():
            layer.add(PROP_ID_TO_NAME[int(prop_id)], core)

        return layer

    def weapon(self, w: WEngine) -> PropLayer:
        layer = PropLayer()

        layer.add(PROP_ID_TO_NAME[w.main_stat.type.value], w.main_stat.value)
        layer.add(PROP_ID_TO_NAME[w.sub_stat.type.value], w.sub_stat.value)

        return layer

    def discs(self, ds: list[DriveDisc]) -> PropLayer:
        layer = PropLayer()

        for d in ds:
            layer.add(PROP_ID_TO_NAME[d.main_stat.type.value], d.main_stat.value)

            for sub in d.sub_stats:
                layer.add(PROP_ID_TO_NAME[sub.type.value], sub.value)

        return layer

    def disc_sets(self, ds: list[DriveDisc]) -> PropLayer:
        sets: defaultdict[int, int] = defaultdict(int)
        for d in ds:
            sets[d.set_id] += 1

        layer = PropLayer()
        for set_id, count in sets.items():
            if count < 2:
                continue

            set_data = self._assets.equipments["Suits"][str(set_id)]
            bonus_props: dict[str, int] = set_data["SetBonusProps"]
            for prop_id, value in bonus_props.items():
                layer.add(PROP_ID_TO_NAME[int(prop_id)], value)

        return layer

    def corrections(self, a: Agent, prop_state: PropState) -> PropLayer:
        layer = PropLayer()
        prop_sum = prop_state.sum()

        enh = a.core_skill_level_num
        if a.id == 1121:
            # Ben's initial ATK increases along with his initial DEF. He gains X% of his initial DEF as ATK.
            defense_to_atk_multiplier = (0.4, 0.46, 0.52, 0.6, 0.66, 0.72, 0.8)
            layer.add(
                "Atk_Delta",
                math.floor(math.floor(prop_sum.defense) * defense_to_atk_multiplier[enh]),
            )

        if a.specialty is ProfessionType.RUPTURE:
            # Rupture characters gain extra Sheer Force based on their ATK, with every 1 point of ATK increasing Sheer Force by 0.3.
            layer.add("SkipDefAtk_Delta", math.floor(math.floor(prop_sum.atk) * 0.3))

            # Rupture characters gain extra Sheer Force based on her Max HP, with every 1 point of Max HP increasing Sheer Force by 0.1.
            layer.add("SkipDefAtk_Delta", math.floor(math.floor(prop_sum.max_hp) * 0.1))

        return layer


class PropLayer:  # noqa: PLR0904
    def __init__(self) -> None:
        self.props = DEFAULT_PROPS.copy()

    def add(self, name: str, value: float) -> None:
        if name not in self.props:
            msg = f"Invalid stat name: {name!r}"
            raise ValueError(msg)

        self.props[name] += value

    @property
    def max_hp(self) -> float:
        return (
            self.props["HpMax_Base"]
            + math.ceil(self.props["HpMax_Base"] * (self.props["HpMax_Ratio"] / 10_000))
            + self.props["HpMax_Delta"]
        )

    @property
    def atk(self) -> float:
        return (
            self.props["Atk_Base"] * (1 + self.props["Atk_Ratio"] / 10_000)
            + self.props["Atk_Delta"]
        )

    @property
    def defense(self) -> float:
        return (
            self.props["Def_Base"] * (1 + self.props["Def_Ratio"] / 10_000)
            + self.props["Def_Delta"]
        )

    @property
    def break_stun(self) -> float:
        return self.props["BreakStun_Base"] * (1 + self.props["BreakStun_Ratio"] / 10_000)

    @property
    def crit(self) -> float:
        return self.props["Crit_Base"] + self.props["Crit_Delta"]

    @property
    def crit_dmg(self) -> float:
        return self.props["CritDmg_Base"] + self.props["CritDmg_Delta"]

    @property
    def pen_ratio(self) -> float:
        return self.props["PenRatio_Base"] + self.props["PenRatio_Delta"]

    @property
    def pen_delta(self) -> float:
        return self.props["PenDelta_Base"] + self.props["PenDelta_Delta"]

    @property
    def sp_recover(self) -> float:
        return (
            self.props["SpRecover_Base"] * (1 + self.props["SpRecover_Ratio"] / 10_000)
            + self.props["SpRecover_Delta"]
        )

    @property
    def element_mystery(self) -> float:
        return self.props["ElementMystery_Base"] + self.props["ElementMystery_Delta"]

    @property
    def element_abnormal_power(self) -> float:
        return (
            self.props["ElementAbnormalPower_Base"]
            * (1 + self.props["ElementAbnormalPower_Ratio"] / 10_000)
            + self.props["ElementAbnormalPower_Delta"]
        )

    @property
    def added_damage_ratio_physics(self) -> float:
        return (
            self.props["AddedDamageRatio_Physics_Base"]
            + self.props["AddedDamageRatio_Physics_Delta"]
        )

    @property
    def added_damage_ratio_fire(self) -> float:
        return self.props["AddedDamageRatio_Fire_Base"] + self.props["AddedDamageRatio_Fire_Delta"]

    @property
    def added_damage_ratio_ice(self) -> float:
        return self.props["AddedDamageRatio_Ice_Base"] + self.props["AddedDamageRatio_Ice_Delta"]

    @property
    def added_damage_ratio_elec(self) -> float:
        return self.props["AddedDamageRatio_Elec_Base"] + self.props["AddedDamageRatio_Elec_Delta"]

    @property
    def added_damage_ratio_ether(self) -> float:
        return (
            self.props["AddedDamageRatio_Ether_Base"] + self.props["AddedDamageRatio_Ether_Delta"]
        )

    @property
    def skip_def_atk(self) -> float:
        return self.props["SkipDefAtk_Base"] + self.props["SkipDefAtk_Delta"]

    @property
    def skip_def_damage_ratio(self) -> float:
        return self.props["SkipDefDamageRatio_Base"] + self.props["SkipDefDamageRatio_Delta"]

    @property
    def rp_recover(self) -> float:
        return (
            self.props["RpRecover_Base"] * (1 + self.props["RpRecover_Ratio"] / 10_000)
            + self.props["RpRecover_Delta"]
        )


class PropState:
    def __init__(self) -> None:
        self.layers: list[PropLayer] = []

    def add(self, layer: PropLayer) -> None:
        self.layers.append(layer)

    def sum(self) -> PropLayer:
        sum_layer = PropLayer()
        for layer in self.layers:
            for key, value in layer.props.items():
                sum_layer.add(key, math.floor(value))

        return sum_layer
