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


# ── Componentes animados de dado (v1) ────────────────────────────────────
# Ver .claude/skills/aplicador-marca-conexao/SKILL.md, secao "Componentes
# animados de dado", e docs/03-plano-componentes-animados.md. Cada funcao
# recebe apenas o dict "dados" de um bloco {"tipo": ..., "dados": {...}} e
# devolve HTML pronto para injetar num slide (apresentacao) ou secao
# (landing-page). CSS/animacao vive nos templates via custom properties
# (--gauge-offset, --donut-offset, --barra-pct) para permitir varias
# instancias na mesma pagina sem duplicar regras CSS.

def renderizar_gauge(dados):
    valor = dados.get("valor", 0)
    minimo = dados.get("min", 0)
    maximo = dados.get("max", 100)
    unidade = dados.get("unidade", "")
    titulo_indicador = formatar_markdown(dados.get("titulo_indicador", "Indicador"))
    marcas = dados.get("marcas", [])
    intervalo = (maximo - minimo) or 1
    fracao = max(0.0, min(1.0, (valor - minimo) / intervalo))
    offset = round(251.2 * (1 - fracao), 1)
    angulo = round(-90 + 180 * fracao, 1)

    labels = [f'<span>{minimo}{(" " + unidade) if unidade else ""}</span>']
    for m in marcas:
        m_label = formatar_markdown(m.get("label") or f'{m.get("valor", "")}{(" " + unidade) if unidade else ""}')
        labels.append(f'<span class="ativo">{m_label}</span>')
    labels_str = "".join(labels)

    return f"""<div class="gauge-box">
          <h4>{titulo_indicador}</h4>
          <svg class="gauge-svg" viewBox="0 0 200 110">
            <path class="gauge-track" d="M 20 95 A 80 80 0 0 1 180 95" />
            <path class="gauge-value" style="--gauge-offset:{offset}" d="M 20 95 A 80 80 0 0 1 180 95" />
            <polygon class="gauge-pointer" style="--gauge-angulo:{angulo}deg" points="100,95 97,15 103,15" fill="var(--accent)" stroke="rgb(255, 248, 214)" stroke-width="1" />
            <circle cx="100" cy="95" r="8" fill="var(--surface)" stroke="var(--accent)" stroke-width="2" />
          </svg>
          <div class="gauge-labels">{labels_str}</div>
        </div>"""


def renderizar_fluxo(dados):
    passos = dados.get("passos", [])
    blocos = []
    for i, p in enumerate(passos):
        titulo = formatar_markdown(p.get("titulo", f"Passo {i+1}"))
        texto = formatar_markdown(p.get("texto", ""))
        blocos.append(f"""
        <div class="fluxo-passo">
          <span class="numero">{i+1}</span>
          <h4>{titulo}</h4>
          <p>{texto}</p>
        </div>""")
        if i < len(passos) - 1:
            blocos.append('<div class="fluxo-seta">&rarr;</div>')
    return f'<div class="fluxo-container">{"".join(blocos)}</div>'


def renderizar_contador(dados):
    valor_final = dados.get("valor_final", 0)
    prefixo = dados.get("prefixo", "")
    sufixo = dados.get("sufixo", "")
    label = formatar_markdown(dados.get("label", ""))
    return f"""<div class="contador-box">
          <div class="contador-numero" data-valor="{valor_final}" data-prefixo="{prefixo}" data-sufixo="{sufixo}">{prefixo}0{sufixo}</div>
          <div class="contador-label">{label}</div>
        </div>"""


def renderizar_donut(dados):
    percentual = max(0, min(100, dados.get("percentual", 0)))
    label = formatar_markdown(dados.get("label", ""))
    offset = round(283 * (1 - percentual / 100), 1)
    return f"""<div class="donut-box">
          <svg class="donut-svg" viewBox="0 0 100 100">
            <circle class="donut-track" cx="50" cy="50" r="45" />
            <circle class="donut-value" style="--donut-offset:{offset}" cx="50" cy="50" r="45" />
          </svg>
          <div class="donut-percentual">{percentual}%</div>
          <div class="donut-label">{label}</div>
        </div>"""


def renderizar_accordion(dados):
    itens = dados.get("itens", [])
    blocos = []
    for item in itens:
        pergunta = formatar_markdown(item.get("pergunta", ""))
        resposta = formatar_markdown(item.get("resposta", ""))
        blocos.append(f"""
      <details class="accordion-item">
        <summary>{pergunta}</summary>
        <div class="accordion-resposta">{resposta}</div>
      </details>""")
    return "".join(blocos)


