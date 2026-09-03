"""Robinhood Chain identity and fail-closed network guard."""

from dataclasses import dataclass

ROBINHOOD_CHAIN_ID = 4663
ROBINHOOD_RPC_URL = "https://rpc.mainnet.chain.robinhood.com"


class WrongChainError(RuntimeError):
    """Raised when the connected network is not Robinhood Chain."""


@dataclass(frozen=True)
class ChainIdentity:
    chain_id: int
    name: str
    rpc_url: str

    def assert_robinhood(self) -> None:
        if self.chain_id != ROBINHOOD_CHAIN_ID:
            raise WrongChainError(
                f"Wrong chain: expected {ROBINHOOD_CHAIN_ID}, got {self.chain_id}"
            )


def robinhood_identity(chain_id: int) -> ChainIdentity:
    identity = ChainIdentity(
        chain_id=chain_id,
        name="robinhood",
        rpc_url=ROBINHOOD_RPC_URL,
    )
    identity.assert_robinhood()
    return identity
