"""Initial Phase 0 schema.

Revision ID: 0001_initial_schema
Revises:
"""
from alembic import op

from zupin.db.base import Base
from zupin.db import models  # noqa: F401

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


APPEND_ONLY_TABLES = ("position_events", "cashflows", "fee_events")


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    for table in APPEND_ONLY_TABLES:
        op.execute(
            f"""
            CREATE OR REPLACE FUNCTION zupin_reject_mutation_{table}()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'append-only table: % cannot be updated or deleted', TG_TABLE_NAME;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            f"""
            CREATE TRIGGER {table}_append_only
            BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION zupin_reject_mutation_{table}();
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    for table in reversed(APPEND_ONLY_TABLES):
        op.execute(f"DROP TRIGGER IF EXISTS {table}_append_only ON {table}")
        op.execute(f"DROP FUNCTION IF EXISTS zupin_reject_mutation_{table}()")
    Base.metadata.drop_all(bind=bind)
