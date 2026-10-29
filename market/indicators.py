from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {"open", "high", "low", "close"}


def add_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    """Ajoute EMA 9/21, RSI 14, ATR 14, ADX 14, z-score et niveaux 20 bougies.

    Les calculs sont déterministes et utilisent uniquement les lignes fournies.
    Le tableau doit être dans l'ordre chronologique (MT5Reader le garantit).
    """
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Colonnes de bougies manquantes : {sorted(missing)}")
    if len(frame) < 30:
        raise ValueError("Au moins 30 bougies sont nécessaires pour calculer les indicateurs.")

    data = frame.copy().reset_index(drop=True)
    for column in ("open", "high", "low", "close"):
        data[column] = pd.to_numeric(data[column], errors="coerce")
    if data[["open", "high", "low", "close"]].isna().any().any():
        raise ValueError("Les données OHLC contiennent des valeurs non numériques ou vides.")

    close = data["close"]
    high = data["high"]
    low = data["low"]

    data["ema_fast"] = close.ewm(span=9, adjust=False, min_periods=9).mean()
    data["ema_slow"] = close.ewm(span=21, adjust=False, min_periods=21).mean()

    delta = close.diff()
    gain = delta.clip(lower=0.0).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    loss = (-delta.clip(upper=0.0)).ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    relative_strength = gain / loss.where(loss != 0)
    rsi = 100.0 - (100.0 / (1.0 + relative_strength))
    rsi = rsi.mask((loss == 0) & (gain > 0), 100.0)
    rsi = rsi.mask((gain == 0) & (loss > 0), 0.0)
    rsi = rsi.mask((gain == 0) & (loss == 0), 50.0)
    data["rsi_14"] = rsi

    previous_close = close.shift(1)
    true_range = pd.concat(
        [(high - low), (high - previous_close).abs(), (low - previous_close).abs()],
        axis=1,
    ).max(axis=1)
    atr = true_range.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    data["atr_14"] = atr

    upward = high.diff()
    downward = -low.diff()
    plus_dm = upward.where((upward > downward) & (upward > 0), 0.0)
    minus_dm = downward.where((downward > upward) & (downward > 0), 0.0)
    plus_smoothed = plus_dm.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    minus_smoothed = minus_dm.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    plus_di = 100.0 * plus_smoothed / atr.where(atr != 0)
    minus_di = 100.0 * minus_smoothed / atr.where(atr != 0)
    di_sum = (plus_di + minus_di).where((plus_di + minus_di) != 0)
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    data["adx_14"] = dx.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()

    rolling_mean = close.rolling(window=20, min_periods=20).mean()
    rolling_std = close.rolling(window=20, min_periods=20).std(ddof=0)
    data["zscore_20"] = (close - rolling_mean) / rolling_std.where(rolling_std != 0)
    data["prior_high_20"] = high.shift(1).rolling(window=20, min_periods=20).max()
    data["prior_low_20"] = low.shift(1).rolling(window=20, min_periods=20).min()
    return data


def latest_values(frame: pd.DataFrame) -> dict[str, float | str | None]:
    """Retourne un instantané facile à imprimer et à sérialiser en JSON."""
    if frame.empty:
        raise ValueError("Aucune bougie disponible.")
    row = frame.iloc[-1]

    def number(key: str) -> float | None:
        value = row.get(key)
        if value is None or pd.isna(value):
            return None
        return float(value)

    stamp = row.get("time_utc")
    return {
        "time_utc": stamp.isoformat() if stamp is not None else None,
        "close": number("close"),
        "ema_fast": number("ema_fast"),
        "ema_slow": number("ema_slow"),
        "rsi_14": number("rsi_14"),
        "adx_14": number("adx_14"),
        "atr_14": number("atr_14"),
        "zscore_20": number("zscore_20"),
    }
