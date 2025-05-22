from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel

__all__ = ("Owner", "OwnerProfile")


class OwnerProfile(BaseModel):
    """Represents an Enka account owner's profile information.

    Attributes:
        bio: The owner's bio.
        avatar: The owner's avatar.
    """

    bio: str
    avatar: str | None = None


class Owner(BaseModel):
    """Represents an Enka account owner.

    Attributes:
        hash: The owner's hash.
        username: The owner's username.
        profile: The owner's profile information.
        id: The owner's ID.
    """

    hash: str
    username: str
    profile: OwnerProfile
    id: int


class OwnerInput(TypedDict):
    """This class is used in the `fetch_builds` method.

    Attributes:
        hash: The owner's hash.
        username: The owner's username.
    """

    hash: str
    username: str
