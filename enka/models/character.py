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
    type: StatType = Field(alias="mainPropId")
    value: float = Field(alias="statValue")
    name: str = Field(None)


class SubStat(BaseModel):
    type: StatType = Field(alias="appendPropId")
    value: float = Field(alias="statValue")
    name: str = Field(None)


class Artifact(BaseModel):
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
    type: StatType = Field(alias="appendPropId")
    value: float = Field(alias="statValue")
    name: str = Field(None)


class Weapon(BaseModel):
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
    id: str
    side_icon: str

    @property
    def icon(self) -> str:
        return self.side_icon.replace("Side_", "")

    @property
    def art(self) -> str:
        return self.side_icon.replace("AvatarIcon_Side", "Costume")


class Character(BaseModel):
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
