from __future__ import annotations

import asyncio

import enka


async def main() -> None:
    async with enka.HSRClient(enka.hsr.Language.TRADITIONAL_CHINESE) as api:
        # Update assets
        await api.update_assets()

        try:
            response = await api.fetch_showcase(809162009)
        except enka.errors.PlayerDoesNotExistError:
            return print("Player does not exist.")
        except enka.errors.GameMaintenanceError:
            return print("Game is in maintenance.")

        print("Name:", response.player.nickname)
        print("Level:", response.player.level)
        print("Equilbrium level:", response.player.equilibrium_level)
        print("Achievements:", response.player.stats.achievement_count)
        print("Light Cones:", response.player.stats.light_cone_count)
        print("Characters:", response.player.stats.character_count)
        print("Profile picture side icon:", response.player.icon)

        for character in response.characters:
            print("\n===============================\n")
            print(
                f"Lv. {character.level}/{character.max_level} {character.name} (E{character.eidolons_unlocked})"
            )
            print(f"Rarity: {character.rarity} ★")
            print("Element:", character.element.name.title())
            print("Path:", character.path.name.title())
            print("Round icon:", character.icon.round)

            lc = character.light_cone
            if lc is not None:
                print("\nLight Cone:")
                print(f"Lv. {lc.level}/{lc.max_level} {lc.name} (S{lc.superimpose})")
                print(f"Rarity: {lc.rarity} ★")
                for stat in lc.stats:
                    print(stat.name, stat.formatted_value)

            print("\nStats:")
            for stat in character.stats.values():
                if stat.value == 0 or stat.type.value in enka.hsr.DMG_BONUS_PROPS.values():
                    continue
                print(stat.name, stat.formatted_value)

            dmg_bonus = character.highest_dmg_bonus_stat
            print(dmg_bonus.name, dmg_bonus.formatted_value)

            print("\nRelics:")
            for relic in character.relics:
                main_stat = relic.main_stat
                print(
                    f"+{relic.level} {relic.set_name}: {main_stat.name} {main_stat.formatted_value}"
                )
                for substat in relic.sub_stats:
                    print(f"- {substat.name} {substat.formatted_value}")
                print()
    return None


if __name__ == "__main__":
    asyncio.run(main())
