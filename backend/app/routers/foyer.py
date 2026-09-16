from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/foyer", tags=["foyer"])


@router.get("/membres", response_model=List[schemas.UtilisateurOut])
def lister_membres(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == current_user.foyer_id).all()
