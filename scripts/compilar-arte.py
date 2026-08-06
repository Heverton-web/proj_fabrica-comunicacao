#!/usr/bin/env python3
"""
Compilador de Artes PNG (WhatsApp/Instagram/LinkedIn) via Playwright headless,
aplicando o design system fixo da Conexão. Reaproveita a tecnica de
renderizacao compartilhada em scripts/_arte_common.py (mesmo helper usado
por compilar-kit.py).
"""

import argparse
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _arte_common import (
    DIR_OUTPUT, DIR_PROJETO, carregar_json, preparar_assets, resolver_badge,
    preencher_template, renderizar_pagina, escolher_decoracao_fundo,
    gerar_forma_decorativa_html,
)

DIMENSOES = {
    "arte-01": (1080, 1080),
    "arte-02": (1080, 1350),
    "arte-03": (1080, 1920)
}


def compilar_variante_arte(slug, variante, pasta=None):
    """Renderiza as 3 copies compartilhadas (output/<slug>/arte/copies.json) na
    dimensao desta variante -- 1 render por copy, 3 PNGs no total. Formato
    (variante/dimensao) e copy (conceito criativo) sao eixos ortogonais: as
    mesmas 3 copies sao reaproveitadas em arte-01/02/03, nunca uma copy por
    formato (ver docs/05-plano-expansao-multi-copy-arte.md).

    `pasta` e a pasta real de destino em output/<slug>/ -- normalmente igual a
    `variante`, mas pode ser uma versao regenerada (ex.: "arte-01-v2") por
    /gerar-arte-1080x1080 -- ver REGRA 11 do AGENTS.md. `variante` continua
    sendo a variante BASE (define dimensao e nome de arquivo)."""
    pasta = pasta or variante
    largura, altura = DIMENSOES[variante]
    slug_dir = DIR_OUTPUT / slug
    copies_path = slug_dir / "arte" / "copies.json"

    template_path = DIR_PROJETO / "templates" / f"arte-{largura}x{altura}.html"
    dest_dir = slug_dir / pasta

    if not copies_path.exists():
        print(f"[ERRO] {copies_path} nao encontrado -- redator-arte deve gerar as "
              f"3 copies compartilhadas ANTES de compilar qualquer formato de arte")
        return 1

    if not template_path.exists():
        print(f"[ERRO] template nao encontrado: {template_path}")
        return 1

    dados_copies = carregar_json(copies_path)
    if not isinstance(dados_copies, dict):
        print(f"[ERRO] {copies_path} nao contem um objeto JSON valido")
        return 1
    copies = dados_copies.get("copies", [])
    if len(copies) != 3:
        print(f"[ERRO] {copies_path} deve conter exatamente 3 copies, encontrado {len(copies)}")
        return 1

    img_produto_filename = preparar_assets(dest_dir, slug_dir)
    badge_tag = resolver_badge(slug_dir)
    template_content = template_path.read_text(encoding="utf-8")
    erros = 0

    # Elementos decorativos de fundo sao opt-out via config_projeto.elementos_decorativos
    # (Passo 5 do /esbocar) -- default True se o campo nao existir (REGRA 3).
    config_projeto = carregar_json(slug_dir / "config_projeto.json")
    decorativos_ativos = (config_projeto or {}).get("elementos_decorativos", True)

    forma_html = ""
    if decorativos_ativos:
        # 1 tipo de forma/wave decorativa por bloco -- aqui o bloco e o FORMATO
        # (as 3 copies de arte-01, por exemplo, compartilham a mesma forma/posicao;
        # arte-02 e arte-03 tendem a sortear forma E posicionamento diferentes).
        forma_nome, instancias = escolher_decoracao_fundo(f"{slug}:arte:{variante}")
        forma_html = gerar_forma_decorativa_html(forma_nome, instancias)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for indice, copy in enumerate(copies, start=1):
            sufixo_copy = f"copy{indice:02d}"
            dest_html = dest_dir / ("index.html" if indice == 1 else f"index_{sufixo_copy}.html")
            dest_png = dest_dir / f"arte_{slug}_{variante[-2:]}_{sufixo_copy}.png"

            if not isinstance(copy, dict):
                print(f"[ERRO] {variante}/{sufixo_copy}: copy invalida em {copies_path} "
                      f"(esperado objeto, encontrado {type(copy).__name__})")
                erros += 1
                continue

            html_final = preencher_template(
                template_content,
                titulo=f"Arte {variante[-2:]} {sufixo_copy} - Conexão",
                headline=copy.get("headline", ""),
                subcopy=copy.get("subcopy", ""),
                cta=copy.get("cta", "Fale com a Conexão"),
                img_produto_filename=img_produto_filename,
                badge_tag=badge_tag,
                forma_decorativa_html=forma_html,
            )
            dest_html.write_text(html_final, encoding="utf-8")

            print(f"Renderizando {variante}/{sufixo_copy} em PNG ({largura}x{altura}px)...")
            if not renderizar_pagina(browser, dest_html, dest_png, largura, altura,
                                      rotulo=f"{variante}/{sufixo_copy}"):
                erros += 1

        browser.close()

    # index.html (copy01) e index_copyNN.html sao mantidos (nao temporarios)
    # para permitir auditoria de marca via validar-design-tokens.py/validar-logo.py,
    # que exigem o arquivo persistido no disco.
    return 1 if erros else 0


def main():
    ap = argparse.ArgumentParser(description="Compila dados de conteúdo JSON em peças de arte PNG pixel-perfect")
    ap.add_argument("slug")
    ap.add_argument("--variante", choices=["arte-01", "arte-02", "arte-03", "todas"], default="todas")
    ap.add_argument("--pasta", default=None,
                     help="pasta de destino em output/<slug>/ (default: a propria "
                          "--variante; use '<variante>-v2', '-v3'... para regeneracoes "
                          "que nao devem sobrescrever a versao anterior - ver REGRA 11 "
                          "do AGENTS.md). So valido com --variante != 'todas'.")
    args = ap.parse_args()

    if args.pasta and args.variante == "todas":
        print("[ERRO] --pasta so pode ser usado com uma unica --variante (nunca com 'todas')")
        return 1

    variantes = ["arte-01", "arte-02", "arte-03"] if args.variante == "todas" else [args.variante]

    erros = 0
    for var in variantes:
        ret = compilar_variante_arte(args.slug, var, args.pasta)
        if ret != 0:
            erros += 1

    return 1 if erros > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
