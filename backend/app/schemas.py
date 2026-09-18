from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional

LONGUEUR_MIN_MOT_DE_PASSE = 8


def _valider_longueur_mot_de_passe(cls, v: str) -> str:
    if len(v) < LONGUEUR_MIN_MOT_DE_PASSE:
        raise ValueError(f"Le mot de passe doit faire au moins {LONGUEUR_MIN_MOT_DE_PASSE} caractères")
    return v


class UtilisateurCreate(BaseModel):
    nom: str
    email: EmailStr
    mot_de_passe: str
    nom_foyer: Optional[str] = None  # si fourni, crée un nouveau foyer ; sinon rejoint via invitation_token
    invitation_token: Optional[str] = None  # jeton d'invitation pour rejoindre un foyer existant
    question_secrete: Optional[str] = None
    reponse_secrete: Optional[str] = None

    _valider_mdp = field_validator("mot_de_passe")(_valider_longueur_mot_de_passe)


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


class ChangerMotDePasse(BaseModel):
    mot_de_passe_actuel: str
    nouveau_mot_de_passe: str

    _valider_mdp = field_validator("nouveau_mot_de_passe")(_valider_longueur_mot_de_passe)


class SupprimerCompte(BaseModel):
    mot_de_passe: str


class DefinirQuestionSecrete(BaseModel):
    question: str
    reponse: str


class MotDePasseOublieDemande(BaseModel):
    email: EmailStr


class MotDePasseOublieQuestion(BaseModel):
    question: Optional[str] = None


class MotDePasseOublieReinitialiser(BaseModel):
    email: EmailStr
    reponse: str
    nouveau_mot_de_passe: str

    _valider_mdp = field_validator("nouveau_mot_de_passe")(_valider_longueur_mot_de_passe)


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


class CleRepartitionIn(BaseModel):
    parts: dict[int, float]  # utilisateur_id -> pourcentage (doit sommer à 100)


class CleRepartitionOut(BaseModel):
    type: str  # "50_50" ou "personnalisee"
    parts: dict[int, float]


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


class AlertesResponse(BaseModel):
    depassement_budget_commun: Optional[float] = None
    depassement_budget_solo: Optional[float] = None
    jours_sans_depense_commune: Optional[int] = None


class Invitation(BaseModel):
    id: int
    token: str
    expire_le: datetime
    utilisee_le: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvitationInfo(BaseModel):
    """Réponse publique (avant inscription) : le strict nécessaire pour afficher l'écran de rejoindre."""
    valide: bool
    nom_foyer: Optional[str] = None
