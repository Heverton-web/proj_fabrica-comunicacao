#!/usr/bin/env python3
"""Exemplo de aplicacao do eixo LAYOUT (docs/11-plano-expansao-variacao-layout-arte.md).

Reusa o helper REAL do pipeline (scripts/_arte_common.py — mesmo preencher_template/
renderizar_pagina/preparar_assets usados por compilar-arte.py e compilar-kit.py) para
renderizar 3 copies com 3 layouts diferentes na dimensao 1080x1350.

NAO toca output/<slug>/ (REGRA 11 do AGENTS.md): le o projeto kit-master-flex-02
somente como fonte de insumo (copies em exemplos/expansao-layout/copies.json e a
imagem do produto via config_projeto.json), e escreve apenas em exemplos/expansao-layout/.

Uso:
    python exemplos/expansao-layout/gerar-exemplo-layout.py
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

DIR_RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DIR_RAIZ / "scripts"))

from _arte_common import (  # noqa: E402
    DIR_PROJETO, carregar_json, preparar_assets, resolver_badge,
    preencher_template, renderizar_pagina, escolher_decoracao_fundo,
    gerar_forma_decorativa_html, checar_um_badge_por_peca,
)

BASE = Path(__file__).resolve().parent
DEST = BASE / "saida"
SLUG = "kit-master-flex-02"
SLUG_DIR = DIR_PROJETO / "output" / SLUG
LARGURA, ALTURA = 1080, 1350
TETO_BYTES = 1_000_000

# Layouts aplicaveis a 1080x1350 nesta prova de conceito (docs/11, secao 2).
LAYOUTS_1350 = {"layout-01", "layout-02", "layout-03"}


def main():
    dados_copies = carregar_json(BASE / "copies.json")
    copies = dados_copies.get("copies", [])
    if len(copies) != 3:
        print(f"[ERRO] copies.json deve ter exatamente 3 copies, encontrado {len(copies)}")
        return 1

    # Gate do eixo novo: toda copy declara layout valido para a dimensao
    for copy in copies:
        layout = copy.get("layout")
        if layout not in LAYOUTS_1350:
            print(f"[ERRO] copy {copy.get('id')}: layout {layout!r} invalido para 1080x1350 "
                  f"(aplicaveis: {sorted(LAYOUTS_1350)})")
            return 1

    img_produto_filename = preparar_assets(DEST, SLUG_DIR)
    badge_tag = resolver_badge(SLUG_DIR)
    config_projeto = carregar_json(SLUG_DIR / "config_projeto.json")
    decorativos_ativos = (config_projeto or {}).get("elementos_decorativos", True)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for indice, copy in enumerate(copies, start=1):
            layout = copy["layout"]
            template_path = BASE / "templates" / f"arte-1080x1350-{layout}.html"
            if not template_path.exists():
                print(f"[ERRO] template nao encontrado: {template_path}")
                return 1

            # 1 combinacao decorativa por bloco: aqui o bloco e layout (as copies que
            # compartilham o mesmo layout compartilhariam a mesma forma; no exemplo
            # cada copy tem layout proprio, entao a semente inclui o layout).
            forma_html = ""
            if decorativos_ativos:
                forma_nome, instancias = escolher_decoracao_fundo(
                    f"{SLUG}:arte:arte-02:{layout}")
                forma_html = gerar_forma_decorativa_html(forma_nome, instancias)

            sufixo_copy = f"copy{indice:02d}"
            dest_html = DEST / ("index.html" if indice == 1 else f"index_{sufixo_copy}.html")
            dest_png = DEST / f"arte_{SLUG}_02_{sufixo_copy}_{layout}.png"

            html_final = preencher_template(
                template_path.read_text(encoding="utf-8"),
                titulo=f"Exemplo {layout} {sufixo_copy} - Conexão",
                headline=copy.get("headline", ""),
                subcopy=copy.get("subcopy", ""),
                cta=copy.get("cta", "Fale com a Conexão"),
                img_produto_filename=img_produto_filename,
                badge_tag=badge_tag,
                forma_decorativa_html=forma_html,
            )
            dest_html.write_text(html_final, encoding="utf-8")

            if not renderizar_pagina(browser, dest_html, dest_png, LARGURA, ALTURA,
                                     rotulo=f"exemplo/{sufixo_copy}/{layout}"):
                return 1

        browser.close()

    # Gate deterministico do exemplo (REGRA 8): dimensao exata, peso, 1 badge por peca
    from PIL import Image

    ok = True
    for png in sorted(DEST.glob("*.png")):
        tamanho_bytes = png.stat().st_size
        with Image.open(png) as im:
            largura, altura = im.size
        if (largura, altura) != (LARGURA, ALTURA):
            print(f"[FALHA] {png.name}: dimensao {largura}x{altura}, esperado {LARGURA}x{ALTURA}")
            ok = False
        if tamanho_bytes >= TETO_BYTES:
            print(f"[FALHA] {png.name}: {tamanho_bytes} bytes, teto {TETO_BYTES}")
            ok = False
        if (largura, altura) == (LARGURA, ALTURA) and tamanho_bytes < TETO_BYTES:
            print(f"[OK] {png.name}: {largura}x{altura}, {tamanho_bytes} bytes")

    ok_badges, mensagens = checar_um_badge_por_peca(DEST, "exemplo-layout")
    for msg in mensagens:
        print(msg)
    if not ok_badges:
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
