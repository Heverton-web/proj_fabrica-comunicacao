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
    largura, altura = DIMENSOES[variante]
    slug_dir = DIR_OUTPUT / slug
    conteudo_path = slug_dir / variante / "conteudo.json"
    
    # Template name
    template_path = DIR_PROJETO / "templates" / f"arte-{largura}x{altura}.html"
    dest_html = slug_dir / variante / "temp_arte.html"
    dest_png = slug_dir / variante / f"arte_{slug}_{variante[-2:]}.png"
    dest_assets = slug_dir / variante / "assets"

    if not conteudo_path.exists():
        print(f"[ERRO] conteudo.json não encontrado para {variante} em {conteudo_path}")
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

    # Copia imagem do produto se existir
    img_produto_src = slug_dir / "insumos" / "kit_start_flex_frontal.png"
    if img_produto_src.exists():
        shutil.copy(img_produto_src, dest_assets / "kit_start_flex_frontal.png")

    # Carrega dados
    dados = carregar_json(conteudo_path)
    if not dados:
        print(f"[ERRO] Não foi possível carregar o arquivo {conteudo_path}")
        return 1

    headline = formatar_markdown(dados.get("headline", ""))
    subcopy = formatar_markdown(dados.get("subcopy", ""))
    cta = formatar_markdown(dados.get("cta", "Fale com a Conexão"))

    # Carrega template e substitui
    template_content = template_path.read_text(encoding="utf-8")
    
    # Substituições
    html_final = template_content.replace("{{TITULO}}", f"Arte {variante[-2:]} - Conexão")
    
    # Injeta Logo
    logo_tag = '<img class="logo" src="assets/logos/Logo_Conexão_horizontal_texto_branco.png" alt="Conexão Implantes">'
    html_final = re.sub(r'<!--\s*\{\{LOGO\}\}.*?-->', logo_tag, html_final, flags=re.DOTALL)
    
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
    
    html_final = re.sub(r'<!--\s*\{\{BADGE_CONTEXTO\}\}.*?-->', badge_tag, html_final, flags=re.DOTALL)

    # Injeta Imagem de Produto
    produto_tag = '<img class="produto" src="assets/kit_start_flex_frontal.png" alt="Kit Start Flex">'
    html_final = re.sub(r'<!--\s*\{\{IMAGEM_PRODUTO\}\}.*?-->', produto_tag, html_final, flags=re.DOTALL)

    # Injeta Headline, Subcopy e CTA
    html_final = re.sub(r'<!--\s*\{\{HEADLINE\}\}.*?-->', f'<h1>{headline}</h1>', html_final, flags=re.DOTALL)
    html_final = re.sub(r'<!--\s*\{\{SUBCOPY\}\}.*?-->', f'<p class="subcopy">{subcopy}</p>', html_final, flags=re.DOTALL)
    html_final = html_final.replace("{{NOME_MARCA}}", "Conexão Sistemas de Próteses")
    
    cta_tag = f'<span class="cta">{cta}</span>'
    html_final = re.sub(r'<!--\s*\{\{CTA\}\}.*?-->', cta_tag, html_final, flags=re.DOTALL)

    # Salva HTML temporário
    dest_html.write_text(html_final, encoding="utf-8")

    # Renderiza com Playwright para PNG pixel-perfect
    print(f"Renderizando {variante} em PNG ({largura}x{altura}px)...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": largura, "height": altura})
            page.goto(f"file:///{dest_html.resolve()}")
            page.wait_for_timeout(500) # Aguarda transições e fontes
            page.screenshot(path=dest_png)
            browser.close()
        print(f"[OK] {variante}: Arte PNG gerada em {dest_png}")
    except Exception as e:
        print(f"[FALHA] Falha ao renderizar {variante} via Playwright ({e})")
        dest_html.unlink(missing_ok=True)
        return 1

    # Deleta HTML temporário
    dest_html.unlink(missing_ok=True)
    return 0


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
