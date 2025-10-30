"""fix created_at default value

Revision ID: 002
Revises: 001
Create Date: 2025-10-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add server_default for created_at column
    op.alter_column('pets', 'created_at',
                    server_default=sa.text('CURRENT_TIMESTAMP'),
                    existing_nullable=False,
                    existing_type=sa.DateTime())


def downgrade() -> None:
    # Remove server_default
    op.alter_column('pets', 'created_at',
                    server_default=None,
                    existing_nullable=False,
                    existing_type=sa.DateTime())