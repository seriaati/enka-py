from __future__ import annotations

import contextlib

import pytest

from enka.errors import GameMaintenanceError
from enka.gi import Element, GenshinClient, Language


async def test_update_assets(genshin_client: GenshinClient) -> None:
    await genshin_client.update_assets()


async def test_fetch_showcase(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("901211014")
        assert showcase.uid == "901211014"


async def test_empty_showcase(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("900000001")
        assert showcase.uid == "900000001"
        assert len(showcase.characters) == 0


async def test_traveler_showcase(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("600001919")
        assert showcase.uid == "600001919"


async def test_zero_achievement(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("831335714")
        assert showcase.player.achievements == 0


async def test_new_profile_picture_format(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("724824926")
        assert showcase.player.profile_picture_icon is not None


async def test_costume(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("738081787")
        assert showcase.player.showcase_characters[3].costume is not None


@pytest.mark.parametrize("lang", list(Language))
async def test_langs(lang: Language) -> None:
    async with GenshinClient(lang) as api:
        with contextlib.suppress(GameMaintenanceError):
            await api.fetch_showcase("901211014")


async def test_owner_and_builds(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("618285856")
        assert showcase.owner is not None
        await genshin_client.fetch_builds(showcase.owner)


async def test_fetch_builds(genshin_client: GenshinClient) -> None:
    await genshin_client.fetch_builds({"hash": "1LLUyx", "username": "seria_ati"})


async def test_raw_and_parse(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        raw = await genshin_client.fetch_showcase("901211014", raw=True)
        genshin_client.parse_showcase(raw)


async def test_invalid_player(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await genshin_client.fetch_showcase("901211015")


async def test_no_element_traveler(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("828107378")
        traveler = next(c for c in showcase.characters if c.name == "Aether")
        assert traveler.element is Element.NONE
