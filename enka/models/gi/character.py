from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from .costume import Costume
from .icon import Icon, Namecard
from ...errors import InvalidItemTypeError
from ...enums.gi import Element, EquipmentType, ItemType, StatType, FightPropType
from ...constants.gi import ASCENSION_TO_MAX_LEVEL, DMG_BONUS_FIGHT_PROPS, PERCENT_STAT_TYPES

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

    Attributes:
        type (StatType): The stat's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK, etc.).
        value (float): The stat's value.
        name (str): The stat's name.
    """

    type: StatType
    value: float
    name: str = Field(None)

    @computed_field
    @property
    def is_percentage(self) -> bool:
        return self.type.name in PERCENT_STAT_TYPES

    @computed_field
    @property
    def formatted_value(self) -> str:
        if self.is_percentage:
            return f"{round(self.value, 1)}%"
        return str(round(self.value))


class FightProp(BaseModel):
    """
    Represents a fight prop.

    Attributes:
        type (FightPropType): The fight prop's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK, etc.).
        value (float): The fight prop's value.
        name (str): The fight prop's name.
    """

    type: FightPropType
    value: float
    name: str = Field(None)

    @computed_field
    @property
    def is_percentage(self) -> bool:
        return self.type.name in PERCENT_STAT_TYPES

    @computed_field
    @property
    def formatted_value(self) -> str:
        if self.is_percentage:
            return f"{round(self.value * 100, 1)}%"
        return f"{round(self.value):,}"


class Artifact(BaseModel):
    """
    Represents an artifact.

    Attributes:
        id (int): The artifact's ID.
        main_stat_id (int): The main stat's ID.
        sub_stat_ids (List[int]): The sub stats' IDs.
        level (int): The artifact's level.
        equip_type (EquipmentType): The artifact's type (e.g. FLOWER, GOBLET, etc.).
        icon (str): The artifact's icon.
        item_type (ItemType): The artifact's type.
        name (str): The artifact's name.
        rarity (int): The artifact's rarity.
        main_stat (MainStat): The artifact's main stat.
        sub_stats (List[SubStat]): The artifact's sub stats.
        set_name (str): The artifact's set name.
    """

    id: int = Field(alias="itemId")
    main_stat_id: int = Field(alias="mainPropId")
    sub_stat_ids: List[int] = Field(alias="appendPropIdList", default_factory=list)
    level: int
    equip_type: EquipmentType = Field(alias="equipType")
    icon: str
    item_type: ItemType = Field(alias="itemType")
    name: str = Field(alias="nameTextMapHash")
    rarity: int = Field(alias="rankLevel")
    main_stat: Stat = Field(alias="reliquaryMainstat")
    sub_stats: List[Stat] = Field(alias="reliquarySubstats", default_factory=list)
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

    @field_validator("name", "set_name", mode="before")
    def _stringify_text_map_hash(cls, v: str | int) -> str:
        return str(v)


class Weapon(BaseModel):
    """
    Represents a weapon.

    Args:
        item_id (int): The weapon's ID.
        refinement (int): The weapon's refinement level (1~5).
        level (int): The weapon's level.
        ascension (int): The weapon's ascension level.
        icon (str): The weapon's icon.
        name (str): The weapon's name.
        rarity (int): The weapon's rarity.
        stats (List[WeaponStat]): The weapon's stats.
    """

    item_id: int = Field(alias="itemId")
    refinement: Literal[1, 2, 3, 4, 5] = Field(1, alias="affixMap")
    level: int
    ascension: Literal[0, 1, 2, 3, 4, 5, 6] = Field(0, alias="promoteLevel")
    icon: str
    item_type: ItemType = Field(alias="itemType")
    name: str = Field(alias="nameTextMapHash")
    rarity: int = Field(alias="rankLevel")
    stats: List[Stat] = Field(alias="weaponStats")

    @computed_field
    @property
    def max_level(self) -> int:
        return ASCENSION_TO_MAX_LEVEL[self.ascension]

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

    @field_validator("name", mode="before")
    def _stringify_text_map_hash(cls, v: str | int) -> str:
        return str(v)


class Constellation(BaseModel):
    """
    Represents a character's constellation.

    Attributes:
        id (int): The constellation's ID.
        name (str): The constellation's name.
        icon (str): The constellation's icon.
        unlocked (bool): Whether the constellation is unlocked.
    """

    id: int
    name: str = Field(None)
    icon: str = Field(None)
    unlocked: bool


class Talent(BaseModel):
    """
    Represents a character's talent.

    Attributes:
        id (int): The talent's ID.
        level (int): The talent's level.
        name (str): The talent's name.
        icon (str): The talent's icon.
        is_upgraded (bool): Whether the talent is upgraded by a constellation.
    """

    id: int
    level: int
    name: str = Field(None)
    icon: str = Field(None)
    is_upgraded: bool = False


class Character(BaseModel):
    """Represents a character.

    Attributes:
        id (int): The character's ID.
        artifacts (List[Artifact]): The character's artifacts.
        weapon (Weapon): The character's weapon.
        stats (Dict[FightPropType, FightProp]): The character's stats.
        constellations (List[Constellation]): The character's unlocked constellations.
        talents (List[Talent]): The character's talents.
        ascension (Literal[0, 1, 2, 3, 4, 5, 6]): The character's ascension level.
        level (int): The character's level.
        skill_depot_id (int): The character's skill depot ID.
        name (str): The character's name.
        talent_extra_level_map (Optional[Dict[str, int]]): The map of character's extra talent levels, this is only used internally, the wrapper will handle this.
        icon (Icon): The character's icon.
        friendship_level (int): The character's friendship level (1~10).
        element (Element): The character's element.
        talent_order (List[int]): The character's talent order.
            1. Normal attack
            2. Elemental skill
            3. Elemental burst
        rarity (int): The character's rarity (4~5).
        max_level (int): The character's max level.
        highest_dmg_bonus_stat (FightProp): The character's highest damage bonus stat.
        namecard (Optional[Namecard]): The character's namecard. Travelers don't have namecards.
        costume (Optional[Costume]): The character's costume, if any.
        costume_id (Optional[int]): The character's costume's ID, if any.
        constellations_unlocked (int): The number of constellations unlocked.
    """

    id: int = Field(alias="avatarId")
    artifacts: List[Artifact]
    weapon: Weapon
    stats: Dict[FightPropType, FightProp] = Field(alias="fightPropMap")
    constellations: List[Constellation] = Field([], alias="talentIdList")
    talents: List[Talent] = Field(alias="skillLevelMap")
    ascension: Literal[0, 1, 2, 3, 4, 5, 6]
    level: int
    skill_depot_id: int = Field(alias="skillDepotId")
    talent_extra_level_map: Optional[Dict[str, int]] = Field(None, alias="proudSkillExtraLevelMap")
    friendship_level: int = Field(alias="friendshipLevel")

    name: str = Field(None)
    icon: Icon = Field(None)
    element: Element = Field(None)
    talent_order: list[int] = Field(None)
    rarity: int = Field(None)
    namecard: Optional[Namecard] = Field(None)
    costume: Optional[Costume] = Field(None)
    costume_id: Optional[int] = Field(None, alias="costumeId")

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
            (stat for stat in self.stats.values() if stat.type.name in DMG_BONUS_FIGHT_PROPS),
            key=lambda stat: stat.value,
        )

    @computed_field
    @property
    def specialized_stat(self) -> FightProp:
        """The character's specialized stat

        Returns the highest stat value from the specialized stats (elemental damage bonus and healing bonus).
        """
        specialized_stats = list(DMG_BONUS_FIGHT_PROPS) + [FightPropType.FIGHT_PROP_HEAL_ADD.name]
        return max(
            (stat for stat in self.stats.values() if stat.type.name in specialized_stats),
            key=lambda stat: stat.value,
        )

    @computed_field
    @property
    def constellations_unlocked(self) -> int:
        """The number of constellations unlocked."""
        return len([c for c in self.constellations if c.unlocked])

    @field_validator("ascension", mode="before")
    def _intify_ascension(cls, v: str) -> int:
        return int(v)

    @field_validator("stats", mode="before")
    def _convert_stats(cls, v: Dict[str, float]) -> Dict[FightPropType, FightProp]:
        return {
            FightPropType(int(k)): FightProp(type=FightPropType(int(k)), value=v, name="")
            for k, v in v.items()
        }

    @field_validator("constellations", mode="before")
    def _convert_constellations(cls, v: List[int]) -> List[Constellation]:
        return [
            Constellation(id=constellation_id, name="", icon="", unlocked=True)
            for constellation_id in v
        ]

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
