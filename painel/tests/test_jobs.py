import sys
import time

import pytest

from painel.harness_adapters.base import HarnessAdapter, HeadlessInvocation
from painel.jobs import JobError, _extra_allowed_dirs_for, create_job, get_job, list_jobs, run_job
from painel.repo import REPO_ROOT


def test_create_job_starts_pending(tmp_path):
    job = create_job(str(tmp_path), "meu-slug", "echo", model="m1")

    assert job["status"] == "pending"
    assert job["slug"] == "meu-slug"
    assert job["harness"] == "echo"
    assert job["model"] == "m1"


def test_create_job_rejects_unknown_harness(tmp_path):
    with pytest.raises(JobError):
        create_job(str(tmp_path), "meu-slug", "harness-inventado")


def test_create_job_persists_permission_mode(tmp_path):
    job = create_job(str(tmp_path), "meu-slug", "echo", permission_mode="scoped")
    assert job["permission_mode"] == "scoped"
    assert get_job(job["id"])["permission_mode"] == "scoped"


def test_create_job_rejects_invalid_permission_mode(tmp_path):
    with pytest.raises(JobError):
        create_job(str(tmp_path), "meu-slug", "echo", permission_mode="modo-invalido")


def test_get_job_roundtrip(tmp_path):
    created = create_job(str(tmp_path), "slug-a", "echo")
    fetched = get_job(created["id"])

    assert fetched == created


def test_list_jobs_filtered_by_workspace(tmp_path):
    ws_a, ws_b = tmp_path / "a", tmp_path / "b"
    create_job(str(ws_a), "slug-a1", "echo")
    create_job(str(ws_a), "slug-a2", "echo")
    create_job(str(ws_b), "slug-b1", "echo")

    assert len(list_jobs(str(ws_a))) == 2
    assert len(list_jobs(str(ws_b))) == 1
    assert len(list_jobs()) == 3


def test_run_job_with_echo_adapter_creates_artifact_and_marks_done(tmp_path):
    job = create_job(str(tmp_path), "slug-real", "echo", model="m1")
    finished = run_job(job["id"], "PROVA_JOB_RUNNER")

    assert finished["status"] == "done"
    assert finished["exit_code"] == 0

    project_dir = tmp_path / "slug-real"
    marker = project_dir / "smoke_marker.txt"
    assert marker.read_text(encoding="utf-8") == "PROVA_JOB_RUNNER"

    log_content = open(finished["log_path"], encoding="utf-8").read()
    assert "ECHO_OK:PROVA_JOB_RUNNER" in log_content


def test_list_jobs_matches_regardless_of_slash_style(tmp_path):
    """Regressão: workspace passado com barras diferentes (/ vs \\) não pode
    virar entradas "invisíveis" na listagem por não bater a igualdade de string."""
    forward_slash_path = str(tmp_path).replace("\\", "/")
    create_job(forward_slash_path, "slug-barra", "echo")

    listed = list_jobs(str(tmp_path))
    assert any(j["slug"] == "slug-barra" for j in listed)


def test_extra_allowed_dirs_empty_for_workspace_outside_repo(tmp_path):
    assert _extra_allowed_dirs_for(tmp_path / "algum-projeto") == []


def test_extra_allowed_dirs_includes_repo_root_when_project_is_inside_repo():
    project_dir_inside_repo = REPO_ROOT / "output" / "algum-slug-que-nao-existe"
    assert _extra_allowed_dirs_for(project_dir_inside_repo) == [REPO_ROOT]


def test_run_job_unknown_job_id_raises():
    with pytest.raises(JobError):
        run_job(999999, "prompt")


class _FailingAdapter(HarnessAdapter):
    name = "fail-fake"

    def build_invocation(
        self, cwd, prompt, credential=None, model=None, extra_allowed_dirs=None, permission_mode=None
    ):
        return HeadlessInvocation(cmd=["binario-que-definitivamente-nao-existe-xyz"], cwd=cwd)


def test_run_job_marks_error_when_binary_missing(tmp_path, monkeypatch):
    job = create_job(str(tmp_path), "slug-erro", "echo")
    monkeypatch.setattr("painel.jobs.get_adapter", lambda name: _FailingAdapter())

    finished = run_job(job["id"], "prompt qualquer")

    assert finished["status"] == "error"
    assert finished["exit_code"] is None
    log_content = open(finished["log_path"], encoding="utf-8").read()
    assert "ERRO ao spawnar processo" in log_content


class _NetoOrfaoAdapter(HarnessAdapter):
    """Simula o harness real: o processo direto termina rápido, mas deixa
    para trás um neto (processo filho do processo filho) que herda os
    handles e continua vivo por um tempo."""

    name = "neto-orfao-fake"

    def build_invocation(
        self, cwd, prompt, credential=None, model=None, extra_allowed_dirs=None, permission_mode=None
    ):
        script = (
            "import subprocess, sys\n"
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(3)'], close_fds=False)\n"
            "print('PROCESSO_DIRETO_TERMINOU')\n"
        )
        return HeadlessInvocation(cmd=[sys.executable, "-c", script], cwd=cwd)


def test_run_job_does_not_hang_waiting_for_orphaned_grandchild(tmp_path, monkeypatch):
    """Regressão: com stdout/stderr capturados via subprocess.PIPE,
    `subprocess.run()` só retorna quando TODOS os handles do pipe fecham —
    inclusive o de um neto que herdou o handle e continua vivo depois que o
    processo filho direto já terminou. Isso deixava o job preso em
    "running" para sempre mesmo com o trabalho de verdade (arquivos no
    workspace) já concluído — achado real, não hipotético. Redirecionar
    stdout/stderr para o arquivo de log (painel/jobs.py) remove essa
    dependência: o runner só espera o PID do processo filho direto."""
    job = create_job(str(tmp_path), "slug-neto-orfao", "echo")
    monkeypatch.setattr("painel.jobs.get_adapter", lambda name: _NetoOrfaoAdapter())

    inicio = time.monotonic()
    finished = run_job(job["id"], "prompt qualquer", timeout=10)
    decorrido = time.monotonic() - inicio

    assert finished["status"] == "done"
    assert decorrido < 2.0, (
        f"run_job levou {decorrido:.1f}s — parece estar esperando o neto órfão "
        "(que dorme 3s) em vez de só o processo filho direto."
    )
