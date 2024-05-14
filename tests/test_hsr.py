import pytest

from enka import HSRClient
from enka.hsr import Language


@pytest.mark.asyncio
async def test_fetch_showcase() -> None:
    async with HSRClient() as api:
        await api.fetch_showcase("809162009")


@pytest.mark.asyncio
async def test_trailblazer_showcase() -> None:
    async with HSRClient() as api:
        await api.fetch_showcase("123456786")


@pytest.mark.asyncio
async def test_update_assets() -> None:
    async with HSRClient() as api:
        await api.update_assets()


@pytest.mark.asyncio
async def test_langs() -> None:
    for lang in Language:
        async with HSRClient(lang) as api:
            await api.fetch_showcase("809162009")


@pytest.mark.asyncio
async def test_low_level_acc() -> None:
    async with HSRClient() as api:
        await api.fetch_showcase("829702635")
