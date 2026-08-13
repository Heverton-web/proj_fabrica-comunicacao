import shutil
import subprocess
import sys

import pytest

from painel.harness_adapters import UnknownHarnessError, get_adapter, list_harness_names
from painel.harness_adapters.base import HeadlessInvocation


def test_list_harness_names():
    assert list_harness_names() == ["claude-code", "echo", "opencode"]


def test_get_adapter_unknown_raises():
    with pytest.raises(UnknownHarnessError):
        get_adapter("nao-existe")


def test_echo_adapter_builds_invocation(tmp_path):
    adapter = get_adapter("echo")
    inv = adapter.build_invocation(
        tmp_path, "produzir slug-x", credential={"env_var": "FAKE_KEY", "api_key": "abc"}, model="modelo-y"
    )

    assert inv.cwd == tmp_path
    assert inv.cmd[-1] == "produzir slug-x"
    assert inv.env["FAKE_KEY"] == "abc"
    assert inv.env["ECHO_MODEL"] == "modelo-y"


def test_echo_adapter_real_subprocess_creates_artifact(tmp_path):
    """Único adaptador exercitado com subprocess real nesta camada (sem custo/LLM)."""
    adapter = get_adapter("echo")
    inv = adapter.build_invocation(tmp_path, "PROVA_END_TO_END")

    result = subprocess.run(
        inv.cmd, cwd=inv.cwd, env=inv.full_env(), capture_output=True, text=True, timeout=10
    )

    assert result.returncode == 0
    assert "ECHO_OK:PROVA_END_TO_END" in result.stdout
    assert (tmp_path / "smoke_marker.txt").read_text(encoding="utf-8") == "PROVA_END_TO_END"


def test_claude_code_adapter_builds_command_with_model(tmp_path):
    adapter = get_adapter("claude-code")
    inv = adapter.build_invocation(
        tmp_path, "/produzir-comunicacao-completa slug-x",
        credential={"env_var": "ANTHROPIC_API_KEY", "api_key": "sk-ant-x"},
        model="claude-sonnet-5",
    )

    assert inv.cmd == ["claude", "-p", "/produzir-comunicacao-completa slug-x", "--model", "claude-sonnet-5"]
    assert inv.env == {"ANTHROPIC_API_KEY": "sk-ant-x"}


def test_claude_code_adapter_builds_command_without_model(tmp_path):
    adapter = get_adapter("claude-code")
    inv = adapter.build_invocation(tmp_path, "/esbocar")

    assert inv.cmd == ["claude", "-p", "/esbocar"]
    assert inv.env == {}


def test_resolved_cmd_resolves_executable_via_path(tmp_path):
    """Regressão: no Windows, CLIs instaladas via npm são shims .cmd/.bat —
    sem resolver via shutil.which, subprocess com shell=False não acha o
    binário mesmo ele existindo e funcionando no terminal."""
    nome_no_path = "python" if shutil.which("python") else sys.executable
    inv = HeadlessInvocation(cmd=[nome_no_path, "--version"], cwd=tmp_path)

    resolvido = inv.resolved_cmd()

    assert resolvido[0] == shutil.which(nome_no_path)
    result = subprocess.run(resolvido, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0


def test_resolved_cmd_falls_back_when_binary_not_found(tmp_path):
    inv = HeadlessInvocation(cmd=["binario-que-definitivamente-nao-existe-xyz"], cwd=tmp_path)

    assert inv.resolved_cmd() == inv.cmd


def test_opencode_adapter_builds_command(tmp_path):
    adapter = get_adapter("opencode")
    inv = adapter.build_invocation(
        tmp_path, "/produzir-comunicacao-completa slug-x",
        credential={"env_var": "OPENAI_API_KEY", "api_key": "sk-oa-x"},
        model="gpt-5",
    )

    assert inv.cmd == ["opencode", "run", "/produzir-comunicacao-completa slug-x", "--model", "gpt-5"]
    assert inv.env == {"OPENAI_API_KEY": "sk-oa-x"}


def test_claude_code_adapter_adds_extra_allowed_dirs(tmp_path):
    """Achado real na validação: sem --add-dir, claude -p recusa ler
    AGENTS.md/SPEC_COMANDOS.md quando eles ficam acima do cwd."""
    repo_root = tmp_path / "repo"
    adapter = get_adapter("claude-code")
    inv = adapter.build_invocation(
        tmp_path / "repo" / "output" / "slug-x",
        "/produzir-comunicacao-completa slug-x",
        extra_allowed_dirs=[repo_root],
    )

    assert inv.cmd == [
        "claude", "-p", "/produzir-comunicacao-completa slug-x",
        "--add-dir", str(repo_root),
    ]


def test_opencode_adapter_ignores_extra_allowed_dirs_without_error(tmp_path):
    adapter = get_adapter("opencode")
    inv = adapter.build_invocation(tmp_path, "/esbocar", extra_allowed_dirs=[tmp_path.parent])

    assert "--add-dir" not in inv.cmd


def test_claude_code_scoped_permission_mode_adds_allowed_tools(tmp_path):
    adapter = get_adapter("claude-code")
    inv = adapter.build_invocation(tmp_path, "/esbocar", permission_mode="scoped")

    assert "--allowedTools" in inv.cmd
    assert "--allow-dangerously-skip-permissions" not in inv.cmd


def test_claude_code_bypass_permission_mode_adds_skip_permissions_flag(tmp_path):
    adapter = get_adapter("claude-code")
    inv = adapter.build_invocation(tmp_path, "/esbocar", permission_mode="bypass")

    assert "--allow-dangerously-skip-permissions" in inv.cmd
    assert "--allowedTools" not in inv.cmd


def test_claude_code_default_permission_mode_adds_no_extra_flag(tmp_path):
    adapter = get_adapter("claude-code")
    inv = adapter.build_invocation(tmp_path, "/esbocar")

    assert inv.cmd == ["claude", "-p", "/esbocar"]


def test_opencode_bypass_permission_mode_adds_auto_flag(tmp_path):
    adapter = get_adapter("opencode")
    inv = adapter.build_invocation(tmp_path, "/esbocar", permission_mode="bypass")

    assert "--auto" in inv.cmd


def test_opencode_scoped_permission_mode_has_no_known_equivalent(tmp_path):
    adapter = get_adapter("opencode")
    inv = adapter.build_invocation(tmp_path, "/esbocar", permission_mode="scoped")

    assert inv.cmd == ["opencode", "run", "/esbocar"]
