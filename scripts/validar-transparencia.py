#!/usr/bin/env python3
"""
Verifica se a(s) imagem(ns) de produto fornecida(s) têm fundo transparente real
(canal alfa), conforme exigido por compilador-arte/compilador-html/compilador-pdf
para composição sobre gradiente (REGRA 8).

Se a imagem NÃO for transparente, ela é registrada como faltante obrigatório —
a fábrica NÃO gera corte automático nem substitui por outra imagem (REGRA 6).
O operador deve fornecer o PNG já cortado.

Uso:
    python scripts/validar-transparencia.py <slug>

Lê as imagens de output/<slug>/config_projeto.json (campo imagens[].path).
Exit 0 = todas as imagens têm canal alfa com transparência real.
Exit 1 = uma ou mais imagens sem transparência — registra como faltante.

Dependência: Pillow (pip install Pillow)
"""

import argparse
import json
import sys
from pathlib import Path

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_OUTPUT = DIR_PROJETO / "output"

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("[ERRO] Pillow não instalado. Execute: pip install Pillow numpy")
    sys.exit(1)


def tem_transparencia_real(caminho: Path) -> tuple[bool, str]:
    """
    Retorna (True, '') se o PNG tem canal alfa com pixels realmente transparentes.
    Retorna (False, motivo) caso contrário.
    """
    if not caminho.exists():
        return False, f"arquivo não encontrado: {caminho}"

    try:
        img = Image.open(caminho)
    except Exception as e:
        return False, f"erro ao abrir imagem: {e}"

    # Verifica se tem canal alfa
    if img.mode not in ("RGBA", "LA", "PA"):
        return False, f"sem canal alfa (modo: {img.mode}) — forneça PNG com fundo transparente"

    # Verifica se há pixels realmente transparentes (alpha < 255)
    img_rgba = img.convert("RGBA")
    canal_alpha = img_rgba.split()[3]  # canal A
    pixels = list(canal_alpha.getdata())
    pixels_transparentes = sum(1 for p in pixels if p < 255)

    if pixels_transparentes == 0:
        return False, "canal alfa presente mas todos os pixels são opacos (alpha=255) — fundo não foi removido"

    pct = pixels_transparentes / len(pixels) * 100
    return True, f"{pixels_transparentes} pixels transparentes ({pct:.1f}% do total)"


def registrar_faltante(slug: str, imagens_sem_transparencia: list[str]):
    """Registra imagens sem transparência como faltantes no pool de estado, se existir."""
    pool_path = DIR_OUTPUT / slug / "_pool_estado.json"
    if not pool_path.exists():
        return

    try:
        estado = json.loads(pool_path.read_text(encoding="utf-8"))
        faltantes = estado.setdefault("faltantes_transparencia", [])
        for img in imagens_sem_transparencia:
            if img not in faltantes:
                faltantes.append(img)
        pool_path.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> Registrado em {pool_path}")
    except Exception as e:
        print(f"  -> [AVISO] Não foi possível registrar em _pool_estado.json: {e}")


def main():
    ap = argparse.ArgumentParser(description="Valida transparência real (canal alfa) das imagens de produto")
    ap.add_argument("slug")
    args = ap.parse_args()

    config_path = DIR_OUTPUT / args.slug / "config_projeto.json"
    if not config_path.exists():
        print(f"[ERRO] config_projeto.json não encontrado: {config_path}")
        return 1

    config = json.loads(config_path.read_text(encoding="utf-8"))
    imagens = config.get("imagens", [])

    if not imagens:
        print(f"[AVISO] Nenhuma imagem declarada em config_projeto.json")
        return 0

    falhas = []
    for img_entry in imagens:
        # path relativo a output/<slug>/
        path_rel = img_entry.get("path", "")
        descricao = img_entry.get("descricao", path_rel)
        caminho = DIR_OUTPUT / args.slug / path_rel

        ok, detalhe = tem_transparencia_real(caminho)
        if ok:
            print(f"[OK] {path_rel}: {detalhe}")
        else:
            print(f"[FALHA] {path_rel} ({descricao}): {detalhe}")
            print(f"  -> FALTANTE OBRIGATÓRIO: forneça o PNG com fundo transparente (removido manualmente)")
            print(f"  -> A fábrica NÃO gera corte automático — REGRA 6 proíbe alterar a imagem do produto")
            falhas.append(path_rel)

    if falhas:
        registrar_faltante(args.slug, falhas)
        print(f"\n[RESUMO] {len(falhas)}/{len(imagens)} imagem(ns) sem transparência real — adicionar ao manifesto de faltantes")
        return 1

    print(f"\n[RESUMO] Todas as {len(imagens)} imagem(ns) têm transparência real")
    return 0


if __name__ == "__main__":
    sys.exit(main())
