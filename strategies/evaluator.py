"""Adaptateur indicateurs -> cinq stratégies de départ.

Ces règles sont expérimentales et servent au diagnostic PAPER uniquement.
Elles ne prouvent pas une rentabilité et ne peuvent pas passer d'ordres.
"""
from __future__ import annotations

import pandas as pd

from strategies import breakout, mean_reversion, momentum_pullback, reversal, trend_following
from strategies.models import Direction, Signal


def evaluate_m5(frame: pd.DataFrame) -> list[Signal]:
    if len(frame) < 30:
        return _no_data_signals("Pas assez de bougies M5")

    row = frame.iloc[-1]
    previous = frame.iloc[-2]
    needed = ("ema_fast", "ema_slow", "rsi_14", "adx_14", "zscore_20")
    if any(pd.isna(row.get(name)) for name in needed):
        return _no_data_signals("Indicateurs encore en période de chauffe")

    ema_fast = float(row["ema_fast"])
    ema_slow = float(row["ema_slow"])
    close = float(row["close"])
    adx = float(row["adx_14"])
    rsi = float(row["rsi_14"])
    zscore = float(row["zscore_20"])
    prior_high = _optional_float(row.get("prior_high_20"))
    prior_low = _optional_float(row.get("prior_low_20"))

    trend_signal = trend_following.evaluate(ema_fast=ema_fast, ema_slow=ema_slow, adx=adx)
    reversion_signal = mean_reversion.evaluate(rsi=rsi, zscore=zscore, trending=adx >= 25)
    breakout_signal = breakout.evaluate(
        close=close,
        prior_high=prior_high,
        prior_low=prior_low,
        confirmed=True,
    )

    if ema_fast > ema_slow:
        trend = "BUY"
    elif ema_fast < ema_slow:
        trend = "SELL"
    else:
        trend = None
    momentum = close - float(frame["close"].iloc[-4]) if len(frame) >= 4 else None
    prev_close = float(previous["close"])
    prev_ema_fast = _optional_float(previous.get("ema_fast"))
    pullback_confirmed = False
    if prev_ema_fast is not None and trend == "BUY":
        pullback_confirmed = prev_close <= prev_ema_fast and close > ema_fast
    elif prev_ema_fast is not None and trend == "SELL":
        pullback_confirmed = prev_close >= prev_ema_fast and close < ema_fast
    momentum_signal = momentum_pullback.evaluate(
        trend=trend,
        momentum=momentum,
        pullback_confirmed=pullback_confirmed,
    )

    reversal_signal: Signal
    if prior_low is not None and float(row["low"]) < prior_low and close > prior_low and close > float(row["open"]):
        reversal_signal = reversal.evaluate(
            zone="support", rejection_confirmed=True, swept_level=True, direction="BUY"
        )
    elif prior_high is not None and float(row["high"]) > prior_high and close < prior_high and close < float(row["open"]):
        reversal_signal = reversal.evaluate(
            zone="résistance", rejection_confirmed=True, swept_level=True, direction="SELL"
        )
    else:
        # Appel explicite à la stratégie pour garder une explication de non-signal.
        reversal_signal = reversal.evaluate(
            zone="support/résistance", rejection_confirmed=False,
            swept_level=False, direction="BUY"
        )

    return [trend_signal, reversion_signal, breakout_signal, momentum_signal, reversal_signal]


def directional_bias(frame: pd.DataFrame, *, adx_min: float = 18.0) -> Direction:
    """Biais directionnel simple utilisé comme filtre, jamais comme ordre."""
    if frame.empty:
        return Direction.NONE
    row = frame.iloc[-1]
    try:
        fast, slow = float(row["ema_fast"]), float(row["ema_slow"])
        close, adx = float(row["close"]), float(row["adx_14"])
    except (KeyError, TypeError, ValueError):
        return Direction.NONE
    if pd.isna(fast) or pd.isna(slow) or pd.isna(close) or pd.isna(adx) or adx < adx_min:
        return Direction.NONE
    if fast > slow and close > slow:
        return Direction.BUY
    if fast < slow and close < slow:
        return Direction.SELL
    return Direction.NONE


def micro_trigger(frame: pd.DataFrame) -> Direction:
    """Filtre M1 : prix et EMA rapides doivent aller dans le même sens."""
    if frame.empty:
        return Direction.NONE
    row = frame.iloc[-1]
    try:
        close, fast, slow = float(row["close"]), float(row["ema_fast"]), float(row["ema_slow"])
    except (KeyError, TypeError, ValueError):
        return Direction.NONE
    if pd.isna(close) or pd.isna(fast) or pd.isna(slow):
        return Direction.NONE
    if close > fast > slow:
        return Direction.BUY
    if close < fast < slow:
        return Direction.SELL
    return Direction.NONE


def _optional_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _no_data_signals(reason: str) -> list[Signal]:
    return [
        Signal(name, Direction.NONE, 0.0, reason)
        for name in (
            "trend_following", "mean_reversion", "breakout", "momentum_pullback", "reversal"
        )
    ]
