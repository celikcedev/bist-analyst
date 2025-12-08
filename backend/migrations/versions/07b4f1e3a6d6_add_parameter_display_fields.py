"""add_parameter_display_fields

Revision ID: 07b4f1e3a6d6
Revises: 489ef63df927
Create Date: 2025-12-09 02:17:08.638735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '07b4f1e3a6d6'
down_revision: Union[str, None] = '489ef63df927'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to strategy_parameters table
    op.add_column('strategy_parameters', sa.Column('parameter_type', sa.String(length=20), server_default='str'))
    op.add_column('strategy_parameters', sa.Column('display_name', sa.String(length=200)))
    op.add_column('strategy_parameters', sa.Column('display_group', sa.String(length=100)))
    op.add_column('strategy_parameters', sa.Column('display_order', sa.Integer(), server_default='999'))


def downgrade() -> None:
    # Remove columns if rolling back
    op.drop_column('strategy_parameters', 'display_order')
    op.drop_column('strategy_parameters', 'display_group')
    op.drop_column('strategy_parameters', 'display_name')
    op.drop_column('strategy_parameters', 'parameter_type')
