from typing import Any, List

from pydantic import BaseModel, Field, model_validator

from .character import Character
from .player import Player

__all__ = ("ShowcaseResponse",)


class ShowcaseResponse(BaseModel):
    """
    Represents a Honkai: Star Rail showcase response.

    Attributes:
        characters (List[Character]): The characters in the showcase.
        player (Player): The player.
        ttl (int): The time to live of the response.
        uid (str): The UID of the showcase.
    """

    characters: List[Character] = Field(alias="avatarDetailList")
    player: Player = Field(alias="detailInfo")
    ttl: int = 0
    uid: str

    @model_validator(mode="before")
    def _flatten_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        values["avatarDetailList"] = values["detailInfo"].pop("avatarDetailList")
        return values
