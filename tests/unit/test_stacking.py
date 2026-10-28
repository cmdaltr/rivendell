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
    assert totals["hosts"] == 7
    rows = read(case / "stacking.csv")
    values = [r["Value"] for r in rows]
    # The generated name outranks a merely rare one; the rest are rare on their own
    assert values[0] == "a7f3k9qz2m.exe" and rows[0]["Reasons"] == "rare, generated name"
    assert "commandlineeventconsumer: updater" in values and "diamorphine" in values
    # Windows programs aren't rare for being absent from the Linux hosts, nor Linux modules from Windows
    assert not any(v in values for v in ("svchost.exe", "ext4", "tracker"))
    diamorphine = next(r for r in rows if r["Value"] == "diamorphine")
    assert (diamorphine["Hosts With It"], diamorphine["Hosts In Case"], diamorphine["Hosts"]) == ("1", "2", "WEB02")
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
