#!/usr/bin/env python3
"""
Valida a estrutura de um Kit do Consultor / Kit Distribuidor (ver SPEC_KITS.md):
5 pastas de tom, cada uma com exatamente 2 subpastas arte-01/arte-02, cada uma
com exatamente 1 PNG 1080x1350 (pixel-perfect, < 1 MB), 1 conteudo.json nao
vazio e 1 texto_whatsapp.txt nao vazio em UTF-8. Total esperado por kit: 10
PNGs + 10 conteudo.json + 10 texto_whatsapp.txt.

Uso:
    python scripts/validar-kit.py <slug> kit-consultor
    python scripts/validar-kit.py <slug> kit-distribuidor
"""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from _arte_common import checar_um_badge_por_peca

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

DIMENSAO_ESPERADA = (1080, 1350)
TETO_BYTES = 1_000_000  # 1 MB, mesmo teto de SPEC_ARTE.md

TONS_PASTAS = [
    "artes-informativas",
    "artes-contra-intuitivas",
    "artes-tecnicas",
    "artes-efeito-uau",
    "artes-educativas",
]
ITENS_POR_TOM = ["arte-01", "arte-02"]


def main():
    ap = argparse.ArgumentParser(description="Valida a estrutura de um Kit do Consultor/Distribuidor")
    ap.add_argument("slug")
    ap.add_argument("kit", choices=["kit-consultor", "kit-distribuidor"])
    ap.add_argument("--pasta", default=None,
                     help="pasta em output/<slug>/ a validar (default: o proprio "
                          "<kit>; use '<kit>-v2', '-v3'... para validar uma "
                          "regeneracao - ver REGRA 11 do AGENTS.md)")
    args = ap.parse_args()
    pasta = args.pasta or args.kit

    try:
        from PIL import Image
    except ImportError:
        print("[ERRO] Pillow nao instalado - rode: pip install Pillow")
        return 1

    kit_dir = DIR_OUTPUT / args.slug / pasta
    if not kit_dir.is_dir():
        print(f"[ERRO] pasta do kit nao encontrada: {kit_dir}")
        return 1

    ok = True
    total_pngs = total_conteudos = total_textos = 0

    for tom_pasta in TONS_PASTAS:
        pasta_tom = kit_dir / tom_pasta
        if not pasta_tom.is_dir():
            print(f"[FALHA] {args.kit}: pasta de tom ausente: {tom_pasta}")
            ok = False
            continue

        for item in ITENS_POR_TOM:
            pasta_item = pasta_tom / item
            rotulo = f"{args.kit}/{tom_pasta}/{item}"

            if not pasta_item.is_dir():
                print(f"[FALHA] {rotulo}: pasta ausente")
                ok = False
                continue

            pngs = sorted(pasta_item.glob("*.png"))
            if len(pngs) != 1:
                print(f"[FALHA] {rotulo}: {len(pngs)} PNG(s) encontrado(s), esperado exatamente 1")
                ok = False
            else:
                png = pngs[0]
                tamanho_bytes = png.stat().st_size
                with Image.open(png) as im:
                    dimensao = im.size
                if dimensao != DIMENSAO_ESPERADA:
                    print(f"[FALHA] {rotulo}: {png.name} dimensao {dimensao}, "
                          f"esperado {DIMENSAO_ESPERADA}")
                    ok = False
                elif tamanho_bytes >= TETO_BYTES:
                    print(f"[FALHA] {rotulo}: {png.name} {tamanho_bytes} bytes, "
                          f"teto e {TETO_BYTES} bytes")
                    ok = False
                else:
                    total_pngs += 1

            conteudo = pasta_item / "conteudo.json"
            if not conteudo.exists() or conteudo.stat().st_size == 0:
                print(f"[FALHA] {rotulo}: conteudo.json ausente ou vazio")
                ok = False
            else:
                total_conteudos += 1

            texto = pasta_item / "texto_whatsapp.txt"
            if not texto.exists() or texto.stat().st_size == 0:
                print(f"[FALHA] {rotulo}: texto_whatsapp.txt ausente ou vazio")
                ok = False
            else:
                try:
                    texto.read_text(encoding="utf-8")
                    total_textos += 1
                except UnicodeDecodeError:
                    print(f"[FALHA] {rotulo}: texto_whatsapp.txt nao esta em UTF-8 valido")
                    ok = False

    if ok:
        print(f"[OK] {args.kit}: {total_pngs} PNGs, {total_conteudos} conteudo.json, "
              f"{total_textos} texto_whatsapp.txt (10 esperados de cada)")

    # SPEC_KITS (endurecimento): 1 badge por peca (somente o CTA pill)
    ok_badges, mensagens = checar_um_badge_por_peca(kit_dir, args.kit)
    for msg in mensagens:
        print(msg)
    if not ok_badges:
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
