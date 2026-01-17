#!/bin/bash
# 4a: Splunk Export (~60 min)
# NOTE: Uses win_splunk_elastic_nav which exports to all SIEM formats

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "4a" "Splunk Export" "~60 minutes" \
    "win_splunk_elastic_nav"
