#!/bin/bash
# 4c: ATT&CK Navigator Export (~30 min)
# NOTE: Uses win_splunk_elastic_nav which exports to all SIEM formats

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "4c" "ATT&CK Navigator Export" "~30 minutes" \
    "win_splunk_elastic_nav"
