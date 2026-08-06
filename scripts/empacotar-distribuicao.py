#!/usr/bin/env python3
"""
Pacote de distribuicao (resultados finais): apos o empacotamento do manifesto
(empacotar-projeto.py), gera em output/<slug>/distribuicao/ apenas os RESULTADOS
FINAIS de cada material concluido_autonomo - sem insumos, sem briefs, sem JSONs
de trabalho, sem revisao/ (REGRA 2: material puro, silenciamento estetico).

Regras:
- A versao empacotada de cada material e a MAIS RECENTE em disco (maior sufixo
  -vN da REGRA 11 do AGENTS.md); as versoes antigas continuam preservadas em
  output/<slug>/ - o pacote e derivado e regeneravel, nunca apaga origem.
- A pasta distribuicao/ e sempre regenerada do zero (mesma disciplina do
  manifesto_materiais.json).
- Inclui COPYRIGHT.txt (direitos autorais de marca) na raiz do pacote.
- Gera tambem o zip distribuicao_<slug>.zip DENTRO da pasta distribuicao/
  (conteudo identico ao da pasta, sem o proprio zip).

Uso:
    python scripts/empacotar-distribuicao.py <slug>
"""

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

NOME_PACOTE = "distribuicao"
COPYRIGHT = (
    "2026 © Conexão Sistemas de Próteses — Todos os direitos reservados.\n"
    "\n"
    "Este pacote contém os materiais finais do projeto {slug}, produzidos pela\n"
    "Fábrica de Materiais de Comunicação da Conexão. Uso exclusivo conforme\n"
    "autorização da Conexão Sistemas de Próteses. Proibida a reprodução,\n"
    "distribuição ou comercialização sem autorização prévia por escrito.\n"
)


def carregar_json(caminho, default=None):
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return default if default is not None else {}


def versao_de(pasta):
    """Extrai o numero de versao de uma pasta 'tipo' ou 'tipo-vN' (sem sufixo = 0)."""
    m = re.search(r"-v(\d+)$", pasta.name)
    return int(m.group(1)) if m else 0


def pastas_do_tipo(base, tipo):
    """Pastas em output/<slug>/ que correspondem a `tipo` (1a geracao e -vN)."""
    return sorted(
        (p for p in base.iterdir() if p.is_dir() and re.fullmatch(rf"{tipo}(-v\d+)?", p.name)),
        key=versao_de,
    )


def copiar_artefato(origem_tipo, destino_tipo, slug):
    """Copia o artefato final do tipo para o pacote. PDF vira so o .pdf; os
    demais tipos copiam a pasta inteira (HTML precisa de assets/, kits de
    artes-*/texto_whatsapp.txt; textos dos .txt). Retorna True se copiou."""
    base_origem = DIR_OUTPUT / slug
    destino = base_origem / NOME_PACOTE / destino_tipo
    destino.mkdir(parents=True, exist_ok=True)

    if destino_tipo == "pdf":
        pdfs = sorted(origem_tipo.glob("*.pdf"))
        if not pdfs:
            return False
        shutil.copy2(pdfs[0], destino / pdfs[0].name)
        return True

    shutil.copytree(origem_tipo, destino, dirs_exist_ok=True)
    return True


def main():
    ap = argparse.ArgumentParser(description="Gera o pacote de distribuicao com os resultados finais")
    ap.add_argument("slug")
    args = ap.parse_args()

    base = DIR_OUTPUT / args.slug
    if not base.exists():
        print(f"[ERRO] projeto nao encontrado: {base}")
        return 1

    manifesto = carregar_json(base / "manifesto_materiais.json")
    materiais = manifesto.get("materiais", [])
    if not materiais:
        print("[ERRO] manifesto_materiais.json vazio - rode empacotar-projeto.py antes")
        return 1

    pacote = base / NOME_PACOTE
    shutil.rmtree(pacote, ignore_errors=True)
    pacote.mkdir(parents=True)

    incluidos = []
    algum_erro = False
    for material in materiais:
        if material.get("status") != "concluido_autonomo":
            continue
        tipo = material["tipo"]
        variantes = pastas_do_tipo(base, tipo)
        if not variantes:
            print(f"[ERRO] {tipo}: nenhuma pasta de material encontrada em disco")
            algum_erro = True
            continue
        mais_recente = variantes[-1]
        if not copiar_artefato(mais_recente, tipo, args.slug):
            print(f"[ERRO] {tipo}: artefato final nao encontrado em {mais_recente}")
            algum_erro = True
            continue
        incluidos.append(f"{tipo} ({mais_recente.name})")

    if algum_erro:
        print("[ERRO] pacote de distribuicao abortado - corrija as inconsistencias acima")
        return 1

    (pacote / "COPYRIGHT.txt").write_text(
        COPYRIGHT.format(slug=args.slug), encoding="utf-8")

    zip_path = pacote / f"{NOME_PACOTE}_{args.slug}.zip"
    arquivos = [
        arquivo for arquivo in sorted(pacote.rglob("*"))
        if arquivo.is_file() and arquivo != zip_path
    ]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arquivo in arquivos:
            zf.write(arquivo, arquivo.relative_to(pacote).as_posix())

    print(f"[OK] pacote de distribuicao em {pacote}")
    print(f"  incluidos : {', '.join(incluidos)}")
    print(f"[OK] zip gerado em {zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
