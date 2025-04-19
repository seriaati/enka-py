from __future__ import annotations

__all__ = ("Icon", "Namecard")


from pydantic import BaseModel, computed_field


class Icon(BaseModel):
    """Represents an icon in Genshin Impact.

    Attributes:
        side_icon_ui_path: The side icon UI path of the character.
        is_costume: Whether the icon is for a costume.
    """

    side_icon_ui_path: str
    is_costume: bool = False

    @computed_field
    @property
    def icon_ui_path(self) -> str:
        """The icon UI path of the character.

        e.g. UI_AvatarIcon_Ambor
        """
        return self.side_icon_ui_path.replace("Side_", "")

    @computed_field
    @property
    def side(self) -> str:
        """The side icon of the character.

        e.g. https://enka.network/ui/UI_AvatarIcon_Side_Ambor.png
        """
        return f"https://enka.network/ui/{self.side_icon_ui_path}.png"

    @computed_field
    @property
    def circle(self) -> str:
        """The circle (round) icon of the character.

        e.g. https://enka.network/ui/UI_AvatarIcon_Ambor_Circle.png
        """
        return self.side.replace("Side_", "").replace(".png", "_Circle.png")

    @computed_field
    @property
    def gacha(self) -> str:
        """The gacha art of the character.

        e.g. https://enka.network/ui/UI_Gacha_AvatarImg_Ambor.png
        """
        return self.side.replace(
            "AvatarIcon_Side", "Costume" if self.is_costume else "Gacha_AvatarImg"
        )

    @computed_field
    @property
    def front(self) -> str:
        """The front icon of the character.

        e.g. https://enka.network/ui/UI_AvatarIcon_Ambor.png
        """
        return self.side.replace("Side_", "")


class Namecard(BaseModel):
    """Represents a namecard in Genshin Impact.

    Attributes:
        ui_path: The UI path of the namecard.
    """

    ui_path: str

    @computed_field
    @property
    def icon(self) -> str:
        """The namecard's icon.

        e.g. https://enka.network/ui/UI_NameCardIcon_0.png
        """
        return f"https://enka.network/ui/{self.ui_path.replace('NameCardPic', 'NameCardIcon').replace('_P', '')}.png"

    @computed_field
    @property
    def full(self) -> str:
        """The full namecard.

        e.g. https://enka.network/ui/UI_NameCardPic_0_P.png
        """
        return f"https://enka.network/ui/{self.ui_path}.png"
