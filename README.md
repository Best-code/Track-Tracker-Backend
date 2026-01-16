# Track Tracker

A data platform that detects emerging music tracks before they hit mainstream charts by monitoring Spotify playlists and Soundcloud trending data.

## Overview

Track Tracker aggregates signals across music platforms to identify rising songs early. By polling playlist additions and tracking cross-platform momentum, we surface tracks days before they appear on official charts.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Ingestion | Python, Spotify API, Soundcloud API |
| Storage | S3 (raw data), PostgreSQL (processed) |
| Orchestration | Airflow |
| Serving | FastAPI |
| Frontend | Next.JS |
| Infrastructure | Docker, Terraform, AWS |

## Architecture
```
Spotify API ──┐
              ├──▶ S3 (raw) ──▶ PostgreSQL ──▶ FastAPI ──▶ Next.JS
Soundcloud ───┘                     
```

## Project Structure
```
track-tracker/
├── app/
│   ├── ingestion/          # API polling scripts
│   ├── processing/         # Data transformation
│   ├── api/                # FastAPI backend
│   ├── airflow/            # DAG definitions
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
git clone https://github.com/Best-Code/track-tracker.git
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
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
AWS_REGION=us-east-1
DATABASE_URL=postgresql://user:pass@host:5432/tracktracker
```

## Team

- [Colin Maloney] - Data Engineer


## License

MIT