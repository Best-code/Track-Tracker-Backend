"""Composite index on track_snapshot(track_id, recorded_at).

Revision ID: b8a4f72e9d31
Revises: c3d74e9f1b52
Create Date: 2026-04-27 19:30:00.000000
"""

from typing import Sequence, Union
from alembic import op

revision: str = "b8a4f72e9d31"
down_revision: Union[str, Sequence[str], None] = "c3d74e9f1b52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_track_snapshot_track_id_recorded_at",
        "track_snapshot",
        ["track_id", "recorded_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_track_snapshot_track_id_recorded_at",
        table_name="track_snapshot",
    )
