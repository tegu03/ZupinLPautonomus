"""Rolling position fee-velocity primitives."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
D = Decimal
@dataclass(frozen=True)
class FeeVelocitySample:
    timestamp: int
    fee_token0: int
    fee_token1: int
    liquidity: int
    def validate(self) -> None:
        if self.timestamp < 0 or self.fee_token0 < 0 or self.fee_token1 < 0 or self.liquidity < 0:
            raise ValueError("invalid fee velocity sample")
@dataclass(frozen=True)
class FeeVelocity:
    elapsed_seconds: int
    token0_per_second: Decimal
    token1_per_second: Decimal
    token0_per_hour: Decimal
    token1_per_hour: Decimal
def calculate_velocity(start: FeeVelocitySample, end: FeeVelocitySample) -> FeeVelocity:
    start.validate(); end.validate()
    if end.timestamp <= start.timestamp: raise ValueError("end timestamp must be after start timestamp")
    if end.liquidity != start.liquidity: raise ValueError("liquidity changed; split lifecycle")
    dt=end.timestamp-start.timestamp
    v0=D(end.fee_token0-start.fee_token0)/D(dt); v1=D(end.fee_token1-start.fee_token1)/D(dt)
    if v0<0 or v1<0: raise ValueError("fee checkpoints must be monotonic")
    return FeeVelocity(dt,v0,v1,v0*D(3600),v1*D(3600))
def rolling_velocity(samples: list[FeeVelocitySample], window_seconds: int) -> FeeVelocity:
    if window_seconds<=0 or len(samples)<2: raise ValueError("invalid rolling window")
    ordered=sorted(samples,key=lambda s:s.timestamp); end=ordered[-1]
    eligible=[s for s in ordered if end.timestamp-s.timestamp<=window_seconds]
    if len(eligible)<2: raise ValueError("insufficient samples for requested window")
    return calculate_velocity(eligible[0],end)
def velocity_change(previous: FeeVelocity,current: FeeVelocity)->Decimal:
    a=previous.token0_per_second+previous.token1_per_second; b=current.token0_per_second+current.token1_per_second
    if a==0: return D(0) if b==0 else D("Infinity")
    return (b-a)/a*D(100)
