from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Foyer(Base):
    __tablename__ = "foyers"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)

    membres = relationship("Utilisateur", back_populates="foyer")
    depenses = relationship("Depense", back_populates="foyer")
    categories = relationship("Categorie", back_populates="foyer")
    reglements = relationship("Reglement", back_populates="foyer")


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    mot_de_passe_hash = Column(String, nullable=False)
    question_secrete = Column(String, nullable=True)
    reponse_secrete_hash = Column(String, nullable=True)
    email_verifie = Column(Boolean, nullable=False, default=False, server_default="true")
    cgu_acceptees_le = Column(DateTime(timezone=True), nullable=True)
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    foyer = relationship("Foyer", back_populates="membres")


class Categorie(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    foyer = relationship("Foyer", back_populates="categories")
    depenses = relationship("Depense", back_populates="categorie")


depense_etiquettes = Table(
    "depense_etiquettes",
    Base.metadata,
    Column("depense_id", Integer, ForeignKey("depenses.id"), primary_key=True),
    Column("etiquette_id", Integer, ForeignKey("etiquettes.id"), primary_key=True),
)


class Etiquette(Base):
    """Étiquette libre (tag), réutilisable sur plusieurs dépenses, transversale aux catégories."""
    __tablename__ = "etiquettes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    foyer_id = Column(Integer, ForeignKey("foyers.id"))


class Depense(Base):
    __tablename__ = "depenses"

    id = Column(Integer, primary_key=True, index=True)
    montant = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String, nullable=True)
    partagee = Column(Boolean, nullable=False, default=True, server_default="true")

    categorie_id = Column(Integer, ForeignKey("categories.id"))
    payeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    foyer_id = Column(Integer, ForeignKey("foyers.id"))
    recurrente_id = Column(Integer, ForeignKey("depenses_recurrentes.id"), nullable=True)
    photo = Column(Text, nullable=True)  # image du justificatif encodée en base64 (data URL)

    categorie = relationship("Categorie", back_populates="depenses")
    payeur = relationship("Utilisateur")
    foyer = relationship("Foyer", back_populates="depenses")
    etiquettes = relationship("Etiquette", secondary=depense_etiquettes)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def a_photo(self) -> bool:
        return self.photo is not None


class DepenseRecurrente(Base):
    """Modèle de dépense qui se recrée automatiquement chaque mois (loyer, abonnement...)."""
    __tablename__ = "depenses_recurrentes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    montant = Column(Float, nullable=False)
    jour_du_mois = Column(Integer, nullable=False, default=1)
    actif = Column(Boolean, nullable=False, default=True, server_default="true")
    partagee = Column(Boolean, nullable=False, default=True, server_default="true")

    categorie_id = Column(Integer, ForeignKey("categories.id"))
    payeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Reglement(Base):
    """Remboursement entre les deux membres du foyer pour équilibrer la balance."""
    __tablename__ = "reglements"

    id = Column(Integer, primary_key=True, index=True)
    montant = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    de_utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    vers_utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    foyer = relationship("Foyer", back_populates="reglements")


class CleRepartition(Base):
    """Définit comment les dépenses sont réparties entre les membres du foyer."""
    __tablename__ = "cles_repartition"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # "50_50", "proportionnelle", "personnalisee"
    valeur = Column(String, nullable=True)  # ex: JSON stringifié si personnalisée
    foyer_id = Column(Integer, ForeignKey("foyers.id"))


class Budget(Base):
    """Budget mensuel défini pour un foyer, mois par mois."""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    mois = Column(Date, nullable=False)  # toujours stocké au 1er du mois concerné
    montant = Column(Float, nullable=False)
    foyer_id = Column(Integer, ForeignKey("foyers.id"))


class BudgetPersonnel(Base):
    """Budget mensuel personnel (mode solo), défini par utilisateur plutôt que par foyer."""
    __tablename__ = "budgets_personnels"

    id = Column(Integer, primary_key=True, index=True)
    mois = Column(Date, nullable=False)
    montant = Column(Float, nullable=False)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))


class Objectif(Base):
    """Objectif d'épargne (vacances, apport maison, etc.), plusieurs possibles par foyer."""
    __tablename__ = "objectifs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    montant_cible = Column(Float, nullable=False)
    date_cible = Column(Date, nullable=True)
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    versements = relationship(
        "VersementObjectif", back_populates="objectif", cascade="all, delete-orphan"
    )


class VersementObjectif(Base):
    """Un versement vers un objectif d'épargne — le montant actuel est la somme des versements."""
    __tablename__ = "versements_objectifs"

    id = Column(Integer, primary_key=True, index=True)
    montant = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    objectif_id = Column(Integer, ForeignKey("objectifs.id"))

    objectif = relationship("Objectif", back_populates="versements")


class Invitation(Base):
    """Invitation à rejoindre un foyer, via un jeton aléatoire non-devinable (remplace l'ancien code_foyer numérique)."""
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    foyer_id = Column(Integer, ForeignKey("foyers.id"))
    cree_par_id = Column(Integer, ForeignKey("utilisateurs.id"))
    expire_le = Column(DateTime(timezone=True), nullable=False)
    utilisee_le = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VerificationEmail(Base):
    """Jeton de vérification d'adresse email, envoyé par email à l'inscription (ou au renvoi)."""
    __tablename__ = "verifications_email"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    expire_le = Column(DateTime(timezone=True), nullable=False)
    verifiee_le = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Cagnotte(Base):
    """Cagnotte pour un projet commun (voyage groupé, cadeau...), partageable via un lien
    public — les contributeurs n'ont pas besoin de compte. Purement déclaratif : chacun
    indique ce qu'il a versé, aucun paiement réel n'est traité (pas d'intégration bancaire)."""
    __tablename__ = "cagnottes"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    description = Column(String, nullable=True)
    montant_cible = Column(Float, nullable=True)
    date_limite = Column(Date, nullable=True)
    token_public = Column(String, unique=True, nullable=False, index=True)
    cloturee = Column(Boolean, nullable=False, default=False, server_default="false")
    foyer_id = Column(Integer, ForeignKey("foyers.id"))
    createur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contributions = relationship(
        "ContributionCagnotte", back_populates="cagnotte", cascade="all, delete-orphan"
    )

    @property
    def montant_total(self) -> float:
        return round(sum(c.montant for c in self.contributions), 2)

    @property
    def nb_contributions(self) -> int:
        return len(self.contributions)


class ContributionCagnotte(Base):
    """Un versement déclaratif à une cagnotte — par un membre du foyer ou par un contributeur
    externe sans compte (identifié par un simple nom donné au moment de contribuer)."""
    __tablename__ = "contributions_cagnottes"

    id = Column(Integer, primary_key=True, index=True)
    nom_contributeur = Column(String, nullable=False)
    montant = Column(Float, nullable=False)
    message = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    cagnotte_id = Column(Integer, ForeignKey("cagnottes.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cagnotte = relationship("Cagnotte", back_populates="contributions")
