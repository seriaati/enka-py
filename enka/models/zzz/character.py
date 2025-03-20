from __future__ import annotations

import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from ...enums.zzz import SkillType, StatType

__all__ = ("Agent", "AgentSkill", "DriveDisc", "DriveDiscStat", "WEngine")


class DriveDiscStat(BaseModel):
    """ZZZ drive disc stat."""

    type: StatType | int = Field(alias="PropertyId")
    level: int = Field(alias="Level")
    value: int = Field(alias="Value")

    @field_validator("type", mode="before")
    @classmethod
    def __convert_type(cls, value: int) -> StatType | int:
        try:
            return StatType(value)
        except ValueError:
            return value


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


class WEngine(BaseModel):
    "ZZZ w-engine."

    id: int = Field(alias="Id")
    uid: int = Field(alias="Uid")
    level: int = Field(alias="Level")
    modification: Literal[0, 1, 2, 3, 4, 5] = Field(alias="BreakLevel")
    phase: Literal[1, 2, 3, 4, 5] = Field(alias="UpgradeLevel")

    is_locked: bool = Field(alias="IsLocked")


class AgentSkill(BaseModel):
    """ZZZ agent skill."""

    level: int
    type: SkillType


class Agent(BaseModel):
    """ZZZ agent."""

    id: int = Field(alias="Id")
    level: int = Field(alias="Level")
    promotion: Literal[1, 2, 3, 4, 5, 6] = Field(alias="PromotionLevel")
    mindscape: Literal[0, 1, 2, 3, 4, 5, 6] = Field(alias="TalentLevel")
    skin_id: int = Field(alias="SkinId")
    core_skill_level: Literal["A", "B", "C", "D", "E", "F"] = Field(alias="CoreSkillEnahncement")

    is_sig_weapon_effect_on: bool | None = Field(alias="WeaponEffectState")
    obtained_at: datetime.datetime = Field(alias="ObtainmentTimestamp")
    """Time when the agent was obtained , in server timezone."""

    skills: list[AgentSkill] = Field(alias="SkillLevelList")
    discs: list[DriveDisc] = Field(alias="EquippedList")
    engine: WEngine = Field(alias="Weapon")

    @field_validator("core_skill_level", mode="before")
    @classmethod
    def __convert_core_skill_level(cls, value: int) -> Literal["A", "B", "C", "D", "E", "F"]:
        return "ABCDEF"[value - 1]  # pyright: ignore[reportReturnType]

    @field_validator("is_sig_weapon_effect_on", mode="before")
    @classmethod
    def __convert_is_sig_weapon_effect_on(cls, value: int) -> bool | None:
        # [0: None, 1: OFF, 2: ON]
        return {0: None, 1: False, 2: True}[value]
