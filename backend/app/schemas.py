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
    cgu_acceptees: bool = False

    _valider_mdp = field_validator("mot_de_passe")(_valider_longueur_mot_de_passe)

    @field_validator("cgu_acceptees")
    @classmethod
    def _valider_cgu(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Tu dois accepter les CGU et la politique de confidentialité pour créer un compte")
        return v


class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str


class UtilisateurOut(BaseModel):
    id: int
    nom: str
    email: str
    foyer_id: int
    email_verifie: bool = True

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


class EtiquetteBase(BaseModel):
    nom: str


class EtiquetteCreate(EtiquetteBase):
    pass


class Etiquette(EtiquetteBase):
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
    etiquette_ids: list[int] = []
    photo: Optional[str] = None  # data URL base64, optionnelle, envoyée seulement à la création


class Depense(DepenseBase):
    id: int
    foyer_id: int
    etiquettes: list[Etiquette] = []
    recurrente_id: Optional[int] = None
    a_photo: bool = False  # jamais l'image elle-même ici (trop lourd en liste) — voir /depenses/{id}/photo

    class Config:
        from_attributes = True


class DepensePhotoIn(BaseModel):
    photo: Optional[str] = None  # None pour retirer la photo


class DepensePhotoOut(BaseModel):
    photo: Optional[str] = None


class DepenseEtiquettesIn(BaseModel):
    etiquette_ids: list[int]


class DepenseRecurrenteBase(BaseModel):
    nom: str
    montant: float
    jour_du_mois: int = 1
    categorie_id: int
    payeur_id: int
    partagee: bool = True


class DepenseRecurrenteCreate(DepenseRecurrenteBase):
    pass


class DepenseRecurrenteUpdate(BaseModel):
    nom: Optional[str] = None
    montant: Optional[float] = None
    jour_du_mois: Optional[int] = None
    categorie_id: Optional[int] = None
    payeur_id: Optional[int] = None
    partagee: Optional[bool] = None
    actif: Optional[bool] = None


class DepenseRecurrente(DepenseRecurrenteBase):
    id: int
    actif: bool
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
    type: str  # "equirepartition" ou "personnalisee"
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


class MoisEvolutionEpargne(BaseModel):
    mois: int
    nom_mois: str
    total_verse: float


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
    changements_recurrentes: list[str] = []


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


class ContributionCagnotteCreate(BaseModel):
    nom_contributeur: Optional[str] = None  # ignoré pour la contribution authentifiée (nom du compte utilisé)
    montant: float
    message: Optional[str] = None

    @field_validator("montant")
    @classmethod
    def _valider_montant(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Le montant doit être positif")
        return v


class ContributionCagnotte(BaseModel):
    id: int
    nom_contributeur: str
    montant: float
    message: Optional[str] = None
    date: date

    class Config:
        from_attributes = True


class CagnotteCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    montant_cible: Optional[float] = None
    date_limite: Optional[date] = None


class CagnotteUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    montant_cible: Optional[float] = None
    date_limite: Optional[date] = None
    cloturee: Optional[bool] = None


class Cagnotte(BaseModel):
    id: int
    nom: str
    description: Optional[str] = None
    montant_cible: Optional[float] = None
    date_limite: Optional[date] = None
    cloturee: bool
    token_public: str
    montant_total: float
    nb_contributions: int

    class Config:
        from_attributes = True


class CagnottePublique(BaseModel):
    """Vue publique (sans authentification) d'une cagnotte, via son lien de partage."""
    nom: str
    description: Optional[str] = None
    montant_cible: Optional[float] = None
    date_limite: Optional[date] = None
    cloturee: bool
    montant_total: float
    contributions: list[ContributionCagnotte]


class VerificationEmailResultat(BaseModel):
    reussi: bool
    message: str
