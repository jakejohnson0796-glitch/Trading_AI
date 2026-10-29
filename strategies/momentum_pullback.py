from .models import Signal, Direction

def evaluate(*, trend=None, momentum=None, pullback_confirmed=False) -> Signal:
    if trend not in {"BUY", "SELL"} or momentum is None:
        return Signal("momentum_pullback", Direction.NONE, 0.0, "Tendance ou momentum manquant")
    if not pullback_confirmed:
        return Signal("momentum_pullback", Direction.NONE, 0.0, "Reprise après repli non confirmée")
    if trend == "BUY" and momentum > 0:
        return Signal("momentum_pullback", Direction.BUY, .55, "Reprise haussière confirmée")
    if trend == "SELL" and momentum < 0:
        return Signal("momentum_pullback", Direction.SELL, .55, "Reprise baissière confirmée")
    return Signal("momentum_pullback", Direction.NONE, 0.0, "Momentum contradictoire")
