from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def _id() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    telegram_user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="ACTIVE")
    autonomy_status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="OFF")


class Wallet(TimestampMixin, Base):
    __tablename__ = "wallets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    evm_address: Mapped[str | None] = mapped_column(String(128))
    svm_address: Mapped[str | None] = mapped_column(String(128))
    evm_key_ref: Mapped[str | None] = mapped_column(String(255))
    svm_key_ref: Mapped[str | None] = mapped_column(String(255))


class Chain(Base):
    __tablename__ = "chains"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    namespace: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    rpc_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    explorer: Mapped[str | None] = mapped_column(String(255))
    native_asset: Mapped[str] = mapped_column(String(32), nullable=False)
    evidence_status: Mapped[str] = mapped_column(String(16), nullable=False)


class Protocol(Base):
    __tablename__ = "protocols"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str | None] = mapped_column(String(64))
    contract_set: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    evidence_status: Mapped[str] = mapped_column(String(16), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    __table_args__ = (UniqueConstraint("chain_id", "name", "version", name="uq_protocol_identity"),)


class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    address: Mapped[str] = mapped_column(String(128), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(32))
    decimals: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    evidence_status: Mapped[str] = mapped_column(String(16), nullable=False)
    __table_args__ = (UniqueConstraint("chain_id", "address", name="uq_token_identity"),)


class Pool(Base):
    __tablename__ = "pools"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol_id: Mapped[str] = mapped_column(String(36), nullable=False)
    token0_id: Mapped[str] = mapped_column(String(36), nullable=False)
    token1_id: Mapped[str] = mapped_column(String(36), nullable=False)
    pool_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    fee_tier: Mapped[Decimal | None] = mapped_column(Numeric(38, 18))
    tick_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class PoolObservation(Base):
    __tablename__ = "pool_observations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    pool_id: Mapped[str] = mapped_column(String(36), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    block_number: Mapped[int | None] = mapped_column(Integer)
    correlation_id: Mapped[str | None] = mapped_column(String(255))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    evidence_status: Mapped[str] = mapped_column(String(16), nullable=False)


class Position(TimestampMixin, Base):
    __tablename__ = "positions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    pool_id: Mapped[str] = mapped_column(String(36), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    range_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    entry_tx_id: Mapped[str | None] = mapped_column(String(36))
    exit_tx_id: Mapped[str | None] = mapped_column(String(36))
    last_reconciled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        Index(
            "uq_one_active_position_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("state IN ('DEPLOYING','MONITORING','REBALANCING','HARVESTING','COMPOUNDING','EXITING','RECONCILING')"),
        ),
    )


class PositionEvent(Base):
    __tablename__ = "position_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    position_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    position_id: Mapped[str | None] = mapped_column(String(36))
    chain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    tx_hash: Mapped[str | None] = mapped_column(String(255), unique=True)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class Cashflow(Base):
    __tablename__ = "cashflows"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    position_id: Mapped[str | None] = mapped_column(String(36))
    asset: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_amount: Mapped[Decimal] = mapped_column(Numeric(78, 0), nullable=False)
    decimals: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    valuation_source: Mapped[str | None] = mapped_column(String(255))
    valuation_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class FeeEvent(Base):
    __tablename__ = "fee_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    position_id: Mapped[str] = mapped_column(String(36), nullable=False)
    asset: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_amount: Mapped[Decimal] = mapped_column(Numeric(78, 0), nullable=False)
    decimals: Mapped[int] = mapped_column(Integer, nullable=False)
    valuation_source: Mapped[str | None] = mapped_column(String(255))
    valuation_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class PnlSnapshot(Base):
    __tablename__ = "pnl_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    position_id: Mapped[str | None] = mapped_column(String(36))
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    ledger_revision: Mapped[str] = mapped_column(String(255), nullable=False)


class DailyPnl(Base):
    __tablename__ = "daily_pnl"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    pnl_date: Mapped[date] = mapped_column(Date, nullable=False)
    chain_id: Mapped[int | None] = mapped_column(Integer)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    fees: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    gas: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    snapshot_id: Mapped[str] = mapped_column(String(36), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "pnl_date", "chain_id", name="uq_daily_pnl"),)


class Referral(Base):
    __tablename__ = "referrals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    referrer_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    referred_user_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)


class ReferralEvent(Base):
    __tablename__ = "referral_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    referral_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    reward_asset: Mapped[str | None] = mapped_column(String(128))
    reward_raw_amount: Mapped[Decimal | None] = mapped_column(Numeric(78, 0))
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class Donation(Base):
    __tablename__ = "donations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    asset: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_amount: Mapped[Decimal] = mapped_column(Numeric(78, 0), nullable=False)
    tx_hash: Mapped[str | None] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    capability_name: Mapped[str] = mapped_column(String(128), nullable=False)
    chain_id: Mapped[int | None] = mapped_column(Integer)
    protocol_version: Mapped[str | None] = mapped_column(String(128))
    contract_addresses: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    source_reference: Mapped[str] = mapped_column(String(1024), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verifier_version: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    decision_id: Mapped[str | None] = mapped_column(String(36))
    policy_version: Mapped[str | None] = mapped_column(String(128))
    evidence_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    transaction_hash: Mapped[str | None] = mapped_column(String(255))
    result: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class DecisionRun(Base):
    __tablename__ = "decision_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(128))
    inputs: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    output: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    evidence_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    gate_result: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
