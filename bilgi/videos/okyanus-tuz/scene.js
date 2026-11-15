// Bilgi #16: Okyanuslar neden tuzlu? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: USGS Water Science School "Why is the ocean salty?" (tuz karadaki kayalardan gelir; yağmur havadaki CO2 ile hafif asidik
// olur, kayaları aşındırır; iyonlar nehirlerle okyanusa taşınır; tuzluluk ~35 binde = ağırlıkça %3,5; okyanus tuzu karaya yayılsa
// "166 metreden kalın", yaklaşık 40 katlı bir bina yüksekliğinde katman olurdu; en yaygın iyonlar klorür ve sodyum).
// NOAA Ocean Service "Why is the ocean salty?" (hidrotermal bacalar ve deniz altı volkanları da mineral ekler; ortalama tuzluluk 35 binde;
// klorür ve sodyum çözünmüş iyonların ~%85'i). Buharlaşma suyu alır, tuzu bırakır (NOAA: tuzluluk buharlaşmayla artar).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { mergeVertices } from '../../node_modules/three/examples/jsm/utils/BufferGeometryUtils.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  let seed = 1616; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const soft = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.4, 'rgba(255,255,255,.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
  function dust(n, sp, color = 0xcfe8ff, size = .2, op = .5, add = true) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
    for (let i = 0; i < n * 3; i += 3) { p[i] = (r1() - .5) * sp[0]; p[i + 1] = (r1() - .5) * sp[1]; p[i + 2] = (r1() - .5) * sp[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color, size, map: soft, transparent: true, opacity: op, depthWrite: false, blending: add ? THREE.AdditiveBlending : THREE.NormalBlending }));
  }
  function lights(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#0a1838', '#010308'])); s.fog = new THREE.Fog(o.fog || 0x02050e, o.near || 30, o.far || 110);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi || .8));
    const key = new THREE.DirectionalLight(0xfff4e0, o.key || 2.2); key.position.set(-10, 12, 10); s.add(key);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 600, 60); rim.position.set(6, 9, -5); s.add(rim);
    const d = dust(500, [26, 18, 16], o.dust || 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return { d, rim };
  }
  const glow = (c, op = .9) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false });
  function rock(r, c1 = 0x6b5e52, c2 = 0x8a7a6a, det = 5) {
    let g = new THREE.IcosahedronGeometry(r, det); g.deleteAttribute('normal'); g.deleteAttribute('uv'); g = mergeVertices(g); const P = g.attributes.position; const cc = [];
    for (let i = 0; i < P.count; i++) { const v = V(P.getX(i), P.getY(i), P.getZ(i)); const n = hash(v.x * 1.4 / r, v.y * 1.4 / r, v.z * 1.4 / r) * .14 + hash(v.x * 4 / r, v.y * 4 / r, v.z * 4 / r) * .05;
      v.multiplyScalar(1 + n); P.setXYZ(i, v.x, v.y, v.z); const c = new THREE.Color(c1).lerp(new THREE.Color(c2), clamp(.5 + n * 3)); cc.push(c.r, c.g, c.b); }
    g.setAttribute('color', new THREE.Float32BufferAttribute(cc, 3)); g.computeVertexNormals();
    return M(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .85, metalness: .05 }));
  }
  const salt = () => std(0xf4f8ff, { roughness: .25, metalness: .1, emissive: 0x3a4a5a, emissiveIntensity: .5 });
  function drops(s, n, x0, x1, ytop, ybot, zs = 2) {
    const m = glow(0x8fd0ff, .8); const arr = Array.from({ length: n }, () => { const d = M(new THREE.SphereGeometry(.05, 8, 8), m); d.scale.y = 3;
      d.userData = { x: lerp(x0, x1, r1()), z: (r1() - .5) * zs, ph: r1() }; s.add(d); return d; });
    arr.m = m; arr.up = (t, on = 1) => arr.forEach(d => { const c = (t * 1.1 + d.userData.ph) % 1; d.visible = on > d.userData.ph * .99; d.position.set(d.userData.x, lerp(ytop, ybot, c), d.userData.z); });
    return arr;
  }
  function cloud() { const g = new THREE.Group(); const m = std(0xc8d2e0, { roughness: .9, emissive: 0x1a2030 });
    [[0, 0, 0, .9], [.9, -.1, .1, .7], [-.9, -.1, 0, .75], [.4, .45, -.1, .7], [-.4, .4, .1, .65], [1.6, -.25, 0, .5], [-1.6, -.25, 0, .5]].forEach(([x, y, z, r]) => { const b = M(new THREE.SphereGeometry(r, 32, 24), m); b.position.set(x, y, z); g.add(b); });
    return g; }
  function qmark(s, x, y, sc = 1) { const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); q.position.set(x, y, .5); q.scale.setScalar(sc); s.add(q);
    const qa = M(new THREE.TorusGeometry(.42, .1, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.12, 12, 8), qm); qd.position.set(-.08, -.72, 0); q.add(qd); return q; }

  const S0b = 2.32, S1 = 5.36, S1b = 7.6, S2 = 9.92, S3 = 13.44, S4 = 18.24, S5 = 20.48, S6 = 24.24, S7 = 27.28, S7b = 29.84, S8 = 32.08;

  // 1) Okyanus tuzu karaya yayılsa: 166 m tuz katmanı = 40 katlı bina
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const land = M(rb(5.8, .6, 3.4, .12), std(0x3a3226, { roughness: .9 })); land.position.set(0, 3.5, 0); s.add(land);
    const lay = M(rb(3.4, 1, 2.8, .08), salt()); s.add(lay);
    const sp = dust(260, [3.2, 1, 2.6], 0xffffff, .1, .9); s.add(sp);
    const wc = document.createElement('canvas'); wc.width = 64; wc.height = 512; { const g = wc.getContext('2d'); g.fillStyle = '#1a2230'; g.fillRect(0, 0, 64, 512);
      for (let r = 0; r < 40; r++) for (let c = 0; c < 4; c++) { g.fillStyle = r1() > .35 ? '#ffd88a' : '#2c3a50'; g.fillRect(4 + c * 15, 4 + r * 12.7, 10, 7); } }
    const wt = new THREE.CanvasTexture(wc); wt.colorSpace = THREE.SRGBColorSpace;
    const bh = 3.4; const bld = M(new THREE.BoxGeometry(.85, bh, .85), [std(0x1a2230), std(0x1a2230), std(0x2a3240), std(0x1a2230), new THREE.MeshStandardMaterial({ map: wt, emissiveMap: wt, emissive: 0xffffff, emissiveIntensity: .6 }), std(0x1a2230)]);
    bld.position.set(1.9, 3.8 + bh / 2, .6); s.add(bld);
    const ant = M(new THREE.CylinderGeometry(.03, .03, .5, 8), std(0x9aa4b0, { metalness: .8 })); ant.position.set(1.9, 3.8 + bh + .25, .6); s.add(ant);
    const line = M(new THREE.BoxGeometry(5.0, .03, .03), glow(0xffcf2e, .9)); line.position.set(.0, 3.8 + bh, 1.7); s.add(line);
    return t => {
      E.d.rotation.y = t * .02; const k = ease(prog(t, S0b - .3, 2.4)); const h = Math.max(.02, bh * k);
      lay.scale.y = h; lay.position.set(-.7, 3.8 + h / 2, 0); sp.position.set(-.7, 3.8 + h, 0); sp.scale.y = .2; sp.visible = k > .02;
      line.visible = t > S0b; line.material.opacity = .9 * prog(t, S0b + 2.0, .4);
      bld.scale.y = Math.max(.01, back(prog(t, .2, .7))); bld.position.y = 3.8 + bh * bld.scale.y / 2;
      cam.position.set(Math.sin(t * .2) * 1.2, 7.2, 17); cam.lookAt(0, 5.3, 0); };
  } });
  // 2) Tuz nereden geldi? Karadaki kayalar (içinde parıldayan mineraller)
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffb04a });
    const R = new THREE.Group(); R.position.set(0, 5.2, 0); s.add(R);
    [[0, 0, 0, 1.7], [-1.9, -.6, .4, 1.0], [1.8, -.7, .3, 1.1], [.7, 1.2, -.6, .8]].forEach(([x, y, z, r], i) => { const k = rock(r, i % 2 ? 0x5a4e44 : 0x6b5e52); k.position.set(x, y, z); R.add(k); });
    const gems = Array.from({ length: 22 }, () => { const g = M(rb(.2, .2, .2, .03), salt()); const v = V(r1() - .5, r1() - .5, r1() * .5 + .5).normalize().multiplyScalar(1.75); g.position.copy(v); g.userData.ph = r1() * 6; R.add(g); return g; });
    const q = qmark(s, 2.3, 7.6, .9);
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02; R.rotation.y = Math.sin(t * .35) * .5; R.scale.setScalar(lerp(.85, 1, easeOut(prog(a, 0, .8))));
      gems.forEach(g => { g.rotation.set(t + g.userData.ph, t * .7, 0); g.material.emissiveIntensity = .4 + .6 * Math.max(0, Math.sin(t * 3 + g.userData.ph)) * prog(a, S1b - S1, .5); });
      q.visible = a < S1b - S1 && a > .2; q.rotation.y = Math.sin(t * 2) * .4;
      cam.position.set(0, 6.2, lerp(15.5, 13.5, ease(prog(a, 0, 4.5)))); cam.lookAt(0, 5.4, 0); };
  } });
  // 3) Yağmur, havadaki CO2 ile birleşip hafif asidik olur
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0c1424', '#020408'], rim: 0x7ee0ff });
    const C = cloud(); C.position.set(0, 7.2, -.5); C.scale.setScalar(1.1); s.add(C);
    const D = drops(s, 70, -2.2, 2.2, 6.5, 3.4);
    const co2 = Array.from({ length: 9 }, () => { const g = new THREE.Group(); const c = M(new THREE.SphereGeometry(.14, 24, 16), std(0x2a2a2e, { metalness: .3, roughness: .4 })); g.add(c);
      [-1, 1].forEach(k => { const o = M(new THREE.SphereGeometry(.12, 24, 16), std(0xff4a3a, { roughness: .4 })); o.position.x = k * .26; g.add(o); });
      g.userData = { x0: (r1() < .5 ? -1 : 1) * (2.4 + r1() * .8), y0: 4.4 + r1() * 2.2, x1: (r1() - .5) * 2.4, ph: r1() }; s.add(g); return g; });
    const water = new THREE.Color(0x8fd0ff), acid = new THREE.Color(0xc8ff6a);
    return t => {
      const a = t - S2; E.d.rotation.y = t * .02; C.position.x = Math.sin(t * .3) * .2; D.up(t, prog(a, 0, .8));
      co2.forEach(g => { const U = g.userData; const k = ease(prog(a, .5 + U.ph * .8, 1.4)); g.position.set(lerp(U.x0, U.x1, k), U.y0 - k * .4, .4); g.rotation.set(t, t * 1.3, 0);
        g.scale.setScalar(Math.max(.01, 1 - prog(a, 2.0 + U.ph * .8, .4))); });
      D.m.color.copy(water).lerp(acid, prog(a, 2.2, .8) * .7);
      cam.position.set(Math.sin(a * .2) * 1, 6.0, 14); cam.lookAt(0, 5.6, 0); };
  } });
  // 4) Yağmur kayayı milyonlarca yıl aşındırır, mineraller çözülüp akar
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffb04a });
    const gr = M(new THREE.CylinderGeometry(12, 12, .6, 64), std(0x2a241e, { roughness: .95 })); gr.position.y = 3.2; s.add(gr);
    const K = rock(1.5); K.position.set(0, 4.7, 0); s.add(K);
    const C = cloud(); C.position.set(0, 7.45, -1); C.scale.setScalar(.75); s.add(C);
    const D = drops(s, 50, -1.6, 1.6, 6.9, 4.0, 1.2);
    const cols = [0xffffff, 0xffc8d8, 0xbfe4ff, 0xfff0b0];
    const min = Array.from({ length: 60 }, (_, i) => { const m = M(rb(.13, .13, .13, .02), std(cols[i % 4], { emissive: cols[i % 4], emissiveIntensity: .4, roughness: .3 }));
      const an = r1() * Math.PI * 2; m.userData = { an, y: .2 + r1() * 1.2, ph: r1() }; s.add(m); return m; });
    const yrs = dust(1, [0, 0, 0]); void yrs;
    return t => {
      const a = t - S3; E.d.rotation.y = t * .02; D.up(t, 1); const er = prog(a, 0, 4.8);
      K.scale.set(1 - er * .25, 1 - er * .35, 1 - er * .25); K.position.y = 4.7 - er * .5; K.rotation.y = t * .1;
      min.forEach(m => { const U = m.userData; const c = ((a * .35 + U.ph) % 1); const r = 1.5 * (1 - er * .25) + c * 2.6;
        m.position.set(Math.cos(U.an) * r, Math.max(3.6, 4.9 + U.y - c * 4), Math.sin(U.an) * r * .5 + .6); m.rotation.set(t * 2 + U.ph, t, 0); m.visible = a > .4; });
      cam.position.set(Math.sin(a * .25) * 2, 6.6, 14.5); cam.lookAt(0, 5.3, 0); };
  } });
  // 5) Nehirler mineralleri okyanusa taşır
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a1630', '#02050c'], rim: 0x3fe0ff });
    const tg = new THREE.PlaneGeometry(16, 16, 96, 96); tg.rotateX(-Math.PI / 2); const P = tg.attributes.position; const cc = [];
    const path = new THREE.CatmullRomCurve3([V(-4, 0, -7), V(-2, 0, -4), V(.5, 0, -2.5), V(-.5, 0, 0), V(1.5, 0, 2), V(4, 0, 3.2)]);
    const pts = path.getSpacedPoints(100);
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), z = P.getZ(i); let dm = 99; pts.forEach(p => dm = Math.min(dm, Math.hypot(p.x - x, p.z - z)));
      const sea = x > 3.2 ? 1 : 0; const h = sea ? -.5 : (.9 * hash(x * .4, 0, z * .4) + .8) * clamp((dm - .35) / 1.6) - .15; P.setY(i, h);
      const c = sea ? new THREE.Color(0x0b3a6a) : new THREE.Color(0x2f4a2a).lerp(new THREE.Color(0x6b5a44), clamp(h)); cc.push(c.r, c.g, c.b); }
    tg.setAttribute('color', new THREE.Float32BufferAttribute(cc, 3)); tg.computeVertexNormals();
    const T = M(tg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .85 })); T.position.y = 3.6; s.add(T);
    const sea = M(new THREE.PlaneGeometry(10, 16), std(0x0e5a9a, { metalness: .5, roughness: .2, transparent: true, opacity: .9 })); sea.rotation.x = -Math.PI / 2; sea.position.set(8.2, 3.3, 0); s.add(sea);
    const rv = M(new THREE.TubeGeometry(path, 160, .22, 12), std(0x2a8ad8, { metalness: .4, roughness: .15, emissive: 0x0a2a50 })); rv.scale.y = .25; rv.position.y = 3.5; s.add(rv);
    const fl = Array.from({ length: 40 }, (_, i) => { const m = M(rb(.1, .1, .1, .02), std(i % 3 ? 0xffffff : 0xffc8d8, { emissive: 0xffffff, emissiveIntensity: .5 })); m.userData.ph = i / 40; s.add(m); return m; });
    return t => {
      const a = t - S4; E.d.rotation.y = t * .02;
      fl.forEach(m => { const u = (a * .3 + m.userData.ph) % 1; const p = path.getPoint(u); m.position.set(p.x, 3.62, p.z); m.rotation.set(t * 2, t, 0); m.visible = a > .1; });
      cam.position.set(lerp(-1.5, 0, ease(prog(a, 0, 2.3))), 11, 11); cam.lookAt(.3, 3.8, 0); };
  } });
  // 6) Okyanus tabanı: sıcak su bacaları ve volkanlar mineral ekler
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#06223e', '#000208'], fog: 0x031428, near: 12, far: 60, rim: 0xff7a2a, dust: 0x8fd0ff, hemi: .6 });
    const fg = new THREE.PlaneGeometry(40, 30, 80, 60); fg.rotateX(-Math.PI / 2); const FP = fg.attributes.position;
    for (let i = 0; i < FP.count; i++) FP.setY(i, .35 * hash(FP.getX(i) * .5, 0, FP.getZ(i) * .5)); fg.computeVertexNormals();
    const fl = M(fg, std(0x2a2620, { roughness: .95 })); fl.position.y = 3.2; s.add(fl);
    const vents = [[-1.8, 2.4, 0], [.3, 3.4, -1], [2.0, 2.0, .4]].map(([x, h, z]) => {
      const g = new THREE.CylinderGeometry(.22, .55, h, 32, 24); const P = g.attributes.position;
      for (let i = 0; i < P.count; i++) { const n = 1 + .25 * hash(P.getX(i) * 4, P.getY(i) * 3, P.getZ(i) * 4); P.setX(i, P.getX(i) * n); P.setZ(i, P.getZ(i) * n); } g.computeVertexNormals();
      const c = M(g, std(0x3a2e26, { roughness: .9 })); c.position.set(x, 3.3 + h / 2, z); s.add(c);
      const mouth = V(x, 3.3 + h, z); const gl = new THREE.PointLight(0xff8a3a, 60, 5); gl.position.copy(mouth); s.add(gl);
      const smoke = Array.from({ length: 34 }, () => { const b = M(new THREE.SphereGeometry(.16, 12, 8), new THREE.MeshStandardMaterial({ color: 0x4a4038, roughness: 1, transparent: true, opacity: .85, depthWrite: false }));
        b.userData = { ph: r1(), dx: (r1() - .5) * .8, dz: (r1() - .5) * .8 }; s.add(b); return b; });
      return { mouth, smoke }; });
    const vol = M(new THREE.ConeGeometry(3.5, 3, 64, 1, true), std(0x2a2420, { roughness: .9 })); vol.position.set(-4.5, 4.5, -12); s.add(vol);
    const lava = M(new THREE.SphereGeometry(.6, 24, 16), glow(0xff5a1a, .9)); lava.position.set(-4.5, 6.0, -12); s.add(lava);
    const sparks = dust(200, [6, 4, 3], 0xffe0a0, .1, .7); sparks.position.set(0, 6, 0); s.add(sparks);
    return t => {
      const a = t - S5; E.d.rotation.y = t * .02; sparks.rotation.y = t * .1; lava.scale.setScalar(1 + .15 * Math.sin(t * 4));
      vents.forEach(v => v.smoke.forEach(b => { const U = b.userData; const c = (t * .35 + U.ph) % 1; b.position.set(v.mouth.x + U.dx * c * 1.6, v.mouth.y + c * 2.8, v.mouth.z + U.dz * c);
        b.scale.setScalar(.5 + c * 2.2); b.material.opacity = .8 * (1 - c); }));
      cam.position.set(Math.sin(a * .25) * 1.5, 6.2, lerp(14.5, 13, ease(prog(a, 0, 3.7)))); cam.lookAt(0, 5.4, 0); };
  } });
  // 7) Su buharlaşır, tuz geride kalıp birikir
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffb04a });
    const sun = M(new THREE.SphereGeometry(.6, 40, 24), new THREE.MeshBasicMaterial({ color: 0xffe8a0, fog: false })); sun.position.set(-2.6, 6.4, -3); s.add(sun);
    const halo = dust(160, [2.4, 2.4, 1], 0xffd070, .8, .45); halo.position.copy(sun.position); s.add(halo);
    const tank = M(rb(5, 2.8, 2.6, .12), new THREE.MeshStandardMaterial({ color: 0xcfe8ff, transparent: true, opacity: .14, roughness: .05, metalness: .2, depthWrite: false })); tank.position.set(0, 4.9, 0); s.add(tank);
    const wat = M(rb(4.8, 1, 2.4, .08), new THREE.MeshStandardMaterial({ color: 0x1a7ad0, transparent: true, opacity: .75, roughness: .1, metalness: .3, emissive: 0x062040 })); s.add(wat);
    const vap = Array.from({ length: 50 }, () => { const b = M(new THREE.SphereGeometry(.09, 12, 8), glow(0xdff2ff, .7)); b.userData = { x: (r1() - .5) * 4.4, z: (r1() - .5) * 2, ph: r1() }; s.add(b); return b; });
    const cr = Array.from({ length: 30 }, (_, i) => { const c = M(rb(.26, .26, .26, .03), salt()); c.userData = { x: -2.1 + (i % 10) * .47 + (r1() - .5) * .1, z: -.8 + Math.floor(i / 10) * .6, ph: r1() }; s.add(c); return c; });
    return t => {
      const a = t - S6; E.d.rotation.y = t * .02; halo.rotation.z = t * .2;
      const lv = lerp(2.3, 1.2, ease(prog(a, .2, 2.6))); wat.scale.y = lv; wat.position.y = 3.62 + lv / 2;
      vap.forEach(b => { const U = b.userData; const c = (t * .45 + U.ph) % 1; b.position.set(U.x + Math.sin(t + U.ph * 6) * .2, 3.62 + lv + c * 2.6, U.z); b.scale.setScalar(1 + c); b.material.opacity = .7 * (1 - c); });
      cr.forEach((c, i) => { const k = back(prog(a, .6 + c.userData.ph * 1.6, .4)); c.scale.setScalar(Math.max(.01, k)); c.position.set(c.userData.x, 3.78, c.userData.z); c.rotation.y = c.userData.ph * 3; });
      cam.position.set(Math.sin(a * .25) * 1.2, 7.0, 13.5); cam.lookAt(0, 5.2, 0); };
  } });
  // 8) Deniz suyunun %3,5'i tuz: 100 küpten 3,5'i tuz
  shots.push({ t0: S7, t1: S7b, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x3fe0ff });
    const G = new THREE.Group(); G.position.set(0, 4.85, 0); G.scale.setScalar(.86); s.add(G);
    const cubes = []; for (let i = 0; i < 100; i++) { const r = Math.floor(i / 10), c = i % 10; const sl = i >= 96;
      const m = sl ? salt() : new THREE.MeshStandardMaterial({ color: 0x1a7ad0, roughness: .15, metalness: .3, transparent: true, opacity: .8, emissive: 0x062040 });
      const k = M(rb(.36, .36, .36, .05), m); k.position.set(-2.025 + c * .45, 2.025 - r * .45, 0); if (i === 96) k.userData.half = true; k.userData.i = i; G.add(k); cubes.push(k); }
    return t => {
      const a = t - S7; E.d.rotation.y = t * .02; G.rotation.y = Math.sin(t * .5) * .3; G.rotation.x = -.15;
      cubes.forEach(k => { const i = k.userData.i; const sc = back(prog(a, .05 + i * .007, .35)); k.scale.set(sc, k.userData.half ? Math.max(.01, sc * .5) : sc, sc);
        if (k.userData.half) k.position.y = 2.025 - 9 * .45 - .09;
        if (i >= 96) { k.position.z = .5 * ease(prog(a, 1.4, .5)); k.material.emissiveIntensity = .5 + .6 * prog(a, 1.4, .5); } });
      cam.position.set(0, 5.8, 13.5); cam.lookAt(0, 5.5, 0); };
  } });
  // 9) Sodyum ve klorür: tuz kristali kafesi
  shots.push({ t0: S7b, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x4ade80 });
    const G = new THREE.Group(); G.position.set(0, 5.5, 0); s.add(G);
    const na = std(0x9a6bff, { roughness: .25, metalness: .2, emissive: 0x2a1060 }), cl = std(0x4ade80, { roughness: .25, metalness: .2, emissive: 0x0a3a1a });
    const bond = std(0xcfd8e2, { metalness: .6, roughness: .3 }); const atoms = [];
    for (let x = -1; x <= 1; x++) for (let y = -1; y <= 1; y++) for (let z = -1; z <= 1; z++) { const isNa = (x + y + z + 3) % 2 === 0;
      const a = M(new THREE.SphereGeometry(isNa ? .22 : .34, 32, 24), isNa ? na : cl); a.position.set(x * .8, y * .8, z * .8); a.userData.d = Math.hypot(x, y, z); G.add(a); atoms.push(a); }
    for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) [0, 1, 2].forEach(ax => { const b = M(new THREE.CylinderGeometry(.04, .04, 1.6, 8), bond);
      if (ax === 0) { b.rotation.z = Math.PI / 2; b.position.set(0, i * .8, j * .8); } else if (ax === 1) b.position.set(i * .8, 0, j * .8); else { b.rotation.x = Math.PI / 2; b.position.set(i * .8, j * .8, 0); } G.add(b); });
    return t => {
      const a = t - S7b; E.d.rotation.y = t * .02; G.rotation.set(t * .3, t * .45, 0);
      atoms.forEach(at => at.scale.setScalar(Math.max(.01, back(prog(a, .05 + at.userData.d * .25, .45)))));
      G.scale.setScalar(lerp(1.1, 1.35, ease(prog(a, 0, 2.2))));
      cam.position.set(0, 5.8, 13); cam.lookAt(0, 5.5, 0); };
  } });
  // 10) Sıradaki soru: kediler neden hep ayaklarının üstüne düşer? — havada dönerek doğrulan kedi
  shots.push({ t0: S8, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#141032', '#020308'], rim: 0xffb04a });
    const cat = new THREE.Group(); s.add(cat); const fur = std(0xf0a040, { roughness: .6 }), wh = std(0xfff4e6, { roughness: .6 });
    const body = M(new THREE.CapsuleGeometry(.42, 1.2, 12, 24), fur); body.rotation.z = Math.PI / 2; cat.add(body);
    const belly = M(new THREE.CapsuleGeometry(.3, .9, 10, 20), wh); belly.rotation.z = Math.PI / 2; belly.position.y = -.16; belly.scale.z = .9; cat.add(belly);
    const head = new THREE.Group(); head.position.set(1.05, .22, 0); cat.add(head);
    head.add(M(new THREE.SphereGeometry(.42, 40, 28), fur));
    [-1, 1].forEach(k => { const e = M(new THREE.ConeGeometry(.15, .32, 24), fur); e.position.set(.02, .4, k * .22); e.rotation.x = k * -.25; head.add(e);
      const ey = M(new THREE.SphereGeometry(.08, 16, 12), new THREE.MeshBasicMaterial({ color: 0x9cff5a })); ey.position.set(.36, .08, k * .15); head.add(ey);
      const pu = M(new THREE.SphereGeometry(.04, 12, 8), new THREE.MeshBasicMaterial({ color: 0x050505 })); pu.position.set(.43, .08, k * .15); head.add(pu); });
    const nose = M(new THREE.SphereGeometry(.05, 12, 8), std(0xff7a9a)); nose.position.set(.42, -.04, 0); head.add(nose);
    const legs = [[-.55, .2], [-.55, -.2], [.55, .2], [.55, -.2]].map(([x, z]) => { const l = new THREE.Group(); l.position.set(x, -.25, z); cat.add(l);
      const m = M(new THREE.CapsuleGeometry(.11, .45, 8, 16), fur); m.position.y = -.3; l.add(m); const p = M(new THREE.SphereGeometry(.13, 16, 12), wh); p.position.y = -.58; l.add(p); return l; });
    const tc = new THREE.CatmullRomCurve3([V(-.9, 0, 0), V(-1.4, .3, 0), V(-1.6, .9, .1), V(-1.4, 1.3, .2)]);
    cat.add(M(new THREE.TubeGeometry(tc, 40, .08, 12), fur));
    const streaks = Array.from({ length: 14 }, () => { const m = M(new THREE.CylinderGeometry(.015, .015, 1.2, 6), glow(0xffffff, .35)); m.userData = { x: (r1() - .5) * 3, z: (r1() - .5) * 2, ph: r1() }; s.add(m); return m; });
    const q = qmark(s, 2.3, 7.7, .85);
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02;
      const cyc = (a % 2.6) / 2.6; const k = ease(prog(cyc, .15, .45));
      cat.position.set(-.2, 6.3 + Math.sin(t * 1.2) * .12, 0); cat.rotation.set(Math.PI * (1 - k), -.5 + Math.sin(t * .4) * .2, .1);
      head.rotation.x = -Math.PI * (1 - ease(prog(cyc, .1, .25))) * .4;
      legs.forEach((l, i) => l.rotation.z = (1 - k) * (i < 2 ? .6 : -.6) + Math.sin(t * 4 + i) * .08);
      streaks.forEach(m => { const c = (t * 1.2 + m.userData.ph) % 1; m.position.set(m.userData.x, 4.4 + c * 4, m.userData.z); m.material.opacity = .3 * Math.sin(c * Math.PI); });
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * 1.2, 6.4, 13.5); cam.lookAt(0, 6.1, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S0b, html: T('BİR SORU', 'OKYANUSLAR NEDEN<br><span class="y">TUZLU?</span>', 98) },
    { t0: S0b, t1: S1, html: BIG('TUZU KARAYA YAYSAK', 'k166', '40 KATLI BİNA YÜKSEKLİĞİ', '166<small>M</small>') },
    { t0: S1, t1: S1b, html: T('PEKİ', 'BU TUZ<br><span class="y">NEREDEN</span> GELDİ?', 104) },
    { t0: S1b, t1: S2, html: T('CEVAP', 'KARADAKİ<br><span class="y">KAYALARDAN</span>', 104) },
    { t0: S2, t1: S3, html: T('YAĞMUR + KARBONDİOKSİT', 'HAFİF <span class="y">ASİDİK</span><br>OLUR', 104) },
    { t0: S3, t1: S4, html: T('MİLYONLARCA YIL', 'KAYALAR <span class="y">AŞINIR</span><br>MİNERAL ÇÖZÜLÜR', 92) },
    { t0: S4, t1: S5, html: T('NEHİRLER', 'MİNERALLERİ<br><span class="y">OKYANUSA</span> TAŞIR', 96) },
    { t0: S5, t1: S6, html: T('OKYANUS TABANI', 'SICAK SU <span class="y">BACALARI</span><br>VE VOLKANLAR', 92) },
    { t0: S6, t1: S7, html: T('SU BUHARLAŞIR', 'TUZ <span class="y">GERİDE</span><br>KALIR', 108) },
    { t0: S7, t1: S7b, html: BIG('DENİZ SUYUNUN', 'k35', 'TUZDUR', '%3,5') },
    { t0: S7b, t1: S8, html: T('EN ÇOK', 'SODYUM VE<br><span class="y">KLORÜR</span>', 108) },
    { t0: S8, t1: 99, html: T('SIRADAKİ SORU', 'KEDİLER NEDEN HEP<br><span class="y">AYAKLARININ</span><br>ÜSTÜNE DÜŞER?', 84) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k166', S0b], ['k35', S7]];
  return {
    END: 37.64, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; }); },
    follow: { t: 35.88, click: 36.74 },
    sfx: [[.3, 'whoosh', .5], [S0b, 'boom', .5], [S0b + .3, 'crunch', .5], [S1 + .3, 'pop', .4], [S1b, 'ding', .5], [S2 + .3, 'whoosh', .4], [S2 + 2.2, 'ding', .3],
      [S3 + .5, 'crunch', .6], [S3 + 2.5, 'crunch', .4], [S4 + .2, 'whoosh', .5], [S5 + .3, 'boom', .5], [S6 + .3, 'whoosh', .4], [S6 + 1.2, 'pop', .4], [S6 + 1.8, 'pop', .4],
      [S7 + .3, 'click', .4], [S7 + 1.4, 'ding', .5], [S7b + .3, 'pop', .5], [S7b + .6, 'pop', .4], [S8 + .4, 'whoosh', .5]],
  };
};
