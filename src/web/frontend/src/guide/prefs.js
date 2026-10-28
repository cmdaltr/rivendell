// What each person wants at start-up, and the tips they've seen lately. Kept in this
// browser (per user), so a blocked or cleared storage just means the defaults: offer both.
import { TIPS } from './content';

const RECENT = 10;
const key = (user, name) => `rivendell.${user?.username || 'local'}.${name}`;

function read(name, fallback) {
  try {
    const raw = window.localStorage.getItem(name);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function write(name, value) {
  try {
    window.localStorage.setItem(name, JSON.stringify(value));
  } catch {
    // Private window or storage blocked: the choice lasts until the page closes
  }
}

export function startPrefs(user) {
  return {
    guide: read(key(user, 'guideAtStart'), true),
    tips: read(key(user, 'tipsAtStart'), true),
  };
}

export function setStartPref(user, which, value) {
  write(key(user, which === 'guide' ? 'guideAtStart' : 'tipsAtStart'), value);
}

/** A random tip, avoiding the last ten this person saw, and remembered as seen. */
export function nextTip(user, exclude) {
  const recent = read(key(user, 'recentTips'), []);
  const avoid = new Set([...recent, exclude].filter(Boolean));
  let pool = TIPS.filter((tip) => !avoid.has(tip.id));
  if (!pool.length) pool = TIPS.filter((tip) => tip.id !== exclude);
  const tip = pool[Math.floor(Math.random() * pool.length)];
  write(key(user, 'recentTips'), [...recent.filter((id) => id !== tip.id), tip.id].slice(-RECENT));
  return tip;
}

// Once per start: per tab session, so a reload doesn't offer it again
export function offeredThisStart() {
  try {
    return window.sessionStorage.getItem('rivendell.offered') === '1';
  } catch {
    return false;
  }
}

export function markOffered() {
  try {
    window.sessionStorage.setItem('rivendell.offered', '1');
  } catch {
    // nothing to remember it in
  }
}
