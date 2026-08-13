import time
from pathlib import Path

from fastapi.testclient import TestClient

from painel.main import app

client = TestClient(app)


def _wait_job_finished(job_id: int, timeout: float = 5.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.get(f"/api/jobs/{job_id}")
        job = resp.json()
        if job["status"] in ("done", "error"):
            return job
        time.sleep(0.05)
    raise AssertionError(f"Job {job_id} não terminou em {timeout}s")


def test_repo_workspace_suggestion_points_inside_repo():
    from painel.repo import REPO_ROOT

    resp = client.get("/api/repo-workspace")
    assert resp.status_code == 200
    suggested = Path(resp.json()["path"])
    assert suggested == REPO_ROOT / "output"
    assert REPO_ROOT in suggested.parents


def test_register_and_list_workspace(tmp_path):
    target = tmp_path / "meu-workspace"
    resp = client.post("/api/workspaces", json={"path": str(target)})
    assert resp.status_code == 200
    assert resp.json()["path"] == str(target.resolve())

    listed = client.get("/api/workspaces").json()
    assert any(w["path"] == str(target.resolve()) for w in listed)


def test_register_workspace_rejects_invalid_path():
    resp = client.post("/api/workspaces", json={"path": "   "})
    assert resp.status_code == 400


def test_delete_workspace_endpoint_removes_only_the_index_entry(tmp_path):
    target = tmp_path / "workspace-descartavel"
    client.post("/api/workspaces", json={"path": str(target)})

    resp = client.delete("/api/workspaces", params={"path": str(target)})
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    assert target.exists()

    listed = client.get("/api/workspaces").json()
    assert not any(w["path"] == str(target.resolve()) for w in listed)


def test_credentials_roundtrip_never_leaks_secret_in_list():
    resp = client.post(
        "/api/credentials",
        json={"harness": "claude-code", "env_var": "ANTHROPIC_API_KEY", "api_key": "sk-ant-secreta"},
    )
    assert resp.status_code == 200

    listed = client.get("/api/credentials").json()
    assert "claude-code" in listed["harnesses_com_credencial"]
    assert "sk-ant-secreta" not in str(listed)

    deleted = client.delete("/api/credentials/claude-code").json()
    assert deleted["deleted"] is True


def test_list_harnesses_endpoint():
    resp = client.get("/api/harnesses")
    assert resp.json() == {"harnesses": ["claude-code", "echo", "opencode"]}


def test_create_project_writes_file_in_workspace_not_database(tmp_path):
    resp = client.post(
        "/api/projects",
        json={
            "workspace_path": str(tmp_path),
            "slug": "projeto-teste",
            "texto_base": "texto mãe de teste",
            "publico_alvo": "consultores",
            "objetivo_tom": "educacional_comercial",
            "materiais_selecionados": ["pdf", "textos"],
        },
    )
    assert resp.status_code == 200

    config_file = tmp_path / "projeto-teste" / "config_projeto.json"
    assert config_file.exists()
    on_disk = config_file.read_text(encoding="utf-8")
    assert "consultores" in on_disk


def test_list_projects_reads_from_folder(tmp_path):
    client.post(
        "/api/projects",
        json={"workspace_path": str(tmp_path), "slug": "proj-a"},
    )
    client.post(
        "/api/projects",
        json={"workspace_path": str(tmp_path), "slug": "proj-b"},
    )

    listed = client.get("/api/projects", params={"workspace_path": str(tmp_path)}).json()
    slugs = {p["slug"] for p in listed}
    assert slugs == {"proj-a", "proj-b"}


def test_create_and_run_job_end_to_end_via_http(tmp_path):
    created = client.post(
        "/api/jobs",
        json={
            "workspace_path": str(tmp_path),
            "slug": "job-http",
            "harness": "echo",
            "prompt": "PROVA_API_ENDPOINT",
            "model": "modelo-x",
        },
    ).json()

    finished = _wait_job_finished(created["id"])
    assert finished["status"] == "done"
    assert finished["exit_code"] == 0

    marker = tmp_path / "job-http" / "smoke_marker.txt"
    assert marker.read_text(encoding="utf-8") == "PROVA_API_ENDPOINT"


def test_list_project_files_endpoint(tmp_path):
    client.post("/api/projects", json={"workspace_path": str(tmp_path), "slug": "proj-files"})

    resp = client.get("/api/projects/files", params={"workspace_path": str(tmp_path), "slug": "proj-files"})
    assert resp.status_code == 200
    paths = [f["path"] for f in resp.json()]
    assert "config_projeto.json" in paths


def test_list_project_files_endpoint_404_when_missing(tmp_path):
    resp = client.get("/api/projects/files", params={"workspace_path": str(tmp_path), "slug": "nao-existe"})
    assert resp.status_code == 404


def test_job_list_matches_workspace_regardless_of_slash_style(tmp_path):
    forward_slash_path = str(tmp_path).replace("\\", "/")

    created = client.post(
        "/api/jobs",
        json={"workspace_path": forward_slash_path, "slug": "job-barra", "harness": "echo", "prompt": "x"},
    ).json()
    _wait_job_finished(created["id"])

    listed = client.get("/api/jobs", params={"workspace_path": str(tmp_path)}).json()
    assert any(j["slug"] == "job-barra" for j in listed)


def test_create_job_with_permission_mode(tmp_path):
    created = client.post(
        "/api/jobs",
        json={
            "workspace_path": str(tmp_path),
            "slug": "job-permissao",
            "harness": "echo",
            "prompt": "x",
            "permission_mode": "scoped",
        },
    ).json()
    assert created["permission_mode"] == "scoped"

    finished = _wait_job_finished(created["id"])
    assert finished["status"] == "done"


def test_create_job_rejects_unknown_harness(tmp_path):
    resp = client.post(
        "/api/jobs",
        json={
            "workspace_path": str(tmp_path),
            "slug": "job-x",
            "harness": "harness-inventado",
            "prompt": "x",
        },
    )
    assert resp.status_code == 400


def test_create_job_rejects_gerar_command_without_brief(tmp_path):
    resp = client.post(
        "/api/jobs",
        json={
            "workspace_path": str(tmp_path),
            "slug": "projeto-sem-brief",
            "harness": "echo",
            "prompt": "/gerar-pdf projeto-sem-brief",
            "command": "gerar-pdf",
        },
    )
    assert resp.status_code == 400
    assert "brief_criativo.json" in resp.json()["detail"]


def test_create_job_allows_gerar_command_when_brief_exists(tmp_path):
    project_dir = tmp_path / "projeto-com-brief"
    project_dir.mkdir()
    (project_dir / "brief_criativo.json").write_text("{}", encoding="utf-8")

    created = client.post(
        "/api/jobs",
        json={
            "workspace_path": str(tmp_path),
            "slug": "projeto-com-brief",
            "harness": "echo",
            "prompt": "x",
            "command": "gerar-pdf",
        },
    ).json()
    finished = _wait_job_finished(created["id"])
    assert finished["status"] == "done"


def test_create_job_allows_esbocar_without_brief(tmp_path):
    created = client.post(
        "/api/jobs",
        json={
            "workspace_path": str(tmp_path),
            "slug": "projeto-novo",
            "harness": "echo",
            "prompt": "x",
            "command": "esbocar",
        },
    ).json()
    finished = _wait_job_finished(created["id"])
    assert finished["status"] == "done"


def test_list_projects_reports_brief_presence(tmp_path):
    client.post("/api/projects", json={"workspace_path": str(tmp_path), "slug": "proj-sem-brief"})
    project_dir = tmp_path / "proj-com-brief"
    project_dir.mkdir()
    (project_dir / "config_projeto.json").write_text("{}", encoding="utf-8")
    (project_dir / "brief_criativo.json").write_text("{}", encoding="utf-8")

    listed = {p["slug"]: p for p in client.get("/api/projects", params={"workspace_path": str(tmp_path)}).json()}
    assert listed["proj-sem-brief"]["tem_brief"] is False
    assert listed["proj-com-brief"]["tem_brief"] is True
