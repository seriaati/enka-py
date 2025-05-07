from __future__ import annotations

import sys
from enum import IntEnum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


__all__ = ("Element", "Language", "Path", "RelicType", "StatType", "TraceType")


class Language(StrEnum):
    """Languages supported by the HSR Enka Network API."""

    ENGLISH = "en"
    RUSSIAN = "ru"
    VIETNAMESE = "vi"
    THAI = "th"
    PORTUGUESE = "pt"
    KOREAN = "ko"
    JAPANESE = "ja"
    INDOENSIAN = "id"
    FRENCH = "fr"
    ESPANOL = "es"
    GERMAN = "de"
    TRADITIONAL_CHINESE = "zh-tw"
    SIMPLIFIED_CHINESE = "zh-cn"


class RelicType(IntEnum):
    """HSR relic types."""

    HEAD = 1
    HAND = 2
    BODY = 3
    FOOT = 4
    ROPE = 5  # NECK
    ORBIT = 6  # OBJECT


class StatType(StrEnum):
    """HSR property types."""

    MAX_HP = "MaxHP"
    ATK = "Attack"
    DEF = "Defence"
    SPD = "Speed"

    CRIT_RATE = "CriticalChance"
    CRIT_DMG = "CriticalDamage"
    BREAK_EFFECT = "BreakDamageAddedRatio"
    BREAK_EFFECT_BASE = "BreakDamageAddedRatioBase"
    HEALING_BOOST = "HealRatio"

    MAX_ENERGY = "MaxSP"
    ENERGY_REGEN_RATE = "SPRatio"
    EFFECT_HIT_RATE = "StatusProbability"
    EFFECT_RES = "StatusResistance"
    CRIT_RATE_BASE = "CriticalChanceBase"
    CRIT_DMG_BASE = "CriticalDamageBase"
    HEALING_BOOST_BASE = "HealRatioBase"
    ENERGY_REGEN_RATE_BASE = "SPRatioBase"
    EFFECT_HIT_RATE_BASE = "StatusProbabilityBase"
    EFFECT_RES_BASE = "StatusResistanceBase"

    # Element dmg/resistance boosts
    PHYSICAL_DMG_BOOST = "PhysicalAddedRatio"
    PHYSICAL_RES_BOOST = "PhysicalResistance"
    FIRE_DMG_BOOST = "FireAddedRatio"
    FIRE_RES_BOOST = "FireResistance"
    ICE_DMG_BOOST = "IceAddedRatio"
    ICE_RES_BOOST = "IceResistance"
    LIGHTNING_DMG_BOOST = "ThunderAddedRatio"
    LIGHTNING_RES_BOOST = "ThunderResistance"
    WIND_DMG_BOOST = "WindAddedRatio"
    WIND_RES_BOOST = "WindResistance"
    QUANTUM_DMG_BOOST = "QuantumAddedRatio"
    QUANTUM_RES_BOOST = "QuantumResistance"
    IMAGINARY_DMG_BOOST = "ImaginaryAddedRatio"
    IMAGINARY_RES_BOOST = "ImaginaryResistance"

    BASE_HP = "BaseHP"
    HP_DELTA = "HPDelta"
    HP_BOOST = "HPAddedRatio"
    BASE_ATK = "BaseAttack"
    ATK_DELTA = "AttackDelta"
    ATK_BOOST = "AttackAddedRatio"
    BASE_DEF = "BaseDefence"
    DEF_DELTA = "DefenceDelta"
    DEF_BOOST = "DefenceAddedRatio"
    BASE_SPEED = "BaseSpeed"
    INCOMING_HEALING_BOOST = "HealTakenRatio"

    PHYSICAL_RES_DELTA = "PhysicalResistanceDelta"
    FIRE_RES_DELTA = "FireResistanceDelta"
    ICE_RES_DELTA = "IceResistanceDelta"
    THUNDER_RES_DELTA = "ThunderResistanceDelta"
    WIND_RES_DELTA = "WindResistanceDelta"
    QUANTUM_RES_DELTA = "QuantumResistanceDelta"
    IMAGINARY_RES_DELTA = "ImaginaryResistanceDelta"

    SPEED_DELTA = "SpeedDelta"


class Element(StrEnum):
    """HSR elements."""

    ICE = "Ice"
    FIRE = "Fire"
    WIND = "Wind"
    LIGHTNING = "Thunder"
    PHYSICAL = "Physical"
    QUANTUM = "Quantum"
    IMAGINARY = "Imaginary"


class Path(StrEnum):
    """HSR paths."""

    PRESERVATION = "Knight"
    THE_HUNT = "Rogue"
    ERUDITION = "Mage"
    NIHILITY = "Warlock"
    DESTRUCTION = "Warrior"
    HARMONY = "Shaman"
    ABUNDANCE = "Priest"
    REMEMBRANCE = "Memory"
    NONE = "None"


class TraceType(IntEnum):
    """HSR trace types."""

    UNKNOWN = 0
    """Set before post-processing"""
    SKILL = 2
    """Basic ATK, Skill, Ultimate, Talent, Technique"""
    TALENT = 3
    """Special talents (there are 3 of these)"""
    STAT = 1
    """Stat boost traces"""
    MEMOSPRITE = 4
    """Memosprite traces"""
