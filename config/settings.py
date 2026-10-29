from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    bot_mode: str = "PAPER"
    mt5_symbol: str = "XAUUSD"
    sqlite_path: str = "data/quantum_scalper.db"
    log_level: str = "INFO"
    order_execution_enabled: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        mode = os.getenv("BOT_MODE", "PAPER").strip().upper()
        if mode != "PAPER":
            raise ValueError("Ce socle n'autorise que BOT_MODE=PAPER.")
        enabled = os.getenv("ORDER_EXECUTION_ENABLED", "false").strip().lower()
        if enabled in {"1", "true", "yes", "on"}:
            raise ValueError("L'exécution d'ordres est désactivée dans ce socle.")
        symbol = os.getenv("MT5_SYMBOL", "XAUUSD").strip()
        if not symbol:
            raise ValueError("MT5_SYMBOL ne peut pas être vide.")
        return cls(mode, symbol, os.getenv("SQLITE_PATH", "data/quantum_scalper.db"),
                   os.getenv("LOG_LEVEL", "INFO"), False)
