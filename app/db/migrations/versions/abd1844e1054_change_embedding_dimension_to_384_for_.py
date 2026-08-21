"""change embedding dimension to 384 for huggingface

Revision ID: abd1844e1054
Revises: 76026bf25891
Create Date: 2026-08-17 19:47:28.277598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abd1844e1054'
down_revision: Union[str, Sequence[str], None] = '76026bf25891'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Pehle purana index hatao (dimension badalne se pehle zaroori hai)
    op.execute("DROP INDEX IF EXISTS ix_knowledge_chunk_embedding_hnsw")
    # Column type change karo
    op.execute("ALTER TABLE knowledge_chunk ALTER COLUMN embedding TYPE vector(384)")
    # Index dobara banao naye dimension ke sath
    op.execute(
        "CREATE INDEX ix_knowledge_chunk_embedding_hnsw "
        "ON knowledge_chunk USING hnsw (embedding vector_cosine_ops)"
    )

def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_knowledge_chunk_embedding_hnsw")
    op.execute("ALTER TABLE knowledge_chunk ALTER COLUMN embedding TYPE vector(1536)")
    op.execute(
        "CREATE INDEX ix_knowledge_chunk_embedding_hnsw "
        "ON knowledge_chunk USING hnsw (embedding vector_cosine_ops)"
    )
