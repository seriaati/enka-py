from __future__ import annotations

from pydantic import BaseModel

__all__ = ("Owner", "OwnerProfile")


class OwnerProfile(BaseModel):
    """Represents an Enka account owner's profile information.

    Attributes:
        bio (str): The owner's bio.
        avatar (str, optional): The owner's avatar.
    """

    bio: str
    avatar: str | None = None


class Owner(BaseModel):
    """Represents an Enka account owner.

    Attributes:
        hash (str): The owner's hash.
        username (str): The owner's username.
        profile (:class:`OwnerProfile`): The owner's profile information.
        id (int): The owner's ID.
    """

    hash: str
    username: str
    profile: OwnerProfile
    id: int
