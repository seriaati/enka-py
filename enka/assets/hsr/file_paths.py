from __future__ import annotations

from pathlib import Path
from typing import Final

ASSET_PATH = Path(".enka_py/assets/hsr")

TEXT_MAP_PATH = ASSET_PATH / "text_map.json"
CHARACTER_DATA_PATH = ASSET_PATH / "characters.json"
LIGHT_CONE_DATA_PATH = ASSET_PATH / "light_cone.json"
RELIC_DATA_PATH = ASSET_PATH / "relic.json"
SKILL_TREE_DATA_PATH = ASSET_PATH / "skill_tree.json"
META_DATA_PATH = ASSET_PATH / "promotions.json"
AVATAR_DATA_PATH = ASSET_PATH / "avatars.json"
PROPERTY_CONFIG_PATH = ASSET_PATH / "property_config.json"
EIDOLON_DATA_PATH = ASSET_PATH / "eidolons.json"

ENKA_API_DOCS = "https://raw.githubusercontent.com/pizza-studio/EnkaDBGenerator/main/Sources/EnkaDBFiles/Resources/Specimen/HSR"
ENKA_PY_ASSETS = "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/hsr"

PATH_TO_SOURCE: Final[dict[Path, str]] = {
    CHARACTER_DATA_PATH: f"{ENKA_API_DOCS}/honker_characters.json",
    LIGHT_CONE_DATA_PATH: f"{ENKA_API_DOCS}/honker_weps.json",
    RELIC_DATA_PATH: f"{ENKA_API_DOCS}/honker_relics.json",
    META_DATA_PATH: f"{ENKA_API_DOCS}/honker_meta.json",
    AVATAR_DATA_PATH: f"{ENKA_API_DOCS}/honker_avatars.json",
    EIDOLON_DATA_PATH: f"{ENKA_API_DOCS}/honker_ranks.json",
    SKILL_TREE_DATA_PATH: f"{ENKA_PY_ASSETS}/skill_tree.json",
    PROPERTY_CONFIG_PATH: f"{ENKA_PY_ASSETS}/property_config.json",
    TEXT_MAP_PATH: f"{ENKA_PY_ASSETS}/hsr.json",
}
