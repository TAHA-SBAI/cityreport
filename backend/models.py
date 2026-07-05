from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Float, Text, Date, DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Citoyen(Base):
    __tablename__ = "citoyens"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(80))
    prenom: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    telephone: Mapped[str] = mapped_column(String(40), default="")
    mot_de_passe: Mapped[str] = mapped_column(String(200), default="")
    date_inscription: Mapped[date] = mapped_column(Date, default=date.today)

    signalements: Mapped[list["Signalement"]] = relationship(
        back_populates="citoyen"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "telephone": self.telephone,
            "date_inscription": self.date_inscription.isoformat(),
            "nb_signalements": len(self.signalements),
        }


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(80))
    prenom: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    telephone: Mapped[str] = mapped_column(String(40), default="")
    secteur: Mapped[str] = mapped_column(String(60))  # ex: Voirie, Éclairage
    date_prise_fonction: Mapped[date] = mapped_column(Date, default=date.today)

    signalements: Mapped[list["Signalement"]] = relationship(
        back_populates="agent"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "telephone": self.telephone,
            "secteur": self.secteur,
            "date_prise_fonction": self.date_prise_fonction.isoformat(),
            "nb_signalements_geres": len(self.signalements),
        }


class Categorie(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(60), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    priorite_defaut: Mapped[int] = mapped_column(Integer, default=2)  # 1=haute,3=basse

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "description": self.description,
            "priorite_defaut": self.priorite_defaut,
        }


class Signalement(Base):
    __tablename__ = "signalements"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    photo_url: Mapped[str] = mapped_column(String(300), default="")
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    quartier: Mapped[str] = mapped_column(String(80), default="")
    date_creation: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    statut: Mapped[str] = mapped_column(String(20), default="Nouveau")

    # Niveau d'urgence : "" (normal), "police" (19) ou "secours" (15)
    urgence: Mapped[str] = mapped_column(String(20), default="")

    # Catégorie prédite par le module ML + score de confiance
    categorie: Mapped[str] = mapped_column(String(60), default="")
    score_confiance: Mapped[float] = mapped_column(Float, default=0.0)

    citoyen_id: Mapped[int] = mapped_column(ForeignKey("citoyens.id"))
    agent_id: Mapped[int | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True
    )

    citoyen: Mapped["Citoyen"] = relationship(back_populates="signalements")
    agent: Mapped["Agent"] = relationship(back_populates="signalements")
    resultat_ml: Mapped["ResultatML"] = relationship(
        back_populates="signalement", uselist=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "photo_url": self.photo_url,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "quartier": self.quartier,
            "date_creation": self.date_creation.isoformat(),
            "statut": self.statut,
            "urgence": self.urgence,
            "categorie": self.categorie,
            "score_confiance": round(self.score_confiance, 3),
            "citoyen_id": self.citoyen_id,
            "citoyen_nom": (
                f"{self.citoyen.prenom} {self.citoyen.nom}"
                if self.citoyen else ""
            ),
            "agent_id": self.agent_id,
            "agent_nom": (
                f"{self.agent.prenom} {self.agent.nom}" if self.agent else None
            ),
            "anomalie": (
                self.resultat_ml.is_anomalie if self.resultat_ml else False
            ),
            "score_anomalie": (
                round(self.resultat_ml.score_anomalie, 3)
                if self.resultat_ml else 0.0
            ),
        }


class ResultatML(Base):
    __tablename__ = "resultats_ml"

    id: Mapped[int] = mapped_column(primary_key=True)
    signalement_id: Mapped[int] = mapped_column(
        ForeignKey("signalements.id"), unique=True
    )

    # Sortie classification
    categorie_predite: Mapped[str] = mapped_column(String(60), default="")
    score_confiance: Mapped[float] = mapped_column(Float, default=0.0)

    # Sortie détection d'anomalies (Isolation Forest)
    is_anomalie: Mapped[bool] = mapped_column(Boolean, default=False)
    score_anomalie: Mapped[float] = mapped_column(Float, default=0.0)
    anomalie_localisation: Mapped[bool] = mapped_column(Boolean, default=False)
    anomalie_frequence: Mapped[bool] = mapped_column(Boolean, default=False)
    raison_principale: Mapped[str] = mapped_column(String(120), default="")

    signalement: Mapped["Signalement"] = relationship(
        back_populates="resultat_ml"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "signalement_id": self.signalement_id,
            "categorie_predite": self.categorie_predite,
            "score_confiance": round(self.score_confiance, 3),
            "is_anomalie": self.is_anomalie,
            "score_anomalie": round(self.score_anomalie, 3),
            "anomalie_localisation": self.anomalie_localisation,
            "anomalie_frequence": self.anomalie_frequence,
            "anomalie_both": (
                self.anomalie_localisation and self.anomalie_frequence
            ),
            "raison_principale": self.raison_principale,
        }


class HistoriqueStatut(Base):
    """Trace chaque changement de statut d'un signalement, pour la timeline."""
    __tablename__ = "historique_statuts"

    id: Mapped[int] = mapped_column(primary_key=True)
    signalement_id: Mapped[int] = mapped_column(
        ForeignKey("signalements.id"), index=True
    )
    ancien_statut: Mapped[str] = mapped_column(String(20), default="")
    nouveau_statut: Mapped[str] = mapped_column(String(20))
    commentaire: Mapped[str] = mapped_column(String(240), default="")
    date_changement: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "signalement_id": self.signalement_id,
            "ancien_statut": self.ancien_statut,
            "nouveau_statut": self.nouveau_statut,
            "commentaire": self.commentaire,
            "date_changement": self.date_changement.isoformat(),
        }
