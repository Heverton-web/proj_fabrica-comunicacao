import pytest

from painel.appdata import appdata_dir
from painel.vault import VaultError, delete_credential, get_credential, list_harnesses, save_credential


def test_save_and_get_credential_roundtrip():
    save_credential("claude-code", api_key="sk-ant-super-secreta", model="claude-sonnet-5")

    cred = get_credential("claude-code")
    assert cred == {"api_key": "sk-ant-super-secreta", "model": "claude-sonnet-5"}


def test_get_credential_missing_returns_none():
    assert get_credential("nao-existe") is None


def test_list_harnesses_sorted():
    save_credential("opencode", api_key="a")
    save_credential("claude-code", api_key="b")

    assert list_harnesses() == ["claude-code", "opencode"]


def test_delete_credential():
    save_credential("opencode", api_key="a")
    assert delete_credential("opencode") is True
    assert get_credential("opencode") is None
    assert delete_credential("opencode") is False


def test_save_credential_rejects_empty_harness():
    with pytest.raises(VaultError):
        save_credential("", api_key="x")


def test_vault_file_on_disk_is_encrypted_not_plaintext():
    secret = "sk-ant-nao-deve-aparecer-em-claro"
    save_credential("claude-code", api_key=secret)

    vault_bytes = (appdata_dir() / "vault.enc").read_bytes()
    assert secret.encode("utf-8") not in vault_bytes
