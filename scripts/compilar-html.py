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


def formatar_markdown(texto):
    if not isinstance(texto, str):
        return texto
    # Substitui **texto** por <strong>texto</strong>
    texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
    # Substitui *texto* por <em>texto</em>
    texto = re.sub(r'\*(.*?)\*', r'<em>\1</em>', texto)
    return texto


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
            corpo_formatado = formatar_markdown(corpo)
            html = f"""
    <div class="slide capa{ativo_class}">
      <div class="capa-esquerda">
        <span class="badge">Uso Interno</span>
        <div style="max-width: 540px; width: 100%;">
          <h1>{titulo}</h1>
          <p style="font-size: 1.25rem; line-height: 1.5; color: var(--text-muted); max-width: 100%;">{corpo_formatado}</p>
        </div>
      </div>
      <div class="capa-direita">
        <img src="assets/kit_start_flex_frontal.png" alt="Start Flex">
      </div>
    </div>"""
            html_slides.append(html)

        elif tipo == "cta":
            # Slide CTA Centralizado com botão-badge translúcido
            corpo_formatado = formatar_markdown(corpo)
            html = f"""
    <div class="slide cta{ativo_class}">
      <span class="badge">Dica de Ouro</span>
      <h1 style="font-size: 2.6rem;">{titulo}</h1>
      <p style="margin-bottom: 1.5rem; color: var(--text-main); font-size: 1.25rem;">{corpo_formatado}</p>
      <button class="btn-badge">Conexão Implantes</button>
    </div>"""
            html_slides.append(html)

        else:
            # Tipo Conteúdo: Auto-detecta o layout mais visual aplicável (Fluxogramas ou Tabelas)
            # Se título contiver "Script" ou "SPIN" -> Renderiza FLUXOGRAMA horizontal!
            if "script" in titulo.lower() or "spin" in titulo.lower():
                passos_html = []
                if isinstance(corpo, list):
                    for i, item in enumerate(corpo):
                        partes = item.split(" — ") if " — " in item else item.split(" - ")
                        p_num = partes[0].strip() if len(partes) >= 2 else f"P{i+1}"
                        p_desc = partes[1].strip() if len(partes) >= 2 else item
                        
                        p_num = formatar_markdown(p_num.replace("**", ""))
                        p_desc = formatar_markdown(p_desc)
                        
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

            # Se título contiver "Torque" -> Renderiza TABELA com GAUGE interativo!
            elif "torque" in titulo.lower():
                rows_html = []
                if isinstance(corpo, list):
                    for item in corpo:
                        partes = item.split(" → ") if " → " in item else (item.split(" — ") if " — " in item else item.split(" - "))
                        if len(partes) >= 2:
                            c1 = formatar_markdown(partes[0].replace("**", "").replace('"', '').strip())
                            c2 = formatar_markdown(partes[1].strip())
                        else:
                            c1 = "Parâmetro"
                            c2 = formatar_markdown(item.replace("**", "").strip())
                        rows_html.append(f"<tr><td><strong>{c1}</strong></td><td>{c2}</td></tr>")
                rows_str = "\n".join(rows_html)
                
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <div class="torque-container">
        <div class="torque-tabela">
          <table class="tabela-visual">
            <thead>
              <tr>
                <th>Especificação</th>
                <th>Parâmetro Clínico</th>
              </tr>
            </thead>
            <tbody>
              {rows_str}
            </tbody>
          </table>
        </div>
        <div class="torque-gauge-box">
          <h4>Indicador de Torque Seguro</h4>
          <svg class="gauge-svg" viewBox="0 0 200 110">
            <path class="gauge-track" d="M 20 95 A 80 80 0 0 1 180 95" />
            <path class="gauge-value" d="M 20 95 A 80 80 0 0 1 180 95" />
            <polygon class="gauge-pointer" points="100,95 97,15 103,15" fill="var(--accent)" stroke="rgb(255, 248, 214)" stroke-width="1" />
            <circle cx="100" cy="95" r="8" fill="var(--surface)" stroke="var(--accent)" stroke-width="2" />
          </svg>
          <div class="torque-labels">
            <span>0 Ncm</span>
            <span class="ativo" style="color: rgb(229, 193, 88);">45 Ncm (Slim)</span>
            <span class="ativo" style="color: var(--accent);">60 Ncm (NP)</span>
          </div>
        </div>
      </div>
    </div>"""
                html_slides.append(html)

            # Se título contiver "Objeções" ou "Tabela" -> Renderiza TABELA técnica padrão!
            elif "objec" in titulo.lower() or "tabela" in titulo.lower():
                rows_html = []
                if isinstance(corpo, list):
                    for item in corpo:
                        partes = item.split(" → ") if " → " in item else (item.split(" — ") if " — " in item else item.split(" - "))
                        if len(partes) >= 2:
                            c1 = formatar_markdown(partes[0].replace("**", "").replace('"', '').strip())
                            c2 = formatar_markdown(partes[1].strip())
                        else:
                            c1 = "Parâmetro"
                            c2 = formatar_markdown(item.replace("**", "").strip())
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
                if isinstance(corpo, list) and len(corpo) >= 4:
                    # Divisão dinâmica em duas colunas para dar espaçamento de respiro e tamanho perfeito de fonte
                    meio = (len(corpo) + 1) // 2
                    c1 = corpo[:meio]
                    c2 = corpo[meio:]
                    bullets1 = "\n".join([f"<li>{formatar_markdown(item)}</li>" for item in c1])
                    bullets2 = "\n".join([f"<li>{formatar_markdown(item)}</li>" for item in c2])
                    html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <div class="duas-colunas">
        <ul>
          {bullets1}
        </ul>
        <ul>
          {bullets2}
        </ul>
      </div>
    </div>"""
                else:
                    bullets_html = []
                    if isinstance(corpo, list):
                        for item in corpo:
                            formatted_item = formatar_markdown(item)
                            bullets_html.append(f"<li>{formatted_item}</li>")
                    elif isinstance(corpo, str):
                        formatted_item = formatar_markdown(corpo)
                        bullets_html.append(f"<li>{formatted_item}</li>")
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
    html_final = re.sub(r'<!--\s*\{\{LOGO\}\}.*?-->', logo_tag, html_final, flags=re.DOTALL)

    # Injeta Slides
    html_final = re.sub(r'<!--\s*\{\{SLIDES\}\}.*?-->', slides_html_block, html_final, flags=re.DOTALL)

    # Salva o arquivo final
    dest_html.write_text(html_final, encoding="utf-8")
    print(f"[OK] Apresentação compilada com sucesso em {dest_html}")
    return 0


