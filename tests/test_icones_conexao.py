import importlib.util
from pathlib import Path

import pytest

import _icones_conexao as icones

REPO_ROOT = Path(__file__).resolve().parent.parent


def _carregar_modulo(nome_modulo):
    """Carrega um script com hífen no nome (não importável via `import`)."""
    caminho = REPO_ROOT / "scripts" / f"{nome_modulo}.py"
    spec = importlib.util.spec_from_file_location(nome_modulo, caminho)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"nao foi possivel carregar scripts/{nome_modulo}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


VOCABULARIO_ESPERADO = {
    "problema",
    "solucao",
    "dado_tecnico",
    "evidencia",
    "processo",
    "checklist",
    "tempo",
    "contato",
}


def test_vocabulario_eh_fechado_e_imutavel():
    assert set(icones.CATEGORIAS_ICONES) == VOCABULARIO_ESPERADO
    assert len(icones.CATEGORIAS_ICONES) == 8


@pytest.mark.parametrize("categoria", sorted(VOCABULARIO_ESPERADO))
def test_id_simbolo_segue_convencao_icone(categoria):
    assert icones.id_simbolo(categoria) == f"icone-{categoria}"


@pytest.mark.parametrize("categoria", ["nao-existe", "", "CUSTOM", "emoji ✨"])
def test_id_simbolo_rejeita_fora_do_vocabulario(categoria):
    assert icones.id_simbolo(categoria) is None


@pytest.mark.parametrize("categoria", sorted(VOCABULARIO_ESPERADO))
def test_html_icone_referencia_sprite(categoria):
    html = icones.html_icone(categoria)
    assert html
    assert f'href="#icone-{categoria}"' in html
    assert 'class="icone"' in html
    assert 'aria-hidden="true"' in html


def test_html_icone_vazio_fora_do_vocabulario():
    assert icones.html_icone("nao-existe") == ""


def test_renderizar_cards_destaque_com_dict_item():
    compilar = _carregar_modulo("compilar-html")
    html = compilar.renderizar_cards_destaque(
        [{"texto": "**Fratura** — Redução da dor", "categoria": "problema"}]
    )
    assert 'data-categoria="problema"' in html
    assert 'href="#icone-problema"' in html
    assert "<h4>Fratura</h4>" in html


def test_renderizar_cards_destaque_com_categoria_padrao_do_slide():
    compilar = _carregar_modulo("compilar-html")
    html = compilar.renderizar_cards_destaque(
        ["**Evidência** — Estudo clínico randomizado"], categoria_padrao="evidencia"
    )
    assert 'data-categoria="evidencia"' in html
    assert 'href="#icone-evidencia"' in html


def test_renderizar_cards_destaque_item_dict_sobrescreve_slide():
    compilar = _carregar_modulo("compilar-html")
    html = compilar.renderizar_cards_destaque(
        [{"texto": "**Contato** — Fale com um consultor", "categoria": "contato"}],
        categoria_padrao="problema",
    )
    assert 'data-categoria="contato"' in html
    assert 'href="#icone-contato"' in html


def test_renderizar_cards_destaque_categoria_desconhecida_mantem_data_sem_icone():
    compilar = _carregar_modulo("compilar-html")
    html = compilar.renderizar_cards_destaque(
        [{"texto": "**X** — Sem categoria válida", "categoria": "nao-existe"}]
    )
    assert 'data-categoria="nao-existe"' in html
    assert 'class="icone"' not in html


def test_renderizar_cards_destaque_string_legada_sem_categoria():
    compilar = _carregar_modulo("compilar-html")
    html = compilar.renderizar_cards_destaque(["**A** — Item legado"])
    assert "data-categoria" not in html
    assert 'class="icone"' not in html


def test_emoji_re_pega_emoji_mas_nao_setas_de_texto():
    validar = _carregar_modulo("validar-html")
    assert validar.EMOJI_RE.search("🖥️")       # computador (U+1F5A5 + U+FE0F)
    assert validar.EMOJI_RE.search("✍️")        # mão escrevendo (U+270D + U+FE0F)
    assert validar.EMOJI_RE.search("📱")        # celular
    assert not validar.EMOJI_RE.search("← →")   # setas de texto (U+2190/U+2192)
    assert not validar.EMOJI_RE.search("100% + seguros")
