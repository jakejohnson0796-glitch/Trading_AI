from .models import Signal, Direction

def evaluate(*, ema_fast=None, ema_slow=None, adx=None) -> Signal:
    if None in (ema_fast, ema_slow, adx):
        return Signal("trend_following", Direction.NONE, 0.0, "Données EMA/ADX manquantes")
    if adx < 20:
        return Signal("trend_following", Direction.NONE, 0.0, "Tendance trop faible (ADX < 20)")
    if ema_fast > ema_slow:
        return Signal("trend_following", Direction.BUY, .55, "EMA rapide au-dessus de l'EMA lente")
    if ema_fast < ema_slow:
        return Signal("trend_following", Direction.SELL, .55, "EMA rapide sous l'EMA lente")
    return Signal("trend_following", Direction.NONE, 0.0, "EMA sans direction")
