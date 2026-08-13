"""FastAPI do Painel de Controle Universal Multi-Harness.

Serviço local (não é backend cloud) — precisa acesso a filesystem arbitrário
e capacidade de spawnar processo, algo que um browser puro não tem. Todo
conteúdo gerado pela Fábrica continua sendo arquivo dentro do workspace do
usuário; o único estado próprio da aplicação é o índice de execuções
(``painel/jobs.py``) e o cofre de credenciais (``painel/vault.py``), ambos
fora do workspace.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from painel.files import ProjectNotFoundError, list_project_files
from painel.harness_adapters import list_harness_names
from painel.jobs import JobError, create_job, get_job, list_jobs, run_job
from painel.repo import REPO_ROOT
from painel.vault import VaultError, delete_credential, get_credential, list_harnesses, save_credential
from painel.workspace import WorkspaceError, list_workspaces, register_workspace

app = FastAPI(title="Painel de Controle da Fábrica de Materiais de Comunicação")


# ---------- workspace (pasta escolhida pelo usuário) ----------

@app.get("/api/repo-workspace")
def api_repo_workspace():
    """Sugestão de workspace dentro deste repositório (``<repo>/output``).

    É a configuração recomendada para harnesses reais (claude-code) terem
    acesso a `.claude/skills`, `AGENTS.md` e `SPEC_COMANDOS.md` — o job
    runner detecta automaticamente quando o projeto está dentro deste repo e
    libera esse acesso (ver `painel/jobs.py` e a validação real no README).
    """
    return {"path": str(REPO_ROOT / "output")}


class WorkspaceIn(BaseModel):
    path: str


@app.post("/api/workspaces")
def api_register_workspace(body: WorkspaceIn):
    try:
        return register_workspace(body.path)
    except WorkspaceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/workspaces")
def api_list_workspaces():
    return list_workspaces()


# ---------- credenciais (cofre local, nunca no workspace) ----------

class CredentialIn(BaseModel):
    harness: str
    env_var: str
    api_key: str


@app.post("/api/credentials")
def api_save_credential(body: CredentialIn):
    try:
        save_credential(body.harness, env_var=body.env_var, api_key=body.api_key)
    except VaultError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"harness": body.harness, "saved": True}


@app.get("/api/credentials")
def api_list_credentials():
    return {"harnesses_com_credencial": list_harnesses()}


@app.delete("/api/credentials/{harness}")
def api_delete_credential(harness: str):
    return {"harness": harness, "deleted": delete_credential(harness)}


# ---------- harnesses disponiveis no registry ----------

@app.get("/api/harnesses")
def api_list_harnesses():
    return {"harnesses": list_harness_names()}


# ---------- projetos: sempre arquivo dentro do workspace, nunca banco ----------

class ProjectIn(BaseModel):
    workspace_path: str
    slug: str
    texto_base: str = ""
    publico_alvo: str = ""
    objetivo_tom: str = ""
    materiais_selecionados: list[str] = []
    edicao: str | None = None
    elementos_decorativos: bool = True


@app.post("/api/projects")
def api_create_project(body: ProjectIn):
    project_dir = Path(body.workspace_path) / body.slug
    project_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "slug": body.slug,
        "texto_base": body.texto_base,
        "publico_alvo": body.publico_alvo,
        "objetivo_tom": body.objetivo_tom,
        "materiais_selecionados": body.materiais_selecionados,
        "edicao": body.edicao,
        "elementos_decorativos": body.elementos_decorativos,
    }
    config_path = project_dir / "config_projeto.json"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    return config


@app.get("/api/projects")
def api_list_projects(workspace_path: str):
    root = Path(workspace_path)
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_path}' não existe.")

    projetos = []
    for child in sorted(root.iterdir()):
        config_path = child / "config_projeto.json"
        if child.is_dir() and config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            manifesto_path = child / "manifesto_materiais.json"
            manifesto = (
                json.loads(manifesto_path.read_text(encoding="utf-8"))
                if manifesto_path.exists()
                else None
            )
            tem_brief = (child / "brief_criativo.json").exists()
            projetos.append({
                "slug": child.name,
                "config": config,
                "manifesto": manifesto,
                "tem_brief": tem_brief,
            })
    return projetos


# ---------- arquivos do projeto: sempre lidos do disco, nunca de banco ----------

@app.get("/api/projects/files")
def api_list_project_files(workspace_path: str, slug: str):
    try:
        return list_project_files(workspace_path, slug)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ---------- jobs: dispara o harness escolhido em thread de segundo plano ----------

class JobIn(BaseModel):
    workspace_path: str
    slug: str
    harness: str
    prompt: str
    model: str | None = None
    permission_mode: str | None = None  # None (padrão) | "scoped" | "bypass"
    command: str | None = None  # nome do comando sem a barra (ex.: "gerar-pdf")


# Comandos que regeneram 1 material a partir de um projeto já esboçado — todos
# "falham rápido" sem brief_criativo.json (ver .claude/commands/*.md). `esbocar`
# e `kit-completo-*` ficam de fora porque são eles que CRIAM o brief; um
# "customizado" (command=None) não entra na lista porque não dá pra saber o
# que ele exige.
COMANDOS_QUE_EXIGEM_BRIEF_PREVIO = {
    "gerar-pdf", "gerar-landing", "gerar-apresentacao",
    "gerar-arte", "gerar-arte-1080x1080", "gerar-arte-1080x1350", "gerar-arte-1080x1920",
    "gerar-textos", "gerar-kit-consultor", "gerar-kit-distribuidor",
    "produzir-comunicacao-completa",
}


@app.post("/api/jobs")
def api_create_job(body: JobIn):
    if body.command in COMANDOS_QUE_EXIGEM_BRIEF_PREVIO:
        brief_path = Path(body.workspace_path) / body.slug / "brief_criativo.json"
        if not brief_path.exists():
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Projeto '{body.slug}' ainda não tem brief_criativo.json — "
                    f"rode /esbocar para este slug antes de /{body.command}."
                ),
            )
    try:
        job = create_job(
            body.workspace_path,
            body.slug,
            body.harness,
            model=body.model,
            permission_mode=body.permission_mode,
        )
    except JobError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    credential = get_credential(body.harness)
    thread = threading.Thread(target=run_job, args=(job["id"], body.prompt, credential), daemon=True)
    thread.start()
    return job


@app.get("/api/jobs")
def api_list_jobs(workspace_path: str | None = None):
    return list_jobs(workspace_path)


@app.get("/api/jobs/{job_id}")
def api_get_job(job_id: int):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado.")
    return job


_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
