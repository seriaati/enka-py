from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from ...constants.gi import ASCENSION_TO_MAX_LEVEL, DMG_BONUS_FIGHT_PROPS, PERCENT_STAT_TYPES
from ...enums.gi import Element, EquipmentType, FightPropType, ItemType, StatType
from ...errors import InvalidItemTypeError
from .costume import Costume
from .icon import Icon, Namecard

__all__ = ("Artifact", "Character", "Constellation", "FightProp", "Stat", "Talent", "Weapon")


class Stat(BaseModel):
    """Represents a stat.

    Attributes:
        type: The stat's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK).
        value: The stat's value.
        name: The stat's name.
    """

    type: StatType
    value: float
    name: str = ""

    @computed_field
    @property
    def is_percentage(self) -> bool:
        """Whether this stat is a percentage stat."""
        return self.type.name in PERCENT_STAT_TYPES

    @computed_field
    @property
    def formatted_value(self) -> str:
        """ "The formatted value of the stat."""
        if self.is_percentage:
            return f"{round(self.value, 1)}%"
        return str(round(self.value))


class FightProp(BaseModel):
    """Represents a character's stat (property.)

    Attributes:
        type: The fight prop's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK).
        value: The fight prop's value.
        name: The fight prop's name.
    """

    type: FightPropType | int
    value: float
    name: str = ""

    @field_validator("type", mode="before")
    @classmethod
    def __convert_type(cls, v: int) -> FightPropType | int:
        try:
            return FightPropType(v)
        except ValueError:
            return v

    @computed_field
    @property
    def is_percentage(self) -> bool:
        """Whether this stat is a percentage stat."""
        return isinstance(self.type, FightPropType) and self.type.name in PERCENT_STAT_TYPES

    @computed_field
    @property
    def formatted_value(self) -> str:
        """The formatted value of the stat."""
        if self.is_percentage:
            return f"{round(self.value * 100, 1)}%"
        return f"{round(self.value):,}"


class Artifact(BaseModel):
    """Represents an artifact.

    Attributes:
        id: The artifact's ID.
        main_stat_id: The main stat's ID.
        sub_stat_ids: The sub stats' IDs.
        level: The artifact's level.
        equip_type: The artifact's type (e.g. FLOWER, GOBLET).
        icon: The artifact's icon.
        item_type: The artifact's type.
        name: The artifact's name.
        rarity: The artifact's rarity.
        main_stat: The artifact's main stat.
        sub_stats: The artifact's sub stats.
        set_name: The artifact's set name.
    """

    id: int = Field(alias="itemId")
    main_stat_id: int = Field(alias="mainPropId")
    sub_stat_ids: list[int] = Field(alias="appendPropIdList", default_factory=list)
    level: int
    equip_type: EquipmentType = Field(alias="equipType")
    icon: str
    item_type: ItemType = Field(alias="itemType")
    name: str = Field(alias="nameTextMapHash")
    rarity: int = Field(alias="rankLevel")
    main_stat: Stat = Field(alias="reliquaryMainstat")
    sub_stats: list[Stat] = Field(alias="reliquarySubstats", default_factory=list)
    set_name: str = Field(alias="setNameTextMapHash")

    @field_validator("level", mode="before")
    @classmethod
    def _convert_level(cls, v: int) -> int:
        return v - 1

    @field_validator("icon", mode="before")
    @classmethod
    def _convert_icon(cls, v: str) -> str:
        return f"https://enka.network/ui/{v}.png"

    @field_validator("main_stat", mode="before")
    @classmethod
    def _convert_main_stat(cls, v: dict[str, Any]) -> Stat:
        return Stat(type=StatType(v["mainPropId"]), value=v["statValue"], name="")

    @field_validator("sub_stats", mode="before")
    @classmethod
    def _convert_sub_stats(cls, v: list[dict[str, Any]]) -> list[Stat]:
        return [
            Stat(type=StatType(stat["appendPropId"]), value=stat["statValue"], name="")
            for stat in v
        ]

    @field_validator("name", "set_name", mode="before")
    @classmethod
    def _stringify_text_map_hash(cls, v: str | int) -> str:
        return str(v)


