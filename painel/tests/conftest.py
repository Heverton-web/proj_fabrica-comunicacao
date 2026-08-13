import pytest


@pytest.fixture(autouse=True)
def isolated_appdata(tmp_path, monkeypatch):
    """Nunca deixa um teste tocar o ~/.fabrica-painel real do usuário."""
    monkeypatch.setenv("FABRICA_PAINEL_HOME", str(tmp_path / "appdata"))
    yield tmp_path
