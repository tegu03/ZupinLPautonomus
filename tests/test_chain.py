import pytest

from src.infrastructure.chain import (
    ROBINHOOD_CHAIN_ID,
    WrongChainError,
    robinhood_identity,
)


def test_robinhood_chain_id_is_4663() -> None:
    assert ROBINHOOD_CHAIN_ID == 4663


def test_robinhood_identity_accepts_only_4663() -> None:
    identity = robinhood_identity(4663)
    assert identity.name == "robinhood"
    assert identity.chain_id == 4663


def test_wrong_chain_fails_closed() -> None:
    with pytest.raises(WrongChainError):
        robinhood_identity(1)

    with pytest.raises(WrongChainError):
        robinhood_identity(42161)
