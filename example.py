import asyncio

import enka


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

        for showcase_character in response.player.showcase_characters:
            print("\n==================\n")
            print("Level:", showcase_character.level)
            if showcase_character.costuime_icon:
                print("Costume icon:", showcase_character.costuime_icon.gacha)

        # for character in response.characters:
        #     print("\n==================\n")
        #     print(character.name)
        #     print("Level:", character.level)
        #     print("Element:", character.element.name)
        #     print("Constellation:", len(character.constellations))
        #     print("Weapon:", character.weapon.name)
        #     print("Weapon level:", character.weapon.level)
        #     print("Weapon refinement:", character.weapon.refinement)
        #     print("Side icon:", character.icon.side)
        #     print("Circle icon:", character.icon.circle)
        #     print("Gacha art:", character.icon.gacha)
        #     print("Front icon:", character.icon.front)


asyncio.run(main())
