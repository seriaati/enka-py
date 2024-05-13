import sys
from enum import StrEnum

if sys.version_info < (3, 11):
    from enum import Enum as StrEnum


class Game(StrEnum):
    """Game."""

    GI = "gi"
    HSR = "hsr"
