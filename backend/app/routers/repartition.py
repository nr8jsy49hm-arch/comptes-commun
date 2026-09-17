import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/repartition", tags=["repartition"])


def _obtenir_parts(foyer_id: int, db: Session, utilisateurs: List[models.Utilisateur]) -> dict[int, float]:
    """Renvoie {utilisateur_id: pourcentage}. 50/50 par défaut si aucune clé personnalisée valide."""
    defaut = {u.id: 50.0 for u in utilisateurs}
    cle = db.query(models.CleRepartition).filter(models.CleRepartition.foyer_id == foyer_id).first()
    if cle and cle.type == "personnalisee" and cle.valeur:
        try:
            parts = {int(k): float(v) for k, v in json.loads(cle.valeur).items()}
            if set(parts.keys()) == {u.id for u in utilisateurs}:
                return parts
        except (ValueError, TypeError):
            pass
    return defaut


def _calculer_balance(foyer_id: int, db: Session) -> List[schemas.BalanceResponse]:
    """Calcule qui doit combien à qui, selon la clé de répartition définie (50/50 par défaut)."""
    utilisateurs = db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == foyer_id).all()
    depenses = db.query(models.Depense).filter(
        models.Depense.foyer_id == foyer_id, models.Depense.partagee == True
    ).all()
    reglements = db.query(models.Reglement).filter(models.Reglement.foyer_id == foyer_id).all()

    if len(utilisateurs) != 2:
        # MVP pensé pour un couple ; à généraliser plus tard pour N utilisateurs
        return []

    u1, u2 = utilisateurs[0], utilisateurs[1]
    total = sum(d.montant for d in depenses)

    parts = _obtenir_parts(foyer_id, db, utilisateurs)
    part_u1 = total * parts.get(u1.id, 50.0) / 100
    part_u2 = total * parts.get(u2.id, 50.0) / 100

    paye_par_u1 = sum(d.montant for d in depenses if d.payeur_id == u1.id)
    paye_par_u2 = sum(d.montant for d in depenses if d.payeur_id == u2.id)

    for r in reglements:
        if r.de_utilisateur_id == u1.id:
            paye_par_u1 += r.montant
        elif r.de_utilisateur_id == u2.id:
            paye_par_u2 += r.montant

    solde_u1 = paye_par_u1 - part_u1
    solde_u2 = paye_par_u2 - part_u2

    return [
        schemas.BalanceResponse(utilisateur_id=u1.id, nom=u1.nom, solde=round(solde_u1, 2)),
        schemas.BalanceResponse(utilisateur_id=u2.id, nom=u2.nom, solde=round(solde_u2, 2)),
    ]


@router.get("/balance", response_model=List[schemas.BalanceResponse])
def calculer_balance(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return _calculer_balance(current_user.foyer_id, db)


@router.get("/reglements", response_model=List[schemas.Reglement])
def lister_reglements(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    return (
        db.query(models.Reglement)
        .filter(models.Reglement.foyer_id == current_user.foyer_id)
        .order_by(models.Reglement.date.desc())
        .all()
    )


@router.post("/reglements", response_model=schemas.Reglement)
def creer_reglement(
    reglement: schemas.ReglementCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    db_reglement = models.Reglement(**reglement.model_dump(), foyer_id=current_user.foyer_id)
    db.add(db_reglement)
    db.commit()
    db.refresh(db_reglement)
    return db_reglement


# ---------- Clé de répartition ----------

@router.get("/cle", response_model=schemas.CleRepartitionOut)
def obtenir_cle(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    utilisateurs = db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == current_user.foyer_id).all()
    parts = _obtenir_parts(current_user.foyer_id, db, utilisateurs)
    cle = db.query(models.CleRepartition).filter(models.CleRepartition.foyer_id == current_user.foyer_id).first()
    return schemas.CleRepartitionOut(type=cle.type if cle else "50_50", parts=parts)


@router.post("/cle", response_model=schemas.CleRepartitionOut)
def definir_cle(
    payload: schemas.CleRepartitionIn,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    utilisateurs = db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == current_user.foyer_id).all()
    if len(utilisateurs) != 2:
        raise HTTPException(400, "La répartition personnalisée nécessite exactement deux membres dans le foyer")
    if set(payload.parts.keys()) != {u.id for u in utilisateurs}:
        raise HTTPException(400, "Les parts doivent couvrir exactement les deux membres du foyer")
    if abs(sum(payload.parts.values()) - 100) > 0.5:
        raise HTTPException(400, "Les parts doivent totaliser 100%")

    cle = db.query(models.CleRepartition).filter(models.CleRepartition.foyer_id == current_user.foyer_id).first()
    valeur_json = json.dumps(payload.parts)
    if cle:
        cle.type = "personnalisee"
        cle.valeur = valeur_json
    else:
        cle = models.CleRepartition(type="personnalisee", valeur=valeur_json, foyer_id=current_user.foyer_id)
        db.add(cle)
    db.commit()

    return schemas.CleRepartitionOut(type="personnalisee", parts=payload.parts)


@router.delete("/cle")
def reinitialiser_cle(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    db.query(models.CleRepartition).filter(models.CleRepartition.foyer_id == current_user.foyer_id).delete()
    db.commit()
    return {"ok": True}
