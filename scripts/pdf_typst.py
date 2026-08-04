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


def _normalizar_flags_v(comando):
    """Quebra tokens '-V chave=valor' em ['-V', 'chave=valor'].

    Motivo: os compiladores montam o comando a partir da saida de
    `parametros_projeto.py --pdf-vars`, que imprime uma linha '-V chave=valor'
    por par. Se o chamador passar cada linha como UM argv (forma natural de
    copiar a saida), o pandoc interpreta o token '-V chave=valor' como opcao
    '-V' com argumento ' chave=valor' (espaco a esquerda no nome da variavel) e
    a substituicao no template FALHA SILENCIOSAMENTE - o template cai no
    else/default (fonte Arial, cores default) sem nenhum erro, quebrando a
    fidelidade a marca (REGRA 6). Normalizar aqui garante argv separados,
    independente de como o chamador montou a lista.
    """
    novo = []
    for arg in comando:
        arg = str(arg)
        if arg.startswith("-V "):
            # strip(): captura de saida no Windows pode deixar '\r' (CRLF)
            # ou espaco no fim - um '\r' embutido no valor quebraria a
            # variavel no template (ex.: rgb("#0f172a\r")). Nao afeta
            # valores legitimos com espacos internos (ex.: title=Kit Start Flex).
            novo += ["-V", arg[3:].strip()]
        elif arg.startswith("--variable "):
            novo += ["--variable", arg[len("--variable "):].strip()]
        else:
            novo.append(arg)
    return novo


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

    pandoc = subprocess.run(_sem_motor_pdf(_normalizar_flags_v(comando), typ_path),
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
