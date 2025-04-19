from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

__all__ = ("Player", "PlayerStats")


class PlayerStats(BaseModel):
    """Represents the statistics of a HSR player.

    Attributes:
        achievement_count: The number of achievements the player has.
        light_cone_count: The number of light cones the player has.
        character_count: The number of characters the player has.
        max_simulated_universe_world: The maximum world completed in the simulated universe.
        book_count: The number of books the player has, added in game version 2.2
        relic_count: The number of relics the player has, added in game version 2.2
        music_count: The number of music tracks the player has, added in game version 2.2
    """

    achievement_count: int = Field(0, alias="achievementCount")
    light_cone_count: int = Field(0, alias="equipmentCount")
    character_count: int = Field(alias="avatarCount")
    max_simulated_universe_world: int | None = Field(None, alias="maxRogueChallengeScore")

    # New after game version 2.2
    book_count: int | None = Field(None, alias="bookCount")
    relic_count: int | None = Field(None, alias="relicCount")
    music_count: int | None = Field(None, alias="musicCount")


class Player(BaseModel):
    """Represents a HSR player.

    Attributes:
        nickname: The player's nickname.
        signature: The player's signature.
        uid: The player's UID.
        level: The player's level.
        equilibrium_level: The player's equilibrium level.
        friend_count: The number of friends the player has.
        stats: The player's statistics.
    """

    nickname: str
    signature: str = ""
    uid: int
    level: int
    equilibrium_level: int = Field(0, alias="worldLevel")
    friend_count: int = Field(0, alias="friendCount")
    stats: PlayerStats = Field(alias="recordInfo")

    # The following fields are added in post-processing
    icon: str = Field("", alias="headIcon")

    @field_validator("icon", mode="before")
    @classmethod
    def _stringify_icon(cls, value: int) -> str:
        return str(value)
