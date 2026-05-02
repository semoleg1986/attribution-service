"""add source and medium to referral tokens

Revision ID: 20260502_0002
Revises: 20260412_0001
Create Date: 2026-05-02
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260502_0002"
down_revision: Union[str, Sequence[str], None] = "20260412_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "referral_tokens",
        sa.Column("source", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "referral_tokens",
        sa.Column("medium", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_referral_tokens_source", "referral_tokens", ["source"], unique=False
    )
    op.create_index(
        "ix_referral_tokens_medium", "referral_tokens", ["medium"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_referral_tokens_medium", table_name="referral_tokens")
    op.drop_index("ix_referral_tokens_source", table_name="referral_tokens")
    op.drop_column("referral_tokens", "medium")
    op.drop_column("referral_tokens", "source")
