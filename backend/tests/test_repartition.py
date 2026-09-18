from datetime import date
from .conftest import inscrire, entetes_auth


def _foyer_a_deux(client):
    pierre = inscrire(client, nom="Pierre", email="pierre@test.fr")
    foyer_id = pierre["utilisateur"]["foyer_id"]
    headers_pierre = entetes_auth(pierre["access_token"])
    invitation = client.post("/foyer/invitations", headers=headers_pierre).json()
    orleanes = inscrire(
        client, nom="Orléanes", email="orleanes@test.fr", invitation_token=invitation["token"]
    )
    headers_orleanes = entetes_auth(orleanes["access_token"])
    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers_pierre).json()
    return pierre, orleanes, headers_pierre, headers_orleanes, cat


def test_balance_50_50_par_defaut(client):
    pierre, orleanes, headers_pierre, headers_orleanes, cat = _foyer_a_deux(client)
    pid, oid = pierre["utilisateur"]["id"], orleanes["utilisateur"]["id"]

    # Pierre paie 100€, Orléanes ne paie rien -> chacun doit 50€ de part,
    # donc Orléanes doit 50€ à Pierre.
    client.post(
        "/depenses/",
        json={"montant": 100, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": pid},
        headers=headers_pierre,
    )

    balance = {b["utilisateur_id"]: b["solde"] for b in client.get("/repartition/balance", headers=headers_pierre).json()}
    assert balance[pid] == 50.0
    assert balance[oid] == -50.0


def test_repartition_personnalisee(client):
    pierre, orleanes, headers_pierre, headers_orleanes, cat = _foyer_a_deux(client)
    pid, oid = pierre["utilisateur"]["id"], orleanes["utilisateur"]["id"]

    # Pierre prend 70% des charges, Orléanes 30%
    res = client.post("/repartition/cle", json={"parts": {str(pid): 70, str(oid): 30}}, headers=headers_pierre)
    assert res.status_code == 200

    client.post(
        "/depenses/",
        json={"montant": 100, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": pid},
        headers=headers_pierre,
    )

    balance = {b["utilisateur_id"]: b["solde"] for b in client.get("/repartition/balance", headers=headers_pierre).json()}
    # Pierre a payé 100, sa part est 70 -> on lui doit 30. Orléanes doit 30.
    assert balance[pid] == 30.0
    assert balance[oid] == -30.0


def test_reinitialiser_cle_repartition(client):
    pierre, orleanes, headers_pierre, headers_orleanes, cat = _foyer_a_deux(client)
    pid, oid = pierre["utilisateur"]["id"], orleanes["utilisateur"]["id"]

    client.post("/repartition/cle", json={"parts": {str(pid): 70, str(oid): 30}}, headers=headers_pierre)
    res = client.delete("/repartition/cle", headers=headers_pierre)
    assert res.status_code == 200

    cle = client.get("/repartition/cle", headers=headers_pierre).json()
    assert cle["type"] == "equirepartition"


def test_reglement_ajuste_la_balance(client):
    pierre, orleanes, headers_pierre, headers_orleanes, cat = _foyer_a_deux(client)
    pid, oid = pierre["utilisateur"]["id"], orleanes["utilisateur"]["id"]

    client.post(
        "/depenses/",
        json={"montant": 100, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": pid},
        headers=headers_pierre,
    )
    # Orléanes rembourse ses 50€
    client.post(
        "/repartition/reglements",
        json={"montant": 50, "date": date.today().isoformat(), "de_utilisateur_id": oid, "vers_utilisateur_id": pid},
        headers=headers_orleanes,
    )

    balance = {b["utilisateur_id"]: b["solde"] for b in client.get("/repartition/balance", headers=headers_pierre).json()}
    assert balance[pid] == 0.0
    assert balance[oid] == 0.0


def test_balance_foyer_a_trois(client):
    pierre = inscrire(client, nom="Pierre", email="pierre@test.fr")
    foyer_id = pierre["utilisateur"]["foyer_id"]
    headers_pierre = entetes_auth(pierre["access_token"])

    inv1 = client.post("/foyer/invitations", headers=headers_pierre).json()
    orleanes = inscrire(client, nom="Orléanes", email="orleanes@test.fr", invitation_token=inv1["token"])

    inv2 = client.post("/foyer/invitations", headers=headers_pierre).json()
    coloc = inscrire(client, nom="Coloc", email="coloc@test.fr", invitation_token=inv2["token"])

    pid = pierre["utilisateur"]["id"]
    oid = orleanes["utilisateur"]["id"]
    cid = coloc["utilisateur"]["id"]

    cat = client.post("/categories/", json={"nom": "Courses"}, headers=headers_pierre).json()
    # Pierre paie 90€ pour les trois -> chacun doit 30€ (équirépartition par défaut)
    client.post(
        "/depenses/",
        json={"montant": 90, "date": date.today().isoformat(), "categorie_id": cat["id"], "payeur_id": pid},
        headers=headers_pierre,
    )

    balance = {b["utilisateur_id"]: b["solde"] for b in client.get("/repartition/balance", headers=headers_pierre).json()}
    assert balance[pid] == 60.0  # a payé 90, sa part est 30 -> on lui doit 60
    assert balance[oid] == -30.0
    assert balance[cid] == -30.0

    # Répartition personnalisée à trois : 50 / 30 / 20
    res = client.post(
        "/repartition/cle",
        json={"parts": {str(pid): 50, str(oid): 30, str(cid): 20}},
        headers=headers_pierre,
    )
    assert res.status_code == 200

    balance = {b["utilisateur_id"]: b["solde"] for b in client.get("/repartition/balance", headers=headers_pierre).json()}
    assert balance[pid] == 45.0  # payé 90, part 45 (50% de 90)
    assert balance[oid] == -27.0  # part 27 (30%)
    assert balance[cid] == -18.0  # part 18 (20%)
