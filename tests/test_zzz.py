import contextlib

import pytest

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
