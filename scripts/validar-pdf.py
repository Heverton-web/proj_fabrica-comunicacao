#!/usr/bin/env python3
"""
Valida R6 do SPEC.md / SPEC_PDF.md: o PDF da apostila existe, pesa menos de
5 MB, tem texto vetorial extraivel (nao e imagem rasterizada de texto) e tem
contagem de paginas coerente (> 0).

Uso:
    python scripts/validar-pdf.py <slug>
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

TETO_BYTES = 5_000_000  # 5 MB

STOPWORDS = {
    "para", "com", "uma", "que", "tem", "dos", "das", "mais", "não", "sobre",
    "como", "pelo", "pela", "todo", "toda", "este", "esta", "são", "ser",
    "foi", "seu", "sua", "seus", "suas", "cada", "após", "quando", "onde",
    "entre", "também", "porém", "sem", "já", "até", "mas", "essa", "esse",
    "num", "numa", "nesse", "nessa", "nisso",
}


def _normalizar(texto):
    nfkd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def _palavras_significativas(texto):
    palavras = set()
    for p in _normalizar(texto).split():
        p = p.strip(".,;:!?()[]{}\"'-\u201c\u201d\u2018\u2019")
        if len(p) >= 4 and p not in STOPWORDS:
            palavras.add(p)
    return palavras


def _agrupar_linhas(spans):
    spans_ord = sorted(spans, key=lambda s: (s["bbox"][1], s["bbox"][0]))
    linhas = []
    atual = None
    for s in spans_ord:
        if atual is None or abs(s["bbox"][1] - atual["y"]) > 2:
            if atual:
                linhas.append(atual)
            atual = {"y": s["bbox"][1], "texto": s["texto"]}
        else:
            atual["texto"] += " " + s["texto"]
    if atual:
        linhas.append(atual)
    return linhas


def _bbox_uniao(bboxes):
    bboxes = list(bboxes)
    if not bboxes:
        return None
    return [
        min(b[0] for b in bboxes),
        min(b[1] for b in bboxes),
        max(b[2] for b in bboxes),
        max(b[3] for b in bboxes),
    ]


def validar_capa(pdf_path, texto_base_path):
    """SPEC_PDF (endurecimento): a capa deve ter titulo tematico em no maximo
    2 linhas, sem linha com uma unica palavra isolada, com impressao de bloco
    quadrado; paragrafo da capa em bloco quadrado, sem palavra isolada; titulo
    remete ao tema do texto-base (>= 2 palavras significativas em comum) e nao
    usa o rotulo generico 'Guia de Treinamento'."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("[AVISO] PyMuPDF (fitz) nao instalado - pulando checagens de capa")
        return True

    doc = fitz.open(str(pdf_path))
    spans = []
    texto_capa = doc[0].get_text("dict")
    if isinstance(texto_capa, dict):
        for bloco in texto_capa.get("blocks", []):
            if not isinstance(bloco, dict):
                continue
            for linha in bloco.get("lines", []):
                for span in linha.get("spans", []):
                    texto = span["text"].strip()
                    if texto:
                        spans.append({"texto": texto, "size": span["size"], "bbox": span["bbox"]})
    doc.close()

    if not spans:
        print("[AVISO] nenhum span extraido da capa - pulando checagens de capa")
        return True

    spans_titulo = [s for s in spans if s["size"] >= 18]
    spans_paragrafo = [s for s in spans if 9.0 <= s["size"] <= 16.5]

    ok = True

    # ── 1) Título da capa ──────────────────────────────────────────────
    if not spans_titulo:
        print("[FALHA] capa sem titulo (nenhum span >= 18pt)")
        ok = False
    else:
        linhas_titulo = _agrupar_linhas(spans_titulo)
        n_linhas = len(linhas_titulo)
        if n_linhas > 2:
            print(f"[FALHA] titulo da capa com {n_linhas} linhas (max: 2)")
            ok = False
        else:
            print(f"[OK] titulo da capa com {n_linhas} linha(s)")
        for i, linha in enumerate(linhas_titulo, 1):
            if len(linha["texto"].split()) == 1:
                print(f"[FALHA] linha {i} do titulo com 1 palavra isolada: '{linha['texto']}'")
                ok = False
        bbox = _bbox_uniao(s["bbox"] for s in spans_titulo)
        if bbox:
            altura = bbox[3] - bbox[1]
            largura = bbox[2] - bbox[0]
            if largura > 0 and altura / largura < 0.18:
                print(f"[FALHA] titulo nao forma bloco (largura {largura:.0f}pt x altura {altura:.0f}pt)")
                ok = False
        titulo_texto = " ".join(l["texto"] for l in linhas_titulo)
        if "guia de treinamento" in _normalizar(titulo_texto):
            print("[FALHA] titulo da capa usa rotulo generico 'Guia de Treinamento' (deve remeter ao tema)")
            ok = False
        if texto_base_path.exists():
            base = texto_base_path.read_text(encoding="utf-8", errors="ignore")
            comuns = _palavras_significativas(titulo_texto) & _palavras_significativas(base)
            if len(comuns) < 2:
                print(f"[FALHA] titulo nao remete ao tema do texto-base ({len(comuns)} palavra(s) em comum, min: 2)")
                ok = False
            else:
                print(f"[OK] titulo remete ao tema do texto-base ({len(comuns)} palavras em comum)")
        else:
            print("[AVISO] texto-mae.txt nao encontrado - pulando checagem de tema")

    # ── 2) Parágrafo da capa ───────────────────────────────────────────
    if not spans_paragrafo:
        print("[FALHA] capa sem paragrafo de apoio (nenhum span 9-16.5pt)")
        ok = False
    else:
        linhas_par = _agrupar_linhas(spans_paragrafo)
        if len(linhas_par) < 2:
            print(f"[FALHA] paragrafo da capa com {len(linhas_par)} linha(s) (min: 2)")
            ok = False
        for i, linha in enumerate(linhas_par, 1):
            if len(linha["texto"].split()) == 1:
                print(f"[FALHA] linha {i} do paragrafo da capa com 1 palavra isolada: '{linha['texto']}'")
                ok = False
        bbox = _bbox_uniao(s["bbox"] for s in spans_paragrafo)
        if bbox:
            altura = bbox[3] - bbox[1]
            largura = bbox[2] - bbox[0]
            if largura > 0:
                prop = altura / largura
                # Paragrafo de capa em bloco: 3+ linhas (~0.15) ate texto alto
                # demais (1.2). Um fiapo de 1-2 linhas (prop < 0.12) reprova.
                if not (0.12 <= prop <= 1.2):
                    print(f"[FALHA] paragrafo da capa fora do bloco (prop {prop:.2f}, esperado em [0.12, 1.2])")
                    ok = False
    return ok


