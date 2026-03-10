"""
Track Tracker - Emerging music detection platform.

This is the main entry point for the Track Tracker application.
It provides a CLI interface for running ingestion jobs and querying data.

Usage:
    # Run Spotify ingestion
    uv run python main.py ingest

    # Show database statistics
    uv run python main.py stats

    # Initialize database tables
    uv run python main.py init-db
"""

import argparse
import logging
import sys


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def cmd_ingest(args: argparse.Namespace) -> int:
    """Run Spotify ingestion pipeline."""
    import asyncio
    from app.ingestion.pipeline import run_pipeline

    result = asyncio.run(run_pipeline())
    print(f"Ingested {result.tracks_processed} tracks")

    if result.errors > 0:
        print(f"Encountered {result.errors} errors during ingestion")
        return 1
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Display database statistics."""
    from app.db.query import show_stats

    show_stats()
    return 0


def cmd_init_db(args: argparse.Namespace) -> int:
    """Initialize database tables."""
    from app.db.init import init_db

    init_db()
    return 0


def main() -> int:
    """Main entry point for Track Tracker CLI."""
    parser = argparse.ArgumentParser(
        description="Track Tracker - Detect emerging music before it charts"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Run Spotify ingestion")
    ingest_parser.add_argument(
        "--limit", type=int, default=20, help="Number of albums to fetch (default: 20)"
    )
    ingest_parser.set_defaults(func=cmd_ingest)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.set_defaults(func=cmd_stats)

    # Init-db command
    init_parser = subparsers.add_parser("init-db", help="Initialize database tables")
    init_parser.set_defaults(func=cmd_init_db)

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
