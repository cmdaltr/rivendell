#!/bin/bash
# 3c: YARA Scanning (~45 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "3c" "YARA Scanning" "~45 minutes" \
    "win_yara"
