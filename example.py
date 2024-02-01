import asyncio

import enka


async def main() -> None:
    async with enka.EnkaAPI() as api:
        response = await api.fetch_showcase(901211014)

        print("Name:", response.player.nickname)
        print("Level:", response.player.level)
        print("Achievements:", response.player.achievements)
        print("Namecard:", response.player.namecard_icon)

        for character in response.characters:
            print("\n==================\n")
            print(character.name)
            print("Level:", character.level)
            print("Element:", character.element.name)
            print("Constellation:", len(character.constellations))
            print("Weapon:", character.weapon.name)
            print("Weapon level:", character.weapon.level)
            print("Weapon refinement:", character.weapon.refinement)


asyncio.run(main())
