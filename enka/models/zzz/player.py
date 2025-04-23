from __future__ import annotations

from typing import Any

from deprecated import deprecated
from pydantic import BaseModel, Field, model_validator

__all__ = ("Medal", "Namecard", "Player", "Title")


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


class Title(BaseModel):
    """Represents a title obtained by a player in ZZZ.

    Attributes:
        id: The unique identifier for the title.
        name: The name of the title (e.g., "Cooked More Than a Hamburger").
        color1: The primary color associated with the title (e.g., "#e6e9ea").
        color2: The secondary color associated with the title (e.g., "#8ea3ae").
    """

    id: int = Field(alias="Title")

    # Fields that are not in the API response
    text: str = ""
    color1: str = ""
    color2: str = ""


class Namecard(BaseModel):
    """Represents a namecard obtained by a player in ZZZ.

    Attributes:
        id: The unique identifier for the name card.
        icon: The icon associated with the name card.
    """

    id: int

    # Fields that are not in the API response
    icon: str = ""


class Player(BaseModel):
    """Represents a ZZZ player's profile information.

    Attributes:
        medals: List of medals obtained by the player.
        nickname: The player's in-game nickname.
        avatar_id: The ID of the player's selected avatar.
        uid: The player's unique identifier.
        level: The player's current level.
        signature: The player's custom signature or description.
        title: The player's title.
        id: The player's profile ID.
        namecard_id: The ID of the player's namecard.
        namecard: The player's namecard.
    """

    medals: list[Medal] = Field(alias="MedalList")

    nickname: str = Field(alias="Nickname")
    avatar_id: int = Field(alias="AvatarId")
    uid: int = Field(alias="Uid")
    level: int = Field(alias="Level")
    signature: str = Field(alias="Desc")

    title: Title = Field(alias="TitleInfo")
    id: int = Field(alias="ProfileId")
    namecard_id: int = Field(alias="CallingCardId")

    # Fields that are not in the API response
    namecard: Namecard = Field(default=None)  # pyright: ignore[reportAssignmentType]

    @model_validator(mode="before")
    @classmethod
    def __unnest_info(cls, value: dict[str, Any]) -> dict[str, Any]:
        info = value.pop("ProfileDetail", {})
        value.update(info)
        return value

    @property
    @deprecated(reason="Use `title.id` instead.")
    def title_id(self) -> int:
        """(Deprecated) The ID of the player's selected title."""
        return self.title.id
