import pytest
from config.settings import Settings

def test_paper_is_default(monkeypatch):
    monkeypatch.delenv("BOT_MODE", raising=False)
    monkeypatch.delenv("ORDER_EXECUTION_ENABLED", raising=False)
    assert Settings.from_env().bot_mode == "PAPER"

def test_non_paper_mode_rejected(monkeypatch):
    monkeypatch.setenv("BOT_MODE", "LIVE")
    with pytest.raises(ValueError):
        Settings.from_env()

def test_order_execution_cannot_be_enabled(monkeypatch):
    monkeypatch.setenv("BOT_MODE", "PAPER")
    monkeypatch.setenv("ORDER_EXECUTION_ENABLED", "true")
    with pytest.raises(ValueError):
        Settings.from_env()