def renderizar_barras(dados):
    itens = dados.get("itens", [])
    maximo = dados.get("max") or (max([i.get("valor", 0) for i in itens], default=1) or 1)
    unidade = dados.get("unidade", "")
    blocos = []
    for item in itens:
        label = formatar_markdown(item.get("label", ""))
        valor = item.get("valor", 0)
        u = item.get("unidade", unidade)
        pct = round(min(100, (valor / maximo) * 100), 1) if maximo else 0
        blocos.append(f"""
        <div class="barra-item">
          <div class="barra-topo-label"><span>{label}</span><strong>{valor}{(" " + u) if u else ""}</strong></div>
          <div class="barra-trilho"><div class="barra-fill" style="--barra-pct:{pct}%"></div></div>
        </div>""")
    return f'<div class="barras-container">{"".join(blocos)}</div>'


def renderizar_cards_destaque(itens):
    """Layout padrão de slides/seções sem componente de dado (substitui a
    antiga lista <ul><li> plana): cada bullet vira um card com barra de
    assinatura no topo, mesma linguagem visual dos demais componentes.
    Reaproveita o padrao "**Titulo** — Texto" ja usado pelos parsers de
    torque/objecoes."""
    cards = []
    for item in itens:
        if not isinstance(item, str):
            continue
        partes = item.split(" — ") if " — " in item else (item.split(" - ") if " - " in item else [item])
        if len(partes) >= 2:
            titulo_item = formatar_markdown(partes[0].replace("**", "").strip())
            corpo_item = formatar_markdown(" — ".join(partes[1:]).strip())
        else:
            titulo_item = ""
            corpo_item = formatar_markdown(item)
        titulo_html = f"<h4>{titulo_item}</h4>" if titulo_item else ""
        cards.append(f"""
        <div class="card-destaque">
          {titulo_html}
          <p>{corpo_item}</p>
        </div>""")
    return f'<div class="cards-grid">{"".join(cards)}</div>'


COMPONENTES_RENDERIZADORES = {
    "gauge": renderizar_gauge,
    "fluxo": renderizar_fluxo,
    "contador": renderizar_contador,
    "donut": renderizar_donut,
    "accordion": renderizar_accordion,
    "barras": renderizar_barras,
}


def renderizar_componente(componente):
    """componente = {"tipo": "gauge"|"fluxo"|"contador"|"donut"|"accordion"|"barras", "dados": {...}}"""
    if not componente:
        return ""
    tipo = componente.get("tipo")
    fn = COMPONENTES_RENDERIZADORES.get(tipo)
    if not fn:
        print(f"[AVISO] tipo de componente desconhecido: {tipo!r} — ignorado")
        return ""
    return fn(componente.get("dados", {}))


