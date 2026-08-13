import pytest

from painel.workspace import (
    WorkspaceError,
    delete_workspace,
    list_workspaces,
    register_workspace,
    validate_workspace_path,
)


def test_register_workspace_creates_folder_and_record(tmp_path):
    target = tmp_path / "meus-projetos-fabrica"
    record = register_workspace(str(target))

    assert target.exists() and target.is_dir()
    assert record["path"] == str(target.resolve())
    assert record["created_at"]


def test_register_workspace_is_idempotent(tmp_path):
    target = tmp_path / "ws"
    first = register_workspace(str(target))
    second = register_workspace(str(target))

    assert first["id"] == second["id"]
    assert len(list_workspaces()) == 1


def test_register_workspace_rejects_empty_path():
    with pytest.raises(WorkspaceError):
        register_workspace("   ")


def test_register_workspace_rejects_appdata_dir(isolated_appdata):
    from painel.appdata import appdata_dir

    with pytest.raises(WorkspaceError):
        validate_workspace_path(str(appdata_dir()))


def test_register_workspace_rejects_file_path(tmp_path):
    a_file = tmp_path / "arquivo.txt"
    a_file.write_text("nao sou uma pasta")

    with pytest.raises(WorkspaceError):
        register_workspace(str(a_file))


def test_list_workspaces_orders_most_recent_first(tmp_path):
    register_workspace(str(tmp_path / "a"))
    register_workspace(str(tmp_path / "b"))

    paths = [w["path"] for w in list_workspaces()]
    assert paths[0].endswith("b")
    assert paths[1].endswith("a")


def test_delete_workspace_removes_only_the_index_entry(tmp_path):
    target = tmp_path / "workspace-de-teste"
    register_workspace(str(target))

    assert delete_workspace(str(target)) is True
    assert list_workspaces() == []
    assert target.exists()  # a pasta e os arquivos dentro dela nunca sao apagados


def test_delete_workspace_returns_false_when_not_registered(tmp_path):
    assert delete_workspace(str(tmp_path / "nunca-registrado")) is False
