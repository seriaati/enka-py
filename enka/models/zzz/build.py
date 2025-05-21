from __future__ import annotations

from pydantic import BaseModel, Field

from .character import Agent


class Build(BaseModel):
    """Represents a ZZZ build.

    Attributes:
        id: The build's ID.
        name: The build's name.
        order: The build's order.
        live: Whether the build is live.
        character_id: The build's character ID.
        character: The build's character data.
    """

    id: int
    name: str
    order: int
    live: bool
    character_id: int = Field(alias="avatar_id")
    character: Agent = Field(alias="avatar_data")
