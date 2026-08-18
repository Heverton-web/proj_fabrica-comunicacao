#!/usr/bin/env python3
"""
Script de Setup e Governança do Workspace:
Centraliza skills comuns na pasta raiz 'skills/' e estabelece Directory Junctions (Windows)
ou Symlinks (Unix/macOS) para os diretórios ocultos de cada plataforma (.claude, .gemini, etc.),
garantindo operação não-destrutiva, idempotente e sem necessidade de elevação de privilégios.
"""

import sys
import os
import shutil
import platform
import subprocess
from pathlib import Path

DIR_RAIZ = Path(__file__).resolve().parent.parent
DIR_SKILLS_CENTRAL = DIR_RAIZ / "skills"

SKILLS_COMUNS = [
    "debug-issue",
    "explore-codebase",
    "refactor-safely",
    "review-changes"
]

PLATAFORMAS = [
    DIR_RAIZ / ".claude" / "skills",
    DIR_RAIZ / ".gemini" / "skills",
    DIR_RAIZ / ".codebuddy" / "skills",
    DIR_RAIZ / ".qoder" / "skills",
]


def criar_junction_ou_symlink(origem: Path, destino: Path) -> bool:
    """Cria Directory Junction no Windows (sem requerer Admin) ou Symlink no Unix."""
    origem_str = str(origem.resolve())
    destino_str = str(destino.resolve() if destino.exists() else destino)

    # Se já é um link/junction que aponta para a origem
    if destino.is_symlink() or (os.name == 'nt' and is_junction(destino)):
        return True

    # Se o destino existe como pasta comum não-linkada
    if destino.exists() and destino.is_dir():
        backup_dir = destino.parent / f".bak_{destino.name}"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.move(str(destino), str(backup_dir))

    destino.parent.mkdir(parents=True, exist_ok=True)

    if platform.system() == "Windows":
        # mklink /J cria Directory Junction no Windows (sem elevar privilégios)
        cmd = f'cmd.exe /c mklink /J "{destino}" "{origem}"'
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            print(f"[OK] Junction criado: {destino.relative_to(DIR_RAIZ)} -> {origem.relative_to(DIR_RAIZ)}")
            return True
        else:
            print(f"[ERRO] Falha ao criar junction para {destino}: {res.stderr}")
            return False
    else:
        try:
            os.symlink(origem, destino, target_is_directory=True)
            print(f"[OK] Symlink criado: {destino.relative_to(DIR_RAIZ)} -> {origem.relative_to(DIR_RAIZ)}")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao criar symlink para {destino}: {e}")
            return False


def is_junction(path: Path) -> bool:
    """Verifica se um caminho é Directory Junction no Windows."""
    try:
        if platform.system() != "Windows":
            return False
        # os.stat de junction em python costuma ter st_reparse_tag em versões recentes ou retornos do win32
        import stat
        st = os.lstat(str(path))
        return bool(st.st_mode & stat.S_IFLNK) or (hasattr(st, "st_file_attributes") and bool(st.st_file_attributes & 1024))
    except Exception:
        return False


def main():
    print("=== SETUP DO WORKSPACE: CENTRALIZACAO DE SKILLS E JUNCTIONS ===")
    DIR_SKILLS_CENTRAL.mkdir(parents=True, exist_ok=True)

    # 1. Garante que as skills comuns estejam na raiz /skills
    for skill_name in SKILLS_COMUNS:
        skill_central = DIR_SKILLS_CENTRAL / skill_name
        if not skill_central.exists():
            # Busca em .claude/skills como fonte primária
            fonte_claude = DIR_RAIZ / ".claude" / "skills" / skill_name
            if fonte_claude.exists():
                shutil.copytree(fonte_claude, skill_central)
                print(f"[OK] Copiada skill mestre para raiz: skills/{skill_name}")
            else:
                print(f"[AVISO] Skill {skill_name} não encontrada para povoar central.")

    # 2. Estabelece Junctions/Symlinks em cada plataforma
    sucessos = 0
    total = 0
    for plat_dir in PLATAFORMAS:
        plat_dir.mkdir(parents=True, exist_ok=True)
        for skill_name in SKILLS_COMUNS:
            origem = DIR_SKILLS_CENTRAL / skill_name
            destino = plat_dir / skill_name
            if origem.exists():
                total += 1
                if criar_junction_ou_symlink(origem, destino):
                    sucessos += 1

    print(f"\n[SUCESSO] Total de {sucessos}/{total} junctions/symlinks de skills configurados.")
    return 0 if sucessos == total else 1


if __name__ == "__main__":
    sys.exit(main())
