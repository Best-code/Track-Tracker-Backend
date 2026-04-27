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

- Python 3.14+
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
