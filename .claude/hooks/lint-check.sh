#!/usr/bin/env bash
# PostToolUse — run ruff on Python files after writes. Non-blocking.
set -euo pipefail

FILE=$(cat | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', '').strip())
" 2>/dev/null) || exit 0

[[ -z "$FILE" || "$FILE" != *.py || ! -f "$FILE" ]] && exit 0

command -v ruff &>/dev/null && ruff check "$FILE" --quiet 2>&1 || true
exit 0
