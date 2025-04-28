from __future__ import annotations

import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from ...constants.zzz import RARITY_MAP
from ...enums.zzz import Element, ProfessionType, SkillType, StatType
from ...models.zzz.icon import AgentIcon

__all__ = ("Agent", "AgentColor", "AgentSkill", "DriveDisc", "DriveDiscStat", "Stat", "WEngine")


def _to_formatted_value(value: int, type_: StatType, format_: str) -> str:
    if type_ is StatType.ENERGY_REGEN_BASE:
        return f"{value / 100}"

    if "%" in format_:
        return f"{round(value / 100, 1)}%"
    return str(int(value))


class Stat(BaseModel):
    """Represents a agent's or W-Engine's stat.

    Attributes:
        type: The type of the stat.
        value: The value of the stat.
        name: The name of the stat.
        format: The format specifier.
    """

    type: StatType
    value: int
    name: str
    format: str

    @computed_field
    @property
    def formatted_value(self) -> str:
        """The formatted value of the stat."""
        return _to_formatted_value(self.value, self.type, self.format)


class DriveDiscStat(Stat):
    """Represents a drive disc's stat.

    Attributes:
        type: The type of the stat.
        roll_times: The number of times the stat has been rolled.
        value: The value of the stat.
        name: The name of the stat.
        format: The format specifier.
    """

    type: StatType = Field(alias="PropertyId")
    roll_times: int = Field(alias="PropertyLevel")
    value: int = Field(alias="PropertyValue")

    # Fields that are not in the API response
    name: str = ""
    format: str = ""

    @computed_field
    @property
    def formatted_value(self) -> str:
        """The formatted value of the stat."""
        return _to_formatted_value(self.value, self.type, self.format)


class DriveDisc(BaseModel):
    """Represents a drive disc.

    Attributes:
        slot: The slot number of the drive disc.
        id: The ID of the drive disc.
        uid: The unique identifier of the drive disc.
        level: The level of the drive disc.
        roll_times: The number of times random stats are being rolled.
        main_stat: The main stat of the drive disc.
        sub_stats: List of sub-stats of the drive disc.
        is_locked: Whether the drive disc is marked as locked in-game.
        is_trash: Whether the drive disc is marked as trash in-game.
        rarity_num: The rarity number of the drive disc.
        set_id: The set ID of the drive disc.
    """

    slot: Literal[1, 2, 3, 4, 5, 6] = Field(alias="Slot")

    id: int = Field(alias="Id")
    uid: int = Field(alias="Uid")
    level: int = Field(alias="Level")
    roll_times: int = Field(alias="BreakLevel")

    main_stat: DriveDiscStat = Field(alias="MainPropertyList")
    sub_stats: list[DriveDiscStat] = Field(alias="RandomPropertyList")

    is_locked: bool = Field(alias="IsLocked")
    is_trash: bool = Field(alias="IsTrash")

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
    """Represents a W-Engine.

    Attributes:
        id: The ID of the W-Engine.
        uid: The unique identifier of the W-Engine.
        level: The level of the W-Engine.
        modification: The modification level of the W-Engine.
        phase: The phase level of the W-Engine.
        is_locked: Whether the W-Engine is marked as locked in-game.
        rarity_num: The rarity number of the W-Engine.
        name: The name of the W-Engine.
        specialty: The specialty of the W-Engine.
        icon: The icon of the W-Engine.
        main_stat: The main stat of the W-Engine.
        sub_stat: The sub-stat of the W-Engine.
    """

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
    """Represents a ZZZ agent's skill.

    Attributes:
        level: The level of the skill.
        type: The type of the skill.
    """

    level: int = Field(alias="Level")
    type: SkillType = Field(alias="Index")


class AgentColor(BaseModel):
    """Represents a ZZZ agent's color scheme.

    Attributes:
        accent: The accent color of the agent.
        mindscape: The mindscape color of the agent.
    """

    accent: str = Field(alias="Accent")
    mindscape: str = Field(alias="Mindscape")


class Agent(BaseModel):
    """Represents a ZZZ agent (character).

    Attributes:
        id: The ID of the agent.
        uid: The unique identifier of the agent.
        level: The level of the agent.
        promotion: The promotion level of the agent.
        mindscape: The mindscape level of the agent.
        skin_id: The ID of the agent's skin.
        core_skill_level_num: The core skill level number of the agent.
        is_sig_engine_effect_on: Whether the signature engine effect is on.
        obtained_at: The time when the agent was obtained, in server timezone.
        skills: List of skills for the agent.
        discs: List of drive discs equipped by the agent.
        w_engine: The W-Engine associated with the agent.
        name: The name of the agent.
        rarity_num: The rarity number of the agent.
        elements: List of elements associated with the agent.
        icon: The icon of the agent.
        sig_engine_id: The ID of the signature W-Engine.
        color: The color scheme of the agent.
        highlight_stats: List of stats that are highlighted in the agent menu.
        stats: Dictionary of stats for the agent.
    """

    id: int = Field(alias="Id")
    level: int = Field(alias="Level")
    promotion: Literal[1, 2, 3, 4, 5, 6] = Field(alias="PromotionLevel")
    mindscape: Literal[0, 1, 2, 3, 4, 5, 6] = Field(alias="TalentLevel")
    skin_id: int = Field(alias="SkinId")
    core_skill_level_num: int = Field(alias="CoreSkillEnhancement")

    is_sig_engine_effect_on: bool | None = Field(alias="WeaponEffectState")
    obtained_at: datetime.datetime = Field(alias="ObtainmentTimestamp")

    skills: list[AgentSkill] = Field(alias="SkillLevelList")
    discs: list[DriveDisc] = Field(alias="EquippedList")
    w_engine: WEngine | None = Field(None, alias="Weapon")

    # Fields that are not in the API response
    name: str = Field(default="")
    rarity_num: int = Field(default=0)
    elements: list[Element] = Field(default_factory=list)
    icon: AgentIcon = Field(default=None)  # pyright: ignore[reportAssignmentType]
    sig_engine_id: int = Field(default=0)
    color: AgentColor = Field(default=None)  # pyright: ignore[reportAssignmentType]
    highlight_stats: list[StatType] = Field(default_factory=list)
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
