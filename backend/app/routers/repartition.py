from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/repartition", tags=["repartition"])


def _calculer_balance(foyer_id: int, db: Session) -> List[schemas.BalanceResponse]:
    """
    Calcule qui doit combien à qui, en supposant une répartition 50/50 par défaut.
    (La logique de clé de répartition personnalisée sera branchée ici plus tard.)
    """
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
    part_chacun = total / 2

    paye_par_u1 = sum(d.montant for d in depenses if d.payeur_id == u1.id)
    paye_par_u2 = sum(d.montant for d in depenses if d.payeur_id == u2.id)

    for r in reglements:
        if r.de_utilisateur_id == u1.id:
            paye_par_u1 += r.montant
        elif r.de_utilisateur_id == u2.id:
            paye_par_u2 += r.montant

    solde_u1 = paye_par_u1 - part_chacun
    solde_u2 = paye_par_u2 - part_chacun

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
