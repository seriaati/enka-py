from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..enka.owner import Owner
from .character import Character
from .player import Player

__all__ = ("ShowcaseResponse",)


class ShowcaseResponse(BaseModel):
    """Represents a Genshin Impact showcase response.

    Attributes:
        characters: The characters in the showcase.
        player: The player of the showcase.
        ttl: The time to live of the response.
        uid: The UID of the showcase.
        owner: The owner of the showcase's account.
    """

    characters: list[Character] = Field(alias="avatarInfoList", default_factory=list)
    player: Player = Field(alias="playerInfo")
    ttl: int
    uid: str
    owner: Owner | None = None

    @field_validator("characters", mode="before")
    @classmethod
    def __handle_none_value(cls, v: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        if v is None:
            return []
        return v
