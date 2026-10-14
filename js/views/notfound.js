import { html } from '../util.js';

export const title = () => 'Nicht gefunden';
export const render = () => html`<div class="empty" style="margin-top:40px"><h2 style="font-size:34px;margin-bottom:8px">Hier ist nur ein Abgrund.</h2><p>Diese Seite gibt es nicht. <a href="#/">Zurück zur Übersicht</a></p></div>`;
