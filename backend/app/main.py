from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import engine, Base
from .routers import auth, depenses, repartition, dashboard, categories, foyer, budgets, historique, objectifs, solo

# Crée les tables si elles n'existent pas (à remplacer par Alembic en prod)
Base.metadata.create_all(bind=engine)

# Mini-migration additive : ajoute la colonne "partagee" si la table "depenses"
# existait déjà avant son introduction (create_all ne modifie jamais les tables existantes).
with engine.connect() as _conn:
    _conn.execute(
        text(
            "ALTER TABLE depenses ADD COLUMN IF NOT EXISTS partagee BOOLEAN NOT NULL DEFAULT TRUE"
        )
    )
    _conn.commit()

app = FastAPI(title="Comptes Communs API")

# Autorise le frontend React (à ajuster selon l'URL de déploiement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/")
def health_check():
    return {"status": "ok"}
