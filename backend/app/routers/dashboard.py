from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from .. import models, schemas
from ..database import get_db
from .repartition import calculer_balance

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=schemas.DashboardResponse)
def obtenir_dashboard(foyer_id: int, db: Session = Depends(get_db)):
    aujourdhui = date.today()
    depenses_mois = (
        db.query(models.Depense)
        .filter(
            models.Depense.foyer_id == foyer_id,
            models.Depense.date >= aujourdhui.replace(day=1),
        )
        .all()
    )

    total_mois = sum(d.montant for d in depenses_mois)

    par_categorie: dict[str, float] = {}
    for d in depenses_mois:
        nom_cat = d.categorie.nom if d.categorie else "Autre"
        par_categorie[nom_cat] = par_categorie.get(nom_cat, 0) + d.montant

    balances = calculer_balance(foyer_id=foyer_id, db=db)

    return schemas.DashboardResponse(
        total_mois=round(total_mois, 2),
        par_categorie={k: round(v, 2) for k, v in par_categorie.items()},
        balances=balances,
    )
