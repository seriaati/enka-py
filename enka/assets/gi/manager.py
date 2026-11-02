from ..data import AssetData
from ..manager import AssetManager
from .file_paths import (
    ARITFACTS_PATH,
    ARTIFACT_ITEMS_PATH,
    CHARACTER_DATA_PATH,
    CONSTS_DATA_PATH,
    NAMECARD_DATA_PATH,
    PFPS_DATA_PATH,
    TALENTS_DATA_PATH,
    TEXT_MAP_PATH,
    WEAPONS_DATA_PATH,
)


class GIAssetManager(AssetManager):
    """Genshin Impact asset manager."""

    def __init__(self) -> None:
        self.text_map = AssetData(TEXT_MAP_PATH)
        self.character_data = AssetData(CHARACTER_DATA_PATH)
        self.namecard_data = AssetData(NAMECARD_DATA_PATH)
        self.consts_data = AssetData(CONSTS_DATA_PATH)
        self.talents_data = AssetData(TALENTS_DATA_PATH)
        self.pfps_data = AssetData(PFPS_DATA_PATH)
        self.artifacts_data = AssetData(ARITFACTS_PATH)
        self.artifact_items_data = AssetData(ARTIFACT_ITEMS_PATH)
        self.weapons_data = AssetData(WEAPONS_DATA_PATH)

        self._assets = (
            self.text_map,
            self.character_data,
            self.namecard_data,
            self.consts_data,
            self.talents_data,
            self.pfps_data,
            self.artifacts_data,
            self.artifact_items_data,
            self.weapons_data,
        )


GI_ASSETS = GIAssetManager()
