import sys
from types import SimpleNamespace

import pandas as pd

from mt5_connector.reader import MT5Reader, MT5ReaderError


class FakeMT5:
    TIMEFRAME_M1 = 1

    def __init__(self):
        self.start_pos = None
        self.shut_down = False

    def initialize(self, **kwargs):
        return True

    def terminal_info(self):
        return SimpleNamespace(connected=True)

    def version(self):
        return (5, 0, 0)

    def last_error(self):
        return (0, "ok")

    def symbol_info(self, symbol):
        return SimpleNamespace(visible=True)

    def symbol_select(self, symbol, enabled):
        return True

    def copy_rates_from_pos(self, symbol, timeframe, start_pos, count):
        self.start_pos = start_pos
        return [
            {"time": 200, "open": 2, "high": 3, "low": 1, "close": 2.5, "tick_volume": 10, "spread": 1, "real_volume": 0},
            {"time": 100, "open": 1, "high": 2, "low": 0.5, "close": 1.5, "tick_volume": 9, "spread": 1, "real_volume": 0},
        ]

    def shutdown(self):
        self.shut_down = True


def test_reader_requests_closed_bars_and_sorts_them(monkeypatch):
    fake = FakeMT5()
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake)
    reader = MT5Reader()
    ok, _ = reader.connect()
    assert ok
    reader.select_symbol("XAUUSD")
    frame = reader.get_rates(FakeMT5.TIMEFRAME_M1, 20)
    assert fake.start_pos == 1
    assert frame["time"].tolist() == [100, 200]
    assert pd.api.types.is_datetime64_any_dtype(frame["time_utc"])
    assert frame["time_utc"].dt.tz is not None
    assert str(frame["time_utc"].dt.tz) == "UTC"
    reader.shutdown()
    assert fake.shut_down


def test_reader_rejects_missing_symbol(monkeypatch):
    fake = FakeMT5()
    fake.symbol_info = lambda symbol: None
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake)
    reader = MT5Reader()
    assert reader.connect()[0]
    try:
        reader.select_symbol("NO_SUCH_SYMBOL")
    except MT5ReaderError as exc:
        assert "introuvable" in str(exc)
    else:
        raise AssertionError("MT5ReaderError était attendue")
    finally:
        reader.shutdown()
