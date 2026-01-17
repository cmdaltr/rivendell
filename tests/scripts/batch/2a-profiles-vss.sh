#!/bin/bash
# 2a: User Profiles + VSS (~90 min)

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "2a" "User Profiles + VSS" "~90 minutes" \
    "win_userprofiles" \
    "win_vss"
