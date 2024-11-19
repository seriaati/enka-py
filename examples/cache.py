from __future__ import annotations

import asyncio

import enka


async def main() -> None:
    cache = enka.cache.SQLiteCache()
    async with enka.GenshinClient(cache=cache) as client:
        await client.fetch_showcase(901211014)  # Cached
        await client.fetch_showcase(901211014)  # From cache

    cache = enka.cache.MemoryCache()
    async with enka.GenshinClient(cache=cache) as client:
        await client.fetch_showcase(901211014)  # Cached
        await client.fetch_showcase(901211014)  # From cache


if __name__ == "__main__":
    asyncio.run(main())
