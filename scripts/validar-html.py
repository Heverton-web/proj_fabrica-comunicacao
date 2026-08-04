#!/usr/bin/env python3
"""
Valida R7 do SPEC.md / SPEC_HTML.md: o material HTML (landing-page ou
apresentacao) abre sem erro de console, sem asset quebrado e sem overflow
horizontal, em viewport desktop e mobile.

Uso:
    python scripts/validar-html.py <slug> <tipo>
    # tipo in: landing-page, apresentacao
"""

import argparse
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}


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


def main():
    ap = argparse.ArgumentParser(description="Valida um material HTML via Playwright headless")
    ap.add_argument("slug")
    ap.add_argument("tipo", choices=["landing-page", "apresentacao"])
    args = ap.parse_args()

    html_path = DIR_OUTPUT / args.slug / args.tipo / "index.html"
    if not html_path.exists():
        print(f"[ERRO] {html_path} nao encontrado")
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERRO] playwright nao instalado - rode: pip install playwright && playwright install chromium")
        return 1

    url = f"file:///{html_path.resolve().as_posix()}"
    todos_erros = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for nome, viewport in VIEWPORTS.items():
            erros = checar(browser, url, nome, viewport)
            todos_erros.extend(erros)
        browser.close()

    if todos_erros:
        print(f"[FALHA] {args.tipo}:")
        for e in todos_erros:
            print(f"  - {e}")
        return 1

    print(f"[OK] {args.tipo}: sem erro de console, sem asset quebrado, sem overflow horizontal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
