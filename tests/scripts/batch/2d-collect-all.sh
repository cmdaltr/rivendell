#!/bin/bash
# 2d: Collect All Files (~90 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "2d" "Collect All Files" "~90 minutes" \
    "win_collect_files_all"
