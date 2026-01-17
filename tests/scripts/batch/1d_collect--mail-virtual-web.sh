#!/bin/bash
# 1d: Collect Files - Mail + Virtual + Web (~60 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "1d" "Collect Mail + Virtual + Web" "~60 minutes" \
    "win_collect_files_mail" \
    "win_collect_files_virtual" \
    "win_collect_files_web"
