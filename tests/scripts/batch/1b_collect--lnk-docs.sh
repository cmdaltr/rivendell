#!/bin/bash
# 1b: Collect Files - LNK + Docs (~60 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "1b" "Collect Files - LNK + Docs" "~60 minutes" \
    "win_collect_files_lnk" \
    "win_collect_files_docs"
