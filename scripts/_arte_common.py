#!/usr/bin/env python3
"""
Helper compartilhado entre compilar-arte.py e compilar-kit.py: carregamento
de JSON, formatacao de markdown, copia de assets (fontes/logo/produto),
preenchimento de template de arte e render Playwright pixel-perfect.

Extraido para nao duplicar a tecnica de renderizacao entre os dois
compiladores -- ver docs/06-plano-expansao-kits-consultor-distribuidor.md,
secao 12 (risco de duplicar a mesma logica/bug em 2 arquivos).

Nao e um script standalone -- so exporta funcoes, sem bloco __main__.
"""

import json
import random
import re
import shutil
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
DIR_FONTS = DIR_PROJETO / "templates" / "fonts"
DIR_LOGOS = DIR_PROJETO / "assets" / "logos-marca"

LOGO_HORIZONTAL_BRANCO = "Logo_Conexão_horizontal_texto_branco.png"
NOME_MARCA = "Conexão Sistemas de Próteses"

# Catálogo de elementos geométricos decorativos de fundo (bordas finas douradas,
# sem preenchimento) para enriquecer o background das artes com profundidade.
# 1 tipo por "bloco" de artes (ex.: as 2 artes de um tom de kit, ou as 3 copies de
# 1 formato) -- ver escolher_forma_decorativa().
FORMAS_DECORATIVAS = {
    "quadrado": {
        "viewbox": "0 0 100 100",
        "conteudo": '<rect x="14" y="14" width="72" height="72" transform="rotate(12 50 50)" fill="none" stroke="var(--accent)" stroke-width="0.35"/>',
    },
    "circulo": {
        "viewbox": "0 0 100 100",
        "conteudo": '<circle cx="50" cy="50" r="42" fill="none" stroke="var(--accent)" stroke-width="0.35"/>',
    },
    "triangulo": {
        "viewbox": "0 0 100 100",
        "conteudo": '<polygon points="50,6 93,88 7,88" fill="none" stroke="var(--accent)" stroke-width="0.35"/>',
    },
    "hexagono": {
        "viewbox": "0 0 100 100",
        "conteudo": '<polygon points="50,4 91,27 91,73 50,96 9,73 9,27" fill="none" stroke="var(--accent)" stroke-width="0.35"/>',
    },
    "wave": {
        "viewbox": "0 0 200 60",
        "conteudo": '<path d="M0,32 C 25,6 45,58 70,32 C 95,6 115,58 140,32 C 160,14 180,44 200,30" fill="none" stroke="var(--accent)" stroke-width="0.4"/>',
    },
}


# 4 orientações diagonais possíveis para as 2 instâncias de 1 bloco -- garante que
# as 2 formas nunca fiquem no mesmo canto, mas o CANTO usado varia por bloco (evita
# a fadiga visual de "sempre no mesmo lugar").
_DIAGONAIS = [
    ("top", "left", "bottom", "right"),
    ("top", "right", "bottom", "left"),
    ("bottom", "left", "top", "right"),
    ("bottom", "right", "top", "left"),
]


def escolher_decoracao_fundo(chave_semente):
    """Escolhe deterministicamente, para 1 'bloco' de artes: 1 tipo de forma/wave,
    a diagonal de cantos das 2 instâncias e uma variação de tamanho/deslocamento/
    opacidade em cada uma -- mesma chave sempre resulta na mesma decoração
    (recompilar não muda o visual); chaves diferentes (blocos diferentes) tendem a
    sortear combinações visuais diferentes, tanto de forma quanto de posição/tamanho,
    para não repetir sempre o mesmo padrão. Retorna (nome_forma, [instancia1, instancia2]),
    cada instância com vert/horiz (ex.: "top"/"left"), tamanho e deslocamento em px,
    e opacidade -- sempre no fundo (a marcação HTML resultante fica atrás de
    logo/produto/texto, nunca sobre eles) e sempre sangrando por um canto (nunca
    centralizado sobre o conteúdo)."""
    rng = random.Random(chave_semente)
    nome_forma = rng.choice(list(FORMAS_DECORATIVAS))
    v1, h1, v2, h2 = rng.choice(_DIAGONAIS)

    instancias = []
    for vert, horiz, tamanho_base, opacidade_base in (
        (v1, h1, 500, 0.10),
        (v2, h2, 380, 0.13),
    ):
        tamanho = round(tamanho_base + rng.uniform(-70, 70))
        deslocamento = round(-tamanho * 0.22 + rng.uniform(-20, 20))
        opacidade = round(min(0.15, max(0.06, opacidade_base + rng.uniform(-0.02, 0.02))), 3)
        instancias.append({
            "vert": vert, "horiz": horiz, "tamanho": tamanho,
            "deslocamento": deslocamento, "opacidade": opacidade,
        })

    return nome_forma, instancias


