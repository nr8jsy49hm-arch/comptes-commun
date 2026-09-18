from .conftest import inscrire, entetes_auth


def test_creer_recurrente_genere_la_depense_du_mois(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]

    cat = client.post("/categories/", json={"nom": "Logement"}, headers=headers).json()

    res = client.post(
        "/depenses-recurrentes/",
        json={"nom": "Loyer", "montant": 800, "jour_du_mois": 1, "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    )
    assert res.status_code == 200

    # La dépense du mois a dû être générée automatiquement
    depenses = client.get("/depenses/", headers=headers).json()
    assert len(depenses) == 1
    assert depenses[0]["montant"] == 800
    assert depenses[0]["recurrente_id"] == res.json()["id"]


def test_recurrente_ne_se_duplique_pas(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]
    cat = client.post("/categories/", json={"nom": "Abonnements"}, headers=headers).json()

    client.post(
        "/depenses-recurrentes/",
        json={"nom": "Internet", "montant": 30, "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    )

    # Deux consultations successives du dashboard ne doivent générer qu'une seule dépense
    client.get("/dashboard/", headers=headers)
    client.get("/dashboard/", headers=headers)

    depenses = client.get("/depenses/", headers=headers).json()
    assert len(depenses) == 1


def test_suspendre_recurrente_arrete_la_generation(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]
    cat = client.post("/categories/", json={"nom": "Loisirs"}, headers=headers).json()

    regle = client.post(
        "/depenses-recurrentes/",
        json={"nom": "Salle de sport", "montant": 25, "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    ).json()

    res = client.patch(f"/depenses-recurrentes/{regle['id']}", json={"actif": False}, headers=headers)
    assert res.status_code == 200
    assert res.json()["actif"] is False
