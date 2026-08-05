#!/usr/bin/env python3
"""
Valida que os textos de redes sociais (WhatsApp, Instagram, LinkedIn) do projeto
foram gerados, salvos em arquivos .txt na pasta textos/ e possuem codificação UTF-8 válida.

Uso:
    python scripts/validar-textos.py <slug>
"""

import argparse
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"


def main():
    ap = argparse.ArgumentParser(description="Valida os textos de cópias do projeto")
    ap.add_argument("slug")
    args = ap.parse_args()

    pasta = DIR_OUTPUT / args.slug / "textos"
    if not pasta.exists():
        print(f"[ERRO] Pasta de textos não encontrada: {pasta}")
        return 1

    arquivos = ["whatsapp.txt", "instagram.txt", "linkedin.txt"]
    
    erros = []
    for nome in arquivos:
        caminho = pasta / nome
        if not caminho.exists():
            erros.append(f"arquivo ausente: {nome}")
            continue

        # Verifica tamanho
        if caminho.stat().st_size == 0:
            erros.append(f"arquivo vazio: {nome}")
            continue

        # Verifica codificação UTF-8
        try:
            texto = caminho.read_text(encoding="utf-8")
            if not texto.strip():
                erros.append(f"arquivo contém apenas espaço em branco: {nome}")
        except UnicodeDecodeError:
            erros.append(f"arquivo não está codificado em UTF-8: {nome}")

    if erros:
        print(f"[FALHA] textos: ocorreram os seguintes erros na validação:")
        for err in erros:
            print(f"  - {err}")
        return 1

    print(f"[OK] textos: todos os 3 arquivos (.txt) existem, possuem conteúdo e estão em UTF-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
