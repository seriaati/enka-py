from __future__ import annotations

import asyncio
import contextlib
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiofiles
import aiofiles.os
import aiohttp
import orjson
from loguru import logger

from ..assets.gi.file_paths import PATH_TO_SOURCE as GI_PATH_TO_SOURCE
from ..assets.hsr.file_paths import PATH_TO_SOURCE as HSR_PATH_TO_SOURCE
from ..assets.zzz.file_paths import PATH_TO_SOURCE as ZZZ_PATH_TO_SOURCE
from ..errors import AssetKeyError

if TYPE_CHECKING:
    import pathlib

    from ..enums import gi, hsr, zzz

PATH_TO_SOURCE = GI_PATH_TO_SOURCE | HSR_PATH_TO_SOURCE | ZZZ_PATH_TO_SOURCE

# Streaming download tuning. `total` is intentionally unset: it would cap the
# entire body read and trip on large files over slow links. `sock_read` is a
# per-read inactivity timeout that resets on every chunk, so steady downloads of
# any size succeed while genuinely stalled connections still abort.
DOWNLOAD_TIMEOUT = aiohttp.ClientTimeout(total=None, sock_connect=10, sock_read=30)
DOWNLOAD_CHUNK_SIZE = 1024 * 64
DOWNLOAD_MAX_RETRIES = 3
DOWNLOAD_RETRY_BACKOFF = 1  # base seconds, doubled each retry


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

    async def _stream_to_file(
        self, session: aiohttp.ClientSession, url: str, temp_path: Path, file_path: Path
    ) -> None:
        async with session.get(url, timeout=DOWNLOAD_TIMEOUT) as resp:
            resp.raise_for_status()

            async with aiofiles.open(temp_path, mode="wb") as f:
                async for chunk in resp.content.iter_chunked(DOWNLOAD_CHUNK_SIZE):
                    await f.write(chunk)

        await aiofiles.os.replace(temp_path, file_path)

    async def _download_json(self, session: aiohttp.ClientSession) -> None:
        url = PATH_TO_SOURCE[self._path]
        file_path = Path(self._path)

        await asyncio.to_thread(file_path.parent.mkdir, parents=True, exist_ok=True)

        temp_filename = f".tmp_{uuid.uuid4().hex}_{file_path.name}"
        temp_path = file_path.parent / temp_filename

        try:
            for attempt in range(1, DOWNLOAD_MAX_RETRIES + 1):
                logger.debug(
                    f"Downloading {url} to {file_path} (attempt {attempt}/{DOWNLOAD_MAX_RETRIES})..."
                )
                try:
                    await self._stream_to_file(session, url, temp_path, file_path)
                    break
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    # 4xx responses are not transient (e.g. 404); don't retry them.
                    if isinstance(e, aiohttp.ClientResponseError) and e.status < 500:
                        logger.error(f"Failed to download {url}: {e}")
                        raise

                    if attempt == DOWNLOAD_MAX_RETRIES:
                        logger.error(
                            f"Failed to download {url} after {DOWNLOAD_MAX_RETRIES} attempts: {e}"
                        )
                        raise

                    backoff = DOWNLOAD_RETRY_BACKOFF * 2 ** (attempt - 1)
                    logger.warning(
                        f"Download of {url} failed (attempt {attempt}/{DOWNLOAD_MAX_RETRIES}): "
                        f"{e}; retrying in {backoff}s"
                    )
                    await asyncio.sleep(backoff)

        finally:
            if await aiofiles.os.path.exists(temp_path):
                try:
                    await aiofiles.os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Failed to remove temporary file {temp_path}: {e}")

        self._data = await self._open_json()

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

    def __getitem__(self, key: str) -> Any:
        if not key:
            return key
        try:
            return self.data[str(key)]
        except KeyError:
            logger.error(f"TextMap key {key!r} not found, consider calling update_assets()")
            return str(key)
