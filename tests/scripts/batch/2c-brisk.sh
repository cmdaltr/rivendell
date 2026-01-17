#!/bin/bash
# 2c: Brisk Mode (~10 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "2c" "Brisk Mode" "~10 minutes" \
    "win_brisk"
