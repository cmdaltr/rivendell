# Test Results

Last updated: 2024-12-23

## Summary

| Category | Passed | Failed | Incomplete | Skipped | Total |
|----------|--------|--------|------------|---------|-------|
| Windows Disk | 0 | 0 | 0 | 0 | 23 |
| Windows Memory | 0 | 0 | 0 | 0 | 4 |
| Linux Disk | 0 | 0 | 0 | 0 | 26 |
| Linux Memory | 0 | 0 | 0 | 0 | 2 |
| macOS Disk | 0 | 0 | 0 | 0 | 26 |
| macOS Memory | 0 | 0 | 0 | 0 | 2 |
| Multi-Image | 0 | 0 | 0 | 0 | 5 |
| Gandalf | 0 | 0 | 0 | 0 | 10 |
| Cloud | 0 | 0 | 0 | 0 | 11 |
| Mordor | 0 | 0 | 0 | 0 | 11 |
| **Total** | **0** | **0** | **0** | **0** | **120** |

---

## Windows Disk Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| win_archive | 🟢 SUCCESS | 2026-01-08 | 18m | - |
| win_brisk | 🔴 FAILED | 2026-01-08 | 120m | Job timeout after 120 minutes |
| win_carve_unalloc | 🟢 SUCCESS | 2025-12-23 | - | - |
| win_collect_files_all | 🟢 SUCCESS | 2025-12-23 | - | - |
| win_collect_files_archive | 🟢 SUCCESS | 2026-01-09 | 17m | - |
| win_collect_files_bin | 🟢 SUCCESS | 2026-01-09 | 33m | - |
| win_collect_files_docs | 🟢 SUCCESS | 2026-01-09 | 21m | - |
| win_collect_files_hidden | 🟢 SUCCESS | 2026-01-09 | 16m | - |
| win_collect_files_lnk | 🟢 SUCCESS | 2026-01-09 | 17m | - |
| win_collect_files_mail | 🟢 SUCCESS | 2026-01-09 | 17m | - |
| win_collect_files_scripts | 🟢 SUCCESS | 2026-01-09 | 20m | - |
| win_collect_files_virtual | 🟢 SUCCESS | 2026-01-09 | 17m | - |
| win_collect_files_web | 🟢 SUCCESS | 2026-01-09 | 16m | - |
| win_extract_iocs | 🔴 FAILED | 2026-01-09 | 36m | Job stalled at 91% |
| win_full | 🟣 | - | - | - |
| win_keywords | 🔴 FAILED | 2026-01-09 | 120m | Job timeout after 120 minutes |
| win_mordor_mode | 🟣 | - | - | - |
| win_splunk_elastic_nav | 🟣 | - | - | - |
| win_timeline | 🔴 FAILED | 2026-01-09 | 55s | Failed to submit job |
| win_userprofiles | 🔴 FAILED | 2026-01-09 | 55s | Failed to submit job |
| win_verbose | 🔴 FAILED | - | - | Ensuring audit log and Web UI show the same logs |
| win_vss | 🔴 FAILED | 2026-01-09 | 55s | Failed to submit job |
| win_yara | 🔴 FAILED | 2026-01-09 | 55s | Failed to submit job |

## Windows Memory Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| win_disk_and_memory | 🟣 | - | - | - |
| win_memory_basic | 🔴 FAILED | 2026-01-09 | 55s | Failed to submit job |
| win_mem_splunk_elastic_nav | 🟣 | - | - | - |
| win_memory_timeline | 🔴 FAILED | 2026-01-09 | 55s | Failed to submit job |

## Linux Disk Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| linux_analysis | 🟣 | - | - | - |
| linux_archive | 🟣 | - | - | - |
| linux_basic | 🟣 | - | - | - |
| linux_collect_files_all | 🟣 | - | - | - |
| linux_collect_files_archive | 🟣 | - | - | - |
| linux_collect_files_bin | 🟣 | - | - | - |
| linux_collect_files_docs | 🟣 | - | - | - |
| linux_collect_files_hidden | 🟣 | - | - | - |
| linux_collect_files_lnk | 🟣 | - | - | - |
| linux_collect_files_mail | 🟣 | - | - | - |
| linux_collect_files_scripts | 🟣 | - | - | - |
| linux_carve_unalloc | 🟣 | - | - | - |
| linux_collect_files_virtual | 🟣 | - | - | - |
| linux_collect_files_web | 🟣 | - | - | - |
| linux_debug | 🟣 | - | - | - |
| linux_extract_iocs | 🟣 | - | - | - |
| linux_full | 🟣 | - | - | - |
| linux_hash_collected | 🟣 | - | - | - |
| linux_keywords | 🟣 | - | - | - |
| linux_memory | 🟣 | - | - | - |
| linux_memory_timeline | 🟣 | - | - | - |
| linux_mordor_mode | 🟣 | - | - | - |
| linux_splunk_elastic_nav | 🟣 | - | - | - |
| linux_timeline | 🟣 | - | - | - |
| linux_userprofiles | 🟣 | - | - | - |
| linux_yara | 🟣 | - | - | - |

