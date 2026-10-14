import { $ } from './util.js';

let toastTimer;
export function toast(text) {
  const t = $('#toast');
  t.textContent = text;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2600);
}

export function openDialog(content) {
  const d = $('#dialog');
  $('#dialog-body').innerHTML = String(content);
  if (!d.open) d.showModal();
  d.querySelector('[data-close]')?.addEventListener('click', closeDialog);
  return d;
}

export const closeDialog = () => { const d = $('#dialog'); if (d.open) d.close(); };
