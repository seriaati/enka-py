from typing import Any, Dict, List

from pydantic import BaseModel, Field, model_validator

from .character import Character
from .player import Player

__all__ = ("ShowcaseResponse",)


class ShowcaseResponse(BaseModel):
    """
    Represents a Genshin Impact showcase response.

    Attributes
    ----------
    characters: List[:class:`Character`]
        The characters in the showcase.
    player: :class:`Player`
        The player of the showcase.
    ttl: :class:`int`
        The time to live of the response.
    uid: :class:`str`
        The UID of the showcase.
    """

    characters: List[Character] = Field(alias="avatarInfoList")
    player: Player = Field(alias="playerInfo")
    ttl: int
    uid: str

    @model_validator(mode="before")
    def _handle_no_showcase(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if "avatarInfoList" not in v or v["avatarInfoList"] is None:
            v["avatarInfoList"] = []
        return v
