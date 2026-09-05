from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def database_url() -> str:
    value = os.getenv("ZUPIN_DATABASE_URL")
    if not value:
        raise RuntimeError("ZUPIN_DATABASE_URL is required")
    return value


def create_session_factory() -> sessionmaker[Session]:
    engine = create_engine(database_url(), pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)
