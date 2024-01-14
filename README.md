# enka.py

## Table of Contents
1. [Introduction](#introduction)
   - [Features](#features)
   - [Installation](#installation)
   - [Quick Example](#quick-example)

2. [Usage](#usage)
   - [Starting and closing the client properly](#starting-and-closing-the-client-properly)
   - [Updating assets](#updating-assets)
   - [Client parameters](#client-parameters)
   - [Finding models' attributes](#finding-models-attributes)

3. [Questions, issues, contributions](#questions-issues-contributions)

## Quick links
- [Enka.network API docs](http://api.enka.network/)

# Introduction
enka.py is an async API wrapper for [enka.network](https://enka.network/) written in Python.
> [!NOTE]  
> The wrapper currently only supports fetching Genshin Impact showcase, Honkai Star Rail and profile fetching are planned.

## Features
 - Fully typed.
 - Provides direct icon URLs.
 - Fully asynchronous by using `aiofiles`, `aiohttp`, and `asyncio`.
 - Supports in-memory caching with [cachetools](https://github.com/tkem/cachetools/).
 - Supports [Pydantic V2](https://github.com/pydantic/pydantic).
 - Seamlessly integrates with [GenshinData](https://gitlab.com/Dimbreath/AnimeGameData).

## Installation
```
poetry add git+https://github.com/seriaati/enka-py
```
**No pip install?**  
I personally use [poetry](https://python-poetry.org/), that's why the build backend is using it. `pip` requires `setuptools`, and I don't think it's possible to use multiple build backends. However, if you know how to, I am more than happy to change it so the package can be installed with both tools.  
> Side note: I strongly recommend you to try out poetry! It will make your Python life so much easier.

## Quick Example
```py
import enka
import asyncio

async def main() -> None:
    async with enka.EnkaAPI() as api:
      response = await api.fetch_genshin_showcase(901211014)
      print(response.player.nickname)
      print(response.characters[0].name)

asyncio.run(main())
```

# Usage
## Starting and closing the client properly
To use the client properly, you can either:  
Manually call `start()` and `close()`  
```py
import enka
import asyncio

async def main() -> None:
    api = enka.EnkaAPI()
    await api.start()
    response = await api.fetch_genshin_showcase(901211014)
    await api.close()

asyncio.run(main())
```
Or use the `async with` syntax:  
```py
import enka
import asyncio

async def main() -> None:
   async with enka.EnkaAPI() as api:
     await api.fetch_genshin_showcase(901211014)

asyncio.run(main())
```
> [!IMPORTANT]  
> You ***need*** to call `start()` or the api client will not function properly; the `close()` method releases resources by closing the session and removing cache from memory.

## Updating assets
In your first use, enka.py will download all the necessary data files to a directory named `.enka_py` (if you're using git, you should add it to `.gitignore`). However, sometimes (often after a game update), the local data will be outdated, and you'd need to update them.  
All assets are hosted in [enka-py-assets](https://github.com/seriaati/enka-py-assets), this repo uses GitHub action to automatically update data.  
To update assets, use the `update_assets()` method:
```py
import enka
import asyncio

async def main() -> None:
    async with enka.EnkaAPI() as api:
      await api.update_assets()

asyncio.run(main())
```
> [!TIP]
> If you're running a Discord bot, you can setup a scheduled task that updates the assets everyday.

## Client parameters
Currently, the `EnkaAPI` class allows you to pass in 4 parameters:
### Language
This will affect the languages of names of weapon, character, constellations, etc. You can find all the languages [here](https://github.com/seriaati/enka-py/blob/890e4b21d46763203fba7a5542a2becab723ea21/enka/enums.py#L12).
### Headers
Custom headers used when requesting the Enka API, it is recommended to set a user agent, the default is `None`. 
### Cache max size
Internally, `cachetools.TTLCache` is used, which uses the LRU strategy. Upon requesting, the client will cache the response with the request URL as key. This means that you should reuse the same client throughout your program so cache can be shared between operations. When the cache max size (default is 100) is reached, the least recently used cache is evicted.
### Cache TTL
Default is 60 seconds, the cache is evicted when this time expires. Note that setting longer TTL might result in inconsistent data.

## Finding models' attributes
If you're using an IDE like VSCode, then you can see all the attributes and methods the model has in the autocomplete.
> [!TIP]
> If you're using VSCode, `alt + left click` on the attribute, then teh IDE will bring you to the source code of this wrapper, most classes and methods have docstrings.

# Questions, issues, contributions
For questions, you can contact me on [Discord](https://discord.com/users/410036441129943050) or open an [issue](https://github.com/seriaati/enka-py/issues).  
To report issues with this wrapper, open an [issue](https://github.com/seriaati/enka-py/issues).  
To contribute, fork this repo and open a [pull request](https://github.com/seriaati/enka-py/pulls).
