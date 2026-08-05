#!/usr/bin/env bash
# code-review-graph: incremental update after write/replace (Gemini CLI hook)
# Must output ONLY JSON on stdout. Low-noise: no systemMessage.
set -euo pipefail

cat > /dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_FILE="${REPO_DIR}/.crg-hook.log"

set +e
update_out="$(code-review-graph update --skip-flows --repo "${REPO_DIR}" 2>&1)"
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
