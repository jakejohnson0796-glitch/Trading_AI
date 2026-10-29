import numpy as np
import pandas as pd

from market.indicators import add_indicators, latest_values


def make_bars(n=120):
    rng = np.random.default_rng(7)
    close = 2300 + np.cumsum(rng.normal(0, 1.8, n))
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) + rng.uniform(0.1, 1.0, n)
    low = np.minimum(open_, close) - rng.uniform(0.1, 1.0, n)
    return pd.DataFrame({
        "time_utc": pd.date_range("2026-01-01", periods=n, freq="5min", tz="UTC"),
        "open": open_, "high": high, "low": low, "close": close,
        "tick_volume": np.ones(n, dtype=int), "spread": np.ones(n, dtype=int),
    })


def test_indicators_are_added_and_final_values_are_finite():
    out = add_indicators(make_bars())
    for name in ("ema_fast", "ema_slow", "rsi_14", "atr_14", "adx_14", "zscore_20", "prior_high_20", "prior_low_20"):
        assert name in out.columns
        assert pd.notna(out[name].iloc[-1])
    assert 0 <= out["rsi_14"].iloc[-1] <= 100
    assert out["atr_14"].iloc[-1] > 0
    assert isinstance(latest_values(out)["close"], float)


def test_insufficient_bars_rejected():
    bars = make_bars(20)
    try:
        add_indicators(bars)
    except ValueError as exc:
        assert "30 bougies" in str(exc)
    else:
        raise AssertionError("A ValueError devait être levée")
