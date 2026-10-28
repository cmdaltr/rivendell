"""
Renders the Rivendell walkthrough in scenes.py: narration with Piper, the screen with
Playwright against a running stack, joined with ffmpeg into an MP4 with chapters, an SRT
and a thumbnail, ready for YouTube.

    python3.12 -m venv ~/.local/share/piper/venv
    ~/.local/share/piper/venv/bin/pip install piper-tts
    ~/.local/share/piper/venv/bin/python -m piper.download_voices en_GB-alan-medium --data-dir ~/.local/share/piper
    pip install playwright && python3 -m playwright install chromium
    RIVENDELL_PASSWORD=... python3 scripts/docs/video/make_video.py --username admin \\
        --case-dir /path/to/case/output --out ~/Movies/Rivendell

Keep Piper's venv on a short path: its espeak-ng quietly falls back to the path it was
built at when the real one is too long, and says only that it can't find phontab.

--case-dir is a finished Elrond case: its directory and techniques appear on screen, and
its case and most recent job are the ones Eru and the Job page show. Scenes are kept in
--out/scenes/<section>/, and a scene whose narration and visual haven't changed isn't
rendered again; --only renders just the named sections or scenes (then joins everything).
Each section is joined into --out/scenes/<section>.mp4, fading in from black and out to
black, so adding or reordering sections re-encodes the sections but films nothing again.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "docs" / "guide"))
from capture import latest_job, sign_in  # noqa: E402
from scenes import SECTIONS, SPOKEN  # noqa: E402

WIDTH, HEIGHT, FPS = 1920, 1080, 30
PAGE_VIEW = (1440, 810)
GAP = 0.6  # seconds of quiet after each scene's narration
FADE = 0.8  # seconds from black at a section's start, and to black after its last frame
# What the lab's Windows machine was seeded with, and the IOCs it planted
SEEDED = ["T1070.006", "T1564.004", "T1546.003"]
PLANTED = "rivendell-lab.test"
MAP = REPO / "src" / "web" / "frontend" / "public" / "architecture" / "realm.jpg"

STYLE = """
:root { --navy: #0b1426; --deep: #070d1a; --teal: #2ec4b6; --gold: #f0dba5; --dim: #8aa0b8; }
* { box-sizing: border-box; margin: 0; }
body { width: 1920px; height: 1080px; overflow: hidden; background: var(--deep); color: var(--gold);
       font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace; }
"""

CARD = """<!doctype html><html><head><meta charset="utf-8"><style>{style}
.bg {{ position: fixed; inset: 0; background: url('{map}') center / cover; filter: brightness(.35) saturate(.8);
       animation: drift 30s linear forwards; }}
@keyframes drift {{ from {{ transform: scale(1.04) }} to {{ transform: scale(1.12) }} }}
.card {{ position: fixed; inset: 0; display: flex; flex-direction: column; justify-content: center; padding: 0 180px;
         background: linear-gradient(90deg, rgba(7,13,26,.92) 0%, rgba(7,13,26,.55) 60%, rgba(7,13,26,.2) 100%); }}
h1 {{ font-family: Cinzel, 'Times New Roman', serif; font-size: 112px; font-weight: 600; letter-spacing: .02em;
      opacity: 0; animation: rise 1.4s ease-out .3s forwards; }}
.rule {{ width: 0; height: 3px; background: var(--teal); margin: 36px 0; animation: rule 1.2s ease-out 1s forwards; }}
p {{ font-size: 34px; color: var(--dim); max-width: 1300px; line-height: 1.5; opacity: 0;
     animation: rise 1.2s ease-out 1.6s forwards; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(18px) }} to {{ opacity: 1; transform: none }} }}
