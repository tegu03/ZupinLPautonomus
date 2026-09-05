from pathlib import Path

from zupin.chain.robinhood import (
    ROBINHOOD_CHAIN_ID,
    UNISWAP_V4_POOL_MANAGER,
    UNISWAP_V4_POSITION_MANAGER,
    UNISWAP_V4_QUOTER,
)


def test_robinhood_constants_are_explicit_and_non_signing() -> None:
    assert ROBINHOOD_CHAIN_ID == 4663
    for address in (UNISWAP_V4_POOL_MANAGER, UNISWAP_V4_POSITION_MANAGER, UNISWAP_V4_QUOTER):
        assert address.startswith("0x")
        assert len(address) == 42


def test_probe_source_contains_no_transaction_submission_method() -> None:
    source = Path("src/zupin/chain/robinhood.py").read_text(encoding="utf-8")
    assert "eth_sendRawTransaction" not in source
    assert "eth_sendTransaction" not in source
