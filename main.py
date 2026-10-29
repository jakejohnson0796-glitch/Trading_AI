from __future__ import annotations

from datetime import datetime, timezone
import logging

import pandas as pd

from config.settings import Settings
from database.store import TradeStore
from decision_engine.engine import Decision, combine_signals
from logging_config import configure_logging
from market.indicators import add_indicators, latest_values
from mt5_connector.reader import MT5Reader, MT5ReaderError
from strategies.evaluator import directional_bias, evaluate_m5, micro_trigger
from strategies.models import Direction

TIMEFRAMES = {
    "M1": {"minutes": 1, "fresh_seconds": 5 * 60},
    "M5": {"minutes": 5, "fresh_seconds": 15 * 60},
    "M15": {"minutes": 15, "fresh_seconds": 35 * 60},
}


def main() -> int:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    logger = logging.getLogger("quantum_scalper")
    store = TradeStore(settings.sqlite_path)
    store.initialize()
    reader = MT5Reader()

    print("Quantum Scalper AI — connexion MT5 en lecture seule")
    print(f"Mode : {settings.bot_mode} | Symbole : {settings.mt5_symbol} | Bougies demandées : {settings.bars_count}")
    print("Sécurité : aucun ordre ne sera envoyé par ce programme.")

    try:
        connected, message = reader.connect(settings.mt5_path)
        print(f"MT5 : {message}")
        store.record_event("mt5_connection", {"connected": connected, "message": message})
        if not connected:
            print("Diagnostic : impossible de lire le marché. Vérifie que MT5 est installé et ouvert, et que MetaTrader5 est installé dans ce Python.")
            return 2

        try:
            reader.select_symbol(settings.mt5_symbol)
        except MT5ReaderError as exc:
            print(f"Symbole : ERREUR — {exc}")
            store.record_event("mt5_symbol_error", {"symbol": settings.mt5_symbol, "error": str(exc)})
            return 2

        mt5 = reader._mt5  # constantes timeframe fournies par la bibliothèque officielle
        timeframe_constants = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
        }
        frames: dict[str, pd.DataFrame] = {}
        stale: dict[str, bool] = {}

        for name, info in TIMEFRAMES.items():
            try:
                raw = reader.get_rates(timeframe_constants[name], count=settings.bars_count)
                if len(raw) < 30:
                    raise MT5ReaderError(
                        f"Seulement {len(raw)} bougies reçues ; au moins 30 sont nécessaires."
                    )
                frame = add_indicators(raw)
                frames[name] = frame
                latest = latest_values(frame)
                last_open = pd.Timestamp(frame["time_utc"].iloc[-1]).to_pydatetime()
                expected_close = last_open.timestamp() + info["minutes"] * 60
                age_seconds = max(0.0, datetime.now(timezone.utc).timestamp() - expected_close)
                is_stale = age_seconds > info["fresh_seconds"]
                stale[name] = is_stale
                freshness = "PÉRIMÉE" if is_stale else "OK"

                print(
                    f"{name} : {len(frame)} bougies | clôture la plus récente "
                    f"{last_open.strftime('%Y-%m-%d %H:%M:%S')} UTC | "
                    f"close={_fmt(latest['close'])} | EMA9={_fmt(latest['ema_fast'])} | "
                    f"EMA21={_fmt(latest['ema_slow'])} | RSI14={_fmt(latest['rsi_14'])} | "
                    f"ADX14={_fmt(latest['adx_14'])} | ATR14={_fmt(latest['atr_14'])} | "
                    f"fraîcheur={age_seconds:.0f}s [{freshness}]"
                )
                store.record_event(
                    "market_snapshot",
                    {
                        "symbol": settings.mt5_symbol,
                        "timeframe": name,
                        "bars": len(frame),
                        **latest,
                        "age_seconds": round(age_seconds, 2),
                        "stale": is_stale,
                    },
                )
            except (MT5ReaderError, ValueError, KeyError) as exc:
                logger.warning("Données %s indisponibles : %s", name, exc)
                stale[name] = True
                print(f"{name} : ERREUR — {exc}")
                store.record_event("market_data_error", {"timeframe": name, "error": str(exc)})

        if len(frames) != 3 or any(stale.get(name, True) for name in TIMEFRAMES):
            decision = Decision(
                Direction.NONE,
                "Données M1/M5/M15 manquantes ou périmées ; analyse bloquée par prudence.",
            )
            print(f"Décision PAPER : {decision.direction.value} — {decision.reason}")
            store.record_event("decision", {"direction": decision.direction.value, "reason": decision.reason})
            return 0

        signals = evaluate_m5(frames["M5"])
        print("\nSignaux diagnostiques M5 (règles prototypes, non validées) :")
        for signal in signals:
            print(f"  - {signal.strategy}: {signal.direction.value} | {signal.reason}")
        for signal in signals:
            store.record_event(
                "strategy_signal",
                {
                    "strategy": signal.strategy,
                    "direction": signal.direction.value,
                    "confidence": signal.confidence,
                    "reason": signal.reason,
                    "timeframe": "M5",
                },
            )

        candidate = combine_signals(signals, min_agreement=2)
        m15_bias = directional_bias(frames["M15"])
        m1_trigger = micro_trigger(frames["M1"])
        print(f"\nFiltre M15 : {m15_bias.value} | Déclencheur M1 : {m1_trigger.value}")

        if candidate.direction != Direction.NONE and m15_bias != candidate.direction:
            decision = Decision(
                Direction.NONE,
                f"Consensus M5 non confirmé par M15 (biais={m15_bias.value}).",
                candidate.agreeing_strategies,
            )
        elif candidate.direction != Direction.NONE and m1_trigger != candidate.direction:
            decision = Decision(
                Direction.NONE,
                f"Consensus M5 non confirmé par le déclencheur M1 ({m1_trigger.value}).",
                candidate.agreeing_strategies,
            )
        else:
            decision = candidate

        print(f"\nDécision PAPER : {decision.direction.value} — {decision.reason}")
        if decision.agreeing_strategies:
            print("Stratégies concordantes : " + ", ".join(decision.agreeing_strategies))
        print("AUCUNE EXÉCUTION : cette version ne contient aucun placement d'ordre MT5.")
        store.record_event(
            "decision",
            {
                "direction": decision.direction.value,
                "reason": decision.reason,
                "agreeing_strategies": list(decision.agreeing_strategies),
                "m15_bias": m15_bias.value,
                "m1_trigger": m1_trigger.value,
                "execution": "disabled",
            },
        )
        return 0
    finally:
        reader.shutdown()
        store.close()


def _fmt(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/d"
    return f"{float(value):.2f}"


if __name__ == "__main__":
    raise SystemExit(main())
