from __future__ import annotations

from enka import GenshinClient
from enka.gi import Language


async def test_fetch_showcase() -> None:
    async with GenshinClient() as api:
        showcase = await api.fetch_showcase("901211014")
        assert showcase.uid == "901211014"


async def test_empty_showcase() -> None:
    async with GenshinClient() as api:
        showcase = await api.fetch_showcase("123456789")
        assert showcase.uid == "123456789"
        assert len(showcase.characters) == 0


async def test_traveler_showcase() -> None:
    async with GenshinClient() as api:
        showcase = await api.fetch_showcase("600001919")
        assert showcase.uid == "600001919"


async def test_update_assets() -> None:
    async with GenshinClient() as api:
        await api.update_assets()


async def test_zero_achievement() -> None:
    async with GenshinClient() as api:
        showcase = await api.fetch_showcase("831335714")
        assert showcase.player.achievements == 0


async def test_new_profile_picture_format() -> None:
    async with GenshinClient() as api:
        showcase = await api.fetch_showcase("724824926")
        assert showcase.player.profile_picture_icon is not None


async def test_costume() -> None:
    async with GenshinClient() as api:
        showcase = await api.fetch_showcase("738081787")
        assert showcase.player.showcase_characters[3].costume is not None


async def test_langs() -> None:
    for lang in Language:
        async with GenshinClient(lang) as api:
            await api.fetch_showcase("901211014")


async def test_owner_and_builds() -> None:
    async with GenshinClient() as api:
        showcase = await api.fetch_showcase("618285856")
        assert showcase.owner is not None
        await api.fetch_builds(showcase.owner)


async def test_raw_and_parse() -> None:
    async with GenshinClient() as api:
        raw = await api.fetch_showcase("901211014", raw=True)
        api.parse_showcase(raw)


async def test_invalid_player() -> None:
    async with GenshinClient() as api:
        await api.fetch_showcase("901211015")
