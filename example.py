import asyncio

import enka
from enka.enums.enums import FightPropType

FIGHT_PROPS_TO_SHOW = (
    FightPropType.FIGHT_PROP_MAX_HP,
    FightPropType.FIGHT_PROP_CUR_ATTACK,
    FightPropType.FIGHT_PROP_CUR_DEFENSE,
    FightPropType.FIGHT_PROP_ELEMENT_MASTERY,
    FightPropType.FIGHT_PROP_CRITICAL,
    FightPropType.FIGHT_PROP_CRITICAL_HURT,
    FightPropType.FIGHT_PROP_CHARGE_EFFICIENCY,
)


async def main() -> None:  # noqa: C901
    async with enka.EnkaAPI() as api:
        # Update assets
        # await api.update_assets()

        try:
            response = await api.fetch_showcase(831335713)
        except enka.exceptions.PlayerDoesNotExistError:
            return print("Player does not exist.")
        except enka.exceptions.GameMaintenanceError:
            return print("Game is in maintenance.")

        print("Name:", response.player.nickname)
        print("Level:", response.player.level)
        print("Achievements:", response.player.achievements)
        print("Namecard:", response.player.namecard.full)
        print("Profile picture side icon:", response.player.profile_picture_icon.side)

        for character in response.characters:
            print("\n===============================\n")
            print(
                f"Lv. {character.level}/{character.max_level} {character.name} (C{character.constellations_unlocked})"
            )
            print(f"Rarity: {character.rarity} ★")
            print("Element:", character.element.name.title())
            print("Side icon:", character.icon.side)
            print(f"Talent levels: {'/'.join(str(talent.level) for talent in character.talents)}")
            if character.namecard is not None:
                print("Namecard:", character.namecard.full)

            if character.costume is not None:
                print("Costume side icon:", character.costume.icon.side)

            weapon = character.weapon
            print("\nWeapon:")
            print(f"Lv. {weapon.level}/{weapon.max_level} {weapon.name} (R{weapon.refinement})")
            print(f"Rarity: {weapon.rarity} ★")
            for stat in weapon.stats:
                print(stat.name, stat.formatted_value)

            print("\nStats:")
            for stat_type, stat in character.stats.items():
                if stat_type in FIGHT_PROPS_TO_SHOW:
                    print(stat.name, stat.formatted_value)
            dmg_bonus = character.highest_dmg_bonus_stat
            print(dmg_bonus.name, dmg_bonus.formatted_value)

            print("\nArtifacts:")
            for artifact in character.artifacts:
                main_stat = artifact.main_stat
                print(
                    f"Lv. {artifact.level} {artifact.name}: {main_stat.name} {main_stat.formatted_value}"
                )
                for substat in artifact.sub_stats:
                    print(f"- {substat.name} {substat.formatted_value}")
                print("")


asyncio.run(main())
