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

sys.path.append(str(Path(__file__).resolve().parent))
from _tipos_comuns import tipo_base

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

TONS_PASTAS_KIT = ["artes-informativas", "artes-contra-intuitivas", "artes-tecnicas",
                   "artes-efeito-uau", "artes-educativas"]


def resolver_artefato(base, slug, tipo):
    """Retorna o path do artefato principal de `tipo` (que pode ser uma pasta
    versionada, ex.: "pdf-v2" - ver REGRA 11 do AGENTS.md), ou None se ainda nao
    estiver completo. O dispatch usa sempre tipo_base(tipo); a pasta lida em
    disco e sempre a string completa `tipo`."""
    pasta = base / tipo
    base_tipo = tipo_base(tipo)

    if base_tipo == "pdf":
        return next(iter(sorted(pasta.glob("*.pdf"))), None)

    if base_tipo in ("landing-page", "apresentacao"):
        idx = pasta / "index.html"
        return idx if idx.exists() else None

    if base_tipo.startswith("arte-"):
        pngs = [p for p in pasta.glob("*.png") if p.stat().st_size > 0] if pasta.is_dir() else []
        # 3 PNGs esperados: 1 por copy compartilhada (arte/copies.json),
        # ver docs/05-plano-expansao-multi-copy-arte.md
        if len(pngs) != 3:
            return None
        # REGRA INTOCAVEL: as 9 legendas de publicacao (3 copies x 3 canais:
        # instagram/linkedin/whatsapp) sao parte obrigatoria do material - vivem em
        # output/<slug>/arte/ (compartilhadas entre arte-01/02/03, ver SPEC_ARTE.md),
        # nao dentro da propria pasta de formato.
        pasta_legendas = base / "arte"
        legendas_ok = all(
            (pasta_legendas / f"legenda_copy{i:02d}_{canal}.txt").exists()
            and (pasta_legendas / f"legenda_copy{i:02d}_{canal}.txt").stat().st_size > 0
            for i in (1, 2, 3) for canal in ("instagram", "linkedin", "whatsapp")
        )
        return pasta if legendas_ok else None

    if base_tipo == "textos":
        esperados = ("whatsapp.txt", "instagram.txt", "linkedin.txt")
        if pasta.is_dir() and all((pasta / n).exists() and (pasta / n).stat().st_size > 0 for n in esperados):
            return pasta
        return None

    if base_tipo in ("kit-consultor", "kit-distribuidor"):
        if not pasta.is_dir():
            return None
        pngs = conteudos = textos = 0
        for tom_pasta in TONS_PASTAS_KIT:
            for item in ("arte-01", "arte-02"):
                pasta_item = pasta / tom_pasta / item
                if not pasta_item.is_dir():
                    continue
                if any(p.stat().st_size > 0 for p in pasta_item.glob("*.png")):
                    pngs += 1
                conteudo = pasta_item / "conteudo.json"
                if conteudo.exists() and conteudo.stat().st_size > 0:
                    conteudos += 1
                texto = pasta_item / "texto_whatsapp.txt"
                if texto.exists() and texto.stat().st_size > 0:
                    textos += 1
        # 10 PNGs + 10 conteudo.json + 10 texto_whatsapp.txt esperados (5 tons x 2
        # itens), ver SPEC_KITS.md.
        return pasta if (pngs, conteudos, textos) == (10, 10, 10) else None

    return None


def com_versoes(base, tipos_selecionados):
    """Acrescenta a `tipos_selecionados` qualquer pasta irma versionada
    (<tipo>-v2, -v3...) ja encontrada em disco - garante que o manifesto sempre
    reflita 100% do que foi gerado, nao so a 1a geracao (REGRA 11)."""
    completos = list(tipos_selecionados)
    for tipo in tipos_selecionados:
        n = 2
        while (base / f"{tipo}-v{n}").exists():
            completos.append(f"{tipo}-v{n}")
            n += 1
    return completos


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
    tipos = com_versoes(base, tipos)

    estado_pool = carregar_json(base / "_pool_estado.json", {}).get("materiais", {})
    parecer = carregar_json(base / "revisao" / "parecer_revisao.json", {
        "decisoes_design": [], "informacoes_faltantes": [], "sugestoes_legenda": [],
    })

    materiais = []
    algum_erro = False
    for tipo in tipos:
        estado = estado_pool.get(tipo, {}).get("estado", "desconhecido")
        artefato = resolver_artefato(base, args.slug, tipo)

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
