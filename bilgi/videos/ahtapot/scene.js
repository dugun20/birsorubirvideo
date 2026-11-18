// Bilgi #21: Ahtapotun neden 3 kalbi var? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Live Science, "How many hearts does an octopus have?" (3 kalp: 2 solungaç kalbi kanı solungaçlardan geçirir, ortadaki en büyük
// sistemik kalp oksijenli kanı vücuda pompalar; kan bakır içeren hemosiyanin yüzünden mavidir, hemosiyanin soğuk ve oksijeni az ortamda daha iyi taşır;
// ahtapot yüzerken sistemik kalp birkaç anlığına durur). Smithsonian Magazine, "Ten curious facts about octopuses" (yüzerken kalp durur, bu yüzden
// sürünmeyi tercih etmeleri yorucu yüzmeden kaçınmalarıyla açıklanır).
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
  // Uca doğru incelen kol: eğri noktalarından tüp, halkalar merkeze doğru ölçeklenir
  function armGeo(P, r0, seg = 36, rad = 10) {
    const curve = new THREE.CatmullRomCurve3(P); const g = new THREE.TubeGeometry(curve, seg, r0, rad); const pa = g.attributes.position;
    for (let i = 0; i <= seg; i++) { const c = curve.getPointAt(i / seg); const k = 1 - .85 * i / seg;
      for (let j = 0; j <= rad; j++) { const idx = i * (rad + 1) + j; pa.setXYZ(idx, c.x + (pa.getX(idx) - c.x) * k, c.y + (pa.getY(idx) - c.y) * k, c.z + (pa.getZ(idx) - c.z) * k); } }
    g.computeVertexNormals(); return g; }
  // Ahtapot: baş (manto), gözler, 8 kol; o.glass=true ise yarı saydam gövde (kalpler görünsün)
  function octo(s, o = {}) {
    const O = new THREE.Group(); s.add(O); const col = o.col || 0xd0603a;
    const skin = o.glass ? std(col, { roughness: .35, transparent: true, opacity: .42, depthWrite: false }) : std(col, { roughness: .45, emissive: 0x2a0a04 });
    const head = M(new THREE.SphereGeometry(.85, 48, 32), skin); head.scale.set(1, 1.3, 1); head.position.y = .55; O.add(head);
    [-1, 1].forEach(k => { const e = M(new THREE.SphereGeometry(.15, 20, 16), std(0xfff3d0, { roughness: .3 })); e.position.set(k * .38, -.05, .7); O.add(e);
      const p = M(new THREE.BoxGeometry(.16, .05, .05), new THREE.MeshBasicMaterial({ color: 0x111111 })); p.position.set(k * .38, -.05, .85); O.add(p); });
    const armM = std(col, { roughness: .5, emissive: 0x2a0a04 });
    const arms = Array.from({ length: 8 }, (_, i) => { const m = M(new THREE.BufferGeometry(), armM); m.userData.an = (i + .5) / 8 * Math.PI * 2; O.add(m); return m; });
    O.head = head; O.arms = arms; O.skin = skin;
    // mode: 'float' (kollar aşağı dalgalanır), 'jet' (kollar arkada toplanır), 'crawl' (kollar zeminde yayılır)
    O.pose = (t, mode = 'float', k = 1) => arms.forEach((m, i) => { const an = m.userData.an; const P = [];
      for (let j = 0; j <= 10; j++) { const u = j / 10; let p;
        if (mode === 'jet') { const r = .35 + u * .25; p = V(Math.cos(an) * r, -.3 - u * 2.2, Math.sin(an) * r * .7); p.x += Math.sin(t * 6 + an + u * 4) * .08 * u; }
        else if (mode === 'crawl') { const r = .5 + u * 1.5; const lift = Math.max(0, Math.sin(t * 2.5 + i * 1.6)) * .25 * u; p = V(Math.cos(an) * r, -.5 - u * .45 + lift + u * u * .3, Math.sin(an) * r * .8); p.x += Math.sin(t * 2 + i - u * 3) * .12 * u; }
        else { const r = .45 + u * 1.0; const sw = Math.sin(t * 2 + an * 3 - u * 4) * .25 * u; p = V(Math.cos(an + sw) * r, -.35 - u * 1.1 + Math.sin(t * 2.5 + an + u * 5) * .15 * u, Math.sin(an + sw) * r * .7); }
        P.push(p); }
      m.geometry.dispose(); m.geometry = armGeo(P, .12 * k); });
    return O; }
  function heart(r, c) { const h = new THREE.Group(); const m = std(c, { emissive: c, emissiveIntensity: .45, roughness: .3 });
    const a = M(new THREE.SphereGeometry(r, 32, 24), m); a.scale.set(1, 1.15, .9); h.add(a);
    const g = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: c, transparent: true, opacity: .7, blending: THREE.AdditiveBlending, depthWrite: false })); g.scale.setScalar(r * 4); h.add(g); h.m = m; h.g = g; return h; }
  // solungaç: tüy gibi üst üste dizilmiş ince lameller
  function gill(len = 1.6) { const g = new THREE.Group(); const m = std(0xe08a8a, { roughness: .5, emissive: 0x401818 });
    for (let i = 0; i < 14; i++) { const u = i / 13; const l = M(new THREE.SphereGeometry(.28 * Math.sin(.2 + u * 2.6), 20, 12), m); l.scale.set(1, .18, .7); l.position.y = (u - .5) * len; g.add(l); }
    const ax = M(new THREE.CylinderGeometry(.04, .04, len, 10), std(0xc06060)); g.add(ax); return g; }
  // akış partikülleri: bir eğri boyunca ilerleyen küreler
  function flow(s, curve, n, c, r = .05) { const arr = Array.from({ length: n }, (_, i) => { const b = M(new THREE.SphereGeometry(r, 12, 8), glow(c, .95)); b.userData.ph = i / n; s.add(b); return b; });
    return (t, sp = .35, col) => arr.forEach(b => { const u = (t * sp + b.userData.ph) % 1; b.position.copy(curve.getPointAt(u)); if (col) b.material.color.copy(col(u)); }); }
  const deepBlue = new THREE.Color(0x24407a), brightBlue = new THREE.Color(0x4fc3ff);

  const S1 = 3.28, S2 = 8.08, S3 = 11.92, S4 = 13.84, S5 = 17.68, S6 = 22.32, S7 = 26.64, S8 = 30.32;

  // 1) Şeffaf ahtapot, içinde 3 kalp sırayla belirip atar; mavi kan damlaları
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a2246', '#010308'], rim: 0xff6a8a, fog: 0x02081a });
    const O = octo(s, { glass: true }); O.position.set(0, 5.15, 0);
    const H = [[V(0, .55, -.1), .24, 0x4f9cff], [V(-.42, .2, -.15), .15, 0x7fd0ff], [V(.42, .2, -.15), .15, 0x7fd0ff]].map(([p, r, c]) => { const h = heart(r, c); h.position.copy(p); O.add(h); return h; });
    const bub = dust(160, [6, 5, 4], 0x8fd8ff, .1, .5); bub.position.set(0, 5, -1); s.add(bub);
    return t => {
      E.d.rotation.y = t * .02; bub.position.y = 5 + (t * .25) % 1; O.pose(t);
      O.rotation.y = Math.sin(t * .5) * .35; O.position.y = 4.7 + Math.sin(t * 1.5) * .08;
      H.forEach((h, i) => { const ap = back(prog(t, .9 + i * .3, .4)); const b = 1 + .22 * Math.max(0, Math.sin(t * 7 + i * 1.3)); h.scale.setScalar(Math.max(.001, ap * b)); });
      cam.position.set(Math.sin(t * .3) * .8, 5.6, lerp(12.2, 11.4, ease(prog(t, 0, S1)))); cam.lookAt(0, 4.9, 0); };
  } });
  // 2) İki solungaç kalbi: kan solungaçtan geçer, koyu maviden parlak maviye döner (oksijen yüklenir)
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a2246', '#010308'], rim: 0x7fd0ff });
    const G = new THREE.Group(); G.position.set(0, 4.85, 0); s.add(G);
    const flows = [-1, 1].map(k => {
      const gl = gill(1.9); gl.position.set(k * 1.45, .1, 0); gl.rotation.z = k * .15; G.add(gl);
      const h = heart(.3, 0x7fd0ff); h.position.set(k * .55, -.55, .2); G.add(h);
      const c = new THREE.CatmullRomCurve3([V(k * .1, -1.4, .3), V(k * .55, -.55, .3), V(k * 1.2, -.9, .35), V(k * 1.55, .1, .35), V(k * 1.3, 1.1, .35), V(k * .4, 1.3, .3)]);
      const tube = M(new THREE.TubeGeometry(c, 60, .07, 10), new THREE.MeshStandardMaterial({ color: 0x9fc8ff, transparent: true, opacity: .25, roughness: .1, depthWrite: false })); G.add(tube);
      return { h, gl, f: flow(G, c, 18, 0x4fc3ff, .065) }; });
    const o2 = Array.from({ length: 14 }, (_, i) => { const b = M(new THREE.SphereGeometry(.07, 12, 8), glow(0xffffff, .8)); b.userData = { k: i % 2 ? 1 : -1, ph: i / 14 }; G.add(b); return b; });
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02;
      flows.forEach(({ h, gl, f }, i) => { h.scale.setScalar(1 + .25 * Math.max(0, Math.sin(t * 7 + i))); gl.children.forEach((l, j) => l.rotation.y = Math.sin(t * 2 + j * .4) * .2);
        f(t, .3, u => deepBlue.clone().lerp(brightBlue, clamp((u - .4) * 3))); });
      o2.forEach(b => { const u = (t * .35 + b.userData.ph) % 1; b.position.set(b.userData.k * (2.4 - u * .9), -.8 + u * 1.8, .4); b.material.opacity = .8 * Math.sin(u * Math.PI); });
      G.rotation.y = Math.sin(t * .4) * .25; G.scale.setScalar(easeOut(prog(a, 0, .5)) * .3 + .7);
      cam.position.set(Math.sin(a * .2) * .6, 5.4, 12.6); cam.lookAt(0, 4.95, 0); };
  } });
  // 3) Büyük ana kalp: oksijenli kanı 8 kola ve gövdeye pompalar
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a2246', '#010308'], rim: 0x4fc3ff });
    const O = octo(s, { glass: true, col: 0xc85a3a }); O.position.set(0, 5.0, 0); O.scale.setScalar(1.05);
    const h = heart(.36, 0x4f9cff); h.position.set(0, .45, 0); O.add(h);
    const fl = O.arms.map((m, i) => { const an = m.userData.an; const c = new THREE.CatmullRomCurve3([V(0, .45, 0), V(Math.cos(an) * .4, -.2, Math.sin(an) * .3), V(Math.cos(an) * 1.0, -.9, Math.sin(an) * .7), V(Math.cos(an) * 1.35, -1.4, Math.sin(an) * .9)]); return flow(O, c, 5, 0x6fd8ff, .05); });
    return t => {
      const a = t - S2; E.d.rotation.y = t * .02; O.pose(t);
      const beat = Math.max(0, Math.sin(t * 6.5)); h.scale.setScalar(1 + .3 * beat); h.g.material.opacity = .5 + .4 * beat;
      fl.forEach(f => f(t, .55)); O.rotation.y = Math.sin(t * .45) * .4;
      cam.position.set(Math.sin(a * .25) * .7, 5.6, lerp(13.2, 12.4, ease(prog(a, 0, S3 - S2)))); cam.lookAt(0, 4.95, 0); };
  } });
  // 4) Peki kan neden mavi? Mavi ve kırmızı kan damlası yan yana döner
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a2246', '#010308'], rim: 0xff6a8a });
    const drop = c => { const g = new THREE.LatheGeometry(Array.from({ length: 40 }, (_, i) => { const th = Math.PI * (1 - i / 39); return new THREE.Vector2(.8 * Math.sin(th) * Math.sin(th / 2), 1.0 * Math.cos(th)); }), 48);
      return M(g, std(c, { roughness: .08, metalness: .2, emissive: c, emissiveIntensity: .25, transparent: true, opacity: .92 })); };
    const blue = drop(0x2f7dff); blue.position.set(-1.0, 4.85, 0); s.add(blue);
    const red = drop(0xd02030); red.position.set(1.0, 4.85, 0); s.add(red);
    const q = qmark(s, 0, 5.75, .7);
    return t => {
      const a = t - S3; E.d.rotation.y = t * .02;
      blue.rotation.y = t * .8; red.rotation.y = -t * .8; blue.position.y = 4.85 + Math.sin(t * 2) * .1; red.position.y = 4.85 + Math.sin(t * 2 + 1) * .1;
      const k = back(prog(a, 0, .5)); blue.scale.setScalar(k * 1.0); red.scale.setScalar(k * .8); q.rotation.y = Math.sin(t * 2) * .5; q.scale.setScalar(.55 * back(prog(a, .3, .4)));
      cam.position.set(Math.sin(a * .3) * .5, 5.5, 12.4); cam.lookAt(0, 5.0, 0); };
  } });
  // 5) Hemosiyanin: bakır atomları oksijen yakalayınca protein maviye döner
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a2246', '#010308'], rim: 0x4fc3ff, keyc: 0xffe8d0 });
    const P = new THREE.Group(); P.position.set(0, 4.75, 0); s.add(P);
    const pm = new THREE.MeshStandardMaterial({ color: 0xbfc8d8, roughness: .35, transparent: true, opacity: .35, depthWrite: false });
    for (let i = 0; i < 26; i++) { const th = r1() * Math.PI * 2, ph = Math.acos(2 * r1() - 1), rr = .9 + r1() * .35; const b = M(new THREE.SphereGeometry(.28 + r1() * .18, 20, 14), pm); b.position.set(Math.sin(ph) * Math.cos(th) * rr, Math.cos(ph) * rr * .9, Math.sin(ph) * Math.sin(th) * rr * .7); P.add(b); }
    const cu = [-1, 1].map(k => { const c = M(new THREE.SphereGeometry(.26, 32, 24), std(0xd9773a, { metalness: .9, roughness: .25, emissive: 0x401800 })); c.position.set(k * .38, 0, .3); P.add(c); return c; });
    const ox = [-1, 1].map(k => { const o = M(new THREE.SphereGeometry(.17, 24, 16), std(0xff3a3a, { emissive: 0x500000, roughness: .3 })); P.add(o); return o; });
    const fe = M(new THREE.SphereGeometry(.22, 24, 16), std(0x8a8a90, { metalness: .9, roughness: .3 })); fe.position.set(-1.9, 5.75, 0); s.add(fe);
    const xm = [0, 1].map(i => { const b = M(new THREE.BoxGeometry(.75, .09, .09), new THREE.MeshBasicMaterial({ color: 0xff3a3a })); b.rotation.z = i ? .78 : -.78; b.position.copy(fe.position); b.position.z = .3; s.add(b); return b; });
    return t => {
      const a = t - S4; E.d.rotation.y = t * .02; P.rotation.y = Math.sin(t * .5) * .5;
      const k = ease(prog(a, 1.2, 1.2)); ox.forEach((o, i) => o.position.set((i ? 1 : -1) * lerp(2.2, .12, k), lerp(1.4, .05, k), .45));
      pm.color.copy(new THREE.Color(0xbfc8d8).lerp(new THREE.Color(0x2f8dff), ease(prog(a, 2.2, 1.0)))); pm.opacity = .35 + .2 * prog(a, 2.2, 1);
      cu.forEach(c => c.scale.setScalar(1 + .1 * Math.sin(t * 5)));
      const fk = back(prog(a, .2, .4)); fe.scale.setScalar(fk); xm.forEach(b => b.scale.setScalar(fk * (a > .5 ? 1 : 0.001))); fe.rotation.y = t;
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 12.6); cam.lookAt(0, 4.95, 0); };
  } });
  // 6) Soğuk, oksijeni az derin su: termometre düşük, seyrek O2 kabarcıkları, kalp hızlı pompalar
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#06183a', '#000206'], rim: 0x4fc3ff, hemi: .6, fog: 0x010a1a, near: 14, far: 40 });
    const O = octo(s, { col: 0xb8502e }); O.position.set(-.5, 4.9, 0); O.scale.setScalar(.85);
    const T = new THREE.Group(); T.position.set(1.85, 5.0, .4); s.add(T);
    const tube = M(new THREE.CapsuleGeometry(.17, 2.0, 8, 24), new THREE.MeshStandardMaterial({ color: 0xdfefff, transparent: true, opacity: .3, roughness: .05, depthWrite: false })); T.add(tube);
    const bulb = M(new THREE.SphereGeometry(.3, 32, 24), std(0x3fa0ff, { emissive: 0x1050a0, emissiveIntensity: .7 })); bulb.position.y = -1.2; T.add(bulb);
    const liq = M(new THREE.CylinderGeometry(.09, .09, 1, 24), std(0x3fa0ff, { emissive: 0x1050a0, emissiveIntensity: .7 })); T.add(liq);
    for (let i = 0; i < 8; i++) { const tk = M(new THREE.BoxGeometry(.16, .025, .02), new THREE.MeshBasicMaterial({ color: 0xffffff })); tk.position.set(.27, -.95 + i * .27, 0); T.add(tk); }
    const ob = Array.from({ length: 6 }, (_, i) => { const b = M(new THREE.SphereGeometry(.08, 14, 10), glow(0xdff4ff, .7)); b.userData.ph = i / 6; b.userData.x = (r1() - .5) * 3.6; s.add(b); return b; });
    const h = heart(.16, 0x4f9cff); h.position.set(0, .55, .9); O.add(h);
    const snowd = dust(200, [6, 5, 3], 0xcfe8ff, .07, .45, false); snowd.position.set(0, 5, 0); s.add(snowd);
    return t => {
      const a = t - S5; E.d.rotation.y = t * .02; O.pose(t); O.rotation.y = Math.sin(t * .4) * .3 + .3; O.position.y = 4.9 + Math.sin(t * 1.3) * .08;
      const hl = lerp(1.6, .45, ease(prog(a, .2, 1.6))); liq.scale.y = hl; liq.position.y = -1.05 + hl / 2;
      ob.forEach(b => { const u = (t * .2 + b.userData.ph) % 1; b.position.set(b.userData.x + Math.sin(u * 8) * .1, 3.2 + u * 3.8, -.5); });
      h.scale.setScalar(1 + .35 * Math.max(0, Math.sin(t * 10))); snowd.position.y = 5 - (t * .1) % 1;
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 12.6); cam.lookAt(0, 4.95, 0); };
  } });
  // 7) Yüzerken: ahtapot jet ile ilerler, ana kalp söner, EKG çizgisi düzleşir
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a2246', '#010308'], rim: 0xff6a8a });
    const O = octo(s, { glass: true, col: 0xc85a3a }); O.scale.setScalar(.75);
    const h = heart(.3, 0x4f9cff); h.position.set(0, .5, 0); O.add(h);
    const ecgM = glow(0x4fffa0, 1); const ecg = M(new THREE.BufferGeometry(), ecgM); s.add(ecg);
    const trail = dust(120, [1.2, 3, 1], 0xbfe8ff, .1, .6); s.add(trail);
    const ekg = x => { const ph = (x % 1 + 1) % 1; return ph > .45 && ph < .5 ? (ph - .45) * 24 : ph >= .5 && ph < .55 ? (.55 - ph) * 24 - .3 * (ph - .5) / .05 : 0; };
    return t => {
      const a = t - S6; E.d.rotation.y = t * .02; const sw = prog(a, 1.4, .3);
      O.pose(t, sw > 0 ? 'jet' : 'float', 1); O.rotation.z = -1.0 * sw; O.position.set(lerp(-.2, .3, sw) - .4 * Math.sin(a * .8) * sw, 5.3 + Math.sin(t * 3) * .05 * sw, 0);
      trail.position.set(O.position.x - 1.3 * sw, O.position.y - .2, -.3); trail.material.opacity = .6 * sw;
      const stop = prog(a, 2.6, .4); const beat = Math.max(0, Math.sin(t * 6.5)) * (1 - stop);
      h.scale.setScalar(1 + .3 * beat); h.m.emissiveIntensity = .45 * (1 - .8 * stop); h.g.material.opacity = .7 * (1 - .85 * stop);
      const P = []; const cut = 2.6; for (let i = 0; i <= 120; i++) { const u = i / 120; const tt = a - (1 - u) * 2.2; P.push(V(-2.0 + u * 4.0, 3.25 + (tt < cut ? ekg(tt * 1.1) * .5 : 0), .5)); }
      ecg.geometry.dispose(); ecg.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(P), 240, .025, 6);
      ecgM.color.set(stop > .5 ? 0xff4040 : 0x4fffa0);
      cam.position.set(Math.sin(a * .2) * .5, 5.4, 12.4); cam.lookAt(0, 4.85, 0); };
  } });
  // 8) Deniz tabanı: ahtapot kayaların üstünde kollarıyla sürünür
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a2246', '#010308'], rim: 0x4fc3ff, hemi: .7, fog: 0x031026, near: 9, far: 26 });
    const floorG = new THREE.PlaneGeometry(30, 20, 80, 50); const fp = floorG.attributes.position; for (let i = 0; i < fp.count; i++) fp.setZ(i, hash(fp.getX(i) * .5, fp.getY(i) * .5, 1) * .25); floorG.computeVertexNormals();
    const floor = M(floorG, std(0x5a4c36, { roughness: .95 })); floor.rotation.x = -Math.PI / 2; floor.position.y = 3.3; s.add(floor);
    const rocks = Array.from({ length: 9 }, () => { const r = M(new THREE.DodecahedronGeometry(.3 + r1() * .5, 2), std(0x5a5a62, { roughness: .9 })); r.position.set((r1() - .5) * 9, 3.35, -1.5 - r1() * 5); r.scale.y = .6; s.add(r); return r; });
    const weeds = Array.from({ length: 10 }, (_, i) => { const w = M(new THREE.CylinderGeometry(.02, .05, 1.4 + r1(), 8, 6), std(0x3a8a5a, { roughness: .6 })); w.position.set((r1() - .5) * 8, 4.0, -2 - r1() * 4); w.userData.ph = r1() * 6; s.add(w); return w; });
    const O = octo(s, { col: 0xc8603a }); O.scale.setScalar(.85);
    return t => {
      const a = t - S7; E.d.rotation.y = t * .02; O.pose(t, 'crawl');
      O.position.set(lerp(-1.2, 1.0, a / (S8 - S7)), 4.15 + Math.abs(Math.sin(t * 2.5)) * .05, 0); O.rotation.y = -.5 + Math.sin(t * .8) * .1;
      weeds.forEach(w => w.rotation.z = Math.sin(t * 1.5 + w.userData.ph) * .15);
      cam.position.set(Math.sin(a * .2) * .4, 6.0, 11.8); cam.lookAt(0, 4.7, 0); };
  } });
  // 9) Sıradaki soru: Mıknatıs nasıl çeker? Nal mıknatıs ataşları ve demir bilyeleri çeker
  shots.push({ t0: S8, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a1a3a', '#010308'], rim: 0xff4a4a });
    const Mg = new THREE.Group(); Mg.position.set(0, 5.45, 0); Mg.scale.setScalar(.9); s.add(Mg);
    const red = std(0xd42a2a, { roughness: .35, metalness: .3 }), sil = std(0xdfe4ea, { roughness: .2, metalness: .9 });
    const arc = M(new THREE.TorusGeometry(.8, .28, 32, 64, Math.PI), red); Mg.add(arc);
    [-1, 1].forEach(k => { const leg = M(new THREE.CylinderGeometry(.28, .28, .7, 32), red); leg.position.set(k * .8, -.35, 0); Mg.add(leg);
      const tip = M(new THREE.CylinderGeometry(.28, .28, .3, 32), sil); tip.position.set(k * .8, -.85, 0); Mg.add(tip); });
    const lines = Array.from({ length: 6 }, (_, i) => { const r = .25 + i * .14; const c = new THREE.CatmullRomCurve3(Array.from({ length: 21 }, (_, j) => { const an = Math.PI + j / 20 * Math.PI; return V(Math.cos(an) * (.8 + r) * (j % 20 === 0 ? 1 : 1), -1.0 + Math.sin(an) * r * 1.4, 0); }));
      const m = M(new THREE.TubeGeometry(c, 40, .012, 6), glow(0x7ee0ff, .5)); Mg.add(m); return m; });
    const clips = Array.from({ length: 7 }, (_, i) => { const g = new THREE.Group(); const cm = std(0xc8ccd4, { metalness: .9, roughness: .25 });
      const t1 = M(new THREE.TorusGeometry(.12, .025, 8, 24), cm); t1.scale.set(1, 2.2, 1); g.add(t1); g.userData = { x: (r1() - .5) * 3.6, z: (r1() - .5) * 1.0, d: .3 + i * .18, tx: (i % 2 ? 1 : -1) * .8 + (r1() - .5) * .3, ty: -1.15 - (i >> 1) * .22 }; s.add(g); return g; });
    const q = qmark(s, 2.05, 6.0, .55);
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02; Mg.rotation.y = Math.sin(t * .6) * .35;
      lines.forEach((m, i) => m.material.opacity = .25 + .3 * Math.sin(t * 3 - i * .6) ** 2);
      clips.forEach(g => { const k = ease(prog(a, g.userData.d, .7)); g.position.set(lerp(g.userData.x, g.userData.tx * .9, k), lerp(3.4, 5.45 + g.userData.ty * .9, k), lerp(g.userData.z, 0, k)); g.rotation.set(t + g.userData.x, (1 - k) * t * 2, (1 - k) * 2); });
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * .8, 5.7, 12.6); cam.lookAt(0, 5.0, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:300px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('KANI DA MAVİ', 'AHTAPOTUN<br><span class="y">3 KALBİ</span> VAR', 110) },
    { t0: S1, t1: S2, html: BIG('SOLUNGAÇ KALPLERİ', 'k2', 'KANA OKSİJEN YÜKLER', '2') },
    { t0: S2, t1: S3, html: T('1 ANA KALP', 'KANI <span class="y">TÜM VÜCUDA</span><br>POMPALAR', 100) },
    { t0: S3, t1: S4, html: T('PEKİ', 'KAN NEDEN<br><span class="y">MAVİ?</span>', 120) },
    { t0: S4, t1: S5, html: T('DEMİR DEĞİL', '<span class="y">BAKIR</span> TAŞIR<br><span style="font-size:64px">HEMOSİYANİN</span>', 120) },
    { t0: S5, t1: S6, html: T('SOĞUK VE OKSİJENİ AZ SU', 'AMA <span class="y">GÜÇLÜ POMPA</span><br>İSTER', 100) },
    { t0: S6, t1: S7, html: T('YÜZERKEN', 'ANA KALP<br><span class="y">DURUYOR</span>', 116) },
    { t0: S7, t1: S8, html: T('BU YÜZDEN', 'YÜZMEK YERİNE<br><span class="y">SÜRÜNÜR</span>', 104) },
    { t0: S8, t1: 99, html: T('SIRADAKİ SORU', 'MIKNATIS<br><span class="y">NASIL</span> ÇEKER?', 108) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k2', S1]];
  return {
    END: 34.76, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; }); },
    follow: { t: 32.96, click: 33.9 },
    sfx: [[.3, 'whoosh', .5], [.9, 'pop', .4], [1.2, 'pop', .4], [1.5, 'pop', .4], [S1 + .2, 'pop_low', .5], [S2 + .3, 'boom', .4], [S3 + .2, 'pop', .5],
      [S4 + .3, 'ding', .3], [S4 + 2.3, 'ding', .4], [S5 + .4, 'crunch', .3], [S6 + 1.4, 'whoosh', .5], [S6 + 2.6, 'snap', .4], [S7 + .3, 'pop_low', .4],
      [S8 + .3, 'whoosh', .5], [S8 + .6, 'snap', .4], [S8 + .9, 'snap', .35], [S8 + 1.2, 'snap', .3]],
  };
};
