import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SQLite par défaut en local — aucune installation requise.
    # En production (Render), la variable DATABASE_URL fournit PostgreSQL.
    _db_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'cityreport.db')}"
    )
    # Render fournit "postgres://" mais SQLAlchemy attend "postgresql://"
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "cityreport-dev-secret-change-me")

    # Catégories métier reconnues par la plateforme
    CATEGORIES = [
        "Voirie",
        "Éclairage",
        "Propreté",
        "Espaces verts",
        "Sécurité",
    ]

    # Statuts du cycle de vie d'un signalement
    STATUTS = ["Nouveau", "En cours", "Résolu"]
