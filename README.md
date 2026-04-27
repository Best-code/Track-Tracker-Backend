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
