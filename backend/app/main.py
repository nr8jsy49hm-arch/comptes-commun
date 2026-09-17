import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .database import engine, Base
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
)

logger = logging.getLogger("uvicorn.error")

# Crée les tables si elles n'existent pas (à remplacer par Alembic en prod)
Base.metadata.create_all(bind=engine)

# Mini-migration additive : ajoute les colonnes apparues après la création initiale des
# tables (create_all ne modifie jamais les tables existantes, seulement les nouvelles).
with engine.connect() as _conn:
    _conn.execute(
        text(
            "ALTER TABLE depenses ADD COLUMN IF NOT EXISTS partagee BOOLEAN NOT NULL DEFAULT TRUE"
        )
    )
    _conn.execute(
        text("ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS question_secrete VARCHAR")
    )
    _conn.execute(
        text("ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS reponse_secrete_hash VARCHAR")
    )
    _conn.commit()

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


@app.get("/")
def health_check():
    return {"status": "ok"}
