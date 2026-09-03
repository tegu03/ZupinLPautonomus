import json
from pathlib import Path

import pytest
from web3 import Web3

from src.infrastructure.contracts.registry import load_robinhood_registry


CONFIG = Path(__file__).parents[1] / "config" / "robinhood.json"


def test_registry_is_robinhood_only() -> None:
    registry = load_robinhood_registry(CONFIG)
    assert registry.chain_id == 4663
    assert set(registry.protocols) == {"uniswap_v4", "uniswap_v3"}


def test_all_configured_addresses_are_valid_and_nonzero() -> None:
    registry = load_robinhood_registry(CONFIG)
    zero = "0x0000000000000000000000000000000000000000"
    for address in registry.all_addresses().values():
        assert Web3.is_address(address)
        assert Web3.to_checksum_address(address) != Web3.to_checksum_address(zero)


def test_registry_rejects_other_chain(tmp_path: Path) -> None:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    data["network"]["chain_id"] = 42161
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="Robinhood-only"):
        load_robinhood_registry(path)


def test_registry_prioritizes_v4() -> None:
    registry = load_robinhood_registry(CONFIG)
    assert registry.protocol("uniswap_v4").priority < registry.protocol("uniswap_v3").priority


def test_known_robinhood_uniswap_addresses() -> None:
    registry = load_robinhood_registry(CONFIG)
    v4 = registry.protocol("uniswap_v4")
    v3 = registry.protocol("uniswap_v3")

    assert v4.address("pool_manager") == "0x8366a39cc670b4001a1121b8f6a443a643e40951"
    assert v4.address("position_manager") == "0x58daec3116aae6d93017baaea7749052e8a04fa7"
    assert v4.address("state_view") == "0xf3334192d15450cdd385c8b70e03f9a6bd9e673b"
    assert v3.address("factory") == "0x1f7d7550b1b028f7571e69a784071f0205fd2efa"
    assert v3.address("position_manager") == "0x73991a25c818bf1f1128deaab1492d45638de0d3"
