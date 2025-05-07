from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from enka.assets.hsr.manager import HSRAssetManager
    from enka.models.hsr import Character, LightCone, Relic

DEFAULT_PROPS: Final[dict[str, float]] = {
    "BaseHP": 0,
    "HPAddedRatio": 0,
    "HPDelta": 0,
    "HPConvert": 0,
    "BaseAttack": 0,
    "AttackAddedRatio": 0,
    "AttackDelta": 0,
    "AttackConvert": 0,
    "BaseDefence": 0,
    "DefenceAddedRatio": 0,
    "DefenceDelta": 0,
    "DefenceConvert": 0,
    "BaseSpeed": 0,
    "SpeedAddedRatio": 0,
    "SpeedDelta": 0,
    "SpeedConvert": 0,
    "CriticalChance": 0,
    "CriticalChanceBase": 0,
    "CriticalDamage": 0,
    "CriticalDamageBase": 0,
    "SPRatio": 0,
    "SPRatioBase": 0,
    "SPRatioConvert": 0,
    "StatusProbability": 0,
    "StatusProbabilityBase": 0,
    "StatusProbabilityConvert": 0,
    "StatusResistance": 0,
    "StatusResistanceBase": 0,
    "StatusResistanceConvert": 0,
    "HealRatioBase": 0,
    "HealRatioConvert": 0,
    "HealTakenRatio": 0,
    "ShieldAddedRatio": 0,
    "ShieldTakenRatio": 0,
    "AggroBase": 0,
    "AggroAddedRatio": 0,
    "AggroDelta": 0,
    "BreakDamageAddedRatio": 0,
    "BreakDamageAddedRatioBase": 0,
    "AllDamageTypeResistance": 0,
    "PhysicalResistanceDelta": 0,
    "FireResistanceDelta": 0,
    "IceResistanceDelta": 0,
    "ThunderResistanceDelta": 0,
    "QuantumResistanceDelta": 0,
    "ImaginaryResistanceDelta": 0,
    "WindResistanceDelta": 0,
    "PhysicalPenetrate": 0,
    "FirePenetrate": 0,
    "IcePenetrate": 0,
    "ThunderPenetrate": 0,
    "QuantumPenetrate": 0,
    "ImaginaryPenetrate": 0,
    "WindPenetrate": 0,
    "AllDamageTypeTakenRatio": 0,
    "PhysicalTakenRatio": 0,
    "FireTakenRatio": 0,
    "IceTakenRatio": 0,
    "ThunderTakenRatio": 0,
    "QuantumTakenRatio": 0,
    "ImaginaryTakenRatio": 0,
    "WindTakenRatio": 0,
    "AllDamageTypeAddedRatio": 0,
    "DOTDamageAddedRatio": 0,
    "PhysicalAddedRatio": 0,
    "FireAddedRatio": 0,
    "IceAddedRatio": 0,
    "ThunderAddedRatio": 0,
    "QuantumAddedRatio": 0,
    "ImaginaryAddedRatio": 0,
    "WindAddedRatio": 0,
    "StanceBreakAddedRatio": 0,
    "AllDamageReduce": 0,
    "FatigueRatio": 0,
    "MinimumFatigueRatio": 0,
}


class LayerGenerator:
    def __init__(self, assets: HSRAssetManager) -> None:
        self._assets = assets

    def character(self, c: Character) -> PropLayer:
        layer = PropLayer()
        promotion = self._assets.meta_data["avatar"][str(c.id)][str(c.ascension)]

        layer.add("BaseHP", promotion["HPBase"] + promotion["HPAdd"] * (c.level - 1))
        layer.add("BaseAttack", promotion["AttackBase"] + promotion["AttackAdd"] * (c.level - 1))
        layer.add("BaseDefence", promotion["DefenceBase"] + promotion["DefenceAdd"] * (c.level - 1))
        layer.add("BaseSpeed", promotion["SpeedBase"])
        layer.add("CriticalChance", promotion["CriticalChance"])
        layer.add("CriticalDamage", promotion["CriticalDamage"])
        layer.add("SPRatio", 1)

        return layer

    def skill_tree(self, c: Character) -> PropLayer:
        layer = PropLayer()
        tree_store = self._assets.meta_data["tree"]

        for trace in c.traces:
            if str(trace.id) not in tree_store:
                continue

            meta = tree_store[str(trace.id)][str(trace.level)]["props"]
            for key, value in meta.items():
                layer.add(key, value)

        return layer

    def light_cone(self, lc: LightCone) -> PropLayer:
        layer = PropLayer()
        promotion = self._assets.meta_data["equipment"][str(lc.id)][str(lc.ascension)]

        base_stats = {
            "BaseHP": promotion["BaseHP"] + promotion["HPAdd"] * (lc.level - 1),
            "BaseAttack": promotion["BaseAttack"] + promotion["AttackAdd"] * (lc.level - 1),
            "BaseDefence": promotion["BaseDefence"] + promotion["DefenceAdd"] * (lc.level - 1),
        }

        for key, value in base_stats.items():
            layer.add(key, value)

        return layer

    def light_cone_skill(self, lc: LightCone) -> PropLayer:
        layer = PropLayer()
        meta = self._assets.meta_data["equipmentSkill"]

        if str(lc.id) in meta:
            meta = meta[str(lc.id)][str(lc.superimpose)]["props"]
            for key, value in meta.items():
                layer.add(key, value)

        return layer

    def relics(self, relics: list[Relic]) -> PropLayer:
        layer = PropLayer()

        for r in relics:
            for stat in r.stats:
                layer.add(stat.type.value, stat.value)

        return layer

    def relic_set(self, relics: list[Relic]) -> PropLayer:
        sets: defaultdict[int, int] = defaultdict(int)
        for r in relics:
            sets[r.set_id] += 1

        layer = PropLayer()
        for relic_set_id, count in sets.items():
            if count >= 2:
                props = self._assets.meta_data["relic"]["setSkill"][str(relic_set_id)]["2"]["props"]
                for key, value in props.items():
                    layer.add(key, value)

            if count >= 4:
                props = self._assets.meta_data["relic"]["setSkill"][str(relic_set_id)]["4"]["props"]
                for key, value in props.items():
                    layer.add(key, value)

        return layer


