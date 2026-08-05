#!/usr/bin/env python3
"""
Guarda-corpo estrutural (Fase 2 do plano de acao / relatorio 01): garante que todo
tipo de material em TIPOS_VALIDOS esteja presente em TODAS as camadas do pipeline —
entrevista, dispatcher, skill de redacao, subagente produtor e validador tecnico.

Existe porque o material "textos" ficou, por 2 commits inteiros, funcional em todas as
camadas MENOS na entrevista (.claude/commands/esbocar.md), tornando-o estruturalmente
inatingivel por qualquer operador. Este script torna essa classe de lacuna detectavel
antes da producao real de um projeto, nao depois.

Uso:
    python scripts/verificar-consistencia-pipeline.py [--estrito]

Exit code 0 = tudo consistente. Exit code 1 = pelo menos uma lacuna encontrada
(sempre nao-zero com --estrito; sem --estrito so avisa e retorna 0 mesmo com lacunas,
para uso exploratorio).
"""

import argparse
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_AGENTS = DIR_PROJETO / ".claude" / "agents"
DIR_SKILLS = DIR_PROJETO / ".claude" / "skills"
DIR_SCRIPTS = DIR_PROJETO / "scripts"
CAMINHO_ESBOCAR = DIR_PROJETO / ".claude" / "commands" / "esbocar.md"
CAMINHO_PRODUZIR = DIR_PROJETO / ".claude" / "commands" / "produzir-comunicacao-completa.md"

# Fonte de verdade dos tipos validos: os proprios scripts de validacao/auditoria.
TIPOS_VALIDOS = {"pdf", "landing-page", "apresentacao", "arte-01", "arte-02", "arte-03", "textos"}

# Mapeamento tipo -> o que cada camada precisa conter/ter, para permitir nomes
# nao-uniformes (ex.: arte-01/02/03 compartilham 1 skill e 1 validador).
MAPA_ESBOCAR = {
    "pdf": "PDF (apostila)",
    "landing-page": "Landing Page",
    "apresentacao": "Apresenta",  # cobre "Apresentação"/"Apresentacao"
    "arte-01": "1080×1080",
    "arte-02": "1080×1350",
    "arte-03": "1080×1920",
    "textos": "Textos de Apoio",
}

MAPA_DISPATCH = {
    "pdf": "subagente-produtor-pdf",
    "landing-page": "subagente-produtor-landing",
    "apresentacao": "subagente-produtor-apresentacao",
    "arte-01": "subagente-produtor-arte",
    "arte-02": "subagente-produtor-arte",
    "arte-03": "subagente-produtor-arte",
    "textos": "subagente-produtor-textos",
}

MAPA_SKILL = {
    "pdf": "redator-apostila",
    "landing-page": "redator-landing",
    "apresentacao": "redator-apresentacao",
    "arte-01": "redator-arte",
    "arte-02": "redator-arte",
    "arte-03": "redator-arte",
    "textos": "redator-textos",
}

MAPA_AGENTE = {
    "pdf": "subagente-produtor-pdf.md",
    "landing-page": "subagente-produtor-landing.md",
    "apresentacao": "subagente-produtor-apresentacao.md",
    "arte-01": "subagente-produtor-arte.md",
    "arte-02": "subagente-produtor-arte.md",
    "arte-03": "subagente-produtor-arte.md",
    "textos": "subagente-produtor-textos.md",
}

MAPA_VALIDADOR = {
    "pdf": "validar-pdf.py",
    "landing-page": "validar-html.py",
    "apresentacao": "validar-html.py",
    "arte-01": "validar-dimensoes.py",
    "arte-02": "validar-dimensoes.py",
    "arte-03": "validar-dimensoes.py",
    "textos": "validar-textos.py",
}


def carregar_texto(caminho):
    if not caminho.exists():
        return None
    return caminho.read_text(encoding="utf-8")


def verificar():
    problemas = []

    texto_esbocar = carregar_texto(CAMINHO_ESBOCAR)
    texto_produzir = carregar_texto(CAMINHO_PRODUZIR)

    if texto_esbocar is None:
        problemas.append(f"CRITICO: {CAMINHO_ESBOCAR} nao encontrado.")
    if texto_produzir is None:
        problemas.append(f"CRITICO: {CAMINHO_PRODUZIR} nao encontrado.")

    for tipo in sorted(TIPOS_VALIDOS):
        # (a) opcao na entrevista /esbocar
        if texto_esbocar is not None:
            marcador = MAPA_ESBOCAR.get(tipo, tipo)
            if marcador not in texto_esbocar:
                problemas.append(
                    f"[{tipo}] nao encontrado em esbocar.md (Passo 4) - operador "
                    f"nunca conseguira selecionar este material via /esbocar."
                )

        # (b) entrada no dispatch de producao
        if texto_produzir is not None:
            agente_dispatch = MAPA_DISPATCH.get(tipo)
            if agente_dispatch and agente_dispatch not in texto_produzir:
                problemas.append(
                    f"[{tipo}] nao encontrado no dispatch de "
                    f"produzir-comunicacao-completa.md - material selecionavel mas "
                    f"nunca sera despachado para producao."
                )

        # (c) skill redator-*
        skill = MAPA_SKILL.get(tipo)
        if skill and not (DIR_SKILLS / skill / "SKILL.md").exists():
            problemas.append(f"[{tipo}] skill '{skill}/SKILL.md' nao encontrada.")

        # (d) agente subagente-produtor-*
        agente = MAPA_AGENTE.get(tipo)
        if agente and not (DIR_AGENTS / agente).exists():
            problemas.append(f"[{tipo}] agente '.claude/agents/{agente}' nao encontrado.")

        # (e) validador tecnico
        validador = MAPA_VALIDADOR.get(tipo)
        if validador and not (DIR_SCRIPTS / validador).exists():
            problemas.append(f"[{tipo}] validador 'scripts/{validador}' nao encontrado.")

    return problemas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estrito", action="store_true",
                     help="retorna exit code 1 se qualquer lacuna for encontrada")
    args = ap.parse_args()

    problemas = verificar()

    print(f"VERIFICACAO DE CONSISTENCIA DO PIPELINE - {len(TIPOS_VALIDOS)} tipo(s) de material")
    print("=" * 70)

    if not problemas:
        print("[OK] Todos os tipos de material estao presentes em todas as camadas "
              "(entrevista, dispatch, skill, agente, validador).")
        return 0

    for p in problemas:
        print(f"  - {p}")

    print("=" * 70)
    print(f"VEREDITO: {len(problemas)} lacuna(s) encontrada(s)")

    if args.estrito:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