@keyframes rule {{ to {{ width: 220px }} }}
</style></head><body><div class="bg"></div><div class="card"><h1>{title}</h1><div class="rule"></div><p>{subtitle}</p></div></body></html>"""

TERMINAL = """<!doctype html><html><head><meta charset="utf-8"><style>{style}
body {{ display: flex; align-items: center; justify-content: center;
        background: radial-gradient(ellipse at 30% 20%, #12233f 0%, var(--deep) 70%); }}
.win {{ width: 1560px; height: 860px; background: rgba(5,10,20,.94); border: 1px solid #1d3354; border-radius: 14px;
        box-shadow: 0 40px 120px rgba(0,0,0,.6); overflow: hidden; display: flex; flex-direction: column; }}
.bar {{ height: 46px; background: #0f1d33; display: flex; align-items: center; gap: 10px; padding: 0 18px; }}
.bar i {{ width: 14px; height: 14px; border-radius: 50%; background: #2a3e5c; }}
.bar span {{ margin-left: 18px; color: var(--dim); font-size: 18px; }}
pre {{ flex: 1; padding: 30px 38px; font: 25px/1.6 'JetBrains Mono', 'SF Mono', Menlo, monospace; color: #c9d6e6;
       white-space: pre-wrap; overflow: hidden; }}
.cmd {{ color: var(--teal); }} .cursor {{ display: inline-block; width: 13px; height: 27px; background: var(--teal);
       vertical-align: text-bottom; animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0 }} }}
</style></head><body><div class="win"><div class="bar"><i></i><i></i><i></i><span>{title}</span></div><pre id="out"></pre></div>
<script>
const LINES = {lines};
const out = document.getElementById('out');
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
let html = '';
function show(extra) {{ out.innerHTML = html + (extra || '') + '<span class="cursor"></span>'; out.scrollTop = out.scrollHeight; }}
// Commands are typed; what they print appears a line at a time, paced to fill the narration
window.play = async (seconds) => {{
  const typed = LINES.filter((l) => l.startsWith('$')).join('').length;
  const printed = LINES.length - LINES.filter((l) => l.startsWith('$')).length;
  const budget = Math.max(4, seconds * 0.8) * 1000;
  const perChar = Math.min(45, budget * 0.55 / Math.max(1, typed));
  const perLine = Math.min(700, budget * 0.45 / Math.max(1, printed));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  for (const line of LINES) {{
    if (line.startsWith('$')) {{
      let shown = '';
      for (const ch of line) {{ shown += ch; show(`<span class="cmd">${{esc(shown)}}</span>`); await sleep(perChar); }}
      html += `<span class="cmd">${{esc(line)}}</span>\\n`;
      await sleep(300);
    }} else {{
      html += esc(line) + '\\n';
      await sleep(perLine);
    }}
    show();
  }}
}};
show();
</script></body></html>"""

POINT = """([selector, seconds]) => {
  const el = document.querySelector(selector);
  if (!el) return false;
  el.scrollIntoView({block: 'center', behavior: 'smooth'});
  if (!document.getElementById('video-point-style')) {
    const s = document.createElement('style');
    s.id = 'video-point-style';
    s.textContent = `@keyframes video-pulse { 0%,100% { box-shadow: 0 0 0 3px rgba(46,196,182,.95), 0 0 0 9999px rgba(5,10,20,.45) }
      50% { box-shadow: 0 0 0 7px rgba(46,196,182,.55), 0 0 0 9999px rgba(5,10,20,.45) } }
      .video-point { position: fixed; z-index: 99999; border-radius: 8px; pointer-events: none;
      animation: video-pulse 1.6s ease-in-out infinite; transition: all .5s ease; }`;
    document.head.appendChild(s);
  }
  const box = document.createElement('div');
  box.className = 'video-point';
  document.body.appendChild(box);
  const place = () => { const r = el.getBoundingClientRect();
    Object.assign(box.style, {left: `${r.left - 8}px`, top: `${r.top - 8}px`, width: `${r.width + 16}px`, height: `${r.height + 16}px`}); };
  place();
  const timer = setInterval(place, 50);
  setTimeout(() => { clearInterval(timer); box.remove(); }, seconds * 1000);
  return true;
}"""

# The app scrolls inside its own container, so scroll whichever element actually scrolls
SCROLL = """([pixels, seconds]) => new Promise((done) => {
  const candidates = [...document.querySelectorAll('*')].filter((e) => {
    const o = getComputedStyle(e).overflowY;
    return (o === 'auto' || o === 'scroll') && e.scrollHeight > e.clientHeight + 10 && e.clientHeight > 300;
  });
  candidates.sort((a, b) => b.clientHeight * b.clientWidth - a.clientHeight * a.clientWidth);
  const el = candidates[0] || document.scrollingElement;
  const start = el.scrollTop, began = performance.now();
  const step = (now) => {
    const t = Math.min(1, (now - began) / (seconds * 1000));
    el.scrollTop = start + pixels * (t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
    t < 1 ? requestAnimationFrame(step) : done();
  };
  requestAnimationFrame(step);
})"""


def run(*args: str, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=True, capture_output=True, text=True, **kw)


def duration(path: Path) -> float:
    out = run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path))
    return float(out.stdout.strip())


def fingerprint(scene: dict, fills: dict) -> str:
    return hashlib.sha256(json.dumps([scene, fills], sort_keys=True, default=str).encode()).hexdigest()[:16]


def narrate(scene: dict, wav: Path, args: argparse.Namespace) -> float:
    """Speak the scene's text with Piper, then pad it with GAP seconds of quiet. A preview
    is silent, timed at Piper's usual pace."""
    if args.preview:
        seconds = len(scene["text"].split()) / 2.6 * args.pace + GAP
        run("ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{seconds:.2f}", str(wav))
        return seconds
    raw = wav.with_suffix(".raw.wav")
    command = [args.piper, "-m", "piper", "-m", args.voice, "-f", str(raw), "--length-scale", str(args.pace)]
    if args.voice_dir:
        command += ["--data-dir", args.voice_dir]
    spoken = scene["text"]
    for written, said in SPOKEN.items():
        spoken = spoken.replace(written, said)
    subprocess.run(command, input=spoken, check=True, capture_output=True, text=True)
    run("ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", f"apad=pad_dur={GAP}", "-ar", "48000", "-ac", "2", str(wav))
    raw.unlink()
    return duration(wav)


def case_tree(case_dir: Path) -> list:
    """The case directory as a terminal would show it: the top level, then cooked/ with a
    file count for each artefact directory."""
    lines = [f"$ ls {case_dir.name}"]
    for entry in sorted(case_dir.iterdir()):
        lines.append(f"  {entry.name}{'/' if entry.is_dir() else ''}")
    cooked = next(case_dir.rglob("cooked"), None)
    if cooked:
        lines.append(f"$ ls {cooked.relative_to(case_dir.parent)}")
        for entry in sorted(cooked.iterdir()):
            if entry.is_dir():
                count = sum(1 for p in entry.rglob("*") if p.is_file())
                lines.append(f"  {entry.name + '/':<24} {count} files")
            else:
                lines.append(f"  {entry.name}")
    return lines


def techniques(case_dir: Path) -> list:
    """How many techniques the case tagged, then the lab's seeded ones among them."""
    found = next(case_dir.rglob("mitre_techniques.txt"), None)
    if not found:
        return ["$ wc -l mitre_techniques.txt", "  (not in this case)"]
    tagged = [line.strip() for line in found.read_text(errors="replace").splitlines() if line.strip()]
    name = found.relative_to(case_dir.parent)
    seeded = [t for t in SEEDED if t in tagged]
    return ([f"$ wc -l < {name}", f"  {len(tagged)}", f"$ cat {name} | column -c 120"]
            + [f"  {'   '.join(f'{t:<10}' for t in tagged[i:i + 7])}" for i in range(0, len(tagged), 7)]
            + [f"$ grep -E '{'|'.join(SEEDED)}' {name}"] + [f"  {t}" for t in seeded])


def head(case_dir: Path, pattern: str, rows: int = 12) -> list:
    """The first rows of a case file, as `head` would print them."""
    found = next(case_dir.rglob(pattern), None)
    if not found:
        return [f"$ head {pattern}", "  (not in this case)"]
    lines = found.read_text(errors="replace").splitlines()
    return [f"$ head {found.relative_to(case_dir.parent)}"] + [f"  {line[:150]}" for line in lines[:rows]]


def integrity(found: Path) -> list:
    """Gandalf's hash check, hashes shortened to fit, then the tally."""
    rows = list(csv.DictReader(found.open(errors="replace")))
    lines = [f"$ column -s, -t {found.parent.name}/{found.name} | head"]
    lines += [f"  {r['status']:<9} {r['expected_sha256'][:12]}…  {r['file_path']}" for r in rows[:9]]
    lines.append(f"$ cut -d, -f4 {found.name} | sort | uniq -c")
    tally = {}
    for r in rows:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    lines += [f"  {n:>6} {status}" for status, n in sorted(tally.items())]
    return lines


def iocs(case_dir: Path) -> list:
    """Each distinct indicator once, with the artefact it came from."""
    found = next(case_dir.rglob("iocs.csv"), None)
    if not found:
        return ["$ head iocs.csv", "  (not in this case)"]
    rows = list(csv.DictReader(found.open(errors="replace")))
    lines = [f"$ cut -d, -f4-6 {found.relative_to(case_dir.parent)} | sort -u", f"  {len(rows)} indicators"]
    seen = set()
    for r in sorted(rows, key=lambda r: (PLANTED not in r["ioc"], r["indicator_type"], r["ioc"])):
        if r["ioc"] in seen or len(seen) >= 15:
            continue
        seen.add(r["ioc"])
        lines.append(f"  {r['indicator_type'][:12]:<13} {r['ioc'][:36]:<37} {Path(r['Filename']).name[:38]}")
    return lines


TERMINALS = {
    "case_tree": case_tree,
    "techniques": techniques,
    "iocs": iocs,
}


def fill(value, fills: dict):
    if isinstance(value, str):
        if value.startswith("{") and value.endswith("}") and value[1:-1] in (*TERMINALS, "integrity"):
            return fills[value[1:-1]]
        for key in ("repo", "case", "job"):
            value = value.replace(f"{{{key}}}", fills[key])
        return value
    if isinstance(value, (list, tuple)):
        return type(value)(fill(v, fills) for v in value)
    if isinstance(value, dict):
        return {k: fill(v, fills) for k, v in value.items()}
    return value


def film(scene: dict, seconds: float, webm: Path, args: argparse.Namespace, session: dict, browser) -> float:
    """Record the scene's visual for `seconds`; returns where in the recording the scene starts."""
    visual = scene["visual"]
    record = webm.parent / f".rec-{scene['id']}"
    shutil.rmtree(record, ignore_errors=True)
    # The web UI is filmed in a smaller window and scaled up, or it's unreadable on a phone
    view = PAGE_VIEW if visual["kind"] == "page" else (WIDTH, HEIGHT)
    context = browser.new_context(viewport={"width": view[0], "height": view[1]}, device_scale_factor=1,
                                  record_video_dir=str(record), record_video_size={"width": view[0], "height": view[1]})
    offered = "" if visual.get("fresh") else "sessionStorage.setItem('rivendell.offered', '1');"
    context.add_init_script(
        offered
        + f"localStorage.setItem('access_token', {json.dumps(session['token'])});"
        + f"localStorage.setItem('user', {json.dumps(json.dumps(session['user']))});")
    began = time.monotonic()
    page = context.new_page()

    if visual["kind"] == "card":
        html = CARD.format(style=STYLE, map=MAP.as_uri(), title=visual["title"], subtitle=visual["subtitle"])
        page_file = webm.parent / f".{scene['id']}.html"
        page_file.write_text(html)
        page.goto(page_file.as_uri())
    elif visual["kind"] == "terminal":
        html = TERMINAL.format(style=STYLE, title=visual.get("title", "rivendell — zsh"), lines=json.dumps(visual["lines"]))
        page_file = webm.parent / f".{scene['id']}.html"
        page_file.write_text(html)
        page.goto(page_file.as_uri())
    else:
        url = visual["url"]
        page.goto(f"{args.url}{url}" if url.startswith("/") else url, wait_until="networkidle")
    page.wait_for_timeout(600)
    start = time.monotonic() - began

    if visual["kind"] == "terminal":
        page.evaluate("(s) => { play(s); }", seconds)
    for action in visual.get("actions", []):
        act(page, action, args)
    left = seconds - (time.monotonic() - began - start)
    if left > 0:
        page.wait_for_timeout(left * 1000)
    context.close()
    recorded = next(record.glob("*.webm"))
    shutil.move(recorded, webm)
    shutil.rmtree(record, ignore_errors=True)
    for stray in webm.parent.glob(f".{scene['id']}.html"):
        stray.unlink()
    return start


def act(page, action: tuple, args: argparse.Namespace) -> None:
    kind, *rest = action
    try:
        if kind == "wait":
            page.wait_for_timeout(rest[0] * 1000)
        elif kind == "scroll":
            page.evaluate(SCROLL, list(rest))
        elif kind == "point":
            if page.evaluate(POINT, list(rest)):
                page.wait_for_timeout(rest[1] * 1000)
            else:
                print(f"    point: {rest[0]} isn't on the page")
        elif kind == "click":
            page.click(rest[0], timeout=10000)
        elif kind == "fill":
            page.fill(rest[0], rest[1], timeout=4000)
        elif kind == "check":
            page.check(rest[0], timeout=4000)
        elif kind == "select":
            page.select_option(rest[0], rest[1], timeout=4000)
        elif kind == "key":
            page.keyboard.press(rest[0])
        elif kind == "js":
            page.evaluate(rest[0])
        elif kind == "goto":
            url = rest[0]
            page.goto(f"{args.url}{url}" if url.startswith("/") else url, wait_until="networkidle")
        else:
            raise ValueError(f"unknown action {kind}")
    except Exception as exc:  # the scene goes on without it
        if exc.__class__.__name__ != "TimeoutError":
            raise
        print(f"    {kind} {rest[0]!r}: not found, skipped")


def encode(webm: Path, wav: Path, start: float, seconds: float, mp4: Path) -> None:
    run("ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", str(webm), "-i", str(wav),
        "-t", f"{seconds:.3f}", "-map", "0:v", "-map", "1:a",
        "-vf", f"scale={WIDTH}:{HEIGHT}:flags=lanczos,fps={FPS},format=yuv420p,fade=in:st=0:d=0.25",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(mp4))


def stamp(seconds: float, srt: bool = False) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if srt:
        return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"
    return f"{int(h)}:{int(m):02}:{int(s):02}" if h else f"{int(m)}:{int(s):02}"


def captions(text: str, start: float, spoken: float) -> list:
    """Sentences, timed by their share of the scene's characters."""
    sentences = [s for s in re.split(r"(?<=[.?!:])\s+", text) if s]
    total = sum(len(s) for s in sentences)
    out, at = [], start
    for sentence in sentences:
        length = spoken * len(sentence) / total
        out.append((at, at + length, sentence))
        at += length
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", default="http://localhost:5687", help="the web UI")
    parser.add_argument("--api", default="http://localhost:5688", help="the API")
    parser.add_argument("--username", required=True, help="an admin (password in RIVENDELL_PASSWORD)")
    parser.add_argument("--case-dir", required=True, type=Path, help="a finished case's output directory")
    parser.add_argument("--case", help="the case ID Eru shows (default: the case directory's name)")
    parser.add_argument("--integrity", type=Path, help="a gandalf_integrity.csv, when the case has none")
    parser.add_argument("--out", type=Path, default=Path.home() / "Movies" / "Rivendell")
    parser.add_argument("--voice", default="en_GB-alan-medium", help="a Piper voice name or .onnx path")
    parser.add_argument("--voice-dir", default=str(Path.home() / ".local" / "share" / "piper"))
    parser.add_argument("--pace", type=float, default=1.12, help="Piper's length scale: above 1 is slower")
    parser.add_argument("--piper", default=str(Path.home() / ".local" / "share" / "piper" / "venv" / "bin" / "python"),
                        help="a Python with piper-tts installed")
    parser.add_argument("--only", nargs="*", help="render just these scenes")
    parser.add_argument("--preview", action="store_true", help="silent, to check the filming without Piper")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    token, user = sign_in(args.api, args.username, os.environ.get("RIVENDELL_PASSWORD", ""))
    session = {"token": token, "user": user}
    fills = {"repo": str(REPO), "case": args.case or args.case_dir.name, "job": latest_job(args.api, token)}
    fills.update({name: make(args.case_dir) for name, make in TERMINALS.items()})
    checked = args.integrity or next(args.case_dir.rglob("gandalf_integrity.csv"), None)
    if not checked:
        sys.exit("No gandalf_integrity.csv in the case: pass --integrity with one from another case")
    fills["integrity"] = integrity(checked)
    scenes_dir = args.out / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)

    timeline = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for section in SECTIONS:
            section_dir = scenes_dir / section["id"]
            section_dir.mkdir(exist_ok=True)
            rendered = []
            for scene in section["scenes"]:
                scene = fill(scene, fills)
                mp4 = section_dir / f"{scene['id']}.mp4"
                stamp_file = mp4.with_suffix(".json")
                key = fingerprint(scene, {"pace": args.pace, "voice": args.voice, "preview": args.preview,
                                          "view": PAGE_VIEW if scene["visual"]["kind"] == "page" else None})
                wanted = not args.only or scene["id"] in args.only or section["id"] in args.only
                known = json.loads(stamp_file.read_text()) if stamp_file.exists() else {}
                if mp4.exists() and (known.get("key") == key or not wanted):
                    rendered.append((scene, mp4, known["spoken"], known["key"]))
                    continue
                if not wanted:
                    sys.exit(f"{scene['id']} hasn't been rendered yet: leave it out of --only")
                print(f"  {section['id']}/{scene['id']}")
                wav = mp4.with_suffix(".wav")
                seconds = narrate(scene, wav, args)
                webm = mp4.with_suffix(".webm")
                start = film(scene, seconds, webm, args, session, browser)
                encode(webm, wav, start, seconds, mp4)
                webm.unlink()
                wav.unlink()
                spoken = seconds - GAP
                stamp_file.write_text(json.dumps({"key": key, "spoken": spoken}))
                rendered.append((scene, mp4, spoken, key))
            timeline.append(join_section(section, rendered, scenes_dir))
        thumbnail(browser, args.out)
        browser.close()

    join(timeline, args.out)


def thumbnail(browser, out: Path) -> None:
    page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
    html = CARD.format(style=STYLE + "h1,.rule,p { animation: none !important; opacity: 1 !important } .rule { width: 220px }",
                       map=MAP.as_uri(), title="Rivendell",
                       subtitle="DFIR from collection to answers: Gandalf, Elrond and Eru")
    page_file = out / ".thumbnail.html"
    page_file.write_text(html)
    page.goto(page_file.as_uri())
    page.wait_for_timeout(500)
    page.screenshot(path=str(out / "thumbnail.png"))
    page.close()
    page_file.unlink()
    run("ffmpeg", "-y", "-v", "error", "-i", str(out / "thumbnail.png"), "-vf", "scale=1280:720", str(out / "thumbnail.jpg"))
    (out / "thumbnail.png").unlink()


def join_section(section: dict, rendered: list, scenes_dir: Path) -> tuple:
    """A section's scenes as one MP4 that fades in from black and, holding its last frame, out
    to black; re-encoded only when a scene in it changed. Returns (section, mp4, [(scene,
    start in the section, spoken seconds)])."""
    mp4 = scenes_dir / f"{section['id']}.mp4"
    stamp_file = mp4.with_suffix(".json")
    key = hashlib.sha256(json.dumps([[k for *_, k in rendered], FADE]).encode()).hexdigest()[:16]
    lengths = [duration(scene_mp4) for _, scene_mp4, _, _ in rendered]
    starts = [sum(lengths[:i]) for i in range(len(lengths))]
    parts = [(scene, start, spoken) for (scene, _, spoken, _), start in zip(rendered, starts)]
    known = json.loads(stamp_file.read_text()) if stamp_file.exists() else {}
    if mp4.exists() and known.get("key") == key:
        return section, mp4, parts
    print(f"  joining {section['id']}")
    listing = scenes_dir / f"{section['id']}.txt"
    listing.write_text("".join(f"file '{section['id']}/{scene_mp4.name}'\n" for _, scene_mp4, _, _ in rendered))
    total = sum(lengths)
    run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-vf", f"tpad=stop_mode=clone:stop_duration={FADE},fade=in:st=0:d={FADE},fade=out:st={total:.3f}:d={FADE}",
        "-af", "apad", "-t", f"{total + FADE:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(mp4))
    listing.unlink()
    stamp_file.write_text(json.dumps({"key": key}))
    return section, mp4, parts


def join(timeline: list, out: Path) -> None:
    """One MP4 with a chapter per section, plus the SRT and the description's chapter list."""
    listing = out / "scenes" / "concat.txt"
    listing.write_text("".join(f"file '{mp4.name}'\n" for _, mp4, _ in timeline))
    metadata = [";FFMETADATA1", "title=Rivendell: the full walkthrough"]
    chapters, cues, at = [], [], 0.0
    for section, mp4, parts in timeline:
        chapters.append((at, section["chapter"]))
        for scene, start, spoken in parts:
            cues += captions(scene["text"], at + start, spoken)
        at += duration(mp4)
    for i, (begin, title) in enumerate(chapters):
        end = chapters[i + 1][0] if i + 1 < len(chapters) else at
        metadata += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(begin * 1000)}", f"END={int(end * 1000)}", f"title={title}"]
    meta_file = out / "scenes" / "chapters.ffmeta"
    meta_file.write_text("\n".join(metadata) + "\n")
    video = out / "rivendell-walkthrough.mp4"
    run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-i", str(meta_file),
        "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart", str(video))
    (out / "rivendell-walkthrough.srt").write_text("".join(
        f"{n}\n{stamp(a, True)} --> {stamp(b, True)}\n{text}\n\n" for n, (a, b, text) in enumerate(cues, 1)))
    (out / "chapters.txt").write_text("".join(f"{stamp(begin)} {title}\n" for begin, title in chapters))
    print(f"Wrote {video} ({stamp(at)}), its captions, chapters.txt and thumbnail.jpg")


if __name__ == "__main__":
    main()
