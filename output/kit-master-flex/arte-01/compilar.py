#!/usr/bin/env python3
"""Render arte-01 (1080x1080) for kit-master-flex: 3 copies × 1 PNG each."""
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(DIR_PROJETO / "scripts"))

from _arte_common import (
    escolher_decoracao_fundo, gerar_forma_decorativa_html,
    preparar_assets, resolver_badge, preencher_template, renderizar_pagina,
    carregar_json
)

SLUG = "kit-master-flex"
VARIAENTE = "arte-01"
LARGURA, ALTURA = 1080, 1080

DIR_SLUG = DIR_PROJETO / "output" / SLUG
DIR_ARTE = DIR_SLUG / VARIAENTE
DIR_TEMPLATE = DIR_PROJETO / "templates"

# 1. Load template
template = (DIR_TEMPLATE / "arte-1080x1080.html").read_text(encoding="utf-8")

# 2. Load copies
copies = carregar_json(DIR_SLUG / "arte" / "copies.json")["copies"]
assert len(copies) == 3, f"Expected 3 copies, got {len(copies)}"

# 3. Prepare assets (fonts, logos, product image)
img_filename = preparar_assets(DIR_ARTE, DIR_SLUG)

# 4. Badge from brief
badge_tag = resolver_badge(DIR_SLUG)

# 5. Decorative elements (shared across 3 copies of same variant)
nome_forma, instancias = escolher_decoracao_fundo(f"{SLUG}:{VARIAENTE}")
forma_html = gerar_forma_decorativa_html(nome_forma, instancias)

# 6. Generate and render each copy
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    for idx, copy in enumerate(copies, start=1):
        html_filled = preencher_template(
            template,
            titulo=f"Kit MasterFlex — {copy['angulo']}",
            headline=copy["headline"],
            subcopy=copy["subcopy"],
            cta=copy["cta"],
            img_produto_filename=img_filename,
            badge_tag=badge_tag,
            forma_decorativa_html=forma_html,
        )

        suffix = f"_copy{idx:02d}" if idx > 1 else ""
        html_path = DIR_ARTE / f"index{suffix}.html"
        png_path = DIR_ARTE / f"arte_{SLUG}_01_copy{idx:02d}.png"

        html_path.write_text(html_filled, encoding="utf-8")
        print(f"[HTML] {html_path.name} written")

        ok = renderizar_pagina(browser, html_path, png_path, LARGURA, ALTURA,
                               f"{VARIAENTE}/copy-{idx:02d}")
        if not ok:
            print(f"[FALHA] copy-{idx:02d} render failed")
            browser.close()
            sys.exit(1)

    browser.close()

print(f"\n[OK] 3 PNGs gerados em {DIR_ARTE}/")
for f in sorted(DIR_ARTE.glob("*.png")):
    print(f"  {f.name}  ({f.stat().st_size / 1024:.0f} KB)")
