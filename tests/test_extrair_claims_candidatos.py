import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Nome do arquivo tem hifen (convencao do repo, ex.: verificar-universalidade.py)
# - nao e um nome de modulo Python valido pra `import` direto.
_spec = importlib.util.spec_from_file_location(
    "extrair_claims_candidatos", REPO_ROOT / "scripts" / "extrair-claims-candidatos.py"
)
extrair = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(extrair)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(extrair, "DIR_OUTPUT", tmp_path)
    return tmp_path


def _montar_projeto(base, slug, tipo, dossie_texto, arquivos_txt):
    projeto = base / slug
    (projeto / tipo).mkdir(parents=True)
    (projeto / "insumos").mkdir(parents=True)
    (projeto / "insumos" / "dossie_insumos.md").write_text(dossie_texto, encoding="utf-8")
    for nome, conteudo in arquivos_txt.items():
        (projeto / tipo / nome).write_text(conteudo, encoding="utf-8")
    return projeto


def test_hashtag_fora_do_dossie_e_flagrada(workspace):
    """Reproduz o defeito real que o revisor-marca corrigiu no teste (hashtags
    de outro nicho coladas por engano)."""
    _montar_projeto(
        workspace,
        "slug-a",
        "textos",
        dossie_texto="Kit Teste Painel ajuda consultores a apresentar o programa de indicacao.",
        arquivos_txt={"instagram.txt": "Confira o Kit Teste Painel! #ConexaoImplantes #KitTestePainel"},
    )

    relatorio = extrair.analisar("slug-a", "textos")
    hashtags = [c for c in relatorio["candidatos"] if c["categoria"] == "hashtag"]

    achado = next(c for c in hashtags if c["trecho"] == "#ConexaoImplantes")
    assert achado["encontrado_no_dossie"] is False

    ok = next(c for c in hashtags if c["trecho"] == "#KitTestePainel")
    assert ok["encontrado_no_dossie"] is True


def test_percentual_encontrado_no_dossie_nao_e_flagrado(workspace):
    _montar_projeto(
        workspace,
        "slug-b",
        "textos",
        dossie_texto="O produto reduz o tempo de reuniao em 30% comparado ao metodo antigo.",
        arquivos_txt={"whatsapp.txt": "Reduza em 30% o tempo da sua reuniao!"},
    )

    relatorio = extrair.analisar("slug-b", "textos")
    percentuais = [c for c in relatorio["candidatos"] if c["categoria"] == "percentual"]

    assert percentuais and all(c["encontrado_no_dossie"] for c in percentuais)


def test_percentual_inventado_e_flagrado(workspace):
    _montar_projeto(
        workspace,
        "slug-c",
        "textos",
        dossie_texto="O produto ajuda consultores a vender mais.",
        arquivos_txt={"whatsapp.txt": "Aumente suas vendas em 87%!"},
    )

    relatorio = extrair.analisar("slug-c", "textos")
    percentuais = [c for c in relatorio["candidatos"] if c["categoria"] == "percentual"]

    assert percentuais[0]["encontrado_no_dossie"] is False


def test_numero_com_unidade_e_extraido(workspace):
    _montar_projeto(
        workspace,
        "slug-d",
        "textos",
        dossie_texto="Apresente o programa em uma reuniao de 15 minutos.",
        arquivos_txt={"whatsapp.txt": "Aprenda a apresentar em 15 minutos."},
    )

    relatorio = extrair.analisar("slug-d", "textos")
    unidades = [c for c in relatorio["candidatos"] if c["categoria"] == "numero_unidade"]

    assert any(c["trecho"] == "15 minutos" and c["encontrado_no_dossie"] for c in unidades)


def test_nome_proprio_multi_palavra_e_extraido(workspace):
    _montar_projeto(
        workspace,
        "slug-e",
        "textos",
        dossie_texto="A Conexao lanca o Kit Teste Painel para consultores.",
        arquivos_txt={"linkedin.txt": "Conheca o Kit Teste Painel da Conexao."},
    )

    relatorio = extrair.analisar("slug-e", "textos")
    nomes = [c["trecho"] for c in relatorio["candidatos"] if c["categoria"] == "nome_proprio"]

    assert "Kit Teste Painel" in nomes


def test_numero_dentro_de_hashtag_nao_gera_submatch_espurio(workspace):
    """Regressao: achado real ao validar contra output/zz-teste-painel-view -
    '#ReuniaoDe15Minutos' nao pode virar tambem um candidato solto
    'numero_unidade' (15Minutos, sem espaco, nunca bate contra o dossie)."""
    _montar_projeto(
        workspace,
        "slug-h",
        "textos",
        dossie_texto="Apresente o programa em uma reuniao de 15 minutos.",
        arquivos_txt={"instagram.txt": "Confira! #ReuniaoDe15Minutos"},
    )

    relatorio = extrair.analisar("slug-h", "textos")

    unidades = [c for c in relatorio["candidatos"] if c["categoria"] == "numero_unidade"]
    assert unidades == []

    hashtags = [c for c in relatorio["candidatos"] if c["categoria"] == "hashtag"]
    assert hashtags[0]["trecho"] == "#ReuniaoDe15Minutos"
    assert hashtags[0]["encontrado_no_dossie"] is True


def test_pasta_do_material_ausente_levanta_erro(workspace):
    (workspace / "slug-f" / "insumos").mkdir(parents=True)
    (workspace / "slug-f" / "insumos" / "dossie_insumos.md").write_text("x", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        extrair.analisar("slug-f", "textos")


def test_dossie_ausente_levanta_erro(workspace):
    (workspace / "slug-g" / "textos").mkdir(parents=True)
    (workspace / "slug-g" / "textos" / "whatsapp.txt").write_text("x", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        extrair.analisar("slug-g", "textos")


def test_cli_end_to_end_com_pasta_de_saida_isolada(tmp_path):
    """Teste de integracao real via subprocess, com --pasta-saida isolada
    (nao precisa tocar output/ de verdade, mas exercita o script inteiro)."""
    slug_dir = REPO_ROOT / "output" / "zz-test-pytest-claims"
    try:
        (slug_dir / "textos").mkdir(parents=True)
        (slug_dir / "insumos").mkdir(parents=True)
        (slug_dir / "insumos" / "dossie_insumos.md").write_text(
            "Kit Teste Painel ajuda consultores.", encoding="utf-8"
        )
        (slug_dir / "textos" / "whatsapp.txt").write_text(
            "Confira o Kit Teste Painel! #NichoErrado", encoding="utf-8"
        )

        resultado = subprocess.run(
            [
                sys.executable,
                "scripts/extrair-claims-candidatos.py",
                "zz-test-pytest-claims",
                "textos",
                "--pasta-saida",
                str(tmp_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )

        assert resultado.returncode == 0
        assert "#NichoErrado" in resultado.stdout

        relatorio = json.loads((tmp_path / "candidatos_verificacao.json").read_text(encoding="utf-8"))
        hashtag = next(c for c in relatorio["candidatos"] if c["trecho"] == "#NichoErrado")
        assert hashtag["encontrado_no_dossie"] is False
    finally:
        shutil.rmtree(slug_dir, ignore_errors=True)
