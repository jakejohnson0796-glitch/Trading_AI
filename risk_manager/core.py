from dataclasses import dataclass
import math

@dataclass(frozen=True)
class RiskConfig:
    risk_fraction: float = .0025
    max_daily_loss_fraction: float = .02
    max_drawdown_fraction: float = .05
    max_positions: int = 1

def risk_budget(equity: float, risk_fraction: float) -> float:
    if not math.isfinite(equity) or equity <= 0:
        raise ValueError("L'équité doit être finie et positive.")
    if not 0 < risk_fraction <= .01:
        raise ValueError("Le risque doit être entre 0 et 1 % dans ce socle.")
    return equity * risk_fraction

def may_open_position(*, open_positions: int, daily_loss_fraction: float,
                      drawdown_fraction: float, config: RiskConfig = RiskConfig()) -> tuple[bool, str]:
    if open_positions < 0 or daily_loss_fraction < 0 or drawdown_fraction < 0:
        return False, "Mesure de risque incohérente"
    if open_positions >= config.max_positions:
        return False, "Limite de positions atteinte"
    if daily_loss_fraction >= config.max_daily_loss_fraction:
        return False, "Limite de perte journalière atteinte"
    if drawdown_fraction >= config.max_drawdown_fraction:
        return False, "Limite de drawdown atteinte"
    return True, "Contrôles de base validés (ne suffit pas à autoriser un ordre)"
