#!/usr/bin/env python3
"""
Token Guard — Cross-check de gasto de tokens
Compara auto-relato (session-cost.jsonl) contra ccusage independente.

Uso:
    python scripts/token-guard.py [--data YYYY-MM-DD] [--verbose]

Se nao especificar data, usa hoje.
Ferramenta best-effort: falhas sao reported mas nao bloqueiam.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Token Guard — validacao cruzada de gasto")
    parser.add_argument("--data", default="", help="Data a validar (YYYY-MM-DD, default=hoje)")
    parser.add_argument("--verbose", action="store_true", help="Output detalhado")
    args = parser.parse_args()

    if not args.data:
        args.data = datetime.now().strftime("%Y-%m-%d")

    print(f"[TOKEN-GUARD] Cross-check de gasto — {args.data}", flush=True)

    # Passo 1: Rodar ccusage
    print(f"  Consultando ccusage...", flush=True)
    try:
        result = subprocess.run(
            "npx ccusage@latest daily --json --since " + args.data + " --until " + args.data,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"  Aviso: ccusage falhou", flush=True)
            return 0
        ccusage_json = result.stdout
    except Exception as e:
        print(f"  Aviso: {e}", flush=True)
        return 0

    # Passo 2: Parse JSON
    try:
        ccusage_data = json.loads(ccusage_json)
    except json.JSONDecodeError:
        print(f"  Aviso: erro ao fazer parse JSON", flush=True)
        return 0

    # Passo 3: Extrair custo
    ccusage_total = 0
    if isinstance(ccusage_data, dict) and "totalCost" in ccusage_data:
        ccusage_total = float(ccusage_data["totalCost"])
    elif isinstance(ccusage_data, list) and len(ccusage_data) > 0:
        ccusage_total = sum(float(item.get("totalCost", 0)) for item in ccusage_data)

    print(f"  ccusage: ${ccusage_total:.2f}", flush=True)

    # Passo 4: Ler session-cost.jsonl
    cost_jsonl = Path(".agents") / "session-cost.jsonl"
    session_total = 0

    if cost_jsonl.exists():
        try:
            with open(cost_jsonl, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or args.data not in linha:
                        continue
                    obj = json.loads(linha)
                    if "cost" in obj:
                        session_total += float(obj["cost"])
            print(f"  session-cost: ${session_total:.2f}", flush=True)
        except Exception as e:
            print(f"  Aviso ao ler session-cost.jsonl: {e}", flush=True)
    else:
        print(f"  Aviso: session-cost.jsonl nao encontrado", flush=True)

    # Passo 5: Comparar
    print("", flush=True)
    if ccusage_total == 0 and session_total == 0:
        print(f"  [OK] Sem gasto", flush=True)
        return 0

    if ccusage_total == 0:
        print(f"  [AVISO] Session reporta gasto, ccusage nao", flush=True)
        return 0

    diferenca_pct = abs(ccusage_total - session_total) / ccusage_total * 100 if ccusage_total > 0 else 0
    diferenca_pct = round(diferenca_pct, 1)

    if diferenca_pct > 20:
        print(f"  [AVISO] Divergencia {diferenca_pct}% > 20% (auto-relato pode estar desatualizado)", flush=True)
    else:
        print(f"  [OK] Divergencia {diferenca_pct}% dentro do esperado", flush=True)

    print("", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
