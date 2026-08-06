#!/usr/bin/env python3
"""
Valida R8 do SPEC.md: cada arte PNG precisa ter dimensao pixel-perfect exata e
ficar abaixo do teto de peso da variante (ver SPEC_ARTE.md).

Uso:
    python scripts/validar-dimensoes.py <slug> <variante>
    # variante in: arte-01, arte-02, arte-03
"""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from _arte_common import checar_um_badge_por_peca

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

DIMENSOES = {
    "arte-01": (1080, 1080),
    "arte-02": (1080, 1350),
    "arte-03": (1080, 1920),
}
TETO_BYTES = 1_000_000  # 1 MB


def main():
    ap = argparse.ArgumentParser(description="Valida dimensao exata e peso de uma arte PNG")
    ap.add_argument("slug")
    ap.add_argument("variante", choices=sorted(DIMENSOES))
    args = ap.parse_args()

    largura_esperada, altura_esperada = DIMENSOES[args.variante]
    base = DIR_OUTPUT / args.slug / args.variante
    pngs = sorted(base.glob("*.png")) if base.exists() else []

    if not pngs:
        print(f"[ERRO] nenhum PNG encontrado em {base}")
        return 1

    if len(pngs) != 3:
        print(f"[FALHA] {args.variante}: {len(pngs)} PNG(s) encontrado(s), esperado "
              f"exatamente 3 (1 por copy — ver docs/05-plano-expansao-multi-copy-arte.md)")
        return 1

    try:
        from PIL import Image
    except ImportError:
        print("[ERRO] Pillow nao instalado - rode: pip install Pillow")
        return 1

    ok = True
    for png in pngs:
        tamanho_bytes = png.stat().st_size
        with Image.open(png) as im:
            largura, altura = im.size

        if (largura, altura) != (largura_esperada, altura_esperada):
            print(f"[FALHA] {png.name}: dimensao {largura}x{altura}, esperado "
                  f"{largura_esperada}x{altura_esperada}")
            ok = False
        if tamanho_bytes >= TETO_BYTES:
            print(f"[FALHA] {png.name}: {tamanho_bytes} bytes, teto e {TETO_BYTES} bytes")
            ok = False
        if (largura, altura) == (largura_esperada, altura_esperada) and tamanho_bytes < TETO_BYTES:
            print(f"[OK] {png.name}: {largura}x{altura}, {tamanho_bytes} bytes")

    # SPEC_ARTE (endurecimento): 1 badge por peca (somente o CTA pill)
    ok_badges, mensagens = checar_um_badge_por_peca(base, args.variante)
    for msg in mensagens:
        print(msg)
    if not ok_badges:
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
