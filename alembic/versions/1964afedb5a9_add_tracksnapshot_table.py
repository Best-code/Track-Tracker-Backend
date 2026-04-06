"""add TrackSnapshot table

Revision ID: 1964afedb5a9
Revises:
Create Date: 2026-03-05 18:44:38.125816

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1964afedb5a9"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "track_snapshot",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("spotify_popularity", sa.Integer(), nullable=True),
        sa.Column("spotify_followers", sa.Integer(), nullable=True),
        sa.Column(
            "recorded_at", sa.TIMESTAMP(), server_default="now()", nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["track.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("track_snapshot")
