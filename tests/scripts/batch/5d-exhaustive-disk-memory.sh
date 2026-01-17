#!/bin/bash
# 5d: Exhaustive - Disk + Memory (~240 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "5d" "Exhaustive - Disk + Memory" "~240 minutes" \
    "win_disk_and_memory"
