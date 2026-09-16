from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[schemas.Categorie])
def lister_categories(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return db.query(models.Categorie).filter(models.Categorie.foyer_id == current_user.foyer_id).all()


@router.post("/", response_model=schemas.Categorie)
def creer_categorie(
    categorie: schemas.CategorieCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    db_categorie = models.Categorie(**categorie.model_dump(), foyer_id=current_user.foyer_id)
    db.add(db_categorie)
    db.commit()
    db.refresh(db_categorie)
    return db_categorie


@router.delete("/{categorie_id}")
def supprimer_categorie(
    categorie_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    categorie = (
        db.query(models.Categorie)
        .filter(models.Categorie.id == categorie_id, models.Categorie.foyer_id == current_user.foyer_id)
        .first()
    )
    if not categorie:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    db.delete(categorie)
    db.commit()
    return {"ok": True}
