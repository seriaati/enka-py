__all__ = (
    "EnkaAPIError",
    "WrongUIDFormatError",
    "PlayerDoesNotExistError",
    "GameMaintenanceError",
    "RateLimitedError",
    "GeneralServerError",
    "AlgoScrewedUpMassivelyError",
    "raise_for_retcode",
    "EnkaPyError",
    "InvalidItemTypeError",
)


class EnkaAPIError(Exception):
    def __str__(self) -> str:
        return "Unknown error"


class WrongUIDFormatError(EnkaAPIError):
    def __str__(self) -> str:
        return "UID must be a string of 9 digits"


class PlayerDoesNotExistError(EnkaAPIError):
    def __str__(self) -> str:
        return "Player does not exist"


class GameMaintenanceError(EnkaAPIError):
    def __str__(self) -> str:
        return "Game is under maintenance"


class RateLimitedError(EnkaAPIError):
    def __str__(self) -> str:
        return "Rate limited"


class GeneralServerError(EnkaAPIError):
    def __str__(self) -> str:
        return "General server error"


class AlgoScrewedUpMassivelyError(EnkaAPIError):
    def __str__(self) -> str:
        return "Algo screwed up massively"


def raise_for_retcode(retcode: int) -> None:
    """
    Raises an exception based on the retcode
    """
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
        case _:
            raise EnkaAPIError


class EnkaPyError(Exception):
    def __str__(self) -> str:
        return "enka.py error"


class InvalidItemTypeError(EnkaPyError):
    def __str__(self) -> str:
        return "Invalid item type"
