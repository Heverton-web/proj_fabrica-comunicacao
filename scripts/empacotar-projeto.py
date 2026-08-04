#!/usr/bin/env python3
"""
Empacotamento final (equivalente a empacotar-distribuicao.py da Fabrica
Agentica de Livros): consolida o estado de _pool_estado.json, o veredito de
relatorio_auditoria.json e o parecer qualitativo de parecer_revisao.json em
um unico manifesto_materiais.json na raiz do projeto.

Falha ruidosamente (exit 1) se um material esperado nao tiver artefato no
disco - nunca reporta sucesso silencioso para algo que nao foi de fato gerado.

Uso:
    python scripts/empacotar-projeto.py <slug>
"""

import argparse
import json
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

PATH_POR_TIPO = {
    "pdf": lambda base, slug: next(iter(sorted((base / "pdf").glob("*.pdf"))), None),
    "landing-page": lambda base, slug: (base / "landing-page" / "index.html"),
    "apresentacao": lambda base, slug: (base / "apresentacao" / "index.html"),
    "arte-01": lambda base, slug: next(iter(sorted((base / "arte-01").glob("*.png"))), None),
    "arte-02": lambda base, slug: next(iter(sorted((base / "arte-02").glob("*.png"))), None),
    "arte-03": lambda base, slug: next(iter(sorted((base / "arte-03").glob("*.png"))), None),
}


def carregar_json(caminho, default=None):
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return default if default is not None else {}


def main():
    ap = argparse.ArgumentParser(description="Empacota o manifesto final de materiais do projeto")
    ap.add_argument("slug")
    args = ap.parse_args()

    base = DIR_OUTPUT / args.slug
    if not base.exists():
        print(f"[ERRO] projeto nao encontrado: {base}")
        return 1

    config = carregar_json(base / "config_projeto.json")
    tipos = config.get("materiais_selecionados", [])
    if not tipos:
        print(f"[ERRO] config_projeto.json de {args.slug} nao tem materiais_selecionados")
        return 1

    estado_pool = carregar_json(base / "_pool_estado.json", {}).get("materiais", {})
    parecer = carregar_json(base / "revisao" / "parecer_revisao.json", {
        "decisoes_design": [], "informacoes_faltantes": [], "sugestoes_legenda": [],
    })

    materiais = []
    algum_erro = False
    for tipo in tipos:
        estado = estado_pool.get(tipo, {}).get("estado", "desconhecido")
        resolver = PATH_POR_TIPO.get(tipo)
        artefato = resolver(base, args.slug) if resolver else None

        if estado == "concluido_autonomo" and (artefato is None or not artefato.exists()):
            print(f"[ERRO] {tipo}: estado diz concluido_autonomo mas o artefato nao existe no disco "
                  f"({artefato}) - nao vou reportar sucesso falso")
            algum_erro = True
            continue

        materiais.append({
            "tipo": tipo,
            "status": estado,
            "path": str(artefato.relative_to(DIR_PROJETO).as_posix()) if artefato and artefato.exists() else None,
        })

    if algum_erro:
        print("[ERRO] empacotamento abortado - corrija as inconsistencias acima antes de reempacotar")
        return 1

    manifesto = {
        "slug": args.slug,
        "materiais": materiais,
        "decisoes_design": parecer.get("decisoes_design", []),
        "informacoes_faltantes": parecer.get("informacoes_faltantes", []),
        "sugestoes_legenda": parecer.get("sugestoes_legenda", []),
    }

    (base / "manifesto_materiais.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")

    entregues = [m for m in materiais if m["status"] == "concluido_autonomo"]
    esgotados = [m for m in materiais if m["status"] == "esgotado"]
    print(f"[OK] manifesto_materiais.json gravado em {base / 'manifesto_materiais.json'}")
    print(f"  entregues : {len(entregues)}/{len(materiais)} ({', '.join(m['tipo'] for m in entregues)})")
    if esgotados:
        print(f"  esgotados : {len(esgotados)} ({', '.join(m['tipo'] for m in esgotados)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
