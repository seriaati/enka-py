from __future__ import annotations

import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from ...constants.zzz import RARITY_MAP
from ...enums.zzz import Element, ProfessionType, SkillType, StatType
from ...models.zzz.icon import AgentIcon

__all__ = ("Agent", "AgentColor", "AgentSkill", "DriveDisc", "DriveDiscStat", "Stat", "WEngine")


class Stat(BaseModel):
    type: StatType
    value: int
    name: str
    format: str

    @property
    def formatted_value(self) -> str:
        """The formatted value of the stat."""
        if "%" in self.format:
            return f"{round(self.value / 100, 1)}%"
        return str(int(self.value))

    def as_dict(self) -> dict[int, int]:
        return {self.type.value: self.value}


class DriveDiscStat(Stat):
    """ZZZ drive disc stat."""

    type: StatType = Field(alias="PropertyId")
    roll_times: int = Field(alias="PropertyLevel")
    value: int = Field(alias="PropertyValue")

    # Fields that are not in the API response
    name: str = ""
    format: str = ""


class DriveDisc(BaseModel):
    "ZZZ drive disc."

    slot: Literal[1, 2, 3, 4, 5, 6] = Field(alias="Slot")

    id: int = Field(alias="Id")
    uid: int = Field(alias="Uid")
    level: int = Field(alias="Level")
    roll_times: int = Field(alias="BreakLevel")
    """Number of times random stats are being rolled."""

    main_stat: DriveDiscStat = Field(alias="MainPropertyList")
    sub_stats: list[DriveDiscStat] = Field(alias="RandomPropertyList")

    is_locked: bool = Field(alias="IsLocked")
    is_trash: bool = Field(alias="IsTrash")
    """Whether the disc is marked as trash in-game."""

    # Fields that are not in the API response
    rarity_num: int = Field(default=0)
    set_id: int = Field(default=0)

    @field_validator("main_stat", mode="before")
    @classmethod
    def __get_first_main_stat_value(cls, value: list[dict[str, Any]]) -> dict[str, Any]:
        return value[0]

    @model_validator(mode="before")
    @classmethod
    def __unnest_info(cls, value: dict[str, Any]) -> dict[str, Any]:
        info = value.pop("Equipment")
        value.update(info)
        return value

    @computed_field
    @property
    def rarity(self) -> Literal["S", "A", "B", "?"]:
        """The drive disc's rarity."""
        return RARITY_MAP.get(self.rarity_num, "?")


class WEngine(BaseModel):
    "ZZZ w-engine."

    id: int = Field(alias="Id")
    uid: int = Field(alias="Uid")
    level: int = Field(alias="Level")
    modification: Literal[0, 1, 2, 3, 4, 5] = Field(alias="BreakLevel")
    phase: Literal[1, 2, 3, 4, 5] = Field(alias="UpgradeLevel")

    is_locked: bool = Field(alias="IsLocked")

    # Fields that are not in the API response
    rarity_num: int = Field(default=0)
    name: str = ""
    specialty: ProfessionType = ProfessionType.UNKNOWN
    icon: str = ""
    main_stat: Stat = Field(default=None)  # pyright: ignore[reportAssignmentType]
    sub_stat: Stat = Field(default=None)  # pyright: ignore[reportAssignmentType]

    @computed_field
    @property
    def rarity(self) -> Literal["S", "A", "B", "?"]:
        """The W-Engine's rarity."""
        return RARITY_MAP.get(self.rarity_num, "?")


class AgentSkill(BaseModel):
    """ZZZ agent skill."""

    level: int = Field(alias="Level")
    type: SkillType = Field(alias="Index")


class AgentColor(BaseModel):
    accent: str = Field(alias="Accent")
    mindscape: str = Field(alias="Mindscape")


class Agent(BaseModel):
    """ZZZ agent."""

    id: int = Field(alias="Id")
    level: int = Field(alias="Level")
    promotion: Literal[1, 2, 3, 4, 5, 6] = Field(alias="PromotionLevel")
    mindscape: Literal[0, 1, 2, 3, 4, 5, 6] = Field(alias="TalentLevel")
    skin_id: int = Field(alias="SkinId")
    core_skill_level_num: int = Field(alias="CoreSkillEnhancement")

    is_sig_engine_effect_on: bool | None = Field(alias="WeaponEffectState")
    obtained_at: datetime.datetime = Field(alias="ObtainmentTimestamp")
    """Time when the agent was obtained , in server timezone."""

    skills: list[AgentSkill] = Field(alias="SkillLevelList")
    discs: list[DriveDisc] = Field(alias="EquippedList")
    w_engine: WEngine = Field(alias="Weapon")

    # Fields that are not in the API response
    name: str = Field(default="")
    rarity_num: int = Field(default=0)
    elements: list[Element] = Field(default_factory=list)
    icon: AgentIcon = Field(default=None)  # pyright: ignore[reportAssignmentType]
    sig_engine_id: int = Field(default=0)
    """Signature W-Engine ID."""
    color: AgentColor = Field(default=None)  # pyright: ignore[reportAssignmentType]
    highlight_stats: list[StatType] = Field(default_factory=list)
    """Stats that are highlighted in the agent menu."""
    stats: dict[StatType, Stat] = Field(default_factory=dict)

    @field_validator("is_sig_engine_effect_on", mode="before")
    @classmethod
    def __convert_is_sig_engine_effect_on(cls, value: int) -> bool | None:
        # [0: None, 1: OFF, 2: ON]
        return {0: None, 1: False, 2: True}[value]

    @computed_field
    @property
    def rarity(self) -> Literal["S", "A", "B", "?"]:
        """The agent's rarity."""
        return RARITY_MAP.get(self.rarity_num, "?")

    @computed_field
    @property
    def core_skill_level(self) -> Literal["A", "B", "C", "D", "E", "F"]:
        """The agent's core skill level."""
        return "ABCDEF"[self.core_skill_level_num - 1]  # pyright: ignore[reportReturnType]
