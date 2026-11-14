from typing import Final

CN_UID_PREFIXES: Final[tuple[str, ...]] = ("1", "2", "5")
# Seconds before API request times out, showcases with an unavailable profile take ~6s
DEFAULT_TIMEOUT: Final[int] = 10
ASSET_REFRESH_COOLDOWN: Final[int] = 3600  # Seconds between automatic asset updates

HSR_API_URL: Final[str] = "https://enka.network/api/hsr/uid/{}"
HSR_BACKUP_API_URL: Final[str] = "https://api.asterity.net/hsr/uid/{}?parse=enka"
GI_API_URL: Final[str] = "https://enka.network/api/uid/{}"
ZZZ_API_URL: Final[str] = "https://enka.network/api/zzz/uid/{}"
PROFILE_API_URL: Final[str] = "https://enka.network/api/profile/{}/hoyos/{}/builds/"
