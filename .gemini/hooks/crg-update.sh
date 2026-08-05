#!/usr/bin/env bash
# code-review-graph: incremental update after write/replace (Gemini CLI hook)
# Must output ONLY JSON on stdout. Low-noise: no systemMessage.
# Falhas nao bloqueiam a sessao, mas sao logadas em .crg-hook.log (antes eram
# descartadas por completo via >/dev/null 2>&1, tornando qualquer falha de
# indexacao indetectavel - ver relatorio 01-relatorio-de-melhorias.md, Secao 2).
set -euo pipefail

cat > /dev/null || true

LOG_FILE="C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao/.crg-hook.log"

set +e
update_out="$(code-review-graph update --skip-flows --repo "C:/Users/trcnologia/Desktop/proj_fabrica-comunicacao" 2>&1)"
update_status=$?
set -e

if [ "$update_status" -ne 0 ]; then
  {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) [crg-update] update retornou exit $update_status"
    printf '%s\n' "$update_out"
  } >> "$LOG_FILE" 2>/dev/null || true
fi

echo '{"suppressOutput": true}'
exit 0
