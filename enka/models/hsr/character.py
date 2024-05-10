from typing import Any
from pydantic import BaseModel, Field, field_validator

from ...enums.hsr import PropType, RelicType


class Trace(BaseModel):
    id: int = Field(alias="pointId")
    level: int


class Prop(BaseModel):
    type: PropType
    value: float


class LightCone(BaseModel):
    id: int = Field(alias="tid")
    level: int
    ascension: int = Field(alias="promotion")
    superimpose: int = Field(alias="rank")
    name: str  # Returned as text map hash in the API response
    props: list[Prop] = Field(alias="_flat")

    @field_validator("name", mode="before")
    def _stringify_name(cls, value: int) -> str:
        return str(value)

    @field_validator("props", mode="before")
    def _flatten_props(cls, value: dict[str, Any]) -> dict[str, Any]:
        return value.pop("props")


class RelicSubAffix(BaseModel):
    id: int = Field(alias="affixId")
    cnt: int
    step: int


class Relic(BaseModel):
    id: int = Field(alias="tid")
    level: int
    type: RelicType
    main_affix_id: int = Field(alias="mainAffixId")
    set_name: str = Field(alias="setName")  # Returned as text map hash in the API response
    set_id: int = Field(alias="setId")
    props: list[Prop] = Field(alias="_flat")
    sub_affix_list: list[RelicSubAffix] = Field(alias="subAffixList")

    @field_validator("set_name", mode="before")
    def _stringify_set_name(cls, value: int) -> str:
        return str(value)

    @field_validator("props", mode="before")
    def _flatten_props(cls, value: dict[str, Any]) -> dict[str, Any]:
        return value.pop("props")


class Character(BaseModel):
    level: int
    position: int = Field(alias="pos")
    ascension: int = Field(alias="promotion")
    id: int = Field(alias="avatarId")
    traces: list[Trace] = Field(alias="skillTreeList")
    light_cone: LightCone = Field(alias="equipment")
    relics: list[Relic] = Field(alias="relicList")
