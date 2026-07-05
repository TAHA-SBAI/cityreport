from database import SessionLocal


def get_session():
    """Retourne la session scoped courante."""
    return SessionLocal()
