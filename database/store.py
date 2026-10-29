import json
import sqlite3
from pathlib import Path
from typing import Any

class TradeStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.connection: sqlite3.Connection | None = None

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )''')
        self.connection.commit()

    def record_event(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.connection is None:
            raise RuntimeError("Base non initialisée")
        self.connection.execute("INSERT INTO events(event_type, payload_json) VALUES (?, ?)",
            (event_type, json.dumps(payload, ensure_ascii=False, sort_keys=True)))
        self.connection.commit()

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
