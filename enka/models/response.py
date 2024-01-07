from typing import Any, Dict, List

from pydantic import BaseModel, Field, model_validator

from .character import Character
from .player import Player


class ShowcaseResponse(BaseModel):
    characters: List[Character] = Field(alias="avatarInfoList")
    player: Player = Field(alias="playerInfo")
    ttl: int
    uid: str

    @model_validator(mode="before")
    def _handle_no_showcase(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if "avatarInfoList" not in v:
            v["avatarInfoList"] = []
        return v
