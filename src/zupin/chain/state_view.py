"""Read-only Uniswap v4 StateView reader for concrete pool verification.

This module only performs eth_call reads. It never signs, estimates writes, or
broadcasts transactions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen
import json

from .pool_state import PoolStateObservation
from .robinhood import ROBINHOOD_CHAIN_ID, ROBINHOOD_RPC_URL

UNISWAP_V4_STATE_VIEW = "0xf3334192d15450cdd385c8b70e03f9a6bd9e673b"
GET_SLOT0_SELECTOR = "0xc815641c"
GET_LIQUIDITY_SELECTOR = "0xfa6793d5"


@dataclass(frozen=True)
class StateViewRead:
    state: PoolStateObservation
    block_number: int


class StateViewReadError(RuntimeError):
    pass


def _rpc(rpc_url: str, method: str, params: list[Any], timeout: float = 15.0) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode())
    if "error" in result:
        raise StateViewReadError(str(result["error"]))
    return result.get("result")


def _pool_id_word(pool_id: str) -> str:
    if not isinstance(pool_id, str) or not pool_id.startswith("0x") or len(pool_id) != 66:
        raise StateViewReadError("pool_id must be a 32-byte hex value")
    try:
        int(pool_id[2:], 16)
    except ValueError as exc:
        raise StateViewReadError("pool_id contains non-hex characters") from exc
    return pool_id[2:].lower()


def _decode_words(data: str, count: int) -> list[int]:
    if not isinstance(data, str) or not data.startswith("0x"):
        raise StateViewReadError("StateView returned malformed data")
    raw = data[2:]
    if len(raw) != count * 64:
        raise StateViewReadError(f"expected {count} ABI words, received {len(raw) // 64}")
    try:
        return [int(raw[index:index + 64], 16) for index in range(0, len(raw), 64)]
    except ValueError as exc:
        raise StateViewReadError("StateView returned non-hex ABI data") from exc


def _decode_signed_int24(word: int) -> int:
    value = word & ((1 << 24) - 1)
    return value - (1 << 24) if value & (1 << 23) else value


def read_pool_state(
    *,
    pool_id: str,
    rpc_url: str = ROBINHOOD_RPC_URL,
    observed_block: int | None = None,
    source_ref: str = "rpc://robinhood/state-view",
) -> StateViewRead:
    """Read getSlot0/getLiquidity for one pool at a single RPC block tag.

    The returned observation is evidence input only. Callers must still match it
    against independently discovered PoolKey metadata before treating it as
    trusted state.
    """
    word = _pool_id_word(pool_id)
    if not source_ref:
        raise StateViewReadError("source_ref is required")
    block_tag = "latest" if observed_block is None else hex(observed_block)
    slot0_data = _rpc(
        rpc_url,
        "eth_call",
        [{"to": UNISWAP_V4_STATE_VIEW, "data": GET_SLOT0_SELECTOR + word}, block_tag],
    )
    liquidity_data = _rpc(
        rpc_url,
        "eth_call",
        [{"to": UNISWAP_V4_STATE_VIEW, "data": GET_LIQUIDITY_SELECTOR + word}, block_tag],
    )
    slot0 = _decode_words(slot0_data, 4)
    liquidity = _decode_words(liquidity_data, 1)[0]
    if slot0[0] > (1 << 160) - 1:
        raise StateViewReadError("sqrtPriceX96 exceeds uint160")
    if slot0[3] > (1 << 24) - 1 or slot0[2] > (1 << 24) - 1:
        raise StateViewReadError("fee exceeds uint24")
    if liquidity > (1 << 128) - 1:
        raise StateViewReadError("active liquidity exceeds uint128")
    block_number = observed_block
    if block_number is None:
        block_hex = _rpc(rpc_url, "eth_blockNumber", [])
        if not isinstance(block_hex, str):
            raise StateViewReadError("eth_blockNumber returned malformed data")
        block_number = int(block_hex, 16)
    if block_number < 0:
        raise StateViewReadError("observed block must be non-negative")
    state = PoolStateObservation(
        pool_id=pool_id,
        sqrt_price_x96=slot0[0],
        tick=_decode_signed_int24(slot0[1]),
        protocol_fee=slot0[2],
        lp_fee=slot0[3],
        active_liquidity=liquidity,
        observed_block=block_number,
        source_ref=source_ref,
        evidence_status="PROVEN",
    )
    return StateViewRead(state=state, block_number=block_number)
