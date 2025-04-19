from __future__ import annotations

from typing import Any

from pydantic import BaseModel, computed_field

from .icon import Icon

__all__ = ("Costume",)


class Costume(BaseModel):
    """Represents a character's costume.

    Attributes:
       id: The costume's ID.
       icon: The costume's icon.
    """

    id: int
    data: dict[str, Any]

    @computed_field
    @property
    def icon(self) -> Icon:
        """The costume's icon."""
        return Icon(side_icon_ui_path=self.data["sideIconName"], is_costume=True)
