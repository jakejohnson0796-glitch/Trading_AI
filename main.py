from config.settings import Settings
from database.store import TradeStore
from logging_config import configure_logging
from decision_engine.engine import combine_signals
from strategies.models import Signal, Direction

def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    store = TradeStore(settings.sqlite_path)
    store.initialize()
    signals = [Signal(name, Direction.NONE, 0.0, "Aucune donnée de marché chargée")
               for name in ("trend_following", "mean_reversion", "breakout",
                            "momentum_pullback", "reversal")]
    decision = combine_signals(signals)
    store.record_event("startup", {"mode": settings.bot_mode, "symbol": settings.mt5_symbol,
                                   "decision": decision.direction.value, "reason": decision.reason})
    print("Quantum Scalper AI — socle initial")
    print(f"Mode : {settings.bot_mode} | Symbole : {settings.mt5_symbol}")
    print(f"Décision : {decision.direction.value} — {decision.reason}")
    print("Sécurité : l'exécution d'ordres n'est pas implémentée.")
    store.close()

if __name__ == "__main__":
    main()
