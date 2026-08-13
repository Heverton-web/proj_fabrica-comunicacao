"""Índice local (SQLite) de workspaces registrados e execuções (jobs).

Guarda só bookkeeping da aplicação — nunca o conteúdo gerado pela Fábrica, que
permanece exclusivamente como arquivos dentro do workspace escolhido pelo
usuário.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from painel.appdata import appdata_dir

SCHEMA = """
CREATE TABLE IF NOT EXISTS workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_path TEXT NOT NULL,
    slug TEXT NOT NULL,
    harness TEXT NOT NULL,
    model TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    log_path TEXT,
    pid INTEGER,
    exit_code INTEGER
);
"""

# Migrações leves (SQLite não tem "ADD COLUMN IF NOT EXISTS") — cada uma é
# idempotente: se a coluna já existe, o OperationalError é engolido.
_MIGRATIONS = [
    "ALTER TABLE jobs ADD COLUMN permission_mode TEXT",
]


def db_path() -> Path:
    return appdata_dir() / "painel.db"


def get_connection(path: Path | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path or db_path()))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    for migration in _MIGRATIONS:
        try:
            conn.execute(migration)
        except sqlite3.OperationalError:
            pass  # coluna já existe de uma execução anterior
    conn.commit()
    return conn
