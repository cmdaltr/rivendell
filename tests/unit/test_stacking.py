"""Stacking (rivendell/analysis/stacking.py): rare values across hosts, explainable reasons,
families compared only across hosts that have them, a baseline, and precision at k."""
import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# Appended, not prepended: src/analysis/platform would shadow the stdlib module.
sys.path.append(str(REPO / "src" / "analysis"))

from rivendell.analysis.stacking import (build_baseline, looks_generated, precision_at_k,  # noqa: E402
                                         stack_case)

PROGRAMS = ["svchost.exe", "explorer.exe", "msedge.exe", "onedrive.exe", "teams.exe"]


def windows_host(case: Path, name: str, extra=(), wmi=None) -> None:
    cooked = case / name / "artefacts" / "cooked"
    (cooked / "prefetch").mkdir(parents=True, exist_ok=True)
    (cooked / "prefetch" / "prefetch.json").write_text(json.dumps(
        [{"filename": p.upper()} for p in PROGRAMS + list(extra)]))
    if wmi:
        (cooked / "wbem.json").write_text(json.dumps([wmi]))


def linux_host(case: Path, name: str, modules=("ext4", "xfs"), autostart=()) -> None:
    cooked = case / name / "artefacts" / "cooked"
    cooked.mkdir(parents=True)
    with open(cooked / "kernel_modules.csv", "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["Name", "Size", "Instances", "State", "Taint", "Path", "SHA256", "Flag"])
        writer.writerows([[m, "1", "1", "Live", "", "", "", ""] for m in modules])
    with open(cooked / "autostart.csv", "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["Source", "Kind", "Name", "Command", "Flag"])
        writer.writerows([["/etc/xdg/autostart", "desktop", n, c, ""] for n, c in autostart])


def make_case(root: Path) -> Path:
    case = root / "CASE-9"
    for number in range(1, 6):
        windows_host(case, f"WS{number:02}")
    windows_host(case, "WS03", extra=["a7f3k9qz2m.exe"],
                 wmi={"consumer_class": "CommandLineEventConsumer", "consumer_name": "Updater", "consumer_values": ["x"]})
    linux_host(case, "WEB01", autostart=[("tracker", "/usr/bin/tracker")])
    linux_host(case, "WEB02", modules=("ext4", "xfs", "diamorphine"), autostart=[("tracker", "/usr/bin/tracker")])
    linux_host(case, "WEB03", autostart=[("tracker", "/usr/bin/tracker")])
    return case


def read(path: Path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def test_generated_names():
    assert not any(looks_generated(n) for n in ("backgroundtaskhost.exe", "windowsterminal.exe", "svchost.exe",
                                                "am_delta_patch_1.461.197.0.exe", "gsd-print-notifications.service"))
    assert all(looks_generated(n) for n in ("a7f3k9qz2m.exe", "3f2a9c0b1d4e5f60.dll", "ngrxbcpvt.exe"))


def test_stacking_finds_the_seeded_values(tmp_path):
    case = make_case(tmp_path)
    totals = stack_case(str(case))
    assert totals["hosts"] == 8
    rows = read(case / "stacking.csv")
    values = [r["Value"] for r in rows]
    # The generated name outranks a merely rare one; the rest are rare on their own
    assert values[0] == "a7f3k9qz2m.exe" and rows[0]["Reasons"] == "rare, generated name"
    assert "commandlineeventconsumer: updater" in values and "diamorphine" in values
    # Windows programs aren't rare for being absent from the Linux hosts, nor Linux modules from Windows
    assert not any(v in values for v in ("svchost.exe", "ext4", "tracker"))
    diamorphine = next(r for r in rows if r["Value"] == "diamorphine")
    assert (diamorphine["Hosts With It"], diamorphine["Hosts In Case"], diamorphine["Hosts"]) == ("1", "3", "WEB02")
    assert precision_at_k(str(case / "stacking.csv"), ["a7f3k9qz2m", "updater", "diamorphine"], k=3) == 1.0


def test_baseline_and_single_host(tmp_path):
    clean = tmp_path / "CLEAN"
    windows_host(clean, "GOLD", extra=["a7f3k9qz2m.exe"])
    baseline = tmp_path / "baseline.csv"
    assert build_baseline([str(clean)], str(baseline)) == 6
    case = make_case(tmp_path)
    stack_case(str(case), str(baseline))
    rows = {r["Value"]: r for r in read(case / "stacking.csv")}
    assert "not in baseline" not in rows["a7f3k9qz2m.exe"]["Reasons"]
    assert "not in baseline" in rows["commandlineeventconsumer: updater"]["Reasons"]

    single = tmp_path / "ONE"
    windows_host(single, "WS01")
    assert stack_case(str(single)) is None and not (single / "stacking.csv").exists()


def test_two_hosts_of_an_os_are_a_diff_not_a_tail(tmp_path):
    case = tmp_path / "PAIR"
    linux_host(case, "UBUNTU", modules=("ext4", "overlay"))
    linux_host(case, "ROCKY", modules=("ext4", "xfs"))
    stack_case(str(case))
    assert read(case / "stacking.csv") == []
    baseline = tmp_path / "baseline.csv"
    build_baseline([str(tmp_path / "PAIR")], str(baseline))
    linux_host(case, "NEW", modules=("ext4", "diamorphine"))
    stack_case(str(case), str(baseline))
    rows = {r["Value"]: r["Reasons"] for r in read(case / "stacking.csv")}
    assert rows["diamorphine"] == "rare, not in baseline"


def systemd_host(case: Path, name: str, units, os_release: str = "") -> None:
    services = case / name / "artefacts" / "cooked" / "services"
    services.mkdir(parents=True)
    for unit in units:
        (services / f"{unit}.json").write_text("{}")
    if os_release:
        raw = case / name / "artefacts" / "raw" / "conf"
        raw.mkdir(parents=True)
        (raw / "etc+os-release").write_text(os_release)


def test_linux_hosts_compared_within_their_distro(tmp_path):
    case = tmp_path / "MIXED"
    debian = ["apt-daily.service", "dpkg-db-backup.service", "cron.service", "ssh.service"]
    systemd_host(case, "UB1", debian)
    systemd_host(case, "UB2", debian)
    systemd_host(case, "UB3", debian + ["lab-sync.service"])
    # One RHEL host, known only from its os-release: its own units aren't rare among Debian ones
    systemd_host(case, "ROCKY", ["crond.service", "sshd.service", "chronyd.service"],
                 os_release='NAME="Rocky Linux"\nID="rocky"\nID_LIKE="rhel centos fedora"\n')
    stack_case(str(case))
    rows = read(case / "stacking.csv")
    assert [(r["Value"], r["Family"], r["Hosts In Case"]) for r in rows] == \
        [("lab-sync.service", "service (systemd), debian", "3")]
