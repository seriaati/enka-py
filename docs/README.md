# enka.py

## ⚠️ Notice: Package Renaming

The `enka-api` package has been deprecated and is now replaced by the new package named **`enka`**.
Please install the new package:

```bash
pip install enka
```

The `enka-api` package will continue to be available, but new updates will be released in the `enka` package, so I encourage you to transition to the new package as soon as possible.

## Introduction

enka.py is an async API wrapper for [Enka Network](https://enka.network/) written in Python.  
Developing something for Hoyoverse games? You might be interested in [other API wrappers](https://github.com/seriaati#api-wrappers) written by me.

- [Enka Network API docs](http://api.enka.network/)
- [Documentation for this wrapper](https://gh.seria.moe/enka-py)

### Features

- Fully typed.
- Fully asynchronous by using `aiofiles`, `aiohttp`, and `asyncio`, suitable for Discord bots.
- Provides direct icon URLs.
- Supports Python 3.10+.
- Supports all game languages.
- Supports Genshin Impact, Honkai Star Rail, and Zenless Zone Zero.
- Supports persistent caching using SQLite and allows custom caching strategies.
- Implements stat calculations for HSR and ZZZ.
- Uses [Pydantic v2](https://github.com/pydantic/pydantic), this also means full autocomplete support.
- Seamlessly integrates with [GenshinData](https://gitlab.com/Dimbreath/AnimeGameData), [StarRailData](https://github.com/Dimbreath/StarRailData), and [ZenlessData](https://git.mero.moe/dimbreath/ZenlessData).

## Installation

```bash
pip install enka
```

With optional dependencies:

```bash
# For SQLite caching
pip install enka[sqlite]

# For Redis caching
pip install enka[redis]
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
