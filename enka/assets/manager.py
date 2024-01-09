import contextlib
from typing import TYPE_CHECKING, Any

import aiofiles
import orjson

from .file_paths import CHARACTER_DATA_PATH, NAMECARD_DATA_PATH, TEXT_MAP_PATH

if TYPE_CHECKING:
    from ..client import Language

__all__ = ("AssetManager",)


class AssetManager:
    def __init__(self, lang: "Language") -> None:
        self._lang = lang
        self.text_map = TextMap(lang)
        self.character_data = CharacterData()
        self.namecard_data = NamecardData()

    async def load(self) -> bool:
        text_map_loaded = await self.text_map.load()
        character_data_loaded = await self.character_data.load()
        namecard_data_loaded = await self.namecard_data.load()

        return text_map_loaded and character_data_loaded and namecard_data_loaded


class TextMap:
    def __init__(self, lang: "Language") -> None:
        self._lang = lang
        self._map: dict[str, str] | None = None

    async def load(self) -> bool:
        with contextlib.suppress(FileNotFoundError):
            async with aiofiles.open(TEXT_MAP_PATH, encoding="utf-8") as f:
                self._map = orjson.loads(await f.read())[self._lang.value]
        return self._map is not None

    def __getitem__(self, key: str) -> str:
        if self._map is None:
            msg = "Text map not loaded"
            raise RuntimeError(msg)

        text = self._map.get(str(key))
        if text is None:
            msg = f"Cannot find text for key {key} in text map, consider calling `EnkaNetworkAPI.update_assets` to update the text map"
            raise KeyError(msg)

        return text

    def get(self, key: str, default: Any = None) -> str | Any:
        if self._map is None:
            msg = "Text map not loaded"
            raise RuntimeError(msg)

        text = self._map.get(str(key))
        if text is None:
            return default

        return text


class CharacterData:
    def __init__(self) -> None:
        self._data: dict[str, Any] | None = None

    async def load(self) -> bool:
        with contextlib.suppress(FileNotFoundError):
            async with aiofiles.open(CHARACTER_DATA_PATH, encoding="utf-8") as f:
                self._data = orjson.loads(await f.read())

        return self._data is not None

    def __getitem__(self, key: str) -> Any:
        if self._data is None:
            msg = "Character data not loaded"
            raise RuntimeError(msg)

        data = self._data.get(key)
        if data is None:
            msg = f"Cannot find data for key {key} in character data, consider calling `EnkaNetworkAPI.update_assets` to update the character data"
            raise KeyError(msg)

        return data


class NamecardData:
    def __init__(self) -> None:
        self._data: dict[str, Any] | None = None

    async def load(self) -> bool:
        with contextlib.suppress(FileNotFoundError):
            async with aiofiles.open(NAMECARD_DATA_PATH, encoding="utf-8") as f:
                self._data = orjson.loads(await f.read())

        return self._data is not None

    def get_icon(self, namecard_id: str) -> str:
        if self._data is None:
            msg = "Namecard data not loaded"
            raise RuntimeError(msg)

        data = self._data.get(namecard_id)
        if data is None:
            msg = f"Cannot find data for key {namecard_id} in namecard data, consider calling `EnkaNetworkAPI.update_assets` to update the namecard data"
            raise KeyError(msg)

        return data["icon"]
