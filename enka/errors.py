from typing import Any

__all__ = (
    "AlgoScrewedUpMassivelyError",
    "AssetDownloadError",
    "EnkaAPIError",
    "EnkaPyError",
    "GameMaintenanceError",
    "GatewayTimeoutError",
    "GeneralServerError",
    "InvalidItemTypeError",
    "PlayerDoesNotExistError",
    "ProfileUnavailableError",
    "RateLimitedError",
    "WrongUIDFormatError",
    "raise_for_retcode",
)


class EnkaAPIError(Exception):
    """Base exception class for Enka API.

    Attributes:
        code: The string error code returned by the API, if any.
        message: The error message returned by the API, if any.
    """

    def __init__(self, code: str | None = None, message: str | None = None) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return "An error occurred while requesting the API"


class WrongUIDFormatError(EnkaAPIError):
    """Raised when the UID format is incorrect."""

    def __str__(self) -> str:
        return "UID must be a string of 9 digits"


class PlayerDoesNotExistError(EnkaAPIError):
    """Raised when the player does not exist."""

    def __str__(self) -> str:
        return "Player does not exist"


class ProfileUnavailableError(PlayerDoesNotExistError):
    """Raised when the player exists, but the game doesn't return their profile."""

    def __str__(self) -> str:
        return "Player exists, but their profile is unavailable"


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
    """Raised when Enka or the game servers time out, the request can be retried."""

    def __str__(self) -> str:
        return "Gateway timeout"


class APIRequestTimeoutError(EnkaAPIError):
    """Raised when an API request times out."""

    def __str__(self) -> str:
        return "API request timed out"


def raise_for_retcode(retcode: int, code: str | None = None, message: str | None = None) -> None:
    """Raises an exception based on the retcode and the error code."""
    if code == "profile_unavailable":
        raise ProfileUnavailableError(code, message)

    match retcode:
        case 400:
            raise WrongUIDFormatError(code, message)
        case 404:
            raise PlayerDoesNotExistError(code, message)
        case 424:
            raise GameMaintenanceError(code, message)
        case 429:
            raise RateLimitedError(code, message)
        case 500:
            raise GeneralServerError(code, message)
        case 503:
            raise AlgoScrewedUpMassivelyError(code, message)
        case 504:
            raise GatewayTimeoutError(code, message)
        case _:
            raise EnkaAPIError(code, message)


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
