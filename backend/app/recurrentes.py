from calendar import monthrange
from datetime import date
from sqlalchemy.orm import Session

from . import models


def generer_recurrentes_du_mois(foyer_id: int, db: Session) -> list[str]:
    """
    Pour chaque dépense récurrente active du foyer, crée la dépense du mois en cours si elle
    n'existe pas déjà (une seule génération par règle et par mois). Renvoie une liste de
    messages si le montant d'une règle a changé depuis sa dernière génération, pour alimenter
    les notifications.

    Appelé à chaque consultation du tableau de bord / de la liste des dépenses : pas besoin
    d'un job planifié séparé, la génération se fait "à la demande" dès que quelqu'un ouvre
    l'appli ce mois-ci.
    """
    aujourdhui = date.today()
    debut_mois = aujourdhui.replace(day=1)
    dernier_jour_mois = monthrange(aujourdhui.year, aujourdhui.month)[1]

    regles = (
        db.query(models.DepenseRecurrente)
        .filter(models.DepenseRecurrente.foyer_id == foyer_id, models.DepenseRecurrente.actif == True)
        .all()
    )

    notices: list[str] = []

    for regle in regles:
        deja_generee = (
            db.query(models.Depense)
            .filter(models.Depense.recurrente_id == regle.id, models.Depense.date >= debut_mois)
            .first()
        )
        if deja_generee:
            continue

        # Compare au dernier montant généré (mois précédents) pour détecter un changement
        derniere_occurrence = (
            db.query(models.Depense)
            .filter(models.Depense.recurrente_id == regle.id)
            .order_by(models.Depense.date.desc())
            .first()
        )
        if derniere_occurrence and derniere_occurrence.montant != regle.montant:
            notices.append(
                f"Le montant de « {regle.nom} » a changé : {derniere_occurrence.montant:.2f} € → {regle.montant:.2f} € ce mois-ci."
            )

        jour = min(regle.jour_du_mois, dernier_jour_mois)
        db.add(
            models.Depense(
                montant=regle.montant,
                date=date(aujourdhui.year, aujourdhui.month, jour),
                note=f"Récurrent : {regle.nom}",
                partagee=regle.partagee,
                categorie_id=regle.categorie_id,
                payeur_id=regle.payeur_id,
                foyer_id=foyer_id,
                recurrente_id=regle.id,
            )
        )

    if regles:
        db.commit()

    return notices
