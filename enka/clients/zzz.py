from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Final, Literal, overload

from loguru import logger

from ..assets.data import TextMap
from ..assets.hsr.manager import HSR_ASSETS
from ..enums.enum import Game
from ..enums.zzz import Language
from ..models.zzz import ShowcaseResponse
from .base import BaseClient

if TYPE_CHECKING:
    from .cache import BaseTTLCache

__all__ = ("ZZZClient",)

API_URL: Final[str] = "https://enka.network/api/zzz/uid/{uid}"


class ZZZClient(BaseClient):
    """The main client to interact with the Enka Network Honkai Star Rail API.

    Args:
        lang (Language | str): The language to use for the client, defaults to Language.ENGLISH.
        headers (dict[str, Any] | None): The headers to use for the client, defaults to None.
        cache (BaseTTLCache | None): The cache to use for the client, defaults to None.
        use_enka_icons (bool): Whether to get stat icons from Enka, defaults to True.
    """

    def __init__(
        self,
        lang: Language | str = Language.ENGLISH,
        *,
        headers: dict[str, Any] | None = None,
        cache: BaseTTLCache | None = None,
        use_enka_icons: bool = True,
    ) -> None:
        super().__init__(Game.HSR, headers=headers, cache=cache)

        self._lang = self._convert_lang(lang)
        self._use_enka_icons = use_enka_icons
        self._assets = HSR_ASSETS

    def _convert_lang(self, lang: Language | str) -> Language:
        if isinstance(lang, str):
            try:
                lang = Language(lang)
            except ValueError as e:
                available_langs = ", ".join(lang.value for lang in Language)
                msg = f"Invalid language: {lang}, must be one of {available_langs}"
                raise ValueError(msg) from e

        return lang

    @property
    def lang(self) -> Language:
        return self._lang

    @lang.setter
    def lang(self, lang: Language | str) -> None:
        self._lang = self._convert_lang(lang)
        self._text_map = TextMap(self._lang, self._assets.text_map)

    async def __aenter__(self) -> ZZZClient:
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    async def start(self) -> None:
        await super().start()
        await self._assets.load(self.session)
        self._text_map = TextMap(self.lang, self._assets.text_map)

    async def update_assets(self) -> None:
        """Update game assets."""
        logger.info("Updating HSR assets")
        await self._assets.load(self.session)
        logger.info("HSR assets updated")

    @overload
    async def fetch_showcase(
        self, uid: str | int, *, raw: Literal[False] = False
    ) -> ShowcaseResponse: ...
    @overload
    async def fetch_showcase(
        self, uid: str | int, *, raw: Literal[True] = True
    ) -> dict[str, Any]: ...
    async def fetch_showcase(
        self, uid: str | int, *, raw: bool = False
    ) -> ShowcaseResponse | dict[str, Any]:
        """Fetches the ZZZ character showcase of the given UID.

        Args:
            uid (str | int): The UID of the player.
            raw (bool): Whether to return the raw data or not, defaults to False.

        Returns:
            ShowcaseResponse | dict[str, Any]: The parsed or raw showcase data.
        """
        url = API_URL.format(uid=uid)

        data = await self._request(url)
        if raw:
            return data

        data = copy.deepcopy(data)
        showcase = ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase

    def parse_showcase(self, data: dict[str, Any]) -> ShowcaseResponse:
        """Parses the given showcase data.

        Args:
            data (dict[str, Any]): The showcase data.

        Returns:
            ShowcaseResponse: The parsed showcase data.
        """
        data = copy.deepcopy(data)
        showcase = ShowcaseResponse(**data)
        self._post_process_showcase(showcase)
        return showcase
