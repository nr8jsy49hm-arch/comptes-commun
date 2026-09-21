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


# ---------- Budgets par catégorie ("enveloppes") ----------

def _depense_categorie_ce_mois(db: Session, foyer_id: int, categorie_id: int) -> float:
    aujourdhui = date.today()
    depenses = (
        db.query(models.Depense)
        .filter(
            models.Depense.foyer_id == foyer_id,
            models.Depense.categorie_id == categorie_id,
            models.Depense.partagee == True,
            models.Depense.date >= aujourdhui.replace(day=1),
        )
        .all()
    )
    return round(sum(d.montant for d in depenses), 2)


@router.get("/categories", response_model=list[schemas.BudgetCategorieOut])
def lister_budgets_categories(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    mois = _premier_du_mois(date.today())
    budgets = (
        db.query(models.BudgetCategorie)
        .filter(models.BudgetCategorie.foyer_id == current_user.foyer_id, models.BudgetCategorie.mois == mois)
        .all()
    )
    resultat = []
    for b in budgets:
        categorie = db.query(models.Categorie).filter(models.Categorie.id == b.categorie_id).first()
        depense_actuelle = _depense_categorie_ce_mois(db, current_user.foyer_id, b.categorie_id)
        resultat.append(
            schemas.BudgetCategorieOut(
                id=b.id,
                categorie_id=b.categorie_id,
                categorie_nom=categorie.nom if categorie else "Autre",
                montant=b.montant,
                depense_actuelle=depense_actuelle,
                reste=round(b.montant - depense_actuelle, 2),
                mois=b.mois,
            )
        )
    return resultat


@router.post("/categories", response_model=schemas.BudgetCategorieOut)
def definir_budget_categorie(
    payload: schemas.BudgetCategorieIn,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    mois = _premier_du_mois(payload.mois or date.today())

    existant = (
        db.query(models.BudgetCategorie)
        .filter(
            models.BudgetCategorie.foyer_id == current_user.foyer_id,
            models.BudgetCategorie.categorie_id == payload.categorie_id,
            models.BudgetCategorie.mois == mois,
        )
        .first()
    )
    if existant:
        existant.montant = payload.montant
        db.commit()
        db.refresh(existant)
        b = existant
    else:
        b = models.BudgetCategorie(
            mois=mois, montant=payload.montant, categorie_id=payload.categorie_id, foyer_id=current_user.foyer_id
        )
        db.add(b)
        db.commit()
        db.refresh(b)

    categorie = db.query(models.Categorie).filter(models.Categorie.id == b.categorie_id).first()
    depense_actuelle = _depense_categorie_ce_mois(db, current_user.foyer_id, b.categorie_id)
    return schemas.BudgetCategorieOut(
        id=b.id,
        categorie_id=b.categorie_id,
        categorie_nom=categorie.nom if categorie else "Autre",
        montant=b.montant,
        depense_actuelle=depense_actuelle,
        reste=round(b.montant - depense_actuelle, 2),
        mois=b.mois,
    )


@router.delete("/categories/{categorie_id}")
def supprimer_budget_categorie(
    categorie_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    mois = _premier_du_mois(date.today())
    db.query(models.BudgetCategorie).filter(
        models.BudgetCategorie.foyer_id == current_user.foyer_id,
        models.BudgetCategorie.categorie_id == categorie_id,
        models.BudgetCategorie.mois == mois,
    ).delete()
    db.commit()
    return {"ok": True}
