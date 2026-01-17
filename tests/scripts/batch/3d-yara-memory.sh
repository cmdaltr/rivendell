#!/bin/bash
# 3d: YARA + Memory Analysis (~60 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "3d" "YARA + Memory Analysis" "~60 minutes" \
    "win_yara" \
    "win_memory_basic"
