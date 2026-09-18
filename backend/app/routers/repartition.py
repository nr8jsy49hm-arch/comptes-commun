import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/repartition", tags=["repartition"])


def _obtenir_parts(foyer_id: int, db: Session, utilisateurs: List[models.Utilisateur]) -> dict[int, float]:
    """Renvoie {utilisateur_id: pourcentage}. Équirépartition par défaut (100/N) si aucune
    clé personnalisée valide n'est définie pour les membres actuels du foyer."""
    n = len(utilisateurs) or 1
    defaut = {u.id: round(100 / n, 4) for u in utilisateurs}
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
    """Calcule qui doit combien à qui, pour N membres, selon la clé de répartition définie
    (équirépartition par défaut). Chaque règlement ajuste les deux côtés (celui qui rembourse
    et celui qui est remboursé), pour que le solde retombe bien à zéro une fois soldé."""
    utilisateurs = db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == foyer_id).all()
    if len(utilisateurs) < 2:
        return []

    depenses = db.query(models.Depense).filter(
        models.Depense.foyer_id == foyer_id, models.Depense.partagee == True
    ).all()
    reglements = db.query(models.Reglement).filter(models.Reglement.foyer_id == foyer_id).all()

    total = sum(d.montant for d in depenses)
    parts = _obtenir_parts(foyer_id, db, utilisateurs)

    paye_par = {u.id: 0.0 for u in utilisateurs}
    for d in depenses:
        if d.payeur_id in paye_par:
            paye_par[d.payeur_id] += d.montant

    for r in reglements:
        if r.de_utilisateur_id in paye_par:
            paye_par[r.de_utilisateur_id] += r.montant
        if r.vers_utilisateur_id in paye_par:
            paye_par[r.vers_utilisateur_id] -= r.montant

    resultat = []
    for u in utilisateurs:
        part_u = total * parts.get(u.id, 100 / len(utilisateurs)) / 100
        solde = paye_par[u.id] - part_u
        resultat.append(schemas.BalanceResponse(utilisateur_id=u.id, nom=u.nom, solde=round(solde, 2)))
    return resultat


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
    return schemas.CleRepartitionOut(type=cle.type if cle else "equirepartition", parts=parts)


@router.post("/cle", response_model=schemas.CleRepartitionOut)
def definir_cle(
    payload: schemas.CleRepartitionIn,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    utilisateurs = db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == current_user.foyer_id).all()
    if len(utilisateurs) < 2:
        raise HTTPException(400, "La répartition personnalisée nécessite au moins deux membres dans le foyer")
    if set(payload.parts.keys()) != {u.id for u in utilisateurs}:
        raise HTTPException(400, "Les parts doivent couvrir exactement tous les membres actuels du foyer")
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
