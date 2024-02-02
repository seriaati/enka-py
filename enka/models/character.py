from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .icon import Icon

from ..exceptions import InvalidItemTypeError
from ..enums import Element, EquipmentType, ItemType, StatType, FightPropType
from ..constants import PERCENT_STAT_TYPES

__all__ = (
    "Stat",
    "FightProp",
    "Artifact",
    "Character",
    "Weapon",
    "Constellation",
    "Talent",
)


class Stat(BaseModel):
    """
    Represents a stat.

    Attributes
    ----------
    type: :class:`StatType`
        The stat's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK, etc.)
    value: :class:`float`
        The stat's value.
    name: :class:`str`
        The stat's name.
    """

    type: StatType
    value: float
    name: str = Field(None)

    @property
    def is_percentage(self) -> bool:
        return self.type.name in PERCENT_STAT_TYPES

    @property
    def formatted_value(self) -> str:
        if self.is_percentage:
            return f"{round(self.value, 1)}%"
        return str(round(self.value))


class FightProp(BaseModel):
    """
    Represents a fight prop.

    Attributes
    ----------
    type: :class:`FightProp`
        The fight prop's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK, etc.)
    value: :class:`float`
        The fight prop's value.
    name: :class:`str`
        The fight prop's name.
    """

    type: FightPropType
    value: float
    name: str = Field(None)

    @property
    def is_percentage(self) -> bool:
        return self.type.name in PERCENT_STAT_TYPES

    @property
    def formatted_value(self) -> str:
        if self.is_percentage:
            return f"{round(self.value, 1)}%"
        return str(round(self.value))


class Artifact(BaseModel):
    """
    Represents an artifact.

    Attributes
    ----------
    item_id: :class:`int`
        The artifact's ID.
    main_stat_id: :class:`int`
        The main stat's ID.
    sub_stat_ids: List[:class:`int`]
        The sub stats' IDs.
    level: :class:`int`
        The artifact's level.
    equip_type: :class:`EquipmentType`
        The artifact's type (e.g. FLOWER, GOBLET, etc.)
    icon: :class:`str`
        The artifact's icon.
    item_type: :class:`ItemType`
        The artifact's type.
    name: :class:`str`
        The artifact's name.
    rarity: :class:`int`
        The artifact's rarity.
    main_stat: :class:`MainStat`
        The artifact's main stat.
    sub_stats: List[:class:`SubStat`]
        The artifact's sub stats.
    set_name: :class:`str`
        The artifact's set name.
    """

    item_id: int = Field(alias="itemId")
    main_stat_id: int = Field(alias="mainPropId")
    sub_stat_ids: List[int] = Field(alias="appendPropIdList")
    level: int
    equip_type: EquipmentType = Field(alias="equipType")
    icon: str
    item_type: ItemType = Field(alias="itemType")
    name: str = Field(alias="nameTextMapHash")
    rarity: int = Field(alias="rankLevel")
    main_stat: Stat = Field(alias="reliquaryMainstat")
    sub_stats: List[Stat] = Field(alias="reliquarySubstats")
    set_name: str = Field(alias="setNameTextMapHash")

    @field_validator("level", mode="before")
    def _convert_level(cls, v: int) -> int:
        return v - 1

    @field_validator("icon", mode="before")
    def _convert_icon(cls, v: str) -> str:
        return f"https://enka.network/ui/{v}.png"

    @field_validator("main_stat", mode="before")
    def _convert_main_stat(cls, v: Dict[str, Any]) -> Stat:
        return Stat(type=StatType(v["mainPropId"]), value=v["statValue"], name="")

    @field_validator("sub_stats", mode="before")
    def _convert_sub_stats(cls, v: List[Dict[str, Any]]) -> List[Stat]:
        return [
            Stat(type=StatType(stat["appendPropId"]), value=stat["statValue"], name="")
            for stat in v
        ]


class Weapon(BaseModel):
    """
    Represents a weapon.

    Attributes
    ----------
    item_id: :class:`int`
        The weapon's ID.
    refinement: :class:`int`
        The weapon's refinement level (1~5).
    level: :class:`int`
        The weapon's level.
    ascension: :class:`int`
        The weapon's ascension level.
    icon: :class:`str`
        The weapon's icon.
    name: :class:`str`
        The weapon's name.
    rarity: :class:`int`
        The weapon's rarity.
    stats: List[:class:`WeaponStat`]
        The weapon's stats.
    """

    item_id: int = Field(alias="itemId")
    refinement: int = Field(1, alias="affixMap")
    level: int
    ascension: int = Field(0, alias="promoteLevel")
    icon: str
    item_type: ItemType = Field(alias="itemType")
    name: str = Field(alias="nameTextMapHash")
    rarity: int = Field(alias="rankLevel")
    stats: List[Stat] = Field(alias="weaponStats")

    @field_validator("refinement", mode="before")
    def _extract_refinement(cls, v: Dict[str, int]) -> int:
        return list(v.values())[0] + 1

    @field_validator("icon", mode="before")
    def _convert_icon(cls, v: str) -> str:
        return f"https://enka.network/ui/{v}.png"

    @field_validator("stats", mode="before")
    def _convert_stats(cls, v: List[Dict[str, Any]]) -> List[Stat]:
        return [
            Stat(type=StatType(stat["appendPropId"]), value=stat["statValue"], name="")
            for stat in v
        ]


