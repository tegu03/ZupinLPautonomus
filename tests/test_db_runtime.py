import os
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session


def _postgres_engine():
    url = os.getenv("ZUPIN_DATABASE_URL")
    if not url:
        pytest.skip("ZUPIN_DATABASE_URL is not configured")
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        engine.dispose()
        pytest.skip(f"PostgreSQL is unavailable: {exc}")
    return engine


def test_runtime_constraints_and_append_only_triggers() -> None:
    engine = _postgres_engine()
    user_id = "runtime-user"
    pool_id = "runtime-pool"
    position_id = "runtime-position-1"
    position_id_2 = "runtime-position-2"

    try:
        with Session(engine) as session:
            session.execute(text("TRUNCATE position_events"))
            session.execute(text("DELETE FROM positions WHERE user_id = :user_id"), {"user_id": user_id})
            session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
            session.commit()

            session.execute(
                text("INSERT INTO users (id, telegram_user_id) VALUES (:id, :telegram_id)"),
                {"id": user_id, "telegram_id": 900000001},
            )
            session.execute(
                text(
                    "INSERT INTO positions "
                    "(id, user_id, pool_id, state, principal_amount, range_metadata) "
                    "VALUES (:id, :user_id, :pool_id, 'MONITORING', :principal, '{}'::jsonb)"
                ),
                {"id": position_id, "user_id": user_id, "pool_id": pool_id, "principal": Decimal("1")},
            )
            session.commit()

            with pytest.raises(IntegrityError):
                session.execute(
                    text(
                        "INSERT INTO positions "
                        "(id, user_id, pool_id, state, principal_amount, range_metadata) "
                        "VALUES (:id, :user_id, :pool_id, 'DEPLOYING', :principal, '{}'::jsonb)"
                    ),
                    {"id": position_id_2, "user_id": user_id, "pool_id": pool_id, "principal": Decimal("1")},
                )
                session.commit()
            session.rollback()

            session.execute(
                text(
                    "INSERT INTO position_events "
                    "(id, position_id, event_type, idempotency_key, payload) "
                    "VALUES ('runtime-event-1', :position_id, 'TEST', 'runtime-event-key-1', '{}'::jsonb)"
                ),
                {"position_id": position_id},
            )
            session.commit()

            # PostgreSQL RAISE EXCEPTION is surfaced by SQLAlchemy as ProgrammingError,
            # so assert the broader SQLAlchemy database-error contract here.
            with pytest.raises(SQLAlchemyError):
                session.execute(text("UPDATE position_events SET event_type = 'MUTATED' WHERE id = 'runtime-event-1'"))
                session.commit()
            session.rollback()

            with pytest.raises(SQLAlchemyError):
                session.execute(text("DELETE FROM position_events WHERE id = 'runtime-event-1'"))
                session.commit()
            session.rollback()
    finally:
        with Session(engine) as session:
            # TRUNCATE bypasses row-level UPDATE/DELETE triggers and is appropriate for
            # isolated test cleanup; production code never uses it for financial events.
            session.execute(text("TRUNCATE position_events"))
            session.execute(text("DELETE FROM positions WHERE user_id = :user_id"), {"user_id": user_id})
            session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
            session.commit()
        engine.dispose()
