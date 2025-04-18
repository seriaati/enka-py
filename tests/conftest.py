from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from enka.gi import GenshinClient
from enka.hsr import HSRClient
from enka.zzz import ZZZClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@pytest.fixture
async def genshin_client() -> AsyncGenerator[GenshinClient]:
    async with GenshinClient() as client:
        yield client


@pytest.fixture
async def hsr_client() -> AsyncGenerator[HSRClient]:
    async with HSRClient() as client:
        yield client


@pytest.fixture
async def zzz_client() -> AsyncGenerator[ZZZClient]:
    async with ZZZClient() as client:
        yield client
