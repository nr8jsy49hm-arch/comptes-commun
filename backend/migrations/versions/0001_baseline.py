"""baseline initiale — schéma complet au moment de l'adoption d'Alembic

Revision ID: 0001
Revises:
Create Date: 2026-09-17

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "foyers",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom", sa.String(), nullable=False),
    )

    op.create_table(
        "utilisateurs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("mot_de_passe_hash", sa.String(), nullable=False),
        sa.Column("question_secrete", sa.String(), nullable=True),
        sa.Column("reponse_secrete_hash", sa.String(), nullable=True),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )

    op.create_table(
        "depenses",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("partagee", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("categorie_id", sa.Integer(), sa.ForeignKey("categories.id")),
        sa.Column("payeur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "reglements",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("de_utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
        sa.Column("vers_utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )

    op.create_table(
        "cles_repartition",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("valeur", sa.String(), nullable=True),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("mois", sa.Date(), nullable=False),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )

    op.create_table(
        "budgets_personnels",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("mois", sa.Date(), nullable=False),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
    )

    op.create_table(
        "objectifs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("montant_cible", sa.Float(), nullable=False),
        sa.Column("date_cible", sa.Date(), nullable=True),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )

    op.create_table(
        "versements_objectifs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("objectif_id", sa.Integer(), sa.ForeignKey("objectifs.id")),
    )


def downgrade() -> None:
    op.drop_table("versements_objectifs")
    op.drop_table("objectifs")
    op.drop_table("budgets_personnels")
    op.drop_table("budgets")
    op.drop_table("cles_repartition")
    op.drop_table("reglements")
    op.drop_table("depenses")
    op.drop_table("categories")
    op.drop_table("utilisateurs")
    op.drop_table("foyers")
