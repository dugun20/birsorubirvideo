// Bilgi #12: Deprem nasıl oluşur? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: IRIS/EarthScope "Why do Earthquakes Happen?" (yer kabuğu levhalara bölünmüş; levhalar tırnak uzama hızı mertebesinde
// hareket eder; faydaki kilitli bölge gerilim biriktirir ve aniden kırılır); USGS "Earthquake Magnitude, Energy Release, and Shaking
// Intensity" (her tam büyüklük artışı yaklaşık 32 kat daha fazla enerji); USGS "Magnitude 7.8 earthquake, Nurdağı, Turkey"
// (6 Şubat 2023, M7.8, Doğu Anadolu Fay Zonu).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 313; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
    s.background = gradTex(...(o.bg || ['#0d2240', '#02060e'])); s.fog = new THREE.Fog(o.fog || 0x050d1c, o.near || 40, o.far || 140);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x0a0a12, o.hemi || .9));
    const key = new THREE.SpotLight(0xfff1dc, o.key || 2000, 160, .45, .55, 1.2); key.position.set(-18, 44, 34); s.add(key); s.add(key.target);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 700, 90); rim.position.set(20, 16, -14); s.add(rim);
    return key;
  }
  const warm = { bg: ['#2a1608', '#050302'], fog: 0x0a0604, rim: 0xff7a1a };
  const crustM = () => std(0x6b4a32, { roughness: .9 }), grassM = () => std(0x3d5a2a, { roughness: .9 });
  const mantleM = () => std(0xb3541e, { roughness: .7, emissive: 0x5a1a00, emissiveIntensity: .6 });
  // yer kabuğu bloğu (çim + kabuk + manto)
  function slab(w, d, o = {}) {
    const b = new THREE.Group();
    const soil = M(rb(w, .3, d, .08), grassM()); soil.position.y = .1; b.add(soil);
    const crust = M(rb(w, 1.6, d, .1), crustM()); crust.position.y = -.8; b.add(crust);
    for (let i = 0; i < 3; i++) { const ln = M(new THREE.BoxGeometry(w + .02, .05, d + .02), std(0x4a3222, { roughness: 1 })); ln.position.y = -.4 - i * .4; b.add(ln); }
    if (o.mantle !== false) { const m = M(rb(w, 1.2, d, .1), mantleM()); m.position.y = -2.2; b.add(m); }
    return b;
  }
  function town(b, n, w, d, seedOff = 0) {
    const bs = [];
    for (let i = 0; i < n; i++) { const h = .8 + r1() * 1.8; const bl = M(rb(.8, h, .8, .06), std([0xc9ced6, 0xd8c7b0, 0xa9b4c2][i % 3], { metalness: .2, roughness: .6 }));
      bl.position.set((r1() - .5) * (w - 1), .25 + h / 2, (r1() - .5) * (d - 1)); b.add(bl); bs.push(bl);
      for (let k = 0; k < 2; k++) { const wn = M(new THREE.PlaneGeometry(.2, .22), new THREE.MeshBasicMaterial({ color: 0xffd27a })); wn.position.set(-.18 + k * .36, h * .2, .41); bl.add(wn); } }
    return bs;
  }
  function arrow(len, col) {
    const g = new THREE.Group(); const m = new THREE.MeshBasicMaterial({ color: col });
    const sh = M(new THREE.CylinderGeometry(.12, .12, 1, 16), m); g.add(sh); const hd = M(new THREE.ConeGeometry(.32, .6, 24), m); g.add(hd);
    g.userData.set = l => { l = Math.max(.01, l); sh.scale.y = l; sh.position.y = l / 2; hd.position.y = l + .3; }; g.userData.set(len); return g;
  }

  const S1 = 3.12, S2 = 6.12, S3 = 10.24, S4 = 13.04, S5 = 17.31, S6 = 20.48, S7 = 24.96, S8 = 29.76, S9 = 32.96;

  // 1) Gece kasabası, zemin hafifçe titrer
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    lights(s, Object.assign({ key: 1900 }, warm));
    const B = slab(9, 7); B.position.set(0, 3.2, 0); s.add(B); const bs = town(B, 9, 9, 7);
    const d = dust(400, [30, 20, 20], 0xffd8b0, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const q = Math.sin(t * 31) * .04 * prog(t, .6, .8);
      B.position.set(q, 3.2 + Math.sin(t * 23) * .02 * prog(t, .6, .8), 0); B.rotation.y = -.5 + t * .05;
      bs.forEach((b, i) => b.rotation.z = Math.sin(t * 20 + i) * .03 * prog(t, .6, .8));
      d.rotation.y = t * .03;
      cam.position.set(0, lerp(9, 8, t / S1), lerp(24, 21, t / S1)); cam.lookAt(0, 5.0, 0); };
  } });
  // 2) Dünya: levhalar (parlayan sınır çizgileri)
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    s.background = gradTex('#0a0f1e', '#000000'); s.fog = new THREE.Fog(0x000000, 60, 200);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, .6)); const sun = new THREE.DirectionalLight(0xfff4e0, 2.6); sun.position.set(-10, 8, 10); s.add(sun);
    const rim = new THREE.PointLight(0xff7a1a, 500, 60); rim.position.set(8, 6, -6); s.add(rim);
    const E = new THREE.Group(); E.position.set(0, 6.6, 0); s.add(E);
    const eg = new THREE.SphereGeometry(3.4, 96, 64); const P = eg.attributes.position; const ec = [];
    const cO = new THREE.Color(0x1a4f9a), cL = new THREE.Color(0x5a7a3a);
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i); const n = hash(x, y, z) + .4 * hash(x * 2.7, z * 2.7, y * 2.7); const c = n > .5 ? cL : cO; ec.push(c.r, c.g, c.b); }
    eg.setAttribute('color', new THREE.Float32BufferAttribute(ec, 3)); E.add(M(eg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .7 })));
    const lineM = new THREE.MeshBasicMaterial({ color: 0xff8a2a, transparent: true, opacity: 0 });
    const rings = []; [[.3, 0, .2], [1.2, .5, 0], [-.6, 1.1, .4], [.9, -.8, 1.4], [0, 1.57, .9], [-1.1, .2, -.7]].forEach(([a, b, c]) => {
      const r = M(new THREE.TorusGeometry(3.43, .035, 8, 160, Math.PI * (.9 + r1() * .8)), lineM); r.rotation.set(a, b, c); E.add(r); rings.push(r); });
    const atm = M(new THREE.SphereGeometry(3.6, 64, 48), new THREE.MeshBasicMaterial({ color: 0x4aa8ff, transparent: true, opacity: .15, side: THREE.BackSide })); E.add(atm);
    const stars = dust(1200, [120, 120, 40], 0xffffff, .25, .9); stars.position.z = -40; s.add(stars);
    return t => {
      const a = t - S1; E.rotation.set(.3, t * .25, 0);
      lineM.opacity = .95 * prog(a, .7, .8) * (.8 + .2 * Math.sin(t * 6));
      cam.position.set(0, 6.6, lerp(26, 23, ease(prog(a, 0, 3)))); cam.lookAt(0, 7.0, 0); };
  } });
  // 3) İki levha yavaşça kayar (yılda birkaç cm)
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    lights(s, Object.assign({ key: 2000 }, warm));
    const G = new THREE.Group(); G.position.set(0, 3.4, 0); s.add(G);
    const A = slab(4.4, 6); A.position.x = -2.25; G.add(A); const B = slab(4.4, 6); B.position.x = 2.25; G.add(B);
    const ar = [arrow(1.4, 0xffcf2e), arrow(1.4, 0xffcf2e)]; ar[0].rotation.x = Math.PI / 2; ar[1].rotation.x = -Math.PI / 2; ar.forEach(a => G.add(a));
    const ruler = new THREE.Group(); ruler.position.set(0, 1.3, 3.4); G.add(ruler);
    ruler.add(M(rb(3.2, .5, .1, .04), std(0xf2d14b, { roughness: .5 })));
    for (let i = 0; i <= 10; i++) { const tk = M(new THREE.BoxGeometry(.03, i % 5 ? .15 : .3, .02), new THREE.MeshBasicMaterial({ color: 0x222222 })); tk.position.set(-1.5 + i * .3, .25 - (i % 5 ? .075 : .15), .06); ruler.add(tk); }
    const mk = M(new THREE.ConeGeometry(.12, .3, 16), new THREE.MeshBasicMaterial({ color: 0xff3b30 })); mk.rotation.z = Math.PI; ruler.add(mk);
    const d = dust(400, [30, 20, 20], 0xffd8b0, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S2; const sl = a * .18;
      A.position.z = sl; B.position.z = -sl;
      ar[0].position.set(-2.25, 1.0, -1 + sl); ar[1].position.set(2.25, 1.0, 1 - sl); ar.forEach(x => x.visible = a > .4);
      mk.position.set(-1.5 + clamp(a / 4) * 1.2, .5, .1);
      G.rotation.set(.15, -.6 + a * .04, 0); d.rotation.y = t * .03;
      cam.position.set(0, 10.5, 23); cam.lookAt(0, 4.6, 0); };
  } });
  // fay kesiti: iki blok yan yana, aralarında tırtıklı fay yüzeyi + işaret çizgisi
  function faultScene(s) {
    const G = new THREE.Group(); G.position.set(0, 3.6, 0); s.add(G);
    const A = slab(4, 5, { mantle: false }); A.position.x = -2.02; G.add(A);
    const B = slab(4, 5, { mantle: false }); B.position.x = 2.02; G.add(B);
    const teeth = []; for (let i = 0; i < 10; i++) { const tth = M(new THREE.ConeGeometry(.18, .5, 4), std(0x8a6242, { roughness: .9 })); tth.rotation.z = (i % 2 ? 1 : -1) * Math.PI / 2; tth.position.set((i % 2 ? .12 : -.12), -.2 - (i % 5) * .3, -2 + Math.floor(i / 2) * 1); G.add(tth); teeth.push(tth); }
    // yol / çit: fayı kesen sarı şerit (gerilmeyi gösterir)
    const segs = []; for (let i = 0; i < 16; i++) { const sg = M(rb(.5, .06, .4, .02), new THREE.MeshStandardMaterial({ color: 0xffcf2e, emissive: 0x8a6a00, emissiveIntensity: .5 })); G.add(sg); segs.push(sg); }
    const setRoad = (bend, off) => segs.forEach((sg, i) => { const x = -3.75 + i * .5; const side = x < 0 ? -1 : 1;
      const z = off * side * .5 + bend * Math.tanh(x * 1.2) * (1 - Math.min(1, Math.abs(x) / 4)) * -1; sg.position.set(x, .3, z); });
    return { G, A, B, teeth, segs, setRoad };
  }
  // 4) Fay sürtünmeyle kilitlenir (kilit)
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    lights(s, Object.assign({ key: 2000 }, warm));
    const F = faultScene(s);
    const lock = new THREE.Group(); lock.position.set(0, 7.0, 1); s.add(lock);
    lock.add(M(rb(1.4, 1.1, .5, .12), std(0xffcf2e, { metalness: .8, roughness: .25 })));
    const sh = M(new THREE.TorusGeometry(.45, .12, 16, 40, Math.PI), std(0xc0c6ce, { metalness: .9, roughness: .2 })); sh.position.y = .55; lock.add(sh);
    const kh = M(new THREE.CylinderGeometry(.1, .1, .1, 16), std(0x111111)); kh.rotation.x = Math.PI / 2; kh.position.z = .26; lock.add(kh);
    const d = dust(400, [30, 20, 20], 0xffd8b0, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S3; F.setRoad(0, 0);
      const k = back(prog(a, 1.6, .5)); lock.scale.setScalar(Math.max(.01, k)); lock.visible = k > .01; sh.position.y = .55 + (1 - ease(prog(a, 2.0, .3))) * .35;
      lock.rotation.y = Math.sin(t * 1.2) * .3;
      F.G.rotation.set(.35, -.35 + a * .05, 0); d.rotation.y = t * .03;
      cam.position.set(0, 9.0, 20); cam.lookAt(0, 5.2, 0); };
  } });
  // 5) Levhalar iter, kayalar yay gibi gerilir, enerji birikir
  shots.push({ t0: S4, t1: S6, fov: 40, build: (s, cam) => {
    lights(s, Object.assign({ key: 2000 }, warm));
    const F = faultScene(s);
    const ar = [arrow(1.2, 0xffcf2e), arrow(1.2, 0xffcf2e)]; ar[0].rotation.x = Math.PI / 2; ar[1].rotation.x = -Math.PI / 2; ar.forEach(x => F.G.add(x));
    const glow = new THREE.PointLight(0xff5a1a, 0, 14); glow.position.set(0, 4, 3); s.add(glow);
    const core = M(new THREE.SphereGeometry(.5, 32, 24), new THREE.MeshBasicMaterial({ color: 0xffb04a, transparent: true, opacity: 0 })); core.position.set(0, 3.0, 0); s.add(core);
    const spark = dust(200, [3, 2, 3], 0xffc07a, .2, .8); spark.position.set(0, 3.0, 0); s.add(spark);
    const cracks = []; for (let i = 0; i < 7; i++) { const c = M(new THREE.BoxGeometry(.06, .9 + r1(), .06), new THREE.MeshBasicMaterial({ color: 0xffe08a })); c.position.set((r1() - .5) * .3, -.5 - r1() * .8, -2 + i * .65); c.rotation.z = (r1() - .5) * .8; F.G.add(c); cracks.push(c); }
    return t => {
      const a = t - S4; const str = ease(prog(a, .3, 3.6)); const brk = S6 - 1.6 + .05; const br = t > 19.85;
      F.setRoad(br ? 0 : str * 1.4, br ? 1.4 : 0);
      F.A.position.z = br ? .7 : 0; F.B.position.z = br ? -.7 : 0;
      ar[0].position.set(-2.4, 1.1, -1.6); ar[1].position.set(2.4, 1.1, 1.6); ar.forEach(x => { x.visible = !br; x.userData.set(1 + .2 * Math.sin(t * 6)); });
      glow.intensity = br ? 600 * Math.exp(-(t - 19.85) * 2) : 300 * str;
      core.material.opacity = br ? 0 : .7 * str; core.scale.setScalar(.6 + str * .9 + .08 * Math.sin(t * 12));
      spark.visible = br; const sk = prog(t, 19.85, .7); spark.scale.setScalar(.5 + sk * 4); spark.material.opacity = .9 * (1 - sk);
      cracks.forEach((c, i) => c.visible = br && t < 19.85 + .15 + i * .04 + .5);
      const sh = br ? Math.sin(t * 40) * .12 * Math.exp(-(t - 19.85) * 3) : Math.sin(t * 50) * .01 * str;
      F.G.position.x = sh; F.G.rotation.set(.35, -.35 + a * .03, 0);
      cam.position.set(0, 9.0, lerp(20, 18, ease(prog(a, 0, 3)))); cam.lookAt(0, 5.2, 0); };
  } });
  // 6) Sismik dalgalar her yöne yayılır
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    lights(s, Object.assign({ key: 700, hemi: .6 }, warm));
    const N = 90; const g = new THREE.PlaneGeometry(26, 26, N, N); g.rotateX(-Math.PI / 2); const P = g.attributes.position; const base = Float32Array.from(P.array);
    const col = []; for (let i = 0; i < P.count; i++) col.push(.24, .35, .16); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    const ground = M(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .85 })); ground.position.y = 2.4; s.add(ground);
    const C = g.attributes.color; const bs = []; const bm = [0xc9ced6, 0xd8c7b0, 0xa9b4c2].map(c => std(c, { roughness: .6 }));
    for (let i = 0; i < 26; i++) { const h = .8 + r1() * 1.8; const bl = M(rb(.8, h, .8, .06), bm[i % 3]); const a = r1() * Math.PI * 2, rr = 2.5 + r1() * 8; bl.userData = { x: Math.cos(a) * rr, z: Math.sin(a) * rr, h }; s.add(bl); bs.push(bl); }
    const epi = M(new THREE.SphereGeometry(.35, 24, 16), new THREE.MeshBasicMaterial({ color: 0xff3b30 })); s.add(epi);
    const el = new THREE.PointLight(0xff4a1a, 300, 10); s.add(el);
    const wave = (x, z, t) => { const r = Math.hypot(x, z); const ph = r - (t - S6) * 5.5; return ph < 0 ? Math.sin(ph * 1.6) * .45 * Math.exp(ph * .12) / (1 + r * .08) : 0; };
    return t => {
      for (let i = 0; i < P.count; i++) { const x = base[i * 3], z = base[i * 3 + 2]; const y = wave(x, z, t); P.setY(i, y); const k = clamp(.5 + y * 1.2); const cr = clamp(Math.abs(y) * 2); C.setXYZ(i, lerp(.2, .95, cr), lerp(.3, .45, cr), lerp(.14, .1, cr)); }
      P.needsUpdate = true; C.needsUpdate = true; g.computeVertexNormals();
      bs.forEach(b => { const { x, z, h } = b.userData; const y = wave(x, z, t); b.position.set(x, 2.4 + y + h / 2, z); b.rotation.set(wave(x + .5, z, t) * .25, 0, wave(x, z + .5, t) * .25); });
      epi.position.set(0, 2.6 + .1 * Math.sin(t * 10), 0); el.position.set(0, 3.5, 0); el.intensity = 120 + 80 * Math.sin(t * 8);
      const a = t - S6; cam.position.set(Math.sin(a * .2) * 4, 16, 25); cam.lookAt(0, 2.0, 0); };
  } });
  // 7) Her 1 büyüklük = ~32 kat enerji: 1 küp vs 32 küp
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    lights(s, Object.assign({ key: 2000 }, warm));
    const em = new THREE.MeshStandardMaterial({ color: 0xffb04a, emissive: 0xff6a00, emissiveIntensity: .7, metalness: .3, roughness: .3 });
    const one = M(rb(.7, .7, .7, .08), em); one.position.set(-2.6, 4.0, 0); s.add(one);
    const many = []; for (let i = 0; i < 32; i++) { const c = M(rb(.7, .7, .7, .08), em); c.userData.p = new THREE.Vector3(.35 + (i % 4) * .78, 4.0 + Math.floor(i / 8) * .78, ((i >> 2) % 2) * .78 - .4); s.add(c); many.push(c); }
    const ped = [-2.6, 1.5].map(x => { const p = M(new THREE.CylinderGeometry(1.6, 1.8, .4, 48), std(0x2a2f36, { metalness: .6 })); p.position.set(x, 3.4, 0); s.add(p); return p; });
    const glow = new THREE.PointLight(0xff8a2a, 400, 14); glow.position.set(2.2, 7, 3); s.add(glow);
    const d = dust(400, [30, 20, 20], 0xffd8b0, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S7; one.rotation.y = t * .5;
      many.forEach((c, i) => { const k = easeOut(prog(a, 1.0 + i * .06, .35)); c.visible = k > 0; c.position.copy(c.userData.p); c.position.y += (1 - k) * 4; c.rotation.y = (1 - k) * 2; });
      d.rotation.y = t * .03;
      cam.position.set(Math.sin(a * .2) * 1.5, 7.0, 17); cam.lookAt(-.2, 5.2, 0); };
  } });
  // 8) 6 Şubat: sismograf çizer, 7,8
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    lights(s, Object.assign({ key: 2000 }, warm, { rim: 0xff3b30 }));
    const G = new THREE.Group(); G.position.set(0, 5.4, 0); G.scale.setScalar(.72); s.add(G);
    const drum = M(new THREE.CylinderGeometry(1.5, 1.5, 5.6, 64), std(0xf2efe8, { roughness: .6 })); drum.rotation.z = Math.PI / 2; G.add(drum);
    [-1, 1].forEach(k => { const c = M(new THREE.CylinderGeometry(1.6, 1.6, .2, 64), std(0x2a2f36, { metalness: .7 })); c.rotation.z = Math.PI / 2; c.position.x = k * 2.9; G.add(c); });
    const base = M(rb(7, .5, 3.4, .1), std(0x1a2230, { metalness: .6 })); base.position.y = -2.0; G.add(base);
    const arm = M(new THREE.BoxGeometry(.12, .12, 2.4), std(0xc0c6ce, { metalness: .9 })); G.add(arm);
    const pen = M(new THREE.ConeGeometry(.1, .3, 16), new THREE.MeshBasicMaterial({ color: 0xff3b30 })); pen.rotation.x = -Math.PI / 2; G.add(pen);
    const NP = 260; const pts = new Float32Array(NP * 3); const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.BufferAttribute(pts, 3));
    const line = new THREE.Line(lg, new THREE.LineBasicMaterial({ color: 0xd1201a })); G.add(line);
    const amp = u => { const q = prog(u, .25, .1) * Math.exp(-Math.max(0, u - .35) * 3.5); return (Math.sin(u * 160) * .9 + Math.sin(u * 97) * .5) * (.03 + q * .9); };
    return t => {
      const a = t - S8; const head = a * .5;
      for (let i = 0; i < NP; i++) { const u = head - i * .006; const x = -2.6 + i * .02; const y = u > 0 ? amp(u) : 0; pts[i * 3] = -x * .9 + .2; pts[i * 3 + 1] = y * .9; pts[i * 3 + 2] = 1.55; }
      lg.attributes.position.needsUpdate = true; lg.setDrawRange(0, Math.min(NP, Math.floor(a * 90)));
      const py = head > 0 ? amp(head) * .9 : 0; pen.position.set(2.54, py, 1.72); arm.position.set(2.54, py, 3.0);
      drum.rotation.x = -t * .6; G.rotation.set(.15, -.25 + Math.sin(t * .3) * .08, 0); G.position.x = Math.sin(t * 40) * .03 * prog(a, .7, .2) * Math.exp(-Math.max(0, a - 1) * 1.5);
      cam.position.set(0, 6.4, 16); cam.lookAt(0, 5.2, 0); };
  } });
  // 9) Sıradaki soru: hapşırık — yüz, kapanan gözler, damlacık bulutu
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    lights(s, { key: 500, hemi: .6, rim: 0x7ee0ff });
    const H = new THREE.Group(); H.position.set(0, 6.6, 0); H.scale.setScalar(.8); s.add(H);
    const head = M(new THREE.SphereGeometry(2, 64, 48), std(0xd9b49a, { roughness: .6 })); head.scale.set(1, 1.15, 1); H.add(head);
    const hair = M(new THREE.SphereGeometry(2.06, 64, 32, 0, Math.PI * 2, 0, Math.PI * .42), std(0x2a1c14, { roughness: .8 })); hair.rotation.x = -.05; hair.scale.set(1, 1.15, 1); H.add(hair);
    const nose = M(new THREE.SphereGeometry(.34, 32, 24), std(0xd0a088, { roughness: .6 })); nose.position.set(0, -.15, 1.95); H.add(nose);
    const eyes = [-1, 1].map(k => { const e = new THREE.Group(); e.position.set(k * .7, .45, 1.72); H.add(e);
      const w = M(new THREE.SphereGeometry(.32, 32, 24), std(0xffffff, { roughness: .3 })); w.scale.z = .5; e.add(w);
      const p = M(new THREE.SphereGeometry(.15, 24, 16), new THREE.MeshBasicMaterial({ color: 0x1a1a1a })); p.position.z = .14; e.add(p);
      const lid = M(new THREE.SphereGeometry(.34, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), std(0xc99c84, { roughness: .6 })); lid.rotation.x = Math.PI / 2; e.add(lid);
      return { e, lid }; });
    const mouth = M(new THREE.SphereGeometry(.4, 32, 16), new THREE.MeshBasicMaterial({ color: 0x5a1a1a })); mouth.scale.set(1.2, .5, .4); mouth.position.set(0, -.95, 1.8); H.add(mouth);
    const spray = dust(400, [2, 1.2, 4], 0xdff4ff, .14, .9); s.add(spray);
    const q = M(new THREE.TorusGeometry(.5, .12, 12, 32, Math.PI * 1.4), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); q.rotation.z = -Math.PI * .3; s.add(q);
    const qd = M(new THREE.SphereGeometry(.14, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); s.add(qd);
    return t => {
      const a = t - S9; const cyc = (a % 2.4) / 2.4; const pre = prog(cyc, .2, .3), sn = prog(cyc, .5, .08);
      const close = cyc > .45 && cyc < .8 ? 1 : 0;
      eyes.forEach(({ lid }) => lid.rotation.x = lerp(Math.PI * .95, Math.PI * .5, close));
      H.rotation.set(lerp(-.15, .25, sn) * (cyc < .8 ? 1 : 0) - pre * .15 * (cyc < .5 ? 1 : 0), Math.sin(t * .4) * .3, 0);
      mouth.scale.set(1.2, .5 + (cyc > .45 && cyc < .6 ? .5 : 0), .4);
      const sk = prog(cyc, .5, .4); spray.visible = sk > 0 && sk < 1; spray.position.set(0, 5.8, 2.0 + sk * 3); spray.scale.set(.3 + sk * 1.5, .3 + sk * 1.2, .3 + sk); spray.material.opacity = .9 * (1 - sk);
      q.position.set(2.5, 8.4, .5); qd.position.set(2.4, 7.55, .5); q.visible = qd.visible = Math.sin(a * 4) > -.6;
      cam.position.set(Math.sin(a * .2) * 2, 6.6, 18); cam.lookAt(0, 6.2, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'DEPREM NASIL<br><span class="y">OLUŞUR?</span>', 104) },
    { t0: S1, t1: S2, html: T('YER KABUĞU', 'DEV BİR <span class="y">YAPBOZ</span>') },
    { t0: S2, t1: S3, html: T('TIRNAK UZAMA HIZIYLA', 'YILDA BİRKAÇ <span class="y">CM</span>', 104) },
    { t0: S3, t1: S4, html: T('FAYLAR', 'SÜRTÜNMEYLE <span class="y">KİLİTLENİR</span>', 96) },
    { t0: S4, t1: S5, html: T('KAYALAR', 'YAY GİBİ <span class="y">GERİLİR</span>') },
    { t0: S5, t1: 19.85, html: T('YÜZYILLARCA', 'ENERJİ <span class="y">BİRİKİR</span>') },
    { t0: 19.85, t1: S6, html: T('BİR ANDA', 'KAYA <span class="y">KIRILIR!</span>') },
    { t0: S6, t1: S7, html: T('FAY KAYAR', 'SİSMİK <span class="y">DALGALAR</span>') },
    { t0: S7, t1: S8, html: BIG('+1 BÜYÜKLÜK', 'k32', 'KAT DAHA FAZLA ENERJİ', '~32') },
    { t0: S8, t1: S9, html: BIG('6 ŞUBAT 2023', 'k78', 'BÜYÜKLÜĞÜNDE', '7,8') },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'HAPŞIRIRKEN GÖZLER<br>NEDEN <span class="y">KAPANIR?</span>', 90) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k32', S7], ['k78', S8]];
  return {
    END: 38.44, shots, titles,
    update: (t, q) => pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; }),
    follow: { t: 36.56, click: 37.54 },
    sfx: [[.7, 'boom', .4], [4.0, 'ding', .5], [S2 + .5, 'whoosh', .4], [S3 + 1.6, 'pop', .6], [S3 + 2.0, 'snap', .8], [14.0, 'crunch', .3], [16.0, 'crunch', .4],
      [19.85, 'snap', 1], [19.88, 'boom', 1], [19.9, 'crunch', .9], [S6 + .2, 'boom', .6], [26.0, 'ding', .5], [27.0, 'pop', .4], [27.6, 'pop', .4], [28.2, 'ding', .6],
      [S8 + .9, 'boom', .6], [S9 + 1.2, 'whoosh', .5]],
  };
};
