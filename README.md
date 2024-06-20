# enka.py

## Quick links

- [Enka.network API docs](http://api.enka.network/)
  
Developing something for Hoyoverse games? Here's a collection of Python async API wrappers for Hoyoverse games made by me:

- [enka.py](https://github.com/seriaati/enka-py) is an Enka Network API wrapper for fetching in-game showcase.
- [yatta.py](https://github.com/seriaati/yatta) is a Project Yatta API wrapper for fetching Honkai Star Rail game data.
- [ambr.py](https://github.com/seriaati/ambr) is a Project Ambr API wrapper for fetching Genshin Impact game data.
- [hakushin.py](https://github.com/seriaati/hakushin-py) is a Hakushin API wrapper for fetching Genshin Impact and Honkai Star Rail beta game data.

## Introduction

enka.py is an async API wrapper for [enka.network](https://enka.network/) written in Python.

### Features

- Fully typed.
- Fully asynchronous by using `aiofiles`, `aiohttp`, and `asyncio`, suitable for Discord bots.
- Provides direct icon URLs.
- Supports Python 3.10+.
- Supports all game languages.
- Supports both Genshin Impact and Honkai Star Rail.
- Supports persistent caching using SQLite.
- Supports [Pydantic V2](https://github.com/pydantic/pydantic), this also means full autocomplete support.
- Seamlessly integrates with [GenshinData](https://gitlab.com/Dimbreath/AnimeGameData) and [StarRailData](https://github.com/Dimbreath/StarRailData).

## Installation

I know it's annoying that the project is named enka-py but the package is named enka-api, but package name enka-py was already taken on PyPI.

```bash
# poetry
poetry add enka-api

# pip
pip install enka-api
```

## Quick Example

```py
import enka
import asyncio

async def main() -> None:
    async with enka.GenshinClient(enka.gi.Language.ENGLISH) as client:
      response = await client.fetch_showcase(901211014)
      print(response.player.nickname)
      print(response.characters[0].name)

asyncio.run(main())
```

## Getting Started

Read the [wiki](https://github.com/seriaati/enka-py/wiki) to learn more about on how to use this wrapper.

## Questions, Issues, Contributions

For questions, you can contact me on [Discord](https://discord.com/users/410036441129943050) or open an [issue](https://github.com/seriaati/enka-py/issues).  
You can also join the [Enka Network Discord server](https://discord.gg/PTyDE78RJC) and find me in the enka-py channel.  
To report issues with this wrapper, open an [issue](https://github.com/seriaati/enka-py/issues).  
To contribute, fork this repo and submit a [pull request](https://github.com/seriaati/enka-py/pulls).
