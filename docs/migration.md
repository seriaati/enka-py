# Migration Guide

Due to the addition of Honkai Star Rail, the project structure of enka-py had changed drastically. If you see a lot of import errors after upgrading to V2, don't panic, it is normal.

## How-To

`EnkaAPI` is now `GenshinClient`

```py
import enka

# v1
async with enka.EnkaAPI() as api:
    ...

# v2
async with enka.GenshinClient() as api:
    ...
```

Models, enums, and constants have been moved to the `gi` module

```py
# v1
from enka.models import Character
from enka import Language
from enka.enums import Element

# v2
from enka.gi import Character, Language, Element

# If you plan to use both games, do this instead
from enka import gi, hsr

async with gi.GenshinClient(gi.Language.TURKISH) as client:
    ...

async with hsr.HSRClient(hsr.Language.RUSSIAN) as client:
    ...
```

The `exceptions` module has been renamed to `errors`.

```py
# v1
from enka.exceptions import GameMaintenanceError

# v2
from enka.errors import GameMaintenanceError
```

The `item_id` attribute in `gi.Artifact` has been renamed to `id`, using the `item_id` attribute will now raise a `DeprecationWarning`

```py
# v1
print(artifact.item_id)

# v2
print(artifact.id)
```
