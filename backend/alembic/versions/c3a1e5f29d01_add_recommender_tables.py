"""add_recommender_tables

Revision ID: c3a1e5f29d01
Revises: f8650a768763
Create Date: 2026-02-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c3a1e5f29d01'
down_revision: Union[str, Sequence[str], None] = 'f8650a768763'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create movie_embeddings table with vector column
    op.execute("""
        CREATE TABLE movie_embeddings (
            title_id INTEGER NOT NULL REFERENCES catalog_titles(id),
            model_id VARCHAR(128) NOT NULL,
            embedding vector(1536),
            embedding_text TEXT,
            updated_at TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (title_id, model_id)
        )
    """)

    # Create HNSW index for cosine distance on embedding column
    op.execute("""
        CREATE INDEX ix_movie_embeddings_embedding_hnsw
        ON movie_embeddings
        USING hnsw (embedding vector_cosine_ops)
    """)

    # Create profile_taste table with vector column
    op.execute("""
        CREATE TABLE profile_taste (
            profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            model_id VARCHAR(128) NOT NULL,
            taste_vector vector(1536),
            num_rated_movies INTEGER DEFAULT 0,
            updated_at TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (profile_id, model_id)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('profile_taste')
    op.drop_table('movie_embeddings')
    op.execute("DROP EXTENSION IF EXISTS vector")
