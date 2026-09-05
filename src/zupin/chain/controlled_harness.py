"""Controlled, non-broadcast Uniswap v4 PositionManager test vectors.

This module encodes only the documented MINT_POSITION + SETTLE_PAIR + SWEEP
command shape. It is intentionally a fixture/harness boundary: producing
calldata here does not prove that a live Robinhood deployment accepts it.
"""
from __future__ import annotations

from dataclasses import dataclass

from .pool_discovery import PoolKey, validate_pool_key
from .pool_id import derive_pool_id
from .simulation import POSITION_MANAGER_MODIFY_LIQUIDITIES_SELECTOR

MINT_POSITION = 0x02
SETTLE_PAIR = 0x0D
SWEEP = 0x14


def _word(value: int) -> bytes:
    if value < 0 or value >= 1 << 256:
        raise ValueError("value must fit uint256")
    return value.to_bytes(32, "big")


def _address_word(address: str) -> bytes:
    if len(address) != 42 or not address.startswith("0x"):
        raise ValueError("malformed address")
    try:
        value = int(address[2:], 16)
    except ValueError as exc:
        raise ValueError("malformed address") from exc
    return value.to_bytes(32, "big")


def _bytes(value: bytes) -> bytes:
    padding = (-len(value)) % 32
    return _word(len(value)) + value + b"\x00" * padding


def _abi_encode_bytes_and_bytes_array(actions: bytes, params: list[bytes]) -> bytes:
    """Encode abi.encode(bytes, bytes[]) for PositionManager.unlockData."""
    head_size = 64
    actions_tail = _bytes(actions)
    array_head = _word(len(params))
    offsets = []
    cursor = 32 + 32 * len(params)
    param_tails = []
    for item in params:
        offsets.append(cursor)
        encoded = _bytes(item)
        param_tails.append(encoded)
        cursor += len(encoded)
    params_tail = array_head + b"".join(_word(offset) for offset in offsets) + b"".join(param_tails)
    actions_offset = head_size
    params_offset = head_size + len(actions_tail)
    return _word(actions_offset) + _word(params_offset) + actions_tail + params_tail


def _abi_encode_modify_liquidities(unlock_data: bytes, deadline: int) -> str:
    if deadline < 0 or deadline >= 1 << 256:
        raise ValueError("deadline must fit uint256")
    payload = _word(64) + _word(deadline) + _bytes(unlock_data)
    return POSITION_MANAGER_MODIFY_LIQUIDITIES_SELECTOR + payload.hex()


def _mint_params(
    pool_key: PoolKey,
    tick_lower: int,
    tick_upper: int,
    liquidity: int,
    amount0_max: int,
    amount1_max: int,
    recipient: str,
    hook_data: bytes,
) -> bytes:
    validate_pool_key(pool_key)
    if not -(1 << 23) <= tick_lower < (1 << 23):
        raise ValueError("tick_lower must fit int24")
    if not -(1 << 23) <= tick_upper < (1 << 23):
        raise ValueError("tick_upper must fit int24")
    if tick_lower >= tick_upper:
        raise ValueError("tick_lower must be less than tick_upper")
    if liquidity < 0 or liquidity >= 1 << 256:
        raise ValueError("liquidity must fit uint256")
    if amount0_max < 0 or amount0_max >= 1 << 128:
        raise ValueError("amount0_max must fit uint128")
    if amount1_max < 0 or amount1_max >= 1 << 128:
        raise ValueError("amount1_max must fit uint128")
    if len(recipient) != 42 or not recipient.startswith("0x"):
        raise ValueError("malformed recipient")
    # abi.encode(PoolKey, int24, int24, uint256, uint128, uint128, address, bytes)
    # PoolKey is five static words; hookData is the only dynamic tail.
    head = b"".join(
        (
            _address_word(pool_key.token0),
            _address_word(pool_key.token1),
            _word(pool_key.fee),
            _word(pool_key.tick_spacing & ((1 << 256) - 1)),
            _address_word(pool_key.hook),
            _word(tick_lower & ((1 << 256) - 1)),
            _word(tick_upper & ((1 << 256) - 1)),
            _word(liquidity),
            _word(amount0_max),
            _word(amount1_max),
            _address_word(recipient),
            _word(12 * 32),
        )
    )
    return head + _bytes(hook_data)


def _settle_pair_params(pool_key: PoolKey) -> bytes:
    return _address_word(pool_key.token0) + _address_word(pool_key.token1)


def _sweep_params(currency: str, recipient: str) -> bytes:
    return _address_word(currency) + _address_word(recipient)


@dataclass(frozen=True)
class ControlledMintVector:
    pool_key: PoolKey
    pool_id: str
    actions: bytes
    params: tuple[bytes, bytes, bytes]
    calldata: str
    value_wei: int


def build_controlled_native_mint_vector(
    *,
    pool_key: PoolKey,
    recipient: str,
    tick_lower: int,
    tick_upper: int,
    liquidity: int,
    amount0_max: int,
    amount1_max: int,
    deadline: int,
) -> ControlledMintVector:
    """Build a deterministic native-currency mint fixture; never broadcasts."""
    if pool_key.token0.lower() != "0x" + "0" * 40:
        raise ValueError("controlled native mint requires native currency as token0")
    mint = _mint_params(
        pool_key,
        tick_lower,
        tick_upper,
        liquidity,
        amount0_max,
        amount1_max,
        recipient,
        b"",
    )
    settle = _settle_pair_params(pool_key)
    sweep = _sweep_params(pool_key.token0, recipient)
    actions = bytes((MINT_POSITION, SETTLE_PAIR, SWEEP))
    unlock = _abi_encode_bytes_and_bytes_array(actions, [mint, settle, sweep])
    calldata = _abi_encode_modify_liquidities(unlock, deadline)
    return ControlledMintVector(
        pool_key=pool_key,
        pool_id=derive_pool_id(pool_key),
        actions=actions,
        params=(mint, settle, sweep),
        calldata=calldata,
        value_wei=amount0_max,
    )
