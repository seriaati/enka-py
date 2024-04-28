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
   - [Catching exceptions](#catching-exceptions)
   - [Namecards and Icons](#namecards-and-icons)
   - [Stats](#stats)
   - [Constellations](#constellations)

3. [Questions, issues, contributions](#questions-issues-contributions)

## Quick links
- [Enka.network API docs](http://api.enka.network/)
  
Developing something for Hoyoverse games? Here's a collection of Python async API wrappers for Hoyoverse games made by me:

- [enka.py](https://github.com/seriaati/enka-py) is an Enka Network API wrapper for fetching in-game showcase.
- [yatta.py](https://github.com/seriaati/yatta) is a Project Yatta API wrapper for fetching Honkai Star Rail game data.
- [ambr.py](https://github.com/seriaati/yatta) is a Project Ambr API wrapper for fetching Genshin Impact game data.
- [hakushin.py](https://github.com/seriaati/hakushin) is a Hakushin API wrapper for fetching Genshin Impact and Honkai Star Rail beta game data.

# Introduction
enka.py is an async API wrapper for [enka.network](https://enka.network/) written in Python.
> [!NOTE]  
> The wrapper only supports fetching Genshin Impact showcase, for Honkai: Star Rail, use [mihomo](https://github.com/KT-Yeh/mihomo) instead.

## Features
 - Fully typed.
 - Provides direct icon URLs.
 - Fully asynchronous by using `aiofiles`, `aiohttp`, and `asyncio`.
 - Supports persistent caching using SQLite.
 - Supports [Pydantic V2](https://github.com/pydantic/pydantic).
 - Seamlessly integrates with [GenshinData](https://gitlab.com/Dimbreath/AnimeGameData).

## Installation
```
# poetry
poetry add git+https://github.com/seriaati/enka-py

# pip
pip install git+https://github.com/seriaati/enka-py
```

## Quick Example
```py
import enka
import asyncio

async def main() -> None:
    async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(901211014)
      print(response.player.nickname)
      print(response.characters[0].name)

asyncio.run(main())
```

Full example can be found in [example.py](https://github.com/seriaati/enka-py/blob/main/example.py)

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
    response = await api.fetch_showcase(901211014)
    await api.close()

asyncio.run(main())
```
Or use the `async with` syntax:  
```py
import enka
import asyncio

async def main() -> None:
   async with enka.EnkaAPI() as api:
     await api.fetch_showcase(901211014)

asyncio.run(main())
```
> [!IMPORTANT]  
> You ***need*** to call `start()` or the api client will not function properly; the `close()` method closes the request session and database properly.

## Updating assets
In your first use, enka.py will download all the necessary data files to a directory named `.enka_py` (if you're using git, you should add it to `.gitignore`). However, sometimes (often after a game update), the local data will be outdated, and you'd need to update them.  
All assets are hosted in [enka-py-assets](https://github.com/seriaati/enka-py-assets), it uses GitHub action to automatically update data.  
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
Custom headers used when requesting the Enka API, it is recommended to set a user agent, the default is `{"User-Agent": "enka-py"}`.
### Cache TTL
Default is 60 seconds, the cache is evicted when this time expires. Note that setting longer TTL might result in inconsistent data.

## Finding models' attributes
If you're using an IDE like VSCode or Pycharm, then you can see all the attributes and methods the model has in the autocomplete.
> [!TIP]
> If you're using VSCode, `alt` + `left click` on the attribute, then the IDE will bring you to the source code of this wrapper, most classes and methods have docstrings.

## Catching exceptions
All exception classes can be found in [enka/exceptions.py](https://github.com/seriaati/enka-py/blob/main/enka/exceptions.py), catch them with `try-except`.  
Example can be found in [example.py](https://github.com/seriaati/enka-py/blob/main/example.py)

## Namecards and icons
*Available after v1.2.0*  
  
Character icons are now `Icon` objects, you can access all types of icons from it:
- `icon.side`: https://enka.network/ui/UI_AvatarIcon_Side_Ambor.png
- `icon.circle`: https://enka.network/ui/UI_AvatarIcon_Ambor_Circle.png
- `icon.gacha`:  https://enka.network/ui/UI_Gacha_AvatarImg_Ambor.png
- `icon.front`: https://enka.network/ui/UI_AvatarIcon_Ambor.png

The same goes for `ShowcaseCharacter.costume_icon` and `Player.profile_picture_icon`.

Namecards are now `Namecard` objects:
- `Namecard.icon`: https://enka.network/ui/UI_NameCardIcon_0.png
- `Namecard.full`: https://enka.network/ui/UI_NameCardPic_0_P.png

> [!WARNING]
> `Player.namecard_icon` is renamed to `Player.namecard`. Also, `Character.side_icon`, `Character.art` are removed as they are merged into the `Icon` class, same for `ShowcaseCharacter.costume_art` and `ShowcaseCharacter.costume_side_icon`.

## Stats
*Available after v1.4.0*  
  
Stats refer to character, weapon, and artifact stats.  
Internally, stats for characters are `FightProp` classes, while the others are `Stat` classes; they can be accessed in the same way, but their `type`s are different (`FightPropType` and `StatType`).  
For your convenience, there are `stat.is_percentage` and `stat.formatted_value` to use, for exmple:  
- If `stat.type` is `StatType.FIGHT_PROP_CUR_ATTACK`
  - `stat.is_percentage = False`
  - `stat.formatted_value = '2300'`
- If `stat.type` is `StatType.FIGHT_PROP_CRITICAL`
  - `stat.is_percentage = True`
  - `stat.formatted_value = '23.1%'`

## Constellations
*Available after v1.7.0*  
  
After v1.7.0, all constellations that belong to a character will appear in `Character.constellations`, the `Constellation.unlocked` attribute will indicate whether the constellation is unlocked. Also, there is a new attribute `Character.constellations_unlocked` that indicates how many constellations the character has unlocked.

# Questions, issues, contributions
For questions, you can contact me on [Discord](https://discord.com/users/410036441129943050) or open an [issue](https://github.com/seriaati/enka-py/issues).  
To report issues with this wrapper, open an [issue](https://github.com/seriaati/enka-py/issues).  
To contribute, fork this repo and submit a [pull request](https://github.com/seriaati/enka-py/pulls).
