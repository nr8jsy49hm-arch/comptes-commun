from datetime import date
from .conftest import inscrire, entetes_auth


def test_definir_et_lister_enveloppe(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]
    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()

    res = client.post("/budgets/categories", json={"categorie_id": cat["id"], "montant": 300}, headers=headers)
    assert res.status_code == 200
    assert res.json()["depense_actuelle"] == 0
    assert res.json()["reste"] == 300

    client.post(
        "/depenses/",
        json={"montant": 120, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    )

    liste = client.get("/budgets/categories", headers=headers).json()
    assert liste[0]["depense_actuelle"] == 120
    assert liste[0]["reste"] == 180


def test_enveloppe_depassee_remontee_en_alerte(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]
    cat = client.post("/categories/", json={"nom": "Loisirs"}, headers=headers).json()

    client.post("/budgets/categories", json={"categorie_id": cat["id"], "montant": 50}, headers=headers)
    client.post(
        "/depenses/",
        json={"montant": 80, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    )

    alertes = client.get("/alertes/", headers=headers).json()
    assert len(alertes["enveloppes_depassees"]) == 1
    assert "Loisirs" in alertes["enveloppes_depassees"][0]


def test_mise_a_jour_enveloppe_pas_de_doublon(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    cat = client.post("/categories/", json={"nom": "Factures"}, headers=headers).json()

    client.post("/budgets/categories", json={"categorie_id": cat["id"], "montant": 100}, headers=headers)
    client.post("/budgets/categories", json={"categorie_id": cat["id"], "montant": 150}, headers=headers)

    liste = client.get("/budgets/categories", headers=headers).json()
    assert len(liste) == 1
    assert liste[0]["montant"] == 150


def test_supprimer_enveloppe(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    cat = client.post("/categories/", json={"nom": "Autre"}, headers=headers).json()

    client.post("/budgets/categories", json={"categorie_id": cat["id"], "montant": 50}, headers=headers)
    res = client.delete(f"/budgets/categories/{cat['id']}", headers=headers)
    assert res.status_code == 200
    assert client.get("/budgets/categories", headers=headers).json() == []
