"""
The Rivendell walkthrough: what's said, and what's on screen while it's said.

Each scene is narrated (Piper) and filmed (Playwright) separately, then make_video.py joins
them. A scene's `chapter` starts a YouTube chapter. Visuals:

  card      a title card over the map: {"kind": "card", "title": ..., "subtitle": ...}
  page      a page of the running web UI or a file: {"kind": "page", "url": ..., "actions": [...]}
  terminal  commands typed into a terminal: {"kind": "terminal", "lines": [...]}

Actions run in order while the narration plays, and the scene holds on the last frame
until the narration ends:

  ("wait", seconds)                 ("scroll", pixels, seconds)
  ("point", selector, seconds)      a pulsing outline round an element (the guide's style)
  ("click", selector)               ("fill", selector, text)
  ("check", selector)               ("key", "ArrowRight")
  ("js", "expression")              ("goto", url)
  ("select", selector, value)

An action whose element isn't on the page is skipped (Eru's questions differ with and
without a model), and the scene carries on.

URLs starting with / are the web UI's (--url). {repo}, {case} and {job} are filled in, and
{case_tree}, {techniques}, {integrity} and {iocs} become the demo case's files.
"""

# How Piper should say what the captions write
SPOKEN = {
    "T1070.006": "T one oh seven oh, point oh oh six",
    "T1564.004": "T one five six four, point oh oh four",
    "T1546.003": "T one five four six, point oh oh three",
    "E01": "E oh one",
    "Windows 11": "Windows eleven",
    "github.com/cmdaltr/rivendell": "github dot com, slash cmd alt r, slash rivendell",
    "Andúril": "Anduril",
    "MITRE ATT&CK": "Miter attack",
    "ATT&CK": "attack",
    "VMDK": "V M D K",
    "CSV": "C S V",
    "JSON": "jason",
    "YARA": "Yara",
    "TLS": "T L S",
    "GPU": "G P U",
}

# Eru's answers land above its question buttons: bring the latest one into shot
ANSWER = "document.querySelector(\"[data-guide='eru.chat']\").lastElementChild?.scrollIntoView({block: 'center', behavior: 'smooth'})"

