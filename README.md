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
2. Une fois connecté, il va dans **Mon compte → Inviter quelqu'un dans le foyer** et génère un lien d'invitation (jeton aléatoire, valable 7 jours, à usage unique).
3. **Le/la partenaire ouvre ce lien** (`.../?invite=<jeton>`) — l'appli détecte automatiquement le jeton, affiche le nom du foyer à rejoindre, et pré-remplit l'inscription.

Les deux comptes sont alors rattachés au même foyer, et toutes les dépenses/balances sont automatiquement partagées entre eux. Ce système remplace l'ancien numéro de foyer (`code_foyer`), qui était un simple entier devinable — inadapté dès qu'il y a des utilisateurs qu'on ne connaît pas personnellement.

## Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend tourne sur `http://localhost:5173` et appelle l'API sur `http://localhost:8000`.

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

- Connexion bancaire automatique : nécessite un agrégateur tiers agréé (Bridge, Powens...), avec inscription développeur et éventuels frais — à cadrer séparément.

## Tests automatisés

Suite de tests pytest, isolée de la vraie base (utilise un fichier SQLite temporaire, recréé à chaque test).

```bash
cd backend
pip install -r requirements-dev.txt --break-system-packages   # ou sans ce flag si venv actif
pytest
```

Couverture actuelle : inscription/connexion, mot de passe (changement, question secrète, réinitialisation), dépenses (création/suppression/isolation solo-commun), catégories (renommer, suppression bloquée si utilisée), budget et reste à vivre, répartition (50/50 par défaut, personnalisée, effet d'un règlement), objectifs d'épargne.

## Migrations Alembic (activées)

Le schéma de la base est géré par Alembic (`alembic.ini`, `migrations/`). Le `Procfile` exécute `alembic upgrade head` avant de démarrer le serveur à chaque déploiement — plus de migration manuelle dans `main.py`.

Pour toute future modification de modèle (`app/models.py`), génère une nouvelle migration avant de pousser :

```bash
cd backend
alembic revision --autogenerate -m "description du changement"
```

Vérifie le fichier généré dans `migrations/versions/` (l'autogénération n'est pas toujours parfaite), puis committe-le avec le reste. Au déploiement suivant, Railway l'appliquera automatiquement via le `Procfile`.

Pour appliquer une migration manuellement sur la base de production (rare — normalement automatique au déploiement), utilise le tunnel Railway :
```bash
railway connect Postgres --tunnel-only   # dans un premier terminal, à laisser ouvert
# dans un second terminal, avec l'URL affichée par le tunnel :
$env:DATABASE_URL="<url-du-tunnel>"
alembic upgrade head
```

## Recherche globale

Bouton "Rechercher" dans la barre latérale : trouve une dépense par mot-clé (note, catégorie, étiquette, payeur, montant), peu importe le mois — pratique pour retrouver "cette dépense de mars dont je ne me souviens plus exactement quand". Recherche insensible à la casse et aux accents, résultats limités aux 50 plus récents. Purement côté frontend, aucun nouvel endpoint backend.

## Cagnottes pour projets communs

Onglet Cagnottes : crée une cagnotte pour un projet (voyage groupé, cadeau d'anniversaire ou de mariage...), avec un montant cible et une échéance optionnels. **Purement déclaratif**, comme les objectifs d'épargne — aucun paiement réel n'est traité, chacun indique juste ce qu'il a mis.

- **Lien public partageable** (`.../?cagnotte=<jeton>`) : n'importe qui peut **voir** la progression sans compte. Pour **contribuer**, un compte est nécessaire (création en une minute directement sur la page si besoin) — ça garantit que chaque participation vienne d'une vraie personne identifiée, plutôt qu'un simple nom tapé en texte libre. Le compte créé n'a pas besoin d'appartenir au même foyer que la cagnotte.
- **Gestion** : copier le lien, le régénérer (invalide l'ancien si jamais il a fuité), verser directement depuis l'appli (le nom est pris automatiquement sur ton compte), clôturer/rouvrir, supprimer.
- **Sécurité** : isolation stricte par foyer côté gestion (impossible de gérer la cagnotte d'un autre foyer, même en devinant son ID) ; la vue publique reste accessible sans connexion, seule la contribution exige un compte.

## Photo de justificatif

À l'ajout d'une dépense, possibilité de joindre une photo (ticket, facture) — compressée et redimensionnée directement dans le navigateur avant envoi (max ~1000px de large, JPEG) pour rester léger, stockée en base (pas de service de stockage tiers). La liste des dépenses n'expose jamais l'image elle-même (trop lourd) : seulement un indicateur `a_photo`, avec une icône cliquable qui charge et affiche la photo en plein écran à la demande via une route dédiée.

## Vue calendrier

Onglet Nos Dépenses : grille mensuelle avec le total dépensé chaque jour, navigation mois par mois, jour courant repéré visuellement. Cliquer sur un jour affiche le détail des dépenses de ce jour (catégorie, note, payeur, montant). Aucun nouvel endpoint backend, regroupement fait côté frontend à partir de la liste des dépenses déjà chargée.

## Dépenses récurrentes

Onglet Nos Dépenses : programme un loyer, un abonnement ou une facture fixe (nom, montant, jour du mois, catégorie, payeur). Génération **automatique à la demande** — dès que quelqu'un ouvre le Tableau de bord ou la liste des dépenses ce mois-ci, la dépense du mois est créée si elle n'existe pas déjà (pas besoin de tâche planifiée séparée). Si le montant d'une règle change d'un mois sur l'autre, un rappel apparaît dans les notifications. Les règles peuvent être suspendues (sans les supprimer) ou supprimées.

## Étiquettes libres

En plus des catégories, des étiquettes libres transversales (ex : "Vacances Italie", "Travaux cuisine") permettent de regrouper des dépenses qui traversent plusieurs catégories. Choix multiple à la création d'une dépense (avec création à la volée), gestion (suppression) dans l'onglet Nos Dépenses, et filtre par étiquette dans la liste complète des dépenses. Relation many-to-many en base (une dépense peut avoir plusieurs étiquettes, une étiquette peut couvrir plusieurs dépenses).

## Simulateur d'achat

Sur le Tableau de bord : teste l'impact d'une dépense hypothétique (commune ou perso) avant de la valider — nouveau total du mois, et si un budget est défini, le reste à vivre qui en découlerait (avec alerte si ça dépasserait). Rien n'est enregistré, purement informatif ; aucun nouvel endpoint backend.

## Comparaison de périodes

Sur le Tableau de bord : le mois en cours comparé au mois précédent et au même mois l'an dernier, avec le delta en pourcentage (hausse en brique, baisse en vert). Réutilise les données déjà exposées par l'historique, aucun nouvel endpoint backend.

## Calculette

Accessible depuis n'importe quel onglet (bouton dans la barre latérale). Opérations de base (+, −, ×, ÷), bouton pour copier le résultat dans le presse-papier — pratique pour calculer un montant avant de le saisir dans un formulaire.

## Graphiques et classements

- **Graphiques** (onglet Tableau de bord, bas de page) : dépenses communes par mois (histogramme) et évolution cumulée de l'épargne tous objectifs confondus (courbe), avec sélecteur d'année. Basé sur `recharts`.
- **Classement automatisé par catégorie** : partout où une répartition par catégorie s'affichait (Tableau de bord, Historique, Solo), c'est maintenant un vrai classement trié (médailles pour le top 3, pourcentage du total, barre de progression) plutôt qu'une simple liste.

## Foyers à plus de 2 personnes

L'appli n'est plus limitée à un couple : un foyer peut compter autant de membres que nécessaire (colocs, famille...).

- **Rejoindre à plusieurs** : génère une invitation par nouvelle personne depuis "Mon compte" (chaque lien est à usage unique).
- **Répartition** : par défaut, les dépenses communes sont partagées à parts égales entre tous les membres (100/N chacun). La clé personnalisée (onglet Nos Dépenses) affiche désormais un champ pourcentage par membre plutôt qu'un simple curseur à deux, avec vérification que le total fait bien 100%.
- **Règlements** : quand il y a plus de deux membres, un menu déroulant permet de choisir à qui on rembourse ; l'historique précise toujours qui a payé qui.
- Tout le reste (dépenses, catégories, budgets, objectifs) fonctionnait déjà pour N personnes sans changement — seule la logique de répartition/règlement était câblée pour exactement deux.

## RGPD

- **Export des données personnelles** : depuis "Mon compte" → "Exporter mes données", téléchargement d'un fichier JSON avec toutes les données rattachées au compte (profil, dépenses, budgets, règlements, invitations créées).
- **CGU et politique de confidentialité** : brouillon accessible depuis l'inscription et "Mon compte". **⚠️ Ce sont des textes rédigés à titre indicatif — à faire relire et compléter par un professionnel du droit avant tout usage commercial réel** (identité de l'éditeur, adresse, email de contact à renseigner dans `frontend/src/components/LegalDocs.jsx`).
- **Traçabilité du consentement** : la date d'acceptation des CGU est enregistrée à l'inscription (`cgu_acceptees_le`), et l'inscription est bloquée si la case n'est pas cochée.
- Déjà couvert ailleurs : droit à l'effacement (suppression de compte), droit de rectification (modifiable dans l'appli).

## Sauvegardes automatiques

Une sauvegarde complète de la base (toutes les tables, au format JSON) est générée automatiquement chaque nuit via **GitHub Actions** (`.github/workflows/backup.yml`) — gratuit, aucun service tiers à payer.

**Mise en place (une fois) :**
1. Sur Railway, backend → Variables : ajoute `BACKUP_SECRET` avec une longue chaîne aléatoire (ex : `openssl rand -hex 32`).
2. Sur GitHub, va sur ton dépôt → **Settings** → **Secrets and variables** → **Actions** → ajoute deux secrets :
   - `BACKUP_SECRET` : la même valeur qu'à l'étape 1
   - `BACKEND_URL` : l'URL de ton backend Railway (ex : `https://comptes-commun-production.up.railway.app`)
3. C'est tout — la sauvegarde tourne automatiquement chaque nuit à 3h UTC. Tu peux aussi la lancer manuellement depuis l'onglet **Actions** du dépôt → "Sauvegarde quotidienne de la base" → **Run workflow**.

Les sauvegardes sont téléchargeables depuis l'onglet Actions → le run concerné → section "Artifacts", conservées 90 jours. Pour restaurer, il faudrait réinjecter le JSON dans la base — pas encore automatisé (à faire si le besoin se présente réellement).

## Monitoring (suivi des erreurs)

Intégration [Sentry](https://sentry.io) (gratuit jusqu'à 5000 erreurs/mois), backend et frontend, pour être alerté si l'appli plante en production plutôt que de le découvrir par hasard.

**Mise en place :**
1. Crée un compte gratuit sur [sentry.io](https://sentry.io), crée un projet Python (FastAPI) et un projet React — récupère leurs DSN respectifs (Settings → Client Keys).
2. Sur Railway, backend → Variables : ajoute `SENTRY_DSN` avec le DSN du projet Python.
3. Sur Vercel, ton projet → Settings → Environment Variables : ajoute `VITE_SENTRY_DSN` avec le DSN du projet React, puis redéploie.

Si ces variables ne sont pas définies, tout fonctionne normalement — le monitoring est simplement inactif.

## Sécurité

- **Vérification d'email** : à l'inscription, un email de confirmation est envoyé (via Resend). Tant que l'email n'est pas confirmé, un bandeau discret le rappelle dans l'appli, avec un bouton pour renvoyer l'email. **Étapes pour l'activer** :
  1. Crée un compte gratuit sur [resend.com](https://resend.com) (100 emails/jour, 3000/mois).
  2. Génère une clé API (Dashboard → API Keys → Create).
  3. Sur Railway, backend → Variables, ajoute `RESEND_API_KEY` avec cette clé, et `FRONTEND_URL` = `https://comptes-commun.vercel.app`.
  4. **Limite du mode gratuit sans domaine vérifié** : Resend n'autorise l'envoi qu'à l'adresse email de ton propre compte Resend (protection anti-spam standard). Concrètement, tant que tu n'as pas vérifié un nom de domaine sur Resend, seul ton email à toi recevra réellement les emails — celui d'Orléanes ne recevra rien, même si le compte se crée normalement. Pour débloquer l'envoi à tout le monde, il faut acheter un nom de domaine et le vérifier dans Resend (Domains → Add Domain), puis définir `RESEND_FROM_EMAIL` avec une adresse de ce domaine.
  5. Si `RESEND_API_KEY` n'est pas configurée du tout, l'inscription fonctionne quand même normalement — l'email est juste silencieusement non envoyé (visible dans les logs Railway), rien ne casse.

- **Limitation de débit (anti brute-force)** : connexion (10/min), inscription et mot de passe oublié (5/min chacune) par adresse IP, via `slowapi`. Au-delà, l'API renvoie une erreur 429.
- **Mot de passe minimum 8 caractères**, imposé côté serveur (Pydantic) à l'inscription, au changement de mot de passe et à la réinitialisation — pas seulement une suggestion côté frontend.
- **En-têtes de sécurité HTTP** : `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` ajoutés à chaque réponse.
- **Alerte au démarrage** si `SECRET_KEY` n'a pas été changée (reste sur sa valeur par défaut) — visible dans les logs Railway. **Vérifie que tu as bien une vraie valeur définie** dans les variables d'environnement Railway du backend (généré avec `openssl rand -hex 32` par exemple).
- Déjà en place depuis le début : mots de passe hashés (bcrypt), tokens JWT, HTTPS géré automatiquement par Railway et Vercel, CORS restreint aux domaines connus, pas de fuite d'information sur l'existence d'un compte (messages d'erreur génériques à la connexion et à la récupération de mot de passe).

## Notifications

- **Bandeaux dans l'appli** : affichés en haut de chaque page si le budget (commun ou solo) est dépassé ce mois-ci, ou si aucune dépense commune n'a été enregistrée depuis 5 jours ou plus. Chaque bandeau peut être ignoré pour la journée (bouton ✕) ; il réapparaît le lendemain si la situation persiste.
- **Notifications navigateur** (optionnelles) : activables depuis "Mon compte" — demande l'autorisation du navigateur, puis affiche une vraie notification système (même onglet en arrière-plan) une fois par jour et par type d'alerte, tant que l'appli est ouverte quelque part au moment où la vérification se fait (pas de vraie notification "push" quand l'appli est complètement fermée, ça demanderait un serveur dédié).
