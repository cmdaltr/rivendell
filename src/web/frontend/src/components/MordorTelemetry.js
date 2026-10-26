// Mordor → Recorded telemetry: where attack telemetry comes from (public datasets and the lab's
// own recordings), the lab that records it, and which logs record each technique. Ported from
// Archer's Emulate page (templates/emulate.html, static/js/lab.js, emulate.js); the engine is
// src/mordor/telemetry and the lab src/mordor/lab, driven on the host by the lab agent.
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getTelemetryStatus,
  getTelemetryTechniques,
  getTelemetryTechnique,
  searchTelemetry,
  updateTelemetry,
  getMordorLab,
  getMordorLabLogs,
  getMordorLabSteps,
  postMordorLab,
  getLabStatus,
  getLabRun,
  runLabCommand,
} from '../api';

const IMG = `${process.env.PUBLIC_URL}/images/mordor`;
const errorText = (err) => {
  const d = err.response?.data?.detail;
  if (!d) return err.message;
  return typeof d === 'string' ? d : JSON.stringify(d);
};

// The public datasets, in the order the cards show them; counts and notes come from the API
const SOURCES = [
  { key: 'splunk', img: 'splunk.png', badge: 'Maintained' },
  { key: 'otrf', img: 'otrf.png', badge: 'Updated Mar 2024' },
  { key: 'evtx', img: 'evtx.png', badge: 'Maintained' },
  { key: 'macos', img: 'attack.png', badge: 'Local only' },
];
const OS_ICON = { windows: 'windows.svg', macos: 'macos.png', linux: 'tux.svg' };
const ENGINE_ICON = { docker: 'docker.png', tart: 'tart.png', utm: 'utm.svg' };
const ENGINE_NAME = { docker: 'Docker', tart: 'Tart', utm: 'UTM' };
const PAGE = 50;

const OsIcon = ({ os, name = '' }) => {
  let f = OS_ICON[os];
  if (os === 'linux' && /ubuntu/i.test(name)) f = 'ubuntu.png';
  return f ? <img className="mt-icon" src={`${IMG}/${f}`} alt={os} /> : null;
};
const EngineIcon = ({ engine }) =>
  ENGINE_ICON[engine] ? <img className="mt-icon" src={`${IMG}/${ENGINE_ICON[engine]}`} alt={engine} /> : null;

// ---------------------------------------------------------------- diagram

