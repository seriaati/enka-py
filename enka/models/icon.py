class Icon:
    def __init__(self, side_icon_ui_path: str, *, is_costume: bool = False) -> None:
        self._side_icon_ui_path = side_icon_ui_path
        self._side_icon = f"https://enka.network/ui/{side_icon_ui_path}.png"
        self._is_costume = is_costume

    @property
    def icon_ui_path(self) -> str:
        """
        The icon UI path of the character.
        e.g. UI_AvatarIcon_Ambor
        """
        return self._side_icon_ui_path.replace("Side_", "")

    @property
    def side(self) -> str:
        """
        The side icon of the character.
        e.g. https://enka.network/ui/UI_AvatarIcon_Side_Ambor.png
        """
        return self._side_icon

    @property
    def circle(self) -> str:
        """
        The circle (round) icon of the character.
        e.g. https://enka.network/ui/UI_AvatarIcon_Ambor_Circle.png
        """
        return self._side_icon.replace("Side_", "").replace(".png", "_Circle.png")

    @property
    def gacha(self) -> str:
        """
        The gacha art of the character.
        e.g. https://enka.network/ui/UI_Gacha_AvatarImg_Ambor.png
        """
        return self._side_icon.replace(
            "AvatarIcon_Side", "Costume" if self._is_costume else "Gacha_AvatarImg"
        )

    @property
    def front(self) -> str:
        """
        The front icon of the character.
        e.g. https://enka.network/ui/UI_AvatarIcon_Ambor.png
        """
        return self._side_icon.replace("Side_", "")


class Namecard:
    def __init__(self, ui_path: str) -> None:
        self._ui_path = ui_path

    @property
    def icon_ui_path(self) -> str:
        """
        The namecard UI path.
        e.g. UI_NameCardPic_Feiyan_P
        """
        return self._ui_path.replace("NamrCardIcon", "NameCardPic").replace("_P", "0")

    @property
    def icon(self) -> str:
        """
        The namecard's icon.
        e.g. https://enka.network/ui/UI_NameCardIcon_0.png
        """
        return f"https://enka.network/ui/{self.icon_ui_path}.png"

    @property
    def full(self) -> str:
        """
        The full namecard.
        e.g. https://enka.network/ui/UI_NameCardPic_0_P.png
        """
        return f"https://enka.network/ui/UI_NameCardPic_{self._ui_path}_P.png"
