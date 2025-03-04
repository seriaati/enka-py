from __future__ import annotations

from typing import Any

__all__ = (
    "AlgoScrewedUpMassivelyError",
    "AssetDownloadError",
    "EnkaAPIError",
    "EnkaPyError",
    "GameMaintenanceError",
    "GeneralServerError",
    "InvalidItemTypeError",
    "PlayerDoesNotExistError",
    "RateLimitedError",
    "WrongUIDFormatError",
    "raise_for_retcode",
)


class EnkaAPIError(Exception):
    """Base exception class for Enka API."""

    def __str__(self) -> str:
        return "Unknown error"


class WrongUIDFormatError(EnkaAPIError):
    """Raised when the UID format is incorrect."""

    def __str__(self) -> str:
        return "UID must be a string of 9 digits"


class PlayerDoesNotExistError(EnkaAPIError):
    """Raised when the player does not exist."""

    def __str__(self) -> str:
        return "Player does not exist"


class GameMaintenanceError(EnkaAPIError):
    """Raised when the game is under maintenance."""

    def __str__(self) -> str:
        return "Game is under maintenance"


class RateLimitedError(EnkaAPIError):
    """Raised when the API rate limit is exceeded."""

    def __str__(self) -> str:
        return "Rate limited"


class GeneralServerError(EnkaAPIError):
    """Raised when a general server error occurs."""

    def __str__(self) -> str:
        return "General server error"


class AlgoScrewedUpMassivelyError(EnkaAPIError):
    """Raised when something goes wrong on the server side."""

    def __str__(self) -> str:
        return "Algo screwed up massively"


class GatewayTimeoutError(EnkaAPIError):
    """Raised when a gateway timeout occurs."""

    def __str__(self) -> str:
        return "Gateway timeout"


def raise_for_retcode(retcode: int) -> None:
    """Raises an exception based on the retcode."""
    match retcode:
        case 400:
            raise WrongUIDFormatError
        case 404:
            raise PlayerDoesNotExistError
        case 424:
            raise GameMaintenanceError
        case 429:
            raise RateLimitedError
        case 500:
            raise GeneralServerError
        case 503:
            raise AlgoScrewedUpMassivelyError
        case 504:
            raise GatewayTimeoutError
        case _:
            raise EnkaAPIError


class EnkaPyError(Exception):
    """Base exception class for enka.py."""

    def __str__(self) -> str:
        return "enka.py error"


class InvalidItemTypeError(EnkaPyError):
    """Raised when the item type is invalid."""

    def __str__(self) -> str:
        return "Invalid item type"


class AssetDownloadError(EnkaPyError):
    """Raised when an asset fail to download."""

    def __init__(self, status: int, url: str) -> None:
        self.status = status
        self.url = url

    def __str__(self) -> str:
        return f"Failed to update assets, status code: {self.status}, url: {self.url}"


class AssetKeyError(EnkaPyError, KeyError):
    """Raised when the asset key is not found."""

    def __init__(self, key: str, cls: Any) -> None:
        self.key = key
        self.cls = cls

    def __str__(self) -> str:
        return (
            f"Cannot find {self.key!r} in {self.cls.__name__}, consider calling `update_assets()`"
        )
