from .conftest import inscrire, entetes_auth


def test_creer_cagnotte_et_contribuer_publiquement(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])

    res = client.post(
        "/cagnottes/",
        json={"nom": "Voyage au Portugal", "montant_cible": 1000},
        headers=headers,
    )
    assert res.status_code == 200
    cagnotte = res.json()
    assert cagnotte["montant_total"] == 0
    token = cagnotte["token_public"]

    # Vue publique, sans aucune authentification
    vue = client.get(f"/cagnottes/publique/{token}")
    assert vue.status_code == 200
    assert vue.json()["nom"] == "Voyage au Portugal"
    assert vue.json()["contributions"] == []

    # Un inconnu contribue sans compte
    res = client.post(
        f"/cagnottes/publique/{token}/contribuer",
        json={"nom_contributeur": "Tonton Bernard", "montant": 100, "message": "Bon voyage !"},
    )
    assert res.status_code == 200
    assert res.json()["montant_total"] == 100
    assert res.json()["contributions"][0]["nom_contributeur"] == "Tonton Bernard"


def test_contribution_publique_sans_nom_refusee(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    token = client.post("/cagnottes/", json={"nom": "Cadeau"}, headers=headers).json()["token_public"]

    res = client.post(f"/cagnottes/publique/{token}/contribuer", json={"nom_contributeur": "", "montant": 20})
    assert res.status_code == 400


def test_contribuer_depuis_appli_utilise_le_nom_du_compte(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    cagnotte = client.post("/cagnottes/", json={"nom": "Cadeau anniversaire"}, headers=headers).json()

    res = client.post(f"/cagnottes/{cagnotte['id']}/contribuer", json={"montant": 50}, headers=headers)
    assert res.status_code == 200
    assert res.json()["montant_total"] == 50

    token = cagnotte["token_public"]
    vue = client.get(f"/cagnottes/publique/{token}").json()
    assert vue["contributions"][0]["nom_contributeur"] == "Pierre"


def test_cagnotte_cloturee_refuse_les_contributions(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    cagnotte = client.post("/cagnottes/", json={"nom": "Projet"}, headers=headers).json()

    client.patch(f"/cagnottes/{cagnotte['id']}", json={"cloturee": True}, headers=headers)

    res = client.post(
        f"/cagnottes/publique/{cagnotte['token_public']}/contribuer",
        json={"nom_contributeur": "Quelqu'un", "montant": 10},
    )
    assert res.status_code == 400


def test_regenerer_lien_invalide_lancien(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    cagnotte = client.post("/cagnottes/", json={"nom": "Projet"}, headers=headers).json()
    ancien_token = cagnotte["token_public"]

    res = client.post(f"/cagnottes/{cagnotte['id']}/regenerer-lien", headers=headers)
    nouveau_token = res.json()["token_public"]
    assert nouveau_token != ancien_token

    assert client.get(f"/cagnottes/publique/{ancien_token}").status_code == 404
    assert client.get(f"/cagnottes/publique/{nouveau_token}").status_code == 200


def test_cagnotte_isolee_par_foyer(client):
    pierre = inscrire(client, nom="Pierre", email="pierre@test.fr")
    autre = inscrire(client, nom="Quelqu'un", email="autre@test.fr")

    headers_pierre = entetes_auth(pierre["access_token"])
    headers_autre = entetes_auth(autre["access_token"])

    cagnotte = client.post("/cagnottes/", json={"nom": "Cagnotte de Pierre"}, headers=headers_pierre).json()

    # L'autre foyer ne la voit pas dans sa liste, et ne peut pas la gérer directement
    liste_autre = client.get("/cagnottes/", headers=headers_autre).json()
    assert liste_autre == []

    res = client.patch(f"/cagnottes/{cagnotte['id']}", json={"cloturee": True}, headers=headers_autre)
    assert res.status_code == 404