def gerar_forma_decorativa_html(nome_forma, instancias):
    """Gera as instâncias da forma escolhida, cada uma com posição/tamanho/opacidade
    próprios (inline style), sempre atrás do conteúdo (ver CSS .forma-decorativa nos
    templates: position absolute + z-index abaixo de logo/bloco-conteudo/barras)."""
    forma = FORMAS_DECORATIVAS[nome_forma]
    partes = []
    for inst in instancias:
        estilo = (
            f'{inst["vert"]}: {inst["deslocamento"]}px; '
            f'{inst["horiz"]}: {inst["deslocamento"]}px; '
            f'width: {inst["tamanho"]}px; height: {inst["tamanho"]}px; '
            f'opacity: {inst["opacidade"]};'
        )
        partes.append(
            f'<svg class="forma-decorativa" style="{estilo}" viewBox="{forma["viewbox"]}" '
            f'preserveAspectRatio="xMidYMid meet">{forma["conteudo"]}</svg>'
        )
    return "".join(partes)


def carregar_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except Exception:
        return None


def formatar_markdown(texto):
    if not isinstance(texto, str):
        return texto
    # Substitui **texto** por <strong>texto</strong>
    texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
    # Substitui *texto* por <em>texto</em>
    texto = re.sub(r'\*(.*?)\*', r'<em>\1</em>', texto)
    return texto


def preparar_assets(dest_dir, slug_dir):
    """Cria dest_dir/assets/{fonts,logos}/, copia fontes+logos fixos e a
    imagem do produto de config_projeto.json. Retorna o filename da imagem
    do produto copiada, para uso em {{IMAGEM_PRODUTO}}."""
    dest_assets = dest_dir / "assets"
    (dest_assets / "fonts").mkdir(parents=True, exist_ok=True)
    (dest_assets / "logos").mkdir(parents=True, exist_ok=True)

    for f in DIR_FONTS.glob("*.woff2"):
        shutil.copy(f, dest_assets / "fonts" / f.name)
    for l in DIR_LOGOS.glob("*.png"):
        shutil.copy(l, dest_assets / "logos" / l.name)

    # Imagem do produto (path real vem de config_projeto.json, nunca
    # hardcoded — cada projeto tem seu próprio nome/local de imagem)
    img_produto_filename = "kit_start_flex_frontal.png"  # fallback histórico
    config_para_imagem = carregar_json(slug_dir / "config_projeto.json")
    if config_para_imagem and config_para_imagem.get("imagens"):
        primeira_imagem = config_para_imagem["imagens"][0].get("path", "")
        if primeira_imagem:
            img_produto_src = DIR_PROJETO / primeira_imagem
            if img_produto_src.exists():
                img_produto_filename = img_produto_src.name
                shutil.copy(img_produto_src, dest_assets / img_produto_filename)
    else:
        img_produto_src_legado = slug_dir / "insumos" / "kit_start_flex_frontal.png"
        if img_produto_src_legado.exists():
            shutil.copy(img_produto_src_legado, dest_assets / "kit_start_flex_frontal.png")

    return img_produto_filename


def resolver_badge(slug_dir):
    """REGRa 1 BADGE POR PECA (rodada de endurecimento): em pecas PNG (arte-* e
    kits) o CTA pill e o UNICO elemento tipo badge -- o badge de contexto
    (USO INTERNO/USO PROFISSIONAL) e sempre suprimido aqui (string vazia).
    Badge de contexto so existe em material HTML vivo (landing/apresentacao,
    no cabecalho) via compilar-html.py. Mantido o placeholder nos templates
    para permitir retorno futuro sem quebrar o pipeline."""
    return ""


