from datetime import date
from .conftest import inscrire, entetes_auth

PHOTO_TEST = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wA="


def test_creer_depense_avec_photo(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]
    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()

    res = client.post(
        "/depenses/",
        json={
            "montant": 42,
            "date": date.today().isoformat(),
            "categorie_id": cat["id"],
            "payeur_id": payeur_id,
            "photo": PHOTO_TEST,
        },
        headers=headers,
    )
    assert res.status_code == 200
    depense = res.json()
    assert depense["a_photo"] is True
    assert "photo" not in depense  # jamais dans la réponse de création/liste, trop lourd

    # La liste ne renvoie pas non plus l'image elle-même
    liste = client.get("/depenses/", headers=headers).json()
    assert liste[0]["a_photo"] is True

    # Mais la route dédiée la renvoie bien
    photo = client.get(f"/depenses/{depense['id']}/photo", headers=headers).json()
    assert photo["photo"] == PHOTO_TEST


def test_depense_sans_photo(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]
    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()

    depense = client.post(
        "/depenses/",
        json={"montant": 10, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    ).json()
    assert depense["a_photo"] is False

    photo = client.get(f"/depenses/{depense['id']}/photo", headers=headers).json()
    assert photo["photo"] is None


def test_modifier_photo_depense(client):
    data = inscrire(client)
    headers = entetes_auth(data["access_token"])
    payeur_id = data["utilisateur"]["id"]
    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers).json()

    depense = client.post(
        "/depenses/",
        json={"montant": 10, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": payeur_id},
        headers=headers,
    ).json()

    res = client.patch(f"/depenses/{depense['id']}/photo", json={"photo": PHOTO_TEST}, headers=headers)
    assert res.status_code == 200
    assert res.json()["a_photo"] is True

    # Retirer la photo
    res = client.patch(f"/depenses/{depense['id']}/photo", json={"photo": None}, headers=headers)
    assert res.json()["a_photo"] is False
