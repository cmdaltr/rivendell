#!/usr/bin/env bash
# SessionStart — inject project threat model into Claude's context.
# No threat-model.md yet? This exits silently.
set -euo pipefail

THREAT_MODEL="${CLAUDE_PROJECT_DIR:-.}/.claude/threat-model.md"
if [[ -f "$THREAT_MODEL" ]]; then
    echo "=== PROJECT THREAT MODEL ==="
    cat "$THREAT_MODEL"
    echo "=== END THREAT MODEL ==="
fi
exit 0
