# Roadmap: the v2.3 features

Plans for four of the README's v2.3 items: what already exists, what each one needs, and the order to build them in. The other two v2.3 items have their own write-ups: lab VM consoles (`docs/SERVER.md`) and the Rocky Linux 9 RPM (`app/README.md`).

| Feature | Already there | Size | Order |
|---|---|---|---|
| Container forensics | Python Gandalf collects `/var/lib/docker`; a Docker parser exists but isn't wired in | Small to medium | 1 |
| Threat intelligence | `--iocsFile` watchlist matching, ATT&CK enrichment, the Iran APT loader's schema | Medium | 2 |
| Collaborative investigation | Job ownership, sharing by name, Eru scoped to visible cases (server mode) | Large (needs a case browser) | 3 |
| ML-based anomaly detection | Nothing | Medium, plus evaluation | 4 |

Container forensics goes first because half of it is written. ML goes last because it needs multi-host cases and the lab's ground truth to measure it against, and an unmeasured anomaly score is worse than none.

## Container forensics (Docker, Kubernetes)

**There now.** `gandalf.py` collects `/var/lib/docker/containers/`, `volumes/` and `overlay2/`. `DockerArtifactParser` in `process/extractions/linux_enhanced.py` parses container configs and logs and names **T1610**, **T1611** and **T1613**, but nothing imports it, so none of that reaches a case. The Bash and PowerShell collectors take nothing container-related, and there's no Kubernetes support.

**Phase 1: Docker on a Linux host.**
- Move the parser into `process/extractions/docker.py` (stdlib, returns rows) and route it from `linux_artefacts.py` into `cooked/docker_containers.csv`: image, command, created, state, privileged, mounts, capabilities, network and PID mode, from each `config.v2.json` and `hostconfig.json`.
- Container logs (`<id>-json.log`) go into the timeline, one row per line, with the container's name.
- Techniques via `_record_techniques`: a privileged container, the Docker socket mounted, or the host PID or network namespace → **T1611**. A container created during the incident window → **T1610**.
- Bash collector parity with Python Gandalf.

**Phase 2: what changed inside each container.** A container's overlay2 upper (`diff`) layer is exactly the set of files changed since its image: the container version of misplaced binaries. List new and modified executables, scripts and cron or init files per container into `cooked/docker_changes.csv`.

The cost is collection size. `overlay2/` holds every image layer and can be tens of gigabytes. Gandalf should take only each running container's upper layer and the metadata, not the lower layers, with a collection option for the full tree.

**Phase 3: containerd, CRI-O and Kubernetes nodes.**
- `/var/lib/containerd`, `/var/log/pods`, `/var/log/containers`, kubelet logs, `/etc/kubernetes/manifests` (static pods are a persistence route) and kubeconfigs on the node.
- Cluster-level evidence is a new source under `cloud/k8s/`, beside AWS, Azure and GCP:
  - API server audit logs;
  - a snapshot of pods, role bindings, service accounts and secret metadata (names, not values);
  - mapped to the ATT&CK Containers matrix.

**Not planned: live container capture.** `docker export` or a CRIU checkpoint changes the running state. If it's ever added, it should be an explicit opt-in, recorded in the audit log.

**Lab.** A Docker host target with a seeded container: privileged, the socket mounted, and a miner-shaped binary in its upper layer. That gives Phase 1 and 2 a known answer.

## Threat intelligence integration

**There now.**
- `--iocsFile` matches extracted IOCs against a text watchlist (`analysis/iocs.py`) and fills `watchlist_match` in `iocs.csv`.
- ATT&CK technique enrichment in `post/mitre/`.
- The Iran APT loader, which is designed but not built. It has a fixed 10-column schema, a `threat_intel_indicators` table and `enrich_artefact()` as Eru's entry point.

**Phase 1: the Iran APT loader, as designed.**
- The schema, table name and function name stay exactly as specified, and the table comes in through an Alembic migration.
- One decision is needed first: the module's path. `rivendell/threat_intel/` no longer works now that `rivendell` is the launcher script. The proposal is `src/analysis/rivendell/threat_intel/iran_apt_loader.py`, inside Elrond's package.

**Phase 2: general intake into the same table.**
- STIX 2.1 bundles and TAXII 2.1 collections: MITRESaw's output, OpenCTI, or MISP's TAXII server.
- `Source Type` records which source each row came from.
- Indicators are deduplicated on value, keeping each source.
- Confidence and expiry come from the STIX object where it has them.

Everything stays in the schema's ten columns, with no new ones, as the threat model requires.

