#!/usr/bin/env python3
"""
Compila a apostila Markdown de um projeto em PDF final usando o template Typst
e aplicando o design system da Conexão.
"""

import argparse
import re
import shutil
import sys
import json
from pathlib import Path

# Adiciona o diretório de scripts ao path para poder importar pdf_typst
sys.path.append(str(Path(__file__).resolve().parent))
from pdf_typst import executar

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
CAMINHO_BRAND = DIR_PROJETO / "brand" / "design-system-conexao.json"
DIR_LOGOS = DIR_PROJETO / "assets" / "logos-marca"


def carregar_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except Exception:
        return None


def extrair_nome_produto(slug_dir, slug):
    """Nome do produto para o título — lido do cabeçalho do dossiê de insumos
    ('# Dossiê de Insumos — Kit X'), nunca hardcoded por slug."""
    dossie = slug_dir / "insumos" / "dossie_insumos.md"
    if dossie.exists():
        try:
            primeira_linha = dossie.read_text(encoding="utf-8").splitlines()[0]
            if "—" in primeira_linha:
                nome = primeira_linha.split("—", 1)[-1].strip()
                if nome:
                    return nome
        except Exception:
            pass
    # Fallback: deriva do slug (ex.: kit-start-flex -> Kit Start Flex)
    return " ".join(p.capitalize() for p in slug.split("-"))


def extrair_imagem_produto(config, slug_dir, slug):
    """Path da imagem do produto, relativo a slug_dir (root de compilação do Typst).
    Fonte de verdade: config_projeto.json.imagens[0].path (nunca hardcoded)."""
    if config:
        imagens = config.get("imagens", [])
        if imagens:
            path = str(imagens[0].get("path", "")).replace("\\", "/")
            if path:
                prefixo = f"output/{slug}/"
                if path.startswith(prefixo):
                    return path[len(prefixo):]
                return path
    # Fallback: procura a primeira imagem em insumos/
    insumos_dir = slug_dir / "insumos"
    if insumos_dir.exists():
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            achados = sorted(insumos_dir.rglob(ext))
            if achados:
                return str(achados[0].relative_to(slug_dir)).replace("\\", "/")
    return None


def extrair_cta_final(md_path):
    """CTA final — texto da última seção '## ' da apostila (Fechamento, por
    contrato de redator-apostila), nunca hardcoded por projeto."""
    fallback = (
        "Fale com o time de produto Conexão para dúvidas técnicas adicionais. "
        "— Conexão Sistemas de Próteses"
    )
    try:
        texto = md_path.read_text(encoding="utf-8")
    except Exception:
        return fallback

    secoes = re.split(r"(?m)^## .*$", texto)
    if len(secoes) > 1:
        corpo = secoes[-1].strip()
        corpo = re.sub(r"<!--.*?-->", "", corpo, flags=re.S).strip()
        if corpo:
            return corpo
    return fallback


def extrair_capa_textos(md_path):
    """Título e parágrafo da capa — extraídos da seção '## Abertura' do próprio
    Markdown (SPEC_PDF: a capa remete ao TEMA do material, nunca ao rótulo
    genérico 'Guia de Treinamento'). capa_titulo = primeiro H1 da Abertura;
    capa_paragrafo = primeiro parágrafo logo após o H1 (parágrafo de apoio).
    Retorna (None, None) se a seção não existir."""
    try:
        texto = md_path.read_text(encoding="utf-8")
    except Exception:
        return None, None

    secoes = re.split(r"(?m)^## .*$", texto)
    abertura = secoes[1] if len(secoes) > 1 else texto
    titulo = None
    paragrafo = None
    achou_h1 = False
    linhas = abertura.splitlines()
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        i += 1
        if not linha or linha.startswith("<!--"):
            continue
        if linha.startswith("# "):
            if titulo is None:
                titulo = linha[2:].strip()
                achou_h1 = True
            continue
        if linha.startswith("## ") or linha.startswith("!"):
            continue
        if achou_h1:
            partes = [re.sub(r"[\*\>]", "", linha).strip()]
            while i < len(linhas):
                prox = linhas[i].strip()
                if not prox or prox.startswith("#") or prox.startswith("!"):
                    break
                partes.append(re.sub(r"[\*\>]", "", prox).strip())
                i += 1
            paragrafo = " ".join(p for p in partes if p)
            break
    return titulo, paragrafo