class Constellation(BaseModel):
    """
    Represents a character's constellation.

    Attributes
    ----------
    id: :class:`int`
        The constellation's ID.
    name: :class:`str`
        The constellation's name.
    icon: :class:`str`
        The constellation's icon.
    """

    id: int
    name: str = Field(None)
    icon: str = Field(None)


class Talent(BaseModel):
    """
    Represents a character's talent.

    Attributes
    ----------
    id: :class:`int`
        The talent's ID.
    level: :class:`int`
        The talent's level.
    name: :class:`str`
        The talent's name.
    icon: :class:`str`
        The talent's icon.
    """

    id: int
    level: int
    name: str = Field(None)
    icon: str = Field(None)


class Character(BaseModel):
    """
    Represents a character.

    Attributes
    ----------
    id: :class:`int`
        The character's ID.
    artifacts: List[:class:`Artifact`]
        The character's artifacts.
    weapon: :class:`Weapon`
        The character's weapon.
    stats: Dict[:class:`CharacterStat`]
        The character's stats.
    constellations: List[:class:`Constellation`]
        The character's unlocked constellations.
    talents: List[:class:`Talent`]
        The character's talents.
    ascension: :class:`int`
        The character's ascension level.
    level: :class:`int`
        The character's level.
    skill_depot_id: :class:`int`
        The character's skill depot ID.
    name: :class:`str`
        The character's name.
    talent_extra_level_map: Optional[Dict[:class:`str`, :class:`int`]]
        The map of character's extra talent levels, this is only used internally, the wrapper will handle this.
    icon: :class:`Icon`
        The character's icon.
    friendship_level: :class:`int`
        The character's friendship level (1~10).
    element: :class:`Element`
        The character's element.
    talent_order: List[:class:`int`]
        The character's talent order.
        1. Normal attack
        2. Elemental skill
        3. Elemental burst
    rarity: :class:`int`
        The character's rarity (4~5).
    """

    id: int = Field(alias="avatarId")
    artifacts: List[Artifact]
    weapon: Weapon
    stats: Dict[FightPropType, FightProp] = Field(alias="fightPropMap")
    constellations: List[Constellation] = Field([], alias="talentIdList")
    talents: List[Talent] = Field(alias="skillLevelMap")
    ascension: int
    level: int
    skill_depot_id: int = Field(alias="skillDepotId")
    name: str = Field(None)
    icon: Icon = Field(None)
    talent_extra_level_map: Optional[Dict[str, int]] = Field(None, alias="proudSkillExtraLevelMap")
    friendship_level: int = Field(alias="friendshipLevel")
    element: Element = Field(None)
    talent_order: list[int] = Field(None)
    rarity: int = Field(None)

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("stats", mode="before")
    def _convert_stats(cls, v: Dict[str, float]) -> Dict[FightPropType, FightProp]:
        return {
            FightPropType(int(k)): FightProp(type=FightPropType(int(k)), value=v, name="")
            for k, v in v.items()
        }

    @field_validator("constellations", mode="before")
    def _convert_constellations(cls, v: List[int]) -> List[Constellation]:
        return [Constellation(id=constellation_id, name="", icon="") for constellation_id in v]

    @field_validator("talents", mode="before")
    def _convert_talents(cls, v: Dict[str, int]) -> List[Talent]:
        return [Talent(id=int(k), level=v, name="", icon="") for k, v in v.items()]

    @field_validator("weapon", mode="before")
    def _flatten_weapon_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        v.update(v["weapon"])
        v.update(v["flat"])
        v.pop("weapon")
        v.pop("flat")
        return v

    @field_validator("artifacts", mode="before")
    def _flatten_artifacts_data(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for artifact in v:
            artifact.update(artifact["reliquary"])
            artifact.update(artifact["flat"])
            artifact.pop("reliquary")
            artifact.pop("flat")

        return v

    @model_validator(mode="before")
    def _transform_values(cls, v: Dict[str, Any]) -> Dict[str, Any]:
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
