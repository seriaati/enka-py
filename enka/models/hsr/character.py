from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from ...constants.hsr import ASCENSION_TO_MAX_LEVEL, DMG_BONUS_PROPS, PERCENT_STAT_TYPES
from ...enums.hsr import Element, Path, RelicType, StatType, TraceType
from ...utils import round_down
from .icon import CharacterIcon, LightConeIcon

__all__ = ("Character", "LightCone", "Relic", "RelicSubAffix", "Stat", "Trace")


class Trace(BaseModel):
    """Represents a character's trace (skill).

    Attributes:
        id: The trace's ID.
        level: The trace's level.
        boosted: Whether the trace's level is boosted by an activated eidolon's effect.
        icon: The trace's icon.
        max_level: The trace's maximum level.
        anchor: The trace's anchor.
        type: The trace's type.
    """

    id: int = Field(alias="pointId")
    level: int
    boosted: bool = False
    """Whether the level of this trace is boosted by an activated eidolon's effect."""

    # Following fields are added in post-processing
    icon: str = ""
    max_level: int = 0
    anchor: str = ""
    type: TraceType = TraceType.UNKNOWN


class Stat(BaseModel):
    """Represents a HSR stat.

    Attributes:
        type: The type of the stat.
        value: The value of the stat.
        name: The name of the stat.
        icon: The icon of the stat.
    """

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
        """The formatted value of the stat."""
        if self.is_percentage:
            return f"{round_down(self.value * 100, 1)}%"
        if self.type in {StatType.SPD, StatType.SPEED_DELTA}:
            return str(round_down(self.value, 2))
        return str(int(round_down(self.value, 0)))


class LightCone(BaseModel):
    """Represents a light cone (weapon.)

    Attributes:
        id: The light cone's ID.
        level: The light cone's level.
        ascension: The light cone's ascension level.
        superimpose: The light cone's superimpose level.
        name: The name of the light cone.
        stats: The stats of the light cone.
        rarity: The rarity of the light cone.
        icon: The icon of the light cone.
        path: The light cone's path.
    """

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
    path: Path = Path.NONE

    @computed_field
    @property
    def max_level(self) -> Literal[20, 30, 40, 50, 60, 70, 80]:
        """Light Cone's max level."""
        return ASCENSION_TO_MAX_LEVEL[self.ascension]

    @field_validator("name", mode="before")
    @classmethod
    def _stringify_name(cls, value: int) -> str:
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def _flatten_flat(cls, values: dict[str, Any]) -> dict[str, Any]:
        flat_ = values.pop("_flat")
        values.update(flat_)
        return values


class RelicSubAffix(BaseModel):
    """Represents a relic's sub-stat information.

    Attributes:
        id: The ID of the sub-stat.
        cnt: The count of the sub-stat.
        step: The step of the sub-stat.
    """

    id: int = Field(alias="affixId")
    cnt: int
    step: int | None = None


class Relic(BaseModel):
    """Represents a relic in HSR.

    Attributes:
        id: The relic's ID.
        level: The relic's level.
        type: The relic's type.
        main_affix_id: The ID of the main affix.
        set_name: The name of the relic set.
        set_id: The ID of the relic set.
        stats: The stats of the relic.
        sub_affix_list: List of sub-stat information for the relic.
        icon: The icon of the relic.
        rarity: The rarity of the relic.
    """

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
    @classmethod
    def _stringify_set_name(cls, value: int) -> str:
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def _flatten_flat(cls, values: dict[str, Any]) -> dict[str, Any]:
        flat_ = values.pop("_flat")
        values.update(flat_)
        return values

    @computed_field
    @property
    def main_stat(self) -> Stat:
        """The relic's main stat."""
        return self.stats[0]

    @computed_field
    @property
    def sub_stats(self) -> list[Stat]:
        """The relic's sub-stats."""
        return self.stats[1:]


class Eidolon(BaseModel):
    """Represents a character's eidolon.

    Attributes:
        id: The eidolon's ID.
        icon: The eidolon's icon.
        unlocked: Whether the eidolon is unlocked.
    """

    id: int
    icon: str
    unlocked: bool


class Character(BaseModel):
    """Represents a character in HSR.

    Attributes:
        level: The character's level.
        ascension: The character's ascension level.
        id: The character's ID.
        traces: List of the character's traces (skills).
        light_cone: The character's light cone (weapon).
        relics: List of the character's relics.
        eidolons: List of the character's eidolons.
        eidolons_unlocked: The number of unlocked eidolons.
        is_assist: Whether the character is an assist character.
        icon: The character's icon.
        name: The character's name.
        rarity: The character's rarity.
        element: The character's element (type.)
        path: The character's path.
        stats: The character's stats.
    """

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
