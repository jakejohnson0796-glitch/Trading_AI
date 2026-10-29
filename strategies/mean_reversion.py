from .models import Signal, Direction

def evaluate(*, rsi=None, zscore=None, trending=False) -> Signal:
    if rsi is None or zscore is None:
        return Signal("mean_reversion", Direction.NONE, 0.0, "Données RSI/z-score manquantes")
    if trending:
        return Signal("mean_reversion", Direction.NONE, 0.0, "Suspendue en marché directionnel")
    if rsi <= 30 and zscore <= -2:
        return Signal("mean_reversion", Direction.BUY, .55, "Excès baissier en régime non directionnel")
    if rsi >= 70 and zscore >= 2:
        return Signal("mean_reversion", Direction.SELL, .55, "Excès haussier en régime non directionnel")
    return Signal("mean_reversion", Direction.NONE, 0.0, "Pas d'excès confirmé")
