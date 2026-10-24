# Rivendell Test Lab

Targets to acquire with Gandalf and datasets to analyse with Mordor, all on one machine. Containers and VMs are seeded with known artefacts: persistence entries, suspicious shell history, IOCs on documentation-only addresses (198.51.100.0/24, `*.rivendell-lab.test`), YARA bait strings. Each target also gets an `expected.json` listing what Elrond should find, with MITRE ATT&CK IDs. Nothing in the lab is malicious, and all networking is loopback or host-only.

`lab.sh` detects the host OS and CPU and uses the right tooling:

| Host | Linux targets | Linux VM | macOS VM | Windows VM | Mordor capture |
|---|---|---|---|---|---|
| macOS, Intel | 4 containers | Vagrant + VirtualBox | — (Tart needs Apple silicon) | Windows 11 x64, unattended | Yes |
| macOS, Apple silicon | 4 containers | Tart | Tart | Windows 11 ARM in UTM, guided | Download only |
| Linux x86-64 | 4 containers | Vagrant + VirtualBox | — (macOS licensing) | Windows 11 x64, unattended | Yes |
| Linux arm64 | 4 containers | — | — | — | Download only |

On Windows hosts, run the lab inside WSL2.

## Requirements

- Rivendell installed and running (`docker compose ... up -d`; see [QUICKSTART](../docs/QUICKSTART.md)), on Docker Desktop or OrbStack. The lab builds its containers on the same engine.
- 16 GB RAM minimum; 32 GB if you want the Windows VM and Rivendell's SIEM profile up together.
- Free disk: about 5 GB for the containers, plus 15 GB for the Windows box, 30 GB for the macOS image, and 2–10 GB for Mordor datasets. VMs can live on an external drive (see [Settings](#settings)).
- An admin password for this machine, the first time only (Homebrew, VirtualBox).

## First Run

```bash
cd lab
./lab.sh
```

Choose **1) Quickstart**. It checks the host, offers to install what's missing, asks where to keep data and VMs, and asks for a lab password: the `gandalf` user on every target gets this password, and it's stored in your Keychain (or the Secret Service keyring on Linux), never on disk. Then it builds and starts the Linux containers, collects from them with both the Bash and Python collectors, downloads APT29 days 1–2 from OTRF, and writes the settings Rivendell's test runner needs.

The same steps exist as single commands:

```bash
./lab.sh check                      # what this host can run, and what's missing
./lab.sh install                    # Homebrew/apt/dnf packages for this profile
./lab.sh configure                  # data location, VM directory, VM sizes, password
./lab.sh linux-targets up           # lab-ubuntu, lab-debian, lab-rocky, lab-alpine
./lab.sh gandalf-collect bash       # every running target; or name them:
./lab.sh gandalf-collect python "lab-debian lab-rocky"
./lab.sh mordor-download apt29/day1 apt29/day2
./lab.sh rivendell-env
```

`./lab.sh help` lists everything.

## Running It from the Web UI

Start the lab agent on the machine running Rivendell:

```bash
cd lab
./lab.sh agent start
```

Then sign in to Rivendell as an admin and open **Lab** in the navigation bar. The page shows the host profile, lets you edit settings and set the lab password, and has buttons for every lab step except `install`, which needs your password at a terminal. The command output streams into the page, and a run can be cancelled.

The agent is a small Python service (standard library only) on loopback port 5691. It accepts only the lab commands, with validated arguments, and runs one at a time. Its access token is regenerated on each start and written to `/tmp/rivendell/.lab-agent/token`, which the Rivendell backend already mounts. The page also stays off until the backend's `SECRET_KEY` is set, because the default JWT secret would let anyone mint an admin token. Stop the agent with `./lab.sh agent stop`.

## Gandalf Targets

The four **Linux containers** (Ubuntu 24.04, Debian 12, Rocky 9, Alpine) listen for SSH on `127.0.0.1:2221–2224`. They are quick to rebuild (`linux-targets reset`), but there's no real kernel, so memory acquisition can't be tested against them.

The **Linux VM** (`linux-vm create`) is Ubuntu with a real kernel (`bento/ubuntu-24.04` under Vagrant, Cirrus Labs `ubuntu:latest` under Tart), on SSH port 2230. The **macOS VM** (`macos-vm create`, Apple silicon only) is a Cirrus Labs Sequoia image on port 2231. It needs one manual step on first boot, which the script prints.

The **Windows VM** (`windows-vm create`, x86-64 hosts) is Windows 11 from `gusztavvargadr/windows-11`. Provisioning enables PowerShell remoting and seeds a Run key, a scheduled task, a service, failed logons and PSReadLine history. The first boot takes 10–20 minutes. On Apple silicon, `./lab.sh windows-vm` walks you through a Windows 11 ARM install in UTM; DumpIt is x64-only, so Windows memory acquisition can't be tested there.

The collectors run from a controller container (`rivendell-lab-controller`) that reaches the VMs via `host.docker.internal`, so nothing is installed on the host. Output goes where Elrond's `--Gandalf` mode expects it:

```
<data>/gandalf/<collector>_collection/acquisitions/<target>/
```

Each target folder also gets that target's `expected.json` and a `collector.log`.

The Bash collector runs unencrypted by default; set `GANDALF_ENCRYPTION=Key` to test Key encryption (the key comes back as `<target>.shadowfax.key` next to the archive). The lab runs Gandalf as shipped. `GANDALF_WORKAROUNDS=1` repacks `.tar.gz` archives as `.zip`, for Rivendell builds whose Elrond predates `.tar.gz` support (bug E7 in [BUGS.md](../tests/docs/BUGS.md)).

## Mordor Datasets

`mordor-download` fetches only the OTRF Security-Datasets that Rivendell's tests reference: a sparse, blob-less clone, so you don't pull the multi-gigabyte repository. It unpacks them under `<data>/mordor/<test path>/` and writes a `manifest.json`. `--list` shows the mapping without downloading.

On x86-64 hosts you can also generate your own datasets:

```bash
./lab.sh mordor-sensor               # Sysmon (sysmon-modular), PowerShell logging, Atomic Red Team
./lab.sh mordor-capture persistence  # presets: persistence, credential_access, defense_evasion, discovery
./lab.sh mordor-capture custom my_set T1059.001,T1003.001
```

Each capture runs the Atomic tests, exports the Sysmon, Security and PowerShell logs as OTRF-style JSONL, and writes a zip with an `expected.json` of the techniques run. Elrond's `--Mordor` mode can't ingest OTRF JSON yet (bug E6), so the Mordor tests will fail until it can.

## Running Rivendell's Tests Against the Lab

```bash
./lab.sh rivendell-env
set -a; . ~/.config/rivendell-lab/rivendell-tests.env; set +a
python3 tests/scripts/run_test.py --run-tags gandalf
```

Elrond's `--Gandalf` mode currently identifies the collected hosts but doesn't process their artefacts (bug E18), so these tests run but produce no analysis yet.

`rivendell-env` also checks that Rivendell's worker can see the lab's data directory. If it can't, it generates `lab/docker-compose.lab.yml` and prints the command to recreate the backend and worker with that extra mount.

## Settings

Settings live in `~/.config/rivendell-lab/lab.conf`. Edit them with `./lab.sh configure` or from the web UI. Environment variables of the same name win for one-off runs.

| Setting | Default | |
|---|---|---|
| `LAB_DATA_DIR` | `~/rivendell-lab-data` | Collected data and datasets |
| `TEST_IMAGES_PATH` | — | When set, data goes to `$TEST_IMAGES_PATH/gandalf` and `/mordor`, the paths `run_test.py` uses |
| `LAB_VM_DIR` | `$LAB_DATA_DIR/vms` | Vagrant boxes, VirtualBox VMs and Tart images. Existing lab VMs in the default locations are left where they are |
| `WINDOWS_VM_MEMORY_MB` / `WINDOWS_VM_CPUS` | 6144 / 2 | |
| `LINUX_VM_MEMORY_MB` | 2048 | |

Unattended runs: `LAB_YES=1` accepts every default, `LAB_FORCE=1` answers yes to everything, and `LAB_PASSWORD` supplies the lab password instead of the keyring.

## Tearing Down

```bash
./lab.sh teardown
```

This removes the lab's containers, volumes and VMs; collected data is kept, and so are the built `rivendell-lab-*` images (remove them with `docker rmi` if you want the space back). It asks whether to remove the stored password too. The lab only touches the `rivendell-lab` compose project and its own VMs; other containers and VMs on the machine (Tart or VirtualBox) are left alone.

## Troubleshooting

- **The image build hangs on "load build context".** This happens when the repo is in a cloud-synced folder (OneDrive, iCloud). The lab avoids it by streaming the context as a tar; if you build by hand, do the same.
- **"No input … menus need a terminal".** You ran `lab.sh` without a terminal and without a command. Pass a command, or set `LAB_YES=1`.
- **The web UI says the agent isn't reachable.** Check `./lab.sh agent status` and `~/.config/rivendell-lab/run/agent.log`. On Linux, the backend needs `host.docker.internal`, which `docker-compose.yml` maps to the host gateway.
- **Collector failures.** Each collection leaves `collector.log` next to its archive (`collector-python.log` for the Python collector), and the lab's known Gandalf issues are tracked in [BUGS.md](../tests/docs/BUGS.md).
