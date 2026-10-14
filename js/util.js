// Kleine Helfer: sicheres HTML-Templating, DOM-Zugriff, Text-Normalisierung.

class SafeHTML {
  constructor(value) { this.value = value; }
  toString() { return this.value; }
}

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ESCAPES[c]);

function serialize(value) {
  if (value == null || value === false) return '';
  if (value instanceof SafeHTML) return value.value;
  if (Array.isArray(value)) return value.map(serialize).join('');
  return esc(value);
}

/** Tagged template: interpolierte Werte werden escaped, verschachtelte html``-Ergebnisse und Arrays nicht. */
export function html(strings, ...values) {
  let out = strings[0];
  for (let i = 0; i < values.length; i++) out += serialize(values[i]) + strings[i + 1];
  return new SafeHTML(out);
}
export const raw = (s) => new SafeHTML(String(s ?? ''));

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

export const slug = (s) => String(s ?? '')
  .toLowerCase()
  .normalize('NFKD').replace(/[̀-ͯ]/g, '')
  .replace(/['’`]/g, '')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

/** Normalisierter Vergleichsschlüssel für Namen ("Assassin's Dagger" == "assassins dagger"). */
export const norm = (s) => slug(s).replace(/-/g, '');

export const debounce = (fn, ms = 150) => {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
};

export const uniq = (arr) => [...new Set(arr.filter((x) => x != null && x !== ''))];

export const pct = (n, d) => (d ? Math.round((n / d) * 100) : 0);

export const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;

/** Suche: alle Wörter müssen im Heuhaufen vorkommen (diakritik-/case-insensitiv). */
export function matches(query, ...hay) {
  const q = fold(query).trim();
  if (!q) return true;
  const h = fold(hay.flat().filter(Boolean).join(' '));
  return q.split(/\s+/).every((w) => h.includes(w));
}
export const fold = (s) => String(s ?? '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/['’]/g, '');

export function download(filename, text, type = 'application/json') {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
