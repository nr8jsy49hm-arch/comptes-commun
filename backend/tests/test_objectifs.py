from .conftest import inscrire, entetes_auth


def test_creer_objectif_et_verser(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])

    res = client.post(
        "/objectifs/",
        json={"nom": "Vacances", "montant_cible": 1000, "date_cible": "2027-06-01"},
        headers=headers,
    )
    assert res.status_code == 200
    objectif = res.json()
    assert objectif["montant_actuel"] == 0

    res = client.post(f"/objectifs/{objectif['id']}/versements", json={"montant": 250}, headers=headers)
    assert res.status_code == 200
    assert res.json()["montant_actuel"] == 250

    client.post(f"/objectifs/{objectif['id']}/versements", json={"montant": 100}, headers=headers)
    objectifs = client.get("/objectifs/", headers=headers).json()
    assert objectifs[0]["montant_actuel"] == 350


def test_supprimer_objectif(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])

    objectif = client.post(
        "/objectifs/", json={"nom": "Apport maison", "montant_cible": 5000}, headers=headers
    ).json()

    res = client.delete(f"/objectifs/{objectif['id']}", headers=headers)
    assert res.status_code == 200
    assert client.get("/objectifs/", headers=headers).json() == []
