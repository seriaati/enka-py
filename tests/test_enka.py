import pytest

from enka.client import EnkaAPI


@pytest.mark.asyncio
async def test_fetch_showcase() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_genshin_showcase("901211014")
        assert showcase.uid == "901211014"


@pytest.mark.asyncio
async def test_empty_showcase() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_genshin_showcase("123456789")
        assert showcase.uid == "123456789"
        assert len(showcase.characters) == 0


@pytest.mark.asyncio
async def test_traveler_showcase() -> None:
    async with EnkaAPI() as api:
        showcase = await api.fetch_genshin_showcase("600001919")
        assert showcase.uid == "600001919"


@pytest.mark.asyncio
async def test_update_assets() -> None:
    async with EnkaAPI() as api:
        await api.update_assets()