class PropLayer:
    def __init__(self) -> None:
        self.props = DEFAULT_PROPS.copy()

    def add(self, name: str, value: float) -> None:
        if name not in self.props:
            msg = f"Invalid stat name: {name!r}"
            raise ValueError(msg)

        self.props[name] += value

    @property
    def hp(self) -> float:
        return (
            self.props["BaseHP"] * (1 + self.props["HPAddedRatio"])
            + self.props["HPDelta"]
            + self.props["HPConvert"]
        )

    @property
    def attack(self) -> float:
        return (
            self.props["BaseAttack"] * (1 + self.props["AttackAddedRatio"])
            + self.props["AttackDelta"]
            + self.props["AttackConvert"]
        )

    @property
    def defence(self) -> float:
        return (
            self.props["BaseDefence"] * (1 + self.props["DefenceAddedRatio"])
            + self.props["DefenceDelta"]
            + self.props["DefenceConvert"]
        )

    @property
    def speed(self) -> float:
        return (
            self.props["BaseSpeed"] * (1 + self.props["SpeedAddedRatio"])
            + self.props["SpeedDelta"]
            + self.props["SpeedConvert"]
        )

    @property
    def break_damage(self) -> float:
        return self.props["BreakDamageAddedRatioBase"] + self.props["BreakDamageAddedRatio"]

    @property
    def critical_chance(self) -> float:
        return self.props["CriticalChanceBase"] + self.props["CriticalChance"]

    @property
    def critical_damage(self) -> float:
        return self.props["CriticalDamageBase"] + self.props["CriticalDamage"]

    @property
    def heal_ratio(self) -> float:
        return self.props["HealRatioBase"] + self.props["HealRatioConvert"]

    @property
    def sp_ratio(self) -> float:
        return self.props["SPRatioBase"] + self.props["SPRatio"] + self.props["SPRatioConvert"]

    @property
    def status_probability(self) -> float:
        return self.props["StatusProbabilityBase"] + self.props["StatusProbability"]

    @property
    def status_resistance(self) -> float:
        return self.props["StatusResistanceBase"] + self.props["StatusResistance"]

    @property
    def physical_damage(self) -> float:
        return self.props["PhysicalAddedRatio"] + self.props["AllDamageTypeAddedRatio"]

    @property
    def fire_damage(self) -> float:
        return self.props["FireAddedRatio"] + self.props["AllDamageTypeAddedRatio"]

    @property
    def ice_damage(self) -> float:
        return self.props["IceAddedRatio"] + self.props["AllDamageTypeAddedRatio"]

    @property
    def thunder_damage(self) -> float:
        return self.props["ThunderAddedRatio"] + self.props["AllDamageTypeAddedRatio"]

    @property
    def wind_damage(self) -> float:
        return self.props["WindAddedRatio"] + self.props["AllDamageTypeAddedRatio"]

    @property
    def quantum_damage(self) -> float:
        return self.props["QuantumAddedRatio"] + self.props["AllDamageTypeAddedRatio"]

    @property
    def imaginary_damage(self) -> float:
        return self.props["ImaginaryAddedRatio"] + self.props["AllDamageTypeAddedRatio"]


class PropState:
    def __init__(self) -> None:
        self.layers: list[PropLayer] = []

    def add(self, layer: PropLayer) -> None:
        self.layers.append(layer)

    def sum(self) -> PropLayer:
        sum_layer = PropLayer()
        for layer in self.layers:
            for key, value in layer.props.items():
                sum_layer.add(key, value)

        return sum_layer
