#!/usr/bin/env bash
# PreToolUse — log every bash command Claude runs. Non-blocking.
set -euo pipefail

LOG_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/logs"
mkdir -p "$LOG_DIR"

CMD=$(cat | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', '').strip())
" 2>/dev/null) || CMD="(parse error)"

printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$CMD" >> "$LOG_DIR/command-audit.log"
exit 0
