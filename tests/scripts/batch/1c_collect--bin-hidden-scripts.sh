#!/bin/bash
# 1c: Collect Files - Binaries + Hidden + Scripts (~60 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "1c" "Collect Binaries + Hidden + Scripts" "~60 minutes" \
    "win_collect_files_bin" \
    "win_collect_files_hidden" \
    "win_collect_files_scripts"
