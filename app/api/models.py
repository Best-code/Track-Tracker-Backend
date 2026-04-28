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


class TrackListItem(BaseModel):
    """Single track entry returned by GET /tracks."""

    track_id: int
    track_name: str | None
    artist_name: str | None
    image_url: str | None
    total_streams: int | None
    daily_streams_change: int | None
    weekly_growth_percent: float | None
    rank: int


class TrackListResponse(BaseModel):
    tracks: list[TrackListItem]
    count: int
    total: int
    total_streams: int


class SnapshotPoint(BaseModel):
    recorded_at: str
    streams: int | None


class TrackSnapshotsResponse(BaseModel):
    track_id: int
    snapshots: list[SnapshotPoint]
