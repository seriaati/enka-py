from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from aiohttp_client_cache.backends.sqlite import SQLiteBackend
from aiohttp_client_cache.session import CachedSession

from ..errors import raise_for_retcode

if TYPE_CHECKING:
    from ..enums.enum import Game

LOGGER_ = logging.getLogger(__name__)


class BaseClient:
    """Base client with requesting capabilities."""

    def __init__(
        self,
        game: Game,
        *,
        headers: dict[str, Any] | None = None,
        cache_ttl: int = 60,
    ) -> None:
        self.game = game

        self._headers = headers or {"User-Agent": "enka-py"}
        self._session: CachedSession | None = None
        self._cache = SQLiteBackend(
            cache_name=f".enka_py/cache/{game.value}", expire_after=cache_ttl
        )

    async def __aenter__(self) -> BaseClient:
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def start(self) -> None:
        """Start the client."""
        self._session = CachedSession(headers=self._headers, cache=self._cache)

    async def close(self) -> None:
        """Close the client."""
        if self._session is None:
            msg = f"Client is not started, call `{self.__class__.__name__}.start` first"
            raise RuntimeError(msg)

        await self._session.close()

    async def _request(self, url: str) -> dict[str, Any]:
        if self._session is None:
            msg = f"Client is not started, call `{self.__class__.__name__}.start` first"
            raise RuntimeError(msg)

        LOGGER_.debug("Requesting %s", url)

        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise_for_retcode(resp.status)

            data: dict[str, Any] = await resp.json()
            return data
