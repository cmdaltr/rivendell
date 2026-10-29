# Roadmap: the v2.3 features

Plans for four of the README's v2.3 items: what already exists, what each one needs, and the order to build them in. Everything else requested is in `docs/FEATURE_REQUESTS.md`.

| Feature | Already there | Size | Order |
|---|---|---|---|
| Container forensics | Built (see below) | Done | 1 |
| Threat intelligence | Built (see below) | Done | 2 |
| Collaborative investigation | Built (see below) | Done | 3 |
| ML-based anomaly detection | Stacking, features and baseline built; model and lab evaluation to do | Evaluation left | 4 |

Container forensics goes first because half of it is written. ML goes last because it needs multi-host cases and the lab's ground truth to measure it against, and an unmeasured anomaly score is worse than none.

## Container forensics (Docker, Kubernetes)

**Built.** The outputs are listed in `docs/CLI.md` (Gandalf's Linux table).

- **Collection.** All three collectors take the same set: `gandalf.sh`, `gandalf.py`, and Elrond's image collection in `collect/linux.py`. It covers:
  - each Docker container's `config.v2.json`, `hostconfig.json` and log;
  - static pod manifests, pod logs and the API server's audit log.
- **The writable layer.** Each container's writable layer is listed with hashes, not copied, as `gandalf+container_changes.csv`. That makes the change set the container version of misplaced binaries, without the tens of gigabytes of image layers that `gandalf.py` used to risk.
- **Parsing.** `process/extractions/containers.py` and `k8s_audit.py`, routed from `linux_artefacts.py`.
- **Techniques.** A technique is tagged only where a row justifies it. A container is tagged for what it can reach, not for existing; a Kubernetes component doing its job is never a finding.
- **Exported audit logs.** `python3 -m src.analysis.rivendell.cloud.cli k8s analyze-logs` handles audit logs exported from EKS, AKS or GKE.
- **The lab.** The Linux targets seed a Docker host's and a Kubernetes node's state on disk (`lab/linux-targets/seed/seed-containers.sh`), with the expected results in their `expected.json`. `tests/unit/test_containers.py` runs that seed through collection and processing.

**Still to do.**
- **Rebuild the lab targets** (`./lab.sh linux-targets reset`) and run `gandalf-collect`. That exercises the two Gandalf collectors' copies of the container lists against the seed. So far only Elrond's copy has run against it, in the unit test.
- **containerd's own metadata** (`/var/lib/containerd`, a bbolt database) isn't parsed. On a containerd or CRI-O node, the pod logs, static pods and audit log are covered, but per-container settings come only from Docker.
- **Live container capture** (`docker export`, CRIU checkpoints) stays out of scope. It changes the running state, so if it's ever added it must be an explicit opt-in, recorded in the audit log.

## Threat intelligence integration

**Built.** The package is `src/analysis/rivendell/threat_intel/`, inside Elrond's tree, so the worker has it and the backend mounts it.

- **Schema and loader.** The fixed ten columns are a frozen dataclass (`schema.py`). `iran_apt_loader.py` reads the workbook and finds its header row. Postgres holds the indicators in `threat_intel_indicators`, added by Alembic revision `7c41d2e9a0b3`.
- **Intake.** `sources.py` takes a file and recognises its format. It handles:
  - the workbook;
  - Rivendell's CSV;
  - MITRESaw's procedures CSV;
  - STIX 2.1 bundles;
  - text watchlists;
  - TAXII 2.1 collections (`stix.py`).

  The STIX and TAXII parsers are ported from Archer. `Source Type` records each row's origin, and duplicates are dropped on element, group, technique and source. No columns were added.
- **Matching.** `index.py` infers each indicator's kind and refuses the ones that would flood a case: built-ins, ordinary words, prose, placeholders, bare extensions and shallow directories. Archer's `known_good.json` supplies part of that list. Each element carries its breadth, the number of groups behind it, and an element more than 15 groups use is marked common. Against a whole case, MITRESaw contributes only software names and multi-word command phrases. On a copy of the Windows 11 demo case, that took the result from 86,829 matches (Lazarus first, on `.jpg`) to 42 matches across seven elements.
- **Elrond.** `--threatIntel FILE ...`, or Threat Intelligence on Elrond's page, runs after analysis (`match.py`). It writes `<host>/analysis/threat_intel_matches.csv`, fills `watchlist_match` in `iocs.csv`, and writes the case's `threat_groups.csv`. That file ranks groups by atomic indicators, then specific elements, then technique overlap. Its Basis column states which of those each rank rests on, and a group that overlaps only on techniques says so.
- **Web.** Pippin, the threat intelligence page (`/pippin`), imports files, pulls TAXII collections, lists and removes sources, searches indicators and checks a single value (`/api/threat-intel`, [API.md](API.md#threat-intelligence)). Importing is admin-only on a team server.
- **Eru.** The offline question "Does anything match known threat intelligence?" lists the most specific matches first. `enrich_artefact()` (`threat_intel_routes.enrich_value`) is ready for the planned MCP server.
- **Tests.** `tests/unit/test_threat_intel.py`, and the Eru question in `test_eru_offline.py`.

**Still to do.**
- **Rebuild the images.** The worker image needs a rebuild for `--threatIntel`. The backend image needs one for `openpyxl` (workbook uploads), and the backend container needs recreating for the package mount.
- **Expiry.** Archer expires IPs and domains after 90 days. Here, STIX `valid_until` and confidence aren't kept, because the schema has no column for them. Re-import and delete by source for now.
- **Online lookups** (VirusTotal and the like) stay out. They would be opt-in per case, after the threat model's review of Eru's outbound access.

## Collaborative investigation

**Built.** It works the same on one analyst's machine as on a team server, where access follows job sharing (`auth/access.py`'s job check covers every route, since they're all under `/api/jobs/{id}/case`).

- **Case browser.** **Browse Case** on a completed job opens `/jobs/{id}/case`. It lists each host's cooked artefacts and analysis files, plus the case's own CSVs (`threat_groups.csv`), in paged tables you can filter on any field. It is read-only by construction (`case_files.py`): requests are resolved against `artefacts/cooked/`, `analysis/` and the case root, `raw/` is never reachable, and nothing opens a file for writing.
- **Findings.** ⚑ on any row flags it as a lead or confirms it outright, with a title and an optional technique. The server reads the row itself and stores its file, row reference, SHA-256 and an excerpt. If a re-run or an edited file changes the row, the finding shows "row changed" rather than silently pointing at something else.
- **Notes, assignment and activity.** Notes are Markdown, on the case or on a finding. Each host has an assignee and a status: to do, in progress or done. An append-only feed records who flagged, marked, assigned, noted or exported what. The page polls every 15 seconds.
- **Working at the same time.** Findings, notes and activity are separate rows, so simultaneous additions never collide.
  - A second flag on an already-flagged row is refused with the existing finding's number and author; the second analyst adds a note to it instead.
  - A status change carries the `updated_at` it was made against, and the server refuses it (409) if a colleague changed the finding first; the page then reloads it.
  - The worker's image locks keep two jobs off the same evidence. Re-running a case that already has findings rewrites its cooked output, and the affected findings then show "row changed".
- **Output.** **Report** is Markdown: case notes first, then confirmed findings by host with their notes. **Navigator layer** holds confirmed findings' techniques only. Elrond's own layer is unchanged.
- **Eru.** The offline question "What have analysts confirmed?" lists confirmed findings, then open leads. With a model, confirmed findings go into its context first.
- **Storage.** Four tables, `case_findings`, `case_notes`, `case_hosts` and `case_activity`, added by Alembic revision `4d8b1f6e2c57`.
- **Tests.** `tests/unit/test_case_browser.py` covers the refusals around `raw/`, paging and filters, the finding lifecycle (including a changed row), notes, assignment, activity, the report, the layer and Eru's answer.

**Still to do.**
- **Flagging from an Eru answer.** A finding needs a row, and Eru's answers are prose. This needs Eru to cite rows first.
- **Restart with findings.** Restarting a job that has findings should warn first, since the re-run will change rows they point at.
- **Assignees** are free text, offered from the user directory on a server, not checked against it.
- **Live updates.** Polling is enough at this size. Websockets can wait until someone asks.

## ML-based anomaly detection

"ML-based" is easy to oversell. This plan builds the frequency analysis practitioners already trust first, then features, then a model, and measures each step against the lab before it ships.

**Built: Phases 1, 2 and 4.** The code is `src/analysis/rivendell/analysis/stacking.py`, stdlib only. `--Analysis` runs it on any case with two or more hosts; a value is only called rare among three or more hosts of its OS (`MIN_HOSTS`), since on two, "on one of them" is a diff of their builds. A baseline still applies below that. Linux hosts are compared within their distribution family (Debian, RHEL, SUSE, Arch, Alpine), from os-release or the distro's fingerprints, so a lone Rocky host among Ubuntu ones doesn't make its whole distro rare.

- **Stacking.** For each host, it collects the values the host has in each family:
  - processes (Prefetch, Amcache, 4688, Sysmon 1);
  - parent and child pairs;
  - services (7045, systemd units);
  - scheduled tasks (4698);
  - autoruns (startup items, Linux autostart, BTM);
  - WMI consumers;
  - kernel modules.

  A value on at most a fifth of the hosts of its OS (one, in a small case) goes to the case's `stacking.csv`, which the case browser shows. Families are compared across hosts of the same OS only. A Windows host's programs aren't rare because the case also holds Linux, but a WMI consumer on one of five Windows hosts is rare even when the other four have none. User folders are normalised, so `C:\Users\alice\x` and `C:\Users\bob\x` stack together. A single-host case writes nothing and says so in the log.
- **Features.** Each row's score is the sum of named reasons, and the row lists them:
  - **rare**;
  - **user path** (Users, AppData, Temp, ProgramData, `/tmp`, `/dev/shm`, `/home`);
  - **generated name**;
  - **not in baseline**.

  "Generated name" looks at shape: few vowels, a long consonant run, digits and letters interleaved, or long hex. Entropy alone flagged every long English compound (`backgroundtaskhost.exe`) on the demo case.
- **Baseline.** `python3 -m rivendell.analysis.stacking --baseline OUT CASE...` (from `src/analysis`) writes every value from clean cases. `--stackBaseline OUT` then scores what's absent from it, and with a baseline even a one-OS-host family is scored. It stays a lab-built, local file.
- **Measurement.** `precision_at_k(stacking.csv, seeded values, k)` is the lab's yardstick. `tests/unit/test_stacking.py` seeds an eight-host case (five Windows, three Linux) and requires the seeded values in the top three, plus a mixed-distro case.
- **In the lab (29 October 2026).** `./lab.sh linux-targets stacking` adds two clean Ubuntu targets to the seeded `lab-ubuntu` and `lab-rocky`. Over all four as one case, stacking returned four rows, every one planted on `lab-ubuntu` (`lab-sync.service`, `lab-agent.service` system and user, the `lab updater` autostart): precision@3 of 1.0, no noise. Before Linux hosts were grouped by distro, the same case gave twenty rows, all Rocky's own units.
- **On real data.** Across the two Windows images in `claude_testing`, the two hosts differ in almost everything, which shows how little two hosts give. The list still surfaced `bcwipe service` on the nfury Windows 7 image, a disk wiper.

**Still to do.**
- **Evaluate in the lab per release.** The lab run above is the method; report precision at 20 each release, and add Windows hosts (one seeded among clean ones) when the lab has them. Signed or unsigned, and time of day against the host's logons, aren't features yet, because the cooked artefacts don't carry signatures and logon patterns need a per-host model of their own.
- **Phase 3, the isolation forest: decision deferred (Ben, 29 October 2026).** It would score how unusual each host's values are, not only how many hosts have them, catching what counting can't, such as a process every host runs but with an odd parent or command line on one. Against: `scikit-learn` (with numpy and scipy, about 30–40 MB) in the worker image, which the dependency rule needs agreed, and a score that's harder to explain than stacking's named reasons. Stacking found every plant with no noise on the lab case, so there's nothing yet for a forest to improve on. **Revisit when** a lab or real case has something planted that stacking misses (an odd parent or command line on a common process is the likely first one); measure the forest against stacking on that case with `precision_at_k` before adding the dependency.
- **Eru's "What's rare in this case?"** is held back, as the plan says, until the lab numbers hold up. Until then `stacking.csv` is in the case browser.

## Outstanding (29 October 2026)

What's left after the four features above were built, tested in the lab and documented. Each feature's own "Still to do" holds its longer-term work; this list is the near-term loose ends.

| Item | What it needs |
|---|---|
| Video sections for stacking and container forensics | Narration to draft and approve, then a section each in the walkthrough's `scenes.py` (local, git-ignored; `scripts/docs/video/README.md`). The case browser and Pippin sections are done. |
| Ranking of Windows stacking ties | Measured in the lab on 29 October (`lab/README.md`, clean siblings): the four planted persistence values are found, but share score 2.0 with 66 programs from Prefetch and Amcache that differ only because the seeded VM is days older, and ties sort by family name. Decide whether a rare persistence value (autorun, service, task, WMI consumer, kernel module) should outrank a rare program at the same score. |

## Decisions needed

- `scikit-learn` in the worker image, for Phase 3 of anomaly detection: deferred on 29 October 2026 until stacking misses something (see Phase 3 above for what would reopen it).
