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
from _arte_common import checar_um_badge_por_peca, checar_paragrafo_arte

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
    ap.add_argument("--pasta", default=None,
                     help="pasta em output/<slug>/ a validar (default: a propria "
                          "<variante>; use '<variante>-v2', '-v3'... para validar uma "
                          "regeneracao - ver REGRA 11 do AGENTS.md)")
    args = ap.parse_args()
    pasta = args.pasta or args.variante

    largura_esperada, altura_esperada = DIMENSOES[args.variante]
    base = DIR_OUTPUT / args.slug / pasta
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

    # SPEC_ARTE (endurecimento): paragrafo em >= 3 linhas, sem linha orfa
    ok_paragrafo, mensagens_paragrafo = checar_paragrafo_arte(base, args.variante)
    for msg in mensagens_paragrafo:
        print(msg)
    if not ok_paragrafo:
        ok = False

    # SPEC_ARTE: 9 legendas de publicacao (3 copies x 3 canais), format-agnosticas,
    # gravadas em output/<slug>/arte/ (nao dentro da pasta do formato).
    dir_arte = DIR_OUTPUT / args.slug / "arte"
    canais = ("instagram", "linkedin", "whatsapp")
    legendas_ausentes = []
    for indice in range(1, 4):
        sufixo_copy = f"copy{indice:02d}"
        for canal in canais:
            legenda = dir_arte / f"legenda_{sufixo_copy}_{canal}.txt"
            if not legenda.exists() or legenda.stat().st_size == 0:
                legendas_ausentes.append(legenda.name)
    if legendas_ausentes:
        ok = False
        print(f"[FALHA] arte: {len(legendas_ausentes)} legenda(s) ausente(s)/vazia(s) "
              f"em {dir_arte}: {', '.join(legendas_ausentes)}")
    else:
        print(f"[OK] arte: 9 legendas de publicacao presentes em {dir_arte}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
