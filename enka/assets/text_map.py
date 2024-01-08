import contextlib
from typing import TYPE_CHECKING

import aiofiles
import orjson

from .file_paths import TEXT_MAP_PATH

if TYPE_CHECKING:
    from ..client import Language


class TextMap:
    def __init__(self, language: "Language") -> None:
        self.language = language
        self.text_map: dict[str, str] | None = None

    async def load(self) -> None:
        with contextlib.suppress(FileNotFoundError):
            async with aiofiles.open(TEXT_MAP_PATH, encoding="utf-8") as f:
                self.text_map = orjson.loads(await f.read())[self.language.value]

    def __getitem__(self, key: str) -> str:
        if self.text_map is None:
            msg = "Text map not loaded"
            raise RuntimeError(msg)

        text = self.text_map.get(key)
        if text is None:
            msg = f"Cannot find text for key {key} in text map, consider calling `EnkaNetworkAPI.update_assets` to update the text map"
            raise KeyError(msg)

        return text
