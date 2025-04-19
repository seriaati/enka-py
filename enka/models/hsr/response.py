from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from ..enka.owner import Owner
from .character import Character
from .player import Player

__all__ = ("ShowcaseResponse",)


class ShowcaseResponse(BaseModel):
    """
    Represents a HSR showcase response.

    Attributes:
        characters: The characters in the showcase.
        player: The player.
        ttl: The time to live of the response.
        uid: The UID of the showcase.
        owner: The owner of the showcase's account, if any.
    """

    characters: list[Character] = Field(alias="avatarDetailList")
    player: Player = Field(alias="detailInfo")
    ttl: int = 0
    uid: str
    owner: Owner | None = None

    @model_validator(mode="before")
    @classmethod
    def _flatten_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["avatarDetailList"] = values["detailInfo"].pop("avatarDetailList", [])
        return values
