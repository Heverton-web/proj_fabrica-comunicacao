"""Cofre local de credenciais de harness/provedor de LLM.

Guarda API keys/tokens criptografados fora do workspace do usuário. Adequado
para uso pessoal single-user (chave simétrica local); não é um cofre de nível
empresarial (sem rotação de chave, sem HSM) — ver limitações no README.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from painel.appdata import appdata_dir


class VaultError(RuntimeError):
    """Cofre inválido, corrompido ou uso incorreto."""


def _key_path() -> Path:
    return appdata_dir() / "vault.key"


def _vault_path() -> Path:
    return appdata_dir() / "vault.enc"


def _restrict_permissions(path: Path) -> None:
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass  # melhor esforço; alguns filesystems (ex.: Windows/FAT) ignoram


def _load_or_create_key() -> bytes:
    key_path = _key_path()
    if key_path.exists():
        return key_path.read_bytes()
    key = Fernet.generate_key()
    key_path.write_bytes(key)
    _restrict_permissions(key_path)
    return key


def _fernet() -> Fernet:
    return Fernet(_load_or_create_key())


def _load_all() -> dict:
    vault_path = _vault_path()
    if not vault_path.exists():
        return {}
    try:
        raw = _fernet().decrypt(vault_path.read_bytes())
    except InvalidToken as exc:
        raise VaultError(
            "Não foi possível decifrar o cofre de credenciais "
            "(chave incorreta ou arquivo corrompido)."
        ) from exc
    return json.loads(raw.decode("utf-8"))


def _save_all(data: dict) -> None:
    token = _fernet().encrypt(json.dumps(data).encode("utf-8"))
    vault_path = _vault_path()
    vault_path.write_bytes(token)
    _restrict_permissions(vault_path)


def save_credential(harness: str, **fields: str) -> None:
    if not harness or not harness.strip():
        raise VaultError("Nome do harness é obrigatório.")
    data = _load_all()
    data[harness] = fields
    _save_all(data)


def get_credential(harness: str) -> dict | None:
    return _load_all().get(harness)


def list_harnesses() -> list[str]:
    return sorted(_load_all().keys())


def delete_credential(harness: str) -> bool:
    data = _load_all()
    if harness in data:
        del data[harness]
        _save_all(data)
        return True
    return False