def compilar_landing(slug):
    slug_dir = DIR_OUTPUT / slug
    conteudo_path = slug_dir / "landing-page" / "conteudo.json"
    template_path = DIR_PROJETO / "templates" / "landing.html"
    dest_html = slug_dir / "landing-page" / "index.html"
    dest_assets = slug_dir / "landing-page" / "assets"

    if not conteudo_path.exists():
        print(f"[ERRO] conteudo.json não encontrado em {conteudo_path}")
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

    # 1. Monta bloco HERO
    hero = dados.get("hero", {})
    hero_headline = formatar_markdown(hero.get("headline", ""))
    hero_subheadline = formatar_markdown(hero.get("subheadline", ""))
    hero_cta = formatar_markdown(hero.get("cta", "Consultar Guia"))
    hero_html = f"""
      <h1 class="titulo-gradiente">{hero_headline}</h1>
      <p class="sub">{hero_subheadline}</p>
      <a class="btn-primario" href="#cta">{hero_cta}</a>"""

    # 2. Monta bloco PROBLEMA / SOLUCAO
    ps = dados.get("problema_solucao", {})
    p_titulo = formatar_markdown(ps.get("problema", {}).get("titulo", "O Desafio"))
    p_texto = formatar_markdown(ps.get("problema", {}).get("texto", ""))
    s_titulo = formatar_markdown(ps.get("solucao", {}).get("titulo", "A Solução"))
    s_texto = formatar_markdown(ps.get("solucao", {}).get("texto", ""))
    ps_html = f"""
      <div>
        <h3>{p_titulo}</h3>
        <p>{p_texto}</p>
      </div>
      <div>
        <h3>{s_titulo}</h3>
        <p>{s_texto}</p>
      </div>"""

    # 3. Monta bloco DESTAQUES (Cards)
    destaques_list = dados.get("destaques", [])
    destaques_html = []
    for d in destaques_list:
        d_titulo = formatar_markdown(d.get("titulo", ""))
        d_texto = formatar_markdown(d.get("texto", ""))
        destaques_html.append(f"""
        <div class="card">
          <h3>{d_titulo}</h3>
          <p>{d_texto}</p>
        </div>""")
    destaques_str = "\n".join(destaques_html)

    # 4. Monta bloco PROVA (Tabelas técnicas do texto-base)
    prova = dados.get("prova", {})
    prova_html = []
    
    # Imagem do produto em destaque centralizada antes das tabelas
    prova_html.append(f"""
      <div style="display: flex; justify-content: center; margin-bottom: 3.5rem;">
        <img src="assets/kit_start_flex_frontal.png" alt="Kit Start Flex" style="max-height: 50vh; filter: drop-shadow(0 15px 30px rgba(0,0,0,0.4)); object-fit: contain;">
      </div>""")

    for k, v in prova.items():
        if isinstance(v, dict) and "cabecalho" in v and "linhas" in v:
            t_titulo = formatar_markdown(v.get("titulo", ""))
            t_header = v.get("cabecalho", [])
            t_rows = v.get("linhas", [])

            headers_html = "".join([f"<th>{formatar_markdown(h)}</th>" for h in t_header])
            
            rows_html = []
            for row in t_rows:
                cells = "".join([f"<td>{formatar_markdown(cell)}</td>" for cell in row])
                rows_html.append(f"<tr>{cells}</tr>")
            rows_str = "\n".join(rows_html)

            prova_html.append(f"""
      <div style="margin-bottom: 2.5rem;">
        <h3 style="color: var(--accent); margin-bottom: 1rem; text-transform: uppercase;">{t_titulo}</h3>
        <table>
          <thead>
            <tr>{headers_html}</tr>
          </thead>
          <tbody>
            {rows_str}
          </tbody>
        </table>
      </div>""")
    prova_str = "\n".join(prova_html)

    # 5. Monta bloco CTA FINAL
    cta_final = dados.get("cta_final", {})
    cf_headline = formatar_markdown(cta_final.get("headline", ""))
    cf_cta = formatar_markdown(cta_final.get("cta", "Consultar Guia"))
    cf_dica = formatar_markdown(cta_final.get("dica_ouro", ""))
    
    cta_final_html = f"""
      <h2 class="titulo-gradiente">{cf_headline}</h2>
      <a class="btn-primario" href="#">{cf_cta}</a>
      <p class="dica-ouro">{cf_dica}</p>"""

    # Carrega template e substitui
    template_content = template_path.read_text(encoding="utf-8")
    
    guia_title = "Landing Page: " + " ".join(word.capitalize() for word in slug.split("-")[1:])
    html_final = template_content.replace("{{TITULO}}", guia_title)
    
    # Badge contexto (Uso Interno / Uso Externo)
    brief = carregar_json(slug_dir / "brief_criativo.json")
    badge_texto = "USO INTERNO"
    if brief:
        # Se escopo contiver profissional/externo, ajusta
        nota = brief.get("nota_de_escopo", "").lower()
        if "externo" in nota or "profissional" in nota:
          badge_texto = "USO PROFISSIONAL"
    
    html_final = html_final.replace("{{BADGE_CONTEXTO}}", badge_texto)
    html_final = html_final.replace("{{MARCA}}", "2026 © Conexão Sistemas de Próteses — Todos os direitos reservados")

    # Injeta Logo
    logo_tag = '<img class="logo" src="assets/logos/Logo_Conexão_horizontal_texto_branco.png" alt="Conexão Implantes">'
    html_final = re.sub(r'<!--\s*\{\{LOGO\}\}.*?-->', logo_tag, html_final, flags=re.DOTALL)

    # Injeta Placeholders de Bloco
    html_final = re.sub(r'<!--\s*\{\{HERO\}\}.*?-->', hero_html, html_final, flags=re.DOTALL)
    html_final = re.sub(r'<!--\s*\{\{PROBLEMA_SOLUCAO\}\}.*?-->', ps_html, html_final, flags=re.DOTALL)
    html_final = re.sub(r'<!--\s*\{\{DESTAQUES\}\}.*?-->', destaques_str, html_final, flags=re.DOTALL)
    html_final = re.sub(r'<!--\s*\{\{PROVA\}\}.*?-->', prova_str, html_final, flags=re.DOTALL)
    html_final = re.sub(r'<!--\s*\{\{CTA_FINAL\}\}.*?-->', cta_final_html, html_final, flags=re.DOTALL)

    # Salva final
    dest_html.write_text(html_final, encoding="utf-8")
    print(f"[OK] Landing Page compilada com sucesso em {dest_html}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Compila dados estruturados JSON em HTML aplicando design Conexão")
    ap.add_argument("slug")
    ap.add_argument("tipo", choices=["apresentacao", "landing-page"])
    args = ap.parse_args()

    if args.tipo == "apresentacao":
        return compilar_apresentacao(args.slug)
    elif args.tipo == "landing-page":
        return compilar_landing(args.slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
