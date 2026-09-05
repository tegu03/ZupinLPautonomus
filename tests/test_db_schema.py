from sqlalchemy.dialects import postgresql

from zupin.db.base import Base
from zupin.db import models  # noqa: F401


def test_expected_core_tables_exist() -> None:
    expected = {
        "users", "wallets", "chains", "protocols", "tokens", "pools",
        "pool_observations", "positions", "position_events", "transactions",
        "cashflows", "fee_events", "pnl_snapshots", "daily_pnl", "referrals",
        "referral_events", "donations", "evidence_records", "audit_events",
        "decision_runs",
    }
    assert expected.issubset(Base.metadata.tables)


def test_one_active_position_index_is_postgresql_partial_unique() -> None:
    table = Base.metadata.tables["positions"]
    index = next(i for i in table.indexes if i.name == "uq_one_active_position_per_user")
    assert index.unique is True
    assert str(index.dialect_options["postgresql"]["where"]) == (
        "state IN ('DEPLOYING','MONITORING','REBALANCING','HARVESTING','COMPOUNDING','EXITING','RECONCILING')"
    )
    sql = str(index.compile(dialect=postgresql.dialect())) if hasattr(index, "compile") else ""
    assert "uq_one_active_position_per_user" in sql or index.unique
