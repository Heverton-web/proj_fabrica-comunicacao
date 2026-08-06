#!/usr/bin/env python3
"""
Guarda-corpo estrutural (Fase 2 do plano de acao / relatorio 01): garante que todo
tipo de material em TIPOS_VALIDOS esteja presente em TODAS as camadas do pipeline —
entrevista, dispatcher, skill de redacao, subagente produtor e validador tecnico.

Existe porque o material "textos" ficou, por 2 commits inteiros, funcional em todas as
camadas MENOS na entrevista (originalmente .claude/commands/esbocar.md, hoje
SPEC_COMANDOS.md -- ver abaixo), tornando-o estruturalmente inatingivel por qualquer
operador. Este script torna essa classe de lacuna detectavel antes da producao real
de um projeto, nao depois.

Checa SPEC_COMANDOS.md (fonte unica de verdade, universal a qualquer harness) para as
camadas de entrevista/dispatch -- nao mais .claude/commands/*.md, que desde a
universalizacao dos comandos sao so ponteiros finos sem o texto completo (ver
AGENTS.md, secao sobre comandos universais).

Uso:
    python scripts/verificar-consistencia-pipeline.py [--estrito]

Exit code 0 = tudo consistente. Exit code 1 = pelo menos uma lacuna encontrada
(sempre nao-zero com --estrito; sem --estrito so avisa e retorna 0 mesmo com lacunas,
para uso exploratorio).
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from _tipos_comuns import PRESETS_KIT_COMPLETO

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_AGENTS = DIR_PROJETO / ".claude" / "agents"
DIR_SKILLS = DIR_PROJETO / ".claude" / "skills"
DIR_SCRIPTS = DIR_PROJETO / "scripts"
CAMINHO_ESBOCAR = DIR_PROJETO / "SPEC_COMANDOS.md"
CAMINHO_PRODUZIR = DIR_PROJETO / "SPEC_COMANDOS.md"

# Fonte de verdade dos tipos validos: os proprios scripts de validacao/auditoria.
TIPOS_VALIDOS = {"pdf", "landing-page", "apresentacao", "arte-01", "arte-02", "arte-03",
                  "textos", "kit-consultor", "kit-distribuidor"}

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
    "kit-consultor": "Kit do Consultor",
    "kit-distribuidor": "Kit Distribuidor",
}

MAPA_DISPATCH = {
    "pdf": "subagente-produtor-pdf",
    "landing-page": "subagente-produtor-landing",
    "apresentacao": "subagente-produtor-apresentacao",
    "arte-01": "subagente-produtor-arte",
    "arte-02": "subagente-produtor-arte",
    "arte-03": "subagente-produtor-arte",
    "textos": "subagente-produtor-textos",
    "kit-consultor": "subagente-produtor-kit",
    "kit-distribuidor": "subagente-produtor-kit",
}

MAPA_SKILL = {
    "pdf": "redator-apostila",
    "landing-page": "redator-landing",
    "apresentacao": "redator-apresentacao",
    "arte-01": "redator-arte",
    "arte-02": "redator-arte",
    "arte-03": "redator-arte",
    "textos": "redator-textos",
    "kit-consultor": "redator-kit-copy",
    "kit-distribuidor": "redator-kit-copy",
}

MAPA_AGENTE = {
    "pdf": "subagente-produtor-pdf.md",
    "landing-page": "subagente-produtor-landing.md",
    "apresentacao": "subagente-produtor-apresentacao.md",
    "arte-01": "subagente-produtor-arte.md",
    "arte-02": "subagente-produtor-arte.md",
    "arte-03": "subagente-produtor-arte.md",
    "textos": "subagente-produtor-textos.md",
    "kit-consultor": "subagente-produtor-kit.md",
    "kit-distribuidor": "subagente-produtor-kit.md",
}

MAPA_VALIDADOR = {
    "pdf": "validar-pdf.py",
    "landing-page": "validar-html.py",
    "apresentacao": "validar-html.py",
    "arte-01": "validar-dimensoes.py",
    "arte-02": "validar-dimensoes.py",
    "arte-03": "validar-dimensoes.py",
    "textos": "validar-textos.py",
    "kit-consultor": "validar-kit.py",
    "kit-distribuidor": "validar-kit.py",
}


def carregar_texto(caminho):
    if not caminho.exists():
        return None
    return caminho.read_text(encoding="utf-8")


def extrair_secao(texto, titulo):
    """Conteudo da secao '## <titulo>' ate a proxima secao '## ' (headers
    '### '/'#### ' nao quebram a secao). Retorna None se texto/titulo ausentes."""
    if texto is None or titulo not in texto:
        return None
    for parte in re.split(r"(?m)^## ", texto):
        if parte.startswith(titulo[3:]):
            return parte
    return None


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
                    f"[{tipo}] nao encontrado em SPEC_COMANDOS.md (secao /esbocar, "
                    f"Passo 4) - operador nunca conseguira selecionar este material "
                    f"via /esbocar."
                )

        # (b) entrada no dispatch de producao
        if texto_produzir is not None:
            agente_dispatch = MAPA_DISPATCH.get(tipo)
            if agente_dispatch and agente_dispatch not in texto_produzir:
                problemas.append(
                    f"[{tipo}] nao encontrado em SPEC_COMANDOS.md (secao "
                    f"/produzir-comunicacao-completa, dispatch) - material "
                    f"selecionavel mas nunca sera despachado para producao."
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

    # Comandos /kit-completo-<publico>: presenca das 3 secoes, presets dentro de
    # TIPOS_VALIDOS (fonte unica: _tipos_comuns) e dispatch completo na secao
    # canonica (/kit-completo-consultor) — as variantes a referenciam.
    if texto_produzir is not None:
        for comando in ("/kit-completo-consultor", "/kit-completo-distribuidor",
                        "/kit-completo-cliente"):
            if comando not in texto_produzir:
                problemas.append(
                    f"[{comando}] secao nao encontrada em SPEC_COMANDOS.md - "
                    f"comando universal inexistente."
                )

        for preset, esperado in sorted(PRESETS_KIT_COMPLETO.items()):
            invalidos = [m for m in esperado["materiais"] if m not in TIPOS_VALIDOS]
            if invalidos:
                problemas.append(
                    f"[kit-completo-{preset}] materiais fixos fora de TIPOS_VALIDOS: "
                    f"{invalidos} (fonte: PRESETS_KIT_COMPLETO em _tipos_comuns.py)"
                )

        secao = extrair_secao(texto_produzir, "## `/kit-completo-consultor`")
        if secao is not None:
            for tipo in PRESETS_KIT_COMPLETO["consultores"]["materiais"]:
                agente_dispatch = MAPA_DISPATCH.get(tipo)
                if agente_dispatch and agente_dispatch not in secao:
                    problemas.append(
                        f"[kit-completo-consultor] dispatch de '{tipo}' "
                        f"({agente_dispatch}) ausente na secao do comando - "
                        f"material do preset nunca sera despachado."
                    )
            if "--proxima-pasta" not in secao or "pool-materiais.py" not in secao:
                problemas.append(
                    f"[kit-completo-consultor] resolucao de pasta por "
                    f"'pool-materiais.py <slug> --proxima-pasta <tipo>' ausente na "
                    f"secao do comando (REGRA 11 - nunca sobrescrever)."
                )
        else:
            problemas.append(
                "[kit-completo-consultor] secao canonica nao encontrada - "
                "dispatch dos presets nao verificavel."
            )

    # Pacote de distribuicao (auto-atualiza a cada ciclo): o script existe e todo
    # ponto de finalizacao que roda empacotar-projeto.py <slug> (producao completa e
    # cada /gerar-<material>) tambem roda empacotar-distribuicao.py <slug>, garantindo
    # que a pasta distribuicao/ + zip + COPYRIGHT.txt sempre refletem o ultimo ciclo.
    if not (DIR_SCRIPTS / "empacotar-distribuicao.py").exists():
        problemas.append(
            "scripts/empacotar-distribuicao.py nao encontrado - pacote de "
            "distribuicao (pasta distribuicao/ + zip + COPYRIGHT.txt) inexistente."
        )
    if texto_produzir is not None:
        for parte in re.split(r"(?m)^## ", texto_produzir):
            if "empacotar-projeto.py <slug>" in parte:
                if "empacotar-distribuicao.py <slug>" not in parte:
                    titulo = parte.split("\n", 1)[0]
                    problemas.append(
                        f"[{titulo}] passo de empacotamento chama empacotar-projeto.py "
                        f"sem empacotar-distribuicao.py na mesma secao - pacote de "
                        f"distribuicao nao auto-atualiza neste ciclo."
                    )

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
