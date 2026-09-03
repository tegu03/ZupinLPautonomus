import os
from pathlib import Path

import pytest

from src.infrastructure.chain import ROBINHOOD_CHAIN_ID
from src.infrastructure.contracts.registry import load_robinhood_registry
from src.infrastructure.rpc import RobinhoodRpcClient, RpcConfig
from src.protocols.v3.reader import V3Reader
from src.protocols.v4.reader import V4Reader


@pytest.mark.integration
def test_robinhood_protocol_relationships() -> None:
    if os.getenv("ROBINHOOD_INTEGRATION") != "1":
        pytest.skip("set ROBINHOOD_INTEGRATION=1 to run live Robinhood RPC smoke test")

    root = Path(__file__).resolve().parents[1]
    registry = load_robinhood_registry(root / "config" / "robinhood.json")
    rpc = RobinhoodRpcClient(RpcConfig(registry.protocol("uniswap_v4").addresses.get("rpc_url", "https://rpc.mainnet.chain.robinhood.com")))
    try:
        assert rpc.chain_id() == ROBINHOOD_CHAIN_ID
        v4 = registry.protocol("uniswap_v4")
        v4_reader = V4Reader(rpc, v4.address("position_manager"), v4.address("state_view"), v4.address("quoter"))
        v4_reader.verify_relationships(v4.address("pool_manager"))
        assert v4_reader.next_token_id() >= 1

        v3 = registry.protocol("uniswap_v3")
        v3_reader = V3Reader(rpc, v3.address("factory"), v3.address("position_manager"))
        v3_reader.verify_position_manager_factory()
    finally:
        rpc.close()
