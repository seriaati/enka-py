from __future__ import annotations

from loguru import logger as _logger

from . import errors, gi, hsr, utils, zzz
from .clients import GenshinClient, HSRClient, ZZZClient, cache
from .enums.enum import Game
from .models.enka import *

_logger.disable("enka")  # noqa: RUF067
