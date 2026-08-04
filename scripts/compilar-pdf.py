#!/usr/bin/env python3
"""
Compila a apostila Markdown de um projeto em PDF final usando o template Typst
e aplicando o design system da Conexão.
"""

import argparse
import sys
import json
from pathlib import Path

# Adiciona o diretório de scripts ao path para poder importar pdf_typst
sys.path.append(str(Path(__file__).resolve().parent))
from pdf_typst import executar

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
CAMINHO_BRAND = DIR_PROJETO / "brand" / "design-system-conexao.json"


def carregar_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="Compila apostila de Markdown para PDF usando Typst")
    ap.add_argument("slug")
    args = ap.parse_args()

    slug_dir = DIR_OUTPUT / args.slug
    md = slug_dir / "pdf" / f"apostila_{args.slug}.md"
    pdf = slug_dir / "pdf" / f"apostila_{args.slug}.pdf"

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

    # Título e descrição do brief
    brief = carregar_json(slug_dir / "brief_criativo.json")
    title = "Kit de Treinamento Técnico: Start Flex"
    subtitle = "O GPS cirúrgico para os casos mais frequentes do consultório."

    if brief:
        msg = brief.get("mensagem_central", "")
        if msg:
            subtitle = msg
        # Capitaliza o slug de forma bonita
        title = "Guia de Treinamento Técnico: " + " ".join(word.capitalize() for word in args.slug.split("-")[1:])
    
    # Substitui qualquer hífen por dois-pontos de forma garantida
    title = title.replace(" - ", ": ").replace("-", ":")

    # CTA Final da apostila
    cta_final = (
        "O Kit Start Flex é o principal aliado do consultor para fidelizar o cliente. "
        "Ao vendê-lo, você não entrega apenas metal — entrega segurança clínica e previsibilidade.\n\n"
        "Fale com o time de produto Conexão para dúvidas técnicas adicionais. — Conexão Implantes"
    )

    # Recupera edição do config_projeto.json
    config = carregar_json(slug_dir / "config_projeto.json")
    edicao = config.get("edicao", "1ª Edição") if config else "1ª Edição"

    # Cores e fontes da marca
    fonte_titulo = tipografia.get("titulo", {}).get("familia", "Inter")
    fonte_corpo = tipografia.get("corpo", {}).get("familia", "Inter")

    # Paths relativos para o Typst (em relação ao slug_dir / `--root` de compilação)
    logo_imagem = "pdf/assets/logos/Logo_Conexão_horizontal_texto_branco.png"
    imagem_produto = "insumos/kit_start_flex_frontal.png"

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
        "-V", f"author=Conexão Sistemas de Próteses",
        "-V", f"logo_imagem={logo_imagem}",
        "-V", f"imagem_produto={imagem_produto}",
        "-V", f"cta_final={cta_final}",
        "-V", f"edicao={edicao}",
    ]

    comando = [
        "pandoc", str(md),
        "--pdf-engine=typst",
        "--template", "templates/template_apostila.typ",
        "-o", str(pdf),
    ] + lista_de_flags_V

    print(f"Compilando PDF para {args.slug}...")
    resultado = executar(comando, pdf, slug_dir, typst_bin="typst", timeout=300)

    if resultado.returncode == 0:
        print(f"[OK] PDF compilado com sucesso em {pdf}")
        return 0
    else:
        print(f"[FALHA] Falha ao compilar PDF:")
        print(resultado.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
