#!/usr/bin/env python3
"""
Auditoria deterministica final (equivalente a auditar-obra.py da Fabrica
Agentica de Livros): roda os scripts validar-*.py por tipo de material, checa
R9 (todo material selecionado terminou concluido_autonomo ou esgotado) e R12
(estrutura de output/<slug>/ correta), e produz uma tabela de conformidade.

Uso:
    python scripts/auditar-projeto.py <slug> [--estrito] [--apenas pdf,arte-01]

--estrito: exit 1 se qualquer requisito falhar (usado como gate de fase pelo
           /produzir-comunicacao-completa e pelos comandos /gerar-*).
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from _tipos_comuns import erros_preset_kit_completo, tipo_base

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"
DIR_SCRIPTS = Path(__file__).resolve().parent

TIPOS_VALIDOS = ["pdf", "landing-page", "apresentacao", "arte-01", "arte-02", "arte-03",
                  "textos", "kit-consultor", "kit-distribuidor"]


def rodar_validador(slug, tipo, estrito=False):
    """Retorna (ok, saida) rodando o script validar-*.py apropriado para o tipo.

    `tipo` pode ser uma pasta versionada (ex.: "pdf-v2", gerada por
    /gerar-<material> - ver REGRA 11 do AGENTS.md): o dispatch usa sempre
    tipo_base(tipo) para escolher o validador certo, mas passa a string
    completa via --pasta para que o script valide a pasta real em disco.

    `estrito` propaga o gate determinístico (--estrito) aos validadores de
    HTML (validar-html.py), que passam a bloquear emoji e categoria<->icone
    incoerente (ver aplicador-marca-conexao/SKILL.md, seção "Ícones")."""
    py = sys.executable
    base = tipo_base(tipo)
    if base == "pdf":
        cmd = [py, str(DIR_SCRIPTS / "validar-pdf.py"), slug, "--pasta", tipo]
    elif base in ("landing-page", "apresentacao"):
        cmd = [py, str(DIR_SCRIPTS / "validar-html.py"), slug, base, "--pasta", tipo]
        if estrito:
            cmd.append("--estrito")
    elif base.startswith("arte-"):
        cmd = [py, str(DIR_SCRIPTS / "validar-dimensoes.py"), slug, base, "--pasta", tipo]
    elif base == "textos":
        cmd = [py, str(DIR_SCRIPTS / "validar-textos.py"), slug, "--pasta", tipo]
    elif base in ("kit-consultor", "kit-distribuidor"):
        cmd = [py, str(DIR_SCRIPTS / "validar-kit.py"), slug, base, "--pasta", tipo]
    else:
        return False, f"tipo desconhecido: {tipo}"

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    saida = (resultado.stdout or "") + (resultado.stderr or "")
    return resultado.returncode == 0, saida.strip()


def rodar_validador_marca(slug, tipo):
    """R5: fidelidade de cor/fonte - so aplica a landing-page/apresentacao (arte
    e validado por construcao + dimensoes; pdf usa -V, nao ha 'hex solto' a checar).
    `validar-design-tokens.py` ja recebe `tipo` como o nome literal da pasta
    (sem restricao de choices), entao a string versionada (ex.: "landing-page-v2")
    passa direto, sem precisar de --pasta separado."""
    if tipo_base(tipo) not in ("landing-page", "apresentacao"):
        return True, "n/a"
    py = sys.executable
    cmd = [py, str(DIR_SCRIPTS / "validar-design-tokens.py"), slug, tipo]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    saida = (resultado.stdout or "") + (resultado.stderr or "")
    return resultado.returncode == 0, saida.strip()


def checar_r9(slug, tipos):
    """R9: todo material do lote terminou concluido_autonomo ou esgotado."""
    estado_path = DIR_OUTPUT / slug / "_pool_estado.json"
    if not estado_path.exists():
        return False, "_pool_estado.json nao encontrado - pool-materiais.py ainda nao rodou"
    estado = json.loads(estado_path.read_text(encoding="utf-8"))
    materiais = estado.get("materiais", {})
    nao_finalizados = [t for t in tipos
                        if materiais.get(t, {}).get("estado") not in ("concluido_autonomo", "esgotado")]
    if nao_finalizados:
        return False, f"materiais sem estado final: {nao_finalizados}"
    return True, "ok"


def checar_r12(slug, tipos):
    """R12: pasta output/<slug>/<tipo>/ existe para cada material selecionado."""
    faltando = [t for t in tipos if not (DIR_OUTPUT / slug / t).exists()]
    if faltando:
        return False, f"pastas de output ausentes: {faltando}"
    return True, "ok"


def checar_preset_kit_completo(config):
    """Regra dos presets /kit-completo-<publico> (fonte unica em _tipos_comuns):
    publico_alvo e materiais coerentes com o preset declarado em
    config.preset_kit_completo. Projeto sem preset = ok (n/a)."""
    erros = erros_preset_kit_completo(config)
    if not erros:
        if config.get("preset_kit_completo"):
            return True, "ok"
        return True, "n/a"
    return False, "; ".join(erros)


def main():
    ap = argparse.ArgumentParser(description="Auditoria final de conformidade do projeto")
    ap.add_argument("slug")
    ap.add_argument("--estrito", action="store_true")
    ap.add_argument("--apenas", default=None,
                     help="lista separada por virgula de tipos a auditar (default: todos os selecionados)")
    args = ap.parse_args()

    config_path = DIR_OUTPUT / args.slug / "config_projeto.json"
    if not config_path.exists():
        print(f"[ERRO] config_projeto.json nao encontrado para {args.slug}")
        return 1
    config = json.loads(config_path.read_text(encoding="utf-8"))

    if args.apenas:
        tipos = [t.strip() for t in args.apenas.split(",") if t.strip()]
    else:
        tipos = config.get("materiais_selecionados", [])

    tipos = [t for t in tipos if tipo_base(t) in TIPOS_VALIDOS]
    if not tipos:
        print("[ERRO] nenhum tipo de material valido para auditar")
        return 1

    print(f"AUDITORIA - {args.slug} ({len(tipos)} material(is): {', '.join(tipos)})")
    print("=" * 70)

    tudo_ok = True
    relatorio = {"slug": args.slug, "tipos": {}}

    for tipo in tipos:
        ok_validacao, saida_validacao = rodar_validador(args.slug, tipo, estrito=args.estrito)
        ok_marca, saida_marca = rodar_validador_marca(args.slug, tipo)
        ok_tipo = ok_validacao and ok_marca

        status = "CONFORME" if ok_tipo else "NAO CONFORME"
        print(f"\n[{tipo}] {status}")
        print(f"  validacao tecnica : {'OK' if ok_validacao else 'FALHA'}")
        print(f"  fidelidade marca  : {'OK' if ok_marca else ('FALHA' if saida_marca != 'n/a' else 'n/a')}")

        relatorio["tipos"][tipo] = {
            "conforme": ok_tipo,
            "validacao_tecnica": saida_validacao,
            "fidelidade_marca": saida_marca,
        }
        tudo_ok = tudo_ok and ok_tipo

    ok_r9, motivo_r9 = checar_r9(args.slug, tipos)
    ok_r12, motivo_r12 = checar_r12(args.slug, tipos)
    ok_preset, motivo_preset = checar_preset_kit_completo(config)
    print(f"\n[R9]  materiais com estado final : {'OK' if ok_r9 else 'FALHA - ' + motivo_r9}")
    print(f"[R12] estrutura de output correta : {'OK' if ok_r12 else 'FALHA - ' + motivo_r12}")
    print(f"[PRESET] coerencia kit-completo  : {'OK' if ok_preset else 'FALHA - ' + motivo_preset}")
    relatorio["r9_estado_final"] = {"ok": ok_r9, "motivo": motivo_r9}
    relatorio["r12_estrutura_output"] = {"ok": ok_r12, "motivo": motivo_r12}
    relatorio["preset_kit_completo"] = {"ok": ok_preset, "motivo": motivo_preset}
    tudo_ok = tudo_ok and ok_r9 and ok_r12 and ok_preset

    dir_revisao = DIR_OUTPUT / args.slug / "revisao"
    dir_revisao.mkdir(parents=True, exist_ok=True)
    relatorio["conforme"] = tudo_ok
    (dir_revisao / "relatorio_auditoria.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"VEREDITO: {'CONFORME' if tudo_ok else 'NAO CONFORME'}")
    print(f"Relatorio completo em: {dir_revisao / 'relatorio_auditoria.json'}")

    if args.estrito and not tudo_ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
