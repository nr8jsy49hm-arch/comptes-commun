import os
from datetime import date, datetime
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import inspect

from .. import models
from ..database import engine, SessionLocal

router = APIRouter(prefix="/admin", tags=["admin"])

BACKUP_SECRET = os.getenv("BACKUP_SECRET")


def _serialiser(valeur):
    if isinstance(valeur, (datetime, date)):
        return valeur.isoformat()
    return valeur


@router.get("/backup")
def sauvegarde_complete(x_backup_secret: str = Header(default=None)):
    """
    Export JSON complet de toutes les tables — utilisé par la sauvegarde automatique
    GitHub Actions (voir .github/workflows/backup.yml). Protégé par un secret partagé,
    pas par l'authentification utilisateur classique : ce n'est pas une donnée personnelle
    d'un seul compte, mais un instantané complet de la base, à réserver à un usage
    d'administration/sauvegarde.
    """
    if not BACKUP_SECRET:
        raise HTTPException(status_code=503, detail="BACKUP_SECRET n'est pas configurée sur le serveur")
    if x_backup_secret != BACKUP_SECRET:
        raise HTTPException(status_code=401, detail="Secret de sauvegarde incorrect")

    db = SessionLocal()
    try:
        inspecteur = inspect(engine)
        dump = {}
        for nom_table in inspecteur.get_table_names():
            lignes = db.execute(models.Base.metadata.tables[nom_table].select()).mappings().all()
            dump[nom_table] = [{k: _serialiser(v) for k, v in ligne.items()} for ligne in lignes]
        return JSONResponse(
            content={"genere_le": datetime.utcnow().isoformat(), "tables": dump},
            headers={"Content-Disposition": "attachment; filename=backup.json"},
        )
    finally:
        db.close()
