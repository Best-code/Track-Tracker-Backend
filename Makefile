# Track Tracker Makefile
# Common commands for development

.PHONY: help install lint format test run serve init-db stats ingest clean

# Environment file
ENV_FILE = --env-file env/.env.development

# Default target
help:
	@echo "Track Tracker - Available commands:"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make lint       Run Ruff linter"
	@echo "  make format     Format code with Ruff"
	@echo "  make test       Run all tests (mocked, no env needed)"
	@echo "  make run        Run the CLI application (shows help)"
	@echo "  make serve      Start the FastAPI server (http://localhost:8000)"
	@echo "  make init-db    Initialize database tables"
	@echo "  make stats      Show database statistics"
	@echo "  make ingest     Run Spotify ingestion"
	@echo "  make clean      Remove cached files"
	@echo ""

# Install dependencies
install:
	uv sync

# Linting (no env needed)
lint:
	uv run ruff check .

# Format code (no env needed)
format:
	uv run ruff format .
	uv run ruff check --fix .

# Run tests (mocked, no env needed)
test:
	uv run pytest tests/ -v

# Run CLI application
run:
	uv run $(ENV_FILE) python main.py

# Start FastAPI server with hot reload
serve:
	docker compose up -d db
	uv run $(ENV_FILE) uvicorn app.api.api:app --reload

# Initialize database
init-db:
	uv run $(ENV_FILE) python main.py init-db

# Show stats
stats:
	uv run $(ENV_FILE) python main.py stats

# Run ingestion
ingest:
	uv run $(ENV_FILE) python main.py ingest

# Clean up cached files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# Access PostgreSQL directly
psql:
	docker exec -it track-tracker-db psql -U tracker -d track_tracker
