from __future__ import annotations

from pathlib import Path
from typing import Final

ASSET_PATH = Path(".enka_py/assets/zzz")

AVATARS_PATH = ASSET_PATH / "avatars.json"
TEXT_MAP_PATH = ASSET_PATH / "text_map.json"
EQUIPMENT_LEVEL_PATH = ASSET_PATH / "equipment_level.json"
EQUIPMENTS_PATH = ASSET_PATH / "equipments.json"
PROPERTY_PATH = ASSET_PATH / "property.json"
WEAPON_LEVEL_PATH = ASSET_PATH / "weapon_level.json"
WEAPON_STAR_PATH = ASSET_PATH / "weapon_star.json"
WEAPONS_PATH = ASSET_PATH / "weapons.json"
TITLES_PATH = ASSET_PATH / "titles.json"
NAMECARDS_PATH = ASSET_PATH / "namecards.json"

ENKA_API_DOCS = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/zzz"
ENKA_PY_ASSETS = "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/zzz"

PATH_TO_SOURCE: Final[dict[Path, str]] = {
    AVATARS_PATH: f"{ENKA_API_DOCS}/avatars.json",
    TEXT_MAP_PATH: f"{ENKA_API_DOCS}/locs.json",
    EQUIPMENTS_PATH: f"{ENKA_API_DOCS}/equipments.json",
    PROPERTY_PATH: f"{ENKA_API_DOCS}/property.json",
    WEAPONS_PATH: f"{ENKA_API_DOCS}/weapons.json",
    EQUIPMENT_LEVEL_PATH: f"{ENKA_PY_ASSETS}/equipment_level.json",
    WEAPON_LEVEL_PATH: f"{ENKA_PY_ASSETS}/weapon_level.json",
    WEAPON_STAR_PATH: f"{ENKA_PY_ASSETS}/weapon_star.json",
    TITLES_PATH: f"{ENKA_PY_ASSETS}/titles.json",
    NAMECARDS_PATH: f"{ENKA_PY_ASSETS}/namecards.json",
}
