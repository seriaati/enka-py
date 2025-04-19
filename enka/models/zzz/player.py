from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

__all__ = ("Medal", "Player")


class Medal(BaseModel):
    """Represents a medal obtained by a player in ZZZ.

    Attributes:
        value: The value associated with the medal.
        type: The type identifier of the medal.
        icon_id: The identifier for the medal's icon.
    """

    value: int = Field(alias="Value")
    type: int = Field(alias="MedalType")
    icon_id: int = Field(alias="MedalIcon")


class Player(BaseModel):
    """Represents a ZZZ player's profile information.

    Attributes:
        medals: List of medals obtained by the player.
        nickname: The player's in-game nickname.
        avatar_id: The ID of the player's selected avatar.
        uid: The player's unique identifier.
        level: The player's current level.
        signature: The player's custom signature or description.
        title_id: The ID of the player's selected title.
        id: The player's profile ID.
        namecard_id: The ID of the player's selected namecard.
    """

    medals: list[Medal] = Field(alias="MedalList")

    nickname: str = Field(alias="Nickname")
    avatar_id: int = Field(alias="AvatarId")
    uid: int = Field(alias="Uid")
    level: int = Field(alias="Level")
    signature: str = Field(alias="Desc")

    title_id: int = Field(alias="Title")
    id: int = Field(alias="ProfileId")
    namecard_id: int = Field(alias="CallingCardId")

    @model_validator(mode="before")
    @classmethod
    def __unnest_info(cls, value: dict[str, Any]) -> dict[str, Any]:
        info = value.pop("ProfileDetail")
        value.update(info)
        return value
