from pydantic import BaseModel
from datetime import date
from typing import Optional


class CategorieBase(BaseModel):
    nom: str


class CategorieCreate(CategorieBase):
    pass


class Categorie(CategorieBase):
    id: int
    foyer_id: int

    class Config:
        from_attributes = True


class DepenseBase(BaseModel):
    montant: float
    date: date
    note: Optional[str] = None
    categorie_id: int
    payeur_id: int


class DepenseCreate(DepenseBase):
    pass


class Depense(DepenseBase):
    id: int
    foyer_id: int

    class Config:
        from_attributes = True


class ReglementBase(BaseModel):
    montant: float
    date: date
    de_utilisateur_id: int
    vers_utilisateur_id: int


class ReglementCreate(ReglementBase):
    pass


class Reglement(ReglementBase):
    id: int
    foyer_id: int

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    """Résultat du calcul de répartition : qui doit combien à qui."""
    utilisateur_id: int
    nom: str
    solde: float  # positif = on lui doit de l'argent, négatif = il/elle doit de l'argent


class DashboardResponse(BaseModel):
    total_mois: float
    par_categorie: dict[str, float]
    balances: list[BalanceResponse]