def preparar_corpo_sem_h1_duplicado(md_path, dest_path):
    """Grava em `dest_path` uma cópia do Markdown com o H1 temático da Abertura
    (já extraído para `capa_titulo` por `extrair_capa_textos`) rebaixado para
    texto em negrito, em vez de heading nível 1.

    Por quê: `template_apostila.typ` estiliza heading nível 1 como um divisor de
    capítulo (`pagebreak()` + título grande) — correto para um heading real, mas
    esse H1 nunca foi pensado para isso, só para alimentar a capa via regex. Ao
    sobreviver como heading nível 1 no corpo, ele força uma quebra de página
    logo após "## Abertura" (que fica sozinha, sem nada abaixo — a seção parece
    "em branco") e o título reaparece na própria página seguinte como um
    capítulo novo, inclusive duplicado no Sumário. Isso só acontece quando
    `redator-apostila` inclui o H1 (conforme o próprio contrato pede) — quando
    ele é omitido, a Abertura renderiza inteira, sem quebra."""
    texto = md_path.read_text(encoding="utf-8")
    texto_corrigido = re.sub(r"(?m)^# (.+)$", r"**\1**", texto, count=1)
    dest_path.write_text(texto_corrigido, encoding="utf-8")


def preparar_assets_logo(slug_dir, pasta):
    """Copia os logos de marca fixos para <pasta>/assets/logos/, mesmo padrão
    usado por landing-page/apresentacao/arte (compilar-html.py / compilar-arte.py).
    `pasta` é normalmente "pdf", mas pode ser uma versão regenerada (ex.:
    "pdf-v2") por /gerar-pdf — ver REGRA 11 do AGENTS.md."""
    dest = slug_dir / pasta / "assets" / "logos"
    dest.mkdir(parents=True, exist_ok=True)
    if DIR_LOGOS.exists():
        for logo in DIR_LOGOS.glob("*.png"):
            shutil.copy(logo, dest / logo.name)


