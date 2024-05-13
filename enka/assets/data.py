import contextlib
from typing import Any

import aiofiles
import orjson


class AssetData:
    """Base class for asset data."""

    def __init__(self) -> None:
        self._data: dict[str, Any] | None = None

    def __getitem__(self, key: str) -> Any:
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        text = self._data.get(str(key))
        if text is None:
            msg = f"Cannot find text for key {key!r} in `{self.__class__.__name__}._data`, consider calling `update_assets` to update the assets"
            raise KeyError(msg)

        return text

    def __iter__(self) -> Any:
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        return iter(self._data)

    def values(self) -> Any:
        """Get the values of the data."""
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        return self._data.values()

    def items(self) -> Any:
        """Get the items of the data."""
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
        """Get a text by key.

        Args:
            key (str): The key to get the text for.
            default (Any): The default value to return if the key is not found.

        Returns:
            str | Any: The text or the default value.
        """
        if self._data is None:
            msg = f"{self.__class__.__name__} not loaded"
            raise RuntimeError(msg)

        text = self._data.get(str(key))
        if text is None:
            return default

        return text
