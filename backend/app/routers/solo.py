from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from calendar import monthrange
from typing import List
import csv
import io

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/solo", tags=["solo"])

NOMS_MOIS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


def _premier_du_mois(d: date) -> date:
    return d.replace(day=1)


def _plage_mois(annee: int, mois: int) -> tuple[date, date]:
    debut = date(annee, mois, 1)
    fin = date(annee, mois, monthrange(annee, mois)[1])
    return debut, fin


# ---------- Tableau de bord solo ----------

@router.get("/dashboard", response_model=schemas.SoloDashboardResponse)
def obtenir_dashboard_solo(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    aujourdhui = date.today()
    depenses_mois = (
        db.query(models.Depense)
        .filter(
            models.Depense.payeur_id == current_user.id,
            models.Depense.partagee == False,
            models.Depense.date >= aujourdhui.replace(day=1),
        )
        .order_by(models.Depense.date.desc())
        .all()
    )

    total = sum(d.montant for d in depenses_mois)

    par_categorie: dict[str, float] = {}
    for d in depenses_mois:
        nom_cat = d.categorie.nom if d.categorie else "Autre"
        par_categorie[nom_cat] = par_categorie.get(nom_cat, 0) + d.montant

    budget = (
        db.query(models.BudgetPersonnel)
        .filter(
            models.BudgetPersonnel.utilisateur_id == current_user.id,
            models.BudgetPersonnel.mois == aujourdhui.replace(day=1),
        )
        .first()
    )
    budget_mois = budget.montant if budget else None
    reste_a_vivre = (budget_mois - total) if budget_mois is not None else None

    return schemas.SoloDashboardResponse(
        total_mois=round(total, 2),
        par_categorie={k: round(v, 2) for k, v in par_categorie.items()},
        depenses=depenses_mois,
        budget_mois=budget_mois,
        reste_a_vivre=round(reste_a_vivre, 2) if reste_a_vivre is not None else None,
    )


# ---------- Budget personnel ----------

@router.get("/budgets/mois-courant", response_model=schemas.BudgetPersonnel | None)
def obtenir_budget_solo_courant(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    mois = _premier_du_mois(date.today())
    return (
        db.query(models.BudgetPersonnel)
        .filter(models.BudgetPersonnel.utilisateur_id == current_user.id, models.BudgetPersonnel.mois == mois)
        .first()
    )


@router.post("/budgets", response_model=schemas.BudgetPersonnel)
def definir_budget_solo(
    payload: schemas.BudgetBase,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    mois = _premier_du_mois(payload.mois or date.today())

    existant = (
        db.query(models.BudgetPersonnel)
        .filter(models.BudgetPersonnel.utilisateur_id == current_user.id, models.BudgetPersonnel.mois == mois)
        .first()
    )

    if existant:
        existant.montant = payload.montant
        db.commit()
        db.refresh(existant)
        return existant

    db_budget = models.BudgetPersonnel(mois=mois, montant=payload.montant, utilisateur_id=current_user.id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


# ---------- Historique solo ----------

@router.get("/historique/annees", response_model=List[int])
def lister_annees_solo(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    from sqlalchemy import extract

    annees = (
        db.query(extract("year", models.Depense.date))
        .filter(models.Depense.payeur_id == current_user.id, models.Depense.partagee == False)
        .distinct()
        .all()
    )
    resultat = sorted({int(a[0]) for a in annees}, reverse=True)
    annee_courante = date.today().year
    if annee_courante not in resultat:
        resultat.insert(0, annee_courante)
    return resultat


@router.get("/historique/{annee}", response_model=List[schemas.MoisHistorique])
def historique_solo_annee(
    annee: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    resultat = []
    for mois in range(1, 13):
        debut, fin = _plage_mois(annee, mois)
        depenses = (
            db.query(models.Depense)
            .filter(
                models.Depense.payeur_id == current_user.id,
                models.Depense.partagee == False,
                models.Depense.date >= debut,
                models.Depense.date <= fin,
            )
            .all()
        )
        total = sum(d.montant for d in depenses)

        budget = (
            db.query(models.BudgetPersonnel)
            .filter(models.BudgetPersonnel.utilisateur_id == current_user.id, models.BudgetPersonnel.mois == debut)
            .first()
        )
        budget_montant = budget.montant if budget else None

        resultat.append(
            schemas.MoisHistorique(
                mois=mois,
                nom_mois=NOMS_MOIS[mois - 1],
                total_depense=round(total, 2),
                budget=budget_montant,
                reste_a_vivre=round(budget_montant - total, 2) if budget_montant is not None else None,
                nb_depenses=len(depenses),
            )
        )
    return resultat


@router.get("/historique/{annee}/{mois}/categories", response_model=dict[str, float])
def historique_solo_mois_categories(
    annee: int,
    mois: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    debut, fin = _plage_mois(annee, mois)
    depenses = (
        db.query(models.Depense)
        .filter(
            models.Depense.payeur_id == current_user.id,
            models.Depense.partagee == False,
            models.Depense.date >= debut,
            models.Depense.date <= fin,
        )
        .all()
    )
    par_categorie: dict[str, float] = {}
    for d in depenses:
        nom_cat = d.categorie.nom if d.categorie else "Autre"
        par_categorie[nom_cat] = par_categorie.get(nom_cat, 0) + d.montant
    return {k: round(v, 2) for k, v in par_categorie.items()}


# ---------- Export CSV ----------

@router.get("/export/depenses.csv")
def exporter_depenses_solo_csv(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    depenses = (
        db.query(models.Depense)
        .filter(models.Depense.payeur_id == current_user.id, models.Depense.partagee == False)
        .order_by(models.Depense.date.desc())
        .all()
    )
    categories = db.query(models.Categorie).filter(models.Categorie.foyer_id == current_user.foyer_id).all()
    categories_par_id = {c.id: c.nom for c in categories}

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(["Date", "Catégorie", "Note", "Montant (€)"])
    for d in depenses:
        writer.writerow(
            [d.date.isoformat(), categories_par_id.get(d.categorie_id, "Autre"), d.note or "", f"{d.montant:.2f}"]
        )
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=depenses-perso.csv"},
    )