function Pipeline() {
  const node = (x, y, w, h, cls, icon, title, sub, iconCls) => (
    <g>
      <rect x={x} y={y} width={w} height={h} rx="8" className={cls} />
      <use href={`#mt-ic-${icon}`} x={x + 10} y={y + h / 2 - 9} width="18" height="18" className={`mt-dg-ic ${iconCls}`} />
      <text x={x + 34} y={sub ? y + h / 2 - 3 : y + h / 2 + 5} className="mt-dg-t">{title}</text>
      {sub && <text x={x + 34} y={y + h / 2 + 13} className="mt-dg-s">{sub}</text>}
    </g>
  );
  const arrow = (d) => <path d={d} className="mt-dg-link" markerEnd="url(#mt-dg-arrow)" />;
  return (
    <div className="mt-dg">
      <svg viewBox="0 0 960 250" role="img" aria-label="Your lab's recordings and the public datasets are mapped to ATT&CK, checked against detections' indicators, and shown as recorded telemetry">
        <defs>
          <marker id="mt-dg-arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" className="mt-dg-head" />
          </marker>
          <symbol id="mt-ic-flask" viewBox="0 0 16 16"><path d="M6.5 2.5h3M7 2.5V6.5L4 12.2a1 1 0 0 0 .9 1.5h6.2a1 1 0 0 0 .9-1.5L9 6.5V2.5" /></symbol>
          <symbol id="mt-ic-db" viewBox="0 0 16 16"><ellipse cx="8" cy="4" rx="4.8" ry="1.9" /><path d="M3.2 4v8a4.8 1.9 0 0 0 9.6 0V4" /></symbol>
          <symbol id="mt-ic-doc" viewBox="0 0 16 16"><path d="M4 2.5h5l3 3v8H4z" /><path d="M6 8h4M6 10.5h4" /></symbol>
          <symbol id="mt-ic-target" viewBox="0 0 16 16"><circle cx="8" cy="8" r="5.2" /><circle cx="8" cy="8" r="2" /></symbol>
          <symbol id="mt-ic-search" viewBox="0 0 16 16"><circle cx="7" cy="7" r="4" /><path d="M10 10l3.5 3.5" /></symbol>
          <symbol id="mt-ic-chart" viewBox="0 0 16 16"><path d="M3 13h10" /><path d="M5 12V8.5M8 12V5.5M11 12V7" /></symbol>
          <symbol id="mt-ic-create" viewBox="0 0 16 16"><rect x="2.5" y="3.5" width="11" height="8" rx="1.2" /><path d="M5.5 13.5h5M8 6v3.5M6.25 7.75h3.5" /></symbol>
          <symbol id="mt-ic-camera" viewBox="0 0 16 16"><rect x="2.3" y="4.8" width="11.4" height="7.4" rx="1.6" /><circle cx="8" cy="8.5" r="2.1" /><path d="M6.1 4.8l1-1.5h1.8l1 1.5" /></symbol>
          <symbol id="mt-ic-gear" viewBox="0 0 16 16"><circle cx="8" cy="8" r="2" /><path d="M8 2.6v2.1M8 11.3v2.1M2.6 8h2.1M11.3 8h2.1M4.2 4.2l1.5 1.5M10.3 10.3l1.5 1.5M11.8 4.2l-1.5 1.5M5.7 10.3l-1.5 1.5" /></symbol>
          <symbol id="mt-ic-play" viewBox="0 0 16 16"><circle cx="8" cy="8" r="5.3" /><path d="M6.6 5.5l4 2.5-4 2.5z" /></symbol>
        </defs>

        {/* The lab lane is the "Your lab" source, expanded */}
        <polygon points="16,120 196,20 760,92 176,168" className="mt-dg-expand" />
        <path d="M16,120 L196,20" className="mt-dg-expand-edge" />
        <path d="M176,168 L760,92" className="mt-dg-expand-edge" />
        <rect x="196" y="20" width="564" height="72" rx="12" className="mt-dg-lane-box" />
        <text x="208" y="38" className="mt-dg-lane">LAB — BUILD &amp; RECORD A MACHINE</text>
        {node(212, 48, 120, 40, 'mt-dg-loop', 'create', 'Create', null, 'is-lab')}
        {node(350, 48, 120, 40, 'mt-dg-loop', 'camera', 'Snapshot', null, 'is-lab')}
        {node(488, 48, 120, 40, 'mt-dg-loop', 'gear', 'Set up', 'logs & atomics', 'is-lab')}
        {node(626, 48, 120, 40, 'mt-dg-loop', 'play', 'Record', 'run atomics', 'is-lab')}
        {arrow('M332,68 L348,68')}{arrow('M470,68 L486,68')}{arrow('M608,68 L624,68')}

        {node(16, 120, 160, 48, 'mt-dg-origin', 'flask', 'Your lab', 'runs you record', 'is-lab')}
        {node(16, 182, 160, 48, 'mt-dg-pub', 'db', 'Public datasets', 'shipped with Rivendell', 'is-pub')}
        {arrow('M176,144 C194,144 192,170 206,172')}
        {arrow('M176,206 C194,206 192,180 206,178')}

        {node(208, 147, 168, 56, 'mt-dg-node', 'doc', 'Recordings', 'one tool run, logging on', 'is-blue')}
        {node(400, 147, 168, 56, 'mt-dg-node', 'target', 'Mapped to ATT&CK', 'technique · source', 'is-blue')}
        {node(592, 147, 168, 56, 'mt-dg-node', 'search', 'Indicator check', 'detections vs events', 'is-blue')}
        {node(784, 147, 160, 56, 'mt-dg-end', 'chart', 'Recorded telemetry', 'the views below', 'is-green')}
        {arrow('M376,175 L398,175')}{arrow('M568,175 L590,175')}{arrow('M760,175 L782,175')}
      </svg>
    </div>
  );
}

// ---------------------------------------------------------------- sources

function Sources({ status, isAdmin, onUpdate }) {
  if (!status) return <p className="lab-note">Loading…</p>;
  const info = status.sources || {};
  const count = status.per_source || {};
  const runs = status.lab_runs || [];
  const building = status.build?.state === 'running';
  return (
    <>
      <div className="mt-sources-head">
        <h3>Public datasets</h3>
        {isAdmin && (
          <button onClick={onUpdate} disabled={building} title="Fetch what the sources changed since the last build">
            {building ? 'Updating…' : 'Update'}
          </button>
        )}
      </div>
      <ul className="mt-sources">
        <li className="mt-source is-lab">
          <span className="mt-source-logo"><svg viewBox="0 0 16 16"><use href="#mt-ic-flask" /></svg></span>
          <div>
            <div className="mt-source-top"><strong>Your lab</strong><span className="mt-badge">{runs.length ? `${runs.length} run${runs.length === 1 ? '' : 's'}` : 'No runs yet'}</span></div>
            <div className="mt-source-meta">{count.lab || 0} recordings · yours, never committed</div>
            <div className="mt-source-note">Atomic Red Team on the lab's own machines, each test's logs kept apart (Your lab, below)</div>
          </div>
        </li>
        {SOURCES.filter(s => info[s.key]).map(s => (
          <li key={s.key} className="mt-source">
            <img className="mt-source-logo" src={`${IMG}/${s.img}`} alt="" />
            <div>
              <div className="mt-source-top">
                <a href={info[s.key].url} target="_blank" rel="noopener noreferrer">{info[s.key].name}</a>
                <span className="mt-badge">{s.badge}</span>
              </div>
              <div className="mt-source-meta">{(count[s.key] || 0).toLocaleString()} recordings · {info[s.key].licence}</div>
              <div className="mt-source-note">{info[s.key].note}</div>
            </div>
          </li>
        ))}
        {status.guide && (
          <li className="mt-source">
            <img className="mt-source-logo" src={`${IMG}/microsoft.png`} alt="" />
            <div>
              <div className="mt-source-top">
                <a href={status.guide.url} target="_blank" rel="noopener noreferrer">{status.guide.name}</a>
                <span className="mt-badge">Alerts, not logs</span>
              </div>
              <div className="mt-source-meta">{status.guide.techniques} techniques · {status.guide.licence}</div>
              <div className="mt-source-note">{status.guide.note}</div>
            </div>
          </li>
        )}
      </ul>
      <p className="lab-note">
        Each recording is one tool run in a lab with logging on (Sysmon, Windows auditing, PowerShell, cloud audit logs),
        mapped to ATT&amp;CK by the people who recorded it. It shows that a technique can be recorded and by which log,
        for that tool in that lab; not every way the technique can be done. The recordings ship with Rivendell;
        {' '}<strong>Update</strong> (or <code>python3 -m src.mordor.telemetry --build</code>) fetches what the sources have changed since.
      </p>
      {status.build && status.build.state !== 'idle' && (
        <pre className="lab-output">{(status.build.log || []).join('\n') || status.build.state}</pre>
      )}
    </>
  );
}

