#!/bin/bash
# 4d: All SIEM + Navigator Exports (~60 min)
# Uses win_splunk_elastic_nav which exports to Splunk + Elasticsearch + Navigator

source "$(dirname "${BASH_SOURCE[0]}")/batch_common.sh"

run_batch "4d" "All SIEM + Navigator Exports" "~60 minutes" \
    "win_splunk_elastic_nav"
