#!/usr/bin/env bash
# PreToolUse — block file writes containing secrets.
# Exit 1 blocks the write; exit 0 allows it.
set -euo pipefail

CONTENT=$(cat | python3 -c "
import json, sys
data = json.load(sys.stdin)
ti = data.get('tool_input', {})
# Write uses 'content'; Edit uses 'new_string'
print(ti.get('content', '') + '\n' + ti.get('new_string', ''))
" 2>/dev/null) || exit 0

[[ -z "$CONTENT" ]] && exit 0

PATTERNS=(
    'sk-ant-[a-zA-Z0-9\-_]{40,}'
    'sk-[a-zA-Z0-9]{48}'
    'ghp_[a-zA-Z0-9]{36}'
    'github_pat_[a-zA-Z0-9_]{82}'
    'AKIA[0-9A-Z]{16}'
    'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'
    '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
    '(password|passwd|secret|api_key|token)\s*=\s*["'"'"'][^"'"'"']{8,}'
)

for pattern in "${PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -qiE "$pattern" 2>/dev/null; then
        echo "secret-scan: blocked — matches pattern: $pattern" >&2
        exit 1
    fi
done

exit 0
