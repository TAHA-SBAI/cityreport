from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


# Le moteur et la session sont initialisés dans app.py via init_db()
engine = None
SessionLocal = None


def init_engine(database_uri: str):
    """Initialise le moteur SQLAlchemy et la fabrique de sessions."""
    global engine, SessionLocal
    engine = create_engine(database_uri, echo=False, future=True)
    SessionLocal = scoped_session(
        sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    )
    return engine, SessionLocal
