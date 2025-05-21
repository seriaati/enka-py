from __future__ import annotations

import math

from enka.constants.common import CN_UID_PREFIXES


def round_down(number: int | float, decimal_places: int) -> int | float:
    """Round down a number to a specified number of decimal places.

    Args:
        number: The number to round down.
        decimal_places: The number of decimal places to round down to.

    Returns:
        int | float: The rounded down number.
    """
    factor = 10**decimal_places
    return math.floor(number * factor) / factor


def is_hsr_cn_uid(uid: str) -> bool:
    """Check if the given HSR UID belongs to a Chinese server.

    Args:
        uid: The UID to check.

    Returns:
        bool: True if the UID is a CN UID, False otherwise.
    """
    # The length check is to avoid cases where the UID length
    # got extended like in Genshin (18... is Asia server)
    return uid.startswith(CN_UID_PREFIXES) and len(uid) == 9