// ---------------------------------------------------------------- lab

function Modal({ title, onClose, children }) {
  useEffect(() => {
    const esc = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', esc);
    return () => document.removeEventListener('keydown', esc);
  }, [onClose]);
  return (
    <div className="mt-modal" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="mt-modal-box" role="dialog" aria-modal="true">
        <div className="mt-modal-head"><strong>{title}</strong><button className="mt-close" onClick={onClose} aria-label="Close">×</button></div>
        <div className="mt-modal-body">{children}</div>
      </div>
    </div>
  );
}

function NameDialog({ title, label, initial, hint, action, danger, onCancel, onGo }) {
  const [value, setValue] = useState(initial);
  const go = () => value.trim() && onGo(value.trim());
  return (
    <Modal title={title} onClose={onCancel}>
      <label className="mt-field">{label}
        <input type="text" value={value} autoFocus onChange={(e) => setValue(e.target.value)}
               onKeyDown={(e) => { if (e.key === 'Enter') go(); }} />
      </label>
      {hint && <p className="lab-note">{hint}</p>}
      <div className="mt-modal-actions">
        <button className="mt-pill" onClick={onCancel}>Cancel</button>
        <button className={danger ? 'secondary' : ''} onClick={go}>{action}</button>
      </div>
    </Modal>
  );
}

function RecordDialog({ machine, labWindows, onCancel, onRun }) {
  const [techs, setTechs] = useState('');
  const [revert, setRevert] = useState('clean');
  const [snapped, setSnapped] = useState(false);
  const [preview, setPreview] = useState(null);
  const body = { engine: machine.engine, name: machine.name, os: machine.os };
  const doPreview = async () => {
    try { setPreview(await postMordorLab('record', { ...body, techniques: techs, execute: false })); }
    catch (err) { setPreview({ error: errorText(err) }); }
  };
  return (
    <Modal title={`Record on ${machine.name}`} onClose={onCancel}>
      <label className="mt-field">ATT&amp;CK techniques
        <input type="text" value={techs} autoFocus placeholder="T1059.001, T1053.005" onChange={(e) => setTechs(e.target.value)} />
      </label>
      <p className="lab-note">
        Atomic Red Team runs every test of these in the machine and the logs land in <strong>Your lab</strong>.
        The tests change the machine: snapshot it first and revert after.
        {labWindows && ' This is the lab\'s Windows VM, so it records over SSH with ./lab.sh mordor-record.'}
      </p>
      <label className="mt-field">Revert to snapshot afterwards (optional)
        <input type="text" value={revert} onChange={(e) => setRevert(e.target.value)} />
      </label>
      {preview && (
        <div className="mt-preview">
          {preview.error && <div className="mt-warn">{preview.error}</div>}
          {(preview.warnings || []).length > 0 && <div className="mt-warn">Not ready: {preview.warnings.join('; ')}</div>}
          {preview.plan && <ol>{preview.plan.map((s, i) => <li key={i}>{s}</li>)}</ol>}
        </div>
      )}
      <label className="mt-confirm"><input type="checkbox" checked={snapped} onChange={(e) => setSnapped(e.target.checked)} /> I've snapshotted this machine and it's disposable</label>
      <div className="mt-modal-actions">
        <button className="mt-pill" onClick={doPreview} disabled={!techs.trim()}>Preview</button>
        <button className="secondary" disabled={!(snapped && techs.trim())}
                onClick={() => onRun({ ...body, techniques: techs, revert_to: labWindows ? '' : revert, execute: true })}>Run atomics</button>
      </div>
    </Modal>
  );
}

