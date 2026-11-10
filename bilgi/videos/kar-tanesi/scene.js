// Bilgi #8: Kar taneleri neden hep 6 köşeli? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Science News Explores "Explainer: The making of a snowflake" (V şekilli su molekülü, zıt yükler altıgen dizilim kurar,
// tipik kar tanesinde ~10^18 su molekülü); PBS NewsHour "The science of snowflakes" — K. Libbrecht (Caltech): "underlying
// [hexagonal lattice] structure is how the crystal gets its sixfold symmetry", nem arttıkça daha dallı yapılar;
// H–O–H bağ açısı 104,5°; Libbrecht: köşeler nemli havaya daha çok çıkıntı yapar, daha hızlı büyür (dallanma).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 83; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  function dust(n, sp, color = 0xcfe8ff, size = .25, op = .5) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
    for (let i = 0; i < n * 3; i += 3) { p[i] = (r1() - .5) * sp[0]; p[i + 1] = (r1() - .5) * sp[1]; p[i + 2] = (r1() - .5) * sp[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color, size, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending }));
  }
  function lights(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#12305a', '#02060e'])); s.fog = new THREE.Fog(o.fog || 0x050d1c, o.near || 40, o.far || 140);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x0a0a12, o.hemi || .9));
    const key = new THREE.SpotLight(0xfff1dc, o.key || 2200, 160, .45, .55, 1.2); key.position.set(-18, 44, 34); s.add(key); s.add(key.target);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 700, 90); rim.position.set(20, 16, -14); s.add(rim);
    return key;
  }
  const ice = (op = .92) => new THREE.MeshStandardMaterial({ color: 0xd6f2ff, emissive: 0x2a5a8a, emissiveIntensity: .55, roughness: .12, metalness: .2, transparent: true, opacity: op });
  // büyüyebilen kar tanesi: grow(k) 0..1
  function makeFlake(r, o = {}) {
    const g = new THREE.Group(); const m = o.mat || ice(); const w = o.w || .16;
    const core = M(new THREE.CylinderGeometry(r * (o.core || .2), r * (o.core || .2), .12, 6), m); core.rotation.x = Math.PI / 2; core.rotation.y = Math.PI / 2; g.add(core);
    const arms = [];
    for (let i = 0; i < 6; i++) { const a = new THREE.Group(); a.rotation.z = i * Math.PI / 3; g.add(a);
      const bar = M(rb(1, w, .1, .03), m); a.add(bar); const brs = [];
      for (const [p, l] of (o.br || [[.4, .32], [.62, .26], [.82, .16]])) for (const k of [-1, 1]) { const b = new THREE.Group(); b.position.x = r * p; b.rotation.z = k * Math.PI / 3; a.add(b);
        const bm = M(rb(r * l, w * .8, .08, .03), m); bm.position.x = r * l / 2; b.add(bm); brs.push([b, p]); }
      let tip = null; if (o.tip) { tip = M(new THREE.CylinderGeometry(r * o.tip, r * o.tip, .1, 6), m); tip.rotation.x = Math.PI / 2; tip.rotation.y = Math.PI / 2; a.add(tip); }
      arms.push({ bar, brs, tip }); }
    g.userData.grow = k => arms.forEach(({ bar, brs, tip }) => {
      const len = Math.max(.001, r * k); bar.scale.x = len; bar.position.x = len / 2;
      brs.forEach(([b, p]) => { const s = clamp((k - p) / .25); b.scale.setScalar(Math.max(.001, s)); b.visible = s > 0; });
      if (tip) { tip.position.x = len; const s = clamp((k - .7) / .3); tip.scale.setScalar(Math.max(.001, s)); }
    });
    g.userData.grow(1); return g;
  }
  const variants = [
    { br: [[.4, .32], [.62, .26], [.82, .16]] },
    { br: [[.55, .2]], tip: .2, core: .32, w: .3 },
    { br: [[.25, .14], [.4, .2], [.55, .2], [.7, .16], [.85, .1]], w: .12 },
    { br: [], core: .55, tip: .12, w: .34 },
    { br: [[.35, .4], [.7, .22]], tip: .1 },
  ];
  // su molekülü (V): O altta, iki H yukarıda, 104,5°
  function water(sc = 1) {
    const g = new THREE.Group(); const O = M(new THREE.SphereGeometry(.85 * sc, 40, 28), std(0xe23b3b, { roughness: .3, metalness: .1 })); g.add(O);
    const hm = std(0xf4f6fa, { roughness: .3 }); const bm = std(0xcfd6e0, { roughness: .4, metalness: .3 });
    const a = 104.5 / 2 * Math.PI / 180; const hs = [];
    for (const k of [-1, 1]) { const d = new THREE.Vector3(k * Math.sin(a), Math.cos(a), 0); const H = M(new THREE.SphereGeometry(.55 * sc, 32, 24), hm); H.position.copy(d.clone().multiplyScalar(1.45 * sc)); g.add(H); hs.push(H);
      const b = M(new THREE.CylinderGeometry(.16 * sc, .16 * sc, 1.45 * sc, 16), bm); b.position.copy(d.clone().multiplyScalar(.72 * sc)); b.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d); g.add(b); }
    g.userData.hs = hs; return g;
  }
  function hexRing(R = 3) { // 6 molekül + hidrojen bağları
    const g = new THREE.Group(); const mols = []; const bonds = [];
    const bm = new THREE.MeshBasicMaterial({ color: 0x7ee0ff, transparent: true, opacity: .9 });
    for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3 + Math.PI / 6; const w = water(.55); w.position.set(Math.cos(a) * R, Math.sin(a) * R, 0); w.rotation.z = a - Math.PI / 2 - .6; g.add(w); mols.push(w);
      const a2 = a + Math.PI / 3; const p1 = new THREE.Vector3(Math.cos(a) * R, Math.sin(a) * R, 0), p2 = new THREE.Vector3(Math.cos(a2) * R, Math.sin(a2) * R, 0);
      const seg = new THREE.Group(); for (let j = 1; j < 6; j++) { const d = M(new THREE.SphereGeometry(.09, 10, 8), bm); d.position.lerpVectors(p1, p2, j / 6); seg.add(d); } g.add(seg); bonds.push(seg); }
    g.userData = { mols, bonds, R }; return g;
  }
  function vapor(n, R) { const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3); const seeds = [];
    for (let i = 0; i < n; i++) seeds.push([r1() * Math.PI * 2, R * (.6 + r1() * .8), (r1() - .5) * 2, r1()]);
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    const pts = new THREE.Points(g, new THREE.PointsMaterial({ color: 0xbfe8ff, size: .14, transparent: true, opacity: .75, depthWrite: false, blending: THREE.AdditiveBlending }));
    pts.userData.upd = (t, tipR) => { for (let i = 0; i < n; i++) { const [a, r, z, o] = seeds[i]; const f = (o + t * .35) % 1; const ca = Math.round((a - Math.PI / 6) / (Math.PI / 3)) * Math.PI / 3; // en yakın köşe
        const sx = Math.cos(a) * r, sy = Math.sin(a) * r, ex = Math.cos(ca) * tipR, ey = Math.sin(ca) * tipR; p[i * 3] = lerp(sx, ex, f); p[i * 3 + 1] = lerp(sy, ey, f); p[i * 3 + 2] = z * (1 - f); }
      g.attributes.position.needsUpdate = true; };
    return pts; }

  const S1 = 5.6, S2 = 7.85, S3 = 11.85, S4 = 16.9, S4b = 18.7, S5 = 22.1, S6 = 28.58, S7 = 31.85, S7b = 35.4, S8 = 39.46;

  // 1) Kar yağan gece, ortada dönen büyük kar tanesi
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#14345f', '#02060e'], rim: 0x9fe6ff, key: 1600 });
    const F = makeFlake(3.4); F.position.set(0, 5.2, 0); s.add(F);
    const small = []; for (let i = 0; i < 30; i++) { const f = makeFlake(.4 + r1() * .5, variants[i % 5]); f.userData.u = { x: (r1() - .5) * 28, z: -3 - r1() * 18, o: r1() * 30, r: r1() * 6 }; s.add(f); small.push(f); }
    const glow = new THREE.PointLight(0x9fe6ff, 300, 20); glow.position.set(0, 5.2, 4); s.add(glow);
    const d = dust(500, [40, 40, 30], 0xffffff, .12, .6); s.add(d);
    return t => {
      F.userData.grow(easeOut(prog(t, 0, 1.6))); F.rotation.set(Math.sin(t * .7) * .3, Math.sin(t * .5) * .45, t * .2);
      small.forEach(f => { const u = f.userData.u; f.position.set(u.x + Math.sin(t + u.r) * .6, 22 - ((u.o + t * 2.2) % 30), u.z); f.rotation.set(t * .5 + u.r, t * .7, u.r); });
      d.position.y = -((t * 1.5) % 10);
      cam.position.set(0, 5.6, lerp(26, 22, ease(prog(t, 0, S1)))); cam.lookAt(0, 6.2, 0); };
  } });
  // 2) Kar tanesinden su molekülüne zoom
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#0f2a52', '#02060e'], rim: 0xff6a5a });
    const F = makeFlake(3.4); F.position.set(0, 5.2, -6); s.add(F);
    const W = water(1.4); W.position.set(0, 4.6, 0); s.add(W);
    const d = dust(500, [30, 30, 30], 0x9fc4ff, .12, .5); d.position.y = 5; s.add(d);
    return t => {
      const k = ease(prog(t, S1, 1.4)); F.rotation.z = t * .2; F.scale.setScalar(lerp(1, 4, k)); F.children.forEach(c => c.traverse?.(m => { if (m.material) m.material.opacity = .92 * (1 - k * .8); }));
      W.scale.setScalar(Math.max(.01, back(prog(t, S1 + .5, .7)))); W.rotation.set(.2, Math.sin(t * .9) * .6, 0);
      d.rotation.y = t * .05;
      cam.position.set(0, 5.4, lerp(22, 14, k)); cam.lookAt(0, 5.5, 0); };
  } });
  // 3) V şekli: 104,5°
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#0f2a52', '#02060e'], rim: 0xff6a5a });
    const W = water(1.6); W.position.set(0, 4.2, 0); s.add(W);
    const a = 104.5 / 2 * Math.PI / 180;
    const arc = M(new THREE.TorusGeometry(2.0, .09, 10, 48, 104.5 * Math.PI / 180), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); arc.rotation.z = Math.PI / 2 - a; W.add(arc); arc.position.z = 1.0;
    const d = dust(400, [30, 30, 30], 0x9fc4ff, .12, .5); d.position.y = 5; s.add(d);
    return t => {
      const k = easeOut(prog(t, 9.2, .8)); arc.scale.setScalar(Math.max(.01, k)); arc.visible = k > 0;
      W.rotation.set(Math.sin(t * .6) * .15, Math.sin(t * .5) * .35, 0); d.rotation.y = t * .05;
      cam.position.set(Math.sin(t * .2) * 2, 5.6, 19); cam.lookAt(0, 6.0, 0); };
  } });
  // 4) Donarken: moleküller altıgen halkada birleşir
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#10305a', '#02060e'], rim: 0x7ee0ff });
    const H = hexRing(3.2); H.position.set(0, 5.4, 0); s.add(H);
    const starts = H.userData.mols.map((m, i) => [m.position.clone(), new THREE.Vector3((r1() - .5) * 20, 5 + (r1() - .5) * 10, (r1() - .5) * 10), m.rotation.z]);
    const frost = dust(600, [30, 30, 20], 0xcfefff, .1, .5); frost.position.y = 5; s.add(frost);
    return t => {
      H.userData.mols.forEach((m, i) => { const [end, st, rz] = starts[i]; const k = ease(prog(t, S3 + .1 + i * .12, 1.6)); m.position.lerpVectors(st, end, k); m.rotation.z = rz + (1 - k) * 4; });
      H.userData.bonds.forEach((b, i) => { const k = prog(t, 13.4 + i * .15, .4); b.visible = k > 0; b.scale.setScalar(Math.max(.01, k)); });
      H.rotation.set(Math.sin(t * .4) * .25, Math.sin(t * .3) * .3, t * .08); frost.rotation.y = t * .04;
      cam.position.set(0, 5.4, 20); cam.lookAt(0, 6.1, 0); };
  } });
  // 5) Halkalar üst üste -> altıgen prizma
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#10305a', '#02060e'], rim: 0x7ee0ff });
    const lat = new THREE.Group(); lat.position.set(0, 5.4, 0); s.add(lat); const rings = [];
    const om = std(0xe23b3b, { roughness: .3 }), lm = new THREE.MeshBasicMaterial({ color: 0x7ee0ff, transparent: true, opacity: .8 });
    const cells = [[0, 0]]; for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; cells.push([Math.cos(a) * 1.73 * 1.1, Math.sin(a) * 1.73 * 1.1]); }
    for (let layer = 0; layer < 4; layer++) cells.forEach(([cx, cy], ci) => { const r = new THREE.Group(); for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3 + Math.PI / 6; const o = M(new THREE.SphereGeometry(.24, 16, 12), om); o.position.set(Math.cos(a) * 1.1, Math.sin(a) * 1.1, 0); r.add(o);
        const a2 = a + Math.PI / 3; const b = M(new THREE.CylinderGeometry(.04, .04, 1.1, 6), lm); b.position.set((Math.cos(a) + Math.cos(a2)) * .55, (Math.sin(a) + Math.sin(a2)) * .55, 0); b.rotation.z = a + Math.PI / 6; r.add(b); }
      r.position.set(cx, cy, (layer - 1.5) * 1.2); r.userData = { layer, ci }; lat.add(r); rings.push(r); });
    const prism = M(new THREE.CylinderGeometry(4.6, 4.6, 5.2, 6, 1), new THREE.MeshPhysicalMaterial({ color: 0xcfefff, roughness: .05, metalness: .1, transmission: .0, transparent: true, opacity: .55, emissive: 0x1a4a7a, emissiveIntensity: .5 }));
    prism.rotation.x = Math.PI / 2; prism.rotation.y = Math.PI / 6; lat.add(prism);
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(prism.geometry), new THREE.LineBasicMaterial({ color: 0xffffff })); prism.add(edges);
    return t => {
      rings.forEach(r => { const u = r.userData; const k = ease(prog(t, S4 + u.layer * .35 + u.ci * .05, .8)); r.scale.setScalar(Math.max(.01, k)); r.position.z = (u.layer - 1.5) * 1.2 + (1 - k) * 8; });
      const pk = ease(prog(t, S4b + .2, 1.2)); prism.visible = pk > 0; prism.scale.set(Math.max(.01, pk), Math.max(.01, pk), Math.max(.01, pk)); prism.material.opacity = .5 * pk;
      rings.forEach(r => r.children.forEach(c => { c.material.transparent = true; }));
      lat.rotation.set(-.3 + Math.sin(t * .3) * .1, Math.sin(t * .4) * .5, t * .05);
      cam.position.set(0, 5.6, 24); cam.lookAt(0, 6.3, 0); };
  } });
  // 6) Nemli bulut: köşeler hızlı büyür, altı kol uzar
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#16365f', '#02060e'], rim: 0x9fe6ff, key: 1700 });
    const plate = M(new THREE.CylinderGeometry(1.4, 1.4, .25, 6), ice()); plate.rotation.x = Math.PI / 2; plate.rotation.y = Math.PI / 2;
    const F = makeFlake(4.2, { br: [[.45, .3], [.68, .22], [.86, .12]], core: .33 }); const G = new THREE.Group(); G.position.set(0, 5.2, 0); s.add(G); G.add(F);
    const V = vapor(500, 7); G.add(V);
    const cloud = dust(800, [40, 30, 20], 0xdfefff, .35, .18); cloud.position.y = 5; s.add(cloud);
    return t => {
      const k = .05 + .95 * ease(prog(t, 25.0, 3.4)); F.userData.grow(k);
      V.userData.upd(t, 4.2 * k + .5);
      G.rotation.set(Math.sin(t * .4) * .25, Math.sin(t * .3) * .3, t * .1); cloud.rotation.y = t * .03;
      cam.position.set(0, 5.4, lerp(18, 23, ease(prog(t, S5, 6)))); cam.lookAt(0, 6.0, 0); };
  } });
  // 7) Aynı hava -> kollar birbirine benzer (senkron parlama)
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#16365f', '#02060e'], rim: 0xffcf2e, key: 1800 });
    const m = ice(); const F = makeFlake(4.2, { br: [[.45, .3], [.68, .22], [.86, .12]], core: .33, mat: m }); F.position.set(0, 5.2, 0); s.add(F);
    const ring = M(new THREE.TorusGeometry(4.4, .05, 8, 96), new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: .6 })); ring.position.set(0, 5.2, 0); s.add(ring);
    const d = dust(400, [30, 30, 20], 0xdfefff, .12, .5); d.position.y = 5; s.add(d);
    return t => {
      const p = (t - S6) % 1.1 / 1.1; ring.scale.setScalar(.2 + p * 1.0); ring.material.opacity = (1 - p) * .7;
      m.emissiveIntensity = .55 + .5 * Math.max(0, Math.sin((t - S6) * Math.PI / 1.1 * 2));
      F.rotation.set(Math.sin(t * .5) * .2, Math.sin(t * .4) * .25, t * .25); ring.rotation.copy(F.rotation); d.rotation.y = t * .04;
      cam.position.set(0, 5.4, 21); cam.lookAt(0, 6.0, 0); };
  } });
  // 8) 10^18 molekül: kar tanesinin içine dalış
  shots.push({ t0: S7, t1: S7b, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#0f2a52', '#02060e'], rim: 0x7ee0ff });
    const F = makeFlake(4.2, { core: .3 }); F.position.set(0, 5.2, 0); s.add(F);
    const mol = dust(6000, [9, 9, 1.2], 0xff7a6a, .07, .9); mol.position.set(0, 5.2, .2); s.add(mol);
    const mol2 = dust(4000, [9, 9, 1.2], 0xffffff, .05, .8); mol2.position.set(0, 5.2, .2); s.add(mol2);
    return t => {
      const k = ease(prog(t, S7, 3.4)); F.rotation.z = t * .1; mol.rotation.z = mol2.rotation.z = t * .1;
      mol.material.opacity = .9 * k; mol2.material.opacity = .8 * k;
      cam.position.set(0, lerp(5.4, 5.3, k), lerp(21, 13, k)); cam.lookAt(0, lerp(6.0, 5.5, k), 0); };
  } });
  // 9) Her biri farklı: dönen 5 farklı kar tanesi
  shots.push({ t0: S7b, t1: S8, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#14345f', '#02060e'], rim: 0x9fe6ff });
    const fl = variants.map((v, i) => { const f = makeFlake(1.6, v); s.add(f); return f; });
    const pos = [[-2.3, 7.4], [2.3, 7.4], [0, 5.2], [-2.3, 3.0], [2.3, 3.0]];
    const d = dust(500, [40, 40, 30], 0xffffff, .12, .6); s.add(d);
    return t => {
      fl.forEach((f, i) => { const k = back(prog(t, S7b + i * .15, .6)); f.scale.setScalar(Math.max(.01, k)); f.position.set(pos[i][0], pos[i][1], 0); f.rotation.set(Math.sin(t * .6 + i) * .3, Math.sin(t * .5 + i * 2) * .4, t * .3 * (i % 2 ? 1 : -1)); });
      d.position.y = -((t * 1.5) % 10);
      cam.position.set(0, 5.4, 22); cam.lookAt(0, 6.0, 0); };
  } });
  // 10) Sıradaki soru: patlayan volkan
  shots.push({ t0: S8, t1: 99, fov: 40, build: (s, cam) => {
    s.background = gradTex('#2a0e0a', '#030203'); s.fog = new THREE.Fog(0x120604, 40, 130);
    s.add(new THREE.HemisphereLight(0xffb08a, 0x0a0505, .5));
    const key = new THREE.SpotLight(0xfff1dc, 1400, 160, .5, .55, 1.2); key.position.set(-20, 40, 30); s.add(key);
    const g = new THREE.CylinderGeometry(2.2, 11, 9, 160, 40, true); const P = g.attributes.position;
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i); const k = (y + 4.5) / 9; let sc = 1 + .12 * hash(x * .5, y * .5, z * .5) * (1 - k);
      P.setX(i, x * sc); P.setZ(i, z * sc); }
    g.computeVertexNormals(); const vol = M(g, std(0x3a2a24, { roughness: .95, side: THREE.DoubleSide })); vol.position.set(0, 4.5, -2); s.add(vol);
    const ground = M(new THREE.CylinderGeometry(60, 60, 1, 64), std(0x231915, { roughness: 1 })); ground.position.y = -.5; s.add(ground);
    const glow = new THREE.PointLight(0xff5a1a, 900, 40); glow.position.set(0, 10.5, -2); s.add(glow);
    const crater = M(new THREE.CircleGeometry(2.3, 32), new THREE.MeshBasicMaterial({ color: 0xff7a1a })); crater.rotation.x = -Math.PI / 2; crater.position.set(0, 8.9, -2); s.add(crater);
    const lava = []; const lm = new THREE.MeshStandardMaterial({ color: 0xff7a1a, emissive: 0xff4a00, emissiveIntensity: 1.6 });
    for (let i = 0; i < 70; i++) { const b = M(new THREE.SphereGeometry(.18 + r1() * .25, 12, 8), lm); b.userData = { a: r1() * Math.PI * 2, v: 2 + r1() * 3.5, u: 6 + r1() * 5, o: r1() * 2.2 }; s.add(b); lava.push(b); }
    const smoke = dust(900, [10, 16, 10], 0x806a60, .5, .22); smoke.position.set(0, 18, -2); s.add(smoke);
    const streams = []; for (let i = 0; i < 4; i++) { const st = M(new THREE.CylinderGeometry(.3, .5, 5.5, 12), lm); const a = i * 1.6 + .4; st.position.set(Math.sin(a) * 3, 6, -2 + Math.cos(a) * 3); st.rotation.set(Math.cos(a) * .85, 0, -Math.sin(a) * .85); s.add(st); streams.push(st); }
    return t => {
      const a = t - S8; lava.forEach(b => { const u = b.userData; const tt = (a + u.o) % 2.2; b.position.set(Math.cos(u.a) * u.v * tt, 8.8 + u.u * tt - 6 * tt * tt, -2 + Math.sin(u.a) * u.v * tt); b.visible = b.position.y > 4; });
      glow.intensity = 900 + 300 * Math.sin(t * 13); smoke.position.y = 18 + (a * 1.2) % 4; smoke.rotation.y = t * .1;
      streams.forEach(st => st.visible = false);
      cam.position.set(Math.sin(a * .15) * 5, 17, 32); cam.lookAt(0, 8.6, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'KAR TANELERİ NEDEN<br>HEP <span class="y">6 KÖŞELİ?</span>', 92) },
    { t0: S1, t1: S2, html: T('SIRRI', 'SU <span class="y">MOLEKÜLÜ</span>') },
    { t0: S2, t1: S3, html: BIG('H₂O · GENİŞ BİR V', 'v', 'H–O–H AÇISI', '104,5°') },
    { t0: S3, t1: S4, html: T('DONARKEN', 'ALTIGEN <span class="y">HALKALAR</span>') },
    { t0: S4, t1: S4b, html: T('HALKALAR', 'ÜST ÜSTE <span class="y">DİZİLİR</span>') },
    { t0: S4b, t1: S5, html: T('BUZ KRİSTALİ', 'ALTIGEN <span class="y">PRİZMA</span>') },
    { t0: S5, t1: 26.0, html: T('NEMLİ BULUT', 'KÖŞELER <span class="y">HIZLI BÜYÜR</span>', 100) },
    { t0: 26.0, t1: S6, html: T('NEMLİ BULUT', '<span class="y">6</span> KOL UZAR') },
    { t0: S6, t1: S7, html: T('AYNI HAVA', 'AYNI <span class="y">DESEN</span>') },
    { t0: S7, t1: S7b, html: BIG('BİR KAR TANESİNDE', 'n', 'SU MOLEKÜLÜ', '10<sup style="font-size:.5em">18</sup>') },
    { t0: S7b, t1: S8, html: T('HER BİRİ FARKLI', 'İKİZİ <span class="y">YOK</span>') },
    { t0: S8, t1: 99, html: T('SIRADAKİ SORU', 'VOLKAN NASIL <span class="y">PATLAR?</span>', 100) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 44.04, shots, titles,
    follow: { t: 42.24, click: 43.22 },
    sfx: [[.2, 'ding', .6], [S1 + .5, 'pop', .8], [9.2, 'ding', .7], [13.4, 'snap', .5], [14.0, 'pop', .6], [S4 + .3, 'pop_low', .6], [S4b + .2, 'ding', .7], [25.0, 'whoosh', .6], [27.5, 'ding', .6],
      [S6 + .1, 'ding', .5], [S7 + .3, 'whoosh', .7], [S7b + .1, 'pop', .6], [S7b + .4, 'pop', .6], [S7b + .7, 'pop', .6], [S8 + .1, 'boom', 1], [S8 + .12, 'crunch', .5]],
  };
};