## Linux Memory Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| linux_disk_and_memory | 🟣 | - | - | - |
| linux_mem_splunk_elastic_nav | 🟣 | - | - | - |

## macOS Disk Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| mac_analysis | 🟣 | - | - | - |
| mac_archive | 🟣 | - | - | - |
| mac_basic | 🟣 | - | - | - |
| mac_collect_files_all | 🟣 | - | - | - |
| mac_collect_files_archive | 🟣 | - | - | - |
| mac_collect_files_bin | 🟣 | - | - | - |
| mac_collect_files_docs | 🟣 | - | - | - |
| mac_collect_files_hidden | 🟣 | - | - | - |
| mac_collect_files_lnk | 🟣 | - | - | - |
| mac_collect_files_mail | 🟣 | - | - | - |
| mac_collect_files_scripts | 🟣 | - | - | - |
| mac_carve_unalloc | 🟣 | - | - | - |
| mac_collect_files_virtual | 🟣 | - | - | - |
| mac_collect_files_web | 🟣 | - | - | - |
| mac_debug | 🟣 | - | - | - |
| mac_extract_iocs | 🟣 | - | - | - |
| mac_full | 🟣 | - | - | - |
| mac_hash_collected | 🟣 | - | - | - |
| mac_keywords | 🟣 | - | - | - |
| mac_memory | 🟣 | - | - | - |
| mac_memory_timeline | 🟣 | - | - | - |
| mac_mordor_mode | 🟣 | - | - | - |
| mac_splunk_elastic_nav | 🟣 | - | - | - |
| mac_timeline | 🟣 | - | - | - |
| mac_userprofiles | 🟣 | - | - | - |
| mac_yara | 🟣 | - | - | - |

## macOS Memory Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| mac_disk_and_memory | 🟣 | - | - | - |
| mac_mem_splunk_elastic_nav | 🟣 | - | - | - |

## Multi-Image Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| multi_all_platforms | 🟣 | - | - | - |
| multi_all_with_memory | 🟣 | - | - | - |
| multi_full_exhaustive | 🟣 | - | - | - |
| multi_win_linux | 🟣 | - | - | - |
| multi_win_mac | 🟣 | - | - | - |

## Gandalf Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| gandalf_bash_analysis | 🟣 | - | - | - |
| gandalf_bash_basic | 🟣 | - | - | - |
| gandalf_bash_timeline | 🟣 | - | - | - |
| gandalf_powershell_analysis | 🟣 | - | - | - |
| gandalf_powershell_basic | 🟣 | - | - | - |
| gandalf_powershell_elastic | 🟣 | - | - | - |
| gandalf_powershell_splunk | 🟣 | - | - | - |
| gandalf_python_analysis | 🟣 | - | - | - |
| gandalf_python_basic | 🟣 | - | - | - |
| gandalf_python_full_siem | 🟣 | - | - | - |

## Cloud Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| cloud_aws_disk_analysis | 🟣 | - | - | - |
| cloud_aws_disk_basic | 🟣 | - | - | - |
| cloud_aws_disk_memory_combined | 🟣 | - | - | - |
| cloud_aws_full_pipeline | 🟣 | - | - | - |
| cloud_aws_memory | 🟣 | - | - | - |
| cloud_azure_disk_analysis | 🟣 | - | - | - |
| cloud_azure_disk_basic | 🟣 | - | - | - |
| cloud_azure_disk_memory_combined | 🟣 | - | - | - |
| cloud_azure_full_pipeline | 🟣 | - | - | - |
| cloud_azure_memory | 🟣 | - | - | - |
| cloud_multi_aws_azure | 🟣 | - | - | - |

## Mordor Tests

| Test Name | Status | Date | Duration | Notes |
|-----------|--------|------|----------|-------|
| mordor_apt29_day1 | 🟣 | - | - | - |
| mordor_apt29_day2 | 🟣 | - | - | - |
| mordor_apt29_full | 🟣 | - | - | - |
| mordor_atomic_credential_access | 🟣 | - | - | - |
| mordor_atomic_defense_evasion | 🟣 | - | - | - |
| mordor_atomic_lateral_movement | 🟣 | - | - | - |
| mordor_atomic_persistence | 🟣 | - | - | - |
| mordor_full_detection_test | 🟣 | - | - | - |
| mordor_malware_cobalt_strike | 🟣 | - | - | - |
| mordor_malware_emotet | 🟣 | - | - | - |
| mordor_malware_trickbot | 🟣 | - | - | - |

---

## Failed Test Details

<!--
### test_name
- **Date:** YYYY-MM-DD
- **Error:**
  ```
  Error message here
  ```
- **Root Cause:**
- **Resolution:** Pending / Fixed in commit XXX
-->

---

## Known Issues

- None documented yet

---

## Environment

- **OS:** macOS
- **Docker Version:**
- **Test Images Location:** `/tmp/rivendell` or `/Volumes/Media5TB/rivendell_imgs`
- **API URL:** http://localhost:5688
