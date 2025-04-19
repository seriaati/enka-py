from __future__ import annotations

__all__ = ("CharacterIcon", "LightConeIcon")


from pydantic import BaseModel, computed_field


class CharacterIcon(BaseModel):
    """Represents a HSR character icon.

    Attributes:
        character_id: The character's ID.
    """

    character_id: int

    @computed_field
    @property
    def round(self) -> str:
        """Character icon in round shape.

        e.g. https://enka.network/ui/hsr/SpriteOutput/AvatarRoundIcon/1001.png
        """
        return f"https://enka.network/ui/hsr/SpriteOutput/AvatarRoundIcon/{self.character_id}.png"

    @computed_field
    @property
    def gacha(self) -> str:
        """Character gacha splash art.

        e.g. https://enka.network/ui/hsr/SpriteOutput/AvatarDrawCard/1001.png
        """
        return f"https://enka.network/ui/hsr/SpriteOutput/AvatarDrawCard/{self.character_id}.png"

    @computed_field
    @property
    def card(self) -> str:
        """Character icon in card shape.

        Provided by Project Yatta.
        e.g. https://api.yatta.top/hsr/assets/UI//avatar/medium/1001.png
        """
        return f"https://api.yatta.top/hsr/assets/UI//avatar/medium/{self.character_id}.png"


class LightConeIcon(BaseModel):
    """Represents a HSR light cone icon.

    Attributes:
        light_cone_id: The light cone's ID.
    """

    light_cone_id: int

    @computed_field
    @property
    def image(self) -> str:
        """Light cone icon image.

        e.g. https://enka.network/ui/hsr/SpriteOutput/LightConeFigures/20000.png
        """
        return f"https://enka.network/ui/hsr/SpriteOutput/LightConeFigures/{self.light_cone_id}.png"

    @computed_field
    @property
    def item(self) -> str:
        """Light cone icon item.

        Provided by Project Yatta.
        e.g. https://api.yatta.top/hsr/assets/UI//equipment/medium/20000.png
        """
        return f"https://api.yatta.top/hsr/assets/UI//equipment/medium/{self.light_cone_id}.png"
