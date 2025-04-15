from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import aiofiles
import aiofiles.os
import orjson
from loguru import logger

from ..assets.gi.file_paths import PATH_TO_SOURCE as GI_PATH_TO_SOURCE
from ..assets.hsr.file_paths import PATH_TO_SOURCE as HSR_PATH_TO_SOURCE
from ..assets.zzz.file_paths import PATH_TO_SOURCE as ZZZ_PATH_TO_SOURCE
from ..errors import AssetDownloadError, AssetKeyError

if TYPE_CHECKING:
    import pathlib

    import aiohttp

    from ..enums import gi, hsr, zzz

PATH_TO_SOURCE = GI_PATH_TO_SOURCE | HSR_PATH_TO_SOURCE | ZZZ_PATH_TO_SOURCE


class BaseAssetData:
    """Base class for asset data, this functions like a dictionary."""

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self._data: dict[str, Any] | None = data

    @property
    def data(self) -> dict[str, Any]:
        if self._data is None:
            msg = f"{self.__class__.__name__} is not loaded"
            raise RuntimeError(msg)
        return self._data

    @data.setter
    def data(self, value: dict[str, Any]) -> None:
        self._data = value

    def __getitem__(self, key: str) -> Any:
        try:
            return self.data[str(key)]
        except KeyError as e:
            raise AssetKeyError(key, self.__class__) from e

    def __iter__(self) -> Any:
        return iter(self.data)

    def values(self) -> Any:
        return self.data.values()

    def items(self) -> Any:
        return self.data.items()

    def get(self, key: str, default: Any = None) -> Any:
        text = self.data.get(str(key))
        if text is None:
            return default

        return text


class AssetData(BaseAssetData):
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__()
        self._path = path

    async def _open_json(self) -> dict[str, Any] | None:
        logger.debug(f"Opening {self._path}")
        with contextlib.suppress(FileNotFoundError):
            async with aiofiles.open(self._path, encoding="utf-8") as f:
                return orjson.loads(await f.read())
        return None

    async def _download_json(self, session: aiohttp.ClientSession) -> None:
        url = PATH_TO_SOURCE[self._path]
        logger.debug(f"Downloading from {url}")

        async with session.get(url) as resp:
            if resp.status != 200:
                raise AssetDownloadError(resp.status, url)

            text = await resp.text()

            await aiofiles.os.makedirs(self._path.parent, exist_ok=True)
            async with aiofiles.open(self._path, "w", encoding="utf-8") as f:
                await f.write(text)

            self._data = orjson.loads(text)

    async def update(self, session: aiohttp.ClientSession) -> None:
        await self._download_json(session)
        logger.debug(f"Updated {self._path}")

    async def load(self, session: aiohttp.ClientSession) -> None:
        """Load or download the asset data"""
        if self._data is not None:
            # Prevent loading asset again
            return

        self._data = await self._open_json()
        if self._data is None:
            await self._download_json(session)


class TextMap(BaseAssetData):
    """Text map asset data."""

    def __init__(
        self, lang: gi.Language | hsr.Language | zzz.Language, text_map: AssetData
    ) -> None:
        super().__init__(text_map[lang.value])
