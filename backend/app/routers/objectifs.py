from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/objectifs", tags=["objectifs"])


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
