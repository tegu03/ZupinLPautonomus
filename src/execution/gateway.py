"""Execution boundary. Live signing/broadcast remains explicitly disabled."""
from __future__ import annotations
from dataclasses import dataclass
class ExecutionDisabled(RuntimeError): pass
@dataclass(frozen=True)
class ExecutionPolicy:
    chain_id:int=4663
    live_enabled:bool=False
    signing_enabled:bool=False
    broadcast_enabled:bool=False
class ExecutionGateway:
    def __init__(self,policy:ExecutionPolicy): self.policy=policy
    def assert_ready(self,chain_id:int)->None:
        if chain_id!=4663 or self.policy.chain_id!=4663: raise ExecutionDisabled("Robinhood Chain 4663 is mandatory")
        if not (self.policy.live_enabled and self.policy.signing_enabled and self.policy.broadcast_enabled): raise ExecutionDisabled("live execution is disabled")
    def submit(self,chain_id:int,transaction:dict)->str:
        self.assert_ready(chain_id)
        raise ExecutionDisabled("broadcast implementation is intentionally not enabled in foundation")
