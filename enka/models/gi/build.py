from pydantic import BaseModel, Field

from .character import Character


class Build(BaseModel):
    """Represents a Genshin Impact build.

    Attributes:
        id (int): The build's ID.
        name (str): The build's name.
        order (int): The build's order.
        live (bool): Whether the build is live.
        character_id (int): The build's character ID.
        character (:class:`Character`): The build's character data.
    """

    id: int
    name: str
    order: int
    live: bool
    character_id: int = Field(alias="avatar_id")
    character: Character = Field(alias="avatar_data")
