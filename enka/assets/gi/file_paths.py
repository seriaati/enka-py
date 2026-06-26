from pathlib import Path

ASSET_PATH = Path(".enka_py/assets")

TEXT_MAP_PATH = ASSET_PATH / "text_map.json"
CHARACTER_DATA_PATH = ASSET_PATH / "characters.json"
NAMECARD_DATA_PATH = ASSET_PATH / "namecards.json"
CONSTS_DATA_PATH = ASSET_PATH / "consts.json"
TALENTS_DATA_PATH = ASSET_PATH / "talents.json"
PFPS_DATA_PATH = ASSET_PATH / "pfps.json"
ARITFACTS_PATH = ASSET_PATH / "artifacts.json"

_ENKA_API_DOCS = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/refs/heads/master/store/gi"
_ENKA_PY_ASSETS = "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data"

PATH_TO_SOURCE = {
    TEXT_MAP_PATH: f"{_ENKA_PY_ASSETS}/text_map.json",
    CHARACTER_DATA_PATH: f"{_ENKA_PY_ASSETS}/characters.json",
    CONSTS_DATA_PATH: f"{_ENKA_PY_ASSETS}/consts.json",
    TALENTS_DATA_PATH: f"{_ENKA_PY_ASSETS}/talents.json",
    PFPS_DATA_PATH: f"{_ENKA_API_DOCS}/pfps.json",
    NAMECARD_DATA_PATH: f"{_ENKA_API_DOCS}/namecards.json",
    ARITFACTS_PATH: f"{_ENKA_API_DOCS}/relics.json",
}
