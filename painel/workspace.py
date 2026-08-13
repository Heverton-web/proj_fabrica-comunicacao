"""Workspace: a pasta que o usuário escolhe para guardar todos os projetos e
artefatos gerados pela Fábrica. Nunca há banco de dados de conteúdo — só um
registro leve (caminho + quando foi registrado) no índice local da aplicação.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from painel.appdata import appdata_dir
from painel.db import get_connection
from painel.repo import REPO_ROOT

# Workspace raiz recomendado pelo atalho "usar output/ deste repo" (ver
# /api/repo-workspace) -- nunca pode ser removido do indice, nem so o
# registro (delete_workspace não apaga arquivo nenhum de qualquer forma,
# mas essa pasta é tratada como intocável em qualquer circunstância).
_WORKSPACE_RAIZ_PROTEGIDO = str((REPO_ROOT / "output").resolve())


class WorkspaceError(ValueError):
    """Pasta de workspace inválida ou conflitante."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_workspace_path(raw_path: str) -> Path:
    if not raw_path or not raw_path.strip():
        raise WorkspaceError("Caminho do workspace não pode ser vazio.")

    path = Path(raw_path).expanduser().resolve()

    app_dir = appdata_dir().resolve()
    if path == app_dir or app_dir in path.parents:
        raise WorkspaceError(
            "O workspace não pode ser a pasta de dados internos do painel "
            f"({app_dir}). Escolha uma pasta separada para os artefatos."
        )

    if path.exists() and not path.is_dir():
        raise WorkspaceError(f"'{path}' existe e não é uma pasta.")

    return path


def register_workspace(raw_path: str, conn: sqlite3.Connection | None = None) -> dict:
    path = validate_workspace_path(raw_path)
    path.mkdir(parents=True, exist_ok=True)

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        conn.execute(
            "INSERT INTO workspaces (path, created_at) VALUES (?, ?) "
            "ON CONFLICT(path) DO NOTHING",
            (str(path), _now()),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM workspaces WHERE path = ?", (str(path),)
        ).fetchone()
        return dict(row)
    finally:
        if own_conn:
            conn.close()


def list_workspaces(conn: sqlite3.Connection | None = None) -> list[dict]:
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM workspaces ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        if own_conn:
            conn.close()


def delete_workspace(raw_path: str, conn: sqlite3.Connection | None = None) -> bool:
    """Remove só o registro do workspace do índice do painel — a pasta e os
    artefatos dentro dela nunca são tocados (mesma regra de nunca ter banco
    de conteúdo). Útil pra tirar da lista workspaces de teste/temporários que
    não têm mais utilidade.

    O workspace raiz `<repo>/output` nunca pode ser removido, nem do índice
    — é o workspace canônico recomendado para uso com harness real (ver
    `/api/repo-workspace`), tratado como intocável em qualquer circunstância."""
    path = str(Path(raw_path).expanduser().resolve())

    if path == _WORKSPACE_RAIZ_PROTEGIDO:
        raise WorkspaceError(
            "O workspace raiz deste repo ('output/') nunca pode ser removido — "
            "nem da lista, nem (muito menos) do disco."
        )

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        cur = conn.execute("DELETE FROM workspaces WHERE path = ?", (path,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        if own_conn:
            conn.close()
