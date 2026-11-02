"""add service duration check

Revision ID: 8d4b6f2a1c90
Revises: 4a2eccd15bec
Create Date: 2026-11-02

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8d4b6f2a1c90"
down_revision = "4a2eccd15bec"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "ck_services_avg_minutes",
        "services",
        "avg_minutes > 0",
    )


def downgrade():
    op.drop_constraint(
        "ck_services_avg_minutes",
        "services",
        type_="check",
    )
