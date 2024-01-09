from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from ..exceptions import InvalidItemTypeError
from ..enums import EquipmentType, ItemType, StatType

__all__ = (
    "Artifact",
    "Character",
    "CharacterCostume",
    "MainStat",
    "SubStat",
    "Weapon",
    "WeaponStat",
)


class MainStat(BaseModel):
    """
    Represents the main stat of an artifact.

    Attributes
    ----------
    type: :class:`StatType`
        The stat's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK, etc.)
    value: :class:`float`
        The stat's value.
    name: :class:`str`
        The stat's name.
    """

    type: StatType = Field(alias="mainPropId")
    value: float = Field(alias="statValue")
    name: str = Field(None)


class SubStat(BaseModel):
    """
    Represents the sub stat of an artifact.

    Attributes
    ----------
    type: :class:`StatType`
        The stat's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK, etc.)
    value: :class:`float`
        The stat's value.
    name: :class:`str`
        The stat's name.
    """

    type: StatType = Field(alias="appendPropId")
    value: float = Field(alias="statValue")
    name: str = Field(None)


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
    main_stat: MainStat = Field(alias="reliquaryMainstat")
    sub_stats: List[SubStat] = Field(alias="reliquarySubstats")
    set_name: str = Field(alias="setNameTextMapHash")

    @field_validator("level", mode="before")
    def _convert_level(cls, v: int) -> int:
        return v - 1

    @field_validator("icon", mode="before")
    def _convert_icon(cls, v: str) -> str:
        return f"https://enka.network/ui/{v}.png"


class WeaponStat(BaseModel):
    """
    Represents a weapon stat.

    Attributes
    ----------
    type: :class:`StatType`
        The stat's type (e.g. FIGHT_PROP_HP, FIGHT_PROP_ATTACK, etc.)
    value: :class:`float`
        The stat's value.
    name: :class:`str`
        The stat's name.
    """

    type: StatType = Field(alias="appendPropId")
    value: float = Field(alias="statValue")
    name: str = Field(None)


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
    stats: List[WeaponStat] = Field(alias="weaponStats")

    @field_validator("refinement", mode="before")
    def _extract_refinement(cls, v: Dict[str, int]) -> int:
        return list(v.values())[0] + 1

    @field_validator("icon", mode="before")
    def _convert_icon(cls, v: str) -> str:
        return f"https://enka.network/ui/{v}.png"


class CharacterCostume(BaseModel):
    """
    Represents a character costume.

    Attributes
    ----------
    id: :class:`str`
        The costume's ID.
    side_icon: :class:`str`
        The costume's side icon.
        Example: https://enka.network/ui/UI_AvatarIcon_Side_AmborCostumeWic.png
    icon: :class:`str`
        The costume's icon.
        Example: https://enka.network/ui/UI_AvatarIcon_AmborCostumeWic.png
    art: :class:`str`
        The costume's art.
        Example: https://enka.network/ui/UI_Costume_AmborCostumeWic.png
    """

    id: str
    side_icon: str

    @property
    def icon(self) -> str:
        return self.side_icon.replace("Side_", "")

    @property
    def art(self) -> str:
        return self.side_icon.replace("AvatarIcon_Side", "Costume")


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
    stat_map: Dict[:class:`str`, :class:`float`]
        The character's stat map.
    constellations: :class:`int`
        The character's constellation level.
    skills: Dict[:class:`str`, :class:`int`]
        The character's skill levels.
    ascension: :class:`int`
        The character's ascension level.
    level: :class:`int`
        The character's level.
    skill_depot_id: :class:`int`
        The character's skill depot ID.
    name: :class:`str`
        The character's name.
    side_icon: :class:`str`
        The character's side icon.
        Example: https://enka.network/ui/UI_AvatarIcon_Side_Ambor.png
    icon: :class:`str`
        The character's icon.
        Example: https://enka.network/ui/UI_AvatarIcon_Ambor.png
    art: :class:`str`
        The character's art.
        Example: https://enka.network/ui/UI_Gacha_AvatarImg_Ambor.png
    costumes: List[:class:`CharacterCostume`]
        The character's costumes.
    """

    id: int = Field(alias="avatarId")
    artifacts: List[Artifact]
    weapon: Weapon
    stat_map: Dict[str, float] = Field(alias="fightPropMap")
    constellations: int = Field(0, alias="talentIdList")
    skills: Dict[str, int] = Field(alias="skillLevelMap")
    ascension: int
    level: int
    skill_depot_id: int = Field(alias="skillDepotId")
    name: str = Field(None)
    side_icon: str = Field(None)
    costumes: List[CharacterCostume] = Field(list)

    @property
    def icon(self) -> str:
        return self.side_icon.replace("Side_", "")

    @property
    def art(self) -> str:
        return self.side_icon.replace("AvatarIcon_Side", "Gacha_AvatarImg")

    @field_validator("constellations", mode="before")
    def _convert_constellations(cls, v: Optional[List[int]]) -> int:
        if v is None:
            return 0
        return len(v)

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

        return v
