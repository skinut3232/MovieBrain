"""add original_language to catalog_titles

Revision ID: d1a2b3c4e5f6
Revises: c9d3e4f56a78
Create Date: 2026-02-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d1a2b3c4e5f6"
down_revision = "c9d3e4f56a78"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("catalog_titles", sa.Column("original_language", sa.String(10), nullable=True))
    op.create_index("ix_catalog_titles_original_language", "catalog_titles", ["original_language"])


def downgrade() -> None:
    op.drop_index("ix_catalog_titles_original_language", table_name="catalog_titles")
    op.drop_column("catalog_titles", "original_language")
