# Quantum Scalper AI — connexion MT5 en lecture seule

Ce projet est un prototype de recherche/simulation en Python. Il se connecte au terminal MetaTrader 5, télécharge des bougies clôturées pour XAUUSD en M1, M5 et M15, calcule des indicateurs et affiche des signaux diagnostiques. **Aucun ordre n'est envoyé.**

## Sécurité
- `BOT_MODE` doit rester `PAPER` ; tout autre mode est refusé.
- `ORDER_EXECUTION_ENABLED=true` est refusé.
- Le connecteur ne contient aucune méthode `order_send` et ne demande aucun mot de passe.
- Les stratégies sont des règles de prototype, pas un système de trading validé ni une promesse de résultat.
- La base SQLite et les secrets restent locaux et doivent être exclus de Git.

## Installation Windows / VS Code
1. Lance MetaTrader 5 et connecte-toi à un compte de démonstration ou à un terminal disposant de données historiques. Le programme ne se connecte pas à un compte en fournissant un identifiant ou un mot de passe.
2. Depuis le dossier du projet, dans PowerShell :

```powershell
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt
```

3. Copie `.env.example` vers `.env` si tu n'as pas encore de fichier `.env`. Vérifie `MT5_SYMBOL` : il doit correspondre au nom exact affiché dans Market Watch. Certains courtiers ajoutent un suffixe au symbole.
4. Si MT5 n'est pas détecté automatiquement, renseigne `MT5_PATH` dans `.env`, par exemple `C:\Program Files\MetaTrader 5\terminal64.exe`.
5. Lance le diagnostic :

```powershell
py -3.12 .\main.py
```

## Résultat attendu
Le programme indique la connexion MT5, le nombre de bougies lues pour M1/M5/M15, l'heure de la dernière bougie, le close, EMA9/EMA21, RSI14, ADX14 et ATR14. Il imprime les raisons des signaux prototypes M5 et attend un consensus ainsi que des filtres M1/M15 cohérents.

Si MT5 ou l'historique est indisponible, le programme affiche une erreur lisible et reste en attente. Si les données semblent périmées, l'analyse directionnelle est bloquée.

## Tests

```powershell
py -3.12 -m pytest -q
```

Les tests vérifient les indicateurs, le connecteur avec un faux terminal et les garde-fous PAPER sans avoir besoin de se connecter à MT5.

## Limites connues
- Les stratégies ne sont pas validées par des backtests hors échantillon.
- Il manque encore une validation complète des coûts, du spread, du slippage et de la robustesse aux données.
- Cette livraison ne doit pas être utilisée pour exécuter des transactions réelles.
