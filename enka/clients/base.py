from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
import orjson
from loguru import logger

from ..constants.common import PROFILE_API_URL
from ..errors import APIRequestTimeoutError, EnkaAPIError, raise_for_retcode
from ..models.enka.owner import Owner, OwnerInput

if TYPE_CHECKING:
    from .cache import BaseTTLCache


class BaseClient:
    """Base client with requesting capabilities."""

    def __init__(
        self, *, headers: dict[str, Any] | None, cache: BaseTTLCache | None, timeout: int
    ) -> None:
        self._headers = headers or {"User-Agent": "enka-py"}
        self._session: aiohttp.ClientSession | None = None
        self._cache = cache
        self._timeout = timeout

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            msg = f"ClientSession not found, call `{self.__class__.__name__}.start` first"
            raise RuntimeError(msg)
        return self._session

    async def __aenter__(self) -> BaseClient:
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def start(self) -> None:
        timeout = aiohttp.ClientTimeout(total=self._timeout)

        self._session = aiohttp.ClientSession(headers=self._headers, timeout=timeout)
        if self._cache is not None:
            await self._cache.start()

    async def close(self) -> None:
        await self.session.close()
        if self._cache is not None:
            await self._cache.close()

    async def _request(self, url: str) -> dict[str, Any]:
        if self._cache is not None:
            await self._cache.clear_expired()
            cached = await self._cache.get(url)
            if cached is not None:
                return orjson.loads(cached.encode())

        logger.debug(f"Requesting {url}")

        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    raise_for_retcode(resp.status)

                data: dict[str, Any] = await resp.json()
                if self._cache is not None:
                    await self._cache.set(url, orjson.dumps(data).decode(), ttl=60)
                return data
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError):
                raise APIRequestTimeoutError from e
            if isinstance(e, EnkaAPIError):
                raise
            raise EnkaAPIError from e

    async def _request_profile(self, owner: Owner | OwnerInput) -> dict[str, Any]:
        if isinstance(owner, Owner):
            owner_hash, username = owner.hash, owner.username
        else:
            owner_hash, username = owner["hash"], owner["username"]

        url = PROFILE_API_URL.format(username, owner_hash)
        return await self._request(url)
