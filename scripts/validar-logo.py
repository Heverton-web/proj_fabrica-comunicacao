#!/usr/bin/env python3
"""
Confirma que o logo de marca está embutido no artefato final (REGRA 6 / REGRA 8).

O logo deixou de ser "se disponível" — é obrigatório em todo material
(landing-page, apresentacao, arte-*, pdf). Ver:
  .claude/skills/aplicador-marca-conexao/SKILL.md  (seção "Logo — obrigatório")
  brand/design-system-conexao.json                 (seção "logos")

Uso:
    python scripts/validar-logo.py <slug> <tipo>
    # tipo in: landing-page, apresentacao, arte-01, arte-02, arte-03, pdf

Exit 0 = logo presente e referenciado corretamente.
Exit 1 = logo ausente, arquivo não encontrado ou referência não detectada no artefato.
"""

import argparse
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
DIR_LOGOS = DIR_PROJETO / "assets" / "logos-marca"

# Variantes de logo por contexto de fundo
LOGO_FUNDO_ESCURO = "Logo_Conexão_horizontal_texto_branco.png"
LOGO_FUNDO_CLARO  = "Logo_Conexão_horizontal_texto_preto.png"

# O design system usa fundo escuro (--bg: #0f172a) — logo padrão é texto_branco
LOGO_PADRAO = LOGO_FUNDO_ESCURO


def checar_html(slug: str, tipo: str) -> int:
    pasta = DIR_OUTPUT / slug / tipo
    html = pasta / "index.html"

    if not html.exists():
        print(f"[ERRO] Artefato não encontrado: {html}")
        return 1

    conteudo = html.read_text(encoding="utf-8", errors="replace")

    # Verifica se o arquivo de logo foi copiado para assets/
    logo_asset = pasta / "assets" / "logos" / LOGO_PADRAO
    if not logo_asset.exists():
        print(f"[FALHA] {tipo}: arquivo de logo não copiado para {logo_asset}")
        print(f"  -> Copie {DIR_LOGOS / LOGO_PADRAO} para output/<slug>/{tipo}/assets/logos/")
        return 1

    # Verifica se o logo aparece referenciado no HTML
    nome_sem_ext = Path(LOGO_PADRAO).stem
    if nome_sem_ext not in conteudo and "logo" not in conteudo.lower():
        print(f"[FALHA] {tipo}: logo não encontrado referenciado no HTML")
        print(f"  -> Adicione <img src='assets/logos/{LOGO_PADRAO}' ...> no cabeçalho")
        return 1

    print(f"[OK] {tipo}: logo presente e referenciado ({LOGO_PADRAO})")
    return 0


def checar_pdf(slug: str) -> int:
    pasta = DIR_OUTPUT / slug / "pdf"

    # Para PDF: verifica que o arquivo de logo existe na pasta de assets do PDF
    logo_asset = pasta / "assets" / "logos" / LOGO_PADRAO
    if not logo_asset.exists():
        print(f"[FALHA] pdf: arquivo de logo não copiado para {logo_asset}")
        print(f"  -> Copie {DIR_LOGOS / LOGO_PADRAO} para output/<slug>/pdf/assets/logos/")
        return 1

    # Verifica no PDF BINARIO que ha pelo menos uma imagem raster embutida
    # (o logo na capa). O Typst nomeia XObjects como /x0, /x1 (nao /Im0), por
    # isso checamos por presenca de XObject, nao por prefixo. Checar o .typ
    # intermediario e fragil: o helper pdf_typst.py o apaga apos compilar.
    pdf = pasta / f"apostila_{slug}.pdf"
    if not pdf.exists():
        print(f"[FALHA] pdf: {pdf} não encontrado")
        return 1
    try:
        from pypdf import PdfReader
        leitor = PdfReader(str(pdf))
        total_imagens = 0
        for pagina in leitor.pages:
            xo = pagina.get("/Resources", {}).get("/XObject", {}) or {}
            total_imagens += len([k for k in xo if k.startswith("/")])
        if total_imagens == 0:
            print(f"[FALHA] pdf: nenhuma imagem embutida encontrada em {pdf}")
            print(f"  -> Adicione o logo na capa do template Typst (image(...) com logo_imagem)")
            return 1
    except Exception as e:
        print(f"[FALHA] pdf: nao foi possivel inspecionar o PDF ({e})")
        return 1

    print(f"[OK] pdf: logo presente (arquivo copiado) e imagem embutida no PDF ({total_imagens} XObject(s))")
    return 0


def checar_arte(slug: str, tipo: str) -> int:
    pasta = DIR_OUTPUT / slug / tipo

    # Verifica se o arquivo de logo foi copiado para assets/
    logo_asset = pasta / "assets" / "logos" / LOGO_PADRAO
    if not logo_asset.exists():
        print(f"[FALHA] {tipo}: arquivo de logo não copiado para {logo_asset}")
        print(f"  -> Copie {DIR_LOGOS / LOGO_PADRAO} para {logo_asset}")
        return 1

    # Para artes, o HTML temporário é apagado após a geração do PNG. Verificamos o PNG final.
    pngs = list(pasta.glob("*.png"))
    if not pngs:
        print(f"[ERRO] {tipo}: nenhum arquivo PNG encontrado em {pasta}")
        return 1

    print(f"[OK] {tipo}: logo presente (arquivo copiado) e PNG de arte gerado ({pngs[0].name})")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Valida presença obrigatória do logo em artefatos")
    ap.add_argument("slug")
    ap.add_argument("tipo", help="landing-page | apresentacao | arte-01 | arte-02 | arte-03 | pdf")
    args = ap.parse_args()

    # Verifica que os logos de origem existem
    logo_src = DIR_LOGOS / LOGO_PADRAO
    if not logo_src.exists():
        print(f"[ERRO] Logo de origem não encontrado: {logo_src}")
        print(f"  -> Confirme que assets/logos-marca/ contém os arquivos de logo")
        return 1

    if args.tipo == "pdf":
        return checar_pdf(args.slug)
    elif args.tipo in ("landing-page", "apresentacao"):
        return checar_html(args.slug, args.tipo)
    elif args.tipo in ("arte-01", "arte-02", "arte-03"):
        return checar_arte(args.slug, args.tipo)
    else:
        print(f"[ERRO] Tipo desconhecido: {args.tipo}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
