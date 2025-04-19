# Caching

enka-py has 2 built-in caching systems:

- [`SQLiteCache`](./reference/cache.md#enka.clients.cache.SQLiteCache)
- [`MemoryCache`](./reference/cache.md#enka.clients.cache.MemoryCache)

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
