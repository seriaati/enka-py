from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

__all__ = ("GenshinPlayer",)


class ShowcaseCharacter(BaseModel):
    """
    Represents a showcase character.

    Attributes
    ----------
    id: :class:`int`
        The character's ID.
    level: :class:`int`
        The character's level.
    costume_id: Optional[:class:`int`]
        The character's costume's ID.
    costume_side_icon: Optional[:class:`str`]
        The character's costume's side icon.
        Example: https://enka.network/ui/UI_AvatarIcon_Side_Ambor.png
    costume_icon: Optional[:class:`str`]
        The character's costume's icon.
        Example: https://enka.network/ui/UI_AvatarIcon_Ambor.png
    costume_art: Optional[:class:`str`]
        The character's costume's art.
        Example: https://enka.network/ui/UI_Gacha_AvatarImg_Ambor.png
    """

    id: int = Field(alias="avatarId")
    level: int
    costume_id: Optional[int] = Field(None, alias="costumeId")
    costume_side_icon: Optional[str] = Field(None)

    @property
    def costume_icon(self) -> Optional[str]:
        if self.costume_side_icon is None:
            return None
        return self.costume_side_icon.replace("Side_", "")

    @property
    def costume_art(self) -> Optional[str]:
        if self.costume_side_icon is None:
            return None
        return self.costume_side_icon.replace("AvatarIcon_Side", "Costume")


class GenshinPlayer(BaseModel):
    """
    Represents a Genshin Impact player.

    Attributes
    ----------
    achievements: :class:`int`
        The number of completed achievements.
    level: :class:`int`
        The player's adventure level.
    namecard_id: :class:`int`
        The player's namecard's ID.
    namecard_icon: :class:`str`
        The player's namecard's icon.
    nickname: :class:`str`
        The player's nickname.
    signature: :class:`str`
        The player's signature.
    abyss_floor: :class:`int`
        The player's Spiral Abyss floor.
    abyss_level: :class:`int`
        The player's Spiral Abyss level.
    world_level: :class:`int`
        The player's world level.
    profile_picture_id: :class:`int`
        The player's profile picture's ID.
    profile_picture_icon: :class:`str`
        The player's profile picture's icon.
    showcase_characters: List[:class:`ShowcaseCharacter`]
        The player's showcase characters.
    """

    achievements: int = Field(alias="finishAchievementNum")
    level: int
    namecard_id: int = Field(alias="nameCardId")
    namecard_icon: str = Field(None)
    nickname: str
    signature: Optional[str] = Field(None)
    abyss_floor: int = Field(0, alias="towerFloorIndex")
    abyss_level: int = Field(0, alias="towerLevelIndex")
    world_level: int = Field(0, alias="worldLevel")
    profile_picture_id: int = Field(alias="profilePicture")
    profile_picture_icon: str = Field(None)
    showcase_characters: List[ShowcaseCharacter] = Field([], alias="showAvatarInfoList")

    @field_validator("profile_picture_id", mode="before")
    def _extract_avatar_id(cls, v: Dict[str, int]) -> int:
        return v["avatarId"]
