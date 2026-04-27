# Track Tracker

A data platform that detects emerging music tracks before they hit mainstream charts by monitoring Spotify playlists and Soundcloud trending data.

## Overview

Track Tracker aggregates signals across music platforms to identify rising songs early. By polling playlist additions and tracking platform momentum, we surface tracks days before they appear on official charts.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Ingestion | Python, Spotify API, Soundcloud API |
| Storage | S3 (raw data), PostgreSQL (processed) |
<!-- | Orchestration | Airflow | -->
| Serving | FastAPI |
| Frontend | Next.JS |
<!-- | Infrastructure | Docker, Terraform, AWS | -->
| Infrastructure | AWS |

## Architecture
```
Spotify API   ──┐
                ├──▶ S3 (raw) ──▶ PostgreSQL ──▶ FastAPI ──▶ Next.JS
Web Scraping ───┘                     
```

## Project Structure
```
track-tracker/
├── app/
│   ├── ingestion/          # API polling scripts
│   ├── processing/         # Data transformation
│   ├── api/                # FastAPI backend
│   └── infrastructure/     # Terraform configs
├── tests/
├── env/
│   └── .env.example        
├── .gitignore
├── pyproject.toml        
├── uv.lock             
└── README.md
```

## Setup

### Prerequisites

- Python 3.12+
- Docker
- AWS CLI configured
- Terraform
- Spotify Developer account

### Installation
### Installation
```bash
# Clone repo
git clone https://github.com/colinpmaloney/track-tracker.git
cd track-tracker-backend

# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set environment variables
cp .env.example .env
# Edit .env with your API credentials

# Run a script 
uv run --env-file env/.env.example python -m app.ingestion.spotify

1. Run playwright install chromium (in backend folder)


uv run playwright install chromium
2. Create the env file — create the folder and file manually:

Create folder: Track-Tracker-Backend-increment-3/env/
Create file: env/.env.development with this content:

DATABASE_URL=postgresql://tracker:tracker_password@localhost:5422/track_tracker
SPOTIFY_CLIENT_ID="id here"
SPOTIFY_CLIENT_SECRET="key here"
SPOTIFY_REDIRECT_URI=https://127.0.0.1:8888/callback

3. Start Docker Desktop — open the Docker Desktop app and wait for the whale icon to show running.

4. Init the database


docker compose up -d db
uv run --env-file env/.env.development python main.py init-db
5. Apply the album cover migration — stamps Alembic to the existing schema, then adds the spotify_album_image_url column:


uv run --env-file env/.env.development alembic stamp a3f82c1e9b47
uv run --env-file env/.env.development alembic upgrade head
6. Run ingestion (expect a TikTok browser window to open — leave it)


uv run --env-file env/.env.development python main.py ingest
Album cover URLs are fetched from Spotify during this step and saved to the DB.

7. Start the API server


uv run --env-file env/.env.development uvicorn app.api.api:app --reload
Verify at http://localhost:8000/docs

8. Create frontend env file — in Track-Tracker-Frontend-Increment-3/, create .env.local:


NEXT_PUBLIC_API_URL=http://localhost:8000
9. Start the frontend (in the frontend folder)


npm run dev
Open http://localhost:3000

Steps 2 and 3 can be done in parallel. Everything else must follow that order. Step 5 must come before 6 — ingest will fail if the column doesn't exist yet.
```

## Environment Variables
```
# AWS
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
S3_RAW_BUCKET=
S3_PROCESSED_BUCKET=

# DATABASE
DATABASE_URL=

# SPOTIFY
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```

## Team

- [Alex Nino] - Back End Engineer
- [Colin Maloney] - Data Engineer
- [Kobus VanSteenburg] - Front End Engineer
- [Samuel Pauley] - Front End Engineer
- [Zachary Kupersmith] - Database / Systems Engineer


## License

MIT
