#!/bin/bash
# 5c: Exhaustive - Memory Only (~90 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "5c" "Exhaustive - Memory Only" "~90 minutes" \
    "win_memory_basic" \
    "win_memory_timeline"
