import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  getLabStatus,
  getLabState,
  saveLabConfig,
  setLabPassword,
  runLabCommand,
  listLabRuns,
  getLabRun,
  cancelLabRun,
} from '../api';

const errorText = (err) => {
  const detail = err.response?.data?.detail;
  if (!detail) return err.message;
  return typeof detail === 'string' ? detail : JSON.stringify(detail);
};

const SETTINGS = [
  ['LAB_DATA_DIR', 'Lab data directory', 'Collected acquisitions and Mordor datasets go here.'],
  ['TEST_IMAGES_PATH', 'Test images root', "Rivendell's test root; the lab writes gandalf/ and mordor/ under it when set."],
  ['LAB_VM_DIR', 'VM directory', 'Vagrant boxes, VirtualBox and Tart VMs.'],
  ['WINDOWS_VM_MEMORY_MB', 'Windows VM memory (MB)', ''],
  ['WINDOWS_VM_CPUS', 'Windows VM CPUs', ''],
  ['LINUX_VM_MEMORY_MB', 'Linux VM memory (MB)', ''],
  ['ELASTIC_URL', 'Elasticsearch URL', 'Used by the Mordor sensor helpers.'],
];

const MORDOR_GROUPS = {
  'All datasets the tests use': [],
  'APT29 days 1 and 2': ['apt29/day1', 'apt29/day2'],
  'Atomic (credential access, evasion, lateral movement, persistence)': [
    'atomic/credential_access', 'atomic/defense_evasion', 'atomic/lateral_movement', 'atomic/persistence',
  ],
};

const formatTime = (t) => (t ? new Date(t * 1000).toLocaleString() : '—');

function AgentPanel({ status, onRecheck }) {
  return (
    <div className="card">
      <h2>Lab agent not running</h2>
      <p>
        The lab's containers and VMs run on this machine, outside Rivendell's containers, so the web UI drives
        them through a small agent on the host. Start it from the repository on the machine running Rivendell:
      </p>
      <div className="lab-command"><code>cd lab && {status?.start_command || './lab.sh agent start'}</code></div>
      <p className="lab-note">
        It listens on loopback only and accepts nothing but the lab commands. First time? Run <code>./lab.sh</code>{' '}
        in a terminal and choose <em>Install prerequisites</em>, since that step needs your password.
      </p>
      {status?.detail && <p className="lab-note">Last error: {status.detail}</p>}
      <button onClick={onRecheck}>Check again</button>
    </div>
  );
}

function RunOutput({ run, onCancel, onClose }) {
  const preRef = useRef(null);
  useEffect(() => {
    if (preRef.current) preRef.current.scrollTop = preRef.current.scrollHeight;
  }, [run?.output]);
  if (!run) return null;
  return (
    <div className="card">
      <div className="lab-run-head">
        <h3>
          <code>./lab.sh {run.label}</code> <span className={`lab-status lab-status-${run.status}`}>{run.status}</span>
        </h3>
        <div className="lab-actions">
          {run.status === 'running'
            ? <button className="secondary" onClick={onCancel}>Cancel</button>
            : <button className="secondary" onClick={onClose}>Close</button>}
        </div>
      </div>
      <pre ref={preRef} className="lab-output">{run.output || 'Starting…'}</pre>
    </div>
  );
}

