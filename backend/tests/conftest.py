import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db

os.environ["TESTING"] = "1"  # empêche app.main de tenter de se connecter à la vraie base Postgres

from app.main import app  # noqa: E402 — importé après avoir posé TESTING
from app.limiter import limiter
from app import models  # noqa: F401 — enregistre tous les modèles sur Base avant create_all

# Le rate limiting (anti brute-force) n'a pas sa place dans les tests : plusieurs tests
# appellent /auth/register ou /auth/login à la suite et se feraient bloquer par erreur.
limiter.enabled = False

# Base de test sur fichier (pas ":memory:") : évite les pièges classiques de SQLite en
# mémoire où chaque nouvelle connexion peut se retrouver sur une base vide séparée.
# Chemin RELATIF exprès (pas tempfile/chemin absolu Windows) : un chemin Windows avec
# des antislashs inséré dans une URL sqlite:/// peut être mal interprété.
_DB_PATH = "test_comptes_communs.db"
if os.path.exists(_DB_PATH):
    os.remove(_DB_PATH)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def base_de_test():
    """Recrée un schéma propre avant chaque test, pour une isolation totale."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        print("\n[DIAGNOSTIC] Tables après create_all:", tables)
        print("[DIAGNOSTIC] Chemin de la base:", engine.url)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def inscrire(client, nom="Pierre", email="pierre@test.fr", mot_de_passe="motdepasse123", **kwargs):
    payload = {"nom": nom, "email": email, "mot_de_passe": mot_de_passe, **kwargs}
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 200, res.text
    return res.json()


def entetes_auth(token):
    return {"Authorization": f"Bearer {token}"}