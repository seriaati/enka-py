from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from .character import Agent
from .player import Player

__all__ = ("ShowcaseResponse",)


class ShowcaseResponse(BaseModel):
    """Represents a ZZZ player's showcase information.

    Attributes:
        agents: List of agents (characters) in the player's showcase.
        player: The player's profile information.
        uid: The player's unique identifier.
        ttl: The time-to-live for the showcase data.
    """

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

    @property
    def url(self) -> str:
        """The URL of the showcase."""
        return f"https://enka.network/zzz/{self.uid}"
