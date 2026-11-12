import contextlib
from typing import Any

import pytest

from enka.constants.hsr import DMG_BONUS_PROPS
from enka.errors import GameMaintenanceError
from enka.hsr import Element, HSRClient, Language
from enka.models.hsr import ShowcaseResponse


async def test_update_assets(hsr_client: HSRClient) -> None:
    await hsr_client.update_assets()


async def test_fetch_showcase(hsr_client: HSRClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await hsr_client.fetch_showcase("809162009")


@pytest.mark.skip(reason="Can't find a trailblazer showcase for now.")
async def test_trailblazer_showcase(hsr_client: HSRClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await hsr_client.fetch_showcase("123456786")


@pytest.mark.parametrize("lang", list(Language))
async def test_langs(lang: Language) -> None:
    async with HSRClient(lang) as api:
        with contextlib.suppress(GameMaintenanceError):
            await api.fetch_showcase("809162009")


async def test_low_level_acc(hsr_client: HSRClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await hsr_client.fetch_showcase("829702635")


async def test_owner_and_builds(hsr_client: HSRClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        showcase = await hsr_client.fetch_showcase("809162009")
        assert showcase.owner is not None
        await hsr_client.fetch_builds(showcase.owner)


async def test_fetch_builds(hsr_client: HSRClient) -> None:
    await hsr_client.fetch_builds({"hash": "2A2VAE", "username": "seria_ati"})


async def test_raw_and_parse(hsr_client: HSRClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        raw = await hsr_client.fetch_showcase("809162009", raw=True)
        hsr_client.parse_showcase(raw)


def test_4_7_fields() -> None:
    showcase = ShowcaseResponse.model_validate(
        {
            "detailInfo": {
                "uid": 702829957,
                "nickname": "Proxymer",
                "level": 70,
                "birthday": 229,
                "personalCardId": 253000,
                "recordInfo": {"avatarCount": 48},
                "avatarDetailList": [
                    {
                        "avatarId": 1213,
                        "level": 80,
                        "promotion": 6,
                        "rank": 1,
                        "skillTreeList": [],
                        "exRankList": [121301],
                    }
                ],
            },
            "uid": "702829957",
            "region": "EU",
        }
    )
    assert showcase.region == "EU"
    assert showcase.player.birthday == 229
    assert showcase.player.personal_card_id == 253000
    eidolon = showcase.characters[0].affinitive_eidolons[0]
    assert eidolon.id == 121301
    assert eidolon.icon.endswith("Avatar/1213/SkillIcon_1213_ExRank01.png")
    assert eidolon.unlocked


async def test_empty_substat_list(hsr_client: HSRClient) -> None:
    with contextlib.suppress(GameMaintenanceError):
        await hsr_client.fetch_showcase("800724088")


def _stale_asset_showcase() -> dict[str, Any]:
    light_cone = {
        "tid": 99999,
        "level": 80,
        "promotion": 6,
        "rank": 1,
        "_flat": {"name": 0, "props": [{"type": "BaseHP", "value": 1}]},
    }
    relics = [
        {
            "tid": 99990 + i,
            "type": i,
            "mainAffixId": 1,
            "_flat": {"props": [{"type": "HPDelta", "value": 1}]},
        }
        for i in (1, 2)
    ]
    return {
        "detailInfo": {
            "uid": 702829957,
            "nickname": "Proxymer",
            "level": 70,
            "headIcon": 999999,
            "recordInfo": {"avatarCount": 48},
            "avatarDetailList": [
                {
                    "avatarId": 1213,
                    "level": 80,
                    "promotion": 6,
                    "skillTreeList": [],
                    "equipment": light_cone,
                    "relicList": relics,
                },
                {
                    "avatarId": 9999,
                    "level": 80,
                    "promotion": 6,
                    "skillTreeList": [],
                    "equipment": light_cone,
                },
                {"avatarId": 1213, "level": 80, "promotion": 6, "skillTreeList": []},
            ],
        },
        "uid": "702829957",
    }


def test_stale_assets(hsr_client: HSRClient) -> None:
    showcase = hsr_client.parse_showcase(_stale_asset_showcase())
    unknown_gear, unknown_character, known = showcase.characters

    assert not showcase.player.icon

    assert unknown_gear.name
    assert unknown_gear.stats == {}
    assert unknown_gear.light_cone is not None
    assert unknown_gear.light_cone.icon.light_cone_id == 99999

    assert unknown_character.stats == {}
    assert unknown_character.light_cone is not None
    assert unknown_character.light_cone.icon.light_cone_id == 99999

    assert known.stats
    assert known.element != Element.PHYSICAL
    assert known.highest_dmg_bonus_stat.type == DMG_BONUS_PROPS[known.element]

    for character in showcase.characters:
        assert character.highest_dmg_bonus_stat.type in DMG_BONUS_PROPS.values()
        character.model_dump()
