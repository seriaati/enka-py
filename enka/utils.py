from __future__ import annotations

import math


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
