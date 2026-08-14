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
- Inclui GUIA-DO-CONSULTOR.html (guia institucional fixo de como usar cada
  material em cada canal, copiado de templates/guia-consultor-conexao.html)
  na raiz do pacote.
- Gera tambem o zip distribuicao_<slug>.zip DENTRO da pasta distribuicao/
  (conteudo identico ao da pasta, sem o proprio zip).
- REGRA INTOCAVEL: kit-consultor, kit-distribuidor e arte-01/02/03, tanto na
  pasta distribuicao/ quanto no .zip, contem SOMENTE .png e .txt de cada peca -
  nunca index.html, assets/ (fontes/logos/imagem de produto) ou conteudo.json
  (esses continuam existindo em output/<slug>/kit-*/ e output/<slug>/arte-0N/,
  so nao entram no pacote entregue ao cliente). Para arte-01/02/03 os .txt sao
  as 9 legendas de publicacao (instagram/linkedin/whatsapp x 3 copies), que
  moram em output/<slug>/arte/ (compartilhadas entre os 3 formatos) e sao
  copiadas para dentro de cada pasta arte-0N/ do pacote.

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

sys.path.append(str(Path(__file__).resolve().parent))
from _tipos_comuns import KITS, tipo_base

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

NOME_PACOTE = "distribuicao"
ARTES = {"arte-01", "arte-02", "arte-03"}
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
    """Copia o artefato final do tipo para o pacote. PDF vira so o .pdf; kits
    (kit-consultor/kit-distribuidor) e artes (arte-01/02/03) copiam SO .png e
    .txt de cada peca, sem index.html/assets/conteudo.json (REGRA INTOCAVEL:
    kit e arte no pacote de distribuicao e no .zip so podem conter .png +
    .txt); os demais tipos copiam a pasta inteira (HTML precisa de assets/;
    textos dos .txt). Retorna True se copiou."""
    base_origem = DIR_OUTPUT / slug
    destino = base_origem / NOME_PACOTE / destino_tipo
    destino.mkdir(parents=True, exist_ok=True)

    if destino_tipo == "pdf":
        pdfs = sorted(origem_tipo.glob("*.pdf"))
        if not pdfs:
            return False
        shutil.copy2(pdfs[0], destino / pdfs[0].name)
        return True

    if tipo_base(destino_tipo) in ARTES:
        copiado = False
        for png in sorted(origem_tipo.glob("*.png")):
            if png.stat().st_size > 0:
                shutil.copy2(png, destino / png.name)
                copiado = True
        # As 9 legendas de publicacao (3 copies x 3 canais) vivem em
        # output/<slug>/arte/ (compartilhadas entre arte-01/02/03 - ver
        # SPEC_ARTE.md), nao dentro da propria pasta de formato; cada variante
        # de arte no pacote precisa levar sua propria copia dos .txt.
        pasta_legendas = base_origem / "arte"
        for legenda in sorted(pasta_legendas.glob("legenda_copy*_*.txt")):
            if legenda.stat().st_size > 0:
                shutil.copy2(legenda, destino / legenda.name)
                copiado = True
        return copiado

    if tipo_base(destino_tipo) in KITS:
        copiado = False
        for arquivo in sorted(origem_tipo.rglob("*")):
            if not arquivo.is_file() or arquivo.suffix.lower() not in (".png", ".txt"):
                continue
            relativo = arquivo.relative_to(origem_tipo)
            if "assets" in relativo.parts:
                # assets/ (fontes/logos/imagem de produto) sao insumo do render,
                # nao artefato final - REGRA INTOCAVEL exclui do pacote
                continue
            alvo = destino / relativo
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(arquivo, alvo)
            copiado = True
        return copiado

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
        if tipo_base(tipo) != tipo:
            # Entrada versionada do manifesto (ex.: 'pdf-v2', 'arte-01-v2') -
            # a entrada base ('pdf', 'arte-01') ja empacota a versao mais
            # recente (maior -vN, REGRA 11). Ignorar aqui evita duplicar
            # 'pdf' + 'pdf-v2' no pacote e, pior, copiar a pasta versionada
            # inteira (incluindo .md/assets de trabalho) no destino '-v2'.
            continue
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

    guia = DIR_PROJETO / "templates" / "guia-consultor-conexao.html"
    if guia.exists():
        shutil.copy2(guia, pacote / "GUIA-DO-CONSULTOR.html")

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
