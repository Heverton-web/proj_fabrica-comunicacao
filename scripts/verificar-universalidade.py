#!/usr/bin/env python3
"""
Arbitro deterministico da universalidade entre harnesses (REGRA 10 do AGENTS.md).

Garante que comandos, rules e skills funcionem em QUALQUER harness, seguindo a
arquitetura de 3 camadas:
  1. Canonico (harness-agnostic): SPEC_COMANDOS.md (procedimentos), AGENTS.md
     (regras) e .claude/skills/*/SKILL.md (padrao aberto Agent Skills) — unica
     fonte de verdade, nunca duplica logica em arquivo de harness.
  2. Adaptadores finos de descoberta (um por harness): .claude/commands/*.md
     (Claude Code) e .opencode/commands/*.md (opencode) — ponteiros que apenas
     apontam para a secao correspondente de SPEC_COMANDOS.md, nunca copiam o
     procedimento.
  3. Rules finas por harness: CLAUDE.md, GEMINI.md, CODEBUDDY.md, QODER.md —
     referenciam AGENTS.md + SPEC_COMANDOS.md sem duplicar listas canonicas.

O fallback universal para qualquer outro harness e o mapeamento por linguagem
natural descrito em AGENTS.md -> SPEC_COMANDOS.md.

Uso:
    python scripts/verificar-universalidade.py [--estrito]

Exit code 0 = tudo universal. Exit code 1 = lacuna encontrada (com --estrito;
sem --estrito apenas avisa, para uso exploratorio).
"""

import argparse
import re
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_COMMANDS_CLAUDE = DIR_PROJETO / ".claude" / "commands"
DIR_COMMANDS_OPENCODE = DIR_PROJETO / ".opencode" / "commands"
DIR_SKILLS = DIR_PROJETO / ".claude" / "skills"
CAMINHO_SPEC_COMANDOS = DIR_PROJETO / "SPEC_COMANDOS.md"
CAMINHO_AGENTS = DIR_PROJETO / "AGENTS.md"

# Rules finas por harness: o arquivo que o harness carrega como instrucao.
HARNESS_RULES = {
    "CLAUDE.md": "Claude Code",
    "GEMINI.md": "Gemini CLI",
    "CODEBUDDY.md": "CodeBuddy",
    "QODER.md": "Qoder",
}

# Teto de tamanho de um adaptador fino de comando — acima disso, ha copia de
# procedimento (bug historico de TIPOS_VALIDOS duplicado).
TETO_ADAPTADOR_BYTES = 3000

# Teto para rules por harness: listas/regras canonicas vivem no AGENTS.md.
TETO_RULES_BYTES = 6000

PADRAO_SECAO_COMANDO = re.compile(r"^## `(/[a-z0-9-]+)`", re.M)


def carregar_texto(caminho):
    if not caminho.exists():
        return None
    return caminho.read_text(encoding="utf-8")


def extrair_comandos(texto):
    return sorted(PADRAO_SECAO_COMANDO.findall(texto))


def verificar_adaptadores(comandos, problemas):
    """Camada 2: cada comando canonico precisa de adaptador fino em cada harness
    de slash-command suportado, e cada adaptador precisa corresponder a um
    comando canonico (nada de comando orfao)."""
    pares_harness = (
        ("Claude Code", DIR_COMMANDS_CLAUDE),
        ("opencode", DIR_COMMANDS_OPENCODE),
    )
    orfaos_por_harness = {}

    for nome_harness, diretorio in pares_harness:
        arquivos = {p.name for p in diretorio.glob("*.md")} if diretorio.exists() else set()
        orfaos_por_harness[nome_harness] = arquivos

        for comando in comandos:
            nome = comando[1:]
            caminho = diretorio / f"{nome}.md"
            if caminho.name not in arquivos:
                problemas.append(
                    f"[comando {comando}] adaptador ausente em {nome_harness}: "
                    f"{diretorio.relative_to(DIR_PROJETO)}/{nome}.md"
                )
                continue

            texto = carregar_texto(caminho)
            if texto is None:
                continue
            if "SPEC_COMANDOS.md" not in texto:
                problemas.append(
                    f"[comando {comando}] adaptador {nome_harness} nao referencia "
                    f"SPEC_COMANDOS.md (deve ser ponteiro fino, nunca copia)."
                )
            if len(texto.encode("utf-8")) > TETO_ADAPTADOR_BYTES:
                problemas.append(
                    f"[comando {comando}] adaptador {nome_harness} com "
                    f"{len(texto.encode('utf-8'))} bytes (teto {TETO_ADAPTADOR_BYTES}) "
                    f"- suspeita de duplicar o procedimento canonico."
                )
            if not texto.lstrip().startswith("---"):
                problemas.append(
                    f"[comando {comando}] adaptador {nome_harness} sem frontmatter "
                    f"--- (requisito de descoberta do harness)."
                )

    for nome_harness, orfaos in orfaos_por_harness.items():
        for orfao in sorted(orfaos):
            nome_sem_extensao = Path(orfao).stem
            if f"/{nome_sem_extensao}" not in comandos:
                problemas.append(
                    f"[adaptador orfao] {nome_harness}: {orfao} nao tem secao "
                    f"correspondente em SPEC_COMANDOS.md."
                )


