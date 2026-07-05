"""add priority to todos

Revision ID: 4d6172508c2d
Revises: be1c61339c9f
Create Date: 2026-07-05 18:07:57.806395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel  # autogenerate が sqlmodel.sql.sqltypes.AutoString 等を出力するため


# revision identifiers, used by Alembic.
revision: str = '4d6172508c2d'
down_revision: Union[str, Sequence[str], None] = 'be1c61339c9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """既存行にも値が要る NOT NULL 列なので server_default='medium' で追加し、
    既存の TODO をすべて 'medium' に埋める（データ移行）。既定値はアプリ層(schemas)も持つ。"""
    op.add_column(
        "todos",
        sa.Column(
            "priority",
            sqlmodel.sql.sqltypes.AutoString(length=10),
            nullable=False,
            server_default="medium",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("todos", "priority")
