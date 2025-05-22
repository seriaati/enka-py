# Profile Endpoint

Enka Network has an account system, and the profile endpoint can be used to fetch information about an account.

For simplicity, we will call "Enka Network" as "Enka" below.

## What Identifies an Enka Account?

A username represents an Enka account (it is unique accross the platform), and the hash represents one game account that the account owns.
Take this URL as an example: <https://enka.network/u/seria_ati/2A2VAE/1005/1775642/>

`2A2VAE` is the hash (represents the HSR account), and `seria_ati` is the username (represents the Enka account.)

## Fetching Character Builds

Enka lets users save character builds, they are like "snapshots" of the character's stats, weapons, and all at the time when the build was saved. A character can have multiple builds.

There are 2 situations for fetching character builds:

1. When you've already fetched the showcase of some UID, and the UID is attached to an Enka account. Note that an Enka user can choose to not display their account on their UID page, in this case, `showcase.owner` would be `None`.
2. When you only have the Enka account's hash and username.

The code block belows shows how you would fetch builds for a Genshin Impact account, but the same applies to other games, you just need to change the client being used.

```py
import enka

async with enka.HSRClient() as client:
    # Method 1
    showcase = await client.fetch_showcase(809162009)
    await client.fetch_builds(showcase.owner)

    # Method 2
    await client.fetch_builds({"hash": "2A2VAE", "username": "seria_ati"})
```
