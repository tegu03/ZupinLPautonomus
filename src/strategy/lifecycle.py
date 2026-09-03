"""Deterministic LP position lifecycle state machine."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
class PositionState(str,Enum):
    DISCOVERED="discovered"; SIMULATED="simulated"; ENTERING="entering"; ACTIVE="active"; COLLECTING="collecting"; REBALANCING="rebalancing"; EXITING="exiting"; CLOSED="closed"; ERROR="error"
_TRANSITIONS={
 PositionState.DISCOVERED:{PositionState.SIMULATED,PositionState.ERROR},
 PositionState.SIMULATED:{PositionState.ENTERING,PositionState.DISCOVERED,PositionState.ERROR},
 PositionState.ENTERING:{PositionState.ACTIVE,PositionState.ERROR},
 PositionState.ACTIVE:{PositionState.COLLECTING,PositionState.REBALANCING,PositionState.EXITING,PositionState.ERROR},
 PositionState.COLLECTING:{PositionState.ACTIVE,PositionState.ERROR},
 PositionState.REBALANCING:{PositionState.ACTIVE,PositionState.ERROR},
 PositionState.EXITING:{PositionState.CLOSED,PositionState.ERROR},
 PositionState.CLOSED:set(),PositionState.ERROR:{PositionState.DISCOVERED,PositionState.CLOSED}
}
@dataclass
class PositionLifecycle:
    position_id:str
    state:PositionState=PositionState.DISCOVERED
    revision:int=0
    def transition(self,target:PositionState)->None:
        if target not in _TRANSITIONS[self.state]: raise ValueError(f"invalid transition {self.state.value}->{target.value}")
        self.state=target; self.revision+=1
    def can_transition(self,target:PositionState)->bool: return target in _TRANSITIONS[self.state]
