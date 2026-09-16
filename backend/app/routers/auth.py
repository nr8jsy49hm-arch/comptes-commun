from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token)
def register(payload: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    existant = db.query(models.Utilisateur).filter(models.Utilisateur.email == payload.email).first()
    if existant:
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cet email")

    # Détermine le foyer : soit on en crée un nouveau, soit on rejoint un foyer existant
    if payload.code_foyer:
        foyer = db.query(models.Foyer).filter(models.Foyer.id == payload.code_foyer).first()
        if not foyer:
            raise HTTPException(status_code=404, detail="Foyer introuvable avec ce code")
    else:
        foyer = models.Foyer(nom=payload.nom_foyer or f"Foyer de {payload.nom}")
        db.add(foyer)
        db.commit()
        db.refresh(foyer)

    utilisateur = models.Utilisateur(
        nom=payload.nom,
        email=payload.email,
        mot_de_passe_hash=hash_password(payload.mot_de_passe),
        foyer_id=foyer.id,
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)

    token = create_access_token({"sub": str(utilisateur.id)})
    return schemas.Token(access_token=token, utilisateur=utilisateur)


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm attend "username" : on y met l'email
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.email == form_data.username).first()
    if not utilisateur or not verify_password(form_data.password, utilisateur.mot_de_passe_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token({"sub": str(utilisateur.id)})
    return schemas.Token(access_token=token, utilisateur=utilisateur)


@router.get("/me", response_model=schemas.UtilisateurOut)
def me(current_user: models.Utilisateur = Depends(get_current_user)):
    return current_user
