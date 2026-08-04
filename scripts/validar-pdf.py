#!/usr/bin/env python3
"""
Valida R6 do SPEC.md / SPEC_PDF.md: o PDF da apostila existe, pesa menos de
5 MB, tem texto vetorial extraivel (nao e imagem rasterizada de texto) e tem
contagem de paginas coerente (> 0).

Uso:
    python scripts/validar-pdf.py <slug>
"""

import argparse
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

TETO_BYTES = 5_000_000  # 5 MB


def main():
    ap = argparse.ArgumentParser(description="Valida o PDF final da apostila")
    ap.add_argument("slug")
    args = ap.parse_args()

    base = DIR_OUTPUT / args.slug / "pdf"
    pdfs = sorted(base.glob("*.pdf")) if base.exists() else []
    if not pdfs:
        print(f"[ERRO] nenhum PDF encontrado em {base}")
        return 1
    pdf_path = pdfs[0]

    tamanho = pdf_path.stat().st_size
    if tamanho == 0:
        print(f"[FALHA] {pdf_path.name}: arquivo vazio")
        return 1

    ok = True
    if tamanho >= TETO_BYTES:
        print(f"[FALHA] {pdf_path.name}: {tamanho} bytes, teto e {TETO_BYTES} bytes (5 MB)")
        ok = False
    else:
        print(f"[OK] {pdf_path.name}: {tamanho} bytes (< 5 MB)")

    try:
        from pypdf import PdfReader
    except ImportError:
        print("[ERRO] pypdf nao instalado - rode: pip install pypdf")
        return 1

    reader = PdfReader(str(pdf_path))
    n_paginas = len(reader.pages)
    if n_paginas == 0:
        print(f"[FALHA] {pdf_path.name}: 0 paginas")
        ok = False
    else:
        print(f"[OK] {pdf_path.name}: {n_paginas} pagina(s)")

    texto_total = "".join((p.extract_text() or "") for p in reader.pages)
    if len(texto_total.strip()) < 50:
        print(f"[FALHA] {pdf_path.name}: texto extraivel quase vazio "
              f"({len(texto_total.strip())} caracteres) - PDF pode estar rasterizado")
        ok = False
    else:
        print(f"[OK] {pdf_path.name}: {len(texto_total.strip())} caracteres de texto vetorial extraidos")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
