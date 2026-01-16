"""
FastAPI application for Track Tracker.

This module provides REST API endpoints for accessing track data.

Run with:
    uvicorn app.api.api:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.database import get_db, Base, get_engine
from app.db.models import Track, TrackSnapshot

@asynccontextmanager
async def lifespan(app:  FastAPI):
    """Create database tables on startup if they don't exist."""
    Base.metadata.create_all(bind=get_engine())
    yield

# Create FastAPI app instance
app = FastAPI(
    title="Track Tracker API",
    description="API for tracking Spotify track metrics over time",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware - allows frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Track Tracker API is running"}


@app.get("/tracks")
def get_tracks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all tracks with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    tracks = db.query(Track).offset(skip).limit(limit).all()
    return tracks


@app.get("/tracks/{track_id}")
def get_track(track_id: str, db: Session = Depends(get_db)):
    """
    Get a specific track by its Spotify ID.

    - **track_id**: The Spotify track ID
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


@app.get("/tracks/{track_id}/snapshots")
def get_track_snapshots(track_id: str, db: Session = Depends(get_db)):
    """
    Get all snapshots for a specific track.

    - **track_id**: The Spotify track ID
    """
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    snapshots = (
        db.query(TrackSnapshot)
        .filter(TrackSnapshot.track_id == track_id)
        .order_by(TrackSnapshot.snapshot_date.desc())
        .all()
    )
    return snapshots


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get basic statistics about the tracked data."""
    track_count = db.query(Track).count()
    snapshot_count = db.query(TrackSnapshot).count()

    return {
        "total_tracks": track_count,
        "total_snapshots": snapshot_count,
    }
