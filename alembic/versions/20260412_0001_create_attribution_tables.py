"""create attribution tables

Revision ID: 20260412_0001
Revises:
Create Date: 2026-04-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260412_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "referral_tokens",
        sa.Column("token", sa.String(length=64), primary_key=True),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("discount_type", sa.String(length=16), nullable=False),
        sa.Column("discount_value", sa.Float(), nullable=False),
        sa.Column("course_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("campaign", sa.Text(), nullable=True),
        sa.Column("policy_locked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.String(length=64), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_referral_tokens_channel", "referral_tokens", ["channel"], unique=False)
    op.create_index("ix_referral_tokens_course_id", "referral_tokens", ["course_id"], unique=False)
    op.create_index("ix_referral_tokens_status", "referral_tokens", ["status"], unique=False)

    op.create_table(
        "attribution_visits",
        sa.Column("visit_id", sa.String(length=64), primary_key=True),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("clicked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("parent_id", sa.String(length=64), nullable=True),
        sa.Column("anonymous_id", sa.String(length=128), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.String(length=64), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_attribution_visits_token", "attribution_visits", ["token"], unique=False)
    op.create_index("ix_attribution_visits_channel", "attribution_visits", ["channel"], unique=False)
    op.create_index("ix_attribution_visits_clicked_at", "attribution_visits", ["clicked_at"], unique=False)
    op.create_index("ix_attribution_visits_parent_id", "attribution_visits", ["parent_id"], unique=False)
    op.create_index(
        "ix_attribution_visits_anonymous_id",
        "attribution_visits",
        ["anonymous_id"],
        unique=False,
    )

    op.create_table(
        "attribution_conversions",
        sa.Column("access_grant_id", sa.String(length=64), primary_key=True),
        sa.Column("course_id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=True),
        sa.Column("parent_id", sa.String(length=64), nullable=True),
        sa.Column("requested_recorded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("paid_recorded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requested_discount_amount", sa.Float(), nullable=True),
        sa.Column("requested_discount_currency", sa.String(length=3), nullable=True),
        sa.Column("paid_amount", sa.Float(), nullable=True),
        sa.Column("paid_currency", sa.String(length=3), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.String(length=64), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_attribution_conversions_course_id",
        "attribution_conversions",
        ["course_id"],
        unique=False,
    )
    op.create_index(
        "ix_attribution_conversions_student_id",
        "attribution_conversions",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        "ix_attribution_conversions_channel",
        "attribution_conversions",
        ["channel"],
        unique=False,
    )
    op.create_index(
        "ix_attribution_conversions_token",
        "attribution_conversions",
        ["token"],
        unique=False,
    )
    op.create_index(
        "ix_attribution_conversions_parent_id",
        "attribution_conversions",
        ["parent_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_attribution_conversions_parent_id", table_name="attribution_conversions")
    op.drop_index("ix_attribution_conversions_token", table_name="attribution_conversions")
    op.drop_index("ix_attribution_conversions_channel", table_name="attribution_conversions")
    op.drop_index("ix_attribution_conversions_student_id", table_name="attribution_conversions")
    op.drop_index("ix_attribution_conversions_course_id", table_name="attribution_conversions")
    op.drop_table("attribution_conversions")

    op.drop_index("ix_attribution_visits_anonymous_id", table_name="attribution_visits")
    op.drop_index("ix_attribution_visits_parent_id", table_name="attribution_visits")
    op.drop_index("ix_attribution_visits_clicked_at", table_name="attribution_visits")
    op.drop_index("ix_attribution_visits_channel", table_name="attribution_visits")
    op.drop_index("ix_attribution_visits_token", table_name="attribution_visits")
    op.drop_table("attribution_visits")

    op.drop_index("ix_referral_tokens_status", table_name="referral_tokens")
    op.drop_index("ix_referral_tokens_course_id", table_name="referral_tokens")
    op.drop_index("ix_referral_tokens_channel", table_name="referral_tokens")
    op.drop_table("referral_tokens")

