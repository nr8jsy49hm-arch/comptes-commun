import logging
import os
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .security import SECRET_KEY
from .limiter import limiter
from .routers import (
    auth,
    depenses,
    repartition,
    dashboard,
    categories,
    foyer,
    budgets,
    historique,
    objectifs,
    solo,
    export,
    alertes,
    admin,
    etiquettes,
)

logger = logging.getLogger("uvicorn.error")

# Monitoring d'erreurs (optionnel) : n'a d'effet que si SENTRY_DSN est configurée.
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN and os.getenv("TESTING") != "1":
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.1, send_default_pii=False)

# Le schéma de la base est désormais géré par Alembic (voir migrations/), appliqué via
# `alembic upgrade head` dans le Procfile avant le démarrage du serveur — plus de
# create_all()/ALTER TABLE manuels ici.

# Avertissement (pas un blocage, pour ne pas casser un déploiement déjà en place) si la
# clé secrète JWT est restée sur sa valeur par défaut — à corriger via la variable
# d'environnement SECRET_KEY sur Railway.
if SECRET_KEY == "change-moi-en-production":
    logger.warning(
        "⚠️  SECRET_KEY n'a pas été changée (valeur par défaut détectée). "
        "Définis une vraie valeur secrète via la variable d'environnement SECRET_KEY."
    )

app = FastAPI(title="Comptes Communs API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Autorise le frontend React (à ajuster selon l'URL de déploiement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://comptes-commun.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def ajouter_en_tetes_securite(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth.router)
app.include_router(depenses.router)
app.include_router(categories.router)
app.include_router(foyer.router)
app.include_router(budgets.router)
app.include_router(historique.router)
app.include_router(objectifs.router)
app.include_router(repartition.router)
app.include_router(dashboard.router)
app.include_router(solo.router)
app.include_router(export.router)
app.include_router(alertes.router)
app.include_router(admin.router)
app.include_router(etiquettes.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
