from strategies.models import Signal, Direction
from decision_engine.engine import combine_signals

def test_no_signal_means_wait():
    assert combine_signals([Signal("a", Direction.NONE, 0, "none")]).direction is Direction.NONE

def test_conflict_means_wait():
    result = combine_signals([Signal("a", Direction.BUY, .6, "buy"),
                              Signal("b", Direction.SELL, .7, "sell")])
    assert result.direction is Direction.NONE
    assert "contradictoires" in result.reason

def test_consensus_required():
    result = combine_signals([Signal("a", Direction.BUY, .6, "buy"),
                              Signal("b", Direction.BUY, .7, "buy")])
    assert result.direction is Direction.BUY
