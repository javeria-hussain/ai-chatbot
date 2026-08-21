"""add external_id columns for idempotent ingestion

Revision ID: fdfcaf5c597d
Revises: abd1844e1054
Create Date: 2026-08-17 20:09:12.179739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdfcaf5c597d'
down_revision: Union[str, Sequence[str], None] = 'abd1844e1054'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("knowledge_document", sa.Column("external_id", sa.String(100), nullable=True))
    op.create_unique_constraint("uq_knowledge_document_external_id", "knowledge_document", ["external_id"])

    op.add_column("knowledge_chunk", sa.Column("external_id", sa.String(120), nullable=True))
    op.create_unique_constraint("uq_knowledge_chunk_external_id", "knowledge_chunk", ["external_id"])

def downgrade():
    op.drop_constraint("uq_knowledge_chunk_external_id", "knowledge_chunk", type_="unique")
    op.drop_column("knowledge_chunk", "external_id")
    op.drop_constraint("uq_knowledge_document_external_id", "knowledge_document", type_="unique")
    op.drop_column("knowledge_document", "external_id")