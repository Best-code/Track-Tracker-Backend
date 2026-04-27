"""update track_snapshot: replace popularity/followers with streams, add index

Revision ID: a3f82c1e9b47
Revises: 1964afedb5a9
Create Date: 2026-04-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3f82c1e9b47"
down_revision: Union[str, Sequence[str], None] = "1964afedb5a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Replace deprecated spotify_popularity and spotify_followers columns with
    spotify_streams (scraped from open.spotify.com). Add composite index for
    fast boundary queries used in growth stat calculations.

    Note: The previous migration created the table as "TrackSnapshot" (PascalCase).
    The SQLAlchemy model uses __tablename__ = "track_snapshot" (snake_case).
    This migration targets "track_snapshot" to align with the model.
    If your database has "TrackSnapshot", rename it first:
        ALTER TABLE "TrackSnapshot" RENAME TO track_snapshot;
    """
    op.drop_column("track_snapshot", "spotify_popularity")
    op.drop_column("track_snapshot", "spotify_followers")
    op.add_column(
        "track_snapshot",
        sa.Column("spotify_streams", sa.BigInteger(), nullable=True),
    )
    op.create_index(
        "ix_track_snapshot_track_id_recorded_at",
        "track_snapshot",
        ["track_id", "recorded_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_track_snapshot_track_id_recorded_at", table_name="track_snapshot")
    op.drop_column("track_snapshot", "spotify_streams")
    op.add_column(
        "track_snapshot",
        sa.Column("spotify_popularity", sa.Integer(), nullable=True),
    )
    op.add_column(
        "track_snapshot",
        sa.Column("spotify_followers", sa.Integer(), nullable=True),
    )