def main():
    ap = argparse.ArgumentParser(description="Valida o PDF final da apostila")
    ap.add_argument("slug")
    ap.add_argument("--pasta", default="pdf",
                     help="pasta em output/<slug>/ a validar (default: 'pdf'; use "
                          "'pdf-v2', 'pdf-v3'... para validar uma regeneracao - ver "
                          "REGRA 11 do AGENTS.md)")
    args = ap.parse_args()

    base = DIR_OUTPUT / args.slug / args.pasta
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

    # SPEC_PDF (endurecimento): capa tematica em bloco quadrado, titulo <= 2
    # linhas sem palavra isolada, paragrafo em bloco sem palavra isolada
    #
    # texto_base e lido de config_projeto.json (fonte de verdade do /esbocar) -
    # nunca hardcoded como "texto-mae.txt", pois /gerar-<material> pode trocar o
    # texto-base do projeto para um novo arquivo (ex.: texto-mae-02.txt).
    texto_base_path = DIR_OUTPUT / args.slug / "insumos" / "texto-mae.txt"
    config_path = DIR_OUTPUT / args.slug / "config_projeto.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            texto_base_config = config.get("texto_base")
            if texto_base_config:
                texto_base_path = DIR_PROJETO / texto_base_config
        except Exception:
            pass

    if not validar_capa(pdf_path, texto_base_path):
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
