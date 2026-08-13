#!/usr/bin/env python3
"""Peca 5 - converte um bloco de postmortem (formato templates/POSTMORTEM.md)
em um stub de teste de regressao. Nunca sobrescreve um arquivo de teste
existente.

Uso:
    python postmortem_para_teste.py --titulo "cheatsheet vazio" \
        --prevencao "agregacao nunca pode nascer vazia com campos minimos" \
        --saida tests/test_regressao_cheatsheet_vazio.py
"""
import argparse
import re
import sys
from pathlib import Path

TEMPLATE = '''"""Regressao: {titulo}.

Prevencao (do postmortem): {prevencao}
Gerado por kit-fundacao-aidd/scripts/postmortem_para_teste.py - preencha o
corpo do teste com o cenario real antes de considerar concluido.
"""


def test_{slug}():
    # TODO: reproduza o cenario real do bug e assert o comportamento correto
    # descrito na linha de Prevencao acima.
    raise NotImplementedError(
        "preencha o corpo deste teste de regressao antes de commitar"
    )
'''


def slugificar(titulo):
    slug = re.sub(r"[^a-z0-9]+", "_", titulo.lower()).strip("_")
    return slug or "sem_titulo"


def gerar_stub(titulo, prevencao):
    return TEMPLATE.format(titulo=titulo, prevencao=prevencao, slug=slugificar(titulo))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--prevencao", required=True)
    ap.add_argument("--saida", required=True)
    args = ap.parse_args()

    destino = Path(args.saida)
    if destino.exists():
        print(f"[RECUSADO] {destino} ja existe - nao sobrescrevo. "
              f"Revise manualmente ou escolha outro --saida.")
        sys.exit(1)

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_stub(args.titulo, args.prevencao), encoding="utf-8")
    print(f"[OK] stub de teste gerado em {destino} - contem NotImplementedError "
          f"de proposito, preencha antes de commitar (nao conta como suite verde)")


if __name__ == "__main__":
    main()
