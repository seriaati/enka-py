# Getting Started

Interact with the Enka Network API using the API client classes:

- Genshin Impact: [`enka.GenshinClient`](./reference/gi/client.md)
- Honkai Star Rail: [`enka.HSRClient`](./reference/hsr/client.md)
- Zenless Zone Zero: [`enka.ZZZClient`](./reference/zzz/client.md)

## Fetching Showcase Data

For simplicity, examples will only use `GenshinClient`, but the same applies to the other clients.

```py
import enka

async with enka.GenshinClient() as client:
    await client.fetch_showcase(901211014)
```

You can also call the `start` and `close` methods manually.

```py
import enka

client = enka.GenshinClient()

await client.start()
await client.fetch_showcase(901211014)
await client.close()
```

!!! warning "Important"
    When using the client, you **must** use either the `async with` syntax or call `start` and `close` manually; otherwise, the client won't work and `RuntimeError` will be raised.

## Fetching Character Builds

*Available after v2.1.0*  
  
Please read the [Enka Network API docs](https://api.enka.network/#/api?id=profile-endpoints) for more information about what character builds are.  

```py
import enka

async with enka.GenshinClient() as client:
    showcase = await client.fetch_showcase(618285856)
    builds = await client.fetch_builds(showcase.owner)
    
    for character_id, build in builds.items():
        print(character_id)
        print(build.name, build.character.name)
```

## Fetching and Parsing raw Data

*Available after v2.1.1*  
  
You can let the API wrapper return the raw data from the API, and later on parse it.

```py
import enka

async with enka.GenshinClient() as client:
    raw = await client.fetch_showcase(901211014, raw=True)
    parsed = client.parse_showcase(raw)
```

## Catching Exceptions

Exception classes are available in the [`enka.errors`](./reference/errors.md) module.

```py
import enka

async with enka.GenshinClient() as client:
    try:
        await client.fetch_showcase(901211014)
    except enka.errors.GameMaintenanceError:
        print("Game is in maintenance.")
```

## Logging

`enka` uses [Loguru](https://loguru.readthedocs.io/) for internal logging, and the logger is disabled by default.

Enable it explicitly:

```py
from loguru import logger

logger.enable("enka")
```

You can then configure your preferred log level by adding a sink.

```py
import sys
from loguru import logger

logger.enable("enka")

# Optional: replace Loguru's default sink with your own configuration
logger.remove()
logger.add(sys.stderr, level="INFO")
```

Use `"DEBUG"` for verbose output when troubleshooting, or `"INFO"` / `"WARNING"` for quieter logs.

## Gendered Text (ZZZ)

Some languages (e.g. German) encode grammatical gender directly inside localized strings using the placeholder syntax `{M#...}` and `{F#...}`. For example, a title might be stored as:

```text
Wahre{M#r} Schüler{F#in} des Yunkuigipfels
```

`ZZZClient` resolves these automatically based on the `gender` option, which defaults to `enka.zzz.Gender.MALE`.

```py
import enka

# Default – male variant is kept, female tokens are removed:
# "Wahrer Schüler des Yunkuigipfels"
async with enka.ZZZClient() as client:
    showcase = await client.fetch_showcase(1300025292)
    print(showcase.player.title.text)

# Explicitly female:
# "Wahre Schülerin des Yunkuigipfels"
async with enka.ZZZClient(gender=enka.zzz.Gender.FEMALE) as client:
    showcase = await client.fetch_showcase(1300025292)
    print(showcase.player.title.text)
```

You can also change the gender at runtime via the `gender` property:

```py
client.gender = enka.zzz.Gender.FEMALE
```

Both `enka.zzz.Gender` enum values and plain strings (`"M"` / `"F"`) are accepted.

## Examples

You can find more detailed examples in the [examples](https://github.com/seriaati/enka-py/tree/main/examples) folder.
