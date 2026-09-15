from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
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
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    foyer = relationship("Foyer", back_populates="membres")


class Categorie(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    foyer = relationship("Foyer", back_populates="categories")
    depenses = relationship("Depense", back_populates="categorie")


class Depense(Base):
    __tablename__ = "depenses"

    id = Column(Integer, primary_key=True, index=True)
    montant = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String, nullable=True)

    categorie_id = Column(Integer, ForeignKey("categories.id"))
    payeur_id = Column(Integer, ForeignKey("utilisateurs.id"))
    foyer_id = Column(Integer, ForeignKey("foyers.id"))

    categorie = relationship("Categorie", back_populates="depenses")
    payeur = relationship("Utilisateur")
    foyer = relationship("Foyer", back_populates="depenses")

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
