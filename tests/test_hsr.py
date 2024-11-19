from __future__ import annotations

from enka import HSRClient
from enka.hsr import Language


async def test_fetch_showcase() -> None:
    async with HSRClient() as api:
        await api.fetch_showcase("809162009")


async def test_trailblazer_showcase() -> None:
    async with HSRClient() as api:
        await api.fetch_showcase("123456786")


async def test_update_assets() -> None:
    async with HSRClient() as api:
        await api.update_assets()


async def test_langs() -> None:
    for lang in Language:
        async with HSRClient(lang) as api:
            await api.fetch_showcase("809162009")


async def test_low_level_acc() -> None:
    async with HSRClient() as api:
        await api.fetch_showcase("829702635")


async def test_owner_and_builds() -> None:
    async with HSRClient() as api:
        showcase = await api.fetch_showcase("809162009")
        assert showcase.owner is not None
        await api.fetch_builds(showcase.owner)


async def test_raw_and_parse() -> None:
    async with HSRClient() as api:
        raw = await api.fetch_showcase("809162009", raw=True)
        api.parse_showcase(raw)


async def test_empty_substat_list() -> None:
    async with HSRClient() as api:
        await api.fetch_showcase("800724088")
