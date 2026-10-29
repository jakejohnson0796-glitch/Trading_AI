from dataclasses import dataclass
from enum import Enum

class Direction(str, Enum):
    BUY = "ACHAT"
    SELL = "VENTE"
    NONE = "ATTENTE"

@dataclass(frozen=True)
class Signal:
    strategy: str
    direction: Direction
    confidence: float
    reason: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence doit être comprise entre 0 et 1.")
        if not self.strategy.strip():
            raise ValueError("Le nom de stratégie est obligatoire.")
