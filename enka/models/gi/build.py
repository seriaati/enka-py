from __future__ import annotations

from ..enka.build import BaseBuild
from .character import Character


class Build(BaseBuild[Character]):
    """Represents a Genshin Impact build.

    Attributes:
        id: The build's ID.
        name: The build's name.
        order: The build's order.
        live: Whether the build is live.
        character_id: The build's character ID.
        character: The build's character data.
    """
