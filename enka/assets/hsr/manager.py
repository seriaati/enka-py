from typing import TYPE_CHECKING

from ..data import AssetData
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

if TYPE_CHECKING:
    from ...enums.hsr import Language

__all__ = ("AssetManager",)


class AssetManager:
    """Honkai Star Rail asset manager."""

    def __init__(self, lang: "Language") -> None:
        self._lang = lang

        self.text_map = TextMap(lang)
        self.character_data = CharacterData()
        self.skill_tree_data = SkillTreeData()
        self.light_cones_data = LightConesData()
        self.relic_data = RelicData()
        self.meta_data = MetaData()
        self.avatar_data = AvatarData()
        self.property_config_data = PropertyConfigData()
        self.eidolon_data = EidolonData()

    async def load(self) -> bool:
        """Load all assets.

        Returns:
            bool: Whether all assets were loaded successfully.
        """
        return (
            await self.text_map.load()
            and await self.character_data.load()
            and await self.skill_tree_data.load()
            and await self.light_cones_data.load()
            and await self.relic_data.load()
            and await self.meta_data.load()
            and await self.avatar_data.load()
            and await self.property_config_data.load()
            and await self.eidolon_data.load()
        )


class TextMap(AssetData):
    def __init__(self, lang: "Language") -> None:
        super().__init__()
        self._lang = lang

    async def load(self) -> bool:
        text_map = await self._open_json(TEXT_MAP_PATH)
        if text_map is not None:
            self._data = text_map[self._lang.value]
        return self._data is not None


class CharacterData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(CHARACTER_DATA_PATH)
        return self._data is not None


class SkillTreeData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(SKILL_TREE_DATA_PATH)
        return self._data is not None


class LightConesData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(LIGHT_CONE_DATA_PATH)
        return self._data is not None


class RelicData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(RELIC_DATA_PATH)
        return self._data is not None


class MetaData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(META_DATA_PATH)
        return self._data is not None


class AvatarData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(AVATAR_DATA_PATH)
        return self._data is not None


class PropertyConfigData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(PROPERTY_CONFIG_PATH)
        return self._data is not None


class EidolonData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(EIDOLON_DATA_PATH)
        return self._data is not None