def main():
    ap = argparse.ArgumentParser(description="Compila apostila de Markdown para PDF usando Typst")
    ap.add_argument("slug")
    ap.add_argument("--pasta", default="pdf",
                     help="pasta de destino em output/<slug>/ (default: 'pdf'; use "
                          "'pdf-v2', 'pdf-v3'... para regeneracoes que nao devem "
                          "sobrescrever a versao anterior - ver REGRA 11 do AGENTS.md)")
    args = ap.parse_args()

    slug_dir = DIR_OUTPUT / args.slug
    md = slug_dir / args.pasta / f"apostila_{args.slug}.md"
    pdf = slug_dir / args.pasta / f"apostila_{args.slug}.pdf"

    if not md.exists():
        print(f"[ERRO] Arquivo Markdown não encontrado em {md}")
        return 1

    # Carrega variáveis do design system
    brand = carregar_json(CAMINHO_BRAND)
    if brand is None:
        print(f"[ERRO] {CAMINHO_BRAND} não encontrado")
        return 1

    cores = brand.get("cores", {})
    tipografia = brand.get("tipografia", {})

    # Recupera edição/config do config_projeto.json
    config = carregar_json(slug_dir / "config_projeto.json")
    edicao = config.get("edicao", "1ª Edição") if config else "1ª Edição"

    # Título e subtítulo — nome do produto vem do dossiê, mensagem central do brief
    brief = carregar_json(slug_dir / "brief_criativo.json")
    nome_produto = extrair_nome_produto(slug_dir, args.slug)
    title = f"Guia de Treinamento Técnico: {nome_produto}"
    subtitle = (brief or {}).get("mensagem_central") or (
        "Guia de treinamento técnico e de vendas para o consultor Conexão."
    )

    # Substitui qualquer hífen por dois-pontos de forma garantida (SPEC_PDF: sem hífens em títulos)
    title = title.replace(" - ", ": ").replace("-", ":")

    # Capa — título e parágrafo remetem ao TEMA do material (seção Abertura do
    # Markdown, redator-apostila). Fallbacks: título genérico e mensagem central.
    capa_titulo, capa_paragrafo = extrair_capa_textos(md)
    capa_titulo = (capa_titulo or title).strip()
    capa_paragrafo = (capa_paragrafo or subtitle).strip()

    # CTA final — extraído da última seção ('## Fechamento') da própria apostila
    cta_final = extrair_cta_final(md)

    # Cores e fontes da marca
    fonte_titulo = tipografia.get("titulo", {}).get("familia", "Inter")
    fonte_corpo = tipografia.get("corpo", {}).get("familia", "Inter")

    # Logos de marca (fixos) precisam existir em <pasta>/assets/logos/ antes da compilação
    preparar_assets_logo(slug_dir, args.pasta)

    # Paths relativos para o Typst (em relação ao slug_dir / `--root` de compilação)
    logo_imagem = f"{args.pasta}/assets/logos/Logo_Conexão_horizontal_texto_branco.png"
    imagem_produto = extrair_imagem_produto(config, slug_dir, args.slug)

    # Monta as flags -V
    lista_de_flags_V = [
        "-V", f"cor_primaria={cores.get('accent', '#c9a655')}",
        "-V", f"cor_secundaria={cores.get('textMuted', '#94a3b8')}",
        "-V", f"cor_destaque={cores.get('gradientMid', '#e8d48b')}",
        "-V", f"cor_texto={cores.get('textMain', '#f8fafc')}",
        "-V", f"cor_fundo={cores.get('bg', '#0f172a')}",
        "-V", f"fonte_titulo={fonte_titulo}",
        "-V", f"fonte_corpo={fonte_corpo}",
        "-V", f"title={title}",
        "-V", f"subtitle={subtitle}",
        "-V", f"capa_titulo={capa_titulo}",
        "-V", f"capa_paragrafo={capa_paragrafo}",
        "-V", f"author=Conexão Sistemas de Próteses",
        "-V", f"logo_imagem={logo_imagem}",
        "-V", f"cta_final={cta_final}",
        "-V", f"edicao={edicao}",
    ]
    if imagem_produto:
        lista_de_flags_V += ["-V", f"imagem_produto={imagem_produto}"]
    else:
        print("[AVISO] Nenhuma imagem de produto encontrada (config_projeto.json/insumos) — "
              "capa usará o fallback do template. Registrar como faltante.")

    # Corpo real da compilação: mesmo Markdown do redator-apostila, mas com o H1
    # da Abertura rebaixado para negrito (ver preparar_corpo_sem_h1_duplicado) —
    # o arquivo apostila_<slug>.md original nunca é alterado.
    corpo_compilacao = slug_dir / args.pasta / f"_corpo_apostila_{args.slug}.md"
    preparar_corpo_sem_h1_duplicado(md, corpo_compilacao)

    comando = [
        "pandoc", str(corpo_compilacao),
        "--pdf-engine=typst",
        "--template", "templates/template_apostila.typ",
        "-o", str(pdf),
    ] + lista_de_flags_V

    print(f"Compilando PDF para {args.slug}...")
    resultado = executar(comando, pdf, slug_dir, typst_bin="typst", timeout=300)
    corpo_compilacao.unlink(missing_ok=True)

    if resultado.returncode == 0:
        print(f"[OK] PDF compilado com sucesso em {pdf}")
        return 0
    else:
        print(f"[FALHA] Falha ao compilar PDF:")
        print(resultado.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
