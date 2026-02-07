"""add_language_index_and_watch_providers

Revision ID: a7d5e1f02c26
Revises: f6c4d0e93b15
Create Date: 2026-02-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a7d5e1f02c26'
down_revision: Union[str, Sequence[str], None] = 'f6c4d0e93b15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # A4: Add index on catalog_akas.language for the language filter EXISTS subquery
    op.create_index('ix_catalog_akas_language', 'catalog_akas', ['language'])

    # B1: Create provider_master table
    op.create_table(
        'provider_master',
        sa.Column('provider_id', sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column('provider_name', sa.String(200), nullable=False),
        sa.Column('logo_path', sa.String(255), nullable=True),
        sa.Column('display_priority', sa.Integer(), nullable=True),
    )

    # B1: Create watch_providers table
    op.create_table(
        'watch_providers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title_id', sa.Integer(), sa.ForeignKey('catalog_titles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('provider_name', sa.String(200), nullable=False),
        sa.Column('logo_path', sa.String(255), nullable=True),
        sa.Column('provider_type', sa.String(20), nullable=False),
        sa.Column('region', sa.String(10), nullable=False, server_default='US'),
        sa.Column('display_priority', sa.Integer(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('title_id', 'provider_id', 'provider_type', 'region', name='uq_watch_provider_entry'),
    )
    op.create_index('ix_watch_providers_title_id', 'watch_providers', ['title_id'])
    op.create_index('ix_watch_providers_provider_id', 'watch_providers', ['provider_id'])
    op.create_index('ix_watch_providers_region', 'watch_providers', ['region'])


def downgrade() -> None:
    op.drop_index('ix_watch_providers_region', table_name='watch_providers')
    op.drop_index('ix_watch_providers_provider_id', table_name='watch_providers')
    op.drop_index('ix_watch_providers_title_id', table_name='watch_providers')
    op.drop_table('watch_providers')
    op.drop_table('provider_master')
    op.drop_index('ix_catalog_akas_language', table_name='catalog_akas')
