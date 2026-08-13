import json
import subprocess
import sys
from pathlib import Path

import pytest

from parametros_projeto import (
    DECOMPOSICAO_OBJETIVO_TOM,
    OBJETIVOS_TOM_VALIDOS,
    decompor_objetivo_tom,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_decomposicao_cobre_todos_os_objetivos_tom_validos():
    assert set(DECOMPOSICAO_OBJETIVO_TOM) == OBJETIVOS_TOM_VALIDOS


@pytest.mark.parametrize(
    "objetivo_tom,esperado",
    [
        ("educacional_comercial", {"objetivo": "educacional", "tom_de_voz": "comercial"}),
        ("informacional_tecnico", {"objetivo": "informacional", "tom_de_voz": "tecnico"}),
        (
            "comercial_informacional_parceria",
            {"objetivo": "comercial", "tom_de_voz": "informacional_tecnico_de_parceria_de_venda"},
        ),
    ],
)
def test_decompor_objetivo_tom_valores_fixos(objetivo_tom, esperado):
    assert decompor_objetivo_tom(objetivo_tom) == esperado


def test_decompor_objetivo_tom_rejeita_valor_invalido():
    with pytest.raises(ValueError):
        decompor_objetivo_tom("tom-que-nao-existe")


def test_decompor_objetivo_tom_retorna_copia_nao_a_referencia():
    resultado = decompor_objetivo_tom("educacional_comercial")
    resultado["objetivo"] = "alterado"
    assert DECOMPOSICAO_OBJETIVO_TOM["educacional_comercial"]["objetivo"] == "educacional"


def test_cli_decompor_objetivo_tom_imprime_json():
    resultado = subprocess.run(
        [sys.executable, "scripts/parametros_projeto.py", "--decompor-objetivo-tom", "educacional_comercial"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert resultado.returncode == 0
    assert json.loads(resultado.stdout) == {"objetivo": "educacional", "tom_de_voz": "comercial"}


def test_cli_decompor_objetivo_tom_invalido_retorna_erro():
    resultado = subprocess.run(
        [sys.executable, "scripts/parametros_projeto.py", "--decompor-objetivo-tom", "invalido"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert resultado.returncode == 1
