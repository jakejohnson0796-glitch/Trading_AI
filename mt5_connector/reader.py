# Connecteur facultatif en lecture seule. Aucun envoi d'ordre n'est implémenté.
class MT5Reader:
    def __init__(self):
        self._mt5 = None

    def connect(self) -> tuple[bool, str]:
        try:
            import MetaTrader5 as mt5
        except ImportError:
            return False, "Paquet MetaTrader5 absent; lecture MT5 indisponible."
        self._mt5 = mt5
        if not mt5.initialize():
            return False, f"Initialisation MT5 impossible : {mt5.last_error()}"
        return True, "Terminal MT5 initialisé (lecture seulement)."

    def account_snapshot(self) -> dict | None:
        if self._mt5 is None:
            return None
        info = self._mt5.account_info()
        if info is None:
            return None
        return {"balance": info.balance, "equity": info.equity, "currency": info.currency}

    def shutdown(self) -> None:
        if self._mt5 is not None:
            self._mt5.shutdown()
            self._mt5 = None
