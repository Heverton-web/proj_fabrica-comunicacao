#!/usr/bin/env python3
"""
Pre-flight de compatibilidade de slug (Fase 3 do plano de acao / relatorio 01):
roda ANTES do fan-out de producao para detectar, de uma so vez, se algum
scripts/compilar-*.py tem string de OUTRO projeto hardcoded — em vez de deixar cada
subagente-produtor-*/subagente-revisor-marca descobrir o mesmo problema de forma
redundante durante a execucao real (foi o que aconteceu com o bug do path de imagem
"kit_start_flex_frontal.png" encontrado 3+ vezes de forma independente).

Heuristica: para o <slug> alvo, qualquer OUTRO slug ja existente em output/ que
apareca como string literal dentro de scripts/compilar-*.py e um sinal forte de
hardcoding especifico de projeto que nao vai generalizar.

Uso:
    python scripts/preflight-compatibilidade-slug.py <slug> [--estrito]

Exit code 0 = nenhum hardcoding suspeito encontrado (ou aviso, sem --estrito).
Exit code 1 = hardcoding suspeito encontrado com --estrito.
"""

import argparse
import re
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
DIR_SCRIPTS = DIR_PROJETO / "scripts"

COMPILADORES = ["compilar-html.py", "compilar-arte.py", "compilar-pdf.py"]


def outros_slugs(slug_atual):
    if not DIR_OUTPUT.exists():
        return []
    return sorted(
        p.name for p in DIR_OUTPUT.iterdir()
        if p.is_dir() and p.name != slug_atual
    )


def verificar(slug_atual):
    achados = []
    slugs_alheios = outros_slugs(slug_atual)
    variantes_alheias = set()
    for s in slugs_alheios:
        variantes_alheias.add(s)                 # kit-start-flex
        variantes_alheias.add(s.replace("-", "_"))  # kit_start_flex

    for nome in COMPILADORES:
        caminho = DIR_SCRIPTS / nome
        if not caminho.exists():
            continue
        texto = caminho.read_text(encoding="utf-8")
        for i, linha in enumerate(texto.splitlines(), start=1):
            for variante in variantes_alheias:
                eh_fallback_documentado = (
                    "fallback" in linha.lower() or "legado" in linha.lower()
                )
                if variante in linha and not eh_fallback_documentado:
                    achados.append(
                        f"{nome}:{i}: referencia literal a outro projeto ({variante!r}) "
                        f"fora de um comentario de fallback documentado -> {linha.strip()[:100]}"
                    )

    return achados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--estrito", action="store_true",
                     help="retorna exit code 1 se qualquer hardcoding suspeito for encontrado")
    args = ap.parse_args()

    achados = verificar(args.slug)

    print(f"PRE-FLIGHT DE COMPATIBILIDADE DE SLUG - {args.slug}")
    print("=" * 70)

    if not achados:
        print("[OK] Nenhum hardcoding de outro projeto encontrado em "
              "scripts/compilar-*.py. Fan-out de producao liberado.")
        return 0

    for a in achados:
        print(f"  - {a}")

    print("=" * 70)
    print(f"AVISO: {len(achados)} referencia(s) suspeita(s) a outro projeto encontrada(s) "
          f"nos compiladores compartilhados. Isso pode indicar que o compilador nao "
          f"generaliza para o slug '{args.slug}' (mesma causa raiz do bug de path de "
          f"imagem hardcoded corrigido em compilar-html.py/compilar-arte.py/compilar-pdf.py).")

    if args.estrito:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
