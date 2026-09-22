"""Durable SQLite persistence for authority state and audit events."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from .models import AuthorityToken, ExecutionEvent

class SQLiteStore:
    def __init__(self, path: str | Path = "authority.db"):
        self.path = str(path)
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS tokens (token_id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_events_task ON events(task_id);
        """)
        self.db.commit()

    def save_token(self, token: AuthorityToken) -> None:
        self.db.execute("INSERT OR REPLACE INTO tokens(token_id,payload) VALUES (?,?)", (token.token_id, token.model_dump_json()))
        self.db.commit()

    def get_token(self, token_id: str) -> AuthorityToken | None:
        row = self.db.execute("SELECT payload FROM tokens WHERE token_id=?", (token_id,)).fetchone()
        return AuthorityToken.model_validate_json(row[0]) if row else None

    def append_event(self, event: ExecutionEvent) -> None:
        self.db.execute("INSERT OR REPLACE INTO events(event_id,task_id,payload) VALUES (?,?,?)", (event.event_id, event.task_id, event.model_dump_json()))
        self.db.commit()

    def list_events(self, task_id: str | None = None) -> list[ExecutionEvent]:
        if task_id is None:
            rows = self.db.execute("SELECT payload FROM events ORDER BY rowid").fetchall()
        else:
            rows = self.db.execute("SELECT payload FROM events WHERE task_id=? ORDER BY rowid", (task_id,)).fetchall()
        return [ExecutionEvent.model_validate_json(row[0]) for row in rows]

    def close(self) -> None:
        self.db.close()
