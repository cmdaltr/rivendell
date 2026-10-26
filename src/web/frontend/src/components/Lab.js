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

const IMG = `${process.env.PUBLIC_URL}/images/mordor`;
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

// section: 'settings' (host, settings, password) or 'lab' (targets, maintenance, runs)
function LabManage({ section = 'lab', children = null }) {
  const { user } = useAuth();
  const [status, setStatus] = useState(null);
  const [state, setState] = useState(null);
  const [settings, setSettings] = useState({});
  const [password, setPassword] = useState('');
  const [runs, setRuns] = useState([]);
  const [run, setRun] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
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

  const savePassword = async (value) => {
    setError(null);
    setMessage(null);
    try {
      await setLabPassword(value);
      setPassword('');
      setMessage(value ? 'Lab password stored in the host keyring.' : `Using the default lab password '${state.default_password}'.`);
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

  // A target as logos: what it runs, then what runs it; the full description is the tooltip
  const logos = (icons, tip) => (
    <td className="lab-target" title={tip}>
      {icons.map(([f, alt]) => (f.includes('.')
        ? <img key={f} className="lab-logo" src={`${IMG}/${f}`} alt={alt} />
        : <span key={f} className="lab-logo-text">{f}</span>))}
    </td>
  );
  const vmRow = (command, title, actions, icons) => (
    <tr key={command}>
      {logos(icons, title)}
      <td className="lab-actions">
        {actions.map((a) => (
          <button
            key={a}
            className="secondary"
            disabled={busy || (noPassword && (a === 'create' || a === 'adopt'))}
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

      {error && <div className="card lab-error">{error} <button className="secondary" onClick={() => setError(null)}>Dismiss</button></div>}
      {message && <div className="card lab-message">{message}</div>}

      {section === 'settings' && (
        <div className="card">
          <h2>Lab host and settings</h2>
          <div className="lab-facts">
            <span><em>Profile</em>{host.label} <code>{host.profile}</code></span>
            <span><em>System</em>{host.os_version}, {host.ram_gb} GB RAM</span>
            <span><em>Docker</em>{host.docker === 'yes' ? 'running' : 'not running'}</span>
            <span><em>VMs</em>{host.vm_tool === 'none' ? 'not installed (./lab.sh install)' : host.vm_tool}</span>
            <span><em>Password</em>{state.password_default ? <>default <code>{state.default_password}</code></> : 'custom, in the keyring'}</span>
          </div>
          <div className="lab-actions">
            <button className="secondary" disabled={busy} onClick={() => start('check')}>Check prerequisites</button>
            <button className="secondary" disabled={busy} onClick={() => start('status')}>Status</button>
            <button className="secondary" onClick={refresh}>Refresh</button>
          </div>
          <div className="lab-fields">
            {SETTINGS.map(([key, label, help]) => (
              <label key={key} className="lab-field" title={help}>
                <span>{label}</span>
                <input type="text" value={settings[key] ?? ''} placeholder={help}
                       onChange={(e) => setSettings({ ...settings, [key]: e.target.value })} />
              </label>
            ))}
          </div>
          <div className="lab-actions">
            <button onClick={saveSettings}>Save settings</button>
          </div>
          <div className="lab-fields">
            <label className="lab-field lab-field-wide" title="No quotes, backslashes or spaces. Targets created before a change keep their old password until they're re-created.">
              <span>Lab password, for the <code>gandalf</code> user on every target (a custom one goes in the host keyring)</span>
              <div className="lab-actions">
                <input type="password" value={password} autoComplete="new-password" onChange={(e) => setPassword(e.target.value)} />
                <button onClick={() => savePassword(password)} disabled={!password}>Set custom password</button>
                {!state.password_default && <button className="secondary" onClick={() => savePassword('')}>Use the default</button>}
              </div>
            </label>
          </div>
        </div>
      )}

      <RunOutput
        run={run}
        onCancel={async () => { try { setRun(await cancelLabRun(run.id).then((r) => ({ ...run, ...r }))); } catch (err) { setError(errorText(err)); } }}
        onClose={() => setRun(null)}
      />

      {section === 'lab' && (
      <>
      <div className="lab-split">
      <div className="card">
        <h2>Targets</h2>
        <table className="lab-table">
          <tbody>
            <tr>
              {logos([['ubuntu.png', 'Ubuntu'], ['tux.svg', 'Rocky'], ['docker.png', 'Docker']],
                `Linux containers: ${(state.linux_containers || []).join(', ')} (Ubuntu 24.04, Rocky 9), SSH on 127.0.0.1:2221-2222`)}
              <td className="lab-actions">
                <button className="secondary" disabled={busy || noPassword} onClick={() => start('linux-targets', ['up'])}>up</button>
                <button className="secondary" disabled={busy} onClick={() => start('linux-targets', ['down'])}>down</button>
                <button className="secondary" disabled={busy || noPassword} onClick={() => start('linux-targets', ['reset'], 'Rebuild and re-seed all Linux containers?')}>reset</button>
                <button className="secondary" disabled={busy} onClick={() => start('linux-targets', ['status'])}>status</button>
              </td>
            </tr>
            {(vagrant || tart) && vmRow('linux-vm', `Linux VM: Ubuntu with a real kernel (${tart ? 'Tart' : 'Vagrant'}), SSH on 127.0.0.1:2230`,
              ['create', 'start', 'stop', 'delete', 'status'], [['ubuntu.png', 'Ubuntu'], tart ? ['tart.png', 'Tart'] : ['Vagrant', 'Vagrant']])}
            {tart && vmRow('macos-vm', 'macOS VM: Sequoia (Tart), SSH on 127.0.0.1:2231',
              ['create', 'start', 'stop', 'delete', 'status'], [['macos.png', 'macOS'], ['tart.png', 'Tart']])}
            {vagrant && vmRow('windows-vm', 'Windows 11 VM (Vagrant)',
              ['create', 'start', 'stop', 'provision', 'delete', 'status'], [['windows.svg', 'Windows'], ['Vagrant', 'Vagrant']])}
            {tart && vmRow('windows-vm', "Windows 11 ARM VM (UTM), SSH on 127.0.0.1:2232. create installs it unattended from the ARM64 ISO in the lab's isos/ folder (Microsoft's download is manual); adopt takes an installed VM from utm/ that has OpenSSH and provisions it.",
              ['create', 'adopt', 'start', 'stop', 'delete', 'status'], [['windows.svg', 'Windows'], ['utm.svg', 'UTM']])}
          </tbody>
        </table>
        <p className="lab-note">Hover over a target for what it is and its SSH port.{noPassword && ' Set the lab password before creating targets.'}</p>
      </div>

      <div className="card">
        <h2>Recent runs</h2>
        {runs.length ? (
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
        ) : <p className="lab-note">No runs yet. Commands from this page and Deploy show here.</p>}
      </div>
      </div>

      <div className="card">
        <h2>Maintenance</h2>
        <div>
          <div className="lab-actions">
            <button className="secondary" disabled={busy} onClick={() => start('rivendell-env')}>Rivendell test settings</button>
            <button className="secondary" disabled={busy} onClick={() => start('teardown', [], 'Remove all lab containers and VMs? Collected data and the lab password are kept.')}>Tear down lab</button>
          </div>
          <p className="lab-note">
            Test settings writes the paths <code>tests/scripts/run_test.py</code> needs and checks Rivendell's worker can
            read the lab's data directory. Teardown removes every target; collected data and the password are kept.
          </p>
        </div>
      </div>

      {children}
      </>
      )}
    </div>
  );
}

// Aragorn → Settings (host, settings, password) and Aragorn → Lab (targets, maintenance, runs)
export default LabManage;