def compilar_apresentacao(slug, pasta="apresentacao"):
    """`pasta` e normalmente "apresentacao", mas pode ser uma versao regenerada
    (ex.: "apresentacao-v2") por /gerar-apresentacao — ver REGRA 11 do AGENTS.md.
    O `slides.json` de entrada tambem vive dentro de `pasta` (gravado la pelo
    redator-apresentacao antes desta chamada)."""
    slug_dir = DIR_OUTPUT / slug
    slides_path = slug_dir / pasta / "slides.json"
    template_path = DIR_PROJETO / "templates" / "apresentacao.html"
    dest_html = slug_dir / pasta / "index.html"
    dest_assets = slug_dir / pasta / "assets"

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
        <span class="badge pulso">Uso Interno</span>
        <div style="max-width: 540px; width: 100%;">
          <h1>{titulo}</h1>
          <p style="font-size: 1.25rem; line-height: 1.5; color: var(--text-muted); max-width: 100%;">{corpo_formatado}</p>
        </div>
      </div>
      <div class="capa-direita">
        <img src="assets/{img_produto_filename}" alt="Produto">
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
            # Componente explícito (v1, ver docs/03-plano-componentes-animados.md):
            # se o slide já vem com "componente" do redator-apresentacao, usa o
            # dado real em vez de adivinhar pelo título — precedência sobre toda
            # heurística de palavra-chave abaixo.
            if s.get("componente"):
                componente_html = renderizar_componente(s["componente"])
                tipo_componente = s["componente"].get("tipo")
                wrapper_classe = "gauge-container" if tipo_componente == "gauge" else "componente-wrap"
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <div class="{wrapper_classe}">
        {componente_html}
      </div>
    </div>"""
                html_slides.append(html)
                continue

            # Tipo Conteúdo: Auto-detecta o layout mais visual aplicável (Fluxogramas ou Tabelas)
            # Se título contiver "Script" ou "SPIN" -> Renderiza FLUXOGRAMA horizontal!
            if "script" in titulo.lower() or "spin" in titulo.lower():
                passos = []
                if isinstance(corpo, list):
                    for item in corpo:
                        partes = item.split(" — ") if " — " in item else item.split(" - ")
                        p_titulo = partes[0].strip().replace("**", "") if len(partes) >= 2 else item
                        p_texto = partes[1].strip() if len(partes) >= 2 else ""
                        passos.append({"titulo": p_titulo, "texto": p_texto})
                fluxo_html = renderizar_fluxo({"passos": passos})
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      {fluxo_html}
    </div>"""
                html_slides.append(html)

            # Se título contiver "Torque" -> Renderiza TABELA com GAUGE interativo!
            # (caminho legado por palavra-chave — mesmos valores hardcoded de
            # sempre; para dado real, redator-apresentacao deve usar o campo
            # "componente": {"tipo": "gauge", ...} explícito, ver acima)
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

                gauge_html = renderizar_gauge({
                    "valor": 60, "min": 0, "max": 80, "unidade": "Ncm",
                    "titulo_indicador": "Indicador de Torque Seguro",
                    "marcas": [{"valor": 45, "label": "45 Ncm (Slim)"},
                               {"valor": 60, "label": "60 Ncm (NP)"}],
                })

                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      <div class="gauge-container">
        <div class="gauge-corpo">
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
        {gauge_html}
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
                # Layout padrão: grid de cards de destaque (substitui a antiga
                # lista <ul><li> plana — ver renderizar_cards_destaque; CSS
                # grid auto-fit cuida do número de colunas, sem precisar mais
                # de divisão manual em duas-colunas por tamanho de lista).
                itens = corpo if isinstance(corpo, list) else ([corpo] if isinstance(corpo, str) else [])
                cards_html = renderizar_cards_destaque(itens)
                html = f"""
    <div class="slide conteudo{ativo_class}">
      <h2>{titulo}</h2>
      {cards_html}
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


def compilar_landing(slug, pasta="landing-page"):
    """`pasta` e normalmente "landing-page", mas pode ser uma versao regenerada
    (ex.: "landing-page-v2") por /gerar-landing — ver REGRA 11 do AGENTS.md."""
    slug_dir = DIR_OUTPUT / slug
    conteudo_path = slug_dir / pasta / "conteudo.json"
    template_path = DIR_PROJETO / "templates" / "landing.html"
    dest_html = slug_dir / pasta / "index.html"
    dest_assets = slug_dir / pasta / "assets"

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

    # Copia imagem do produto se existir (path real vem de config_projeto.json,
    # nunca hardcoded — cada projeto tem seu próprio nome/local de imagem)
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
      <div class="card">
        <h3>{p_titulo}</h3>
        <p>{p_texto}</p>
      </div>
      <div class="card">
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
        <img src="assets/{img_produto_filename}" alt="Produto" style="max-height: 50vh; filter: drop-shadow(0 15px 30px rgba(0,0,0,0.4)); object-fit: contain;">
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

    # 6. Componentes animados de dado (v1, ver docs/03-plano-componentes-animados.md):
    # cada item de "enriquecimentos" e anexado ao final da secao indicada em
    # "secao" (destaques | prova | cta_final | problema_solucao). Ausente por
    # padrao — so aparece quando o dossie do projeto justificar (REGRA 6).
    enriquecimentos = dados.get("enriquecimentos", [])
    enriquecimentos_por_secao = {"destaques": [], "prova": [], "cta_final": [], "problema_solucao": []}
    for item in enriquecimentos:
        secao = item.get("secao")
        if secao in enriquecimentos_por_secao:
            enriquecimentos_por_secao[secao].append(
                renderizar_componente({"tipo": item.get("tipo"), "dados": item.get("dados", {})})
            )
        else:
            print(f"[AVISO] enriquecimentos: secao desconhecida {secao!r} — ignorado")

    if enriquecimentos_por_secao["problema_solucao"]:
        ps_html += "".join(enriquecimentos_por_secao["problema_solucao"])
    if enriquecimentos_por_secao["destaques"]:
        destaques_str += "".join(enriquecimentos_por_secao["destaques"])
    if enriquecimentos_por_secao["prova"]:
        prova_str += "".join(enriquecimentos_por_secao["prova"])
    if enriquecimentos_por_secao["cta_final"]:
        cta_final_html += "".join(enriquecimentos_por_secao["cta_final"])

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
    ap.add_argument("--pasta", default=None,
                     help="pasta de destino em output/<slug>/ (default: o proprio "
                          "<tipo>; use '<tipo>-v2', '-v3'... para regeneracoes que nao "
                          "devem sobrescrever a versao anterior - ver REGRA 11 do AGENTS.md)")
    args = ap.parse_args()
    pasta = args.pasta or args.tipo

    if args.tipo == "apresentacao":
        return compilar_apresentacao(args.slug, pasta)
    elif args.tipo == "landing-page":
        return compilar_landing(args.slug, pasta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
