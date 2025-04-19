from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from .costume import Costume
from .icon import Icon, Namecard

__all__ = ("Player", "ShowcaseCharacter")


class ShowcaseCharacter(BaseModel):
    """Represents a showcase character.

    Attributes:
        id: The character's ID.
        level: The character's level.
        costume: The character's costume, if any.
        costume_id: The character's costume's ID, if any.
    """

    id: int = Field(alias="avatarId")
    level: int
    costume: Costume | None = None
    costume_id: int | None = Field(None, alias="costumeId")

    model_config = {"arbitrary_types_allowed": True}


class Player(BaseModel):
    """Represents a Genshin Impact player.

    Attributes:
        achievements: The number of completed achievements.
        level: The player's adventure level.
        namecard_id: The player's namecard's ID.
        namecard: The player's namecard.
        nickname: The player's nickname.
        signature: The player's signature.
        abyss_floor: The player's Spiral Abyss floor.
        abyss_level: The player's Spiral Abyss level.
        world_level: The player's world level.
        profile_picture_id: The player's profile picture's ID.
        profile_picture_icon: The player's profile picture's icon.
        showcase_characters: The player's showcase characters.
        max_friendship_character_count: The maximum number of characters with friendship level 10.
        abyss_stars: The number of stars in the Spiral Abyss.
        theater_stars: The number of stars in the Theater Mechanicus.
    """

    achievements: int = Field(0, alias="finishAchievementNum")
    level: int
    namecard_id: int = Field(alias="nameCardId")
    namecard: Namecard = Namecard(ui_path="")
    nickname: str | None = None
    signature: str | None = ""
    abyss_floor: int = Field(0, alias="towerFloorIndex")
    abyss_level: int = Field(0, alias="towerLevelIndex")
    world_level: int = Field(0, alias="worldLevel")
    profile_picture_id: int = Field(alias="profilePicture")
    profile_picture_icon: Icon = Icon(side_icon_ui_path="")
    showcase_characters: list[ShowcaseCharacter] = Field(
        alias="showAvatarInfoList", default_factory=list
    )

    # New fields after v5.0
    max_friendship_character_count: int | None = Field(None, alias="fetterCount")
    abyss_stars: int | None = Field(None, alias="towerStarIndex")
    theater_stars: int | None = Field(None, alias="theaterStarIndex")

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("profile_picture_id", mode="before")
    @classmethod
    def _extract_avatar_id(cls, v: dict[str, int]) -> int:
        if not v:
            return 10000007

        avatar_id = v.get("avatarId", v.get("id"))
        if avatar_id is None:
            msg = f"Cannot find profile picture ID from {v}, maybe there is a new format?"
            raise KeyError(msg)
        return avatar_id
