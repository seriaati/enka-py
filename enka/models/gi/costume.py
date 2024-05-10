from typing import Any

from .icon import Icon


class Costume:
    """
    Represents a character's costume.

    Attributes
    ----------
    id: :class:`int`
        The costume's ID.
    icon: :class:`Icon`
        The costume's icon.
    """

    def __init__(self, id: int, data: dict[str, Any]) -> None:
        self.id = id
        self._data = data

    def __str__(self) -> str:
        return self._data["sideIconName"]

    def __repr__(self) -> str:
        return f"<Costume {self._data['sideIconName']}>"

    @property
    def icon(self) -> Icon:
        """The costume's icon."""
        return Icon(self._data["sideIconName"], is_costume=True)
