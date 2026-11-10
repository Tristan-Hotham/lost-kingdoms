/* Lost kingdoms on the high street. Every UK business, club, public body, street and named site in OpenStreetMap named after
 * an early medieval kingdom, over the kingdoms' approximate extents (heartland, around AD 800, widest), on a plain MapLibre
 * base map (OpenFreeMap Positron). Filled dots: inside the name's own extent; rings: outside.
 * Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const CLS = { b: 'business, club or society', p: 'public body', s: 'street', x: 'named building or site' };
  let map = null, D = null, kSel = +(qs.get('k') ?? -1);
  const types = { b: true, p: true, s: false, x: false };
  document.getElementById('theme').addEventListener('click', () => { const r = document.documentElement, d = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = d ? 'light' : 'dark'; });
  const ct = document.getElementById('cartouche'); const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));

  function colorExpr() { const e = ['match', ['get', 'k']]; D.col.forEach((c, i) => e.push(i, c)); e.push('#888'); return e; }
  function filt() {
    const t = Object.keys(types).filter(x => types[x]);
    const f = ['all', ['in', ['get', 'c'], ['literal', t]]];
    if (kSel >= 0) f.push(['==', ['get', 'k'], kSel]);
    return f;
  }
  function refresh() {
    ['pts', 'rings', 'lbl'].forEach(l => map.setFilter(l, ['all', filt(), l === 'pts' ? ['==', ['get', 'in'], 1] : l === 'rings' ? ['==', ['get', 'in'], 0] : true]));
    ['ex-main-f', 'ex-main-l', 'ex-wide-l', 'ex-core-f'].forEach(l => map.setFilter(l, ['all', ['==', ['get', 'version'], l.split('-')[1]], kSel >= 0 ? ['==', ['get', 'kingdom'], D.names[kSel]] : ['!=', ['get', 'kingdom'], '__none']]));
    document.querySelectorAll('.chip[data-k]').forEach(x => x.setAttribute('aria-pressed', +x.dataset.k === kSel));
  }
  function popup(p, ll) {
    const k = D.names[p.k];
    let h = `<b class="t">${esc(p.n)}</b><div class="nt">${esc(CLS[p.c])} named after <b style="color:${D.col[p.k]}">${esc(k)}</b></div><table>`;
    h += `<tr><td>Where</td><td>${esc(p.d || 'n/a')}</td></tr>`;
    h += `<tr><td>Kingdom</td><td>${p.in ? '<b>inside</b> the approximate extent' : `<b>outside</b>, ${p.dkm} km from the approximate extent`}</td></tr>`;
    h += `<tr><td>Centre</td><td>${esc(D.core[p.k])}</td></tr></table>`;
    if (p.pd) h += '<p class="nt">The name comes from a place named after the kingdom (for example Sherburn in Elmet).</p>';
    if (p.amb) h += '<p class="nt">Lindsey is also a first name: this one could be named after a person.</p>';
    h += `<p class="nt">Source: <a href="https://www.openstreetmap.org/${esc(p.o)}" target="_blank" rel="noopener">OpenStreetMap</a> (ODbL). Extents are approximate.</p>`;
    new maplibregl.Popup({ maxWidth: '330px', anchor: small ? 'bottom' : undefined }).setLngLat(ll).setHTML(h).addTo(map);
  }
  function setup(ex) {
    const C = D.cols, feats = D.f.map((r, i) => { const o = {}; C.forEach((c, j) => o[c] = r[j]);
      return { type: 'Feature', properties: { i, n: o.name, k: o.k, c: o.cls, in: o.in, dkm: o.dkm, d: o.district, o: o.osm, pd: o.pd, amb: o.amb }, geometry: { type: 'Point', coordinates: [o.lon, o.lat] } }; });
    map.addSource('ex', { type: 'geojson', data: ex, attribution: 'Extents: approximate, after Hill (1981) and Yorke (1990)' });
    const kc = ['match', ['get', 'kingdom']]; D.names.forEach((n, i) => kc.push(n, D.col[i])); kc.push('#888');
    const firstSym = map.getStyle().layers.find(l => l.type === 'symbol');
    const before = firstSym ? firstSym.id : undefined;
    map.addLayer({ id: 'ex-main-f', type: 'fill', source: 'ex', filter: ['==', ['get', 'version'], 'main'], paint: { 'fill-color': kc, 'fill-opacity': 0.10 } }, before);
    map.addLayer({ id: 'ex-core-f', type: 'fill', source: 'ex', filter: ['==', ['get', 'version'], 'core'], layout: { visibility: 'none' }, paint: { 'fill-color': kc, 'fill-opacity': 0.16 } }, before);
    map.addLayer({ id: 'ex-main-l', type: 'line', source: 'ex', filter: ['==', ['get', 'version'], 'main'], paint: { 'line-color': kc, 'line-width': ['interpolate', ['linear'], ['zoom'], 4, 1, 9, 2.2], 'line-opacity': 0.8 } }, before);
    map.addLayer({ id: 'ex-wide-l', type: 'line', source: 'ex', filter: ['==', ['get', 'version'], 'wide'], layout: { visibility: 'none' }, paint: { 'line-color': kc, 'line-width': 1.4, 'line-dasharray': [3, 2] } }, before);
    map.addSource('f', { type: 'geojson', data: { type: 'FeatureCollection', features: feats }, attribution: 'Names: OpenStreetMap contributors (ODbL)' });
    const rad = ['interpolate', ['linear'], ['zoom'], 4, ['match', ['get', 'c'], 'b', 4, 'p', 4, 3], 9, 6.5, 14, 9];
    map.addLayer({ id: 'rings', type: 'circle', source: 'f', paint: { 'circle-radius': rad, 'circle-color': '#fff', 'circle-stroke-color': colorExpr(), 'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 4, 2, 10, 3] } });
    map.addLayer({ id: 'pts', type: 'circle', source: 'f', paint: { 'circle-radius': rad, 'circle-color': colorExpr(), 'circle-stroke-color': '#fff', 'circle-stroke-width': 1.2, 'circle-opacity': ['match', ['get', 'c'], 'b', 0.95, 'p', 0.95, 0.75] } });
    map.addLayer({ id: 'lbl', type: 'symbol', source: 'f', minzoom: 9, layout: { 'text-field': ['get', 'n'], 'text-size': 11.5, 'text-font': ['Noto Sans Regular'], 'text-offset': [0, 1.1], 'text-anchor': 'top', 'text-optional': true }, paint: { 'text-color': '#2B2119', 'text-halo-color': '#fff', 'text-halo-width': 1.5 } });
    ['pts', 'rings'].forEach(l => { map.on('click', l, e => { const f = e.features[0]; popup(f.properties, f.geometry.coordinates); }); map.on('mouseenter', l, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', l, () => map.getCanvas().style.cursor = ''); });
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', e => { e.stopPropagation(); const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.addEventListener('click', e => { if (!lp.contains(e.target) && e.target !== btn) { lp.classList.remove('open'); btn.setAttribute('aria-expanded', false); } });
    const vis = (ids, v) => ids.forEach(id => map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none'));
    [['tyB', 'b'], ['tyP', 'p'], ['tyS', 's'], ['tyX', 'x']].forEach(([id, c]) => { const el = document.getElementById(id); el.checked = types[c]; el.addEventListener('change', e => { types[c] = e.target.checked; refresh(); }); });
    document.getElementById('exM').addEventListener('change', e => vis(['ex-main-f', 'ex-main-l'], e.target.checked));
    document.getElementById('exW').addEventListener('change', e => vis(['ex-wide-l'], e.target.checked));
    document.getElementById('exC').addEventListener('change', e => vis(['ex-core-f'], e.target.checked));
    document.getElementById('lyL').addEventListener('change', e => vis(['lbl'], e.target.checked));
    const baseSym = map.getStyle().layers.filter(l => l.type === 'symbol' && l.id !== 'lbl').map(l => l.id);
    document.getElementById('lyB').addEventListener('change', e => vis(baseSym, e.target.checked));
    document.querySelectorAll('.chip[data-k]').forEach(b => b.addEventListener('click', () => { kSel = +b.dataset.k; refresh(); }));
    const g = document.getElementById('keyGrid');
    D.names.forEach((n, i) => { if (!D.f.some(r => r[1] === i)) return; const d = document.createElement('div'); d.className = 'row'; d.innerHTML = `<span class="sw" style="background:${D.col[i]}"></span>${esc(n)}`; g.appendChild(d); });
    refresh();
  }
  function go(i) {
    const r = D.f[i]; fold(true);
    const ll = [r[4], r[3]];
    const c = r[2]; if (!types[c]) { types[c] = true; document.getElementById({ b: 'tyB', p: 'tyP', s: 'tyS', x: 'tyX' }[c]).checked = true; }
    if (kSel >= 0 && kSel !== r[1]) kSel = -1;
    refresh();
    map.flyTo({ center: ll, zoom: small ? 11 : 12, duration: 1200, offset: [0, Math.round(map.getContainer().clientHeight * (small ? 0.3 : 0.22))] });
    map.once('moveend', () => popup({ n: r[0], k: r[1], c: r[2], in: r[5], dkm: r[6], d: r[7], o: r[8], pd: r[9], amb: r[10] }, ll));
  }
  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug'); let items = [], k = -1;
    const idx = D.f.map((r, i) => ({ t: r[0], s: r[7], nn: norm(r[0] + ' ' + r[7]), i }));
    const show = () => { const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1; if (v.length < 2) { sug.style.display = 'none'; return; }
      const w = v.split(/\s+/);
      items = idx.filter(x => w.every(t => x.nn.includes(t))).sort((a, b) => (norm(a.t).startsWith(v) ? 0 : 1) - (norm(b.t).startsWith(v) ? 0 : 1)).slice(0, 14);
      items.forEach((it, j) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.innerHTML = `${esc(it.t)} <span>${esc(it.s)}</span>`; li.addEventListener('mousedown', e => { e.preventDefault(); pick(j); }); sug.appendChild(li); });
      sug.style.display = items.length ? 'block' : 'none'; };
    const pick = j => { const it = items[j]; if (!it) return; q.value = it.t; sug.style.display = 'none'; go(it.i); };
    q.addEventListener('input', show);
    q.addEventListener('keydown', e => { const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) show(); pick(k < 0 ? 0 : k); } else if (e.key === 'Escape') sug.style.display = 'none'; });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }
  Promise.all([fetch('data/site.json').then(r => r.json()), fetch('data/extents_web.geojson').then(r => r.json())]).then(([d, ex]) => {
    D = d;
    const at = (qs.get('at') || '').split(',').map(Number);
    const mo = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { bounds: [[-8.3, 49.9], [1.9, 58.8]], fitBoundsOptions: { padding: small ? { top: 10, bottom: 60, left: 10, right: 10 } : { top: 40, bottom: 40, left: 360, right: 60 } } };
    const m0 = new maplibregl.Map(Object.assign({ container: 'map', style: STYLE, attributionControl: { compact: true }, maxZoom: 16 }, mo));
    return new Promise((res, rej) => { m0.once('load', () => res([m0, ex])); m0.once('error', e => { if (!m0.loaded()) rej(e.error || e); }); });
  }).then(([mm, ex]) => {
    map = mm; window.__map = mm;
    mm.on('error', e => { const er = e && e.error; if (er && (er.name === 'AbortError' || /abort/i.test(er.message || ''))) return; console.error(er || e); });
    const n = document.getElementById('nojs'); if (n) n.remove();
    mm.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(at => { at.classList.remove('maplibregl-compact-show'); at.removeAttribute('open'); });
    mm.once('idle', foldAt); setTimeout(foldAt, 1500);
    setup(ex); setupSearch();
  }).catch(e => { const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + (e && e.message || e); console.error(e); });
})();
