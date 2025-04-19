# Update Game Assets

enka-py relies on several game assets to fill-in things like weapon names, stats icons, etc. that are not provided by the API.  
To speed up the process, these game assets are downloaded **automatically** when you first use the client and are stored **locally** on your machine.  
enka-py doesn't know when the local assets are outdated, so you'd need to update them when necessary. How to handle this process is up to you, I personally just run it once every single day with the scheduled task featured in discord.py  

## How-To

For simplicity, the following examples will use `GenshinClient`, but the same applies to the other clients.

```py
import enka

async with enka.GenshinClient() as client:
    await client.update_assets()
```

!!! note  
    The language you set for the client doesn't matter, the asset updater updates assets for all languages.

## Sources

Data is fetched from the following sources:

- [StarRailData](https://github.com/Dimbreath/StarRailData)
- [AnimeGameData](https://gitlab.com/Dimbreath/AnimeGameData)
- [Enka API-Docs](https://github.com/EnkaNetwork/API-docs)
- [enka-py-assets](https://github.com/seriaati/enka-py-assets)
- [ZenlessData](https://git.mero.moe/dimbreath/ZenlessData)
