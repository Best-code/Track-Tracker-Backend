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

from .config import APP_CONFIG, CORS_CONFIG
from ..db.place_holder_users import (
    fake_users_db,
)  # This is a placeholder just so I could test the OAuth stuff
from .models import UserInDB

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
