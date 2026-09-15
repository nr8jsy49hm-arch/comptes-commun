from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import depenses, repartition, dashboard

# Crée les tables si elles n'existent pas (à remplacer par Alembic en prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Comptes Communs API")

# Autorise le frontend React (à ajuster selon l'URL de déploiement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(depenses.router)
app.include_router(repartition.router)
app.include_router(dashboard.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
