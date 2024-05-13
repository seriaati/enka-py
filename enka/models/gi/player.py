from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .costume import Costume

from .icon import Icon, Namecard

__all__ = ("Player", "ShowcaseCharacter")


class ShowcaseCharacter(BaseModel):
    """
    Represents a showcase character.

    Attributes:
        id (int): The character's ID.
        level (int): The character's level.
        costume (Optional[Costume]): The character's costume, if any.
        costume_id (Optional[int]): The character's costume's ID, if any.
    """

    id: int = Field(alias="avatarId")
    level: int
    costume: Optional[Costume] = Field(None)
    costume_id: Optional[int] = Field(None, alias="costumeId")

    model_config = {"arbitrary_types_allowed": True}


class Player(BaseModel):
    """Represents a Genshin Impact player.

    Attributes:
        achievements (int): The number of completed achievements.
        level (int): The player's adventure level.
        namecard_id (int): The player's namecard's ID.
        namecard (Namecard): The player's namecard.
        nickname (str): The player's nickname.
        signature (str, optional): The player's signature.
        abyss_floor (int): The player's Spiral Abyss floor.
        abyss_level (int): The player's Spiral Abyss level.
        world_level (int): The player's world level.
        profile_picture_id (int): The player's profile picture's ID.
        profile_picture_icon (Icon): The player's profile picture's icon.
        showcase_characters (List[ShowcaseCharacter]): The player's showcase characters.
    """

    achievements: int = Field(0, alias="finishAchievementNum")
    level: int
    namecard_id: int = Field(alias="nameCardId")
    namecard: Namecard = Field(None)
    nickname: str
    signature: Optional[str] = Field(None)
    abyss_floor: int = Field(0, alias="towerFloorIndex")
    abyss_level: int = Field(0, alias="towerLevelIndex")
    world_level: int = Field(0, alias="worldLevel")
    profile_picture_id: int = Field(alias="profilePicture")
    profile_picture_icon: Icon = Field(None)
    showcase_characters: List[ShowcaseCharacter] = Field([], alias="showAvatarInfoList")

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("profile_picture_id", mode="before")
    def _extract_avatar_id(cls, v: Dict[str, int]) -> int:
        avatar_id = v.get("avatarId", v.get("id", None))
        if avatar_id is None:
            raise KeyError("Can't find profile picture ID, maybe there is a new format?")
        return avatar_id
