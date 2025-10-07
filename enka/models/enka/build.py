from __future__ import annotations

from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

C = TypeVar("C")


class BaseBuild(BaseModel, Generic[C]):
    """Represents a character build.

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
    order: Decimal
    live: bool
    character_id: int = Field(alias="avatar_id")
    character: C = Field(alias="avatar_data")