def checar_um_badge_por_peca(base_dir, rotulo):
    """REGRA 1 BADGE POR PECA: cada peca PNG deve ter exatamente 1 elemento
    tipo badge -- o CTA pill -- e nenhum badge de contexto no HTML persistido
    (index*.html renderizado). Retorna (ok, mensagens)."""
    import re as _re

    mensagens = []
    ok = True
    base = Path(base_dir)
    htmls = sorted(base.rglob("index*.html"))
    if not htmls:
        mensagens.append(f"[AVISO] {rotulo}: nenhum index*.html encontrado - pulando checagem de badge")
        return True, mensagens
    for html in htmls:
        conteudo = html.read_text(encoding="utf-8", errors="ignore")
        badges = _re.findall(r'class="badge"', conteudo)
        ctas = _re.findall(r'class="cta"', conteudo)
        if badges:
            ok = False
            mensagens.append(f"[FALHA] {rotulo}/{html.name}: {len(badges)} badge(s) de contexto (esperado 0)")
        if len(ctas) != 1:
            ok = False
            mensagens.append(f"[FALHA] {rotulo}/{html.name}: {len(ctas)} CTA pill(s) (esperado exatamente 1)")
    if ok:
        mensagens.append(f"[OK] {rotulo}: 1 badge por peca (somente o CTA pill, 0 badges de contexto)")
    return ok, mensagens


def _titulo_com_palavras(headline):
    """Divide o headline em palavras, cada uma envolvida em <span class="palavra">
    -- usado pelo script de ajuste embutido nos templates de arte para medir linhas
    renderizadas no navegador e garantir no maximo 2 linhas, nunca uma linha com 1
    unica palavra. Markdown e formatado POR PALAVRA (nao no headline inteiro antes de
    dividir) para nunca quebrar uma tag <strong>/<em> entre dois spans -- visualmente
    identico a formatar o headline inteiro, já que negrito/italico por palavra
    isolada renderiza igual a um span continuo."""
    palavras = [p for p in headline.split(" ") if p]
    return " ".join(f'<span class="palavra">{formatar_markdown(p)}</span>' for p in palavras)


def preencher_template(template_content, *, titulo, headline, subcopy, cta,
                        img_produto_filename, badge_tag, forma_decorativa_html=""):
    """Substitui os placeholders {{...}} do template de arte fixo (logo,
    badge, imagem do produto, headline, subcopy, cta, nome da marca, forma
    decorativa de fundo) e retorna o HTML final pronto para screenshot."""
    html_final = template_content.replace("{{TITULO}}", titulo)

    html_final = re.sub(r'<!--\s*\{\{FORMA_DECORATIVA\}\}.*?-->',
                         forma_decorativa_html, html_final, flags=re.DOTALL)

    logo_tag = f'<img class="logo" src="assets/logos/{LOGO_HORIZONTAL_BRANCO}" alt="Conexão Implantes">'
    html_final = re.sub(r'<!--\s*\{\{LOGO\}\}.*?-->', logo_tag, html_final, flags=re.DOTALL)

    html_final = re.sub(r'<!--\s*\{\{BADGE_CONTEXTO\}\}.*?-->', badge_tag, html_final, flags=re.DOTALL)

    produto_tag = f'<img class="produto" src="assets/{img_produto_filename}" alt="Produto">'
    html_final = re.sub(r'<!--\s*\{\{IMAGEM_PRODUTO\}\}.*?-->', produto_tag, html_final, flags=re.DOTALL)

    html_final = re.sub(r'<!--\s*\{\{HEADLINE\}\}.*?-->',
                         f'<h1>{_titulo_com_palavras(headline)}</h1>', html_final, flags=re.DOTALL)
    html_final = re.sub(r'<!--\s*\{\{SUBCOPY\}\}.*?-->',
                         f'<p class="subcopy">{formatar_markdown(subcopy)}</p>', html_final, flags=re.DOTALL)
    html_final = html_final.replace("{{NOME_MARCA}}", NOME_MARCA)

    cta_tag = f'<span class="cta">{formatar_markdown(cta)}</span>'
    html_final = re.sub(r'<!--\s*\{\{CTA\}\}.*?-->', cta_tag, html_final, flags=re.DOTALL)

    return html_final


def renderizar_pagina(browser, dest_html, dest_png, largura, altura, rotulo):
    """Renderiza 1 pagina HTML->PNG pixel-perfect via Playwright, usando um
    browser ja lancado (reaproveitado entre varios renders pelo chamador,
    nunca 1 browser por render -- custoso). Retorna True em sucesso, False
    em falha (e apaga dest_html na falha, para nao deixar HTML orfao)."""
    page = None
    try:
        page = browser.new_page(viewport={"width": largura, "height": altura})
        page.goto(f"file:///{dest_html.resolve()}")
        page.wait_for_timeout(500)  # Aguarda transições e fontes
        page.screenshot(path=dest_png)
        print(f"[OK] {rotulo}: Arte PNG gerada em {dest_png}")
        return True
    except Exception as e:
        print(f"[FALHA] Falha ao renderizar {rotulo} via Playwright ({e})")
        dest_html.unlink(missing_ok=True)
        return False
    finally:
        if page is not None:
            page.close()
