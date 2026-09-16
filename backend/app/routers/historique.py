from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from calendar import monthrange
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/historique", tags=["historique"])

NOMS_MOIS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


def _plage_mois(annee: int, mois: int) -> tuple[date, date]:
    debut = date(annee, mois, 1)
    fin = date(annee, mois, monthrange(annee, mois)[1])
    return debut, fin


@router.get("/annees", response_model=List[int])
def lister_annees(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    annees = (
        db.query(extract("year", models.Depense.date))
        .filter(models.Depense.foyer_id == current_user.foyer_id)
        .distinct()
        .all()
    )
    resultat = sorted({int(a[0]) for a in annees}, reverse=True)
    annee_courante = date.today().year
    if annee_courante not in resultat:
        resultat.insert(0, annee_courante)
    return resultat


@router.get("/{annee}", response_model=List[schemas.MoisHistorique])
def historique_annee(
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
                models.Depense.foyer_id == current_user.foyer_id,
                models.Depense.partagee == True,
                models.Depense.date >= debut,
                models.Depense.date <= fin,
            )
            .all()
        )
        total = sum(d.montant for d in depenses)

        budget = (
            db.query(models.Budget)
            .filter(models.Budget.foyer_id == current_user.foyer_id, models.Budget.mois == debut)
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


@router.get("/{annee}/{mois}/categories", response_model=dict[str, float])
def historique_mois_par_categorie(
    annee: int,
    mois: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    debut, fin = _plage_mois(annee, mois)
    depenses = (
        db.query(models.Depense)
        .filter(
            models.Depense.foyer_id == current_user.foyer_id,
            models.Depense.partagee == True,
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