function IsoDialog({ hasLabWindows, onClose, onBuild }) {
  const [path, setPath] = useState('');
  const [result, setResult] = useState(null);
  const verify = async () => {
    if (!path.trim()) { setResult({ bad: true, text: 'Give the path first.' }); return; }
    setResult({ text: 'Checking…' });
    try {
      const r = await postMordorLab('verify-iso', { path });
      setResult({ bad: !r.ok_arm64, text: r.detail || r.error || '' });
    } catch (err) { setResult({ bad: true, text: errorText(err) }); }
  };
  return (
    <Modal title="Build a Windows VM from an ISO" onClose={onClose}>
      <ol className="mt-steps">
        <li>Download the official <strong>Windows 11 Arm64</strong> ISO from{' '}
          <a href="https://www.microsoft.com/software-download/windows11arm64" target="_blank" rel="noopener noreferrer">Microsoft</a> (~5 GB)
          into the lab's <code>isos</code> folder.</li>
        <li>Check it's the right installer:
          <label className="mt-field">Path to the .iso
            <input type="text" value={path} placeholder="/Volumes/…/lab/isos/Win11_arm64.iso" onChange={(e) => setPath(e.target.value)} />
          </label>
          <button className="mt-pill" onClick={verify}>Verify ISO</button>{' '}
          {result && <span className={result.bad ? 'mt-bad' : 'mt-good'}>{result.text}</span>}
        </li>
        <li>
          {hasLabWindows
            ? <>The lab's Windows VM already exists. For another, use <strong>Clone</strong> on it: no reinstall.</>
            : <>Let the lab build it unattended (<code>./lab.sh windows-vm create</code>: installs Windows, OpenSSH and the Gandalf target, about an hour), or build it yourself in UTM and use <strong>Set OS</strong> on it.</>}
        </li>
      </ol>
      <div className="mt-modal-actions">
        {!hasLabWindows && <button className="mt-pill" onClick={onBuild}>Build the lab's Windows VM</button>}
        <button onClick={onClose}>Done</button>
      </div>
    </Modal>
  );
}

function LabSection({ onRecorded }) {
  const [available, setAvailable] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [run, setRun] = useState(null);
  const [dialog, setDialog] = useState(null);
  const offsetRef = useRef(0);
  const pollRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const s = await getLabStatus();
      setAvailable(s);
      if (!s.available) return;
      const d = await getMordorLab();
      setData(d);
      setError(null);
      if (d.busy && d.busy.status === 'running') setRun((r) => (r && r.id === d.busy.id ? r : { ...d.busy, output: '' }));
    } catch (err) { setError(errorText(err)); }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Follow the running job's log until it finishes, then reload the machines
  useEffect(() => {
    if (!run || run.status !== 'running') return undefined;
    offsetRef.current = run.offset || 0;
    pollRef.current = setInterval(async () => {
      try {
        const r = await getLabRun(run.id, offsetRef.current);
        offsetRef.current = r.offset;
        setRun((prev) => ({ ...r, output: (prev?.output || '') + (r.output || '') }));
        if (r.status !== 'running') {
          clearInterval(pollRef.current);
          refresh();
          if (/record/.test(r.label)) onRecorded();
        }
      } catch (err) { clearInterval(pollRef.current); setError(errorText(err)); }
    }, 1500);
    return () => clearInterval(pollRef.current);
  }, [run?.id, run?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  const post = async (verb, body) => {
    setDialog(null);
    try {
      const r = await postMordorLab(verb, body);
      if (r && r.id && r.status === 'running') setRun({ ...r, output: '' });
      else refresh();
      return r;
    } catch (err) { setError(errorText(err)); return null; }
  };

  if (available && !available.available) {
    return (
      <div className="mt-lab-off">
        <p>The lab's machines run on the host, outside Rivendell's containers, so this page drives them through the lab agent. Start it on the machine running Rivendell:</p>
        <div className="lab-command"><code>cd lab && {available.start_command || './lab.sh agent start'}</code></div>
        <button className="mt-pill" onClick={refresh}>Check again</button>
      </div>
    );
  }
  if (!data) return error ? <p className="lab-note mt-bad">{error}</p> : <p className="lab-note">Loading the lab…</p>;

  const taken = new Set(data.taken || []);
  const free = (stem) => { for (let n = 1; ; n += 1) { const c = `${stem}-${n}`; if (!taken.has(c)) return c; } };
  const byOs = new Map();
  (data.templates || []).forEach((t) => { if (!byOs.has(t.os)) byOs.set(t.os, []); byOs.get(t.os).push(t); });
  const utm = (data.host.engines || []).find((e) => e.key === 'utm');
  const utmVms = (data.machines || []).filter((m) => m.engine === 'utm');
  const hasLabWindows = utmVms.some((m) => m.name === data.lab_windows_vm);
  const busy = run && run.status === 'running';

  const act = (m, action) => {
    const base = { engine: m.engine, name: m.name };
    if (action === 'start' || action === 'stop') post('action', { ...base, action });
    else if (action === 'delete') {
      if (window.confirm(`Delete ${m.name}? This removes the machine and its snapshots for good.`)) post('action', { ...base, action });
    } else if (action === 'logs') {
      getMordorLabLogs(m.engine, m.name).then((r) => setDialog({ kind: 'logs', m, text: r.logs }))
        .catch((err) => setDialog({ kind: 'logs', m, text: errorText(err) }));
    } else if (action === 'provision') {
      if (m.name === data.lab_windows_vm) setDialog({ kind: 'provision', m, steps: [{ step: 'sensor', label: 'Sysmon, audit logging and Atomic Red Team (./lab.sh mordor-sensor)' }] });
      else getMordorLabSteps(m.os).then((r) => setDialog({ kind: 'provision', m, steps: r.steps || [] }));
    } else setDialog({ kind: action, m });
  };

  return (
    <>
      <div className="mt-host">
        <div>This host: <strong>{data.host.label}</strong> <span className="mt-dim">{data.host.os} · {data.host.arch}</span></div>
        <details>
          <summary>{data.host.label} supports the following platforms</summary>
          <ul className="mt-engines">
            {data.host.engines.map((e) => {
              const state = !e.supported ? 'not on this host' : e.running ? `ready · ${e.version}` : e.installed ? 'installed, not running' : 'not installed';
              const cls = !e.supported ? 'is-na' : e.running ? 'is-ready' : 'is-warn';
              return (
                <li key={e.key} className={`mt-engine ${cls}`}>
                  <div><EngineIcon engine={e.key} /><strong>{e.name}</strong> <span className="mt-dim">{state}</span></div>
                  <div className="mt-dim">{e.blurb || e.runs}</div>
                  {e.note && e.installed && !e.running && <div className="lab-note">{e.note}</div>}
                  {e.install && <code>{e.install}</code>}
                </li>
              );
            })}
          </ul>
        </details>
      </div>

      <div className="mt-cols">
        <div>
          <h3 className="mt-colhead">Create a machine</h3>
          {[...byOs].map(([os, group]) => (
            <div key={os} className="mt-template">
              <div className="mt-template-name"><OsIcon os={os} name={group[0].os_name} /><strong>{group[0].os_name}</strong></div>
              <p>{group[0].os_about}</p>
              <p className="mt-dim"><span>Records:</span> {group[0].os_records}</p>
              <div className="mt-row">
                {group.map((t) => (
                  <button key={t.id} className="mt-pill" disabled={!t.ready || busy} title={t.ready ? `Create with ${ENGINE_NAME[t.engine]}` : t.reason}
                          onClick={() => setDialog({ kind: 'create', t, name: free(`rivendell-${t.id.replace(/-(vm|container)$/, '')}`) })}>
                    <EngineIcon engine={t.engine} /> Create
                  </button>
                ))}
              </div>
            </div>
          ))}
          {utm && utm.supported && (
            <div className="mt-template">
              <div className="mt-template-name"><EngineIcon engine="utm" /><strong>Windows &amp; others, via UTM</strong></div>
              {utm.running ? (
                <>
                  <p>Two ways to a Windows machine: clone one already built, or build one from Microsoft's ISO.</p>
                  <div className="mt-row">
                    <button className="mt-pill" disabled={busy} onClick={() => setDialog({ kind: 'clone-pick' })}><EngineIcon engine="utm" /> Clone existing</button>
                    <button className="mt-pill" disabled={busy} onClick={() => setDialog({ kind: 'iso' })}><OsIcon os="windows" /> From ISO</button>
                  </div>
                </>
              ) : (
                <p className="mt-dim">{utm.installed ? utm.note : 'Install UTM to run Windows 11 on ARM.'} {utm.install && <code>{utm.install}</code>}</p>
              )}
            </div>
          )}
        </div>

        <div>
          <h3 className="mt-colhead">Your machines</h3>
          {(data.machines || []).length === 0 && <p className="lab-note">No machines yet. Create one on the left.</p>}
          <ul className="mt-machines">
            {(data.machines || []).map((m) => (
              <li key={`${m.engine}/${m.name}`} className="mt-machine">
                <div className="mt-machine-head">
                  <span className={`mt-dot is-${m.state}`} title={m.state} />
                  <OsIcon os={m.os} name={m.name} /><strong>{m.name}</strong>
                  {m.lab && <span className="mt-badge" title="Built and deleted by ./lab.sh">lab</span>}
                </div>
                <div className="mt-dim"><EngineIcon engine={m.engine} /> {[m.engine, m.state, m.records && `records ${m.records}`].filter(Boolean).join(' · ')}</div>
                {(m.provisioned || []).length > 0 && <div className="mt-dim">set up: {m.provisioned.join(', ')}</div>}
                <div className="mt-row">
                  <button className="mt-pill" disabled={busy} onClick={() => act(m, m.state === 'running' ? 'stop' : 'start')}>{m.state === 'running' ? 'Stop' : 'Start'}</button>
                  <button className="mt-pill" disabled={busy} onClick={() => act(m, 'snapshot')}>Snapshot</button>
                  <button className="mt-pill" disabled={busy} onClick={() => act(m, 'revert')}>Revert</button>
                  {m.engine === 'utm' && <button className="mt-pill" disabled={busy} onClick={() => act(m, 'clone')}>Clone</button>}
                  {m.engine === 'utm' && !m.os && <button className="mt-pill" onClick={() => act(m, 'adopt')}>Set OS</button>}
                  {m.os && <button className="mt-pill" disabled={busy} onClick={() => act(m, 'provision')}>Set up</button>}
                  {m.os && <button className="mt-pill" disabled={busy} onClick={() => act(m, 'record')}>Record</button>}
                  <button className="mt-pill" onClick={() => act(m, 'logs')}>Logs</button>
                  {m.deletable && <button className="mt-pill mt-danger" disabled={busy} onClick={() => act(m, 'delete')}>Delete</button>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {error && <p className="lab-note mt-bad">{error}</p>}
      {run && (
        <div className="mt-job">
          <div className="lab-run-head">
            <h3>{run.label} <span className={`lab-status lab-status-${run.status}`}>{run.status}</span></h3>
            {run.status !== 'running' && <button className="mt-pill" onClick={() => setRun(null)}>Close</button>}
          </div>
          <pre className="lab-output">{run.output || 'Starting…'}</pre>
        </div>
      )}

      {dialog?.kind === 'create' && (
        <NameDialog title="Create a machine" label="Name" initial={dialog.name} action="Create"
                    hint="Letters, digits, dot, dash or underscore. Pulling the image can take a while."
                    onCancel={() => setDialog(null)} onGo={(name) => post('create', { template: dialog.t.id, name })} />
      )}
      {dialog?.kind === 'snapshot' && (
        <NameDialog title={`Snapshot ${dialog.m.name}`} label="Snapshot name" initial="clean" action="Snapshot"
                    hint={dialog.m.engine === 'tart' ? 'A Tart snapshot is a clone of the VM: instant on APFS until it diverges.' : ''}
                    onCancel={() => setDialog(null)} onGo={(snapshot) => post('action', { engine: dialog.m.engine, name: dialog.m.name, action: 'snapshot', snapshot })} />
      )}
      {dialog?.kind === 'revert' && (
        <NameDialog title={`Revert ${dialog.m.name}`} label="Snapshot to revert to" initial="clean" action="Revert" danger
                    hint="Everything since that snapshot is discarded."
                    onCancel={() => setDialog(null)} onGo={(snapshot) => post('action', { engine: dialog.m.engine, name: dialog.m.name, action: 'revert', snapshot })} />
      )}
      {dialog?.kind === 'clone' && (
        <NameDialog title={`Clone ${dialog.m.name}`} label="New machine name" initial={free(dialog.m.name.replace(/-\d+$/, ''))} action="Clone"
                    hint={`Copies the VM and its disk: a few minutes. The clone inherits ${dialog.m.name}'s OS and set-up; snapshot it before recording.`}
                    onCancel={() => setDialog(null)} onGo={(newName) => post('clone', { engine: 'utm', name: dialog.m.name, new_name: newName })} />
      )}
      {dialog?.kind === 'clone-pick' && (
        utmVms.length === 0 ? (
          <Modal title="Clone a Windows VM" onClose={() => setDialog(null)}>
            <p className="lab-note">No UTM VM to clone yet. Build one from an ISO first.</p>
            <div className="mt-modal-actions"><button onClick={() => setDialog(null)}>OK</button></div>
          </Modal>
        ) : (
          <Modal title="Clone a Windows VM" onClose={() => setDialog(null)}>
            <label className="mt-field">Clone from
              <select value={dialog.src || utmVms[0].name} onChange={(e) => setDialog({ ...dialog, src: e.target.value })}>
                {utmVms.map((m) => <option key={m.name} value={m.name}>{m.name}{m.os ? ` (${m.os})` : ''}</option>)}
              </select>
            </label>
            <p className="lab-note">Copies the VM. The clone inherits the source's OS and set-up; snapshot it before recording.</p>
            <div className="mt-modal-actions">
              <button className="mt-pill" onClick={() => setDialog(null)}>Cancel</button>
              <button onClick={() => { const src = dialog.src || utmVms[0].name; setDialog({ kind: 'clone', m: { engine: 'utm', name: src } }); }}>Next</button>
            </div>
          </Modal>
        )
      )}
      {dialog?.kind === 'iso' && (
        <IsoDialog hasLabWindows={hasLabWindows} onClose={() => setDialog(null)}
                   onBuild={async () => {
                     setDialog(null);
                     try { const r = await runLabCommand('windows-vm', ['create']); setRun({ ...r, output: '' }); }
                     catch (err) { setError(errorText(err)); }
                   }} />
      )}
      {dialog?.kind === 'adopt' && (
        <Modal title={`Set the OS for ${dialog.m.name}`} onClose={() => setDialog(null)}>
          <label className="mt-field">Operating system
            <select value={dialog.os || 'windows'} onChange={(e) => setDialog({ ...dialog, os: e.target.value })}>
              <option value="windows">Windows</option><option value="linux">Linux</option><option value="macos">macOS</option>
            </select>
          </label>
          <p className="lab-note">So Rivendell knows how to turn on logging, install Atomic Red Team and record on it.</p>
          <div className="mt-modal-actions">
            <button className="mt-pill" onClick={() => setDialog(null)}>Cancel</button>
            <button onClick={() => post('adopt', { engine: dialog.m.engine, name: dialog.m.name, os: dialog.os || 'windows' })}>Save</button>
          </div>
        </Modal>
      )}
      {dialog?.kind === 'provision' && (
        <Modal title={`Set up ${dialog.m.name}`} onClose={() => setDialog(null)}>
          <p className="lab-note">Each step changes the machine. Snapshot it first.</p>
          <div className="mt-row">
            {dialog.steps.map((s) => (
              <button key={s.step} className="mt-pill" onClick={() => post('provision', { engine: dialog.m.engine, name: dialog.m.name, os: dialog.m.os, step: s.step })}>{s.label}</button>
            ))}
          </div>
        </Modal>
      )}
      {dialog?.kind === 'record' && (
        <RecordDialog machine={dialog.m} labWindows={dialog.m.name === data.lab_windows_vm}
                      onCancel={() => setDialog(null)} onRun={(body) => post('record', body)} />
      )}
      {dialog?.kind === 'logs' && (
        <Modal title={`Logs — ${dialog.m.name}`} onClose={() => setDialog(null)}>
          <pre className="lab-output">{dialog.text || 'No output'}</pre>
        </Modal>
      )}
    </>
  );
}

// ---------------------------------------------------------------- recorded telemetry

function TechniqueDetail({ tid }) {
  const [t, setT] = useState(null);
  useEffect(() => { getTelemetryTechnique(tid).then(setT).catch(() => setT({ error: true })); }, [tid]);
  if (!t) return <p className="lab-note">Loading…</p>;
  if (t.error) return <p className="lab-note mt-bad">Couldn't load {tid}</p>;
  const g = t.defender;
  return (
    <div className="mt-detail">
      {!t.exact && <p className="lab-note">No recording is mapped to {tid} itself; these are its {tid.includes('.') ? 'parent' : 'sub-techniques'}'.</p>}
      <p className="mt-dim">
        Logs most recordings hold: Defender XDR {(t.need?.mde || []).map((n) => n.name).join(', ') || '—'} ·
        Chronicle UDM {(t.need?.udm || []).map((n) => n.name).join(', ') || '—'}
      </p>
      {g ? (
        <p className="mt-dim"><img className="mt-icon" src={`${IMG}/microsoft.png`} alt="" /> Defender XDR alerting (Microsoft GUIDE): {g.alerts} alerts across {g.orgs} organisations, {Math.round((g.tp_rate || 0) * 100)}% true positives.</p>
      ) : (
        <p className="mt-dim">No Defender XDR alert in Microsoft GUIDE maps to this technique: a custom detection is where coverage comes from.</p>
      )}
      <table className="lab-table">
        <thead><tr><th>Log</th><th>Collection</th><th>Recordings</th><th>Events</th><th>Defender XDR</th><th>UDM</th></tr></thead>
        <tbody>
          {(t.event_types || []).slice(0, 25).map((r) => (
            <tr key={r.event} className={r.common ? 'mt-common' : ''} title={r.common ? 'Also in most recordings of other techniques (lab background)' : ''}>
              <td>{r.label}</td><td>{r.collection}</td><td>{r.recordings}</td><td>{r.events.toLocaleString()}</td><td>{r.mde}</td><td>{r.udm}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ul className="mt-recordings">
        {(t.recordings || []).slice(0, 30).map((d) => (
          <li key={d.id}>
            <img className="mt-icon" src={`${IMG}/${(SOURCES.find((s) => s.key === d.source) || {}).img || 'tux.svg'}`} alt="" />
            {d.url ? <a href={d.url} target="_blank" rel="noopener noreferrer">{d.title}</a> : d.title}
            <span className="mt-dim"> · {d.platforms.join(', ')} · {d.events.toLocaleString()} events</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function TelemetryViews({ refreshKey }) {
  const [rows, setRows] = useState([]);
  const [platform, setPlatform] = useState('');
  const [collection, setCollection] = useState('');
  const [q, setQ] = useState('');
  const [found, setFound] = useState(null);
  const [page, setPage] = useState(0);
  const [open, setOpen] = useState(null);
  const [meta, setMeta] = useState({ collections: {}, platforms: {} });

  useEffect(() => {
    getTelemetryTechniques({ platforms: platform, collections: collection })
      .then((r) => { setRows(r.techniques || []); setMeta({ collections: r.collections || {}, platforms: r.platforms || {} }); setPage(0); })
      .catch(() => setRows([]));
  }, [platform, collection, refreshKey]);

  useEffect(() => {
    if (q.trim().length < 3) { setFound(null); return undefined; }
    const timer = setTimeout(() => searchTelemetry(q.trim()).then((r) => setFound(r.techniques || {})).catch(() => setFound({})), 400);
    return () => clearTimeout(timer);
  }, [q]);

  const shown = found ? rows.filter((r) => found[r.technique] || Object.keys(found).some((t) => t.startsWith(`${r.technique}.`))) : rows;
  const pageRows = shown.slice(page * PAGE, (page + 1) * PAGE);
  return (
    <>
      <div className="mt-filters">
        <input type="search" value={q} maxLength={200} onChange={(e) => setQ(e.target.value)}
               placeholder="Search indicators: a value in the recorded events (comsvcs, lsass.dmp, vssadmin…)" />
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="">All platforms</option>
          {Object.entries(meta.platforms).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select value={collection} onChange={(e) => setCollection(e.target.value)}>
          <option value="">All logging</option>
          {Object.entries(meta.collections).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <span className="mt-dim">{shown.length} techniques</span>
      </div>
      <table className="lab-table mt-techniques">
        <thead><tr><th>Technique</th><th>Recordings</th><th>Logs most recordings hold</th><th>Defender XDR</th><th>Platforms</th></tr></thead>
        <tbody>
          {pageRows.map((r) => (
            <React.Fragment key={r.technique}>
              <tr className="mt-click" onClick={() => setOpen(open === r.technique ? null : r.technique)}>
                <td><a href={`https://attack.mitre.org/techniques/${r.technique.replace('.', '/')}/`} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>{r.technique}</a></td>
                <td>{Object.entries(r.sources).map(([k, n]) => `${n} ${k}`).join(', ')}</td>
                <td>{found && found[r.technique] ? <span className="mt-seen">seen in {found[r.technique].join(', ')}</span> : r.logs.slice(0, 3).join(', ')}</td>
                <td>{r.mde.join(', ')}</td>
                <td>{r.platforms.join(', ')}</td>
              </tr>
              {open === r.technique && <tr><td colSpan="5"><TechniqueDetail tid={r.technique} /></td></tr>}
            </React.Fragment>
          ))}
        </tbody>
      </table>
      {shown.length > PAGE && (
        <div className="mt-row mt-pager">
          <button className="mt-pill" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <span className="mt-dim">{page + 1} / {Math.ceil(shown.length / PAGE)}</span>
          <button className="mt-pill" disabled={(page + 1) * PAGE >= shown.length} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </>
  );
}

// ---------------------------------------------------------------- page

export function MordorTabs({ active }) {
  return (
    <div className="mt-tabs">
      <Link className={active === 'datasets' ? 'is-active' : ''} to="/mordor">Datasets</Link>
      <Link className={active === 'telemetry' ? 'is-active' : ''} to="/mordor/telemetry">Recorded telemetry &amp; lab</Link>
    </div>
  );
}

function MordorTelemetry() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  const [status, setStatus] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [error, setError] = useState(null);

  const loadStatus = useCallback(async () => {
    try { setStatus(await getTelemetryStatus()); } catch (err) { setError(errorText(err)); }
  }, []);
  useEffect(() => { loadStatus(); }, [loadStatus]);

  // Follow an Update until it's done, then reload everything that reads the data
  useEffect(() => {
    if (status?.build?.state !== 'running') return undefined;
    const timer = setTimeout(async () => {
      const s = await getTelemetryStatus().catch(() => null);
      if (s) {
        setStatus(s);
        if (s.build.state !== 'running') setRefreshKey((k) => k + 1);
      }
    }, 2000);
    return () => clearTimeout(timer);
  }, [status]);

  const update = async () => {
    try { await updateTelemetry(); loadStatus(); } catch (err) { setError(errorText(err)); }
  };
  const recorded = () => { loadStatus(); setRefreshKey((k) => k + 1); };

  return (
    <div className="journey-detail mt-page">
      <header>
        <h2>Mordor Recordings</h2>
        <p>Which logs record each ATT&amp;CK technique, from attacks emulated and recorded in labs, and the lab that records your own.</p>
      </header>
      <MordorTabs active="telemetry" />
      {error && <div className="card lab-error">{error}</div>}

      <div className="mt-tiles">
        <div className="mt-tile"><div className="mt-num">{status ? status.datasets.toLocaleString() : '–'}</div><div>Recordings</div></div>
        <div className="mt-tile"><div className="mt-num">{status ? status.techniques : '–'}</div><div>Techniques</div></div>
        <div className="mt-tile"><div className="mt-num">{status ? (status.values ? 'Ready' : 'No values') : '–'}</div><div>Indicator check</div></div>
      </div>

      <div className="card">
        <h2>Generating telemetry</h2>
        <Pipeline />
        <p className="lab-note">
          Recordings are real attacks run in a lab with logging on: the public datasets that ship with Rivendell, plus any you
          record yourself in <strong>Your lab</strong> below. Each is mapped to ATT&amp;CK, then Rivendell checks whether the
          indicators a detection matches actually appear in the recorded events. The result is the <strong>Recorded telemetry</strong>
          {' '}view below. No AI is involved.
        </p>
        <Sources status={status} isAdmin={isAdmin} onUpdate={update} />

        <h3 className="mt-labhead">Your lab</h3>
        <p className="lab-note">
          Create and manage the containers and VMs a recording runs on, without leaving Rivendell. Rivendell drives Docker and Tart
          to create Linux and macOS machines, and UTM for Windows. The lab's own machines (its Gandalf targets and VMs) are here
          too. The machines are disposable: snapshot one before you turn logging on or run atomics, and revert when you're done.
        </p>
        {isAdmin ? <LabSection onRecorded={recorded} /> : <p className="lab-note">Sign in as an admin to create and manage machines.</p>}
      </div>

      <div className="card">
        <h2>Recorded telemetry</h2>
        <p className="lab-note">Every recorded technique and the logs most of its recordings hold. Open one for its recordings, the event types they hold and Defender XDR's alerting on it. Search finds the techniques whose recorded events contain a value.</p>
        <TelemetryViews refreshKey={refreshKey} />
      </div>
    </div>
  );
}

export default MordorTelemetry;
