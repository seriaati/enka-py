from pydantic import BaseModel, Field, field_validator

__all__ = ("Player", "PlayerStats")


class PlayerStats(BaseModel):
    """Represents the statistics of a HSR player.

    Attributes:
        achievement_count (int): The number of achievements the player has.
        light_cone_count (int): The number of light cones the player has.
        character_count (int): The number of characters the player has.
        max_simulated_universe_world (int, optional): The maximum world completed in the simulated universe.
        book_count (int, optional): The number of books the player has. (Added in game version 2.2)
        relic_count (int, optional): The number of relics the player has. (Added in game version 2.2)
        music_count (int, optional): The number of music tracks the player has. (Added in game version 2.2)
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
        nickname (str): The player's nickname.
        signature (str): The player's signature.
        uid (int): The player's UID.
        level (int): The player's level.
        equilibrium_level (int): The player's equilibrium level.
        friend_count (int): The number of friends the player has.
        stats (:class:`PlayerStats`): The player's statistics.
    """

    nickname: str
    signature: str = ""
    uid: int
    level: int
    equilibrium_level: int = Field(0, alias="worldLevel")
    friend_count: int = Field(0, alias="friendCount")
    stats: PlayerStats = Field(alias="recordInfo")

    # The following fields are added in post-processing
    icon: str = Field(None, alias="headIcon")

    @field_validator("icon", mode="before")
    def _stringify_icon(cls, value: int) -> str:
        return str(value)
