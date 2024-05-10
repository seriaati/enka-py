import math


def round_down(number: int | float, decimal_places: int) -> int | float:
    """Round down a number to a specified number of decimal places."""
    factor = 10**decimal_places
    return math.floor(number * factor) / factor