class Weapon(BaseModel):
    """Represents a weapon.

    Attributes:
        item_id: The weapon's ID.
        refinement: The weapon's refinement level (1~5).
        level: The weapon's level.
        ascension: The weapon's ascension level.
        icon: The weapon's icon.
        name: The weapon's name.
        rarity: The weapon's rarity.
        stats: The weapon's stats.
    """

    item_id: int = Field(alias="itemId")
    refinement: Literal[1, 2, 3, 4, 5] = Field(1, alias="affixMap")
    level: int
    ascension: Literal[0, 1, 2, 3, 4, 5, 6] = Field(0, alias="promoteLevel")
    icon: str
    item_type: ItemType = Field(alias="itemType")
    name: str = Field(alias="nameTextMapHash")
    rarity: int = Field(alias="rankLevel")
    stats: list[Stat] = Field(alias="weaponStats")

    @computed_field
    @property
    def max_level(self) -> int:
        return ASCENSION_TO_MAX_LEVEL[self.ascension]

    @field_validator("refinement", mode="before")
    @classmethod
    def _extract_refinement(cls, v: dict[str, int]) -> int:
        return next(iter(v.values())) + 1

    @field_validator("icon", mode="before")
    @classmethod
    def _convert_icon(cls, v: str) -> str:
        return f"https://enka.network/ui/{v}.png"

    @field_validator("stats", mode="before")
    @classmethod
    def _convert_stats(cls, v: list[dict[str, Any]]) -> list[Stat]:
        return [
            Stat(type=StatType(stat["appendPropId"]), value=stat["statValue"], name="")
            for stat in v
            if stat["statValue"] != 0
        ]

    @field_validator("name", mode="before")
    @classmethod
    def _stringify_text_map_hash(cls, v: str | int) -> str:
        return str(v)


class Constellation(BaseModel):
    """Represents a character's constellation.

    Attributes:
        id: The constellation's ID.
        name: The constellation's name.
        icon: The constellation's icon.
        unlocked: Whether the constellation is unlocked.
    """

    id: int
    name: str = ""
    icon: str = ""
    unlocked: bool


class Talent(BaseModel):
    """Represents a character's talent.

    Attributes:
        id: The talent's ID.
        level: The talent's level.
        name: The talent's name.
        icon: The talent's icon.
        is_upgraded: Whether the talent's level is being upgraded by a constellation.
    """

    id: int
    level: int
    name: str = ""
    icon: str = ""
    is_upgraded: bool = False


