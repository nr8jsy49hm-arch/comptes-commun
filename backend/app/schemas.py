from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class UtilisateurCreate(BaseModel):
    nom: str
    email: EmailStr
    mot_de_passe: str
    nom_foyer: Optional[str] = None  # si fourni, crée un nouveau foyer ; sinon rejoint via code_foyer
    code_foyer: Optional[int] = None  # id du foyer existant à rejoindre (ex: la conjointe qui rejoint Pierre)


class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str


class UtilisateurOut(BaseModel):
    id: int
    nom: str
    email: str
    foyer_id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    utilisateur: UtilisateurOut


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
    partagee: bool = True


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


class BudgetBase(BaseModel):
    montant: float
    mois: Optional[date] = None  # si omis, s'applique au mois courant


class Budget(BaseModel):
    id: int
    mois: date
    montant: float
    foyer_id: int

    class Config:
        from_attributes = True


class BudgetPersonnel(BaseModel):
    id: int
    mois: date
    montant: float
    utilisateur_id: int

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    total_mois: float
    par_categorie: dict[str, float]
    balances: list[BalanceResponse]
    budget_mois: Optional[float] = None
    reste_a_vivre: Optional[float] = None


class MoisHistorique(BaseModel):
    mois: int
    nom_mois: str
    total_depense: float
    budget: Optional[float] = None
    reste_a_vivre: Optional[float] = None
    nb_depenses: int


class ObjectifCreate(BaseModel):
    nom: str
    montant_cible: float
    date_cible: Optional[date] = None


class Objectif(BaseModel):
    id: int
    nom: str
    montant_cible: float
    date_cible: Optional[date] = None
    montant_actuel: float
    foyer_id: int

    class Config:
        from_attributes = True


class VersementObjectifCreate(BaseModel):
    montant: float


class VersementObjectif(BaseModel):
    id: int
    montant: float
    date: date
    objectif_id: int

    class Config:
        from_attributes = True


class SoloDashboardResponse(BaseModel):
    total_mois: float
    par_categorie: dict[str, float]
    depenses: list[Depense]
    budget_mois: Optional[float] = None
    reste_a_vivre: Optional[float] = None
