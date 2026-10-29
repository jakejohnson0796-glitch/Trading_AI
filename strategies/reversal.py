from .models import Signal, Direction

def evaluate(*, zone=None, rejection_confirmed=False, swept_level=False, direction=None) -> Signal:
    if not zone or direction not in {"BUY", "SELL"}:
        return Signal("reversal", Direction.NONE, 0.0, "Zone ou direction manquante")
    if not rejection_confirmed or not swept_level:
        return Signal("reversal", Direction.NONE, 0.0, "Balayage et rejet confirmés requis")
    side = Direction.BUY if direction == "BUY" else Direction.SELL
    return Signal("reversal", side, .55, f"Rejet confirmé sur zone {zone}")
