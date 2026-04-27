"""add spotify_album_image_url to track

Revision ID: c3d74e9f1b52
Revises: a3f82c1e9b47
Create Date: 2026-04-26

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d74e9f1b52"
down_revision: Union[str, Sequence[str], None] = "a3f82c1e9b47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "track",
        sa.Column("spotify_album_image_url", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("track", "spotify_album_image_url")
