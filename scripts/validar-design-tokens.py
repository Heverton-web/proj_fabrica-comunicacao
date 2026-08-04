#!/usr/bin/env python3
"""
Confirma fidelidade de marca (REGRA 6 / R5 do SPEC.md): nenhum hex de cor
"solto" fora das variaveis do design system FIXO da Conexão
(brand/design-system-conexao.json) deve aparecer no artefato HTML gerado.

Desde a rodada de refinamento do design system, o arquivo de tokens NAO e mais
gerado por projeto (design_tokens.json) - e um unico arquivo fixo em brand/,
igual para todo material landing-page/apresentacao/arte. Ver
.claude/skills/aplicador-marca-conexao/SKILL.md.

Uso:
    python scripts/validar-design-tokens.py <slug> <tipo>
    # tipo in: landing-page, apresentacao, arte-01, arte-02, arte-03
    # (pdf nao entra aqui - regras de PDF ainda nao definidas nesta rodada;
    #  ver validar-pdf.py para os checks de PDF que ja existem)
"""

import argparse
import json
import re
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
CAMINHO_BRAND = DIR_PROJETO / "brand" / "design-system-conexao.json"

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")


def caminho_html(slug, tipo):
    base = DIR_OUTPUT / slug / tipo
    return base / "index.html"


def cores_da_marca_fixa():
    if not CAMINHO_BRAND.exists():
        print(f"[ERRO] design system fixo nao encontrado em {CAMINHO_BRAND}")
        return None
    brand = json.loads(CAMINHO_BRAND.read_text(encoding="utf-8"))
    return {v.lower() for v in brand.get("cores", {}).values() if isinstance(v, str) and v.startswith("#")}


def main():
    ap = argparse.ArgumentParser(description="Valida fidelidade de cores de marca em um material HTML")
    ap.add_argument("slug")
    ap.add_argument("tipo")
    args = ap.parse_args()

    cores_permitidas = cores_da_marca_fixa()
    if cores_permitidas is None:
        return 1

    html_path = caminho_html(args.slug, args.tipo)
    if not html_path.exists():
        print(f"[ERRO] {html_path} nao encontrado")
        return 1

    conteudo = html_path.read_text(encoding="utf-8", errors="replace")

    # Isola o bloco :root { ... } - hexes ali dentro sao a propria definicao das
    # variaveis de marca, nao "hex solto" fora delas.
    root_match = re.search(r":root\s*\{(.*?)\}", conteudo, re.DOTALL)
    fora_do_root = conteudo
    if root_match:
        fora_do_root = conteudo[:root_match.start()] + conteudo[root_match.end():]

    hexes_fora = {h.lower() for h in HEX_RE.findall(fora_do_root)}
    hexes_nao_autorizados = hexes_fora - cores_permitidas

    if hexes_nao_autorizados:
        print(f"[FALHA] {args.tipo}: hex fora das variaveis de marca encontrados: "
              f"{sorted(hexes_nao_autorizados)}")
        print("  -> Troque por var(--*) definidas a partir de brand/design-system-conexao.json")
        return 1

    print(f"[OK] {args.tipo}: nenhuma cor fora do design system fixo encontrada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
