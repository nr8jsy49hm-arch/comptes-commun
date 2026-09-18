from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/depenses", tags=["depenses"])


@router.get("/", response_model=List[schemas.Depense])
def lister_depenses(
    etiquette_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    requete = db.query(models.Depense).filter(models.Depense.foyer_id == current_user.foyer_id)
    if etiquette_id is not None:
        requete = requete.filter(models.Depense.etiquettes.any(models.Etiquette.id == etiquette_id))
    return requete.all()


@router.post("/", response_model=schemas.Depense)
def creer_depense(
    depense: schemas.DepenseCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    donnees = depense.model_dump(exclude={"etiquette_ids"})
    db_depense = models.Depense(**donnees, foyer_id=current_user.foyer_id)

    if depense.etiquette_ids:
        etiquettes = (
            db.query(models.Etiquette)
            .filter(
                models.Etiquette.id.in_(depense.etiquette_ids),
                models.Etiquette.foyer_id == current_user.foyer_id,
            )
            .all()
        )
        db_depense.etiquettes = etiquettes

    db.add(db_depense)
    db.commit()
    db.refresh(db_depense)
    return db_depense


@router.patch("/{depense_id}/etiquettes", response_model=schemas.Depense)
def modifier_etiquettes_depense(
    depense_id: int,
    payload: schemas.DepenseEtiquettesIn,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    depense = (
        db.query(models.Depense)
        .filter(models.Depense.id == depense_id, models.Depense.foyer_id == current_user.foyer_id)
        .first()
    )
    if not depense:
        raise HTTPException(status_code=404, detail="Dépense introuvable")

    etiquettes = (
        db.query(models.Etiquette)
        .filter(
            models.Etiquette.id.in_(payload.etiquette_ids),
            models.Etiquette.foyer_id == current_user.foyer_id,
        )
        .all()
    )
    depense.etiquettes = etiquettes
    db.commit()
    db.refresh(depense)
    return depense


@router.delete("/{depense_id}")
def supprimer_depense(
    depense_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    depense = (
        db.query(models.Depense)
        .filter(models.Depense.id == depense_id, models.Depense.foyer_id == current_user.foyer_id)
        .first()
    )
    if not depense:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    db.delete(depense)
    db.commit()
    return {"ok": True}
