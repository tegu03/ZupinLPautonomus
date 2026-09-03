"""Block/timestamp provider used by accounting and freshness gates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .rpc import RobinhoodRpcClient


@dataclass(frozen=True)
class ChainHead:
    number: int
    hash: str
    timestamp: datetime


class ChainHeadProvider:
    """Read the canonical latest block from Robinhood Chain."""

    def __init__(self, rpc: RobinhoodRpcClient) -> None:
        self._rpc = rpc

    def latest(self) -> ChainHead:
        block: dict[str, Any] = self._rpc.get_block("latest", False)
        number_hex = block.get("number")
        block_hash = block.get("hash")
        timestamp_hex = block.get("timestamp")
        if not all(isinstance(v, str) for v in (number_hex, block_hash, timestamp_hex)):
            raise ValueError("latest block is missing number/hash/timestamp")
        return ChainHead(
            number=int(number_hex, 16),
            hash=block_hash,
            timestamp=datetime.fromtimestamp(int(timestamp_hex, 16), tz=timezone.utc),
        )
