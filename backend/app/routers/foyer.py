import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/foyer", tags=["foyer"])

DUREE_VALIDITE_INVITATION = timedelta(days=7)


@router.get("/membres", response_model=List[schemas.UtilisateurOut])
def lister_membres(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == current_user.foyer_id).all()


@router.get("/invitations", response_model=List[schemas.Invitation])
def lister_invitations(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    """Liste les invitations créées pour ce foyer (actives ou non), les plus récentes d'abord."""
    return (
        db.query(models.Invitation)
        .filter(models.Invitation.foyer_id == current_user.foyer_id)
        .order_by(models.Invitation.created_at.desc())
        .all()
    )


@router.post("/invitations", response_model=schemas.Invitation)
def creer_invitation(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    """Crée un lien d'invitation à usage unique, valable 7 jours, pour rejoindre ce foyer."""
    token = secrets.token_urlsafe(32)
    invitation = models.Invitation(
        token=token,
        foyer_id=current_user.foyer_id,
        cree_par_id=current_user.id,
        expire_le=datetime.now(timezone.utc) + DUREE_VALIDITE_INVITATION,
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


@router.delete("/invitations/{invitation_id}")
def revoquer_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    invitation = (
        db.query(models.Invitation)
        .filter(models.Invitation.id == invitation_id, models.Invitation.foyer_id == current_user.foyer_id)
        .first()
    )
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation introuvable")
    db.delete(invitation)
    db.commit()
    return {"ok": True}
