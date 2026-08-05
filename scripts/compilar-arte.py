#!/usr/bin/env python3
"""
Compilador de Artes PNG (WhatsApp/Instagram/LinkedIn) via Playwright headless,
aplicando o design system fixo da Conexão.
"""

import argparse
import sys
import json
import re
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
DIR_FONTS = DIR_PROJETO / "templates" / "fonts"
DIR_LOGOS = DIR_PROJETO / "assets" / "logos-marca"

DIMENSOES = {
    "arte-01": (1080, 1080),
    "arte-02": (1080, 1350),
    "arte-03": (1080, 1920)
}


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


def compilar_variante_arte(slug, variante):
    """Renderiza as 3 copies compartilhadas (output/<slug>/arte/copies.json) na
    dimensao desta variante -- 1 render por copy, 3 PNGs no total. Formato
    (variante/dimensao) e copy (conceito criativo) sao eixos ortogonais: as
    mesmas 3 copies sao reaproveitadas em arte-01/02/03, nunca uma copy por
    formato (ver docs/05-plano-expansao-multi-copy-arte.md)."""
    largura, altura = DIMENSOES[variante]
    slug_dir = DIR_OUTPUT / slug
    copies_path = slug_dir / "arte" / "copies.json"

    template_path = DIR_PROJETO / "templates" / f"arte-{largura}x{altura}.html"
    dest_dir = slug_dir / variante
    dest_assets = dest_dir / "assets"

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

    # Garante estrutura de assets
    (dest_assets / "fonts").mkdir(parents=True, exist_ok=True)
    (dest_assets / "logos").mkdir(parents=True, exist_ok=True)

    # Copia fontes
    for f in DIR_FONTS.glob("*.woff2"):
        shutil.copy(f, dest_assets / "fonts" / f.name)

    # Copia logos
    for l in DIR_LOGOS.glob("*.png"):
        shutil.copy(l, dest_assets / "logos" / l.name)

    # Copia imagem do produto (path real vem de config_projeto.json, nunca
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

    # Injeta Badge de contexto (O badge USO INTERNO é suprimido ativamente e NUNCA mais utilizado!)
    brief = carregar_json(slug_dir / "brief_criativo.json")
    badge_texto = "USO INTERNO"
    if brief:
        nota = brief.get("nota_de_escopo", "").lower()
        if "externo" in nota or "profissional" in nota:
          badge_texto = "USO PROFISSIONAL"
    badge_tag = ""
    if badge_texto != "USO INTERNO":
        badge_tag = f'<span class="badge">{badge_texto}</span>'

    template_content = template_path.read_text(encoding="utf-8")
    erros = 0

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

            headline = formatar_markdown(copy.get("headline", ""))
            subcopy = formatar_markdown(copy.get("subcopy", ""))
            cta = formatar_markdown(copy.get("cta", "Fale com a Conexão"))

            html_final = template_content.replace(
                "{{TITULO}}", f"Arte {variante[-2:]} {sufixo_copy} - Conexão")

            logo_tag = '<img class="logo" src="assets/logos/Logo_Conexão_horizontal_texto_branco.png" alt="Conexão Implantes">'
            html_final = re.sub(r'<!--\s*\{\{LOGO\}\}.*?-->', logo_tag, html_final, flags=re.DOTALL)

            html_final = re.sub(r'<!--\s*\{\{BADGE_CONTEXTO\}\}.*?-->', badge_tag, html_final, flags=re.DOTALL)

            produto_tag = f'<img class="produto" src="assets/{img_produto_filename}" alt="Produto">'
            html_final = re.sub(r'<!--\s*\{\{IMAGEM_PRODUTO\}\}.*?-->', produto_tag, html_final, flags=re.DOTALL)

            html_final = re.sub(r'<!--\s*\{\{HEADLINE\}\}.*?-->', f'<h1>{headline}</h1>', html_final, flags=re.DOTALL)
            html_final = re.sub(r'<!--\s*\{\{SUBCOPY\}\}.*?-->', f'<p class="subcopy">{subcopy}</p>', html_final, flags=re.DOTALL)
            html_final = html_final.replace("{{NOME_MARCA}}", "Conexão Sistemas de Próteses")

            cta_tag = f'<span class="cta">{cta}</span>'
            html_final = re.sub(r'<!--\s*\{\{CTA\}\}.*?-->', cta_tag, html_final, flags=re.DOTALL)

            dest_html.write_text(html_final, encoding="utf-8")

            print(f"Renderizando {variante}/{sufixo_copy} em PNG ({largura}x{altura}px)...")
            page = None
            try:
                page = browser.new_page(viewport={"width": largura, "height": altura})
                page.goto(f"file:///{dest_html.resolve()}")
                page.wait_for_timeout(500)  # Aguarda transições e fontes
                page.screenshot(path=dest_png)
                print(f"[OK] {variante}/{sufixo_copy}: Arte PNG gerada em {dest_png}")
            except Exception as e:
                print(f"[FALHA] Falha ao renderizar {variante}/{sufixo_copy} via Playwright ({e})")
                dest_html.unlink(missing_ok=True)
                erros += 1
            finally:
                if page is not None:
                    page.close()

        browser.close()

    # index.html (copy01) e index_copyNN.html sao mantidos (nao temporarios)
    # para permitir auditoria de marca via validar-design-tokens.py/validar-logo.py,
    # que exigem o arquivo persistido no disco.
    return 1 if erros else 0


def main():
    ap = argparse.ArgumentParser(description="Compila dados de conteúdo JSON em peças de arte PNG pixel-perfect")
    ap.add_argument("slug")
    ap.add_argument("--variante", choices=["arte-01", "arte-02", "arte-03", "todas"], default="todas")
    args = ap.parse_args()

    variantes = ["arte-01", "arte-02", "arte-03"] if args.variante == "todas" else [args.variante]
    
    erros = 0
    for var in variantes:
        ret = compilar_variante_arte(args.slug, var)
        if ret != 0:
            erros += 1

    return 1 if erros > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
