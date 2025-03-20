from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from .character import Agent
from .player import Player

__all__ = ("ShowcaseResponse",)


class ShowcaseResponse(BaseModel):
    """ZZZ showcase response."""

    agents: list[Agent] = Field(alias="ShowcaseDetail")
    player: Player = Field(alias="SocialDetail")

    uid: int
    ttl: int

    @field_validator("agents", mode="before")
    @classmethod
    def __get_agents(cls, value: dict[str, Any]) -> list[dict[str, Any]]:
        return value["AvatarList"]

    @model_validator(mode="before")
    @classmethod
    def __unnest_info(cls, value: dict[str, Any]) -> dict[str, Any]:
        info = value.pop("PlayerInfo")
        value.update(info)
        return value
