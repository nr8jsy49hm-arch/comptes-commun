import os
from .conftest import inscrire, entetes_auth


def test_backup_refuse_sans_secret_configure(client):
    # Dans les tests, BACKUP_SECRET n'est pas définie -> 503 attendu
    res = client.get("/admin/backup")
    assert res.status_code == 503


def test_backup_avec_secret(client, monkeypatch):
    monkeypatch.setenv("BACKUP_SECRET", "secret-de-test")
    from app.routers import admin as admin_module

    monkeypatch.setattr(admin_module, "BACKUP_SECRET", "secret-de-test")

    inscrire(client)

    # Mauvais secret -> refusé
    res = client.get("/admin/backup", headers={"x-backup-secret": "mauvais"})
    assert res.status_code == 401

    # Bon secret -> la sauvegarde contient bien la table utilisateurs avec notre compte
    res = client.get("/admin/backup", headers={"x-backup-secret": "secret-de-test"})
    assert res.status_code == 200
    data = res.json()
    assert "tables" in data
    assert any(u["email"] == "pierre@test.fr" for u in data["tables"]["utilisateurs"])
