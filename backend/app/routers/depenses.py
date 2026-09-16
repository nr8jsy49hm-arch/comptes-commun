from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/depenses", tags=["depenses"])


@router.get("/", response_model=List[schemas.Depense])
def lister_depenses(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return db.query(models.Depense).filter(models.Depense.foyer_id == current_user.foyer_id).all()


@router.post("/", response_model=schemas.Depense)
def creer_depense(
    depense: schemas.DepenseCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    db_depense = models.Depense(**depense.model_dump(), foyer_id=current_user.foyer_id)
    db.add(db_depense)
    db.commit()
    db.refresh(db_depense)
    return db_depense


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
