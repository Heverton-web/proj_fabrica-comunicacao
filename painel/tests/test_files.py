import os
import time

import pytest

from painel.files import ProjectNotFoundError, list_project_files


def test_list_project_files_raises_when_project_missing(tmp_path):
    with pytest.raises(ProjectNotFoundError):
        list_project_files(str(tmp_path), "nao-existe")


def test_list_project_files_sorted_by_mtime(tmp_path):
    project_dir = tmp_path / "slug-a"
    project_dir.mkdir()

    older = project_dir / "config_projeto.json"
    older.write_text("{}", encoding="utf-8")
    os.utime(older, (1000, 1000))

    newer = project_dir / "arte" / "capa.png"
    newer.parent.mkdir()
    newer.write_text("fake-png", encoding="utf-8")
    os.utime(newer, (2000, 2000))

    arquivos = list_project_files(str(tmp_path), "slug-a")

    assert [a["path"] for a in arquivos] == ["config_projeto.json", "arte/capa.png"]


def test_list_project_files_uses_forward_slashes_for_nested_paths(tmp_path):
    project_dir = tmp_path / "slug-b"
    (project_dir / "kits" / "kit-consultor").mkdir(parents=True)
    (project_dir / "kits" / "kit-consultor" / "item-01.png").write_text("x", encoding="utf-8")

    arquivos = list_project_files(str(tmp_path), "slug-b")

    assert arquivos[0]["path"] == "kits/kit-consultor/item-01.png"
    assert "\\" not in arquivos[0]["path"]


def test_list_project_files_reports_size(tmp_path):
    project_dir = tmp_path / "slug-c"
    project_dir.mkdir()
    (project_dir / "a.txt").write_text("conteudo de teste", encoding="utf-8")

    arquivos = list_project_files(str(tmp_path), "slug-c")

    assert arquivos[0]["size"] == len("conteudo de teste")
