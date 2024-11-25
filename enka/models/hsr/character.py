from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from ...constants.hsr import ASCENSION_TO_MAX_LEVEL, DMG_BONUS_PROPS, PERCENT_STAT_TYPES
from ...enums.hsr import Element, Path, RelicType, StatType
from ...utils import round_down
from .icon import CharacterIcon, LightConeIcon

__all__ = ("Character", "LightCone", "Relic", "RelicSubAffix", "Stat", "Trace")


class Trace(BaseModel):
    id: int = Field(alias="pointId")
    level: int
    boosted: bool = False
    """Whether the level of this trace is boosted by an activated eidolon's effect."""

    # Following fields are added in post-processing
    icon: str = ""
    max_level: int = 0
    anchor: str = ""
    type: int = 0


class Stat(BaseModel):
    type: StatType
    value: float

    # Following fields are added in post-processing
    name: str = ""
    icon: str = ""

    @computed_field
    @property
    def is_percentage(self) -> bool:
        """Whether the stat is a percentage stat."""
        return self.type.value in PERCENT_STAT_TYPES

    @computed_field
    @property
    def formatted_value(self) -> str:
        """Returns the formatted value of the stat."""
        if self.is_percentage:
            return f"{round_down(self.value * 100, 1)}%"
        else:
            if self.type in {StatType.SPD, StatType.SPEED_DELTA}:
                return str(round_down(self.value, 2))
            return str(int(round_down(self.value, 0)))


class LightCone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int = Field(alias="tid")
    level: int
    ascension: Literal[0, 1, 2, 3, 4, 5, 6] = Field(0, alias="promotion")
    superimpose: Literal[1, 2, 3, 4, 5] = Field(alias="rank")
    name: str  # Returned as text map hash in the API response
    stats: list[Stat] = Field(alias="props")

    # Following fields are added in post-processing
    icon: LightConeIcon = LightConeIcon(light_cone_id=0)
    rarity: Literal[3, 4, 5] = 3

    @computed_field
    @property
    def max_level(self) -> Literal[20, 30, 40, 50, 60, 70, 80]:
        """Light Cone's max level."""
        return ASCENSION_TO_MAX_LEVEL[self.ascension]

    @field_validator("name", mode="before")
    def _stringify_name(cls, value: int) -> str:
        return str(value)

    @model_validator(mode="before")
    def _flatten_flat(cls, values: dict[str, Any]) -> dict[str, Any]:
        flat_ = values.pop("_flat")
        values.update(flat_)
        return values


class RelicSubAffix(BaseModel):
    id: int = Field(alias="affixId")
    cnt: int
    step: int | None = None


class Relic(BaseModel):
    id: int = Field(alias="tid")
    level: int = 0
    type: RelicType
    main_affix_id: int = Field(alias="mainAffixId")
    set_name: str = Field(alias="setName")  # Returned as text map hash in the API response
    set_id: int = Field(alias="setID")
    stats: list[Stat] = Field(alias="props")
    sub_affix_list: list[RelicSubAffix] = Field(alias="subAffixList", default_factory=list)

    # The following fields are added in post-processing
    icon: str = ""
    rarity: Literal[3, 4, 5] = 3

    @field_validator("set_name", mode="before")
    def _stringify_set_name(cls, value: int) -> str:
        return str(value)

    @model_validator(mode="before")
    def _flatten_flat(cls, values: dict[str, Any]) -> dict[str, Any]:
        flat_ = values.pop("_flat")
        values.update(flat_)
        return values

    @computed_field
    @property
    def main_stat(self) -> Stat:
        return self.stats[0]

    @computed_field
    @property
    def sub_stats(self) -> list[Stat]:
        return self.stats[1:]


class Eidolon(BaseModel):
    id: int
    icon: str


class Character(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    level: int
    ascension: Literal[0, 1, 2, 3, 4, 5, 6] = Field(0, alias="promotion")
    id: int = Field(alias="avatarId")
    traces: list[Trace] = Field(alias="skillTreeList")
    light_cone: LightCone | None = Field(None, alias="equipment")
    relics: list[Relic] = Field(alias="relicList", default_factory=list)
    eidolons: list[Eidolon] = Field(default_factory=list)
    eidolons_unlocked: int = Field(0, alias="rank")
    is_assist: bool = Field(False, alias="_assist")

    # Following fields are added in post-processing
    icon: CharacterIcon = CharacterIcon(character_id=0)
    name: str = ""
    rarity: Literal[4, 5] = 4
    element: Element = Element.FIRE
    path: Path = Path.ABUNDANCE
    stats: dict[StatType, Stat] = Field(default_factory=dict)

    @computed_field
    @property
    def max_level(self) -> Literal[20, 30, 40, 50, 60, 70, 80]:
        """Character's max level."""
        return ASCENSION_TO_MAX_LEVEL[self.ascension]

    @computed_field
    @property
    def highest_dmg_bonus_stat(self) -> Stat:
        """Character's highest damage bonus stat."""
        return max(
            (stat for stat in self.stats.values() if stat.type in DMG_BONUS_PROPS.values()),
            key=lambda stat: stat.value,
            default=next(
                stat
                for stat in self.stats.values()
                if stat.type.value == DMG_BONUS_PROPS[self.element]
            ),
        )
