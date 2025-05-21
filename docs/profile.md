# Interacting With the Enka Network Profile Endpoint

Enka Network has an account system, and the profile endpoint can be used to fetch information about an account.

## Fetching Character Builds

Enka Network lets users save character builds, they are like "snapshots" of the character's stats, weapons, and all at the time when the build was saved. A character can have multiple builds.

There are 2 ways to fetch character builds:

1. When you've already fetched the showcase of some UID, and the UID is attached to an Enka Network account. Note that an Enka Network user can choose to not display their account on their UID page, in this case, `showcase.owner` would be `None`.
2. When you have the Enka Network account's hash and username.

```py
import enka

async with enka.HSRClient() as client:
    # Method 1
    showcase = await client.fetch_showcase(809162009)
    await client.fetch_builds(showcase.owner)

    # Method 2
    await client.fetch_builds({"hash": "2A2VAE", "username": "seria_ati"})
```
