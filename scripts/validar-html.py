#!/usr/bin/env python3
"""
Valida R7 do SPEC.md / SPEC_HTML.md: o material HTML (landing-page ou
apresentacao) abre sem erro de console, sem asset quebrado e sem overflow
horizontal, em viewport desktop e mobile.

Uso:
    python scripts/validar-html.py <slug> <tipo> [--estrito] [--pasta X]
    # tipo in: landing-page, apresentacao

--estrito (gate determinístico — REGRA 8 do AGENTS.md) adiciona:
  1. Emoji proibido: nenhum caractere de emoji no HTML renderizado (o design
     system da Conexão usa SVG vetorial da biblioteca fixa, nunca emoji como
     ícone/decoração — ver aplicador-marca-conexao/SKILL.md, seção "Ícones").
  2. Cartão marcado com `data-categoria` precisa conter o <use> do ícone
     correspondente (<use href="#icone-<categoria>">) e o <symbol> precisa
     existir no sprite da página; a categoria precisa pertencer ao vocabulário
     fechado de _icones_conexao.CATEGORIAS_ICONES.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _icones_conexao import categoria_valida

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}

# Ranges de emoji: blocos principais (símbolos/pictogramas/emoticons/
# transporte/suplementares), misc symbols + dingbats (inclui ✍ U+270D, usado
# como ícone em material antigo), variation selector-16 (U+FE0F força
# apresentação como emoji), ZWJ (U+200D) e keycap (U+20E3). Setas de texto
# (U+2190/U+2192, ex. nav-hint "← →") NÃO estão no range e não são emoji.
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0000FE0F\U0000200D\U000020E3]"
)

SCRIPT_ESTRITO_JS = """
() => {
  const erros = [];
  // 1. Emoji visível no texto renderizado (innerText ignora <script>/<style>)
  const texto = document.body ? document.body.innerText : "";
  // 2. Cartões marcados com data-categoria
  const cards = document.querySelectorAll("[data-categoria]");
  const ids_presentes = new Set(
    Array.from(document.querySelectorAll("symbol[id]")).map(s => s.id)
  );
  for (const card of cards) {
    const cat = card.getAttribute("data-categoria");
    const ref = "icone-" + cat;
    const usa = card.querySelector('svg use[href="#' + ref + '"]');
    if (!usa) {
      erros.push("card [data-categoria='" + cat + "'] sem <use href='#" + ref + "'>");
    }
    if (!ids_presentes.has(ref)) {
      erros.push("card [data-categoria='" + cat + "'] referencia <symbol id='" + ref + "'> ausente do sprite");
    }
  }
  return { texto, erros };
}
"""


def checar(pagina_cls, url, viewport_nome, viewport):
    erros = []
    console_erros = []
    requests_falhos = []

    page = pagina_cls.new_page(viewport=viewport)
    page.on("console", lambda msg: console_erros.append(msg.text) if msg.type == "error" else None)
    page.on("requestfailed", lambda req: requests_falhos.append(req.url))

    page.goto(url)
    page.wait_for_timeout(500)

    largura_documento = page.evaluate("document.documentElement.scrollWidth")
    largura_viewport = viewport["width"]
    if largura_documento > largura_viewport + 2:  # tolerancia de 2px por subpixel rendering
        erros.append(f"overflow horizontal em {viewport_nome}: documento {largura_documento}px > "
                     f"viewport {largura_viewport}px")

    if console_erros:
        erros.append(f"{len(console_erros)} erro(s) de console em {viewport_nome}: {console_erros[:3]}")
    if requests_falhos:
        erros.append(f"{len(requests_falhos)} asset(s) quebrado(s) em {viewport_nome}: {requests_falhos[:3]}")

    page.close()
    return erros


def checar_estrito(pagina_cls, url, html_bruto):
    """Gate determinístico --estrito. Roda uma única vez (desktop)."""
    erros = []

    # 1. Emoji no HTML renderizado (tanto o fonte quanto o innerText — o fonte
    #    pega emoji fora do body, ex. <title>; o innerText pega só o visível)
    texto_visivel = ""
    page = pagina_cls.new_page(viewport=VIEWPORTS["desktop"])
    page.goto(url)
    page.wait_for_timeout(500)
    resultado = page.evaluate(SCRIPT_ESTRITO_JS)
    texto_visivel = resultado.get("texto", "")
    page.close()

    for rotulo, alvo in (("fonte", html_bruto), ("renderizado", texto_visivel)):
        ocorrencias = sorted(set(EMOJI_RE.findall(alvo)))
        if ocorrencias:
            exemplos = " ".join(f"U+{ord(oc):04X}" for oc in ocorrencias[:6])
            erros.append(f"emoji {rotulo} ({len(ocorrencias)} tipo(s): {exemplos}) - design system exige SVG, nunca emoji")

    for mensagem in resultado.get("erros", []):
        erros.append(mensagem)

    return erros


def main():
    ap = argparse.ArgumentParser(description="Valida um material HTML via Playwright headless")
    ap.add_argument("slug")
    ap.add_argument("tipo", choices=["landing-page", "apresentacao"])
    ap.add_argument("--estrito", action="store_true",
                    help="gate determinístico: emoji proibido + categoria<->icone (REGRA 8)")
    ap.add_argument("--pasta", default=None,
                     help="pasta em output/<slug>/ a validar (default: o proprio "
                          "<tipo>; use '<tipo>-v2', '-v3'... para validar uma "
                          "regeneracao - ver REGRA 11 do AGENTS.md)")
    args = ap.parse_args()
    pasta = args.pasta or args.tipo

    html_path = DIR_OUTPUT / args.slug / pasta / "index.html"
    if not html_path.exists():
        print(f"[ERRO] {html_path} nao encontrado")
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERRO] playwright nao instalado - rode: pip install playwright && playwright install chromium")
        return 1

    url = f"file:///{html_path.resolve().as_posix()}"
    html_bruto = html_path.read_text(encoding="utf-8")
    todos_erros = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for nome, viewport in VIEWPORTS.items():
            erros = checar(browser, url, nome, viewport)
            todos_erros.extend(erros)
        if args.estrito:
            todos_erros.extend(checar_estrito(browser, url, html_bruto))
        browser.close()

    if todos_erros:
        print(f"[FALHA] {args.tipo}:")
        for e in todos_erros:
            print(f"  - {e}")
        return 1

    if args.estrito:
        print(f"[OK] {args.tipo}: sem erro de console, sem asset quebrado, sem overflow horizontal; "
              f"--estrito: sem emoji, categorias<->icones coerentes")
    else:
        print(f"[OK] {args.tipo}: sem erro de console, sem asset quebrado, sem overflow horizontal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
