"""
FastAPI application for Track Tracker.

This module provides REST API endpoints for accessing track data.

Run with:
    uvicorn app.api.api:app --reload
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .config import APP_CONFIG, CORS_CONFIG
from ..db.place_holder_users import (
    fake_users_db,
)  # This is a placeholder just so I could test the OAuth stuff
from ..db.query import get_library_stats, get_top_tracks, get_track_snapshots, get_track_stats
from ..db.session import get_db
from .models import (
    TrackGrowthStats,
    TrackListResponse,
    TrackSnapshotsResponse,
    UserInDB,
)

# Create FastAPI app instance
app = FastAPI(**APP_CONFIG)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS middleware - allows frontend to call this API
app.add_middleware(CORSMiddleware, **CORS_CONFIG)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Track Tracker API is running"}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = form_data.password
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/test/")
async def test(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.get("/tracks", response_model=TrackListResponse)
def list_tracks(
    q: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    List tracks ranked by weekly stream growth.

    Optional ?q= searches track name and primary artist name (case-insensitive).
    Optional ?limit= caps the result count (default 50).
    """
    tracks = get_top_tracks(session=db, limit=limit, search=q)
    lib = get_library_stats(session=db)
    return {"tracks": tracks, "count": len(tracks), "total": lib["total_tracks"], "total_streams": lib["total_streams"]}


@app.get("/tracks/{track_id}/snapshots", response_model=TrackSnapshotsResponse)
def track_snapshots(track_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Return snapshot history for a track over the past `days` days."""
    snaps = get_track_snapshots(track_id, session=db, days=days)
    return {"track_id": track_id, "snapshots": snaps}


@app.get("/tracks/{track_id}/stats", response_model=TrackGrowthStats)
def track_stats(track_id: int, db: Session = Depends(get_db)):
    """
    Return stream count growth stats and appearance count for a single track.

    Growth windows: day, week, month, year, all_time.
    Windows with no historical baseline return null values.
    """
    stats = get_track_stats(track_id, session=db)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Track {track_id} not found")
    return stats
