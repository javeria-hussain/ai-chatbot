"""add optional lead detail fields

Revision ID: 6a815f2b663d
Revises: b941fc16efe7
Create Date: 2026-08-21 16:10:43.842591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a815f2b663d'
down_revision: Union[str, Sequence[str], None] = 'b941fc16efe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lead_submission", sa.Column("company", sa.String(), nullable=True))
    op.add_column(
        "lead_submission", sa.Column("service_interest", sa.String(), nullable=True)
    )
    op.add_column(
        "lead_submission", sa.Column("project_summary", sa.Text(), nullable=True)
    )
    op.add_column(
        "lead_submission", sa.Column("timeline_budget", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("lead_submission", "timeline_budget")
    op.drop_column("lead_submission", "project_summary")
    op.drop_column("lead_submission", "service_interest")
    op.drop_column("lead_submission", "company")
