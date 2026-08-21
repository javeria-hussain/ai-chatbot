"""add provider message id and error detail to email_notification

Revision ID: e7b06a3ba0bf
Revises: 6a815f2b663d
Create Date: 2026-08-21 16:55:11.418878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b06a3ba0bf'
down_revision: Union[str, Sequence[str], None] = '6a815f2b663d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "email_notification",
        sa.Column("provider_message_id", sa.String(), nullable=True),
    )
    op.add_column(
        "email_notification", sa.Column("error_detail", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("email_notification", "error_detail")
    op.drop_column("email_notification", "provider_message_id")
