from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/etiquettes", tags=["etiquettes"])


@router.get("/", response_model=List[schemas.Etiquette])
def lister_etiquettes(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return db.query(models.Etiquette).filter(models.Etiquette.foyer_id == current_user.foyer_id).all()


@router.post("/", response_model=schemas.Etiquette)
def creer_etiquette(
    payload: schemas.EtiquetteCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    nom = payload.nom.strip()
    existante = (
        db.query(models.Etiquette)
        .filter(models.Etiquette.foyer_id == current_user.foyer_id, models.Etiquette.nom == nom)
        .first()
    )
    if existante:
        return existante

    etiquette = models.Etiquette(nom=nom, foyer_id=current_user.foyer_id)
    db.add(etiquette)
    db.commit()
    db.refresh(etiquette)
    return etiquette


@router.delete("/{etiquette_id}")
def supprimer_etiquette(
    etiquette_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    etiquette = (
        db.query(models.Etiquette)
        .filter(models.Etiquette.id == etiquette_id, models.Etiquette.foyer_id == current_user.foyer_id)
        .first()
    )
    if not etiquette:
        raise HTTPException(status_code=404, detail="Étiquette introuvable")

    # Nettoie d'abord la table d'association (pas de cascade ORM déclaré côté Etiquette)
    db.execute(
        models.depense_etiquettes.delete().where(models.depense_etiquettes.c.etiquette_id == etiquette_id)
    )
    db.delete(etiquette)
    db.commit()
    return {"ok": True}
