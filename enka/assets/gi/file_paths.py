ASSET_PATH = ".enka_py/assets"

TEXT_MAP_PATH = f"{ASSET_PATH}/text_map.json"
CHARACTER_DATA_PATH = f"{ASSET_PATH}/characters.json"
NAMECARD_DATA_PATH = f"{ASSET_PATH}/namecards.json"
CONSTS_DATA_PATH = f"{ASSET_PATH}/consts.json"
TALENTS_DATA_PATH = f"{ASSET_PATH}/talents.json"
PFPS_DATA_PATH = f"{ASSET_PATH}/pfps.json"

SOURCE_TO_PATH = {
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/text_map.json": TEXT_MAP_PATH,
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/characters.json": CHARACTER_DATA_PATH,
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/namecards.json": NAMECARD_DATA_PATH,
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/consts.json": CONSTS_DATA_PATH,
    "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/talents.json": TALENTS_DATA_PATH,
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/pfps.json": PFPS_DATA_PATH,
}
