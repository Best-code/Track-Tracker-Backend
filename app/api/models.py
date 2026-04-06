from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class GrowthWindow(BaseModel):
    """Absolute and percentage change for a single time window."""

    absolute: int | None
    percent: float | None


class TrackGrowthStats(BaseModel):
    """
    Growth stats for a track derived from its TrackSnapshot history.

    growth keys: "day", "week", "month", "year", "all_time"
    Windows with no historical baseline return null for both fields.
    """

    track_id: int
    track_name: str | None
    spotify_id: str | None
    snapshot_count: int
    latest_streams: int | None
    latest_recorded_at: str | None
    growth: dict[str, GrowthWindow]
