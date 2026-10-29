# Quantum Scalper AI — socle initial

Projet Python modulaire pour Windows / VS Code / MetaTrader 5. Cette livraison couvre le socle des phases 1–2 : configuration, journalisation, stockage SQLite, contrôles de risque de base, cinq modules de stratégie de départ et tests.

## Sécurité par défaut
- Mode par défaut : `PAPER`, aucun ordre envoyé.
- L'envoi d'ordres n'est pas implémenté dans cette livraison.
- Ne pas utiliser ce socle pour trader en réel : stratégies, sorties, coûts, backtests et contrôles complets restent à développer et valider.
- Ne jamais placer de mot de passe ou clé API dans le code ou Git.

## Installation Windows (PowerShell)
```powershell
cd quantum_scalper_ai
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```
Tests : `python -m pytest -q`

Le cœur utilise la bibliothèque standard Python. Pandas, NumPy, pytest et MetaTrader5 sont déclarés dans `requirements.txt`; MetaTrader5 nécessite Windows et un terminal installé.

## Structure
`config/`, `mt5_connector/`, `strategies/`, `decision_engine/`, `risk_manager/`, `database/`, `tests/`.

## Limites actuelles
Ce n'est pas encore un bot prêt à trader. Il manque les indicateurs complets, le backtester, le coach génératif, l'interface graphique et l'apprentissage validé. Le connecteur MT5 est facultatif et en lecture seule.
