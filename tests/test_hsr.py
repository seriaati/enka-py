from __future__ import annotations

import pytest

from enka.hsr import HSRClient, Language


async def test_update_assets(hsr_client: HSRClient) -> None:
    await hsr_client.update_assets()


async def test_fetch_showcase(hsr_client: HSRClient) -> None:
    await hsr_client.fetch_showcase("809162009")


async def test_trailblazer_showcase(hsr_client: HSRClient) -> None:
    await hsr_client.fetch_showcase("123456786")


@pytest.mark.parametrize("lang", list(Language))
async def test_langs(lang: Language) -> None:
    async with HSRClient(lang) as api:
        await api.fetch_showcase("809162009")


async def test_low_level_acc(hsr_client: HSRClient) -> None:
    await hsr_client.fetch_showcase("829702635")


async def test_owner_and_builds(hsr_client: HSRClient) -> None:
    showcase = await hsr_client.fetch_showcase("809162009")
    assert showcase.owner is not None
    await hsr_client.fetch_builds(showcase.owner)


async def test_raw_and_parse(hsr_client: HSRClient) -> None:
    raw = await hsr_client.fetch_showcase("809162009", raw=True)
    hsr_client.parse_showcase(raw)


async def test_empty_substat_list(hsr_client: HSRClient) -> None:
    await hsr_client.fetch_showcase("800724088")
