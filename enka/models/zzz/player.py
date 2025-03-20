from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

__all__ = ("Medal", "Player")


class Medal(BaseModel):
    """ZZZ medal."""

    value: int = Field(alias="Value")
    type: int = Field(alias="MedalType")
    icon_id: int = Field(alias="MedalIcon")


class Player(BaseModel):
    """ZZZ player."""

    medals: list[Medal] = Field(alias="MedalList")

    nickname: str = Field(alias="Nickname")
    avatar_id: int = Field(alias="AvatarId")
    uid: int = Field(alias="Uid")
    level: int = Field(alias="Level")
    signature: str = Field(alias="Desc")

    title_id: int = Field(alias="TitleId")
    id: int = Field(alias="ProfileId")
    namecard_id: int = Field(alias="CallingCardId")

    @model_validator(mode="before")
    @classmethod
    def __unnest_info(cls, value: dict[str, Any]) -> dict[str, Any]:
        info = value.pop("ProfileDetail")
        value.update(info)
        return value