function Lab() {
  const { user } = useAuth();
  const [status, setStatus] = useState(null);
  const [state, setState] = useState(null);
  const [settings, setSettings] = useState({});
  const [password, setPassword] = useState('');
  const [runs, setRuns] = useState([]);
  const [run, setRun] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [collector, setCollector] = useState('bash');
  const [targets, setTargets] = useState([]);
  const [mordorGroup, setMordorGroup] = useState(Object.keys(MORDOR_GROUPS)[0]);
  const [preset, setPreset] = useState('');
  const offsetRef = useRef(0);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const s = await getLabStatus();
      setStatus(s);
      if (!s.available) return;
      const st = await getLabState();
      setState(st);
      setSettings(st.config || {});
      setTargets((prev) => (prev.length ? prev : st.linux_containers || []));
      setPreset((prev) => prev || (st.mordor_presets || [])[0] || '');
      setRuns(await listLabRuns());
      if (st.busy && !run) {
        offsetRef.current = 0;
        setRun({ ...st.busy, output: '' });
      }
    } catch (err) {
      setError(errorText(err));
    }
  }, [run]);

  useEffect(() => { refresh(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Follow the current run's output.
  useEffect(() => {
    if (!run || run.status !== 'running') return undefined;
    const timer = setInterval(async () => {
      try {
        const r = await getLabRun(run.id, offsetRef.current);
        offsetRef.current = r.offset;
        setRun((prev) => ({ ...r, output: (prev?.id === r.id ? prev.output || '' : '') + r.output }));
        if (r.status !== 'running') {
          setRuns(await listLabRuns());
          getLabState().then(setState).catch(() => {});
        }
      } catch (err) {
        setError(errorText(err));
      }
    }, 1500);
    return () => clearInterval(timer);
  }, [run?.id, run?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  const start = async (command, args = [], confirmText = null) => {
    if (confirmText && !window.confirm(confirmText)) return;
    setError(null);
    try {
      const r = await runLabCommand(command, args);
      offsetRef.current = 0;
      setRun({ ...r, output: '' });
    } catch (err) {
      setError(errorText(err));
    }
  };

  const openRun = async (id) => {
    try {
      const r = await getLabRun(id, 0);
      offsetRef.current = r.offset;
      setRun(r);
    } catch (err) {
      setError(errorText(err));
    }
  };

  const saveSettings = async () => {
    setError(null);
    setMessage(null);
    const changed = Object.fromEntries(
      Object.entries(settings).filter(([k, v]) => String(v ?? '') !== String(state.config?.[k] ?? '')),
    );
    if (!Object.keys(changed).length) { setMessage('Nothing changed.'); return; }
    try {
      await saveLabConfig(changed);
      setMessage('Settings saved.');
      setState(await getLabState());
    } catch (err) {
      setError(errorText(err));
    }
  };

  const savePassword = async () => {
    setError(null);
    setMessage(null);
    try {
      await setLabPassword(password);
      setPassword('');
      setMessage('Lab password stored in the host keyring.');
      setState(await getLabState());
    } catch (err) {
      setError(errorText(err));
    }
  };

  if (user && user.role !== 'admin') {
    return <div className="lab"><div className="card"><h2>Lab</h2><p>Only admins can run the test lab.</p></div></div>;
  }
  if (!status) return <div className="lab"><div className="card">Checking the lab agent…</div></div>;
  if (!status.available) return <div className="lab"><AgentPanel status={status} onRecheck={refresh} /></div>;
  if (!state) return <div className="lab"><div className="card">{error || 'Loading…'}</div></div>;

  const host = state.host || {};
  const busy = run?.status === 'running';
  const vagrant = ['macos-x86_64', 'linux-x86_64'].includes(host.profile);
  const tart = host.profile === 'macos-arm64';
  const noPassword = !state.password_set;

  const vmRow = (command, title, actions) => (
    <tr key={command}>
      <td>{title}</td>
      <td className="lab-actions">
        {actions.map((a) => (
          <button
            key={a}
            className="secondary"
            disabled={busy || (noPassword && a === 'create')}
            onClick={() => start(command, [a], a === 'delete' ? `Destroy the ${title}? Its disk is deleted.` : null)}
          >
            {a}
          </button>
        ))}
      </td>
    </tr>
  );

  return (
    <div className="lab">
      <h1>Test lab</h1>
      <p className="lab-note">
        Targets for Gandalf and datasets for Mordor, on this machine. Everything here runs <code>lab/lab.sh</code>{' '}
        on the host; the same commands work in a terminal.
      </p>

      {error && <div className="card lab-error">{error} <button className="secondary" onClick={() => setError(null)}>Dismiss</button></div>}
      {message && <div className="card lab-message">{message}</div>}

      <div className="card">
        <h2>Host</h2>
        <table className="lab-table">
          <tbody>
            <tr><th>Profile</th><td>{host.label} <code>{host.profile}</code></td></tr>
            <tr><th>System</th><td>{host.os_version}, {host.ram_gb} GB RAM</td></tr>
            <tr><th>Docker</th><td>{host.docker === 'yes' ? 'running' : 'not running: start Docker Desktop or OrbStack'}</td></tr>
            <tr><th>VMs</th><td>{host.vm_tool === 'none' ? 'not installed: run ./lab.sh install in a terminal' : host.vm_tool}</td></tr>
            <tr><th>Lab password</th><td>{state.password_set ? 'stored in the host keyring' : 'not set: set it below before creating targets'}</td></tr>
          </tbody>
        </table>
        <div className="lab-actions">
          <button className="secondary" disabled={busy} onClick={() => start('check')}>Check prerequisites</button>
          <button className="secondary" disabled={busy} onClick={() => start('status')}>Status</button>
          <button className="secondary" onClick={refresh}>Refresh</button>
        </div>
      </div>

      <RunOutput
        run={run}
        onCancel={async () => { try { setRun(await cancelLabRun(run.id).then((r) => ({ ...run, ...r }))); } catch (err) { setError(errorText(err)); } }}
        onClose={() => setRun(null)}
      />

      <div className="card">
        <h2>Settings</h2>
        <table className="lab-table">
          <tbody>
            {SETTINGS.map(([key, label, help]) => (
              <tr key={key}>
                <th>{label}</th>
                <td>
                  <input
                    type="text"
                    value={settings[key] ?? ''}
                    onChange={(e) => setSettings({ ...settings, [key]: e.target.value })}
                  />
                  {help && <div className="lab-note">{help}</div>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button onClick={saveSettings}>Save settings</button>
        <h3>Lab password</h3>
        <p className="lab-note">
          For the <code>gandalf</code> user on every lab target. At least 12 characters; no quotes, backslashes or spaces.
        </p>
        <div className="lab-actions">
          <input type="password" value={password} autoComplete="new-password" onChange={(e) => setPassword(e.target.value)} />
          <button onClick={savePassword} disabled={password.length < 12}>{state.password_set ? 'Replace' : 'Set'} password</button>
        </div>
      </div>

      <div className="card">
        <h2>Targets</h2>
        <table className="lab-table">
          <tbody>
            <tr>
              <td>Linux containers ({(state.linux_containers || []).join(', ')}; SSH on 127.0.0.1:2221-2224)</td>
              <td className="lab-actions">
                <button className="secondary" disabled={busy || noPassword} onClick={() => start('linux-targets', ['up'])}>up</button>
                <button className="secondary" disabled={busy} onClick={() => start('linux-targets', ['down'])}>down</button>
                <button className="secondary" disabled={busy || noPassword} onClick={() => start('linux-targets', ['reset'], 'Rebuild and re-seed all Linux containers?')}>reset</button>
                <button className="secondary" disabled={busy} onClick={() => start('linux-targets', ['status'])}>status</button>
              </td>
            </tr>
            {(vagrant || tart) && vmRow('linux-vm', 'Linux VM', ['create', 'start', 'stop', 'delete', 'status'])}
            {tart && vmRow('macos-vm', 'macOS VM', ['create', 'start', 'stop', 'delete', 'status'])}
            {vagrant && vmRow('windows-vm', 'Windows 11 VM', ['create', 'start', 'stop', 'provision', 'delete', 'status'])}
          </tbody>
        </table>
        {tart && (
          <p className="lab-note">
            Windows 11 ARM on Apple silicon needs UTM and a few manual steps; run <code>./lab.sh windows-vm</code> in a
            terminal for the guide.
          </p>
        )}
        {noPassword && <p className="lab-note">Set the lab password before creating targets.</p>}
      </div>

      <div className="card">
        <h2>Gandalf</h2>
        <div className="lab-actions">
          <select value={collector} onChange={(e) => setCollector(e.target.value)}>
            <option value="bash">Bash (gandalf.sh)</option>
            <option value="python">Python (gandalf.py)</option>
            {vagrant && <option value="powershell">PowerShell (Invoke-Gandalf.ps1, Windows VM)</option>}
            <option value="all">All</option>
          </select>
          {(state.linux_containers || []).map((t) => (
            <label key={t} className="lab-check">
              <input
                type="checkbox"
                checked={targets.includes(t)}
                onChange={(e) => setTargets(e.target.checked ? [...targets, t] : targets.filter((x) => x !== t))}
              />
              {t}
            </label>
          ))}
          {(vagrant || tart) && ['lab-linuxvm', ...(tart ? ['lab-macos'] : [])].map((t) => (
            <label key={t} className="lab-check">
              <input
                type="checkbox"
                checked={targets.includes(t)}
                onChange={(e) => setTargets(e.target.checked ? [...targets, t] : targets.filter((x) => x !== t))}
              />
              {t}
            </label>
          ))}
          <button disabled={busy || noPassword || (!targets.length && collector !== 'powershell')} onClick={() => start('gandalf-collect', [collector, ...(collector === 'powershell' ? [] : targets)])}>
            Collect
          </button>
        </div>
        <p className="lab-note">
          Archives land in <code>{(settings.TEST_IMAGES_PATH || settings.LAB_DATA_DIR)}/gandalf/&lt;collector&gt;_collection/acquisitions/</code>,
          with each target's <code>expected.json</code>. Then run <em>Rivendell test settings</em> below.
        </p>
      </div>

      <div className="card">
        <h2>Mordor</h2>
        <div className="lab-actions">
          <select value={mordorGroup} onChange={(e) => setMordorGroup(e.target.value)}>
            {Object.keys(MORDOR_GROUPS).map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
          <button disabled={busy} onClick={() => start('mordor-download', MORDOR_GROUPS[mordorGroup])}>Download OTRF datasets</button>
        </div>
        {vagrant && (
          <div className="lab-actions">
            <button className="secondary" disabled={busy} onClick={() => start('mordor-sensor', [], 'Install Sysmon, PowerShell logging and Atomic Red Team in the Windows VM?')}>Install sensor in Windows VM</button>
            <select value={preset} onChange={(e) => setPreset(e.target.value)}>
              {(state.mordor_presets || []).map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
            <button disabled={busy || !preset} onClick={() => start('mordor-capture', [preset], `Run the ${preset} Atomic tests in the Windows VM and capture the logs?`)}>Capture dataset</button>
          </div>
        )}
      </div>

      <div className="card">
        <h2>Rivendell</h2>
        <div className="lab-actions">
          <button className="secondary" disabled={busy} onClick={() => start('rivendell-env')}>Rivendell test settings</button>
          <button className="secondary" disabled={busy} onClick={() => start('teardown', [], 'Remove all lab containers and VMs? Collected data and the lab password are kept.')}>Tear down lab</button>
        </div>
        <p className="lab-note">
          Test settings writes the paths <code>tests/scripts/run_test.py</code> needs and checks Rivendell's worker can
          read the lab's data directory.
        </p>
      </div>

      {runs.length > 0 && (
        <div className="card">
          <h2>Recent runs</h2>
          <table className="lab-table">
            <thead><tr><th>Command</th><th>Status</th><th>Started</th><th /></tr></thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td><code>{r.label}</code></td>
                  <td><span className={`lab-status lab-status-${r.status}`}>{r.status}</span></td>
                  <td>{formatTime(r.started)}</td>
                  <td><button className="secondary" onClick={() => openRun(r.id)}>Output</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Lab;
