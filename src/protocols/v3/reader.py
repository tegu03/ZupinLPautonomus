"""Read-only V3 adapter and factory/pool relationship checks."""

from __future__ import annotations

from dataclasses import dataclass

from eth_abi import decode, encode
from web3 import Web3

from ...infrastructure.rpc import RobinhoodRpcClient


@dataclass(frozen=True)
class V3PoolState:
    sqrt_price_x96: int
    tick: int
    observation_index: int
    observation_cardinality: int
    observation_cardinality_next: int
    fee_protocol: int
    unlocked: bool
    liquidity: int
    fee_growth_global0_x128: int
    fee_growth_global1_x128: int


class V3Reader:
    def __init__(self, rpc: RobinhoodRpcClient, factory: str, position_manager: str) -> None:
        self.rpc = rpc
        self.factory = Web3.to_checksum_address(factory)
        self.position_manager = Web3.to_checksum_address(position_manager)

    @staticmethod
    def _selector(signature: str) -> bytes:
        return Web3.keccak(text=signature)[:4]

    def _call(self, address: str, signature: str, input_types: list[str], args: list[object], output_types: list[str]) -> tuple[object, ...]:
        calldata = self._selector(signature) + (encode(input_types, args) if input_types else b"")
        result = self.rpc.call("eth_call", [{"to": address, "data": "0x" + calldata.hex()}, "latest"])
        if not isinstance(result, str) or not result.startswith("0x"):
            raise ValueError(f"Malformed eth_call result for {signature}")
        return decode(output_types, bytes.fromhex(result[2:]))

    def verify_position_manager_factory(self) -> None:
        actual = self._call(self.position_manager, "factory()", [], [], ["address"])[0]
        if Web3.to_checksum_address(str(actual)) != self.factory:
            raise ValueError(f"V3 PositionManager.factory mismatch: expected {self.factory}, got {actual}")

    def pool_for(self, token_a: str, token_b: str, fee: int) -> str:
        pool = self._call(self.factory, "getPool(address,address,uint24)", ["address", "address", "uint24"], [token_a, token_b, fee], ["address"])[0]
        return Web3.to_checksum_address(str(pool))

    def verify_pool_factory(self, pool: str) -> None:
        actual = self._call(Web3.to_checksum_address(pool), "factory()", [], [], ["address"])[0]
        if Web3.to_checksum_address(str(actual)) != self.factory:
            raise ValueError(f"V3 pool.factory mismatch: expected {self.factory}, got {actual}")

    def pool_metadata(self, pool: str) -> tuple[str, str, int, int]:
        address = Web3.to_checksum_address(pool)
        token0 = self._call(address, "token0()", [], [], ["address"])[0]
        token1 = self._call(address, "token1()", [], [], ["address"])[0]
        fee = self._call(address, "fee()", [], [], ["uint24"])[0]
        spacing = self._call(address, "tickSpacing()", [], [], ["int24"])[0]
        return str(token0), str(token1), int(fee), int(spacing)

    def pool_state(self, pool: str) -> V3PoolState:
        address = Web3.to_checksum_address(pool)
        slot = self._call(address, "slot0()", [], [], ["uint160", "int24", "uint16", "uint16", "uint16", "uint8", "bool"])
        return V3PoolState(
            int(slot[0]), int(slot[1]), int(slot[2]), int(slot[3]), int(slot[4]), int(slot[5]), bool(slot[6]),
            int(self._call(address, "liquidity()", [], [], ["uint128"])[0]),
            int(self._call(address, "feeGrowthGlobal0X128()", [], [], ["uint256"])[0]),
            int(self._call(address, "feeGrowthGlobal1X128()", [], [], ["uint256"])[0]),
        )
