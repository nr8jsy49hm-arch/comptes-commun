from .conftest import inscrire, entetes_auth


def test_inscription_et_connexion(client):
    data = inscrire(client)
    assert "access_token" in data
    assert data["utilisateur"]["nom"] == "Pierre"

    res = client.post(
        "/auth/login",
        data={"username": "pierre@test.fr", "password": "motdepasse123"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_connexion_mauvais_mot_de_passe_refusee(client):
    inscrire(client)
    res = client.post(
        "/auth/login",
        data={"username": "pierre@test.fr", "password": "mauvais_mdp"},
    )
    assert res.status_code == 401


def test_mot_de_passe_trop_court_refuse(client):
    res = client.post(
        "/auth/register",
        json={"nom": "Pierre", "email": "pierre@test.fr", "mot_de_passe": "court"},
    )
    assert res.status_code == 422


def test_rejoindre_foyer_existant(client):
    createur = inscrire(client, nom="Pierre", email="pierre@test.fr")
    foyer_id = createur["utilisateur"]["foyer_id"]

    partenaire = inscrire(
        client, nom="Orléanes", email="orleanes@test.fr", code_foyer=foyer_id
    )
    assert partenaire["utilisateur"]["foyer_id"] == foyer_id


def test_changer_mot_de_passe(client):
    data = inscrire(client)
    token = data["access_token"]

    res = client.post(
        "/auth/mot-de-passe",
        json={"mot_de_passe_actuel": "motdepasse123", "nouveau_mot_de_passe": "nouveaumdp456"},
        headers=entetes_auth(token),
    )
    assert res.status_code == 200

    # L'ancien mot de passe ne doit plus fonctionner
    res = client.post("/auth/login", data={"username": "pierre@test.fr", "password": "motdepasse123"})
    assert res.status_code == 401

    # Le nouveau, oui
    res = client.post("/auth/login", data={"username": "pierre@test.fr", "password": "nouveaumdp456"})
    assert res.status_code == 200


def test_question_secrete_et_reinitialisation(client):
    data = inscrire(client)
    token = data["access_token"]

    client.post(
        "/auth/question-secrete",
        json={"question": "Prénom de ton premier animal ?", "reponse": "Médor"},
        headers=entetes_auth(token),
    )

    res = client.post("/auth/mot-de-passe-oublie/question", json={"email": "pierre@test.fr"})
    assert res.json()["question"] == "Prénom de ton premier animal ?"

    # Mauvaise réponse -> refusé
    res = client.post(
        "/auth/mot-de-passe-oublie/reinitialiser",
        json={"email": "pierre@test.fr", "reponse": "Rex", "nouveau_mot_de_passe": "autremdp789"},
    )
    assert res.status_code == 401

    # Bonne réponse (insensible à la casse/espaces) -> accepté
    res = client.post(
        "/auth/mot-de-passe-oublie/reinitialiser",
        json={"email": "pierre@test.fr", "reponse": " médor ", "nouveau_mot_de_passe": "autremdp789"},
    )
    assert res.status_code == 200

    res = client.post("/auth/login", data={"username": "pierre@test.fr", "password": "autremdp789"})
    assert res.status_code == 200
