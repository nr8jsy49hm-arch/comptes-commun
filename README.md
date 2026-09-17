# Comptes Communs

Squelette du projet conforme au cahier des charges : backend FastAPI + PostgreSQL, frontend React, avec authentification JWT.

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
# SECRET_KEY=une-longue-chaine-aleatoire (génère-la avec `openssl rand -hex 32`)

uvicorn app.main:app --reload
```

L'API tourne sur `http://localhost:8000` (doc interactive auto sur `/docs`).

**Important** : il faut avoir PostgreSQL installé et une base `comptes_communs` créée.

## Authentification

Le flux est le suivant :
1. **Le premier des deux s'inscrit** (`Créer un nouveau foyer`) — ça crée à la fois son compte et le foyer.
2. Une fois connecté, son **numéro de foyer** s'affiche en haut de l'écran (`Foyer n°X`).
3. **Le/la partenaire s'inscrit à son tour** en choisissant `Rejoindre un foyer existant` et en renseignant ce numéro.

Les deux comptes sont alors rattachés au même foyer, et toutes les dépenses/balances sont automatiquement partagées entre eux — plus besoin d'insérer quoi que ce soit à la main en base.

## Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend tourne sur `http://localhost:5173` et appelle l'API sur `http://localhost:8000`.

## Ce qui manque encore (prochaines étapes)

- Gestion avancée des catégories (édition, suppression depuis le frontend — la suppression existe déjà côté API).
- Clé de répartition personnalisable (actuellement 50/50 fixe).
- Migrations Alembic proprement configurées (pour l'instant les tables sont créées automatiquement au démarrage, avec une mini-migration manuelle pour la colonne `partagee`).

## Mode solo

L'onglet Solo a maintenant la même richesse que les comptes communs : budget mensuel perso + reste à vivre, répartition par catégorie, et historique mois par mois / année par année — mais pas de règlement, puisque ça n'a pas de sens pour des dépenses qui n'engagent que soi.

## Raffinements

- Transition douce au changement d'onglet.
- Icône automatique par catégorie (déduite du nom — courses, logement, transport, etc.), visible partout où les catégories apparaissent.
- Mode sombre (bouton dans la barre latérale, suit la préférence du système par défaut, mémorisé ensuite).
- Tableaux de dépenses triables (cliquer sur un en-tête de colonne) avec suppression, dans l'onglet Dépenses et dans le mode Solo.

## Gestion du compte

- **Changer son mot de passe** : depuis "Mon compte" (bouton dans la barre latérale), en connaissant son mot de passe actuel.
- **Question secrète** : définissable à l'inscription ou depuis "Mon compte" — sert à la récupération de mot de passe sans email.
- **Mot de passe oublié** : lien sur l'écran de connexion, demande l'email puis la réponse à la question secrète. Si aucune question n'a été définie pour ce compte, la récupération n'est pas possible par ce biais (il faut alors modifier directement la base, ou demander à son/sa partenaire).
- **Supprimer son compte** : depuis "Mon compte", avec confirmation par mot de passe. Les dépenses et le budget personnels (mode solo) sont supprimés automatiquement ; si des dépenses ou règlements communs existent, la suppression est bloquée pour l'instant (pas de transfert de propriété implémenté).

## Autres fonctionnalités

- **Gestion des catégories** (onglet Dépenses) : renommer ou supprimer une catégorie directement depuis l'appli. La suppression est bloquée si des dépenses l'utilisent encore (message explicite plutôt qu'une erreur brute).
- **Clé de répartition personnalisable** (onglet Dépenses) : un curseur permet de passer d'un partage 50/50 à n'importe quelle proportion entre les deux membres du foyer, avec un bouton pour revenir au 50/50 par défaut.
- **Export des données** : bouton CSV (téléchargement direct) et bouton "Imprimer / PDF" (utilise la boîte de dialogue d'impression du navigateur, qui propose "Enregistrer en PDF") — disponibles dans l'onglet Dépenses (commun) et dans le mode Solo.

## Prochaines pistes (discutées mais pas encore faites)

- Tests automatisés et migrations Alembic propres (remplaceraient la mini-migration manuelle actuelle).
- Connexion bancaire automatique : nécessite un agrégateur tiers agréé (Bridge, Powens...), avec inscription développeur et éventuels frais — à cadrer séparément.

## Sécurité

- **Limitation de débit (anti brute-force)** : connexion (10/min), inscription et mot de passe oublié (5/min chacune) par adresse IP, via `slowapi`. Au-delà, l'API renvoie une erreur 429.
- **Mot de passe minimum 8 caractères**, imposé côté serveur (Pydantic) à l'inscription, au changement de mot de passe et à la réinitialisation — pas seulement une suggestion côté frontend.
- **En-têtes de sécurité HTTP** : `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` ajoutés à chaque réponse.
- **Alerte au démarrage** si `SECRET_KEY` n'a pas été changée (reste sur sa valeur par défaut) — visible dans les logs Railway. **Vérifie que tu as bien une vraie valeur définie** dans les variables d'environnement Railway du backend (généré avec `openssl rand -hex 32` par exemple).
- Déjà en place depuis le début : mots de passe hashés (bcrypt), tokens JWT, HTTPS géré automatiquement par Railway et Vercel, CORS restreint aux domaines connus, pas de fuite d'information sur l'existence d'un compte (messages d'erreur génériques à la connexion et à la récupération de mot de passe).

## Notifications

- **Bandeaux dans l'appli** : affichés en haut de chaque page si le budget (commun ou solo) est dépassé ce mois-ci, ou si aucune dépense commune n'a été enregistrée depuis 5 jours ou plus. Chaque bandeau peut être ignoré pour la journée (bouton ✕) ; il réapparaît le lendemain si la situation persiste.
- **Notifications navigateur** (optionnelles) : activables depuis "Mon compte" — demande l'autorisation du navigateur, puis affiche une vraie notification système (même onglet en arrière-plan) une fois par jour et par type d'alerte, tant que l'appli est ouverte quelque part au moment où la vérification se fait (pas de vraie notification "push" quand l'appli est complètement fermée, ça demanderait un serveur dédié).
