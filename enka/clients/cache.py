from __future__ import annotations

import abc
import os
import pathlib
import time

import aiosqlite

__all__ = ("BaseTTLCache", "MemoryCache", "SQLiteCache")


class BaseTTLCache(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abc.abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> None: ...

    @abc.abstractmethod
    async def delete(self, key: str) -> None: ...

    @abc.abstractmethod
    async def clear_expired(self) -> None: ...


class MemoryCache(BaseTTLCache):
    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, str]] = {}

    async def get(self, key: str) -> str | None:
        cached = self._cache.get(key)
        if cached is None:
            return None
        return cached[1]

    async def set(self, key: str, value: str, ttl: int) -> None:
        self._cache[key] = (time.time() + ttl, value)

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    async def clear_expired(self) -> None:
        now = time.time()

        for key, (expires_at, _) in list(self._cache.items()):
            if now >= expires_at:
                await self.delete(key)


class SQLiteCache(BaseTTLCache):
    def __init__(self, db_path: pathlib.Path | str = ".cache/enka_py.db") -> None:
        self.db_path = pathlib.Path(db_path)

    async def start(self) -> None:
        os.makedirs(self.db_path.parent, exist_ok=True)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, expires_at REAL)"
            )
            await db.commit()

    async def get(self, key: str) -> str | None:
        async with (
            aiosqlite.connect(self.db_path) as db,
            db.execute("SELECT value FROM cache WHERE key = ?", (key,)) as cursor,
        ):
            row = await cursor.fetchone()
            if row is None:
                return None
            return row[0]

    async def set(self, key: str, value: str, ttl: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (key, value, time.time() + ttl),
            )
            await db.commit()

    async def delete(self, key: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cache WHERE key = ?", (key,))
            await db.commit()

    async def clear_expired(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
            await db.commit()
