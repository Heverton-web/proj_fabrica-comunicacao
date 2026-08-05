#!/usr/bin/env bash
# code-review-graph: session start status (Gemini CLI hook)
# Must output ONLY JSON on stdout. Logs go to file. Never blocks the session.
set -euo pipefail

cat > /dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_FILE="${REPO_DIR}/.crg-hook.log"

set +e
msg_raw="$(code-review-graph status --repo "${REPO_DIR}" 2>&1)"
status_code=$?
set -e

msg="$(printf '%s' "$msg_raw" | head -n 1)"

if [ "$status_code" -ne 0 ]; then
  {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) [crg-session-start] status retornou exit $status_code"
    printf '%s\n' "$msg_raw"
  } >> "$LOG_FILE" 2>/dev/null || true
fi

CRG_MSG="$msg" python3 -c '
import json,os
m=os.environ.get("CRG_MSG","")
print(json.dumps({"systemMessage":m,"suppressOutput":True}))
' 2>/dev/null || echo '{"suppressOutput": true}'
exit 0
