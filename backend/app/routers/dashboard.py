from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user
from ..recurrentes import generer_recurrentes_du_mois
from .repartition import _calculer_balance

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=schemas.DashboardResponse)
def obtenir_dashboard(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    generer_recurrentes_du_mois(current_user.foyer_id, db)

    aujourdhui = date.today()
    depenses_mois = (
        db.query(models.Depense)
        .filter(
            models.Depense.foyer_id == current_user.foyer_id,
            models.Depense.partagee == True,
            models.Depense.date >= aujourdhui.replace(day=1),
        )
        .all()
    )

    total_mois = sum(d.montant for d in depenses_mois)

    par_categorie: dict[str, float] = {}
    for d in depenses_mois:
        nom_cat = d.categorie.nom if d.categorie else "Autre"
        par_categorie[nom_cat] = par_categorie.get(nom_cat, 0) + d.montant

    balances = _calculer_balance(current_user.foyer_id, db)

    budget = (
        db.query(models.Budget)
        .filter(
            models.Budget.foyer_id == current_user.foyer_id,
            models.Budget.mois == aujourdhui.replace(day=1),
        )
        .first()
    )
    budget_mois = budget.montant if budget else None
    reste_a_vivre = (budget_mois - total_mois) if budget_mois is not None else None

    return schemas.DashboardResponse(
        total_mois=round(total_mois, 2),
        par_categorie={k: round(v, 2) for k, v in par_categorie.items()},
        balances=balances,
        budget_mois=budget_mois,
        reste_a_vivre=round(reste_a_vivre, 2) if reste_a_vivre is not None else None,
    )
