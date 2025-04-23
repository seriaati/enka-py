from __future__ import annotations

from ..data import AssetData
from ..manager import AssetManager
from .file_paths import (
    AVATARS_PATH,
    EQUIPMENT_LEVEL_PATH,
    EQUIPMENTS_PATH,
    NAMECARDS_PATH,
    PROPERTY_PATH,
    TEXT_MAP_PATH,
    TITLES_PATH,
    WEAPON_LEVEL_PATH,
    WEAPON_STAR_PATH,
    WEAPONS_PATH,
)


class ZZZAssetManager(AssetManager):
    """Zenless Zone Zero asset manager."""

    def __init__(self) -> None:
        self.text_map = AssetData(TEXT_MAP_PATH)
        self.avatars = AssetData(AVATARS_PATH)
        self.equipments = AssetData(EQUIPMENTS_PATH)
        self.equipment_level = AssetData(EQUIPMENT_LEVEL_PATH)
        self.property = AssetData(PROPERTY_PATH)
        self.weapon_star = AssetData(WEAPON_STAR_PATH)
        self.weapon_level = AssetData(WEAPON_LEVEL_PATH)
        self.weapons = AssetData(WEAPONS_PATH)
        self.titles = AssetData(TITLES_PATH)
        self.namecards = AssetData(NAMECARDS_PATH)

        self._assets = (
            self.text_map,
            self.avatars,
            self.equipments,
            self.equipment_level,
            self.property,
            self.weapon_star,
            self.weapon_level,
            self.weapons,
            self.titles,
            self.namecards,
        )


ZZZ_ASSETS = ZZZAssetManager()
