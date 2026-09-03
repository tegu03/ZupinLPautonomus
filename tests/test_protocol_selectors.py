from web3 import Web3

from src.protocols.v3.abi import V3_FACTORY_ABI, V3_POOL_ABI, V3_POSITION_MANAGER_ABI
from src.protocols.v4.abi import V4_POSITION_MANAGER_ABI, V4_QUOTER_ABI, V4_STATE_VIEW_ABI


def selector(signature: str) -> str:
    return "0x" + Web3.keccak(text=signature)[:4].hex()


def abi_signatures(abi: list[dict]) -> set[str]:
    return {item["name"] for item in abi if item.get("type") == "function"}


def test_v4_selectors_are_exact() -> None:
    expected = {
        "poolManager()": "0xdc4c90d3", "nextTokenId()": "0x75794a3c", "positionInfo(uint256)": "0x89097a6a",
        "getPositionLiquidity(uint256)": "0x1efeed33", "getPoolAndPositionInfo(uint256)": "0x7ba03aad",
        "getSlot0(bytes32)": "0xc815641c", "getLiquidity(bytes32)": "0xfa6793d5",
        "getFeeGrowthGlobals(bytes32)": "0x9ec538c8", "getFeeGrowthInside(bytes32,int24,int24)": "0x53e9c1fb",
    }
    assert {key: selector(key) for key in expected} == expected


def test_v3_selectors_are_exact() -> None:
    expected = {
        "factory()": "0xc45a0155", "getPool(address,address,uint24)": "0x1698ee82",
        "token0()": "0x0dfe1681", "token1()": "0xd21220a7", "fee()": "0xddca3f43",
        "tickSpacing()": "0xd0c93a7c", "slot0()": "0x3850c7bd", "liquidity()": "0x1a686502",
        "feeGrowthGlobal0X128()": "0xf3058399", "feeGrowthGlobal1X128()": "0x46141319",
    }
    assert {key: selector(key) for key in expected} == expected


def test_v4_abis_contain_only_foundation_reads() -> None:
    assert abi_signatures(V4_POSITION_MANAGER_ABI) == {"poolManager", "nextTokenId", "positionInfo", "getPositionLiquidity", "getPoolAndPositionInfo"}
    assert abi_signatures(V4_STATE_VIEW_ABI) == {"poolManager", "getSlot0", "getLiquidity", "getFeeGrowthGlobals", "getFeeGrowthInside"}
    assert abi_signatures(V4_QUOTER_ABI) == {"poolManager"}


def test_v3_abis_contain_only_foundation_reads() -> None:
    assert abi_signatures(V3_FACTORY_ABI) == {"getPool"}
    assert abi_signatures(V3_POSITION_MANAGER_ABI) == {"factory"}
    assert abi_signatures(V3_POOL_ABI) == {"factory", "token0", "token1", "fee", "tickSpacing", "slot0", "feeGrowthGlobal0X128", "feeGrowthGlobal1X128", "liquidity"}
