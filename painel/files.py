"""Lista arquivos dentro da pasta de um projeto, direto do disco.

Usado pelo frontend para mostrar em tempo real os arquivos aparecendo
enquanto um job roda (via polling) — funciona para qualquer harness, porque
observa o filesystem em vez de tentar interpretar o log de cada CLI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


class ProjectNotFoundError(FileNotFoundError):
    """Pasta do projeto (workspace/slug) não existe."""


def list_project_files(workspace_path: str, slug: str) -> list[dict]:
    project_dir = Path(workspace_path) / slug
    if not project_dir.exists():
        raise ProjectNotFoundError(f"Projeto '{slug}' não encontrado em '{workspace_path}'.")

    arquivos = []
    for path in project_dir.rglob("*"):
        if path.is_file():
            stat = path.stat()
            arquivos.append(
                {
                    "path": str(path.relative_to(project_dir)).replace("\\", "/"),
                    "size": stat.st_size,
                    "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                }
            )
    arquivos.sort(key=lambda item: item["mtime"])
    return arquivos