class Character(BaseModel):
    """Represents a character.

    Attributes:
        id: The character's ID.
        artifacts: The character's artifacts.
        weapon: The character's weapon.
        stats: The character's stats.
        constellations: The character's unlocked constellations.
        talents: The character's talents.
        ascension: The character's ascension level.
        level: The character's level.
        skill_depot_id: The character's skill depot ID.
        name: The character's name.
        talent_extra_level_map: The map of character's extra talent levels, this is only used internally, the wrapper will handle this.
        icon: The character's icon.
        friendship_level: The character's friendship level (1~10).
        element: The character's element.
        talent_order: The character's talent order.
            1. Normal attack
            2. Elemental skill
            3. Elemental burst
        rarity: The character's rarity (4~5).
        max_level: The character's max level.
        highest_dmg_bonus_stat: The character's highest damage bonus stat.
        namecard: The character's namecard. Travelers don't have namecards.
        costume: The character's costume, if any.
        costume_id: The character's costume's ID, if any.
        constellations_unlocked: The number of constellations unlocked.
    """

    id: int = Field(alias="avatarId")
    artifacts: list[Artifact]
    weapon: Weapon
    stats: dict[FightPropType | int, FightProp] = Field(alias="fightPropMap")
    constellations: list[Constellation] = Field(alias="talentIdList", default_factory=list)
    talents: list[Talent] = Field(alias="skillLevelMap")
    ascension: Literal[0, 1, 2, 3, 4, 5, 6]
    level: int
    skill_depot_id: int = Field(alias="skillDepotId")
    talent_extra_level_map: dict[str, int] | None = Field(None, alias="proudSkillExtraLevelMap")
    friendship_level: int = Field(alias="friendshipLevel")

    name: str = ""
    icon: Icon = Icon(side_icon_ui_path="")
    element: Element = Element.ANEMO
    talent_order: list[int] = Field(default_factory=list)
    rarity: int = 0
    namecard: Namecard | None = None
    costume: Costume | None = None
    costume_id: int | None = Field(None, alias="costumeId")

    model_config = {"arbitrary_types_allowed": True}

    @computed_field
    @property
    def max_level(self) -> Literal[20, 40, 50, 60, 70, 80, 90]:
        """The character's max level."""
        return ASCENSION_TO_MAX_LEVEL[self.ascension]

    @computed_field
    @property
    def highest_dmg_bonus_stat(self) -> FightProp:
        """The character's highest damage bonus stat.

        Returns the highest stat value from the damage bonus stats (elemental damage bonus, physical damage bonus, etc.).
        """
        return max(
            (
                stat
                for stat in self.stats.values()
                if isinstance(stat.type, FightPropType) and stat.type.name in DMG_BONUS_FIGHT_PROPS
            ),
            key=lambda stat: stat.value,
        )

    @computed_field
    @property
    def specialized_stat(self) -> FightProp:
        """The character's specialized stat

        Returns the highest stat value from the specialized stats (elemental damage bonus and healing bonus).
        """
        specialized_stats = [*list(DMG_BONUS_FIGHT_PROPS), FightPropType.FIGHT_PROP_HEAL_ADD.name]
        return max(
            (
                stat
                for stat in self.stats.values()
                if isinstance(stat.type, FightPropType) and stat.type.name in specialized_stats
            ),
            key=lambda stat: stat.value,
        )

    @computed_field
    @property
    def constellations_unlocked(self) -> int:
        """The number of constellations unlocked."""
        return len([c for c in self.constellations if c.unlocked])

    @field_validator("ascension", mode="before")
    @classmethod
    def _intify_ascension(cls, v: str) -> int:
        return int(v)

    @field_validator("stats", mode="before")
    @classmethod
    def _convert_stats(cls, v: dict[str, float]) -> dict[FightPropType | int, FightProp]:
        result: dict[FightPropType | int, FightProp] = {}
        for k, value in v.items():
            if k.isdigit() and int(k) in FightPropType._value2member_map_:
                result[FightPropType(int(k))] = FightProp(
                    type=FightPropType(int(k)), value=value, name=""
                )
            else:
                result[int(k)] = FightProp(type=int(k), value=value, name="")
        return result

    @field_validator("constellations", mode="before")
    @classmethod
    def _convert_constellations(cls, v: list[int]) -> list[Constellation]:
        return [
            Constellation(id=constellation_id, name="", icon="", unlocked=True)
            for constellation_id in v
        ]

    @field_validator("talents", mode="before")
    @classmethod
    def _convert_talents(cls, v: dict[str, int]) -> list[Talent]:
        return [Talent(id=int(k), level=v, name="", icon="") for k, v in v.items()]

    @field_validator("weapon", mode="before")
    @classmethod
    def _flatten_weapon_data(cls, v: dict[str, Any]) -> dict[str, Any]:
        v.update(v["weapon"])
        v.update(v["flat"])
        v.pop("weapon")
        v.pop("flat")
        return v

    @field_validator("artifacts", mode="before")
    @classmethod
    def _flatten_artifacts_data(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for artifact in v:
            artifact.update(artifact["reliquary"])
            artifact.update(artifact["flat"])
            artifact.pop("reliquary")
            artifact.pop("flat")

        return v

    @model_validator(mode="before")
    @classmethod
    def _transform_values(cls, v: dict[str, Any]) -> dict[str, Any]:
        # convert prop map to level and ascension
        prop_map = v["propMap"]
        try:
            v["level"] = prop_map["4001"]["val"]
        except KeyError:
            v["level"] = 1
        try:
            v["ascension"] = prop_map["1002"]["val"]
        except KeyError:
            v["ascension"] = 0

        # convert equipment list to weapon and artifacts
        equip_list = v["equipList"]
        v["artifacts"] = []

        for equipment in equip_list:
            if "weapon" in equipment:
                v["weapon"] = equipment
            elif "reliquary" in equipment:
                v["artifacts"].append(equipment)
            else:
                raise InvalidItemTypeError

        # friendship level
        v["friendshipLevel"] = v["fetterInfo"]["expLevel"]

        return v
