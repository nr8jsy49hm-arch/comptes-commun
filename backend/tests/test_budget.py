from datetime import date
from .conftest import inscrire, entetes_auth


def test_budget_et_reste_a_vivre(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]

    res = client.post("/budgets/", json={"montant": 500}, headers=headers)
    assert res.status_code == 200

    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()
    client.post(
        "/depenses/",
        json={"montant": 120, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    )

    dashboard = client.get("/dashboard/", headers=headers).json()
    assert dashboard["budget_mois"] == 500
    assert dashboard["reste_a_vivre"] == 380


def test_budget_mis_a_jour_pas_duplique(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])

    client.post("/budgets/", json={"montant": 400}, headers=headers)
    res = client.post("/budgets/", json={"montant": 600}, headers=headers)
    assert res.status_code == 200

    courant = client.get("/budgets/mois-courant", headers=headers).json()
    assert courant["montant"] == 600


def test_pas_de_budget_pas_de_reste_a_vivre(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    dashboard = client.get("/dashboard/", headers=headers).json()
    assert dashboard["budget_mois"] is None
    assert dashboard["reste_a_vivre"] is None
