"""Connecteur MetaTrader 5 strictement en lecture seule.

Aucune méthode de placement/modification/suppression d'ordre n'est exposée.
"""
from __future__ import annotations

import os
from typing import Any

import pandas as pd


class MT5ReaderError(RuntimeError):
    """Erreur lisible liée à la connexion ou aux données MT5."""


class MT5Reader:
    def __init__(self) -> None:
        self._mt5: Any | None = None
        self.symbol: str | None = None

    def connect(self, terminal_path: str | None = None) -> tuple[bool, str]:
        if self._mt5 is not None:
            return True, "Connexion MT5 déjà initialisée."

        try:
            import MetaTrader5 as mt5
        except ImportError:
            return (
                False,
                "Le paquet MetaTrader5 est absent. Installe les dépendances avec "
                "python -m pip install -r requirements.txt.",
            )

        self._mt5 = mt5
        path = (terminal_path or os.getenv("MT5_PATH", "")).strip()
        try:
            initialized = mt5.initialize(path=path) if path else mt5.initialize()
        except Exception as exc:  # protège le démarrage si le terminal refuse l'appel
            self._mt5 = None
            return False, f"Erreur pendant l'initialisation MT5 : {exc}"

        if not initialized:
            error = mt5.last_error()
            try:
                mt5.shutdown()
            except Exception:
                pass
            self._mt5 = None
            return False, f"Initialisation MT5 impossible : {error}"

        terminal = mt5.terminal_info()
        if terminal is None or getattr(terminal, "connected", True) is False:
            error = mt5.last_error()
            mt5.shutdown()
            self._mt5 = None
            return False, f"Terminal MT5 non connecté après initialisation : {error}"

        version = mt5.version()
        return True, f"Terminal MT5 initialisé en lecture seule (version={version})."

    def select_symbol(self, symbol: str) -> str:
        if self._mt5 is None:
            raise MT5ReaderError("Connecte MT5 avant de sélectionner le symbole.")
        requested = symbol.strip()
        info = self._mt5.symbol_info(requested)
        if info is None:
            raise MT5ReaderError(
                f"Symbole '{requested}' introuvable dans MT5. Vérifie son nom exact "
                "dans Market Watch (certains courtiers ajoutent un suffixe)."
            )
        if not bool(getattr(info, "visible", False)):
            if not self._mt5.symbol_select(requested, True):
                raise MT5ReaderError(
                    f"Impossible d'activer '{requested}' dans Market Watch : "
                    f"{self._mt5.last_error()}"
                )
        self.symbol = requested
        return requested

    def get_rates(self, timeframe: int, count: int = 250) -> pd.DataFrame:
        """Retourne les bougies clôturées les plus récentes, dans l'ordre chronologique."""
        if self._mt5 is None:
            raise MT5ReaderError("MT5 n'est pas connecté.")
        if self.symbol is None:
            raise MT5ReaderError("Aucun symbole sélectionné.")
        if count < 1:
            raise ValueError("count doit être supérieur à zéro.")

        # start_pos=0 désigne la bougie actuellement en formation ; 1 l'exclut.
        rates = self._mt5.copy_rates_from_pos(self.symbol, timeframe, 1, count)
        if rates is None:
            raise MT5ReaderError(f"Lecture des bougies impossible : {self._mt5.last_error()}")
        if len(rates) == 0:
            raise MT5ReaderError(
                f"MT5 n'a renvoyé aucune bougie pour {self.symbol} : {self._mt5.last_error()}"
            )

        frame = pd.DataFrame(rates)
        required = {"time", "open", "high", "low", "close", "tick_volume", "spread"}
        missing = required.difference(frame.columns)
        if missing:
            raise MT5ReaderError(f"Données MT5 incomplètes ; colonnes absentes : {sorted(missing)}")

        frame["time_utc"] = pd.to_datetime(frame["time"], unit="s", utc=True)
        frame = frame.sort_values("time").drop_duplicates(subset=["time"]).reset_index(drop=True)
        return frame

    def shutdown(self) -> None:
        if self._mt5 is not None:
            try:
                self._mt5.shutdown()
            finally:
                self._mt5 = None
                self.symbol = None
