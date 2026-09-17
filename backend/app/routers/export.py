import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/export", tags=["export"])


def _generer_csv(depenses, categories_par_id, payeurs_par_id, inclure_payeur=True):
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    entetes = ["Date", "Catégorie"]
    if inclure_payeur:
        entetes.append("Payé par")
    entetes += ["Note", "Montant (€)"]
    writer.writerow(entetes)

    for d in depenses:
        ligne = [d.date.isoformat(), categories_par_id.get(d.categorie_id, "Autre")]
        if inclure_payeur:
            ligne.append(payeurs_par_id.get(d.payeur_id, ""))
        ligne += [d.note or "", f"{d.montant:.2f}"]
        writer.writerow(ligne)

    buffer.seek(0)
    return buffer


@router.get("/depenses.csv")
def exporter_depenses_csv(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    depenses = (
        db.query(models.Depense)
        .filter(models.Depense.foyer_id == current_user.foyer_id, models.Depense.partagee == True)
        .order_by(models.Depense.date.desc())
        .all()
    )
    categories = db.query(models.Categorie).filter(models.Categorie.foyer_id == current_user.foyer_id).all()
    membres = db.query(models.Utilisateur).filter(models.Utilisateur.foyer_id == current_user.foyer_id).all()
    categories_par_id = {c.id: c.nom for c in categories}
    payeurs_par_id = {m.id: m.nom for m in membres}

    buffer = _generer_csv(depenses, categories_par_id, payeurs_par_id, inclure_payeur=True)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=depenses-communes.csv"},
    )