SCENES = [
    # ── Opening ──────────────────────────────────────────────────────────────────────────
    {
        "id": "open",
        "chapter": "Rivendell",
        "visual": {"kind": "card", "title": "Rivendell", "subtitle": "Acquisition, analysis and an analyst to ask, in one place"},
        "text": (
            "Every investigation starts with the same questions. What happened on this machine, "
            "when, and is it still happening? Rivendell is a digital forensics and incident response "
            "platform built to answer them: it collects evidence from live hosts, processes disk and "
            "memory images into timelines and artefacts, maps what it finds to MITRE ATT&CK, and gives "
            "you an analyst to ask about the case. This walkthrough covers all of it, from installing "
            "it to running it for a whole team."
        ),
    },

    # ── What it is ───────────────────────────────────────────────────────────────────────
    {
        "id": "realm",
        "chapter": "How it fits together",
        "visual": {"kind": "page", "url": "/architecture/rivendell-architecture.html",
                   "actions": [("wait", 4), ("scroll", 500, 6), ("wait", 6), ("scroll", 600, 6)]},
        "text": (
            "Rivendell has three parts, named the way you'd expect. Gandalf does acquisition: "
            "collectors in PowerShell, Python and Bash that run locally or over SSH and PowerShell "
            "Remoting, taking artefacts in order of volatility and hashing everything they collect. "
            "Elrond does the analysis: it drives more than thirty forensic tools, from Volatility and "
            "Plaso to RegRipper, YARA and The Sleuth Kit, and turns their output into one case "
            "directory. And Eru is the analyst you can ask, reading that case directory to answer "
            "questions about it. Around them sit Mordor, recorded attack telemetry, and Aragorn, "
            "which looks after the platform itself."
        ),
    },
    {
        "id": "graph",
        "visual": {"kind": "page", "url": "/architecture/rivendell-architecture.html",
                   "actions": [("js", "window.scrollTo(0, document.body.scrollHeight / 2)"), ("wait", 3),
                               ("scroll", 700, 10)]},
        "text": (
            "Elrond isn't a straight pipeline. It's a directed graph that branches on what you give it: "
            "a Windows disk image takes a different path from a Linux one, a memory image goes to "
            "Volatility, and a Gandalf archive skips the mounting entirely, because it was collected "
            "already. Whatever the route, the output is the same shape: the raw evidence as collected, "
            "cooked CSV and JSON for every artefact, the analysis, a list of ATT&CK techniques, a "
            "timeline and an audit log."
        ),
    },
    {
        "id": "maps",
        "visual": {"kind": "page", "url": "/architecture/rivendell-journey.html",
                   "actions": [("wait", 6), ("click", "[data-src=memory]"), ("wait", 8),
                               ("click", "[data-src=cloud]"), ("wait", 8), ("click", "[data-src=gandalf]"), ("wait", 6)]},
        "text": (
            "If you'd rather see that than hear it, rivendell map opens the pictures: the realm, "
            "which is the whole platform on one page, Elrond's graph and Gandalf's collectors in "
            "detail, and this one, the journey, which follows a single piece of evidence from the "
            "host it was taken from to the answer Eru gives about it. Pick the kind of evidence, a "
            "Gandalf archive, a disk, memory, a Mordor dataset or cloud logs, and it takes the route "
            "Elrond would."
        ),
    },

    # ── Getting it running ───────────────────────────────────────────────────────────────
    {
        "id": "install",
        "chapter": "Installing it",
        "visual": {"kind": "terminal", "lines": [
            "$ git clone https://github.com/cmdaltr/rivendell.git && cd rivendell",
            "$ ./rivendell install",
            "  Linked ~/.local/bin/rivendell",
            "$ rivendell start",
            "  Starting Rivendell...",
            "  Frontend:      http://localhost:5687",
            "  Backend API:   http://localhost:5688",
        ]},
        "text": (
            "Everything runs in Docker. Clone the repository, run the install, and the rivendell "
            "command works from anywhere: rivendell start brings up the web interface, the API, the "
            "worker that runs the tools, and optionally Splunk, Elastic and the ATT&CK Navigator."
        ),
    },
    {
        "id": "app",
        "visual": {"kind": "page", "url": "file://{repo}/app/macos/setup.html",
                   "actions": [("wait", 4), ("scroll", 400, 5), ("wait", 5)]},
        "text": (
            "Or don't touch a terminal at all. There's a desktop app for macOS, Windows and Linux. The "
            "first time it opens, it asks where Rivendell should run: on this machine, where it can "
            "install a container runtime for you, or on your team's server. It sets up the evidence "
            "folders, and from then on it lives in the dock like any other application."
        ),
    },
    {
        "id": "journey",
        "visual": {"kind": "page", "url": "file://{repo}/app/macos/journey.html",
                   "actions": [("js", "progress({fraction: 0.05, eta: 95, phase: 'docker', message: 'Waking Docker'})"),
                               ("wait", 3),
                               ("js", "progress({fraction: 0.35, eta: 60, phase: 'images', message: 'Forging the images'})"),
                               ("wait", 4),
                               ("js", "progress({fraction: 0.7, eta: 25, phase: 'containers', message: 'Raising the halls'})"),
                               ("wait", 4),
                               ("js", "progress({fraction: 0.93, eta: 6, phase: 'ui', message: 'Opening the doors'})"),
                               ("wait", 3),
                               ("js", "progress({fraction: 1, eta: 0, phase: 'ui', message: ''})")]},
        "text": (
            "Starting the stack takes a minute or two, so the app shows Gandalf walking from the Shire "
            "to Rivendell while it happens. The estimate isn't a guess: every start is timed, phase by "
            "phase, and the next estimate is the median of this machine's own history. When images "
            "are being built, it paces itself on the build's own progress instead."
        ),
    },

    # ── First look ───────────────────────────────────────────────────────────────────────
    {
        "id": "home",
        "chapter": "A first look",
        "visual": {"kind": "page", "url": "/", "fresh": True,
                   "actions": [("wait", 6), ("click", "text=Take the guide"), ("wait", 4),
                               ("key", "ArrowRight"), ("wait", 4), ("key", "ArrowRight"), ("wait", 4)]},
        "text": (
            "The first thing you see is an offer: a guide to every page, and a tip. The guide "
            "photographs each page and walks through it section by section, saying what each part is "
            "for, who uses it, and when it helps most. The tips cover the things that are easy to "
            "miss, picked at random, and never the same few twice. Both can be switched off, and both "
            "are a click away in the navigation."
        ),
    },
    {
        "id": "tips",
        "visual": {"kind": "page", "url": "/", "fresh": True,
                   "actions": [("wait", 5), ("click", "text=Another tip"), ("wait", 5),
                               ("click", "text=Another tip"), ("wait", 5), ("click", "text=Another tip"), ("wait", 4)]},
        "text": (
            "The tips are worth a look even if you skip the guide. They're the features people "
            "don't find on their own: that a job's options save as a template, that a Gandalf "
            "archive can be checked before it's analysed, that Eru answers without a model, that "
            "Mordor shows which logs record a technique before you write a detection for it. "
            "Rivendell remembers the last ten it showed you, so you get new ones."
        ),
    },

    # ── Gandalf ──────────────────────────────────────────────────────────────────────────
    {
        "id": "gandalf",
        "chapter": "Gandalf: collecting evidence",
        "visual": {"kind": "page", "url": "/gandalf",
                   "actions": [("wait", 3), ("fill", "#caseNumber", "IR-2026-031"), ("wait", 2),
                               ("point", "[data-guide='gandalf.config']", 6),
                               ("point", "[data-guide='gandalf.hosts']", 5)]},
        "text": (
            "Gandalf's page builds a collection. Give it a case number, which names everything it "
            "collects, then choose the target's operating system, the collector, and how to reach it: "
            "on the machine itself, over SSH, or over PowerShell Remoting. Add the hosts, by name or "
            "address. Several hosts give one archive each."
        ),
    },
    {
        "id": "gandalf-options",
        "visual": {"kind": "page", "url": "/gandalf",
                   "actions": [("wait", 1), ("fill", "#caseNumber", "IR-2026-031"), ("wait", 1),
                               ("point", "[data-guide='gandalf.options']", 8),
                               ("scroll", 500, 3), ("point", "[data-guide='gandalf.command']", 8)]},
        "text": (
            "Then choose what to take: event logs, the registry, WMI, the master file table and its "
            "journal, scheduled tasks, browser data, user profiles, and live memory. Gandalf copies "
            "the most volatile things first and hashes afterwards, writing every hash to a log that "
            "travels with the archive. The page also gives you the exact command for your choices, "
            "for the machine the web interface can't reach, or simply for your case notes."
        ),
    },
    {
        "id": "gandalf-flow",
        "visual": {"kind": "page", "url": "/architecture/gandalf-acquisition.html",
                   "actions": [("wait", 4), ("scroll", 600, 8), ("wait", 4), ("scroll", 600, 8)]},
        "text": (
            "There are three collectors, because there are three kinds of machine you'll be asked "
            "about. The PowerShell collector covers Windows, locally or over Remoting. The Bash "
            "collector covers Linux and macOS with nothing but what's already installed, which "
            "matters on a server you've been told not to change. The Python collector does both, "
            "for when you want one tool across a mixed estate. They all write the same layout, so "
            "Elrond doesn't care which one took the evidence."
        ),
    },
    {
        "id": "gandalf-run",
        "visual": {"kind": "terminal", "title": "Administrator: Windows PowerShell", "lines": [
            "PS C:\\> .\\Invoke-Gandalf.ps1 -EncryptionObject None -Acquisition Local -OutputDirectory D:\\IR-2026-031 -Memory -ShowProgress",
            "  [+] Memory          LAB-WIN11.mem                    8.0 GB",
            "  [+] Event logs      winevt\\Logs                     412 files",
            "  [+] Registry        SYSTEM SOFTWARE SAM SECURITY + 3 NTUSER.DAT",
            "  [+] File system     $MFT  $UsnJrnl:$J  $LogFile",
            "  [+] WMI             OBJECTS.DATA  INDEX.BTR  MAPPING*.MAP",
            "  [+] Tasks, prefetch, amcache, SRUM, browsers, user profiles",
            "  [+] Hashing         SHA-256 of every file -> log.meta",
            "  Archive: D:\\IR-2026-031\\LAB-WIN11.zip",
        ]},
        "text": (
            "Here's the PowerShell collector on the lab's Windows 11 machine, run as an administrator "
            "with memory included. Memory goes first, because it changes while you watch. Then the "
            "event logs, the registry hives including every user's, the file system's own records, "
            "the WMI repository, and the usual execution artefacts. Last, every file is hashed, and "
            "the hashes go into a log inside the archive. Nothing is analysed on the host. Gandalf's "
            "job is to take a faithful copy and leave."
        ),
    },

    # ── Elrond ───────────────────────────────────────────────────────────────────────────
    {
        "id": "elrond",
        "chapter": "Elrond: analysing it",
        "visual": {"kind": "page", "url": "/elrond",
                   "actions": [("wait", 2), ("fill", "#caseNumber", "IR-2026-031"), ("wait", 2),
                               ("point", "[data-guide='elrond.source']", 7),
                               ("check", "input[name=analysisMode][value=gandalf]"), ("wait", 3),
                               ("point", "[data-guide='elrond.browse']", 6)]},
        "text": (
            "Elrond's page starts the analysis. Evidence can be local images, E01, raw, VMDK or "
            "memory; a Gandalf collection; a Mordor dataset; or logs from cloud storage. Several images "
            "go into one case, so the timeline and the ATT&CK mapping cover the whole intrusion rather "
            "than one machine at a time. With a Gandalf collection, Elrond checks every file against "
            "Gandalf's hash log before it trusts it, and records the result in the case."
        ),
    },
    {
        "id": "elrond-options",
        "visual": {"kind": "page", "url": "/elrond",
                   "actions": [("wait", 1), ("fill", "#caseNumber", "IR-2026-031"), ("wait", 1),
                               ("check", "input[name=analysisMode][value=local]"), ("wait", 2),
                               ("js", "document.querySelector(\"[data-guide='elrond.options']\").scrollIntoView({block: 'center'})"),
                               ("point", "[data-guide='elrond.options']", 14)]},
        "text": (
            "Then how thoroughly. Brisk is tuned for triage. Exhaustive turns everything on. Custom "
            "gives you every switch: carving unallocated space, shadow copies, last access times, "
            "masquerading checks for right-to-left override and double extensions, system binaries in "
            "places they shouldn't be, keyword lists and YARA rules, memory analysis and timelines, and "
            "where the results go: Splunk, Elastic, or an ATT&CK Navigator layer. Each option shows "
            "roughly what it costs in time, and every job saves its options as a template for the next "
            "case."
        ),
    },
    {
        "id": "elrond-memory",
        "visual": {"kind": "card", "title": "Memory, timelines and the cloud",
                   "subtitle": "Volatility 3 · Plaso · AWS, Azure and GCP logs"},
        "text": (
            "Three options deserve more than a tick box. Memory runs Volatility 3 against any memory "
            "image in the case, or the one Gandalf took: processes, network connections, injected "
            "code, command lines, and the services and drivers loaded at the time. A timeline runs "
            "Plaso across everything and gives you one super timeline for the case, which is slow, "
            "and usually worth it. And cloud evidence, CloudTrail from AWS, Azure's activity log, "
            "or Google Cloud's logging, is parsed and mapped to the cloud "
            "techniques in the same ATT&CK matrix as everything else."
        ),
    },
    {
        "id": "elrond-siem",
        "visual": {"kind": "page", "url": "/elrond",
                   "actions": [("wait", 1), ("fill", "#caseNumber", "IR-2026-031"), ("wait", 1),
                               ("check", "input[name=analysisMode][value=local]"), ("wait", 1),
                               ("js", "document.querySelector(\"[data-guide='elrond.options']\").scrollIntoView({block: 'end'})"),
                               ("wait", 2), ("scroll", 300, 4), ("wait", 10)]},
        "text": (
            "Where the results go is up to you. Every case lands on disk regardless. Tick Splunk and "
            "the case is indexed into the Splunk that ships with Rivendell, with an app of its own "
            "for the ATT&CK techniques. Tick Elastic and it goes to Elasticsearch and Kibana instead. "
            "Tick Navigator and Elrond writes a layer for the ATT&CK Navigator from the case's "
            "techniques, so the heat map you put in front of a client comes from the evidence, not "
            "from memory."
        ),
    },

    # ── Jobs ─────────────────────────────────────────────────────────────────────────────
    {
        "id": "jobs",
        "chapter": "Following a job",
        "visual": {"kind": "page", "url": "/jobs",
                   "actions": [("wait", 3), ("point", "[data-guide='jobs.table']", 6),
                               ("point", "[data-guide='jobs.filters']", 6)]},
        "text": (
            "Every analysis is a job. The jobs page shows each one's state and progress, and the bulk "
            "actions do what you'd hope: stop, restart, export, archive or delete a whole selection, "
            "which matters when a batch fails for the same reason."
        ),
    },
    {
        "id": "job",
        "visual": {"kind": "page", "url": "/jobs/{job}",
                   "actions": [("wait", 3), ("point", "[data-guide='job.actions']", 5),
                               ("point", "[data-guide='job.options']", 5), ("point", "[data-guide='job.log']", 6)]},
        "text": (
            "Open one and you can follow it live: its options, its source, and Elrond's own log, line "
            "by line. A long analysis can be paused, not just cancelled, so the machine is free for "
            "something urgent, and resumed later where it stopped."
        ),
    },
    {
        "id": "archive",
        "visual": {"kind": "page", "url": "/archive",
                   "actions": [("wait", 3), ("point", "[data-guide='archive.list']", 8)]},
        "text": (
            "Finished cases don't need to crowd the jobs page. Archive them and they move here, "
            "out of the way, and restore them when the case "
            "comes back, which they do."
        ),
    },

    # ── Outputs ──────────────────────────────────────────────────────────────────────────
    {
        "id": "outputs",
        "chapter": "What comes out",
        "visual": {"kind": "terminal", "lines": "{case_tree}"},
        "text": (
            "Here's a real case: the lab's Windows 11 machine, collected by Gandalf's PowerShell "
            "collector and processed by Elrond. The raw directory is exactly what was collected, never "
            "modified. Cooked holds every artefact Elrond parsed, as CSV or JSON, a hundred and "
            "forty files for this one machine. And at the top, one file lists every ATT&CK technique Elrond "
            "tagged across the whole case."
        ),
    },
    {
        "id": "techniques",
        "visual": {"kind": "terminal", "lines": "{techniques}"},
        "text": (
            "That lab machine was seeded with known tradecraft, so we know what should be found: a "
            "timestomped script, a payload hidden in an alternate data stream, and a WMI event "
            "subscription for persistence. Each turns up as its technique: T1070.006, "
            "T1564.004 and T1546.003. The WMI one comes straight out of the WMI repository, which Rivendell carves "
            "itself, because the usual parsers give up on Windows 11."
        ),
    },
    {
        "id": "integrity",
        "visual": {"kind": "terminal", "lines": "{integrity}"},
        "text": (
            "Here's the integrity check, from the lab's Ubuntu target and the Bash collector. Every "
            "file in the archive is hashed again and compared with "
            "the hash Gandalf wrote on the host. Matching files are marked verified. Anything that "
            "doesn't match, or is missing, or wasn't in the log at all, is listed by name. If you "
            "ever have to explain to someone else that the evidence you analysed is the evidence you "
            "collected, this is the file you show them."
        ),
    },
    {
        "id": "iocs",
        "visual": {"kind": "terminal", "lines": "{iocs}"},
        "text": (
            "With indicator extraction on, Elrond pulls addresses, domains, URLs and encoded strings "
            "out of everything it parsed, and records where each one came from. Most are noise, "
            "Windows talking to Microsoft. Two aren't: the lab's own command and control domains, "
            "one from PowerShell's event log and one from its history, at the top of the list. That's the "
            "list you pivot from: into your threat intelligence, into the SIEM, or across the other "
            "machines in the case to see who else talked to the same address."
        ),
    },

    # ── Eru ───────────────────────────────────────────────────────────────────────────────
    {
        "id": "eru",
        "chapter": "Asking Eru",
        "visual": {"kind": "page", "url": "/ai",
                   "actions": [("wait", 3), ("select", "[data-guide='eru.case'] select", "{case}"), ("wait", 3),
                               ("point", "[data-guide='eru.quick']", 5),
                               ("click", "text=Which ATT&CK techniques were tagged?"), ("wait", 1.5),
                               ("js", ANSWER), ("wait", 7),
                               ("click", "text=What persistence was flagged?"), ("wait", 1.5),
                               ("js", ANSWER), ("wait", 7)]},
        "text": (
            "Eru is Rivendell's analyst. Pick a case, and its answers come from that case's files, "
            "with the files they came from. With a local language model through Ollama, you can ask "
            "it anything. Without one, it still answers the questions that matter first, straight "
            "from the case: which hosts are in it, which techniques were tagged, what persistence was "
            "flagged, who logged in, what indicators were extracted, and which commands look "
            "suspicious. No GPU, no model, and nothing leaves the machine."
        ),
    },
    {
        "id": "eru-model",
        "visual": {"kind": "card", "title": "Eru, with a model", "subtitle": "Ollama on your own hardware · answers cite the case's files"},
        "text": (
            "Give Eru a model through Ollama and it does more: summaries of a case, a narrative of "
            "what happened, and suggestions for where to look next, each answer pointing back at the "
            "files it read. The model runs on your own hardware. Rivendell never sends a case to a "
            "hosted service, so it's usable on evidence you aren't allowed to let out of the "
            "building. A small model is enough for the questions above, and a larger one is better "
            "at the narrative."
        ),
    },

    # ── Mordor ───────────────────────────────────────────────────────────────────────────
    {
        "id": "mordor",
        "chapter": "Mordor: what attacks look like",
        "visual": {"kind": "page", "url": "/mordor",
                   "actions": [("wait", 3), ("point", "[data-guide='mordor.tiles']", 5),
                               ("js", "document.querySelector(\"[data-guide='mordor.recorded']\").scrollIntoView({block: 'start'})"),
                               ("wait", 2), ("scroll", 400, 6)]},
        "text": (
            "Mordor is the other direction: what attacks look like in the logs. It holds recorded "
            "attack telemetry, technique by technique, from public labs and your own, showing which "
            "logs actually record each technique. If you write detections, look the technique up here "
            "first, and start from what it really leaves behind. And because a dataset can be "
            "analysed like evidence, it's also a safe way to practise a case on known-bad data."
        ),
    },

    # ── Aragorn ──────────────────────────────────────────────────────────────────────────
    {
        "id": "aragorn",
        "chapter": "Aragorn: looking after it",
        "visual": {"kind": "page", "url": "/aragorn",
                   "actions": [("wait", 3), ("point", "[data-guide='aragorn.tabs']", 5),
                               ("goto", "/aragorn#settings"), ("wait", 3),
                               ("point", "[data-guide='aragorn.anduril']", 6)]},
        "text": (
            "Aragorn is for administrators. Its lab builds and drives test machines, Windows, Linux "
            "and macOS, each seeded with artefacts to find, so you can check Rivendell against known "
            "answers before trusting it with real evidence. Andúril manages Rivendell's own containers: "
            "their state, their logs, a restart, without opening a terminal."
        ),
    },
    {
        "id": "lab",
        "visual": {"kind": "terminal", "lines": [
            "$ rivendell lab quickstart",
            "  Host check ...................... ok",
            "  Linux targets (4) ............... up",
            "  Windows 11 VM ................... running, seeded",
            "$ rivendell lab gandalf-collect all",
            "  bash ........ 4 targets collected",
            "  python ...... 4 targets collected",
            "  powershell .. LAB-WIN11 collected",
            "$ rivendell lab mordor-record preset",
            "  Recording each atomic test's logs for the telemetry engine",
        ]},
        "text": (
            "The lab is also where Rivendell is tested. One command checks the host, builds four "
            "Linux targets and a Windows 11 virtual machine, and seeds them with tradecraft. Another "
            "runs every Gandalf collector against them. Because the lab knows what it planted, every "
            "release can be checked against what it should have found. And with Sysmon and Atomic "
            "Red Team in the Windows machine, the lab records new Mordor telemetry, technique by "
            "technique."
        ),
    },

    # ── Team server ──────────────────────────────────────────────────────────────────────
    {
        "id": "server",
        "chapter": "Rivendell for a team",
        "visual": {"kind": "terminal", "lines": [
            "$ rivendell server init rivendell.dfir.example.org",
            "  Wrote the server settings to .env",
            "  First admin: admin  (password shown once)",
            "$ rivendell start",
            "  Rivendell:     https://rivendell.dfir.example.org",
            "  Users: 'rivendell server users list'. Nothing else is published.",
            "$ rivendell server users add alice alice@example.org",
        ]},
        "text": (
            "Everything so far works on one analyst's machine. For a team, one command turns an "
            "install into a server. Caddy sits in front with TLS, using its own certificate authority, "
            "Let's Encrypt, or your organisation's certificate, and nothing else is published. Every "
            "request needs a signed-in user, there are no guests, and administrators create the "
            "accounts, or hand sign-in to your identity provider with single sign-on."
        ),
    },
    {
        "id": "sharing",
        "visual": {"kind": "card", "title": "Each job, its owner's", "subtitle": "Shared with colleagues by name · admins see everything · Eru follows the same rules"},
        "text": (
            "On a server, a job belongs to whoever started it. They can share it with colleagues by "
            "name, administrators see everything, and Eru only answers about cases you can see. The "
            "desktop app connects to the server instead of running anything locally, so analysts get "
            "the same window either way."
        ),
    },

    # ── Close ────────────────────────────────────────────────────────────────────────────
    {
        "id": "close",
        "chapter": "Where to find it",
        "visual": {"kind": "card", "title": "github.com/cmdaltr/rivendell", "subtitle": "Gandalf · Elrond · Eru · Mordor · Aragorn"},
        "text": (
            "Rivendell is open source, at github.com/cmdaltr/rivendell. The repository "
            "has the documentation, the command line reference and the server guide. Not all those "
            "who wander are lost, but the ones with a timeline get there faster."
        ),
    },
]
