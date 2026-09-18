"""ajout de la table invitations (remplace le code_foyer devinable)

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-18

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invitations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("token", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
        sa.Column("cree_par_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
        sa.Column("expire_le", sa.DateTime(timezone=True), nullable=False),
        sa.Column("utilisee_le", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("invitations")
