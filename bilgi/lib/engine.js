import * as THREE from 'three';
export { THREE };
export const W = 1080, H = 1920;
// ---------- yardımcılar ----------
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const prog = (t, s, d) => clamp((t - s) / d);
export const ease = x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
export const easeOut = x => 1 - Math.pow(1 - x, 3);
export const back = x => { const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
export const lerp = (a, b, k) => a + (b - a) * k;
export function hash(x, y, z) { return Math.sin(x * 1.7 + y * 3.1 + z * 2.3) * Math.cos(x * 2.9 - z * 1.3 + y * .7) + .5 * Math.sin(x * 5.1 + z * 4.7 + y * 3.3); }
export function gradTex(top, bottom) {
  const c = document.createElement('canvas'); c.width = 4; c.height = 512; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, top); gr.addColorStop(1, bottom);
  g.fillStyle = gr; g.fillRect(0, 0, 4, 512); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
export function snow(n, spread, color = 0xcfe8ff, size = 0.5) {
  const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { p[i * 3] = (Math.random() - .5) * spread[0]; p[i * 3 + 1] = (Math.random() - .5) * spread[1]; p[i * 3 + 2] = (Math.random() - .5) * spread[2]; }
  g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  return new THREE.Points(g, new THREE.PointsMaterial({ color, size, transparent: true, opacity: .7, depthWrite: false }));
}
export const std = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: .6, metalness: .1 }, o));
export const rnd = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();

// deniz tabanı kesiti (1 birim = 100 m), hendek ortada
export function trenchFloor() {
  const sh = new THREE.Shape(); sh.moveTo(-160, -150);
  for (let i = 0; i <= 160; i++) {
    const x = -160 + i * 2; const d = Math.abs(x);
    let y = d > 34 ? -42 - 6 * Math.sin(x * .07) : -42 - (109.35 - 42) * Math.pow(Math.cos(d / 34 * Math.PI / 2), 1.6);
    y += 1.2 * Math.sin(x * .9) ; sh.lineTo(x, y);
  }
  sh.lineTo(160, -150); sh.lineTo(-160, -150);
  const g = new THREE.ExtrudeGeometry(sh, { depth: 60, bevelEnabled: false, steps: 1 });
  g.translate(0, 0, -30);
  return new THREE.Mesh(g, std(0x3a3226, { roughness: .95 }));
}
export function mountain(h, r, seg = 72) {
  const g = new THREE.ConeGeometry(r, h, 160, 60, false); const pos = g.attributes.position; const col = [];
  const c1 = new THREE.Color(0x6b5a4a), c2 = new THREE.Color(0xf4f8ff), c3 = new THREE.Color(0x4a4038);
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i); const k = (y + h / 2) / h;
    const n = hash(x * .25, y * .25, z * .25) * (1 - k) * r * .18;
    const len = Math.hypot(x, z) || 1; pos.setX(i, x + x / len * n); pos.setZ(i, z + z / len * n);
    const c = (k > .62 + .06 * hash(x, z, y)) ? c2 : (k < .15 ? c3 : c1); col.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
  return new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .8 }));
}


// ================= motor =================
export async function run(slug) {
  Math.random = rnd;
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.body.prepend(renderer.domElement);
  const ov = document.getElementById('ov');
  const base = `videos/${slug}/`;
  const WORDS = await (await fetch(base + 'w.json')).json();
  const L = await import('./engine.js');
  const spec = (await import(`../${base}scene.js`)).default(L, WORDS);
  const S = spec.state || {};
  const shots = spec.shots.map(sh => { const s = new THREE.Scene(); const cam = new THREE.PerspectiveCamera(sh.fov || 40, W / H, .1, 3000); return { ...sh, s, cam, up: sh.build(s, cam, S) }; });
  const titles = spec.titles; const END = spec.END;
  const groups = []; { let cur = [];
    WORDS.forEach((w, i) => { cur.push(i); if (/[.,:;?!…]$/.test(w[0]) || cur.length >= 3) { groups.push(cur); cur = []; } });
    if (cur.length) groups.push(cur);
    for (let k = groups.length - 1; k > 0; k--) if (groups[k].length === 1 && groups[k - 1].length < 4 && !/[.:;?!…]$/.test(WORDS[groups[k - 1].slice(-1)[0]][0])) { groups[k - 1].push(...groups[k]); groups.splice(k, 1); } }
  let last = -1;
  const q = id => document.getElementById(id);
  function overlay(t) {
    let si = titles.findIndex(x => t >= x.t0 && t < x.t1); if (si < 0) si = titles.length - 1; const T = titles[si];
    if (si !== last) { ov.innerHTML = `<div class="vig"></div>` + T.html + `<div class="gradb"></div><div class="brand">● <b>BİR SORU</b> BİR VİDEO</div><div class="cap" id="cap"></div><div id="flash"></div>`; last = si; }
    const loc = t - T.t0;
    ov.querySelectorAll('.tagw,.title').forEach((e, i) => { const k = easeOut(prog(loc, .05 + i * .12, .35)); e.style.opacity = k; e.style.transform = `translateY(${(1 - k) * 30}px)`; });
    if (spec.update) spec.update(t, q, S);
    // takip düğmesi (spec.follow = {t, click})
    if (q('fb') && spec.follow) { const F = spec.follow; const k = back(prog(t, F.t, .4)); const fb = q('fb'); fb.style.opacity = prog(t, F.t, .2); fb.style.transform = `translateX(-50%) scale(${Math.max(.01, k)})`;
      const ok = t > F.click; fb.className = 'btn' + (ok ? ' ok' : ''); fb.textContent = ok ? '✓ Takip Edildi' : 'Takip Et';
      const h = q('hd'); if (h) { const hk = easeOut(prog(t, F.click - .65, .4)); h.style.opacity = hk * (1 - prog(t, F.click + .45, .3)); h.style.left = '640px'; h.style.top = (1290 + (1 - hk) * 120 - (Math.abs(t - F.click + .05) < .2 ? 25 : 0)) + 'px'; } }
    // altyazı: son grup videonun sonuna kadar ekranda kalır
    let gi = -1; for (let k = 0; k < groups.length; k++) if (t >= WORDS[groups[k][0]][1] - .08) gi = k;
    const cap = q('cap');
    if (gi >= 0) { const g = groups[gi]; const cur = g.filter(i => t >= WORDS[i][1] - .05).pop();
      cap.innerHTML = g.map(i => `<span class="${i === cur ? 'on' : (t >= WORDS[i][1] - .05 ? '' : 'dim')}">${WORDS[i][0]}</span>`).join(''); }
    else cap.innerHTML = '';
    const nb = Math.min(...titles.slice(1).map(x => Math.abs(t - x.t0)));
    q('flash').style.opacity = nb < .12 ? (1 - nb / .12) * .9 : 0;
  }
  window.setTime = t => { const sh = shots.find(x => t >= x.t0 && t < x.t1) || shots[shots.length - 1]; sh.up(t); renderer.render(sh.s, sh.cam); overlay(t); };
  window.END = END;
  window.SFX = [...shots.slice(1).map(s => [s.t0 - .2, 'whoosh', 1]), ...(spec.sfx || []), ...(spec.follow ? [[spec.follow.click, 'click', 1]] : [])];
  await document.fonts.load('700 100px Osw', 'ŞİĞÇÖÜ'); await document.fonts.load('700 50px Pop');
  window.READY = true;
}
