from __future__ import annotations

from pathlib import Path

ASSET_PATH = Path(".enka_py/assets")

TEXT_MAP_PATH = ASSET_PATH / "text_map.json"
CHARACTER_DATA_PATH = ASSET_PATH / "characters.json"
NAMECARD_DATA_PATH = ASSET_PATH / "namecards.json"
CONSTS_DATA_PATH = ASSET_PATH / "consts.json"
TALENTS_DATA_PATH = ASSET_PATH / "talents.json"
PFPS_DATA_PATH = ASSET_PATH / "pfps.json"

PATH_TO_SOURCE = {
    TEXT_MAP_PATH: "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/text_map.json",
    CHARACTER_DATA_PATH: "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/characters.json",
    NAMECARD_DATA_PATH: "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/namecards.json",
    CONSTS_DATA_PATH: "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/consts.json",
    TALENTS_DATA_PATH: "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/talents.json",
    PFPS_DATA_PATH: "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/pfps.json",
}
