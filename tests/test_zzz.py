from __future__ import annotations

import pytest

from enka.errors import PlayerDoesNotExistError
from enka.zzz import Language, ZZZClient


async def test_update_assets(zzz_client: ZZZClient) -> None:
    await zzz_client.update_assets()


async def test_fetch_showcase(zzz_client: ZZZClient) -> None:
    await zzz_client.fetch_showcase("1300025292")


@pytest.mark.parametrize("lang", list(Language))
async def test_langs(lang: Language) -> None:
    async with ZZZClient(lang) as api:
        await api.fetch_showcase("1300025292")


async def test_raw_and_parse(zzz_client: ZZZClient) -> None:
    raw = await zzz_client.fetch_showcase("1300025292", raw=True)
    zzz_client.parse_showcase(raw)


async def test_not_exist_player(zzz_client: ZZZClient) -> None:
    with pytest.raises(PlayerDoesNotExistError):
        await zzz_client.fetch_showcase("1000000000")
