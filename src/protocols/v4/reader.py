"""Read-only V4 adapter using exact standard function signatures."""

from __future__ import annotations

from dataclasses import dataclass

from eth_abi import decode, encode
from web3 import Web3

from ...infrastructure.rpc import RobinhoodRpcClient
from .position_info import PositionInfo, decode_position_info


@dataclass(frozen=True)
class V4PoolKey:
    currency0: str
    currency1: str
    fee: int
    tick_spacing: int
    hooks: str


@dataclass(frozen=True)
class V4PoolState:
    sqrt_price_x96: int
    tick: int
    protocol_fee: int
    lp_fee: int
    liquidity: int
    fee_growth_global0_x128: int
    fee_growth_global1_x128: int


class V4Reader:
    """Read V4 state; no execution or signing belongs here."""

    def __init__(self, rpc: RobinhoodRpcClient, position_manager: str, state_view: str, quoter: str) -> None:
        self.rpc = rpc
        self.position_manager = Web3.to_checksum_address(position_manager)
        self.state_view = Web3.to_checksum_address(state_view)
        self.quoter = Web3.to_checksum_address(quoter)

    @staticmethod
    def _selector(signature: str) -> bytes:
        return Web3.keccak(text=signature)[:4]

    def _call(self, address: str, signature: str, input_types: list[str], args: list[object], output_types: list[str]) -> tuple[object, ...]:
        calldata = self._selector(signature) + (encode(input_types, args) if input_types else b"")
        result = self.rpc.call("eth_call", [{"to": address, "data": "0x" + calldata.hex()}, "latest"])
        if not isinstance(result, str) or not result.startswith("0x"):
            raise ValueError(f"Malformed eth_call result for {signature}")
        return decode(output_types, bytes.fromhex(result[2:]))

    def verify_relationships(self, expected_pool_manager: str) -> None:
        expected = Web3.to_checksum_address(expected_pool_manager)
        for address, label in ((self.position_manager, "position_manager"), (self.state_view, "state_view"), (self.quoter, "quoter")):
            value = self._call(address, "poolManager()", [], [], ["address"])[0]
            if Web3.to_checksum_address(str(value)) != expected:
                raise ValueError(f"{label}.poolManager() mismatch: expected {expected}, got {value}")

    def next_token_id(self) -> int:
        return int(self._call(self.position_manager, "nextTokenId()", [], [], ["uint256"])[0])

    def position_info(self, token_id: int) -> PositionInfo:
        result = self._call(self.position_manager, "positionInfo(uint256)", ["uint256"], [token_id], ["uint256"])
        return decode_position_info(int(result[0]))

    def pool_and_position_info(self, token_id: int) -> tuple[V4PoolKey, PositionInfo]:
        result = self._call(self.position_manager, "getPoolAndPositionInfo(uint256)", ["uint256"], [token_id], ["address", "address", "uint24", "int24", "address", "uint256"])
        key = V4PoolKey(str(result[0]), str(result[1]), int(result[2]), int(result[3]), str(result[4]))
        return key, decode_position_info(int(result[5]))

    def position_liquidity(self, token_id: int) -> int:
        return int(self._call(self.position_manager, "getPositionLiquidity(uint256)", ["uint256"], [token_id], ["uint128"])[0])

    def pool_state(self, pool_id: bytes | str) -> V4PoolState:
        if isinstance(pool_id, str):
            pool_id = bytes.fromhex(pool_id[2:] if pool_id.startswith("0x") else pool_id)
        if len(pool_id) != 32:
            raise ValueError("V4 PoolId must be exactly 32 bytes")
        slot = self._call(self.state_view, "getSlot0(bytes32)", ["bytes32"], [pool_id], ["uint160", "int24", "uint24", "uint24"])
        liquidity = self._call(self.state_view, "getLiquidity(bytes32)", ["bytes32"], [pool_id], ["uint128"])[0]
        globals_ = self._call(self.state_view, "getFeeGrowthGlobals(bytes32)", ["bytes32"], [pool_id], ["uint256", "uint256"])
        return V4PoolState(int(slot[0]), int(slot[1]), int(slot[2]), int(slot[3]), int(liquidity), int(globals_[0]), int(globals_[1]))

    def fee_growth_inside(self, pool_id: bytes | str, tick_lower: int, tick_upper: int) -> tuple[int, int]:
        if isinstance(pool_id, str):
            pool_id = bytes.fromhex(pool_id[2:] if pool_id.startswith("0x") else pool_id)
        result = self._call(self.state_view, "getFeeGrowthInside(bytes32,int24,int24)", ["bytes32", "int24", "int24"], [pool_id, tick_lower, tick_upper], ["uint256", "uint256"])
        return int(result[0]), int(result[1])
