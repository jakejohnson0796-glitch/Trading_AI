from dataclasses import dataclass
from strategies.models import Direction, Signal

@dataclass(frozen=True)
class Decision:
    direction: Direction
    reason: str
    agreeing_strategies: tuple[str, ...] = ()

def combine_signals(signals: list[Signal], min_agreement: int = 2) -> Decision:
    active = [s for s in signals if s.direction != Direction.NONE]
    if not active:
        return Decision(Direction.NONE, "Aucun signal valide")
    buys = [s for s in active if s.direction == Direction.BUY]
    sells = [s for s in active if s.direction == Direction.SELL]
    if buys and sells:
        return Decision(Direction.NONE, "Signaux contradictoires entre stratégies")
    side = Direction.BUY if buys else Direction.SELL
    agreeing = buys if buys else sells
    if len(agreeing) < min_agreement:
        return Decision(Direction.NONE, f"Consensus insuffisant : {len(agreeing)}/{min_agreement}")
    return Decision(side, f"Consensus de {len(agreeing)} stratégie(s)",
                    tuple(s.strategy for s in agreeing))
