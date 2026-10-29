import pytest
from risk_manager.core import risk_budget, may_open_position, RiskConfig

def test_risk_budget():
    assert risk_budget(1000, .0025) == 2.5

def test_invalid_equity_rejected():
    with pytest.raises(ValueError):
        risk_budget(0, .0025)

def test_position_limit_blocks():
    ok, _ = may_open_position(open_positions=1, daily_loss_fraction=0, drawdown_fraction=0)
    assert not ok

def test_daily_loss_limit_blocks():
    cfg = RiskConfig(max_daily_loss_fraction=.02)
    ok, _ = may_open_position(open_positions=0, daily_loss_fraction=.02, drawdown_fraction=0, config=cfg)
    assert not ok
