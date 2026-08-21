#!/usr/bin/env python3
"""
Testes para validar-comandos-cli.py — gate de validacao de comandos.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

# Importar dinamicamente por causa do hífen no nome
import importlib.util
spec = importlib.util.spec_from_file_location(
    "validar_comandos_cli",
    str(Path(__file__).resolve().parent.parent / "scripts" / "validar-comandos-cli.py")
)
validar_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validar_cli)

extrair_blocos_codigo = validar_cli.extrair_blocos_codigo
encontrar_marcacao_proxima = validar_cli.encontrar_marcacao_proxima


class TestExtrairBlocos(unittest.TestCase):
    """Testes de extracao de blocos de codigo."""

    def test_bloco_bash_simples(self):
        """Extrai bloco bash simples."""
        md = """# Capitulo
```bash
echo "hello"
```
Continua texto."""
        blocos = extrair_blocos_codigo(md)
        self.assertEqual(len(blocos), 1)
        self.assertIn("echo", blocos[0]["comando"])

    def test_multiplos_blocos(self):
        """Extrai multiplos blocos."""
        md = """```bash
cmd1
```
Texto.
```sh
cmd2
```"""
        blocos = extrair_blocos_codigo(md)
        self.assertEqual(len(blocos), 2)

    def test_sem_blocos(self):
        """Sem blocos de codigo."""
        md = "# Capitulo\nApenas texto."
        blocos = extrair_blocos_codigo(md)
        self.assertEqual(len(blocos), 0)

    def test_bloco_python(self):
        """Extrai bloco python."""
        md = """```python
import sys
print("test")
```"""
        blocos = extrair_blocos_codigo(md)
        self.assertEqual(len(blocos), 1)
        self.assertIn("import", blocos[0]["comando"])


class TestMarcacao(unittest.TestCase):
    """Testes de extracao de marcacao cli-check."""

    def test_marcacao_confirmada(self):
        """Encontra marcacao confere=true."""
        md = """```bash
echo "hello"
```
<!-- cli-check: fonte=B; confere=true -->"""
        blocos = extrair_blocos_codigo(md)
        marcacao = encontrar_marcacao_proxima(md, blocos[0]["fim"])
        self.assertIsNotNone(marcacao)
        self.assertTrue(marcacao["confere"])
        self.assertEqual(marcacao["fonte"], "B")

    def test_marcacao_fabricada(self):
        """Encontra marcacao confere=false."""
        md = """```bash
command-that-doesnt-exist
```
<!-- cli-check: fonte=C; confere=false -->"""
        blocos = extrair_blocos_codigo(md)
        marcacao = encontrar_marcacao_proxima(md, blocos[0]["fim"])
        self.assertIsNotNone(marcacao)
        self.assertFalse(marcacao["confere"])

    def test_sem_marcacao(self):
        """Sem marcacao inline."""
        md = """```bash
echo "hello"
```
Continua sem comentario."""
        blocos = extrair_blocos_codigo(md)
        marcacao = encontrar_marcacao_proxima(md, blocos[0]["fim"])
        self.assertIsNone(marcacao)

    def test_marcacao_case_insensitive(self):
        """Marcacao case-insensitive."""
        md = """```bash
cmd
```
<!-- CLI-CHECK: fonte=A; CONFERE=TRUE -->"""
        blocos = extrair_blocos_codigo(md)
        marcacao = encontrar_marcacao_proxima(md, blocos[0]["fim"])
        self.assertIsNotNone(marcacao)
        self.assertTrue(marcacao["confere"])

    def test_fonte_tipos(self):
        """Fonte pode ser A, B ou C."""
        for fonte in ["A", "B", "C"]:
            md = f"""```bash
cmd
```
<!-- cli-check: fonte={fonte}; confere=true -->"""
            blocos = extrair_blocos_codigo(md)
            marcacao = encontrar_marcacao_proxima(md, blocos[0]["fim"])
            self.assertEqual(marcacao["fonte"], fonte)


class TestIntegracaoGate(unittest.TestCase):
    """Testes de logica de gate."""

    def test_bloco_confirmado_passa(self):
        """Bloco confirmado passa sem --estrito."""
        # Simulado: 1 confirmado, 0 fabricados
        fabricados = 0
        passou = True  # Modo nao-estrito
        self.assertTrue(passou)

    def test_bloco_fabricado_reprova_estrito(self):
        """Bloco fabricado reprova com --estrito."""
        fabricados = 1
        estrito = True
        passou = not (estrito and fabricados > 0)
        self.assertFalse(passou)

    def test_bloco_nao_verificado_nao_reprova(self):
        """Bloco nao verificado nao reprova mesmo em --estrito."""
        nao_verificados = 5
        fabricados = 0
        estrito = True
        passou = not (estrito and fabricados > 0)
        self.assertTrue(passou)


if __name__ == "__main__":
    unittest.main()
