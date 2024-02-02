import pytest

from enka.client import EnkaAPI


@pytest.mark.asyncio
async def test_fetch_showcase() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_showcase("901211014")
        assert showcase.uid == "901211014"


@pytest.mark.asyncio
async def test_empty_showcase() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_showcase("123456789")
        assert showcase.uid == "123456789"
        assert len(showcase.characters) == 0


@pytest.mark.asyncio
async def test_traveler_showcase() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_showcase("600001919")
        assert showcase.uid == "600001919"


@pytest.mark.asyncio
async def test_update_assets() -> None:
    async with EnkaAPI() as api:
        await api.update_assets()


@pytest.mark.asyncio
async def test_zero_achievement() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_showcase("831335714")
        assert showcase.player.achievements == 0


@pytest.mark.asyncio
async def test_new_profile_picture_format() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_showcase("724824926")
        assert showcase.player.profile_picture_icon is not None
