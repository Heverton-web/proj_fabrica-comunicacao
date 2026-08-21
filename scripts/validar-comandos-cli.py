#!/usr/bin/env python3
"""
Gate de Validacao de Comandos/CLI em Livros Tecnicos
Valida se comandos, flags e caminhos citados em capitulos tecnicos
foram verificados contra fonte oficial.

Marcacao no markdown (comentario HTML, invisível no PDF):
    ```bash
    docker run -it ubuntu:22.04 /bin/bash
    ```
    <!-- cli-check: fonte=B; confere=true -->

Estados:
  - CONFIRMADO: confere=true (comando verificado e correto)
  - FABRICADO: confere=false (revisor sabe que está errado)
  - NAO_VERIFICADO: sem marcacao (gera aviso mas nao reprova)

Uso:
    python scripts/validar-comandos-cli.py <slug> [--estrito]

--estrito: reprova se algum comando tem confere=false
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tipos_comuns import tipo_base

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

# Regex para encontrar blocos de codigo (```bash, ```sh, etc.)
RE_BLOCO_CODIGO = re.compile(
    r"```(?:bash|sh|shell|zsh|powershell|cmd|python)\n(.*?)\n```",
    re.DOTALL
)

# Regex para encontrar marcacao cli-check
RE_CLI_CHECK = re.compile(
    r"<!--\s*cli-check:\s*fonte=([ABC]);\s*confere=(true|false)\s*-->",
    re.IGNORECASE
)


def extrair_blocos_codigo(conteudo_md):
    """Extrai blocos de codigo com posicao no arquivo."""
    blocos = []
    for match in RE_BLOCO_CODIGO.finditer(conteudo_md):
        blocos.append({
            "comando": match.group(1).strip(),
            "inicio": match.start(),
            "fim": match.end(),
        })
    return blocos


def encontrar_marcacao_proxima(conteudo_md, pos_fim_bloco):
    """Encontra a proxima marcacao cli-check apos a posicao."""
    # Procura ate 200 caracteres depois do bloco (para comentario inline)
    slice_conteudo = conteudo_md[pos_fim_bloco : pos_fim_bloco + 200]
    match = RE_CLI_CHECK.search(slice_conteudo)
    if match:
        return {
            "fonte": match.group(1),
            "confere": match.group(2).lower() == "true",
        }
    return None


def validar_comandos_cli(slug, pasta=None, estrito=False):
    """Valida comandos CLI em um livro tecnico."""
    slug_dir = DIR_OUTPUT / slug

    # Localizar arquivo de conteudo
    # Padroes: capitulos/<numero>-*.md, secoes/*, etc.
    conteudo_files = list(slug_dir.glob("**/*.md"))
    if not conteudo_files:
        return {
            "slug": slug,
            "total_blocos": 0,
            "confirmados": 0,
            "fabricados": 0,
            "nao_verificados": 0,
            "erros": ["Nenhum arquivo .md encontrado"],
            "passou": True,
        }

    total_blocos = 0
    confirmados = 0
    fabricados = 0
    nao_verificados = 0
    erros = []

    for arquivo in conteudo_files:
        conteudo = arquivo.read_text(encoding="utf-8")
        blocos = extrair_blocos_codigo(conteudo)

        for bloco in blocos:
            total_blocos += 1
            marcacao = encontrar_marcacao_proxima(conteudo, bloco["fim"])

            if marcacao:
                if marcacao["confere"]:
                    confirmados += 1
                else:
                    fabricados += 1
                    erros.append(
                        f"{arquivo.name}: comando FABRICADO (confere=false): "
                        f"{bloco['comando'][:60]}..."
                    )
            else:
                nao_verificados += 1
                # Aviso mas nao erro em modo estrito
                if len(nao_verificados) <= 3:  # Limitar a 3 avisos
                    erros.append(
                        f"{arquivo.name}: comando NAO_VERIFICADO: "
                        f"{bloco['comando'][:60]}..."
                    )

    # Gate: --estrito reprova se houver fabricados
    passou = True
    if estrito and fabricados > 0:
        passou = False

    return {
        "slug": slug,
        "total_blocos": total_blocos,
        "confirmados": confirmados,
        "fabricados": fabricados,
        "nao_verificados": nao_verificados,
        "erros": erros,
        "passou": passou,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Valida comandos CLI em livros tecnicos"
    )
    parser.add_argument("slug", help="Slug do projeto")
    parser.add_argument("--estrito", action="store_true", help="Gate determinístico")
    parser.add_argument(
        "--output-json",
        help="Salvar resultado em JSON",
    )
    args = parser.parse_args()

    resultado = validar_comandos_cli(args.slug, estrito=args.estrito)

    # Output
    print(f"[VALIDACAO CLI] {args.slug}")
    print(f"  Total blocos de codigo: {resultado['total_blocos']}")
    print(f"  Confirmados: {resultado['confirmados']}")
    print(f"  Fabricados: {resultado['fabricados']}")
    print(f"  Nao verificados: {resultado['nao_verificados']}")

    if resultado["erros"]:
        print(f"\nAvisos/Erros ({len(resultado['erros'])}):")
        for erro in resultado["erros"]:
            print(f"  - {erro}")

    if args.output_json:
        output_dir = Path(args.output_json).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

    if resultado["passou"]:
        print(f"\n[OK] Validacao passou", flush=True)
        return 0
    else:
        print(f"\n[ERRO] Validacao reprovou (modo --estrito)", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
