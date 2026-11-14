from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import aiohttp
import pytest

from enka.assets.data import AssetData
from enka.clients.base import BaseClient
from enka.errors import (
    GameMaintenanceError,
    GatewayTimeoutError,
    PlayerDoesNotExistError,
    ProfileUnavailableError,
    raise_for_retcode,
)
from enka.gi import Element, GenshinClient, Language

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


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


async def test_error_code(genshin_client: GenshinClient) -> None:
    with pytest.raises(PlayerDoesNotExistError) as exc_info:
        await genshin_client.fetch_showcase("999999999")
    assert exc_info.value.code == "not_found"
    assert exc_info.value.message


def test_profile_unavailable_error() -> None:
    with pytest.raises(ProfileUnavailableError) as exc_info:
        raise_for_retcode(404, "profile_unavailable", "Profile unavailable.")
    assert exc_info.value.code == "profile_unavailable"

    with pytest.raises(GatewayTimeoutError):
        raise_for_retcode(504, "upstream_timeout")


class GatewayTimeoutResponse:
    status = 504

    async def json(self, **_: Any) -> dict[str, str]:
        return {"code": "upstream_timeout", "message": "Timed out."}


@pytest.mark.parametrize("max_retries", [0, 2])
async def test_gateway_timeout_retries(monkeypatch: pytest.MonkeyPatch, max_retries: int) -> None:
    calls = 0

    @contextlib.asynccontextmanager
    async def get(*_: Any) -> AsyncGenerator[GatewayTimeoutResponse]:
        nonlocal calls
        calls += 1
        yield GatewayTimeoutResponse()

    async with GenshinClient(max_retries=max_retries) as client:
        monkeypatch.setattr(aiohttp.ClientSession, "get", get)
        with pytest.raises(GatewayTimeoutError):
            await client.fetch_showcase("901211014")

    assert calls == max_retries + 1


async def test_profile_unavailable_showcase(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("782651148")
        assert showcase.profile_unavailable
        assert showcase.player.nickname == "???"
        assert showcase.characters

        with pytest.raises(ProfileUnavailableError):
            await genshin_client.fetch_showcase("782651148", info_only=True)


async def test_no_element_traveler(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await genshin_client.fetch_showcase("828107378")
        traveler = next(c for c in showcase.characters if c.name == "Traveler")
        assert traveler.element is Element.NONE


async def test_no_element_manekin(genshin_client: GenshinClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await genshin_client.fetch_showcase("753961395")


async def test_stale_assets(genshin_client: GenshinClient, monkeypatch: pytest.MonkeyPatch) -> None:
    assets = genshin_client._assets
    updates: list[AssetData] = []

    async def update(self: AssetData, _: Any) -> None:  # ruff: ignore[unused-async]
        updates.append(self)

    with contextlib.suppress(GameMaintenanceError):
        raw = await genshin_client.fetch_showcase("901211014", raw=True)
        name = genshin_client.parse_showcase(raw).characters[0].artifacts[0].name
        artifact = next(e for e in raw["avatarInfoList"][0]["equipList"] if "reliquary" in e)
        artifact["itemId"] = 99999

        async def request(*_: Any) -> dict[str, Any]:  # ruff: ignore[unused-async]
            return raw

        monkeypatch.setattr(BaseClient, "_request", request)
        monkeypatch.setattr(AssetData, "update", update)
        monkeypatch.setattr(assets, "updated_at", None)

        async with GenshinClient(auto_update_assets=False) as client:
            showcase = await client.fetch_showcase("901211014")
        assert showcase.characters[0].artifacts[0].name == name
        assert not updates

        await genshin_client.fetch_showcase("901211014")
        assert len(updates) == len(assets._assets)

        # The artifact is still missing, but assets were just refreshed
        await genshin_client.fetch_showcase("901211014")
        assert len(updates) == len(assets._assets)
