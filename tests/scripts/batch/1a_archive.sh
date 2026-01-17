#!/bin/bash
# 1a: Archive Test (~30 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "1a" "Archive Test" "~30 minutes" \
    "win_archive"
