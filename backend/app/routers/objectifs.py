from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from calendar import monthrange
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/objectifs", tags=["objectifs"])

NOMS_MOIS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


def _vers_schema(obj: models.Objectif) -> schemas.Objectif:
    montant_actuel = sum(v.montant for v in obj.versements)
    return schemas.Objectif(
        id=obj.id,
        nom=obj.nom,
        montant_cible=obj.montant_cible,
        date_cible=obj.date_cible,
        montant_actuel=round(montant_actuel, 2),
        foyer_id=obj.foyer_id,
    )


@router.get("/", response_model=List[schemas.Objectif])
def lister_objectifs(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    objectifs = db.query(models.Objectif).filter(models.Objectif.foyer_id == current_user.foyer_id).all()
    return [_vers_schema(o) for o in objectifs]


@router.post("/", response_model=schemas.Objectif)
def creer_objectif(
    payload: schemas.ObjectifCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    db_objectif = models.Objectif(**payload.model_dump(), foyer_id=current_user.foyer_id)
    db.add(db_objectif)
    db.commit()
    db.refresh(db_objectif)
    return _vers_schema(db_objectif)


@router.delete("/{objectif_id}")
def supprimer_objectif(
    objectif_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    objectif = (
        db.query(models.Objectif)
        .filter(models.Objectif.id == objectif_id, models.Objectif.foyer_id == current_user.foyer_id)
        .first()
    )
    if not objectif:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    db.delete(objectif)
    db.commit()
    return {"ok": True}


@router.post("/{objectif_id}/versements", response_model=schemas.Objectif)
def ajouter_versement(
    objectif_id: int,
    payload: schemas.VersementObjectifCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    objectif = (
        db.query(models.Objectif)
        .filter(models.Objectif.id == objectif_id, models.Objectif.foyer_id == current_user.foyer_id)
        .first()
    )
    if not objectif:
        raise HTTPException(status_code=404, detail="Objectif introuvable")

    versement = models.VersementObjectif(montant=payload.montant, date=date.today(), objectif_id=objectif.id)
    db.add(versement)
    db.commit()
    db.refresh(objectif)
    return _vers_schema(objectif)


@router.get("/evolution/{annee}", response_model=List[schemas.MoisEvolutionEpargne])
def evolution_epargne(
    annee: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    """Total versé (tous objectifs confondus) chaque mois de l'année, pour le graphique d'épargne."""
    objectifs_ids = [
        o.id for o in db.query(models.Objectif).filter(models.Objectif.foyer_id == current_user.foyer_id).all()
    ]
    resultat = []
    for mois in range(1, 13):
        debut = date(annee, mois, 1)
        fin = date(annee, mois, monthrange(annee, mois)[1])
        total = 0.0
        if objectifs_ids:
            versements = (
                db.query(models.VersementObjectif)
                .filter(
                    models.VersementObjectif.objectif_id.in_(objectifs_ids),
                    models.VersementObjectif.date >= debut,
                    models.VersementObjectif.date <= fin,
                )
                .all()
            )
            total = sum(v.montant for v in versements)
        resultat.append(
            schemas.MoisEvolutionEpargne(mois=mois, nom_mois=NOMS_MOIS[mois - 1], total_verse=round(total, 2))
        )
    return resultat
