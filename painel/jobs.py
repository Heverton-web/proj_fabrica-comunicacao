"""Job runner: spawna o adaptador de harness escolhido em subprocess real e
mantém o índice de execuções. O índice guarda só status/log/exit-code da
execução — nunca o conteúdo gerado, que fica exclusivamente dentro da pasta
do projeto, dentro do workspace escolhido pelo usuário.
"""

from __future__ import annotations

import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from painel.appdata import appdata_dir
from painel.db import get_connection
from painel.harness_adapters import get_adapter, list_harness_names
from painel.repo import REPO_ROOT


class JobError(RuntimeError):
    """Job inválido ou falha ao preparar/executar a invocação."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_workspace_path(workspace_path: str) -> str:
    """Canoniza o caminho antes de gravar/filtrar — sem isso, o mesmo workspace
    passado com barras diferentes (``/`` vs ``\\``) vira duas linhas
    distintas no índice e a filtragem por igualdade de string falha
    silenciosamente."""
    return str(Path(workspace_path).expanduser().resolve())


def _logs_dir() -> Path:
    d = appdata_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


PERMISSION_MODES = (None, "scoped", "bypass")


def create_job(
    workspace_path: str,
    slug: str,
    harness: str,
    model: str | None = None,
    permission_mode: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> dict:
    if harness not in list_harness_names():
        raise JobError(f"Harness '{harness}' não registrado. Disponíveis: {list_harness_names()}")
    if permission_mode not in PERMISSION_MODES:
        raise JobError(f"permission_mode {permission_mode!r} inválido. Use um de {PERMISSION_MODES}.")

    workspace_path = _normalize_workspace_path(workspace_path)

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        now = _now()
        cur = conn.execute(
            "INSERT INTO jobs (workspace_path, slug, harness, model, permission_mode, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)",
            (workspace_path, slug, harness, model, permission_mode, now, now),
        )
        conn.commit()
        return get_job(cur.lastrowid, conn=conn)
    finally:
        if own_conn:
            conn.close()


def get_job(job_id: int, conn: sqlite3.Connection | None = None) -> dict | None:
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None
    finally:
        if own_conn:
            conn.close()


def list_jobs(workspace_path: str | None = None, conn: sqlite3.Connection | None = None) -> list[dict]:
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        if workspace_path:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE workspace_path = ? ORDER BY created_at DESC",
                (_normalize_workspace_path(workspace_path),),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]
    finally:
        if own_conn:
            conn.close()


def _extra_allowed_dirs_for(project_dir: Path) -> list[Path]:
    """Se o projeto vive dentro deste repo, libera a raiz do repo para o
    harness — sem isso, `claude -p` recusa ler `AGENTS.md`/`SPEC_COMANDOS.md`
    por ficarem acima do cwd (achado real na validação, ver README)."""
    resolved = project_dir.resolve()
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        return [REPO_ROOT]
    return []


def _update_job(job_id: int, conn: sqlite3.Connection, **fields) -> None:
    fields["updated_at"] = _now()
    cols = ", ".join(f"{key} = ?" for key in fields)
    conn.execute(f"UPDATE jobs SET {cols} WHERE id = ?", (*fields.values(), job_id))
    conn.commit()


def run_job(
    job_id: int,
    prompt: str,
    credential: dict | None = None,
    timeout: int | None = None,
    conn: sqlite3.Connection | None = None,
) -> dict:
    """Executa o job de verdade (subprocess real, síncrono).

    A API HTTP roda isso em uma thread de segundo plano para não bloquear a
    requisição (ver ``painel/main.py``); aqui a execução é síncrona de
    propósito, para manter o teste determinístico e simples.
    """
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        job = get_job(job_id, conn=conn)
        if job is None:
            raise JobError(f"Job {job_id} não encontrado.")

        project_dir = Path(job["workspace_path"]) / job["slug"]
        project_dir.mkdir(parents=True, exist_ok=True)

        adapter = get_adapter(job["harness"])
        invocation = adapter.build_invocation(
            project_dir,
            prompt,
            credential=credential,
            model=job["model"],
            extra_allowed_dirs=_extra_allowed_dirs_for(project_dir),
            permission_mode=job.get("permission_mode"),
        )

        log_path = _logs_dir() / f"job-{job_id}.log"
        _update_job(job_id, conn, status="running")

        try:
            result = subprocess.run(
                invocation.resolved_cmd(),
                cwd=invocation.cwd,
                env=invocation.full_env(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            log_path.write_text(f"ERRO ao spawnar processo: {exc}", encoding="utf-8")
            _update_job(job_id, conn, status="error", log_path=str(log_path), exit_code=None)
            return get_job(job_id, conn=conn)

        log_path.write_text(
            "$ "
            + " ".join(invocation.cmd)
            + f"\n\n--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}\n",
            encoding="utf-8",
        )
        status = "done" if result.returncode == 0 else "error"
        _update_job(job_id, conn, status=status, log_path=str(log_path), exit_code=result.returncode)
        return get_job(job_id, conn=conn)
    finally:
        if own_conn:
            conn.close()
