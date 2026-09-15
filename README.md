# Comptes Communs — Phase 0 : structure de départ

Squelette du projet conforme au cahier des charges : backend FastAPI + PostgreSQL, frontend React.

## Structure

```
comptes-communs/
├── backend/
│   ├── app/
│   │   ├── main.py          # point d'entrée FastAPI
│   │   ├── database.py      # config connexion PostgreSQL
│   │   ├── models.py        # modèles SQLAlchemy (Foyer, Utilisateur, Depense...)
│   │   ├── schemas.py       # schémas Pydantic (validation API)
│   │   └── routers/
│   │       ├── depenses.py
│   │       ├── repartition.py
│   │       └── dashboard.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   ├── api.js            # client API centralisé
    │   └── components/
    │       ├── Dashboard.jsx
    │       └── DepenseForm.jsx
    └── package.json
```

## Lancer le backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt

# Créer un fichier .env avec :
# DATABASE_URL=postgresql://user:password@localhost:5432/comptes_communs

uvicorn app.main:app --reload
```

L'API tourne sur `http://localhost:8000` (doc interactive auto sur `/docs`).

**Important** : il faut avoir PostgreSQL installé et une base `comptes_communs` créée, et pour l'instant un foyer + deux utilisateurs insérés à la main en base (pas encore d'écran d'inscription — c'est la prochaine étape logique).

## Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend tourne sur `http://localhost:5173` et appelle l'API sur `http://localhost:8000`.

## Ce qui manque encore (prochaines étapes)

- Écran de création du foyer + des deux utilisateurs (actuellement `FOYER_ID = 1` en dur côté frontend).
- Authentification (JWT) — les endpoints ne sont pas encore protégés.
- Gestion des catégories (CRUD) côté API et frontend.
- Écran de règlement (rembourser l'autre).
- Migrations Alembic proprement configurées (pour l'instant les tables sont créées automatiquement au démarrage).