def verificar_rules(problemas):
    """Camada 3: rules por harness sao finas — referenciam o canonico sem copia."""
    texto_agents = carregar_texto(CAMINHO_AGENTS)
    if texto_agents is None:
        problemas.append("[rules] AGENTS.md (canonico de regras) nao encontrado.")
        return

    for nome_arquivo, nome_harness in HARNESS_RULES.items():
        caminho = DIR_PROJETO / nome_arquivo
        texto = carregar_texto(caminho)
        if texto is None:
            problemas.append(f"[rules] {nome_arquivo} ({nome_harness}) nao encontrado.")
            continue
        if "AGENTS.md" not in texto:
            problemas.append(
                f"[rules] {nome_arquivo} nao referencia AGENTS.md (canonico de regras)."
            )
        if "SPEC_COMANDOS.md" not in texto:
            problemas.append(
                f"[rules] {nome_arquivo} nao referencia SPEC_COMANDOS.md "
                f"(canonico dos comandos)."
            )
        if len(texto.encode("utf-8")) > TETO_RULES_BYTES:
            problemas.append(
                f"[rules] {nome_arquivo} com {len(texto.encode('utf-8'))} bytes "
                f"(teto {TETO_RULES_BYTES}) - suspeita de duplicar regras canonicas "
                f"do AGENTS.md."
            )


def verificar_skills(problemas):
    """Camada 1 (skills): padrao aberto Agent Skills — frontmatter name+description,
    exigido por Claude Code, opencode e Gemini CLI."""
    if not DIR_SKILLS.exists():
        problemas.append("[skills] .claude/skills/ nao encontrado.")
        return

    for skill_dir in sorted(DIR_SKILLS.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        texto = carregar_texto(skill_md) or ""
        if not texto.lstrip().startswith("---"):
            problemas.append(f"[skills] {skill_dir.name}/SKILL.md sem frontmatter ---.")
            continue
        if "name:" not in texto or "description:" not in texto:
            problemas.append(
                f"[skills] {skill_dir.name}/SKILL.md sem 'name'/'description' no "
                f"frontmatter (padrao Agent Skills)."
            )


def verificar_mcps(problemas):
    """Camada 1 (MCPs): todo servidor MCP declarado em .mcp.json (Claude Code)
    precisa existir tambem em opencode.jsonc (opencode) — caso contrario a
    personalizacao so existe em um harness."""
    caminho_claude = DIR_PROJETO / ".mcp.json"
    caminho_opencode = DIR_PROJETO / "opencode.jsonc"

    def servidores_mcp(caminho):
        texto = carregar_texto(caminho)
        if texto is None:
            return None
        try:
            import json
            return set(json.loads(texto).get("mcp", {}).keys())
        except (ValueError, AttributeError):
            servidores = set(re.findall(r'"([A-Za-z0-9_-]+)"\s*:\s*\{', texto))
            return servidores

    claude_mcps = servidores_mcp(caminho_claude)
    opencode_mcps = servidores_mcp(caminho_opencode)

    if claude_mcps is None:
        problemas.append("[mcp] .mcp.json nao encontrado.")
    if opencode_mcps is None:
        problemas.append("[mcp] opencode.jsonc nao encontrado.")

    if claude_mcps and opencode_mcps is not None:
        for servidor in sorted(claude_mcps):
            if servidor not in opencode_mcps:
                problemas.append(
                    f"[mcp] servidor '{servidor}' declarado em .mcp.json mas ausente "
                    f"em opencode.jsonc — nao funciona no opencode."
                )


def verificar_hooks(problemas):
    """Camada 4 (hooks): hooks de settings sao conveniencia proprietaria do Claude
    Code; o guarda universal e o script determinístico, listado como passo manual
    no canonico (SPEC_COMANDOS.md)."""
    texto_spec = carregar_texto(CAMINHO_SPEC_COMANDOS) or ""
    for guarda in ("verificar-universalidade", "verificar-consistencia"):
        if guarda not in texto_spec:
            problemas.append(
                f"[hooks] guarda '{guarda}' nao citado em SPEC_COMANDOS.md como passo "
                f"manual obrigatorio — hooks (proprietarios) nao podem ser o unico "
                f"gatilho."
            )


def verificar():
    problemas = []
    texto_spec = carregar_texto(CAMINHO_SPEC_COMANDOS)

    if texto_spec is None:
        problemas.append(f"CRITICO: {CAMINHO_SPEC_COMANDOS} nao encontrado.")
        return problemas

    comandos = extrair_comandos(texto_spec)
    if not comandos:
        problemas.append(
            "CRITICO: nenhuma secao '## /comando' encontrada em SPEC_COMANDOS.md."
        )

    verificar_adaptadores(comandos, problemas)
    verificar_rules(problemas)
    verificar_skills(problemas)
    verificar_mcps(problemas)
    verificar_hooks(problemas)
    return problemas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estrito", action="store_true",
                    help="retorna exit code 1 se qualquer lacuna for encontrada")
    args = ap.parse_args()

    problemas = verificar()

    print(f"VERIFICACAO DE UNIVERSALIDADE ENTRE HARNESSES")
    print("=" * 70)

    if not problemas:
        print("[OK] Comandos, rules e skills universais: canonicos unicos + adaptadores "
              "finos em todos os harnesses suportados.")
        return 0

    for p in problemas:
        print(f"  - {p}")

    print("=" * 70)
    print(f"VEREDITO: {len(problemas)} lacuna(s) de universalidade")

    if args.estrito:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
