from __future__ import annotations

import abc
import pathlib
import time

import aiosqlite

__all__ = ("BaseTTLCache", "MemoryCache", "SQLiteCache")


class BaseTTLCache(abc.ABC):
    """Base class for TTL cache, inherit from this class to implement your own cache."""

    @abc.abstractmethod
    async def start(self) -> None:
        """Start the cache, called when `BaseClient` is started."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the cache, called when `BaseClient` is closed."""

    @abc.abstractmethod
    async def get(self, key: str) -> str | None:
        """Get a value from the cache.

        Returns:
            The value if it exists, otherwise None.
        """

    @abc.abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> None:
        """Set the value in the cache.

        Args:
            key: The key to set.
            value: The value to set.
            ttl: The time to live in seconds.
        """

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        """Delete the value from the cache.

        Args:
            key: The key to delete.
        """

    @abc.abstractmethod
    async def clear_expired(self) -> None:
        """Clear expired values from the cache."""


class MemoryCache(BaseTTLCache):
    """In-memory cache implementation.

    This cache is not persistent and will be cleared when the program exits.
    """

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, str]] = {}

    async def start(self) -> None: ...

    async def close(self) -> None: ...

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
    """SQLite cache implementation.

    This cache is persistent and will be saved to the specified file.
    """

    def __init__(self, db_path: pathlib.Path | str = ".cache/enka_py.db") -> None:
        self._db_path = pathlib.Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            msg = f"Cache is not started, call `{self.__class__.__name__}.start` first"
            raise RuntimeError(msg)
        return self._conn

    async def start(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self._db_path)
        await self.conn.execute(
            "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, expires_at REAL)"
        )
        await self.conn.commit()

    async def close(self) -> None:
        if self._conn is None:
            return
        await self._conn.close()

    async def get(self, key: str) -> str | None:
        async with self.conn.execute("SELECT value FROM cache WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return row[0]

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self.conn.execute(
            "INSERT INTO cache (key, value, expires_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = ?, expires_at = ?",
            (key, value, time.time() + ttl, value, time.time() + ttl),
        )
        await self.conn.commit()

    async def delete(self, key: str) -> None:
        await self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        await self.conn.commit()

    async def clear_expired(self) -> None:
        await self.conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
        await self.conn.commit()
