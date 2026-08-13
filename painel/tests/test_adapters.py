import subprocess

import pytest

from painel.harness_adapters import UnknownHarnessError, get_adapter, list_harness_names


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


def test_opencode_adapter_builds_command(tmp_path):
    adapter = get_adapter("opencode")
    inv = adapter.build_invocation(
        tmp_path, "/produzir-comunicacao-completa slug-x",
        credential={"env_var": "OPENAI_API_KEY", "api_key": "sk-oa-x"},
        model="gpt-5",
    )

    assert inv.cmd == ["opencode", "run", "/produzir-comunicacao-completa slug-x", "--model", "gpt-5"]
    assert inv.env == {"OPENAI_API_KEY": "sk-oa-x"}
