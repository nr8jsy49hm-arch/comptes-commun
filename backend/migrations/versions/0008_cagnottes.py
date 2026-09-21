"""ajout des cagnottes pour projets communs (accès public via lien partagé)

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cagnottes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("montant_cible", sa.Float(), nullable=True),
        sa.Column("date_limite", sa.Date(), nullable=True),
        sa.Column("token_public", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("cloturee", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
        sa.Column("createur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "contributions_cagnottes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom_contributeur", sa.String(), nullable=False),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("cagnotte_id", sa.Integer(), sa.ForeignKey("cagnottes.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("contributions_cagnottes")
    op.drop_table("cagnottes")
