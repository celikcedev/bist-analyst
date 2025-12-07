"""Initial schema with users, strategies, and signal tracking

Revision ID: 489ef63df927
Revises: 
Create Date: 2025-12-08 00:11:41.299690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '489ef63df927'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Insert default user
    op.execute("""
        INSERT INTO users (id, username, email, is_active) 
        VALUES (1, 'default_user', 'default@local', true)
    """)
    
    # Alter tickers table - add new columns
    op.add_column('tickers', sa.Column('user_id', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('tickers', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.create_foreign_key('fk_tickers_user', 'tickers', 'users', ['user_id'], ['id'])
    op.create_index('idx_tickers_user', 'tickers', ['user_id', 'is_active'])
    
    # Alter market_data table - add metadata columns
    op.add_column('market_data', sa.Column('data_source', sa.String(length=50), server_default='tvdatafeed'))
    op.add_column('market_data', sa.Column('is_adjusted', sa.Boolean(), server_default='false'))
    
    # Create strategies table
    op.create_table('strategies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('python_class', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create strategy_parameters table
    op.create_table('strategy_parameters',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('parameter_name', sa.String(length=100), nullable=False),
        sa.Column('parameter_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_default', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_params_user_strategy', 'strategy_parameters', 
                    ['user_id', 'strategy_id', 'parameter_name'], unique=True)
    
    # Create signal_history table
    op.create_table('signal_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('signal_type', sa.String(length=50), nullable=False),
        sa.Column('signal_date', sa.Date(), nullable=False),
        sa.Column('price_at_signal', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('rsi', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('adx', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_signals_user_strategy', 'signal_history', 
                    ['user_id', 'strategy_id', 'signal_date'], postgresql_using='btree')
    op.create_index('idx_signals_unique', 'signal_history', 
                    ['user_id', 'strategy_id', 'symbol', 'signal_date', 'signal_type'], unique=True)
    
    # Create signal_performance table
    op.create_table('signal_performance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('signal_id', sa.Integer(), nullable=False),
        sa.Column('price_1d', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('price_3d', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('price_7d', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('gain_1d', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('gain_3d', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('gain_7d', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['signal_id'], ['signal_history.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('signal_id')
    )


def downgrade() -> None:
    # Drop new tables
    op.drop_table('signal_performance')
    op.drop_index('idx_signals_unique', table_name='signal_history')
    op.drop_index('idx_signals_user_strategy', table_name='signal_history')
    op.drop_table('signal_history')
    op.drop_index('idx_params_user_strategy', table_name='strategy_parameters')
    op.drop_table('strategy_parameters')
    op.drop_table('strategies')
    
    # Revert market_data changes
    op.drop_column('market_data', 'is_adjusted')
    op.drop_column('market_data', 'data_source')
    
    # Revert tickers changes
    op.drop_index('idx_tickers_user', table_name='tickers')
    op.drop_constraint('fk_tickers_user', 'tickers', type_='foreignkey')
    op.drop_column('tickers', 'is_active')
    op.drop_column('tickers', 'user_id')
    
    # Drop users table
    op.drop_table('users')
