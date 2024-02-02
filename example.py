import asyncio

import enka
from enka.enums import FightProp


async def main() -> None:
    async with enka.EnkaAPI() as api:
        try:
            response = await api.fetch_showcase(738081787)
        except enka.exceptions.PlayerDoesNotExistError:
            return print("Player does not exist.")
        except enka.exceptions.GameMaintenanceError:
            return print("Game is in maintenance.")

        print("Name:", response.player.nickname)
        print("Level:", response.player.level)
        print("Achievements:", response.player.achievements)
        print("Namecard:", response.player.namecard.full)

        for character in response.characters:
            print("\n==================\n")
            print(character.name)
            print("Level:", character.level)
            print("Element:", character.element.name)
            print("Constellation:", len(character.constellations))
            print("Weapon:", character.weapon.name)
            print("Weapon level:", character.weapon.level)
            print("Weapon refinement:", character.weapon.refinement)
            print("Side icon:", character.icon.side)
            print("HP:", round(character.stats[FightProp.FIGHT_PROP_CUR_HP].value))
            print("Attack:", round(character.stats[FightProp.FIGHT_PROP_CUR_ATTACK].value))
            print(
                "Defense:",
                round(character.stats[FightProp.FIGHT_PROP_CUR_DEFENSE].value),
            )
            print(
                "Energy recharge:",
                f"{round(character.stats[FightProp.FIGHT_PROP_CHARGE_EFFICIENCY].value, 1)}%",
            )


asyncio.run(main())
