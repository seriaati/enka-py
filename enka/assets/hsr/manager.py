from __future__ import annotations

from ..data import AssetData
from ..manager import AssetManager
from .file_paths import (
    AVATAR_DATA_PATH,
    CHARACTER_DATA_PATH,
    EIDOLON_DATA_PATH,
    LIGHT_CONE_DATA_PATH,
    META_DATA_PATH,
    PROPERTY_CONFIG_PATH,
    RELIC_DATA_PATH,
    SKILL_TREE_DATA_PATH,
    TEXT_MAP_PATH,
)


class HSRAssetManager(AssetManager):
    """Honkai Star Rail asset manager."""

    def __init__(self) -> None:
        self.text_map = AssetData(TEXT_MAP_PATH)
        self.character_data = AssetData(CHARACTER_DATA_PATH)
        self.skill_tree_data = AssetData(SKILL_TREE_DATA_PATH)
        self.light_cones_data = AssetData(LIGHT_CONE_DATA_PATH)
        self.relic_data = AssetData(RELIC_DATA_PATH)
        self.meta_data = AssetData(META_DATA_PATH)
        self.avatar_data = AssetData(AVATAR_DATA_PATH)
        self.property_config_data = AssetData(PROPERTY_CONFIG_PATH)
        self.eidolon_data = AssetData(EIDOLON_DATA_PATH)

        self._assets = (
            self.text_map,
            self.character_data,
            self.skill_tree_data,
            self.light_cones_data,
            self.relic_data,
            self.meta_data,
            self.avatar_data,
            self.property_config_data,
            self.eidolon_data,
        )


HSR_ASSETS = HSRAssetManager()
