"""
Configuração do banco de dados com SQLAlchemy puro.
"""

import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hygeia.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Cria todas as tabelas no banco."""
    Base.metadata.create_all(engine)


@contextmanager
def get_session():
    """Gerenciador de contexto para sessões do banco."""
    session = Session(engine)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()