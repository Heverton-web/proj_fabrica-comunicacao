#!/usr/bin/env python3
"""
Conversao Markdown -> PDF via Pandoc -> .typ -> Typst (Fabrica Agentica de Livros).

Por que existe: `pandoc --pdf-engine=typst` extrai as imagens do documento para uma
pasta temporaria e reescreve os caminhos em forma ABSOLUTA. O Typst recusa caminho
absoluto no Windows ("path contains invalid component `C:`"), entao qualquer livro com
figuras (por exemplo os diagramas Mermaid renderizados pelo Upgrade 2) falha na
compilacao. Gerando o `.typ` intermediario dentro da pasta do livro, os caminhos
relativos das figuras continuam validos.

Uso (drop-in no lugar de subprocess.run(comando, ...) dos compiladores):

    from pdf_typst import executar
    resultado = executar(comando, pdf_path, dir_livro, TYPST, timeout=600)
    # resultado.stderr / resultado.returncode seguem disponiveis
"""

import subprocess
from pathlib import Path


class Resultado:
    """Compativel com o subprocess.CompletedProcess usado pelos compiladores."""

    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _sem_motor_pdf(comando, typ_path):
    """Remove --pdf-engine e redireciona a saida (-o) para o .typ intermediario."""
    novo = []
    i = 0
    while i < len(comando):
        arg = str(comando[i])
        if arg == "--pdf-engine":
            i += 2
            continue
        if arg.startswith("--pdf-engine="):
            i += 1
            continue
        if arg == "-o" or arg == "--output":
            novo += [arg, str(typ_path)]
            i += 2
            continue
        if arg.startswith("--output="):
            novo.append(f"--output={typ_path}")
            i += 1
            continue
        novo.append(arg)
        i += 1
    return novo


def executar(comando, pdf_path, dir_raiz, typst_bin, timeout=600, manter_typ=False):
    """Roda Pandoc -> .typ e depois typst compile --root <dir_raiz>.

    Retorna um objeto com returncode/stdout/stderr, como subprocess.run.
    """
    pdf_path = Path(pdf_path)
    dir_raiz = Path(dir_raiz)
    typ_path = dir_raiz / f"_{pdf_path.stem}.typ"

    pandoc = subprocess.run(_sem_motor_pdf(comando, typ_path),
                            capture_output=True, text=True, timeout=timeout)
    if not typ_path.exists() or typ_path.stat().st_size == 0:
        return Resultado(pandoc.returncode or 1, pandoc.stdout,
                         (pandoc.stderr or "") + "\npandoc nao gerou o .typ intermediario")

    typst = subprocess.run(
        [str(typst_bin), "compile", "--root", str(dir_raiz), str(typ_path), str(pdf_path)],
        capture_output=True, text=True, timeout=timeout,
    )
    if not manter_typ and pdf_path.exists() and pdf_path.stat().st_size > 0:
        typ_path.unlink(missing_ok=True)

    return Resultado(typst.returncode,
                     (pandoc.stdout or "") + (typst.stdout or ""),
                     (pandoc.stderr or "") + (typst.stderr or ""))
