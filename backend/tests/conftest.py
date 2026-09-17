import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

import os

from app.database import Base, get_db

os.environ["TESTING"] = "1"  # empêche app.main de tenter de se connecter à la vraie base Postgres

from app.main import app  # noqa: E402 — importé après avoir posé TESTING
from app.limiter import limiter
import app.models  # noqa: F401 — enregistre tous les modèles sur Base avant create_all

# Le rate limiting (anti brute-force) n'a pas sa place dans les tests : plusieurs tests
# appellent /auth/register ou /auth/login à la suite et se feraient bloquer par erreur.
limiter.enabled = False

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def base_de_test():
    """Recrée un schéma propre avant chaque test, pour une isolation totale."""
    Base.metadata.create_all(bind=engine)
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
