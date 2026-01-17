#!/bin/bash
# 5b: Exhaustive - Disk Only (~180 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "5b" "Exhaustive - Disk Only" "~180 minutes" \
    "win_full"
