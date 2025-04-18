from __future__ import annotations

from typing import Literal

RARITY_MAP: dict[int, Literal["S", "A", "B"]] = {4: "S", 3: "A", 2: "B"}

ICON_FOLDER = "https://raw.githubusercontent.com/seriaati/enka-py-assets/refs/heads/main/icons/zzz"
ELEMENT_ICON = f"{ICON_FOLDER}/element/{{element}}.png"
