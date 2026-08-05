#!/usr/bin/env python3
"""
Motor de concorrencia em lote/backoff/auto-registro — portado de
fabrica-de-livros/scripts/pool-capitulos.py (Upgrade 4 - Controle Dinamico de
Concorrencia). Mesma maquina de estado; a unidade de trabalho deixa de ser
"1 capitulo" e passa a ser "1 material" (pdf, landing-page, apresentacao,
arte-01, arte-02, arte-03).

Em vez de instanciar todos os subagentes de material de uma vez, o Orquestrador
despacha em LOTES, consultando este script para saber:

  - qual e o proximo lote a despachar (`--plano` / `--proximo-lote`)
  - quais materiais continuam pendentes ou falharam (`--pendentes`)
  - quanto esperar antes de retentar um material (backoff exponencial)

Estado persistido em: output/<slug>/_pool_estado.json

Uso:
    python scripts/pool-materiais.py <slug> --plano [--lote 4]
    python scripts/pool-materiais.py <slug> --proximo-lote [--lote 4]
    python scripts/pool-materiais.py <slug> --pendentes [--estrito]
    python scripts/pool-materiais.py <slug> --registrar pdf --sucesso
    python scripts/pool-materiais.py <slug> --registrar arte-01 --falha "playwright timeout"
    python scripts/pool-materiais.py <slug> --status
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

LOTE_PADRAO = 4
MAX_TENTATIVAS = 3
LOCK_TIMEOUT_S = 30
BACKOFF_BASE_S = 15
BACKOFF_MAX_S = 240

TITULOS_MATERIAL = {
    "pdf": "PDF (apostila)",
    "landing-page": "Landing Page",
    "apresentacao": "Apresentacao",
    "arte-01": "Arte 1080x1080",
    "arte-02": "Arte 1080x1350",
    "arte-03": "Arte 1080x1920",
    "textos": "Textos de Apoio",
    "kit-consultor": "Kit do Consultor",
    "kit-distribuidor": "Kit Distribuidor",
}


def carregar_config(slug):
    caminho = DIR_OUTPUT / slug / "config_projeto.json"
    if not caminho.exists():
        print(f"[ERRO] config_projeto.json nao encontrado em {caminho.parent}")
        return None
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    materiais = dados.get("materiais_selecionados", [])
    return [{"material": m, "titulo": TITULOS_MATERIAL.get(m, m)} for m in materiais]


def caminho_estado(slug):
    return DIR_OUTPUT / slug / "_pool_estado.json"


def carregar_estado(slug):
    p = caminho_estado(slug)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"slug": slug, "lote": LOTE_PADRAO, "materiais": {}}


def gravar_estado(slug, estado):
    p = caminho_estado(slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")


def _adquirir_lock(slug, timeout=LOCK_TIMEOUT_S, poll=0.1):
    """Lock exclusivo por arquivo (criacao atomica via O_CREAT|O_EXCL) para
    serializar o read-modify-write de _pool_estado.json entre subagentes
    despachados em paralelo no mesmo lote."""
    lock_path = caminho_estado(slug).with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return lock_path
        except FileExistsError:
            if time.time() > deadline:
                try:
                    if time.time() - lock_path.stat().st_mtime > timeout:
                        lock_path.unlink()
                        continue
                except OSError:
                    continue
                raise TimeoutError(
                    f"nao foi possivel adquirir lock de estado para {slug} "
                    f"apos {timeout}s")
            time.sleep(poll)


def _liberar_lock(lock_path):
    try:
        lock_path.unlink()
    except OSError:
        pass


def material_entregue(slug, tipo):
    """Entregue = artefato esperado existe no disco e tem tamanho > 0.
    Checagem de forma/dimensao exata fica por conta de validar-pdf.py /
    validar-html.py / validar-dimensoes.py — aqui e so o gate de disco."""
    base = DIR_OUTPUT / slug / tipo
    if not base.exists():
        return False, "pasta ainda nao criada"
    if tipo == "pdf":
        pdfs = [p for p in base.glob("*.pdf") if p.stat().st_size > 0]
        return (True, "ok") if pdfs else (False, "PDF ainda nao gerado")
    if tipo in ("landing-page", "apresentacao"):
        idx = base / "index.html"
        if idx.exists() and idx.stat().st_size > 0:
            return True, "ok"
        return False, "index.html ainda nao gerado"
    if tipo.startswith("arte-"):
        pngs = [p for p in base.glob("*.png") if p.stat().st_size > 0]
        if len(pngs) < 3:
            return False, f"esperado 3 PNGs (1 por copy), encontrado {len(pngs)}"
        return True, "ok"
    if tipo == "textos":
        esperados = ("whatsapp.txt", "instagram.txt", "linkedin.txt")
        faltantes = [n for n in esperados
                     if not (base / n).exists() or (base / n).stat().st_size == 0]
        return (True, "ok") if not faltantes else (False, f"faltando: {', '.join(faltantes)}")
    if tipo in ("kit-consultor", "kit-distribuidor"):
        # 5 tons x 2 itens x {PNG, conteudo.json, texto_whatsapp.txt} = 10 de cada,
        # ver SPEC_KITS.md. Checagem de forma/dimensao exata fica com validar-kit.py.
        tons_pastas = ["artes-informativas", "artes-contra-intuitivas", "artes-tecnicas",
                       "artes-efeito-uau", "artes-educativas"]
        pngs = conteudos = textos = 0
        for tom_pasta in tons_pastas:
            for item in ("arte-01", "arte-02"):
                pasta_item = base / tom_pasta / item
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
        if (pngs, conteudos, textos) != (10, 10, 10):
            return False, (f"esperado 10 PNGs/conteudo.json/texto_whatsapp.txt, "
                            f"encontrado {pngs}/{conteudos}/{textos}")
        return True, "ok"
    return False, f"tipo de material desconhecido: {tipo}"


def backoff(tentativas):
    return min(BACKOFF_BASE_S * (2 ** max(0, tentativas - 1)), BACKOFF_MAX_S)


def montar_visao(slug, tamanho_lote):
    materiais = carregar_config(slug)
    if materiais is None:
        return None
    estado = carregar_estado(slug)
    estado["lote"] = tamanho_lote
    for item in materiais:
        tipo = item["material"]
        reg = estado["materiais"].setdefault(
            tipo, {"tentativas": 0, "ultimo_erro": "", "estado": "pendente"})
        ok, motivo = material_entregue(slug, tipo)
        item["tentativas"] = reg["tentativas"]
        item["ultimo_erro"] = reg["ultimo_erro"]
        if ok:
            reg["estado"] = "concluido_autonomo"
            item["estado"] = "concluido_autonomo"
            item["motivo"] = ""
        else:
            esgotado = reg["tentativas"] >= MAX_TENTATIVAS
            reg["estado"] = "esgotado" if esgotado else "pendente"
            item["estado"] = reg["estado"]
            item["motivo"] = motivo
            item["backoff_s"] = backoff(reg["tentativas"]) if reg["tentativas"] else 0
    gravar_estado(slug, estado)
    return materiais


def em_lotes(itens, tamanho):
    return [itens[i:i + tamanho] for i in range(0, len(itens), tamanho)]


def imprimir_lote(indice, lote):
    tipos = ", ".join(c["material"] for c in lote)
    print(f"LOTE {indice}: {len(lote)} material(is) -> {tipos}")
    for c in lote:
        extra = ""
        if c.get("tentativas"):
            extra = f" | tentativa {c['tentativas'] + 1}/{MAX_TENTATIVAS}, aguardar {c.get('backoff_s', 0)}s"
        print(f"  {c['material']:<14} [{c['estado']}] {c['titulo']}{extra}")


def main():
    ap = argparse.ArgumentParser(description="Pool de execucao paralela por lotes (materiais)")
    ap.add_argument("slug")
    ap.add_argument("--lote", type=int, default=LOTE_PADRAO,
                    help=f"materiais por lote (padrao {LOTE_PADRAO})")
    ap.add_argument("--plano", action="store_true", help="imprime o plano completo de lotes")
    ap.add_argument("--proximo-lote", action="store_true",
                    help="imprime apenas o proximo lote a despachar")
    ap.add_argument("--pendentes", action="store_true", help="lista materiais pendentes/esgotados")
    ap.add_argument("--status", action="store_true", help="resumo do progresso")
    ap.add_argument("--registrar", metavar="TIPO", help="registra o resultado de um material")
    ap.add_argument("--sucesso", action="store_true")
    ap.add_argument("--falha", nargs="?", const="falha nao especificada", metavar="MOTIVO")
    ap.add_argument("--reset", action="store_true", help="zera o contador de tentativas")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--estrito", action="store_true",
                    help="com --pendentes: exit 1 se houver material nao concluido")
    args = ap.parse_args()

    if not (DIR_OUTPUT / args.slug).exists():
        print(f"[ERRO] Projeto nao encontrado: {DIR_OUTPUT / args.slug}")
        return 1

    if args.registrar:
        try:
            lock_path = _adquirir_lock(args.slug)
        except TimeoutError as exc:
            print(f"[ERRO] {exc}")
            return 1
        try:
            estado = carregar_estado(args.slug)
            reg = estado["materiais"].setdefault(
                args.registrar, {"tentativas": 0, "ultimo_erro": "", "estado": "pendente"})
            reg["tentativas"] += 1
            if args.sucesso:
                reg["estado"] = "concluido_autonomo"
                reg["ultimo_erro"] = ""
                print(f"[OK] {args.registrar}: sucesso registrado "
                      f"(tentativa {reg['tentativas']})")
            else:
                reg["ultimo_erro"] = args.falha or "falha nao especificada"
                esgotado = reg["tentativas"] >= MAX_TENTATIVAS
                reg["estado"] = "esgotado" if esgotado else "pendente"
                espera = backoff(reg["tentativas"])
                print(f"[FALHA] {args.registrar}: {reg['ultimo_erro']} "
                      f"(tentativa {reg['tentativas']}/{MAX_TENTATIVAS})")
                if esgotado:
                    print("  -> tentativas esgotadas; escalar para revisao manual")
                else:
                    print(f"  -> retentar apos {espera}s (backoff exponencial)")
            gravar_estado(args.slug, estado)
        finally:
            _liberar_lock(lock_path)
        return 0

    if args.reset:
        estado = carregar_estado(args.slug)
        for reg in estado["materiais"].values():
            reg["tentativas"] = 0
            reg["ultimo_erro"] = ""
        gravar_estado(args.slug, estado)
        print("[OK] Contadores de tentativa zerados")
        return 0

    materiais = montar_visao(args.slug, args.lote)
    if materiais is None:
        return 1

    concluidos = [c for c in materiais if c["estado"] == "concluido_autonomo"]
    pendentes = [c for c in materiais if c["estado"] == "pendente"]
    esgotados = [c for c in materiais if c["estado"] == "esgotado"]

    if args.json:
        print(json.dumps({
            "slug": args.slug, "lote": args.lote,
            "total": len(materiais), "concluidos": len(concluidos),
            "pendentes": len(pendentes), "esgotados": len(esgotados),
            "materiais": materiais,
            "lotes_pendentes": em_lotes(pendentes, args.lote),
        }, ensure_ascii=False, indent=2))
        return 1 if (args.estrito and (pendentes or esgotados)) else 0

    if args.status or not (args.plano or args.proximo_lote or args.pendentes):
        print(f"POOL - {args.slug} (lote={args.lote}, max_tentativas={MAX_TENTATIVAS})")
        print(f"  total      : {len(materiais)}")
        print(f"  concluidos : {len(concluidos)}")
        print(f"  pendentes  : {len(pendentes)}")
        print(f"  esgotados  : {len(esgotados)}")
        if esgotados:
            print("  materiais esgotados: " + ", ".join(c["material"] for c in esgotados))
        return 0

    if args.plano:
        lotes = em_lotes(materiais, args.lote)
        print(f"PLANO DE DESPACHO - {args.slug}: {len(materiais)} material(is) "
              f"em {len(lotes)} lote(s) de ate {args.lote}")
        for i, lote in enumerate(lotes, 1):
            imprimir_lote(i, lote)
        print("\nRegra: despache um lote, aguarde TODOS os subagentes do lote, "
              "registre o resultado de cada material, so entao despache o proximo lote.")
        return 0

    if args.proximo_lote:
        fila = pendentes
        if not fila:
            print("[OK] Nenhum material pendente - Fase 2 completa. "
                  "Avance para a Fase 2.5 (revisor-marca).")
            return 0
        imprimir_lote(1, fila[:args.lote])
        restantes = max(0, len(fila) - args.lote)
        print(f"\nRestam {restantes} material(is) na fila depois deste lote.")
        return 0

    if args.pendentes:
        if not pendentes and not esgotados:
            print("[OK] Todos os materiais concluidos e validados estruturalmente")
            return 0
        for i, lote in enumerate(em_lotes(pendentes, args.lote), 1):
            imprimir_lote(i, lote)
        if esgotados:
            print(f"\n[ESGOTADOS] {len(esgotados)} material(is) atingiram "
                  f"{MAX_TENTATIVAS} tentativas:")
            for c in esgotados:
                print(f"  {c['material']}: {c['ultimo_erro'] or c['motivo']}")
        return 1 if args.estrito else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
