from typing import Dict

from pydantic import BaseModel, Field, field_validator

__all__ = ("GenshinPlayer",)


class GenshinPlayer(BaseModel):
    """
    Represents a Genshin Impact player.

    Attributes
    ----------
    achievements: :class:`int`
        The number of achievements the player has.
    level: :class:`int`
        The player's level.
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
    profile_picture_avatar_id: :class:`int`
        The player's profile picture avatar ID.
    """

    achievements: int = Field(alias="finishAchievementNum")
    level: int
    namecard_id: int = Field(alias="nameCardId")
    namecard_icon: str = Field(None)
    nickname: str
    signature: str = Field("")
    abyss_floor: int = Field(0, alias="towerFloorIndex")
    abyss_level: int = Field(0, alias="towerLevelIndex")
    world_level: int = Field(0, alias="worldLevel")
    profile_picture_avatar_id: int = Field(alias="profilePicture")

    @field_validator("profile_picture_avatar_id", mode="before")
    @classmethod
    def _extract_avatar_id(cls, v: Dict[str, int]) -> int:
        return v.get("avatarId", v.get("id", 0))
