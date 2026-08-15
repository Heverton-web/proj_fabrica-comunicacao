import sys
import json
import traceback
from pathlib import Path

# __file__ is at output/<slug>/arte-03/_render.py
# So 4 parents up is the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
scripts_path = str(PROJECT_ROOT / "scripts")
sys.path.insert(0, scripts_path)

from _arte_common import (
    carregar_json, preencher_template, preparar_assets, 
    escolher_decoracao_fundo, gerar_forma_decorativa_html, renderizar_pagina
)
from playwright.sync_api import sync_playwright

SLUG = "kit-master-flex"
VARIANTE = "arte-03"
DIR_OUTPUT = PROJECT_ROOT / "output" / SLUG
DIR_ARTE = DIR_OUTPUT / VARIANTE
DIR_TEMPLATE = PROJECT_ROOT / "templates"

def main():
    try:
        # 1. Preparar assets (fonts, logos, product image)
        print(f"Preparando assets para {VARIANTE}...")
        img_filename = preparar_assets(DIR_ARTE, DIR_OUTPUT)
        print(f"Imagem do produto: {img_filename}")

        # 2. Carregar copies
        copies_path = DIR_OUTPUT / "arte" / "copies.json"
        print(f"Lendo copies de: {copies_path}")
        print(f"Arquivo existe: {copies_path.exists()}")
        
        copies_data = carregar_json(copies_path)
        print(f"Dados carregados: {copies_data is not None}")
        
        if copies_data:
            print(f"Chaves: {list(copies_data.keys())}")
            copies = copies_data.get("copies", [])
            print(f"Numero de copies: {len(copies)}")
            
            if len(copies) != 3:
                print("ERRO: Nao tem 3 copies.")
                sys.exit(1)
        else:
            print("ERRO: Falha ao carregar copies.json")
            sys.exit(1)

        # 3. Escolher forma decorativa (uma vez por variante, como instruido)
        forma_nome, instancias = escolher_decoracao_fundo(f"{SLUG}:{VARIANTE}")
        forma_html = gerar_forma_decorativa_html(forma_nome, instancias)
        print(f"Forma decorativa escolhida: {forma_nome}")

        # 4. Preparar badge
        badge_html = ""
        brief = carregar_json(DIR_OUTPUT / "brief_criativo.json")
        if brief:
            nota = brief.get("nota_de_escopo", "").lower()
            if "externo" in nota or "profissional" in nota:
                badge_html = '<span class="badge">USO PROFISSIONAL</span>'

        # 5. Ler template
        template_html = (DIR_TEMPLATE / "arte-1080x1920.html").read_text(encoding="utf-8")

        # 6. Renderizar com Playwright
        print("Renderizando PNGs...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for i, copy in enumerate(copies, start=1):
                idx_str = f"{i:02d}"
                html_final = preencher_template(
                    template_html,
                    titulo=copy.get("angulo", ""),
                    headline=copy.get("headline", ""),
                    subcopy=copy.get("subcopy", ""),
                    cta=copy.get("cta", ""),
                    img_produto_filename=img_filename,
                    badge_tag=badge_html,
                    forma_decorativa_html=forma_html
                )
                
                # Naming: index.html (copy-01), index_copy02.html (copy-02), etc.
                html_filename = "index.html" if i == 1 else f"index_copy{idx_str}.html"
                html_path = DIR_ARTE / html_filename
                png_path = DIR_ARTE / f"arte_{SLUG}_03_copy{idx_str}.png"
                
                html_path.write_text(html_final, encoding="utf-8")
                renderizar_pagina(browser, html_path, png_path, 1080, 1920, f"copy-{idx_str}")
                
            browser.close()

        print("Compilacao concluida.")
        
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