**Phase 3: matching in Elrond.**
- `watchlist_match` reads the table as well as the text file.
- Process names, command lines and file paths from the cooked artefacts go through `enrich_artefact()`. This is where procedure examples (MITRESaw's invocations) earn their place, because they match how a tool was run, not just its hash.
- Matches go to `analysis/threat_intel_matches.csv` with the reference URL.

**Phase 4: groups whose tradecraft overlaps the case.** Rank ATT&CK groups by the case's techniques, weighted by procedure-level matches.

Technique overlap alone is a weak signal: half the matrix is shared by everyone. The page should say so, and should never label a case with a group.

**Eru.** An offline question: "Does anything match known threat intelligence?" Later, `enrich_artefact()` is exposed through the planned MCP server, as the one registration point.

**Network.** Matching runs locally against the table. Online lookups (VirusTotal and the like) are opt-in per case and off by default. The threat model already flags Eru's outbound access for review, and that review happens before any lookup ships.

## Collaborative investigation

**There now (team server).**
- Each job has an owner.
- Owners share jobs with colleagues by name (`job_access`).
- Admins see everything.
- Eru answers only about cases the user can see (`auth/access.py`).

What's missing is anything to collaborate *on*: there's nowhere in the UI to look at a case's rows, so there's nothing to flag, annotate or hand over.

**Phase 1: a case browser.**
- A page per case listing hosts and cooked artefacts.
- Paged, filterable tables over the CSV and JSON, read through the API and checked with `access.case_allowed`.
- Read-only by construction: the API has no write path into `cooked/` or `raw/`.

This page is useful on its own, server or not, which is why it comes first.

**Phase 2: findings.** A `findings` table (Alembic) with these fields:
- case and job;
- artefact file, row reference (file plus row number and a hash of the row, so a re-run can't silently re-point it) and technique;
- status: lead, confirmed or benign;
- author and timestamps.

"Flag as finding" works from any row in the browser and from an Eru answer. A finding references evidence and never copies or alters it.

**Phase 3: notes, assignment and activity.**
- Notes per case and per finding, in Markdown.
- Hosts assigned to analysts, with a status each.
- An activity feed: who flagged, confirmed, shared or re-ran what, following the audit log's pattern.

Polling is enough for teams of this size. Websockets can wait until someone asks.

**Phase 4: output from findings.**
- A case report and a Navigator layer built from *confirmed* findings only. Today's layer is everything Elrond tagged, which is the right default for one analyst but noisy for a report.
- Eru gets "What have analysts confirmed?", and the confirmed findings go into the language model's context first.

**Single-user mode.** Everything above works on one analyst's machine, with that analyst as the only author. Collaboration is the same feature with more than one user, not a separate mode.

## ML-based anomaly detection

"ML-based" is easy to oversell. This plan builds the frequency analysis practitioners already trust first, then features, then a model, and measures each step against the lab before it ships.

**Phase 1: least frequency of occurrence (stacking).**
- Within a case, count across hosts:
  - process names and paths;
  - parent and child pairs;
  - services, scheduled tasks and autoruns;
  - prefetch names;
  - WMI consumers;
  - cron entries and systemd units.
- The long tail goes to `analysis/stacking.csv`.
- It needs no new dependency (`pandas` is already in `requirements/`).

The more hosts a case has, the more it's worth. A single-host case gets nothing from it, and the page should say so instead of showing an empty table.

**Phase 2: features per artefact row.**
- Entropy of names and command lines.
- Path rarity against a clean baseline.
- Signed or unsigned.
- Time of day against the host's own logon pattern.
- The timestomp deltas Elrond already computes.

Each feature is explainable on its own, and that's the point: every score must say which features drove it.

**Phase 3: a model.**
- An isolation forest over the feature table, run in the worker image only.
- This adds `scikit-learn`, a new dependency, so it's checked against `requirements/` first and confirmed before adding.
- Output is a ranked score with its reasons, never a verdict. Nothing is tagged with a technique on the model's say-so.

**Phase 4: a known-good baseline.** Clean lab hosts give a corpus of normal: the same images before the lab seeds them. Shipping a baseline with Rivendell is tempting but goes stale, so it stays a lab-built, local file.

**Evaluation, before any of it ships.** The lab's seeded hosts are labelled data. Report precision at k (are the seeded artefacts in the top 20?) for stacking, features and the model on every release, in the lab's test run. Eru gets "What's rare in this case?" once the numbers hold up.

## Decisions needed

- The threat intelligence module's path (`src/analysis/rivendell/threat_intel/` proposed).
- `scikit-learn` in the worker image, for Phase 3 of anomaly detection.
- Whether collaboration ever needs live updates, or polling is enough.
