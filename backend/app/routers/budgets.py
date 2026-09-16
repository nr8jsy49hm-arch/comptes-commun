from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _premier_du_mois(d: date) -> date:
    return d.replace(day=1)


@router.get("/mois-courant", response_model=schemas.Budget | None)
def obtenir_budget_courant(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    mois = _premier_du_mois(date.today())
    return (
        db.query(models.Budget)
        .filter(models.Budget.foyer_id == current_user.foyer_id, models.Budget.mois == mois)
        .first()
    )


@router.post("/", response_model=schemas.Budget)
def definir_budget(
    payload: schemas.BudgetBase,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    mois = _premier_du_mois(payload.mois or date.today())

    existant = (
        db.query(models.Budget)
        .filter(models.Budget.foyer_id == current_user.foyer_id, models.Budget.mois == mois)
        .first()
    )

    if existant:
        existant.montant = payload.montant
        db.commit()
        db.refresh(existant)
        return existant

    db_budget = models.Budget(mois=mois, montant=payload.montant, foyer_id=current_user.foyer_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget
