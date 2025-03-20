from __future__ import annotations

from pathlib import Path
from typing import Final

ASSET_PATH = Path(".enka_py/assets/zzz")

AVATARS_PATH = ASSET_PATH / "avatars.json"

ENKA_API_DOCS = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/zzz"
ENKA_PY_ASSETS = "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/hsr"

PATH_TO_SOURCE: Final[dict[Path, str]] = {
    AVATARS_PATH: f"{ENKA_API_DOCS}/avatars.json",
}
