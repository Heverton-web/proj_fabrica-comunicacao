#!/usr/bin/env python3
"""
Compilador HTML para Apresentação (Slides) e Landing Page (Intranet/Wiki),
aplicando o design system fixo da Conexão.
"""

import argparse
import sys
import json
import re
import shutil
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
DIR_FONTS = DIR_PROJETO / "templates" / "fonts"
DIR_LOGOS = DIR_PROJETO / "assets" / "logos-marca"


def carregar_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except Exception:
        return None


def compilar_apresentacao(slug):
    slug_dir = DIR_OUTPUT / slug
    slides_path = slug_dir / "apresentacao" / "slides.json"
    template_path = DIR_PROJETO / "templates" / "apresentacao.html"
    dest_html = slug_dir / "apresentacao" / "index.html"
    dest_assets = slug_dir / "apresentacao" / "assets"

    if not slides_path.exists():
        print(f"[ERRO] slides.json não encontrado em {slides_path}")
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
    dados = carregar_json(slides_path)
    if not dados:
        print(f"[ERRO] Não foi possível carregar o arquivo {slides_path}")
        return 1
    slides_list = dados.get("slides", [])

    html_slides = []
    for idx, s in enumerate(slides_list):
        tipo = s.get("tipo", "conteudo")
        titulo = s.get("titulo", "")
        corpo = s.get("corpo", "")
        ativo_class = " ativo" if idx == 0 else ""

        if tipo == "capa":
            # Slide 1 Layout Hero de Capa (Conteúdo à esquerda, imagem do produto à direita)
            html = f"""
    <div class="slide capa{ativo_class}">
      <div class="capa-esquerda">
        <span class="badge">Uso Interno</span>
        <h1>{titulo}</h1>
        <p>{corpo}</p>
      </div>
      <div class="capa-direita">
        <img src="assets/kit_start_flex_frontal.png" alt="Start Flex">
      </div>
    </div>"""
            html_slides.append(html)

        elif tipo == "cta":
            # Slide CTA Centralizado com botão-badge
            html = f"""
    <div class="slide cta{ativo_class}">
      <span class="badge">Dica de Ouro</span>
      <h1 style="font-size: 2.6rem;">{titulo}</h1>
      <p style="margin-bottom: 1.5rem; color: var(--text-main); font-size: 1.25rem;">{corpo}</p>
      <button class="btn-badge">Conexão Implantes</button>
    </div>"""
            html_slides.append(html)

        else:
            # Tipo Conteúdo: Auto-detecta o layout mais visual aplicável
            # Se título contiver "Composição", "Versatilidade" ou "Diferencial" -> Renderiza Grid de CARDS!
            if "composic" in titulo.lower() or "versatilidade" in titulo.lower() or "diferencial" in titulo.lower():
                cards_html = []
                # Se corpo for uma lista
                if isinstance(corpo, list):
                    for item in corpo:
                        # Tenta quebrar em Título | Descrição
                        partes = item.split(" — ") if " — " in item else item.split(" - ")
                        if len(partes) >= 2:
                            card_title = partes[0].replace("**", "").strip()
                            card_desc = partes[1].strip()
                        else:
                            card_title = "Destaque"
                            card_desc = item.replace("**", "").strip()
                        
                        cards_html.append(f"""
        <div class="card-visual">
          <h3>{card_title}</h3>
          <p>{card_desc}</p>
        </div>""")
                cards_str = "\n".join(cards_html)
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <div class="grid-cards">
        {cards_str}
      </div>
    </div>"""
                html_slides.append(html)

            # Se título contiver "Script" ou "SPIN" -> Renderiza FLUXOGRAMA horizontal!
            elif "script" in titulo.lower() or "spin" in titulo.lower():
                passos_html = []
                if isinstance(corpo, list):
                    for i, item in enumerate(corpo):
                        partes = item.split(" — ") if " — " in item else item.split(" - ")
                        p_num = partes[0].strip() if len(partes) >= 2 else f"P{i+1}"
                        p_desc = partes[1].strip() if len(partes) >= 2 else item
                        
                        # Remove markdown bold
                        p_num = p_num.replace("**", "")
                        
                        passos_html.append(f"""
        <div class="fluxo-passo">
          <span class="numero">{i+1}</span>
          <h4>{p_num}</h4>
          <p>{p_desc}</p>
        </div>""")
                        if i < len(corpo) - 1:
                            passos_html.append('<div class="fluxo-seta">&rarr;</div>')
                passos_str = "\n".join(passos_html)
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <div class="fluxo-container">
        {passos_str}
      </div>
    </div>"""
                html_slides.append(html)

            # Se título contiver "Objeções" ou "Torque" -> Renderiza TABELA técnica!
            elif "objec" in titulo.lower() or "torque" in titulo.lower() or "tabela" in titulo.lower():
                rows_html = []
                if isinstance(corpo, list):
                    for item in corpo:
                        partes = item.split(" → ") if " → " in item else (item.split(" — ") if " — " in item else item.split(" - "))
                        if len(partes) >= 2:
                            c1 = partes[0].replace("**", "").replace('"', '').strip()
                            c2 = partes[1].strip()
                        else:
                            c1 = "Parâmetro"
                            c2 = item.replace("**", "").strip()
                        rows_html.append(f"<tr><td><strong>{c1}</strong></td><td>{c2}</td></tr>")
                rows_str = "\n".join(rows_html)
                
                # Cabeçalho da tabela dinâmico
                h1 = "Objeção / Dúvida" if "objec" in titulo.lower() else "Especificação"
                h2 = "Resposta Tática" if "objec" in titulo.lower() else "Parâmetro Clínico"
                
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <table class="tabela-visual">
        <thead>
          <tr>
            <th>{h1}</th>
            <th>{h2}</th>
          </tr>
        </thead>
        <tbody>
          {rows_str}
        </tbody>
      </table>
    </div>"""
                html_slides.append(html)

            else:
                # Layout padrão: Custom Bullets Double-Bezel
                bullets_html = []
                if isinstance(corpo, list):
                    for item in corpo:
                        bullets_html.append(f"<li>{item}</li>")
                elif isinstance(corpo, str):
                    bullets_html.append(f"<li>{corpo}</li>")
                bullets_str = "\n".join(bullets_html)
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <ul>
        {bullets_str}
      </ul>
    </div>"""
                html_slides.append(html)

    # Une todos os slides em bloco HTML
    slides_html_block = "\n".join(html_slides)

    # Injeta no template apresentacao.html
    template_content = template_path.read_text(encoding="utf-8")
    
    # Recupera edição do config_projeto.json
    config_path = slug_dir / "config_projeto.json"
    config = carregar_json(config_path)
    edicao = config.get("edicao", "1ª Edição") if config else "1ª Edição"

    # Injeta título
    guia_title = "Apresentação: " + " ".join(word.capitalize() for word in slug.split("-")[1:])
    html_final = template_content.replace("{{TITULO}}", guia_title)
    
    # Injeta Edição
    html_final = html_final.replace("{{EDICAO}}", edicao)
    
    # Injeta Logo
    logo_tag = '<img class="logo" src="assets/logos/Logo_Conexão_horizontal_texto_branco.png" alt="Conexão Implantes">'
    html_final = re.sub(r'<!--\s*\{\{LOGO\}\}.*?-->', logo_tag, html_final)

    # Injeta Slides
    html_final = re.sub(r'<!--\s*\{\{SLIDES\}\}.*?-->', slides_html_block, html_final)

    # Salva o arquivo final
    dest_html.write_text(html_final, encoding="utf-8")
    print(f"[OK] Apresentação compilada com sucesso em {dest_html}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Compila dados estruturados JSON em HTML aplicando design Conexão")
    ap.add_argument("slug")
    ap.add_argument("tipo", choices=["apresentacao"])
    args = ap.parse_args()

    if args.tipo == "apresentacao":
        return compilar_apresentacao(args.slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
