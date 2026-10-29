from .models import Signal, Direction

def evaluate(*, close=None, prior_high=None, prior_low=None, confirmed=False) -> Signal:
    if None in (close, prior_high, prior_low):
        return Signal("breakout", Direction.NONE, 0.0, "Niveaux manquants")
    if not confirmed:
        return Signal("breakout", Direction.NONE, 0.0, "Clôture de confirmation absente")
    if close > prior_high:
        return Signal("breakout", Direction.BUY, .55, "Clôture au-dessus du plus haut précédent")
    if close < prior_low:
        return Signal("breakout", Direction.SELL, .55, "Clôture sous le plus bas précédent")
    return Signal("breakout", Direction.NONE, 0.0, "Aucune cassure")
