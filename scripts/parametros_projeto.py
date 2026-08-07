#!/usr/bin/env python3
"""
Modulo compartilhado: le/valida output/<slug>/config_projeto.json e gera os
pares -V para o Pandoc/Typst (compilador-pdf) a partir do design system.

Desde a rodada de refinamento do design system, a marca NAO e mais extraida por
projeto: landing-page/apresentacao/arte usam sempre brand/design-system-conexao.json
(ver .claude/skills/aplicador-marca-conexao/SKILL.md). O PDF ainda nao tem regras
proprias definidas ("Flex Gold") - por ora, --pdf-vars tambem usa o arquivo fixo
como INTERIM, ate que essas regras especificas sejam desenhadas. Isso e um
faltante conhecido, nao uma decisao final (ver CLAUDE.md).

Uso:
    python scripts/parametros_projeto.py <slug> --validar
    python scripts/parametros_projeto.py <slug> --pdf-vars
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from _tipos_comuns import erros_preset_kit_completo

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
CAMINHO_BRAND = DIR_PROJETO / "brand" / "design-system-conexao.json"

TIPOS_VALIDOS = {"pdf", "landing-page", "apresentacao", "arte-01", "arte-02", "arte-03",
                  "textos", "kit-consultor", "kit-distribuidor"}

# Escolhas do operador nas rodadas 2 e 3 do /esbocar (fonte de verdade — nunca derivar).
PUBLICOS_ALVO_VALIDOS = {"consultores", "clientes", "distribuidores"}
OBJETIVOS_TOM_VALIDOS = {
    "educacional_comercial",
    "informacional_tecnico",
    "comercial_informacional_parceria",
}


def caminho_config(slug):
    return DIR_OUTPUT / slug / "config_projeto.json"


def carregar_json(caminho):
    if not caminho.exists():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def validar_config(slug):
    """Retorna (ok, lista_de_erros)."""
    erros = []
    config = carregar_json(caminho_config(slug))
    if config is None:
        return False, [f"config_projeto.json nao encontrado em {caminho_config(slug).parent}"]

    for campo in ("slug", "texto_base", "imagens", "materiais_selecionados"):
        if campo not in config:
            erros.append(f"campo obrigatorio ausente: {campo}")

    if config.get("slug") != slug:
        erros.append(f"config.slug ({config.get('slug')!r}) nao bate com o slug informado ({slug!r})")

    publico = config.get("publico_alvo")
    if publico not in PUBLICOS_ALVO_VALIDOS:
        erros.append(
            f"publico_alvo invalido ou ausente: {publico!r} - esperado um de "
            f"{sorted(PUBLICOS_ALVO_VALIDOS)} (escolha da rodada 2 do /esbocar)")

    objetivo_tom = config.get("objetivo_tom")
    if objetivo_tom not in OBJETIVOS_TOM_VALIDOS:
        erros.append(
            f"objetivo_tom invalido ou ausente: {objetivo_tom!r} - esperado um de "
            f"{sorted(OBJETIVOS_TOM_VALIDOS)} (escolha da rodada 3 do /esbocar)")

    materiais = config.get("materiais_selecionados", [])
    if not materiais:
        erros.append("materiais_selecionados vazio - pelo menos 1 material precisa ser selecionado")
    for m in materiais:
        if m not in TIPOS_VALIDOS:
            erros.append(f"tipo de material invalido em materiais_selecionados: {m!r}")

    erros += erros_preset_kit_completo(config)

    if "pdf" in materiais:
        if "edicao" not in config or not str(config.get("edicao", "")).strip():
            erros.append("campo 'edicao' de preenchimento obrigatorio quando o material 'pdf' esta selecionado")

    if "elementos_decorativos" in config and not isinstance(config["elementos_decorativos"], bool):
        erros.append("campo 'elementos_decorativos' deve ser booleano (true/false) quando presente")

    imagens = config.get("imagens", [])
    for img in imagens:
        p = DIR_PROJETO / img.get("path", "")
        if img.get("path") and not p.exists():
            erros.append(f"imagem referenciada nao encontrada no disco: {img.get('path')}")

    if "pdf" in materiais and not CAMINHO_BRAND.exists():
        erros.append(f"brand/design-system-conexao.json ausente - necessario mesmo para o PDF (uso interim)")

    return (len(erros) == 0), erros


FONTE_FALLBACK = "Arial"


def fontes_instaladas():
    """Lista de fontes que o Typst local consegue resolver (`typst fonts`).
    Diferente de HTML/CSS, o Typst NAO baixa webfonts - so usa o que esta
    instalado na maquina que compila. Uma fonte do design system (ex.: um
    Google Font auto-hospedado no HTML) pode nao existir aqui e cair num
    fallback SILENCIOSO do Typst, sem erro - por isso este check explicito
    antes de montar as -V."""
    try:
        resultado = subprocess.run(["typst", "fonts"], capture_output=True, text=True, timeout=15)
        return {linha.strip() for linha in resultado.stdout.splitlines() if linha.strip()}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None  # typst nao encontrado - deixa o proprio pandoc/typst reportar o erro depois


def resolver_fonte(nome_desejado, disponiveis):
    if disponiveis is None or nome_desejado in disponiveis:
        return nome_desejado, False
    print(f"[AVISO] fonte '{nome_desejado}' nao instalada para o Typst local - "
          f"usando fallback '{FONTE_FALLBACK}'. Registrar como faltante: instalar a fonte "
          f"da marca na maquina de build ou aprovar o fallback.", file=sys.stderr)
    return FONTE_FALLBACK, True


def vars_pdf(slug):
    """Monta os pares -V chave=valor para o Pandoc/Typst.

    INTERIM: le brand/design-system-conexao.json (o mesmo arquivo fixo usado
    por landing-page/apresentacao/arte) ate que regras proprias de PDF
    ('Flex Gold') sejam desenhadas - ver nota no topo do arquivo."""
    brand = carregar_json(CAMINHO_BRAND)
    if brand is None:
        print(f"[ERRO] {CAMINHO_BRAND} nao encontrado")
        return None

    cores = brand.get("cores", {})
    tipografia = brand.get("tipografia", {})
    disponiveis = fontes_instaladas()
    fonte_titulo, _ = resolver_fonte(tipografia.get("titulo", {}).get("familia", FONTE_FALLBACK), disponiveis)
    fonte_corpo, _ = resolver_fonte(tipografia.get("corpo", {}).get("familia", FONTE_FALLBACK), disponiveis)

    # Recupera a edição do config_projeto.json
    config = carregar_json(caminho_config(slug))
    edicao = config.get("edicao", "1ª Edição") if config else "1ª Edição"

    pares = {
        "cor_primaria": cores.get("accent", "#c9a655"),
        "cor_secundaria": cores.get("textMuted", "#94a3b8"),
        "cor_destaque": cores.get("gradientMid", "#e8d48b"),
        "cor_texto": cores.get("textMain", "#f8fafc"),
        "cor_fundo": cores.get("bg", "#0f172a"),
        "fonte_titulo": fonte_titulo,
        "fonte_corpo": fonte_corpo,
        "edicao": edicao,
    }
    return pares


def main():
    ap = argparse.ArgumentParser(description="Parametros/validacao de config_projeto.json")
    ap.add_argument("slug")
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--pdf-vars", action="store_true")
    args = ap.parse_args()

    if args.validar:
        ok, erros = validar_config(args.slug)
        if ok:
            print(f"[OK] config_projeto.json de {args.slug} valido")
            return 0
        print(f"[ERRO] config_projeto.json de {args.slug} invalido:")
        for e in erros:
            print(f"  - {e}")
        return 1

    if args.pdf_vars:
        pares = vars_pdf(args.slug)
        if pares is None:
            return 1
        for chave, valor in pares.items():
            print(f"-V {chave}={valor}")
        return 0

    print("Nada a fazer - use --validar ou --pdf-vars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
