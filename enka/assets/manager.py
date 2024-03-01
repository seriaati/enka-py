import contextlib
from typing import TYPE_CHECKING, Any

import aiofiles
import orjson

from .file_paths import (
    CHARACTER_DATA_PATH,
    CONSTS_DATA_PATH,
    NAMECARD_DATA_PATH,
    PFPS_DATA_PATH,
    TALENTS_DATA_PATH,
    TEXT_MAP_PATH,
)

if TYPE_CHECKING:
    from ..client import Language

__all__ = ("AssetManager",)


class AssetManager:
    def __init__(self, lang: "Language") -> None:
        self._lang = lang
        self.text_map = TextMap(lang)
        self.character_data = CharacterData()
        self.namecard_data = NamecardData()
        self.consts_data = ConstsData()
        self.talents_data = TalentsData()
        self.pfps_data = PfpsData()

    async def load(self) -> bool:
        text_map_loaded = await self.text_map.load()
        character_data_loaded = await self.character_data.load()
        namecard_data_loaded = await self.namecard_data.load()
        consts_data_loaded = await self.consts_data.load()
        talents_data_loaded = await self.talents_data.load()
        pfp_data_loaded = await self.pfps_data.load()

        return (
            text_map_loaded
            and character_data_loaded
            and namecard_data_loaded
            and consts_data_loaded
            and talents_data_loaded
            and pfp_data_loaded
        )


class AssetData:
    def __init__(self) -> None:
        self._data: dict[str, Any] | None = None

    def __getitem__(self, key: str) -> Any:
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        text = self._data.get(str(key))
        if text is None:
            msg = f"Cannot find text for key {key!r} in `{self.__class__.__name__}._data`, consider calling `EnkaNetworkAPI.update_assets` to update the assets"
            raise KeyError(msg)

        return text

    def __iter__(self) -> Any:
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        return iter(self._data)

    def values(self) -> Any:
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        return self._data.values()

    def items(self) -> Any:
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        return self._data.items()

    async def _open_json(self, path: str) -> dict[str, Any] | None:
        with contextlib.suppress(FileNotFoundError):
            async with aiofiles.open(path, encoding="utf-8") as f:
                return orjson.loads(await f.read())
        return None

    def get(self, key: str, default: Any = None) -> str | Any:
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        text = self._data.get(str(key))
        if text is None:
            return default

        return text


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


class NamecardData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(NAMECARD_DATA_PATH)
        return self._data is not None


class ConstsData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(CONSTS_DATA_PATH)
        return self._data is not None


class TalentsData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(TALENTS_DATA_PATH)
        return self._data is not None


class PfpsData(AssetData):
    async def load(self) -> bool:
        self._data = await self._open_json(PFPS_DATA_PATH)
        return self._data is not None
