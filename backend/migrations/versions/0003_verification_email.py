"""ajout de la vérification d'email (colonne email_verifie + table verifications_email)

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-18

"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "utilisateurs",
        sa.Column("email_verifie", sa.Boolean(), nullable=False, server_default="true"),
    )

    op.create_table(
        "verifications_email",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("token", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
        sa.Column("expire_le", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verifiee_le", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("verifications_email")
    op.drop_column("utilisateurs", "email_verifie")
