"""add pgvector hnsw index on knowledge_chunk

Revision ID: 76026bf25891
Revises: efd7eca7fc53
Create Date: 2026-08-17 15:46:43.662511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76026bf25891'
down_revision: Union[str, Sequence[str], None] = 'efd7eca7fc53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_knowledge_chunk_embedding_hnsw "
        "ON knowledge_chunk USING hnsw (embedding vector_cosine_ops)"
    )

def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_knowledge_chunk_embedding_hnsw")