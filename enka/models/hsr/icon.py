__all__ = ("CharacterIcon", "LightConeIcon")


class CharacterIcon:
    """HSR character icon."""

    def __init__(self, character_id: int) -> None:
        self._id = character_id

    @property
    def round(self) -> str:
        """Character icon in round shape.

        e.g. https://enka.network/ui/hsr/SpriteOutput/AvatarRoundIcon/1001.png
        """
        return f"https://enka.network/ui/hsr/SpriteOutput/AvatarRoundIcon/{self._id}.png"

    @property
    def gacha(self) -> str:
        """Character gacha splash art.

        e.g. https://enka.network/ui/hsr/SpriteOutput/AvatarDrawCard/1001.png
        """
        return f"https://enka.network/ui/hsr/SpriteOutput/AvatarDrawCard/{self._id}.png"

    @property
    def card(self) -> str:
        """Character icon in card shape.

        Provided by Project Yatta.
        e.g. https://api.yatta.top/hsr/assets/UI//avatar/medium/1001.png
        """
        return f"https://api.yatta.top/hsr/assets/UI//avatar/medium/{self._id}.png"


class LightConeIcon:
    """HSR light cone icon."""

    def __init__(self, light_cone_id: int) -> None:
        self._id = light_cone_id

    @property
    def image(self) -> str:
        """Light cone icon image.

        e.g. https://enka.network/ui/hsr/SpriteOutput/LightConeFigures/20000.png
        """
        return f"https://enka.network/ui/hsr/SpriteOutput/LightConeFigures/{self._id}.png"

    @property
    def item(self) -> str:
        """Light cone icon item.

        Provided by Project Yatta.
        e.g. https://api.yatta.top/hsr/assets/UI//equipment/medium/20000.png
        """
        return f"https://api.yatta.top/hsr/assets/UI//equipment/medium/{self._id}.png"
