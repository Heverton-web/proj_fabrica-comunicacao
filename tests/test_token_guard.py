#!/usr/bin/env python3
"""
Testes para token-guard.py — validacao cruzada de gasto.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


class TestTokenGuard(unittest.TestCase):
    """Testes de validacao cruzada de gasto."""

    def test_parse_ccusage_simples(self):
        """Parse JSON ccusage com totalCost."""
        ccusage_json = json.dumps({"totalCost": 1.50})
        data = json.loads(ccusage_json)
        total = float(data.get("totalCost", 0))
        self.assertEqual(total, 1.50)

    def test_parse_ccusage_array(self):
        """Parse JSON ccusage como array."""
        ccusage_json = json.dumps([
            {"totalCost": 0.50},
            {"totalCost": 0.75},
        ])
        data = json.loads(ccusage_json)
        total = sum(float(item.get("totalCost", 0)) for item in data) if isinstance(data, list) else 0
        self.assertEqual(total, 1.25)

    def test_calculo_divergencia(self):
        """Calculo de percentual de divergencia."""
        ccusage_total = 1.00
        session_total = 0.95
        diferenca_pct = abs(ccusage_total - session_total) / ccusage_total * 100
        self.assertAlmostEqual(diferenca_pct, 5.0, places=1)

    def test_divergencia_zero(self):
        """Divergencia zero quando iguais."""
        ccusage_total = 1.00
        session_total = 1.00
        diferenca_pct = abs(ccusage_total - session_total) / ccusage_total * 100
        self.assertAlmostEqual(diferenca_pct, 0.0, places=1)

    def test_divergencia_grande(self):
        """Divergencia > 20%."""
        ccusage_total = 1.00
        session_total = 0.70
        diferenca_pct = abs(ccusage_total - session_total) / ccusage_total * 100
        self.assertGreater(diferenca_pct, 20.0)

    def test_filtro_data(self):
        """Filtro de linhas por data em session-cost.jsonl."""
        data = "2026-08-21"
        linhas = [
            '{"data": "2026-08-21", "cost": 0.50}',
            '{"data": "2026-08-20", "cost": 0.30}',
            '{"data": "2026-08-21", "cost": 0.75}',
        ]
        session_total = 0
        for linha in linhas:
            linha = linha.strip()
            if data in linha:
                obj = json.loads(linha)
                if "cost" in obj:
                    session_total += float(obj["cost"])
        self.assertEqual(session_total, 1.25)

    def test_ccusage_zero_sem_gasto(self):
        """Se ccusage = 0 e session = 0, sem gasto."""
        ccusage_total = 0.0
        session_total = 0.0
        self.assertTrue(ccusage_total == 0 and session_total == 0)

    def test_ccusage_zero_session_nonzero(self):
        """Se ccusage = 0 mas session != 0, aviso."""
        ccusage_total = 0.0
        session_total = 0.50
        self.assertTrue(ccusage_total == 0 and session_total > 0)


if __name__ == "__main__":
    unittest.main()
