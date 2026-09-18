from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user
from ..recurrentes import generer_recurrentes_du_mois

router = APIRouter(prefix="/depenses-recurrentes", tags=["depenses-recurrentes"])


@router.get("/", response_model=List[schemas.DepenseRecurrente])
def lister_recurrentes(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return (
        db.query(models.DepenseRecurrente)
        .filter(models.DepenseRecurrente.foyer_id == current_user.foyer_id)
        .all()
    )


@router.post("/", response_model=schemas.DepenseRecurrente)
def creer_recurrente(
    payload: schemas.DepenseRecurrenteCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    regle = models.DepenseRecurrente(**payload.model_dump(), foyer_id=current_user.foyer_id)
    db.add(regle)
    db.commit()
    db.refresh(regle)
    # Génère tout de suite la dépense du mois si on est déjà passé son jour habituel,
    # pour que la première règle créée ne "saute" pas le mois en cours.
    generer_recurrentes_du_mois(current_user.foyer_id, db)
    return regle


@router.patch("/{recurrente_id}", response_model=schemas.DepenseRecurrente)
def modifier_recurrente(
    recurrente_id: int,
    payload: schemas.DepenseRecurrenteUpdate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    regle = (
        db.query(models.DepenseRecurrente)
        .filter(
            models.DepenseRecurrente.id == recurrente_id,
            models.DepenseRecurrente.foyer_id == current_user.foyer_id,
        )
        .first()
    )
    if not regle:
        raise HTTPException(status_code=404, detail="Dépense récurrente introuvable")

    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(regle, champ, valeur)

    db.commit()
    db.refresh(regle)
    return regle


@router.delete("/{recurrente_id}")
def supprimer_recurrente(
    recurrente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    regle = (
        db.query(models.DepenseRecurrente)
        .filter(
            models.DepenseRecurrente.id == recurrente_id,
            models.DepenseRecurrente.foyer_id == current_user.foyer_id,
        )
        .first()
    )
    if not regle:
        raise HTTPException(status_code=404, detail="Dépense récurrente introuvable")
    db.delete(regle)
    db.commit()
    return {"ok": True}
