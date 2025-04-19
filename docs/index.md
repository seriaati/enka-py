# enka.py

## Introduction

enka.py is an async API wrapper for [enka.network](https://enka.network/) written in Python.  
You can find the API docs for Enka Network [here](http://api.enka.network/).  
Developing something for Hoyoverse games? You might be interested in [other API wrappers](https://github.com/seriaati#api-wrappers) written by me.

### Features

- Fully typed.
- Fully asynchronous by using `aiofiles`, `aiohttp`, and `asyncio`, suitable for Discord bots.
- Provides direct icon URLs.
- Supports Python 3.10+.
- Supports all game languages.
- Supports both Genshin Impact and Honkai Star Rail.
- Supports persistent caching using SQLite.
- Supports [Pydantic V2](https://github.com/pydantic/pydantic), this also means full autocomplete support.
- Seamlessly integrates with [GenshinData](https://gitlab.com/Dimbreath/AnimeGameData), [StarRailData](https://github.com/Dimbreath/StarRailData), and [ZenlessData](https://git.mero.moe/dimbreath/ZenlessData).

## Installation

```bash
pip install enka
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

Read the [documentation](https://gh.seria.moe/enka-py) to learn more about on how to use this wrapper.

## Questions, Issues, Feedback, Contributions

Whether you want to make any bug reports, feature requests, or contribute to the wrapper, simply open an issue or pull request in this repository.  
If GitHub is not your type, you can find me on [Discord](https://discord.com/invite/b22kMKuwbS), my username is @seria_ati.
