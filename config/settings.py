from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_mode: str = "PAPER"
    mt5_symbol: str = "XAUUSD"
    sqlite_path: str = "data/quantum_scalper.db"
    log_level: str = "INFO"
    order_execution_enabled: bool = False
    mt5_path: str | None = None
    bars_count: int = 250

    @classmethod
    def from_env(cls) -> "Settings":
        # Charge .env sans écraser les variables déjà définies dans Windows.
        load_dotenv(Path.cwd() / ".env", override=False)

        mode = os.getenv("BOT_MODE", "PAPER").strip().upper()
        if mode != "PAPER":
            raise ValueError("Ce socle n'autorise que BOT_MODE=PAPER.")

        enabled = os.getenv("ORDER_EXECUTION_ENABLED", "false").strip().lower()
        if enabled in {"1", "true", "yes", "on"}:
            raise ValueError("L'exécution d'ordres est désactivée dans ce socle.")

        symbol = os.getenv("MT5_SYMBOL", "XAUUSD").strip()
        if not symbol:
            raise ValueError("MT5_SYMBOL ne peut pas être vide.")

        try:
            bars_count = int(os.getenv("MT5_BARS", "250"))
        except ValueError as exc:
            raise ValueError("MT5_BARS doit être un entier, par exemple 250.") from exc
        if not 80 <= bars_count <= 5000:
            raise ValueError("MT5_BARS doit être compris entre 80 et 5000.")

        mt5_path = os.getenv("MT5_PATH", "").strip() or None
        if mt5_path and not Path(mt5_path).is_file():
            raise ValueError(f"MT5_PATH ne pointe pas vers un fichier : {mt5_path}")

        return cls(
            bot_mode=mode,
            mt5_symbol=symbol,
            sqlite_path=os.getenv("SQLITE_PATH", "data/quantum_scalper.db").strip(),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
            order_execution_enabled=False,
            mt5_path=mt5_path,
            bars_count=bars_count,
        )
