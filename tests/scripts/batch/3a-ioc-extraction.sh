#!/bin/bash
# 3a: IOC Extraction (~60 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "3a" "IOC Extraction" "~60 minutes" \
    "win_extract_iocs" \
    "win_timeline"
