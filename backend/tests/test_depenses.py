from datetime import date
from .conftest import inscrire, entetes_auth


def test_creer_lister_supprimer_depense(client):
    data = inscrire(client)
    token = data["access_token"]
    headers = entetes_auth(token)
    payeur_id = data["utilisateur"]["id"]

    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()

    res = client.post(
        "/depenses/",
        json={
            "montant": 42.5,
            "date": "2026-06-15",
            "note": "Supermarché",
            "categorie_id": cat["id"],
            "payeur_id": payeur_id,
        },
        headers=headers,
    )
    assert res.status_code == 200
    depense_id = res.json()["id"]

    res = client.get("/depenses/", headers=headers)
    assert len(res.json()) == 1
    assert res.json()[0]["montant"] == 42.5

    res = client.delete(f"/depenses/{depense_id}", headers=headers)
    assert res.status_code == 200
    assert client.get("/depenses/", headers=headers).json() == []


def test_renommer_categorie(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])

    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()
    res = client.patch(f"/categories/{cat['id']}", json={"nom": "Alimentation"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["nom"] == "Alimentation"


def test_suppression_categorie_bloquee_si_depenses(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]

    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()
    client.post(
        "/depenses/",
        json={"montant": 10, "date": "2026-06-01", "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    )

    res = client.delete(f"/categories/{cat['id']}", headers=headers)
    assert res.status_code == 400


def test_depense_personnelle_isolee_du_commun(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]

    cat = client.post("/categories/", json={"nom": "Loisirs"}, headers=headers).json()
    client.post(
        "/depenses/",
        json={
            "montant": 30,
            "date": date.today().isoformat(),
            "categorie_id": cat["id"],
            "payeur_id": payeur_id,
            "partagee": False,
        },
        headers=headers,
    )

    # Le dashboard commun ne doit rien voir de cette dépense perso
    dashboard = client.get("/dashboard/", headers=headers).json()
    assert dashboard["total_mois"] == 0

    # Mais le dashboard solo, oui
    solo = client.get("/solo/dashboard", headers=headers).json()
    assert solo["total_mois"] == 30
