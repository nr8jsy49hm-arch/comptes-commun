from datetime import date
from .conftest import inscrire, entetes_auth


def test_creer_attacher_et_filtrer_par_etiquette(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]

    cat = client.post("/categories/", json={"nom": "Loisirs"}, headers=headers).json()
    et = client.post("/etiquettes/", json={"nom": "Vacances Italie"}, headers=headers).json()

    res = client.post(
        "/depenses/",
        json={
            "montant": 50,
            "date": date.today().isoformat(),
            "categorie_id": cat["id"],
            "payeur_id": payeur_id,
            "etiquette_ids": [et["id"]],
        },
        headers=headers,
    )
    assert res.status_code == 200
    depense = res.json()
    assert len(depense["etiquettes"]) == 1
    assert depense["etiquettes"][0]["nom"] == "Vacances Italie"

    # Une deuxième dépense sans étiquette
    client.post(
        "/depenses/",
        json={"montant": 20, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    )

    # Sans filtre : les deux
    assert len(client.get("/depenses/", headers=headers).json()) == 2

    # Avec filtre : seulement celle avec l'étiquette
    filtrees = client.get(f"/depenses/?etiquette_id={et['id']}", headers=headers).json()
    assert len(filtrees) == 1
    assert filtrees[0]["montant"] == 50


def test_creer_etiquette_deja_existante_ne_duplique_pas(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])

    et1 = client.post("/etiquettes/", json={"nom": "Travaux"}, headers=headers).json()
    et2 = client.post("/etiquettes/", json={"nom": "Travaux"}, headers=headers).json()
    assert et1["id"] == et2["id"]

    liste = client.get("/etiquettes/", headers=headers).json()
    assert len(liste) == 1


def test_modifier_etiquettes_dune_depense(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]

    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()
    et1 = client.post("/etiquettes/", json={"nom": "Anniversaire"}, headers=headers).json()
    et2 = client.post("/etiquettes/", json={"nom": "Cadeau"}, headers=headers).json()

    depense = client.post(
        "/depenses/",
        json={"montant": 30, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    ).json()
    assert depense["etiquettes"] == []

    res = client.patch(
        f"/depenses/{depense['id']}/etiquettes",
        json={"etiquette_ids": [et1["id"], et2["id"]]},
        headers=headers,
    )
    assert res.status_code == 200
    assert len(res.json()["etiquettes"]) == 2


def test_supprimer_etiquette(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])

    et = client.post("/etiquettes/", json={"nom": "Temporaire"}, headers=headers).json()
    res = client.delete(f"/etiquettes/{et['id']}", headers=headers)
    assert res.status_code == 200
    assert client.get("/etiquettes/", headers=headers).json() == []
