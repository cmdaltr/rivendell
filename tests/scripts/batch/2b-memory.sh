#!/bin/bash
# 2b: Memory Analysis (~45 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "2b" "Memory Analysis" "~45 minutes" \
    "win_memory_basic" \
    "win_memory_timeline"
