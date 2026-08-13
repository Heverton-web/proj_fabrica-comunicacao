#!/usr/bin/env python3
"""
Pre-filtro deterministico de claims para o revisor-marca (REGRA 6).

NAO substitui a checagem semantica do revisor-marca (paráfrase que muda o
sentido nunca aparece so em regex) - so reduz quanto ele precisa "procurar do
zero", sinalizando candidatos (numero/%/hashtag/data/nome-proprio) que
aparecem no material mas nao aparecem literalmente no dossie de insumos.

Achado real que motivou este script: no teste de
melhorias/plano-determinismo-reducao-custos.md, revisor-marca custou mais
token pago do que a propria escrita do conteudo (34,1% vs 23,5% do total) -
e o defeito que ele corrigiu (hashtags de outro nicho coladas por engano)
era exatamente do tipo que um regex pega.

Uso:
    python scripts/extrair-claims-candidatos.py <slug> <tipo>
    # tipo: nome da pasta em output/<slug>/<tipo>/ com arquivos .txt (ex.: "textos")

Sempre sai com exit 0 quando a analise roda (e' assistivo, nao um gate); exit
1 so se a pasta do material ou o dossie nao existirem (erro de uso).
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

PADROES = {
    "percentual": re.compile(r"\d+[.,]?\d*\s*%"),
    "numero_unidade": re.compile(
        r"\d+[.,]?\d*\s*(?:Ncm|mm|cm|kg|g|ml|anos?|dias?|horas?|minutos?)\b", re.IGNORECASE
    ),
    "hashtag": re.compile(r"#\w+"),
    "data": re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"),
    "nome_proprio": re.compile(r"(?:[A-ZÀ-Ú][a-zà-ú]+\s+){1,3}[A-ZÀ-Ú][a-zà-ú]+"),
}


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto.lower().strip()


def _colado(texto_normalizado):
    """Remove espacos - hashtags juntam palavras (#KitTestePainel), entao so
    batem contra uma versao do dossie tambem sem espaco entre palavras."""
    return re.sub(r"\s+", "", texto_normalizado)


def extrair_candidatos(texto):
    """Hashtags sao escaneadas primeiro e mascaradas antes das outras
    categorias - sem isso, um numero/unidade colado dentro de uma hashtag
    (ex.: "#ReuniaoDe15Minutos") gera um sub-match espurio em numero_unidade
    (achado real ao validar contra output/zz-teste-painel-view/textos/)."""
    candidatos = []
    spans_hashtag = []
    for m in PADROES["hashtag"].finditer(texto):
        candidatos.append({"categoria": "hashtag", "trecho": m.group().strip()})
        spans_hashtag.append((m.start(), m.end()))

    texto_mascarado = texto
    for inicio, fim in sorted(spans_hashtag, reverse=True):
        texto_mascarado = texto_mascarado[:inicio] + ("_" * (fim - inicio)) + texto_mascarado[fim:]

    for categoria, padrao in PADROES.items():
        if categoria == "hashtag":
            continue
        for m in padrao.finditer(texto_mascarado):
            candidatos.append({"categoria": categoria, "trecho": m.group().strip()})
    return candidatos


def analisar(slug, tipo):
    pasta_material = DIR_OUTPUT / slug / tipo
    dossie_path = DIR_OUTPUT / slug / "insumos" / "dossie_insumos.md"

    if not pasta_material.exists():
        raise FileNotFoundError(f"pasta do material nao encontrada: {pasta_material}")
    if not dossie_path.exists():
        raise FileNotFoundError(f"dossie de insumos nao encontrado: {dossie_path}")

    dossie_normalizado = _normalizar(dossie_path.read_text(encoding="utf-8"))
    dossie_colado = _colado(dossie_normalizado)

    candidatos_totais = []
    for arquivo in sorted(pasta_material.glob("*.txt")):
        texto = arquivo.read_text(encoding="utf-8")
        for candidato in extrair_candidatos(texto):
            if candidato["categoria"] == "hashtag":
                alvo = _colado(_normalizar(candidato["trecho"])).lstrip("#")
                encontrado = bool(alvo) and alvo in dossie_colado
            else:
                trecho_normalizado = _normalizar(candidato["trecho"])
                encontrado = trecho_normalizado in dossie_normalizado
            candidatos_totais.append(
                {
                    "arquivo": arquivo.name,
                    "categoria": candidato["categoria"],
                    "trecho": candidato["trecho"],
                    "encontrado_no_dossie": encontrado,
                }
            )

    return {
        "slug": slug,
        "tipo": tipo,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "candidatos": candidatos_totais,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("tipo")
    ap.add_argument("--pasta-saida", default=None, help="Sobrescreve output/<slug>/revisao/ (uso em teste)")
    args = ap.parse_args()

    try:
        relatorio = analisar(args.slug, args.tipo)
    except FileNotFoundError as exc:
        print(f"[ERRO] {exc}")
        return 1

    pasta_saida = Path(args.pasta_saida) if args.pasta_saida else DIR_OUTPUT / args.slug / "revisao"
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho_saida = pasta_saida / "candidatos_verificacao.json"
    caminho_saida.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")

    a_verificar = [c for c in relatorio["candidatos"] if not c["encontrado_no_dossie"]]
    print(f"[OK] {len(relatorio['candidatos'])} candidato(s) extraido(s), {len(a_verificar)} a verificar.")
    print(f"Relatorio: {caminho_saida}")
    for c in a_verificar:
        print(f"  - [{c['categoria']}] {c['trecho']!r} em {c['arquivo']} - nao encontrado no dossie")

    return 0


if __name__ == "__main__":
    sys.exit(main())
