#!/usr/bin/env python3
"""Peca 3 - gera o esqueleto de um registro declarativo (princicpio Aberto/
Fechado): um dicionario unico por conceito, em vez de `if tipo == ...`
espalhado em varios arquivos.

Uso:
    python registro_declarativo_scaffold.py --conceito tipo_obra \
        --campos rotulo,prefixo_curto --saida caminho/para/tipo_obra.py

Nunca sobrescreve um arquivo existente (Regra do instalador: aditivo, nunca
destrutivo) - se `--saida` ja existir, o script recusa e explica.
"""
import argparse
import sys
from pathlib import Path

TEMPLATE = '''"""Registro declarativo de {conceito!r} (Peca 3 - kit-fundacao-aidd).

Adicionar um {conceito} novo = 1 entrada no dicionario abaixo. Nenhuma funcao
que consome este registro deve ganhar `if {conceito} == "...":` - isso e o
sinal de que um campo ainda esta hardcoded e precisa migrar pra ca.
"""

{registro_var} = {{
    # "chave-exemplo": {{{campos_exemplo}}},
}}


def obter(chave):
    """Levanta KeyError explicito se a chave nao existir no registro."""
    if chave not in {registro_var}:
        raise KeyError(
            f"{{chave!r}} nao esta registrado em {registro_var} - "
            f"adicione uma entrada em vez de tratar como caso especial"
        )
    return {registro_var}[chave]


def listar_chaves():
    return sorted({registro_var}.keys())
'''


def gerar_codigo(conceito, campos):
    campos_exemplo = ", ".join(f'"{c}": "..."' for c in campos) or '"campo": "..."'
    registro_var = conceito.upper() + "S"
    return TEMPLATE.format(
        conceito=conceito,
        campos_exemplo=campos_exemplo,
        registro_var=registro_var,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--conceito", required=True, help="nome do conceito, ex.: tipo_obra")
    ap.add_argument("--campos", default="", help="campos separados por virgula, ex.: rotulo,prefixo")
    ap.add_argument("--saida", required=True, help="caminho do arquivo .py a gerar")
    args = ap.parse_args()

    destino = Path(args.saida)
    if destino.exists():
        print(f"[RECUSADO] {destino} ja existe - nao sobrescrevo. "
              f"Revise manualmente ou escolha outro --saida.")
        sys.exit(1)

    campos = [c.strip() for c in args.campos.split(",") if c.strip()]
    codigo = gerar_codigo(args.conceito, campos)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(codigo, encoding="utf-8")
    print(f"[OK] registro declarativo gerado em {destino}")


if __name__ == "__main__":
    main()
