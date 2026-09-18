from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from .. import models, schemas
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token
from ..deps import get_current_user
from ..limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/invitations/{token}", response_model=schemas.InvitationInfo)
def verifier_invitation(token: str, db: Session = Depends(get_db)):
    """Route publique (avant inscription) : dit si un jeton d'invitation est valide, et le nom du foyer si oui."""
    invitation = db.query(models.Invitation).filter(models.Invitation.token == token).first()
    if not invitation or invitation.utilisee_le or invitation.expire_le < datetime.now(timezone.utc):
        return schemas.InvitationInfo(valide=False)
    foyer = db.query(models.Foyer).filter(models.Foyer.id == invitation.foyer_id).first()
    return schemas.InvitationInfo(valide=True, nom_foyer=foyer.nom if foyer else None)


@router.post("/register", response_model=schemas.Token)
@limiter.limit("5/minute")
def register(request: Request, payload: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    existant = db.query(models.Utilisateur).filter(models.Utilisateur.email == payload.email).first()
    if existant:
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cet email")

    # Détermine le foyer : soit on en crée un nouveau, soit on rejoint un foyer existant via invitation
    invitation = None
    if payload.invitation_token:
        invitation = (
            db.query(models.Invitation).filter(models.Invitation.token == payload.invitation_token).first()
        )
        if (
            not invitation
            or invitation.utilisee_le
            or invitation.expire_le < datetime.now(timezone.utc)
        ):
            raise HTTPException(status_code=400, detail="Invitation invalide, expirée ou déjà utilisée")
        foyer = db.query(models.Foyer).filter(models.Foyer.id == invitation.foyer_id).first()
        if not foyer:
            raise HTTPException(status_code=404, detail="Foyer introuvable pour cette invitation")
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
        question_secrete=payload.question_secrete or None,
        reponse_secrete_hash=hash_password(payload.reponse_secrete.strip().lower())
        if payload.reponse_secrete
        else None,
    )
    db.add(utilisateur)

    if invitation:
        invitation.utilisee_le = datetime.now(timezone.utc)

    db.commit()
    db.refresh(utilisateur)

    token = create_access_token({"sub": str(utilisateur.id)})
    return schemas.Token(access_token=token, utilisateur=utilisateur)


@router.post("/login", response_model=schemas.Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm attend "username" : on y met l'email
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.email == form_data.username).first()
    if not utilisateur or not verify_password(form_data.password, utilisateur.mot_de_passe_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token({"sub": str(utilisateur.id)})
    return schemas.Token(access_token=token, utilisateur=utilisateur)


@router.get("/me", response_model=schemas.UtilisateurOut)
def me(current_user: models.Utilisateur = Depends(get_current_user)):
    return current_user


@router.post("/mot-de-passe")
def changer_mot_de_passe(
    payload: schemas.ChangerMotDePasse,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    if not verify_password(payload.mot_de_passe_actuel, current_user.mot_de_passe_hash):
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")

    current_user.mot_de_passe_hash = hash_password(payload.nouveau_mot_de_passe)
    db.commit()
    return {"ok": True}


@router.post("/question-secrete")
def definir_question_secrete(
    payload: schemas.DefinirQuestionSecrete,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    current_user.question_secrete = payload.question
    current_user.reponse_secrete_hash = hash_password(payload.reponse.strip().lower())
    db.commit()
    return {"ok": True}


@router.get("/question-secrete", response_model=schemas.MotDePasseOublieQuestion)
def obtenir_ma_question_secrete(
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return schemas.MotDePasseOublieQuestion(question=current_user.question_secrete)


@router.post("/mot-de-passe-oublie/question", response_model=schemas.MotDePasseOublieQuestion)
@limiter.limit("5/minute")
def obtenir_question_secrete(request: Request, payload: schemas.MotDePasseOublieDemande, db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.email == payload.email).first()
    # Réponse volontairement neutre si l'email est inconnu ou sans question définie,
    # pour ne pas révéler quels emails existent.
    if not utilisateur or not utilisateur.question_secrete:
        return schemas.MotDePasseOublieQuestion(question=None)
    return schemas.MotDePasseOublieQuestion(question=utilisateur.question_secrete)


@router.post("/mot-de-passe-oublie/reinitialiser")
@limiter.limit("5/minute")
def reinitialiser_mot_de_passe(
    request: Request, payload: schemas.MotDePasseOublieReinitialiser, db: Session = Depends(get_db)
):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.email == payload.email).first()
    if (
        not utilisateur
        or not utilisateur.reponse_secrete_hash
        or not verify_password(payload.reponse.strip().lower(), utilisateur.reponse_secrete_hash)
    ):
        raise HTTPException(status_code=401, detail="Réponse incorrecte")

    utilisateur.mot_de_passe_hash = hash_password(payload.nouveau_mot_de_passe)
    db.commit()
    return {"ok": True}


@router.delete("/compte")
def supprimer_compte(
    payload: schemas.SupprimerCompte,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    if not verify_password(payload.mot_de_passe, current_user.mot_de_passe_hash):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    # Nettoie d'abord les données strictement personnelles (sans impact sur l'autre membre)
    db.query(models.BudgetPersonnel).filter(models.BudgetPersonnel.utilisateur_id == current_user.id).delete()
    db.query(models.Depense).filter(
        models.Depense.payeur_id == current_user.id, models.Depense.partagee == False
    ).delete()
    db.commit()

    try:
        db.delete(current_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=(
                "Impossible de supprimer ce compte : il reste des dépenses ou règlements communs "
                "qui le référencent. Contacte-nous si tu veux qu'on ajoute un vrai transfert de "
                "propriété de ces données avant suppression."
            ),
        )

    return {"ok": True}
