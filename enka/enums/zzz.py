from __future__ import annotations

import sys
from enum import IntEnum

from ..constants.zzz import ELEMENT_ICON

if sys.version_info < (3, 11):
    from enum import Enum as StrEnum
else:
    from enum import StrEnum


class Language(StrEnum):
    """ZZZ language enum."""

    ENGLISH = "en"
    RUSSIAN = "ru"
    VIETNAMESE = "vi"
    THAI = "th"
    PORTUGUESE = "pt"
    KOREAN = "ko"
    JAPANESE = "ja"
    INDONESIAN = "id"
    FRENCH = "fr"
    ESPANOL = "es"
    GERMAN = "de"
    TRADITIONAL_CHINESE = "zh-tw"
    SIMPLIFIED_CHINESE = "zh-cn"


class SkillType(IntEnum):
    """ZZZ character skill type."""

    BASIC_ATK = 0
    SPECIAL_ATK = 1
    DASH = 2
    ULTIMATE = 3
    CORE_SKILL = 5
    ASSIST = 6


class StatType(IntEnum):
    """ZZZ stat type."""

    HP_BASE = 11101
    HP_PERCENT = 11102
    HP_FLAT = 11103

    ATK_BASE = 12101
    ATK_PERCENT = 12102
    ATK_FLAT = 12103

    IMPACT_BASE = 12201
    IMPACT_PERCENT = 12202

    SHEER_FORCE_BASE = 12301
    SHEER_FORCE_FLAT = 12302

    DEF_BASE = 13101
    DEF_PERCENT = 13102
    DEF_FLAT = 13103

    CRIT_RATE_BASE = 20101
    CRIT_RATE_FLAT = 20103

    CRIT_DMG_BASE = 21101
    CRIT_DMG_FLAT = 21103

    PEN_RATIO_BASE = 23101
    PEN_RATIO_FLAT = 23103

    PEN_BASE = 23201
    PEN_FLAT = 23203

    ENERGY_REGEN_BASE = 30501
    ENERGY_REGEN_PERCENT = 30502
    ENERGY_REGEN_FLAT = 30503

    ANOMALY_PRO_BASE = 31201
    """Anomaly proficiency base."""
    ANOMALY_PRO_FLAT = 31203
    """Anomaly proficiency flat."""

    ANOMALY_MASTERY_BASE = 31401
    ANOMALY_MASTERY_PERCENT = 31402
    ANOMALY_MASTERY_FLAT = 31403

    PHYSICAL_DMG_BONUS_BASE = 31501
    PHYSICAL_DMG_BONUS_FLAT = 31503

    FIRE_DMG_BONUS_BASE = 31601
    FIRE_DMG_BONUS_FLAT = 31603

    ICE_DMG_BONUS_BASE = 31701
    ICE_DMG_BONUS_FLAT = 31703

    ELECTRIC_DMG_BONUS_BASE = 31801
    ELECTRIC_DMG_BONUS_FLAT = 31803

    ETHER_DMG_BONUS_BASE = 31901
    ETHER_DMG_BONUS_FLAT = 31903

    AAA_BASE = 32001
    """Automatic Adrelanine Accumulation base."""
    AAA_PERCENT = 32002
    """Automatic Adrenaline Accumulation percent."""
    AAA_FLAT = 32003
    """Automatic Adrenaline Accumulation flat."""

    SHEER_DMG_BONUS_BASE = 32201
    SHEER_DMG_BONUS_FLAT = 32203


class AgentStatType(IntEnum):
    """ZZZ stat type for agents."""

    MAX_HP = 111
    ATK = 121
    DEF = 131
    IMPACT = 122
    CRIT_RATE = 201
    CRIT_DMG = 211
    ANOMALY_PROFICIENCY = 312
    ANOMALY_MASTERY = 314
    PEN_RATIO = 231
    PEN = 232
    ENERGY_REGEN = 305
    SHEER_FORCE = 123
    AAA = 320
    """Automatic Adrenaline Accumulation."""

    PHYSICAL_DMG_BONUS = 315
    FIRE_DMG_BONUS = 316
    ICE_DMG_BONUS = 317
    ELECTRIC_DMG_BONUS = 318
    ETHER_DMG_BONUS = 319
    SHEER_DMG_BONUS = 322


class ProfessionType(StrEnum):
    """ZZZ agent speciality."""

    STUN = "Stun"
    ATTACK = "Attack"
    DEFENSE = "Defense"
    SUPPORT = "Support"
    ANOMALY = "Anomaly"
    RUPTURE = "Rupture"
    UNKNOWN = "Unknown"


class Element(StrEnum):
    """ZZZ element type."""

    PHYSICAL = "Physics"
    FIRE = "Fire"
    ICE = "Ice"
    ELECTRIC = "Elec"
    ETHER = "Ether"
    FIRE_FROST = "FireFrost"
    AURIC_ETHER = "AuricEther"
    UNKNOWN = "Unknown"

    @property
    def icon(self) -> str:
        """The element's icon."""
        return ELEMENT_ICON.format(element=self.value)
