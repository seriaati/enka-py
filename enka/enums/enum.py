from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


__all__ = ("Game",)


class Game(StrEnum):
    """Game."""

    GI = "gi"
    HSR = "hsr"
    ZZZ = "zzz"
