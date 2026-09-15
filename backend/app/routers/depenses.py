from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/depenses", tags=["depenses"])


@router.get("/", response_model=List[schemas.Depense])
def lister_depenses(foyer_id: int, db: Session = Depends(get_db)):
    return db.query(models.Depense).filter(models.Depense.foyer_id == foyer_id).all()


@router.post("/", response_model=schemas.Depense)
def creer_depense(foyer_id: int, depense: schemas.DepenseCreate, db: Session = Depends(get_db)):
    db_depense = models.Depense(**depense.model_dump(), foyer_id=foyer_id)
    db.add(db_depense)
    db.commit()
    db.refresh(db_depense)
    return db_depense


@router.delete("/{depense_id}")
def supprimer_depense(depense_id: int, db: Session = Depends(get_db)):
    depense = db.query(models.Depense).filter(models.Depense.id == depense_id).first()
    if not depense:
        raise HTTPException(status_code=404, detail="Dépense introuvable")
    db.delete(depense)
    db.commit()
    return {"ok": True}
