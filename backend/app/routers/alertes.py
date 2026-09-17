from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/alertes", tags=["alertes"])


@router.get("/", response_model=schemas.AlertesResponse)
def obtenir_alertes(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    aujourdhui = date.today()
    debut_mois = aujourdhui.replace(day=1)

    # --- Budget commun ---
    depenses_communes_mois = (
        db.query(models.Depense)
        .filter(
            models.Depense.foyer_id == current_user.foyer_id,
            models.Depense.partagee == True,
            models.Depense.date >= debut_mois,
        )
        .all()
    )
    total_commun = sum(d.montant for d in depenses_communes_mois)
    budget_commun = (
        db.query(models.Budget)
        .filter(models.Budget.foyer_id == current_user.foyer_id, models.Budget.mois == debut_mois)
        .first()
    )
    depassement_commun = None
    if budget_commun and total_commun > budget_commun.montant:
        depassement_commun = round(total_commun - budget_commun.montant, 2)

    # --- Budget solo (propre à l'utilisateur connecté) ---
    depenses_solo_mois = (
        db.query(models.Depense)
        .filter(
            models.Depense.payeur_id == current_user.id,
            models.Depense.partagee == False,
            models.Depense.date >= debut_mois,
        )
        .all()
    )
    total_solo = sum(d.montant for d in depenses_solo_mois)
    budget_solo = (
        db.query(models.BudgetPersonnel)
        .filter(models.BudgetPersonnel.utilisateur_id == current_user.id, models.BudgetPersonnel.mois == debut_mois)
        .first()
    )
    depassement_solo = None
    if budget_solo and total_solo > budget_solo.montant:
        depassement_solo = round(total_solo - budget_solo.montant, 2)

    # --- Rappel de saisie : dernière dépense commune du foyer, tous membres confondus ---
    derniere_depense = (
        db.query(models.Depense)
        .filter(models.Depense.foyer_id == current_user.foyer_id, models.Depense.partagee == True)
        .order_by(models.Depense.date.desc())
        .first()
    )
    jours_sans_depense = (aujourdhui - derniere_depense.date).days if derniere_depense else None

    return schemas.AlertesResponse(
        depassement_budget_commun=depassement_commun,
        depassement_budget_solo=depassement_solo,
        jours_sans_depense_commune=jours_sans_depense,
    )
