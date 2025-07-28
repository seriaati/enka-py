# Caching

enka-py has 3 built-in caching systems:

- [`MemoryCache`](./reference/cache.md#enka.clients.cache.MemoryCache)
- [`SQLiteCache`](./reference/cache.md#enka.clients.cache.SQLiteCache)
- [`RedisCache`](./reference/cache.md#enka.clients.cache.RedisCache)

## Installation

For the different caching systems, you need to install the appropriate optional dependencies.

```bash
pip install enka[redis]
```

```bash
pip install enka[sqlite]
```

## How-To

```py
import enka

cache = enka.cache.SQLiteCache()

async with enka.GenshinClient(cache=cache) as client:
    await client.fetch_showcase(901211014)  # Cached
    await client.fetch_showcase(901211014)  # From cache
```

## Making Your Own Cache System

You can create your own cache system by subclassing [`enka.BaseCache`](./reference/cache.md#enka.clients.cache.BaseCache) and implementing all the abstract methods.
