ASSET_PATH = ".enka_py/assets/hsr"

TEXT_MAP_PATH = f"{ASSET_PATH}/text_map.json"
CHARACTER_DATA_PATH = f"{ASSET_PATH}/characters.json"
LIGHT_CONE_DATA_PATH = f"{ASSET_PATH}/light_cone.json"
RELIC_DATA_PATH = f"{ASSET_PATH}/relic.json"
SKILL_TREE_DATA_PATH = f"{ASSET_PATH}/skill_tree.json"
META_DATA_PATH = f"{ASSET_PATH}/promotions.json"
AVATAR_DATA_PATH = f"{ASSET_PATH}/avatars.json"
PROPERTY_CONFIG_PATH = f"{ASSET_PATH}/property_config.json"
EIDOLON_DATA_PATH = f"{ASSET_PATH}/eidolons.json"

ENKA_API_DOCS = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/hsr"
ENKA_PY_ASSETS = "https://raw.githubusercontent.com/seriaati/enka-py-assets/main/data/hsr"

SOURCE_TO_PATH = {
    f"{ENKA_API_DOCS}/hsr.json": TEXT_MAP_PATH,
    f"{ENKA_API_DOCS}/honker_characters.json": CHARACTER_DATA_PATH,
    f"{ENKA_API_DOCS}/honker_weps.json": LIGHT_CONE_DATA_PATH,
    f"{ENKA_API_DOCS}/honker_relics.json": RELIC_DATA_PATH,
    f"{ENKA_API_DOCS}/honker_meta.json": META_DATA_PATH,
    f"{ENKA_API_DOCS}/honker_avatars.json": AVATAR_DATA_PATH,
    f"{ENKA_API_DOCS}/honker_ranks.json": EIDOLON_DATA_PATH,
    f"{ENKA_PY_ASSETS}/skill_tree.json": SKILL_TREE_DATA_PATH,
    f"{ENKA_PY_ASSETS}/property_config.json": PROPERTY_CONFIG_PATH,
}
