import contextlib
from typing import Any

import pytest

from enka.assets.data import AssetData
from enka.clients.base import BaseClient
from enka.errors import GameMaintenanceError, PlayerDoesNotExistError
from enka.zzz import Gender, Language, ZZZClient


async def test_update_assets(zzz_client: ZZZClient) -> None:
    await zzz_client.update_assets()


async def test_fetch_showcase(zzz_client: ZZZClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await zzz_client.fetch_showcase("1300025292")


@pytest.mark.parametrize("lang", list(Language))
async def test_langs(lang: Language) -> None:
    async with ZZZClient(lang) as api:
        with contextlib.suppress(GameMaintenanceError):
            await api.fetch_showcase("1300025292")


async def test_raw_and_parse(zzz_client: ZZZClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        raw = await zzz_client.fetch_showcase("1300025292", raw=True)
        zzz_client.parse_showcase(raw)


async def test_not_exist_player(zzz_client: ZZZClient) -> None:
    with pytest.raises(PlayerDoesNotExistError):
        await zzz_client.fetch_showcase("1000000000")


async def test_fetch_builds(zzz_client: ZZZClient) -> None:
    await zzz_client.fetch_builds({"hash": "2rfpm9", "username": "CharaAni"})


async def test_rupture_character(zzz_client: ZZZClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await zzz_client.fetch_showcase("1309335571")


def test_gendered_title_text_defaults_to_male() -> None:
    client = ZZZClient()
    parsed = client._parse_gendered_text("Wahre{M#r} Schüler{F#in} des Yunkuigipfels")
    assert parsed == "Wahrer Schüler des Yunkuigipfels"


@pytest.mark.parametrize(
    ("gender", "expected"),
    [
        (Gender.MALE, "Wahrer Schüler des Yunkuigipfels"),
        (Gender.FEMALE, "Wahre Schülerin des Yunkuigipfels"),
    ],
)
def test_gendered_title_text_parsing(gender: Gender, expected: str) -> None:
    client = ZZZClient(gender=gender)
    parsed = client._parse_gendered_text("Wahre{M#r} Schüler{F#in} des Yunkuigipfels")
    assert parsed == expected


async def test_stale_assets(zzz_client: ZZZClient, monkeypatch: pytest.MonkeyPatch) -> None:
    assets = zzz_client._assets
    updates: list[AssetData] = []

    async def update(self: AssetData, _: Any) -> None:  # ruff: ignore[unused-async]
        updates.append(self)

    with contextlib.suppress(GameMaintenanceError):
        raw = await zzz_client.fetch_showcase("1300025292", raw=True)
        agents = raw["PlayerInfo"]["ShowcaseDetail"]["AvatarList"]
        unknown_engine, unknown_discs, unknown_agent, known = [
            i for i, agent in enumerate(agents) if len(agent["EquippedList"]) >= 2
        ][:4]
        agents[unknown_agent]["Id"] = 9999
        agents[unknown_engine]["Weapon"]["Id"] = 99999
        for disc in agents[unknown_discs]["EquippedList"][:2]:
            disc["Equipment"]["Id"] = 99999

        async def request(*_: Any) -> dict[str, Any]:  # ruff: ignore[unused-async]
            return raw

        monkeypatch.setattr(BaseClient, "_request", request)
        monkeypatch.setattr(AssetData, "update", update)
        monkeypatch.setattr(assets, "updated_at", None)

        async with ZZZClient(auto_update_assets=False) as client:
            showcase = await client.fetch_showcase("1300025292")
        assert showcase.agents[unknown_engine].stats == {}
        assert showcase.agents[unknown_discs].stats == {}
        assert showcase.agents[known].stats
        assert not updates

        agent = showcase.agents[unknown_agent]
        assert agent.stats == {}
        assert agent.w_engine is not None
        assert agent.w_engine.name
        assert agent.discs[0].set_name

        await zzz_client.fetch_showcase("1300025292")
        assert len(updates) == len(assets._assets)

        # The gear is still missing, but assets were just refreshed
        await zzz_client.fetch_showcase("1300025292")
        assert len(updates) == len(assets._assets)
