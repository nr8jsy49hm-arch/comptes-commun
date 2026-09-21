import secrets
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user
from ..limiter import limiter

router = APIRouter(prefix="/cagnottes", tags=["cagnottes"])


def _vers_schema(c: models.Cagnotte) -> schemas.Cagnotte:
    return schemas.Cagnotte(
        id=c.id,
        nom=c.nom,
        description=c.description,
        montant_cible=c.montant_cible,
        date_limite=c.date_limite,
        cloturee=c.cloturee,
        token_public=c.token_public,
        montant_total=c.montant_total,
        nb_contributions=c.nb_contributions,
    )


def _vers_schema_publique(c: models.Cagnotte) -> schemas.CagnottePublique:
    return schemas.CagnottePublique(
        nom=c.nom,
        description=c.description,
        montant_cible=c.montant_cible,
        date_limite=c.date_limite,
        cloturee=c.cloturee,
        montant_total=c.montant_total,
        contributions=[
            schemas.ContributionCagnotte.model_validate(contrib)
            for contrib in sorted(c.contributions, key=lambda x: x.date, reverse=True)
        ],
    )


# ---------- Gestion (authentifiée, membres du foyer) ----------

@router.get("/", response_model=List[schemas.Cagnotte])
def lister_cagnottes(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    cagnottes = db.query(models.Cagnotte).filter(models.Cagnotte.foyer_id == current_user.foyer_id).all()
    return [_vers_schema(c) for c in cagnottes]


@router.post("/", response_model=schemas.Cagnotte)
def creer_cagnotte(
    payload: schemas.CagnotteCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    cagnotte = models.Cagnotte(
        **payload.model_dump(),
        token_public=secrets.token_urlsafe(20),
        foyer_id=current_user.foyer_id,
        createur_id=current_user.id,
    )
    db.add(cagnotte)
    db.commit()
    db.refresh(cagnotte)
    return _vers_schema(cagnotte)


@router.patch("/{cagnotte_id}", response_model=schemas.Cagnotte)
def modifier_cagnotte(
    cagnotte_id: int,
    payload: schemas.CagnotteUpdate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    cagnotte = (
        db.query(models.Cagnotte)
        .filter(models.Cagnotte.id == cagnotte_id, models.Cagnotte.foyer_id == current_user.foyer_id)
        .first()
    )
    if not cagnotte:
        raise HTTPException(status_code=404, detail="Cagnotte introuvable")
    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(cagnotte, champ, valeur)
    db.commit()
    db.refresh(cagnotte)
    return _vers_schema(cagnotte)


@router.post("/{cagnotte_id}/regenerer-lien", response_model=schemas.Cagnotte)
def regenerer_lien(
    cagnotte_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    """Invalide l'ancien lien public et en génère un nouveau (utile si le lien a fuité)."""
    cagnotte = (
        db.query(models.Cagnotte)
        .filter(models.Cagnotte.id == cagnotte_id, models.Cagnotte.foyer_id == current_user.foyer_id)
        .first()
    )
    if not cagnotte:
        raise HTTPException(status_code=404, detail="Cagnotte introuvable")
    cagnotte.token_public = secrets.token_urlsafe(20)
    db.commit()
    db.refresh(cagnotte)
    return _vers_schema(cagnotte)


@router.delete("/{cagnotte_id}")
def supprimer_cagnotte(
    cagnotte_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    cagnotte = (
        db.query(models.Cagnotte)
        .filter(models.Cagnotte.id == cagnotte_id, models.Cagnotte.foyer_id == current_user.foyer_id)
        .first()
    )
    if not cagnotte:
        raise HTTPException(status_code=404, detail="Cagnotte introuvable")
    db.delete(cagnotte)
    db.commit()
    return {"ok": True}


@router.post("/{cagnotte_id}/contribuer", response_model=schemas.Cagnotte)
def contribuer_depuis_appli(
    cagnotte_id: int,
    payload: schemas.ContributionCagnotteCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    """Contribution par un membre du foyer déjà connecté (nom pris depuis son compte,
    pas besoin de le ressaisir)."""
    cagnotte = (
        db.query(models.Cagnotte)
        .filter(models.Cagnotte.id == cagnotte_id, models.Cagnotte.foyer_id == current_user.foyer_id)
        .first()
    )
    if not cagnotte:
        raise HTTPException(status_code=404, detail="Cagnotte introuvable")
    if cagnotte.cloturee:
        raise HTTPException(status_code=400, detail="Cette cagnotte est clôturée")

    contribution = models.ContributionCagnotte(
        nom_contributeur=current_user.nom,
        montant=payload.montant,
        message=payload.message,
        date=date.today(),
        cagnotte_id=cagnotte.id,
    )
    db.add(contribution)
    db.commit()
    db.refresh(cagnotte)
    return _vers_schema(cagnotte)


# ---------- Accès via le lien partagé : vue publique, contribution avec compte ----------

@router.get("/publique/{token}", response_model=schemas.CagnottePublique)
@limiter.limit("30/minute")
def voir_cagnotte_publique(token: str, request: Request, db: Session = Depends(get_db)):
    cagnotte = db.query(models.Cagnotte).filter(models.Cagnotte.token_public == token).first()
    if not cagnotte:
        raise HTTPException(status_code=404, detail="Cette cagnotte n'existe pas ou plus")
    return _vers_schema_publique(cagnotte)


@router.post("/publique/{token}/contribuer", response_model=schemas.CagnottePublique)
def contribuer_publiquement(
    token: str,
    payload: schemas.ContributionCagnotteCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    """
    Contribuer via le lien public nécessite désormais un vrai compte connecté (peu importe
    son foyer — pas besoin d'être membre du foyer qui a créé la cagnotte). La visualisation
    (route GET ci-dessus) reste, elle, accessible sans connexion, pour que les gens sachent
    à quoi ils sont invités avant de créer un compte.
    """
    cagnotte = db.query(models.Cagnotte).filter(models.Cagnotte.token_public == token).first()
    if not cagnotte:
        raise HTTPException(status_code=404, detail="Cette cagnotte n'existe pas ou plus")
    if cagnotte.cloturee:
        raise HTTPException(
            status_code=400, detail="Cette cagnotte est clôturée, elle n'accepte plus de contributions"
        )

    contribution = models.ContributionCagnotte(
        nom_contributeur=current_user.nom,
        montant=payload.montant,
        message=payload.message,
        date=date.today(),
        cagnotte_id=cagnotte.id,
    )
    db.add(contribution)
    db.commit()
    db.refresh(cagnotte)
    return _vers_schema_publique(cagnotte)
