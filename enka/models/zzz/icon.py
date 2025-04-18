from __future__ import annotations

from pydantic import BaseModel, computed_field

__all__ = ("AgentIcon",)

ENKA_BASE = "https://enka.network/ui/zzz/{filename}.png"
HAKUSHIN_BASE = "https://api.hakush.in/zzz/UI/{filename}.webp"


class AgentIcon(BaseModel):
    """ZZZ agent icon."""

    filename: str  # Should be "IconRoleXX", parsed from "image" property.

    @computed_field
    @property
    def round(self) -> str:
        """Character's icon in circle/rounded shape.

        e.g. https://enka.network/ui/zzz/IconRoleCircle13.png
        """
        return ENKA_BASE.format(filename=self.filename.replace("IconRole", "IconRoleCircle"))

    @computed_field
    @property
    def image(self) -> str:
        """Character's full image.

        e.g. https://enka.network/ui/zzz/IconRole13.png
        """
        return ENKA_BASE.format(filename=self.filename)

    @computed_field
    @property
    def select(self) -> str:
        """Character's icon in the select screen.

        e.g. https://api.hakush.in/zzz/UI/IconRoleSelect13.webp
        """
        return HAKUSHIN_BASE.format(filename=self.filename.replace("IconRole", "IconRoleSelect"))
