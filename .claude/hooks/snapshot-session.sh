#!/usr/bin/env bash
# PreCompact — save git state before Claude compacts the context.
set -euo pipefail

SNAPSHOT_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/snapshots"
mkdir -p "$SNAPSHOT_DIR"

SNAPSHOT="$SNAPSHOT_DIR/session_$(date '+%Y%m%d_%H%M%S').md"
{
    echo "# Session Snapshot — $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "## Git Status"
    git -C "${CLAUDE_PROJECT_DIR:-.}" status --short 2>/dev/null || echo "(not a git repo)"
    echo ""
    echo "## Recent Commits"
    git -C "${CLAUDE_PROJECT_DIR:-.}" log --oneline -10 2>/dev/null || echo "(no commits)"
} > "$SNAPSHOT"

exit 0
