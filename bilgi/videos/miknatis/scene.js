// Bilgi #22: Mıknatıs nasıl çeker? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: OpenStax College Physics 2e, 22.2 "Ferromagnets and Electromagnets" (UCF Pressbooks: demir gibi ferromanyetik maddelerde atomlar
// 'domain' denen bölgeler oluşturur; mıknatıslanmamış demirde bölgeler gelişigüzel yönlüdür, dış alan onları hizalar; yumuşak demir alan kalkınca
// eski haline döner; mıknatısı ikiye bölmek iki kutuplu iki mıknatıs verir, tek kutup yoktur). Universe Today, "How do magnets work" (elektron
// spini küçük bir manyetik alan üretir; zıt spinli eşleşmiş elektronlar birbirini yok eder; zıt kutuplar çeker, aynı kutuplar iter).
export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const M = (g, m) => new THREE.Mesh(g, m);
  const V = (x, y, z = 0) => new THREE.Vector3(x, y, z);
  let seed = 2020; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
    const hemi = new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi ?? .8); s.add(hemi);
    const key = new THREE.DirectionalLight(o.keyc || 0xfff4e0, o.key ?? 2.2); key.position.set(...(o.kp || [-10, 12, 10])); s.add(key);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 600, 60); rim.position.set(6, 9, -5); s.add(rim);
    const d = dust(500, [26, 18, 16], o.dust || 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return { d, rim, key, hemi };
  }
  const glow = (c, op = .9) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false });
  function qmark(s, x, y, sc = 1) { const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); q.position.set(x, y, .5); q.scale.setScalar(sc); s.add(q);
    const qa = M(new THREE.TorusGeometry(.42, .1, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.12, 12, 8), qm); qd.position.set(-.08, -.72, 0); q.add(qd); return q; }
  const RED = 0xe0302a, BLUE = 0x2f6dff;
  const letterTex = (ch, bg) => { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'); g.fillStyle = bg; g.fillRect(0, 0, 128, 128);
    g.fillStyle = '#ffffff'; g.font = 'bold 84px Oswald, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(ch, 64, 70); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const texN = letterTex('N', '#e0302a'), texS = letterTex('S', '#2f6dff');
  // Çubuk mıknatıs: +x tarafı N (kırmızı), -x tarafı S (mavi)
  function bar(len = 2.4, th = .55) { const g = new THREE.Group();
    const n = M(new THREE.BoxGeometry(len / 2, th, th), new THREE.MeshStandardMaterial({ map: texN, roughness: .3, metalness: .35 })); n.position.x = len / 4; g.add(n);
    const sp = M(new THREE.BoxGeometry(len / 2, th, th), new THREE.MeshStandardMaterial({ map: texS, roughness: .3, metalness: .35 })); sp.position.x = -len / 4; g.add(sp);
    g.n = n; g.s = sp; return g; }
  // Minik mıknatıs oku (+y yönünü gösterir): kırmızı uç, mavi kuyruk
  const arrM = { r: std(RED, { roughness: .3, metalness: .3, emissive: 0x300000 }), b: std(BLUE, { roughness: .3, metalness: .3, emissive: 0x000830 }) };
  function arrow(sz = 1) { const g = new THREE.Group();
    const tail = M(new THREE.CylinderGeometry(.05 * sz, .05 * sz, .3 * sz, 14), arrM.b); tail.position.y = -.1 * sz; g.add(tail);
    const head = M(new THREE.ConeGeometry(.11 * sz, .24 * sz, 18), arrM.r); head.position.y = .15 * sz; g.add(head); return g; }
  function fieldLoops(s, n, rx, ry, c = 0x7ee0ff) { return Array.from({ length: n }, (_, i) => { const k = 1 + i * .45;
    const pts = Array.from({ length: 49 }, (_, j) => { const a = j / 48 * Math.PI * 2; return V(Math.sin(a) * rx * k, Math.cos(a) * ry * Math.sqrt(k), 0); });
    const m = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true), 96, .012, 6, true), glow(c, .5)); s.add(m); return m; }); }
  // Demir blok: hücreler ve her hücrede bir ok; bölgeler 2x2 hücre
  function ironBlock(s, cx, cy) { const G = new THREE.Group(); G.position.set(cx, cy, 0); s.add(G);
    const slab = M(new THREE.BoxGeometry(3.6, 3.0, .35), std(0x6a6e78, { metalness: .85, roughness: .35 })); slab.position.z = -.25; G.add(slab);
    const cells = []; const regColors = [0x3a4a6a, 0x4a3a5a, 0x3a5a5a, 0x5a4a3a, 0x3a5a3a, 0x5a3a3a];
    for (let i = 0; i < 6; i++) for (let j = 0; j < 5; j++) { const reg = Math.floor(i / 2) + 3 * Math.floor(j / 3);
      const tile = M(new THREE.BoxGeometry(.56, .56, .06), std(regColors[reg % 6], { metalness: .5, roughness: .4, transparent: true, opacity: .9 })); const x = -1.5 + i * .6, y = -1.2 + j * .6; tile.position.set(x, y, 0); G.add(tile);
      const a = arrow(1.2); a.position.set(x, y, .25); G.add(a); cells.push({ a, tile, reg, rnd: r1() * Math.PI * 2, reg0: [0.3, 2.2, 4.0, 1.2, 3.1, 5.2][reg % 6] }); }
    G.cells = cells; G.slab = slab; return G; }

  const S1 = 3.68, S2 = 8.4, S3 = 10.84, S4 = 14.4, S5 = 17.44, S6 = 22.24, S7 = 24.68, S8 = 27.95, S9 = 31.68;

  // 1) Çubuk mıknatıs döner, içi açılır: minik mıknatıs okları dizisi
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010308'], rim: 0xff4a4a });
    const B = bar(3.6, .9); B.position.set(0, 4.85, 0); s.add(B);
    const arr = []; for (let i = 0; i < 9; i++) for (let j = 0; j < 3; j++) { const a = arrow(.85); a.rotation.z = -Math.PI / 2; a.position.set(-1.6 + i * .4, -.27 + j * .27, .5); B.add(a); arr.push(a); }
    const loops = fieldLoops(s, 3, 1.55, .55); loops.forEach(l => { l.position.set(0, 4.85, -.2); });
    return t => {
      E.d.rotation.y = t * .02; const op = ease(prog(t, 1.2, .9));
      B.rotation.y = lerp(-.9, -.15, ease(prog(t, 0, 1.6))) + Math.sin(t * .8) * .05; B.rotation.x = .15;
      B.n.material.opacity = B.s.material.opacity = 1 - .75 * op; B.n.material.transparent = B.s.material.transparent = true; B.n.material.depthWrite = B.s.material.depthWrite = op < .5;
      arr.forEach((a, i) => { a.scale.setScalar(Math.max(.001, back(prog(t, 1.4 + i * .02, .4)))); });
      loops.forEach((l, i) => { l.material.opacity = (.25 + .25 * Math.sin(t * 3 - i)) * op; l.rotation.x = B.rotation.y * .3; });
      cam.position.set(Math.sin(t * .3) * .6, 5.5, lerp(13.6, 12.6, ease(prog(t, 0, S1)))); cam.lookAt(0, 4.95, 0); };
  } });
  // 2) Elektron: kendi ekseninde dönen topaç gibi küre + çevresinde manyetik alan halkaları
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010308'], rim: 0x4fc3ff });
    const tex = (() => { const c = document.createElement('canvas'); c.width = 256; c.height = 128; const g = c.getContext('2d'); for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#3a8aff' : '#9fd4ff'; g.fillRect(i * 32, 0, 32, 128); } const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
    const e = M(new THREE.SphereGeometry(.75, 48, 32), new THREE.MeshStandardMaterial({ map: tex, roughness: .25, metalness: .2, emissive: 0x0a2a60 })); e.position.set(0, 4.8, 0); s.add(e);
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0x4fa0ff, transparent: true, opacity: .55, blending: THREE.AdditiveBlending, depthWrite: false })); halo.scale.setScalar(3); halo.position.copy(e.position); s.add(halo);
    const axis = arrow(3.2); axis.position.set(0, 4.8, 0); s.add(axis);
    const spinR = M(new THREE.TorusGeometry(1.05, .025, 8, 64, Math.PI * 1.6), glow(0xffcf2e, .9)); spinR.rotation.x = Math.PI / 2; spinR.position.copy(e.position); s.add(spinR);
    const tip = M(new THREE.ConeGeometry(.08, .2, 12), glow(0xffcf2e, .9)); spinR.add(tip);
    const F = new THREE.Group(); F.position.copy(e.position); s.add(F);
    const loops = []; for (let k = 0; k < 6; k++) { const g = new THREE.Group(); g.rotation.y = k / 6 * Math.PI; F.add(g); fieldLoops(g, 2, 1.0, 1.35).forEach(l => { l.position.x = 1.15; loops.push(l); }); const g2 = new THREE.Group(); g2.rotation.y = k / 6 * Math.PI + Math.PI; F.add(g2); }
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02; e.rotation.y = t * 4; spinR.rotation.z = -t * 4; tip.position.set(Math.cos(Math.PI * 1.6) * 1.05, Math.sin(Math.PI * 1.6) * 1.05, 0); tip.rotation.z = Math.PI * 1.6;
      const k = ease(prog(a, 2.6, 1.0)); loops.forEach((l, i) => { l.material.opacity = .45 * k * (.6 + .4 * Math.sin(t * 3 + i)); l.scale.setScalar(.6 + .4 * k); });
      F.rotation.y = t * .3; axis.scale.setScalar(Math.max(.001, back(prog(a, 1.0, .5))));
      cam.position.set(Math.sin(a * .25) * 1.2, 6.2, 12.4); cam.lookAt(0, 4.85, 0); };
  } });
  // 3) Çoğu maddede: elektron çiftleri zıt yönde, alanlar söner
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010308'], rim: 0x8f7aff });
    const G = new THREE.Group(); G.position.set(0, 4.8, 0); s.add(G);
    const pairs = []; for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) { const p = new THREE.Group(); p.position.set(-1.6 + i * 1.6, -.8 + j * 1.6, 0); G.add(p);
      const up = arrow(1.6); up.position.x = -.25; p.add(up); const dn = arrow(1.6); dn.position.x = .25; dn.rotation.z = Math.PI; p.add(dn);
      const h = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0x4fa0ff, transparent: true, opacity: .6, blending: THREE.AdditiveBlending, depthWrite: false })); h.scale.setScalar(1.4); p.add(h); pairs.push({ p, up, dn, h }); }
    return t => {
      const a = t - S2; E.d.rotation.y = t * .02;
      pairs.forEach(({ p, up, dn, h }, i) => { const k = ease(prog(a, .3 + i * .1, .6)); up.rotation.z = lerp(Math.PI * .5, 0, k); dn.rotation.z = lerp(Math.PI * .5, Math.PI, k);
        h.material.opacity = .6 * (1 - ease(prog(a, .9 + i * .1, .6))); p.rotation.y = Math.sin(t * 1.5 + i) * .4; });
      G.rotation.y = Math.sin(t * .4) * .2;
      cam.position.set(Math.sin(a * .3) * .5, 5.5, 12.6); cam.lookAt(0, 4.9, 0); };
  } });
  // 4) Demirde bölgeler: aynı bölgedeki oklar aynı yöne bakar
  // 5) Normal demirde bölgeler gelişigüzel
  // 6) Mıknatıs yaklaşınca hepsi aynı yöne döner
  const domainShot = (t0, t1, mode) => shots.push({ t0, t1, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010308'], rim: mode === 'align' ? 0xff4a4a : 0x4fc3ff });
    const G = ironBlock(s, 0, 4.55); if (mode === 'align') { G.scale.setScalar(.75); G.position.x = -.65; }
    let B = null; if (mode === 'align') { B = bar(1.5, .45); s.add(B); }
    const loops = mode === 'align' ? fieldLoops(s, 3, 2.2, 2.0) : []; loops.forEach(l => { l.position.set(.5, 4.55, -.6); l.rotation.z = Math.PI / 2; l.scale.setScalar(.55); });
    return t => {
      const a = t - t0; E.d.rotation.y = t * .02; G.rotation.y = Math.sin(t * .5) * .25; G.rotation.x = -.12;
      G.cells.forEach((c, i) => { let ang;
        if (mode === 'regions') { ang = lerp(c.rnd + t * .5, c.reg0, ease(prog(a, .6, 1.2))); c.tile.material.opacity = .9; }
        else if (mode === 'random') { ang = c.reg0 + Math.sin(t * 1.2 + c.reg) * .25; }
        else { const k = ease(prog(a, .9 + (i % 6) * .08, 1.2)); ang = lerp(c.reg0 + Math.sin(t * 1.2 + c.reg) * .25, -Math.PI / 2, k); c.tile.material.color.lerp(new THREE.Color(0x7a3a3a), k * .05); }
        c.a.rotation.z = ang; });
      if (mode === 'random') G.cells.forEach(c => c.tile.material.emissive.setHex(0x000000));
      if (B) { const k = ease(prog(a, 0, 1.0)); B.position.set(lerp(4.5, 1.7, k), 4.55, .2); G.slab.material.emissive.setHex(0x401010); G.slab.material.emissiveIntensity = ease(prog(a, 2.0, 1.5)) * (.6 + .3 * Math.sin(t * 4));
        loops.forEach((l, i) => l.material.opacity = .4 * ease(prog(a, 2.2, 1)) * (.6 + .4 * Math.sin(t * 3 - i))); }
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 12.8); cam.lookAt(0, 4.85, 0); };
  } });
  domainShot(S3, S4, 'regions'); domainShot(S4, S5, 'random'); domainShot(S5, S6, 'align');
  // 7) Ataş zıplayıp mıknatısa yapışır
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010308'], rim: 0xff4a4a });
    const Mg = new THREE.Group(); Mg.position.set(0, 5.45, 0); Mg.scale.setScalar(.9); s.add(Mg);
    const red = std(0xd42a2a, { roughness: .35, metalness: .3 }), sil = std(0xdfe4ea, { roughness: .2, metalness: .9 });
    Mg.add(M(new THREE.TorusGeometry(.8, .28, 32, 64, Math.PI), red));
    [-1, 1].forEach(k => { const leg = M(new THREE.CylinderGeometry(.28, .28, .7, 32), red); leg.position.set(k * .8, -.35, 0); Mg.add(leg); const tp = M(new THREE.CylinderGeometry(.28, .28, .3, 32), sil); tp.position.set(k * .8, -.85, 0); Mg.add(tp); });
    const clipM = std(0xc8ccd4, { metalness: .9, roughness: .2 });
    const clip = () => { const g = new THREE.Group(); const pts = [V(-.15, -.45), V(-.15, .35), V(.15, .35), V(.15, -.3), V(-.06, -.3), V(-.06, .2)];
      const c = new THREE.CatmullRomCurve3(pts.map(p => V(p.x, p.y, 0)), false, 'catmullrom', .1); g.add(M(new THREE.TubeGeometry(c, 60, .03, 8), clipM)); return g; };
    const clips = [-1, 1].map((k, i) => { const c = clip(); c.userData = { x: k * .9, d: .25 + i * .35, tx: k * .72 }; s.add(c); return c; });
    return t => {
      const a = t - S6; E.d.rotation.y = t * .02; Mg.rotation.y = Math.sin(t * .6) * .25;
      clips.forEach(c => { const k = prog(a, c.userData.d, .35); const kk = k * k; c.position.set(lerp(c.userData.x * 1.4, c.userData.tx, kk), lerp(3.2, 5.45 - 1.35 * .9 - .1, kk), 0); c.rotation.set(0, 0, lerp(Math.PI / 2, 0, easeOut(k)));
        if (k <= 0) c.position.y = 3.2 + Math.abs(Math.sin(t * 12)) * .04 * prog(a, c.userData.d - .25, .2); });
      cam.position.set(Math.sin(a * .3) * .6, 5.4, 11.8); cam.lookAt(0, 4.8, 0); };
  } });
  // 8) Zıt kutuplar çekişir (üst), aynı kutuplar itişir (alt)
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010308'], rim: 0x8f7aff });
    const A1 = bar(1.6, .45), A2 = bar(1.6, .45); s.add(A1, A2);
    const B1 = bar(1.6, .45), B2 = bar(1.6, .45); B2.rotation.y = Math.PI; s.add(B1, B2);
    const spark = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0xffe08a, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); spark.position.set(0, 5.75, .5); s.add(spark);
    const rep = [-1, 1].map(k => { const m = M(new THREE.ConeGeometry(.12, .3, 16), glow(0xff5a4a, .9)); m.rotation.z = -k * Math.PI / 2; s.add(m); return m; });
    return t => {
      const a = t - S7; E.d.rotation.y = t * .02;
      const kA = prog(a, .3, .6) ** 2; A1.position.set(lerp(-1.6, -.8, kA), 5.75, 0); A2.position.set(lerp(1.6, .8, kA), 5.75, 0);
      spark.material.opacity = kA >= 1 ? Math.max(0, 1 - (a - .9) * 2) : 0; spark.scale.setScalar(1.5 + (a - .9));
      const kB = easeOut(prog(a, 1.7, .6)); const jit = Math.sin(t * 30) * .03 * (1 - prog(a, 1.7, .3)) * (a > 1.4 ? 1 : 0);
      B1.position.set(lerp(-.95, -1.55, kB) - jit, 4.0, 0); B2.position.set(lerp(.95, 1.55, kB) + jit, 4.0, 0);
      rep.forEach((m, i) => { const k = i ? 1 : -1; m.position.set(k * lerp(.15, .55, kB), 4.0, .4); m.material.opacity = .9 * prog(a, 1.7, .2); });
      [A1, A2, B1, B2].forEach((b, i) => b.rotation.x = Math.sin(t * .8 + i) * .15);
      cam.position.set(Math.sin(a * .25) * .5, 5.4, 12.2); cam.lookAt(0, 4.85, 0); };
  } });
  // 9) Mıknatısı ikiye kes: iki yeni N-S mıknatıs
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010308'], rim: 0xff4a4a });
    const H1 = bar(1.6, .6), H2 = bar(1.6, .6); s.add(H1, H2);
    // kesilmeden önce: H1'in yalnızca S yarısı (sol), H2'nin yalnızca N yarısı (sağ) görünür = tek mıknatıs
    const blade = M(new THREE.BoxGeometry(.04, 1.6, 1.0), std(0xe8eef5, { metalness: 1, roughness: .1 })); s.add(blade);
    const flash = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0xffffff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); flash.position.set(0, 4.8, .5); flash.scale.setScalar(2.5); s.add(flash);
    const sp = dust(80, [1, 1, 1], 0xffe08a, .1, 0); sp.position.set(0, 4.8, .3); s.add(sp);
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02;
      const cut = prog(a, .6, .35); blade.visible = a < 1.4; blade.position.set(0, lerp(7.0, 4.8, ease(cut)) + (cut >= 1 ? prog(a, .95, .4) * 3 : 0), .1);
      const sep = easeOut(prog(a, 1.0, .7));
      const grow = back(prog(a, 1.4, .5)); const g = Math.max(.001, grow);
      H1.n.scale.x = g; H1.n.visible = grow > .01; H1.n.position.x = .4 * g; H1.s.position.x = -.4;
      H2.s.scale.x = g; H2.s.visible = grow > .01; H2.s.position.x = -.4 * g; H2.n.position.x = .4;
      H1.position.set(-sep * 1.0 - .4 * grow, 4.8, 0); H2.position.set(sep * 1.0 + .4 * grow, 4.8, 0);
      flash.material.opacity = cut > 0 && a < 1.3 ? (1 - prog(a, .95, .35)) * cut : 0; sp.material.opacity = .8 * (1 - prog(a, .95, .8)) * (cut >= 1 ? 1 : 0); sp.scale.setScalar(1 + prog(a, .95, .8) * 2);
      [H1, H2].forEach((h, i) => h.rotation.x = .2 + Math.sin(t * .8 + i) * .1);
      cam.position.set(Math.sin(a * .25) * .5, 5.4, 12.2); cam.lookAt(0, 4.85, 0); };
  } });
  // 10) Sıradaki soru: Neden esneriz? Esneyen 3D yüz
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0f1a3a', '#020308'], rim: 0xffb070, keyc: 0xffe6cc });
    const Hd = new THREE.Group(); Hd.position.set(-.15, 5.0, 0); s.add(Hd);
    const skin = std(0xf0b48a, { roughness: .55 });
    const head = M(new THREE.SphereGeometry(1.25, 64, 48), skin); head.scale.set(1, 1.12, 1); Hd.add(head);
    const hair = M(new THREE.SphereGeometry(1.28, 48, 32, 0, Math.PI * 2, 0, Math.PI * .42), std(0x3a2418, { roughness: .8 })); hair.position.y = .12; hair.rotation.x = -.25; Hd.add(hair);
    [-1, 1].forEach(k => { const ear = M(new THREE.SphereGeometry(.25, 24, 16), skin); ear.scale.set(.5, 1, .8); ear.position.set(k * 1.22, 0, 0); Hd.add(ear); });
    const lids = [-1, 1].map(k => { const e = M(new THREE.SphereGeometry(.17, 24, 16), std(0xffffff, { roughness: .3 })); e.position.set(k * .42, .22, 1.08); Hd.add(e);
      const p = M(new THREE.SphereGeometry(.08, 16, 12), std(0x2a1a10)); p.position.set(k * .42, .22, 1.24); Hd.add(p);
      const lid = M(new THREE.SphereGeometry(.185, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), skin); lid.position.copy(e.position); Hd.add(lid); return lid; });
    const mouth = M(new THREE.SphereGeometry(.3, 32, 24), std(0x5a1a1a, { roughness: .7 })); mouth.position.set(0, -.55, 1.05); Hd.add(mouth);
    const tongue = M(new THREE.SphereGeometry(.18, 24, 16), std(0xd06070)); tongue.position.set(0, -.75, 1.12); tongue.scale.set(1.2, .5, .6); Hd.add(tongue);
    const hand = M(new THREE.SphereGeometry(.35, 32, 24), skin); hand.scale.set(1, .7, .5); Hd.add(hand);
    const q = qmark(s, -1.95, 6.0, .55);
    const zt = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'); g.fillStyle = '#cfe6ff'; g.font = 'bold 56px Oswald, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('Z', 32, 34); return new THREE.CanvasTexture(c); })();
    const z = Array.from({ length: 3 }, (_, i) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: zt, transparent: true, depthWrite: false })); m.scale.setScalar(.3 + i * .08); s.add(m); return m; });
    return t => {
      const a = t - S9; E.d.rotation.y = t * .02;
      const y = Math.sin(clamp((a - .4) / 2.6) * Math.PI); const yy = ease(clamp(y * 1.4));
      mouth.scale.set(lerp(.8, 1.2, yy), lerp(.15, 1.6, yy), lerp(.5, .9, yy)); tongue.visible = yy > .3;
      lids.forEach(l => l.rotation.x = lerp(-1.4, .15, yy * .9));
      Hd.rotation.x = -.25 * yy; Hd.rotation.y = Math.sin(t * .5) * .2; Hd.position.y = 4.95 + Math.sin(t * 1.2) * .04;
      hand.position.set(lerp(1.6, .45, ease(prog(a, 1.0, .6))), lerp(-1.6, -.6, ease(prog(a, 1.0, .6))), 1.2); hand.visible = a > .9;
      z.forEach((m, i) => { const u = (t * .4 + i / 3) % 1; m.position.set(1.4 + u * .6, 5.4 + u * 1.0, .5); m.material.opacity = .9 * Math.sin(u * Math.PI); });
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * .8, 5.4, 12.6); cam.lookAt(0, 4.9, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('MIKNATISIN İÇİNDE', '<span class="y">SAYISIZ</span> MİNİK<br>MIKNATIS', 108) },
    { t0: S1, t1: S2, html: T('HER ELEKTRON', 'DÖNEN BİR<br><span class="y">TOPAÇ</span> GİBİ', 112) },
    { t0: S2, t1: S3, html: T('ÇOĞU MADDEDE', 'ALANLAR BİRBİRİNİ<br><span class="y">YOK EDER</span>', 96) },
    { t0: S3, t1: S4, html: T('AMA DEMİRDE', 'ATOMLAR<br><span class="y">BÖLGELER</span> KURAR', 106) },
    { t0: S4, t1: S5, html: T('NORMAL DEMİRDE', 'YÖNLER<br><span class="y">GELİŞİGÜZEL</span>', 110) },
    { t0: S5, t1: S6, html: T('MIKNATIS YAKLAŞINCA', 'HEPSİ <span class="y">AYNI YÖNE</span><br>DÖNER', 104) },
    { t0: S6, t1: S7, html: T('İŞTE BU YÜZDEN', 'ATAŞ<br><span class="y">YAPIŞIR</span>', 120) },
    { t0: S7, t1: S8, html: T('KUTUPLAR', 'ZIT <span class="y">ÇEKER</span><br>AYNI <span class="y">İTER</span>', 116) },
    { t0: S8, t1: S9, html: T('İKİYE KESSEN', '<span class="y">2</span> YENİ<br>MIKNATIS', 116) },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'NEDEN<br><span class="y">ESNERİZ?</span>', 116) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 35.88, shots, titles,
    update: () => {},
    follow: { t: 34.0, click: 34.9 },
    sfx: [[.3, 'whoosh', .5], [1.4, 'pop', .4], [1.7, 'pop', .35], [S1 + .3, 'whoosh', .4], [S1 + 1.0, 'pop_low', .4], [S2 + .4, 'click', .4], [S2 + 1.0, 'pop_low', .4],
      [S3 + .6, 'ding', .3], [S4 + .3, 'whoosh', .3], [S5 + .2, 'whoosh', .5], [S5 + 1.4, 'ding', .4], [S6 + .55, 'snap', .5], [S6 + .9, 'snap', .5],
      [S7 + .9, 'snap', .6], [S7 + 1.7, 'boom', .4], [S8 + .9, 'crunch', .6], [S8 + 1.5, 'pop', .4], [S9 + .4, 'whoosh', .5]],
  };
};
