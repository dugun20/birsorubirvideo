// Bilgi #24: Ay neden Dünya'ya düşmez? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Wikipedia "Orbit of the Moon" (ortalama yörünge hızı 1,022 km/s ≈ 3.680 km/sa; ortalama uzaklık ~385.000 km; yıldız ayı
// 27,32 gün). Techno-Science "Why doesn't the Moon crash into the Earth?" (Dünya'nın çekimi Ay'ı çeker ama Ay ileri gitmeye devam ettiği
// için her an Dünya'yı ıskalar, sürekli serbest düşüştedir; hız ~3.700 km/sa). RocketStem / NASA (Ay her yıl ~3,8 cm uzaklaşıyor).
// Newton'un güllesi: Principia, "A Treatise of the System of the World" (yüksek dağdan yeterince hızlı atılan gülle yere düşmeden dolanır).
export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const M = (g, m) => new THREE.Mesh(g, m);
  const V = (x, y, z = 0) => new THREE.Vector3(x, y, z);
  let seed = 2424; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
    s.background = gradTex(...(o.bg || ['#0a1430', '#010208'])); s.fog = new THREE.Fog(o.fog || 0x02050e, o.near || 30, o.far || 110);
    const hemi = new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi ?? .7); s.add(hemi);
    const key = new THREE.DirectionalLight(o.keyc || 0xfff4e0, o.key ?? 2.4); key.position.set(...(o.kp || [-10, 8, 10])); s.add(key);
    const rim = new THREE.PointLight(o.rim || 0x4fc3ff, 600, 60); rim.position.set(6, 9, -5); s.add(rim);
    const d = dust(700, [30, 22, 16], o.dust || 0xdfeaff, .1, .55); d.position.y = 5; s.add(d);
    return { d, rim, key, hemi };
  }
  const glow = (c, op = .9) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false });
  const halo = (c, sc, op = .5) => { const h = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false })); h.scale.setScalar(sc); return h; };
  function qmark(s, x, y, sc = 1) { const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); q.position.set(x, y, .5); q.scale.setScalar(sc); s.add(q);
    const qa = M(new THREE.TorusGeometry(.42, .1, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.12, 12, 8), qm); qd.position.set(-.08, -.72, 0); q.add(qd); return q; }
  function label(w = 512, h = 128, col = '#ffcf2e', px = 92) { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
    const spr = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false })); let last = null;
    spr.set = txt => { if (txt === last) return; last = txt; g.clearRect(0, 0, w, h); g.font = `bold ${px}px Osw, Oswald, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
      g.lineWidth = 10; g.strokeStyle = 'rgba(0,0,0,.6)'; g.strokeText(txt, w / 2, h / 2 + 4); g.fillStyle = col; g.fillText(txt, w / 2, h / 2 + 4); tex.needsUpdate = true; };
    return spr; }
  const earthTex = (() => { const c = document.createElement('canvas'); c.width = 1024; c.height = 512; const g = c.getContext('2d'); g.fillStyle = '#1b4a92'; g.fillRect(0, 0, 1024, 512);
    g.fillStyle = '#3d8a46'; for (let i = 0; i < 40; i++) { g.beginPath(); g.ellipse(r1() * 1024, 90 + r1() * 330, 30 + r1() * 90, 20 + r1() * 55, r1() * 3, 0, Math.PI * 2); g.fill(); }
    g.fillStyle = '#c8b27a'; for (let i = 0; i < 10; i++) { g.beginPath(); g.ellipse(r1() * 1024, 180 + r1() * 150, 20 + r1() * 40, 10 + r1() * 20, r1() * 3, 0, Math.PI * 2); g.fill(); }
    g.fillStyle = '#eef4ff'; g.fillRect(0, 0, 1024, 26); g.fillRect(0, 486, 1024, 26);
    g.fillStyle = 'rgba(255,255,255,.5)'; for (let i = 0; i < 60; i++) { g.beginPath(); g.ellipse(r1() * 1024, r1() * 512, 30 + r1() * 70, 5 + r1() * 9, r1() * .4, 0, Math.PI * 2); g.fill(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
  const moonTex = (() => { const c = document.createElement('canvas'); c.width = 512; c.height = 256; const g = c.getContext('2d'); g.fillStyle = '#bdbdbd'; g.fillRect(0, 0, 512, 256);
    for (let i = 0; i < 14; i++) { g.fillStyle = `rgba(90,90,95,${.25 + r1() * .3})`; g.beginPath(); g.ellipse(r1() * 512, r1() * 256, 20 + r1() * 50, 15 + r1() * 35, r1() * 3, 0, Math.PI * 2); g.fill(); }
    for (let i = 0; i < 90; i++) { g.fillStyle = `rgba(70,70,70,${.2 + r1() * .4})`; g.beginPath(); g.arc(r1() * 512, r1() * 256, 2 + r1() * 9, 0, Math.PI * 2); g.fill(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
  function earth(s, r, x, y) { const e = M(new THREE.SphereGeometry(r, 64, 48), new THREE.MeshStandardMaterial({ map: earthTex, roughness: .55, metalness: .05 })); e.position.set(x, y, 0); e.rotation.z = .4; s.add(e);
    const a = halo(0x4fa8ff, r * 3.0, .45); a.position.set(x, y, -.2); s.add(a); return e; }
  function moon(s, r) { const m = M(new THREE.SphereGeometry(r, 48, 32), new THREE.MeshStandardMaterial({ map: moonTex, roughness: .95 })); s.add(m); return m; }
  function arrow(col, len = 1, th = .07) { const g = new THREE.Group(); const mat = std(col, { emissive: col, emissiveIntensity: .5, roughness: .3 });
    const sh = M(new THREE.CylinderGeometry(th, th, 1, 16), mat); g.add(sh); const hd = M(new THREE.ConeGeometry(th * 2.6, th * 5, 20), mat); g.add(hd);
    g.setLen = l => { sh.scale.y = Math.max(.001, l); sh.position.y = l / 2; hd.position.y = l + th * 2.5; hd.visible = l > .05; }; g.setLen(len); return g; }
  const pointArrow = (a, from, dir) => { a.position.copy(from); a.quaternion.setFromUnitVectors(V(0, 1, 0), dir.clone().normalize()); };
  const trail = (pts, col, r = .025) => { const m = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), Math.max(8, pts.length * 2), r, 8), glow(col, .85)); m.geometry.setDrawRange(0, 0); m.reveal = k => m.geometry.setDrawRange(0, Math.floor(m.geometry.index.count * clamp(k) / 6) * 6); return m; };

  const S1 = 4.4, S2 = 8.03, S3 = 11.16, S4 = 15.68, S5 = 19.36, S6 = 22.16, S7 = 26.88, S8 = 29.6, S9 = 33.28;

  // 1) Kanca: Ay Dünya'ya doğru düşüyor gibi yaklaşır, sonra yana kayar
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s); const e = earth(s, 1.25, 0, 3.75); const m = moon(s, .42);
    const q = qmark(s, -1.8, 6.1, .5); const fall = arrow(0xff5a4a, .8); s.add(fall);
    return t => { E.d.rotation.y = t * .02; e.rotation.y = t * .25;
      const k = ease(prog(t, .2, 2.0)); const sw = ease(prog(t, 2.4, 1.6)); m.position.set(lerp(.5, 1.0, k) + sw * .45, lerp(6.4, 5.5, k) - sw * .3, .4); m.rotation.y = t * .3;
      pointArrow(fall, m.position.clone().add(V(0, -.5, 0)), V(0, -1, 0)); fall.setLen(.6 + .2 * Math.sin(t * 6)); fall.visible = t > .3;
      q.scale.setScalar(.5 * Math.max(.001, back(prog(t, 2.5, .5)))); q.rotation.y = Math.sin(t * 2) * .4;
      cam.position.set(Math.sin(t * .3) * .5, 5.2, lerp(13.4, 12.4, ease(prog(t, 0, S1)))); cam.lookAt(0, 4.8, 0); };
  } });
  // 2) 385.000 km: Dünya solda, Ay sağda, aradaki çizgi uzar, sayaç döner
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s); const e = earth(s, .75, -1.55, 4.3); const m = moon(s, .22); m.position.set(1.85, 5.6, 0);
    const line = trail([V(-.8, 4.55, .2), V(.5, 5.15, .2), V(1.62, 5.55, .2)], 0x7ee0ff, .02); s.add(line);
    const lb = label(640, 140); lb.scale.set(2.9, .64, 1); lb.position.set(.15, 6.2, .6); s.add(lb);
    const marks = Array.from({ length: 9 }, (_, i) => { const d = M(new THREE.SphereGeometry(.04, 12, 8), glow(0xffcf2e, .9)); const u = i / 8; d.position.set(lerp(-.8, 1.62, u), lerp(4.55, 5.55, u) + Math.sin(u * Math.PI) * .12, .25); s.add(d); return d; });
    return t => { const a = t - S1; E.d.rotation.y = t * .02; e.rotation.y = t * .25; m.rotation.y = t * .2;
      const k = ease(prog(a, .3, 1.8)); line.reveal(k); marks.forEach((d, i) => d.visible = k >= i / 8);
      lb.set(Math.round(385 * k).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '.000 KM'); if (k < .003) lb.set('0 KM');
      lb.material.opacity = ease(prog(a, .3, .3));
      cam.position.set(Math.sin(a * .25) * .7, 5.3, 12.4); cam.lookAt(0, 4.85, 0); };
  } });
  // 3) Çekim kuvveti: Ay'dan Dünya'ya kırmızı ok, kütle çekim halkaları içe doğru akar
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff6a4a }); const e = earth(s, 1.1, -.6, 4.2); const m = moon(s, .35); m.position.set(1.6, 5.7, 0);
    const rings = Array.from({ length: 4 }, (_, i) => { const r = M(new THREE.TorusGeometry(1, .02, 8, 96), glow(0xff8a5a, .5)); r.position.copy(e.position); s.add(r); return r; });
    const ar = arrow(0xff5a4a, 1, .09); s.add(ar);
    return t => { const a = t - S2; E.d.rotation.y = t * .02; e.rotation.y = t * .25; m.rotation.y = t * .2;
      rings.forEach((r, i) => { const u = 1 - ((a * .4 + i / 4) % 1); r.scale.setScalar(1.25 + u * 1.5); r.material.opacity = .5 * Math.sin(u * Math.PI) * ease(prog(a, .2, .6)); });
      const dir = e.position.clone().sub(m.position); const L0 = dir.length() - 1.1 - .35 - .35; pointArrow(ar, m.position.clone().add(dir.clone().normalize().multiplyScalar(.4)), dir);
      ar.setLen(Math.max(.001, L0 * easeOut(prog(a, .6, .7)) * (1 + .04 * Math.sin(t * 8))));
      m.position.set(1.6 - .06 * Math.sin(t * 3), 5.7 - .06 * Math.sin(t * 3), 0);
      cam.position.set(Math.sin(a * .25) * .6, 5.3, 12.2); cam.lookAt(0, 4.85, 0); };
  } });
  // 4) Yana doğru hız: Ay sarı hız oku ve hız çizgileriyle yana kayar
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffcf2e }); const m = moon(s, .75); m.position.set(-.2, 4.8, 0);
    const ar = arrow(0xffcf2e, 1.6, .1); ar.rotation.z = -Math.PI / 2; s.add(ar);
    const lines = Array.from({ length: 12 }, (_, i) => { const l = M(new THREE.CylinderGeometry(.015, .015, 1, 6), glow(0xcfe8ff, .6)); l.rotation.z = Math.PI / 2; l.userData = { y: 4.8 + (r1() - .5) * 1.6, ph: r1(), len: .6 + r1() * 1.2, z: (r1() - .5) * 1.2 }; s.add(l); return l; });
    const lb = label(640, 140); lb.scale.set(2.9, .64, 1); lb.position.set(0, 3.45, .8); s.add(lb); lb.set('3.700 KM/SA');
    return t => { const a = t - S3; E.d.rotation.y = t * .02; m.rotation.y = t * .5; m.position.y = 4.8 + Math.sin(t * 1.3) * .05;
      ar.position.set(m.position.x + .85, m.position.y, .3); ar.setLen(1.2 * easeOut(prog(a, .4, .6)));
      lines.forEach(l => { const u = (a * 1.2 + l.userData.ph) % 1; l.position.set(lerp(1.0, -3.4, u), l.userData.y, l.userData.z); l.scale.y = l.userData.len; l.material.opacity = .6 * Math.sin(u * Math.PI) * ease(prog(a, .2, .5)); });
      lb.material.opacity = ease(prog(a, 1.3, .4)); lb.scale.set(2.9 * (.85 + .15 * back(prog(a, 1.3, .5))), .64, 1);
      cam.position.set(Math.sin(a * .25) * .5, 5.3, 12.0); cam.lookAt(0, 4.85, 0); };
  } });
  // 5) İkisi birlikte: Ay düşer ama ileri gittiği için yörünge çizer, hep ıskalar
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s); const e = earth(s, .7, 0, 4.7); const m = moon(s, .26);
    const RX = 1.75, RY = 1.4, CY = 4.7; const pts = Array.from({ length: 121 }, (_, i) => { const u = i / 120 * Math.PI * 2; return V(RX * Math.sin(u), CY + RY * Math.cos(u), .1); });
    const tr = trail(pts, 0x7ee0ff, .02); s.add(tr);
    const g = arrow(0xff5a4a, .6, .06), v = arrow(0xffcf2e, .8, .06); s.add(g, v);
    return t => { const a = t - S4; E.d.rotation.y = t * .02; e.rotation.y = t * .25;
      const u = a / 3.5 * Math.PI * 2 * .9; const p = V(RX * Math.sin(u), CY + RY * Math.cos(u), .3); m.position.copy(p); m.rotation.y = t;
      tr.reveal(u / (Math.PI * 2));
      const toE = e.position.clone().sub(p).normalize(); pointArrow(g, p.clone().add(toE.clone().multiplyScalar(.32)), toE); g.setLen(.55);
      const vel = V(RX * Math.cos(u), -RY * Math.sin(u), 0).normalize(); pointArrow(v, p.clone().add(vel.clone().multiplyScalar(.32)), vel); v.setLen(.7);
      cam.position.set(Math.sin(a * .25) * .5, 5.1, 12.4); cam.lookAt(0, 4.75, 0); };
  } });
  // Newton'un güllesi: dağ tepesinden atılan gülle yörüngeleri (2B kütle çekimiyle sayısal hesap)
  const R0 = 1.15, EC = V(0, 4.35, 0), H0 = R0 + .42;
  function path(v0) { const pts = []; let x = 0, y = H0, vx = v0, vy = 0; const GM = 1 * H0; const dt = .01;
    for (let i = 0; i < 2000; i++) { const r = Math.hypot(x, y); if (r < R0 + .05) break; const aa = -GM / (r * r); vx += aa * x / r * dt; vy += aa * y / r * dt; x += vx * dt; y += vy * dt;
      if (i % 4 === 0) pts.push(V(x, y + EC.y, .15)); if (i > 50 && Math.hypot(x, y - H0) < .05) break; } return pts; }
  function newtonScene(s) { const e = earth(s, R0, 0, EC.y);
    const mt = M(new THREE.ConeGeometry(.32, .5, 32), std(0x7a6a58, { roughness: .9 })); mt.position.set(0, EC.y + R0 + .15, 0); s.add(mt);
    const snow = M(new THREE.ConeGeometry(.12, .18, 24), std(0xffffff, { roughness: .6 })); snow.position.set(0, EC.y + R0 + .33, 0); s.add(snow);
    const can = M(new THREE.CylinderGeometry(.06, .08, .32, 20), std(0x3a3a3a, { metalness: .8, roughness: .3 })); can.rotation.z = -Math.PI / 2; can.position.set(.05, EC.y + H0 - .02, 0); s.add(can);
    return e; }
  const ball = s => { const b = M(new THREE.SphereGeometry(.07, 20, 14), std(0x222222, { metalness: .8, roughness: .3 })); s.add(b); const h = halo(0xffb060, .5, .8); b.add(h); return b; };
  // 6) Yavaş gülleler yere düşer
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s); const e = newtonScene(s);
    const P = [.45, .65].map(v => { const pts = path(v); const tr = trail(pts, 0xffcf2e, .022); s.add(tr); return { pts, tr, b: ball(s) }; });
    return t => { const a = t - S5; E.d.rotation.y = t * .02; e.rotation.y = t * .1;
      P.forEach((p, i) => { const k = prog(a, .3 + i * 1.1, .9); p.tr.reveal(k); const j = Math.min(p.pts.length - 1, Math.floor(k * (p.pts.length - 1))); p.b.position.copy(p.pts[j]); p.b.visible = k > 0; });
      cam.position.set(Math.sin(a * .25) * .4, 5.3, 12.4); cam.lookAt(0, 4.75, 0); };
  } });
  // 7) Hızlandıkça daha uzağa; yeterince hızlı olunca yere hiç değmeden tam tur
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s); const e = newtonScene(s);
    const P = [.45, .65, .85, 1.0].map((v, i) => { const pts = path(v); const tr = trail(pts, i === 3 ? 0x7ee0ff : 0xffcf2e, i === 3 ? .03 : .018); s.add(tr); return { pts, tr, b: ball(s) }; });
    return t => { const a = t - S6; E.d.rotation.y = t * .02; e.rotation.y = t * .1;
      P.forEach((p, i) => { const st = i < 2 ? -1 : (i === 2 ? .2 : 1.3); const du = i === 3 ? 3.0 : 1.0; const k = i < 2 ? 1 : prog(a, st, du);
        p.tr.reveal(k); if (i < 2) p.tr.material.opacity = .35; const j = Math.min(p.pts.length - 1, Math.floor(k * (p.pts.length - 1))); p.b.position.copy(p.pts[j]); p.b.visible = i >= 2 && k > 0; });
      cam.position.set(Math.sin(a * .25) * .4, 5.3, 12.4); cam.lookAt(0, 4.75, 0); };
  } });
  // 8) 27 günde bir tur: gün sayacı
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s); const e = earth(s, .8, 0, 4.6); const m = moon(s, .26);
    const orb = M(new THREE.TorusGeometry(1, .012, 6, 160), glow(0x7ee0ff, .45)); orb.position.set(0, 4.6, 0); orb.scale.set(2.05, 1.5, 1); s.add(orb);
    const ticks = Array.from({ length: 27 }, (_, i) => { const u = i / 27 * Math.PI * 2; const d = M(new THREE.SphereGeometry(.035, 10, 8), glow(0xffcf2e, .9)); d.position.set(2.05 * Math.sin(u), 4.6 + 1.5 * Math.cos(u), .1); s.add(d); return d; });
    const lb = label(512, 160, '#ffcf2e', 120); lb.scale.set(1.9, .6, 1); lb.position.set(0, 4.6, 1.4); s.add(lb);
    return t => { const a = t - S7; E.d.rotation.y = t * .02; e.rotation.y = t * 2.5;
      const k = ease(prog(a, .2, 2.2)); const u = k * Math.PI * 2; m.position.set(2.05 * Math.sin(u), 4.6 + 1.5 * Math.cos(u), .3); m.rotation.y = u;
      ticks.forEach((d, i) => d.visible = k * 27 >= i); lb.set(Math.round(k * 27) + '. GÜN');
      cam.position.set(Math.sin(a * .25) * .5, 5.2, 12.2); cam.lookAt(0, 4.7, 0); };
  } });
  // 9) Her yıl 3,8 cm uzaklaşıyor: Ay dışarı kayar, cetvel
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    const E = lights(s); const e = earth(s, .9, -1.4, 4.7); const m = moon(s, .3);
    const o1 = M(new THREE.TorusGeometry(1, .012, 6, 160), glow(0x7ee0ff, .35)); o1.position.set(-1.4, 4.7, 0); o1.scale.set(2.5, 2.5 * .55, 1); s.add(o1);
    const o2 = M(new THREE.TorusGeometry(1, .016, 6, 160), glow(0xffcf2e, .0)); o2.position.copy(o1.position); s.add(o2);
    const ruler = new THREE.Group(); ruler.position.set(1.3, 3.75, .5); s.add(ruler);
    const rb = M(new THREE.BoxGeometry(1.3, .22, .05), std(0xe8c860, { roughness: .4 })); ruler.add(rb);
    for (let i = 0; i <= 10; i++) { const tk = M(new THREE.BoxGeometry(.012, i % 5 ? .07 : .13, .02), std(0x222222)); tk.position.set(-.6 + i * .12, .11 - (i % 5 ? .035 : .065), .04); ruler.add(tk); }
    const lb = label(640, 140); lb.scale.set(2.6, .57, 1); lb.position.set(.4, 3.4, .8); s.add(lb); lb.set('3,8 CM / YIL');
    return t => { const a = t - S8; E.d.rotation.y = t * .02; e.rotation.y = t * .25;
      const k = ease(prog(a, .4, 2.4)); const R = 2.5 + .45 * k; const u = .9 + a * .12; m.position.set(-1.4 + R * Math.sin(u), 4.7 + R * Math.cos(u) * .55, .3); m.rotation.y = t * .3;
      o2.scale.set(R, R * .55, 1); o2.material.opacity = .6 * k; ruler.rotation.y = Math.sin(t * .8) * .25;
      lb.material.opacity = ease(prog(a, 1.0, .4));
      cam.position.set(Math.sin(a * .25) * .4, 5.2, 12.4); cam.lookAt(0, 4.75, 0); };
  } });
  // 10) Sıradaki soru: Buz neden suda yüzer? Bardakta yüzen buz küpü
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1e3a', '#010308'], rim: 0x7ee0ff });
    const G = new THREE.Group(); G.position.set(0, 4.3, 0); s.add(G);
    const glass = M(new THREE.CylinderGeometry(1.2, 1.0, 2.6, 64, 1, true), new THREE.MeshStandardMaterial({ color: 0xcfe8ff, transparent: true, opacity: .18, roughness: .05, metalness: .1, side: THREE.DoubleSide, depthWrite: false })); G.add(glass);
    const bottom = M(new THREE.CylinderGeometry(1.0, 1.0, .12, 64), new THREE.MeshStandardMaterial({ color: 0xcfe8ff, transparent: true, opacity: .3, roughness: .05 })); bottom.position.y = -1.3; G.add(bottom);
    const water = M(new THREE.CylinderGeometry(1.12, 1.0, 1.9, 64), new THREE.MeshStandardMaterial({ color: 0x2f7dd8, transparent: true, opacity: .45, roughness: .1, depthWrite: false })); water.position.y = -.33; G.add(water);
    const surf = M(new THREE.CircleGeometry(1.12, 64), new THREE.MeshStandardMaterial({ color: 0x7ec0ff, transparent: true, opacity: .5, roughness: .05, side: THREE.DoubleSide, depthWrite: false })); surf.rotation.x = -Math.PI / 2; surf.position.y = .62; G.add(surf);
    const iceM = new THREE.MeshStandardMaterial({ color: 0xe8f6ff, transparent: true, opacity: .8, roughness: .08, metalness: .05, emissive: 0x0a2040 });
    const cubes = [[-.35, .1, .2], [.4, -.1, -.2]].map(([x, z, r]) => { const c = M(new THREE.BoxGeometry(.62, .62, .62, 4, 4, 4), iceM); c.position.set(x, .62, z); c.rotation.y = r; G.add(c); return c; });
    const bub = dust(50, [1.8, 1.6, 1.6], 0xcfe8ff, .08, .7); bub.position.y = -.4; G.add(bub);
    const q = qmark(s, 1.75, 6.05, .45);
    return t => { const a = t - S9; E.d.rotation.y = t * .02; G.rotation.y = Math.sin(t * .4) * .3;
      cubes.forEach((c, i) => { const drop = clamp(1 - easeOut(prog(a, .2 + i * .25, .7))); c.position.y = .4 + drop * 1.6 + Math.sin(t * 2 + i) * .03; c.rotation.x = Math.sin(t * 1.5 + i) * .06; });
      bub.rotation.y = t * .2; bub.position.y = -.4 + ((t * .3) % .4); q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 12.4); cam.lookAt(0, 4.75, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('AY ASLINDA', 'HER AN<br><span class="y">DÜŞÜYOR!</span>', 120) },
    { t0: S1, t1: S2, html: T('ORTALAMA UZAKLIK', '<span class="y">385.000</span><br>KİLOMETRE', 116) },
    { t0: S2, t1: S3, html: T('DÜNYA\'NIN ÇEKİMİ', 'AY\'I SÜREKLİ<br><span class="y">ÇEKİYOR</span>', 108) },
    { t0: S3, t1: S4, html: T('AMA AY', 'YANA DOĞRU<br><span class="y">UÇUYOR</span>', 116) },
    { t0: S4, t1: S5, html: T('SONUÇ', 'DÜNYA\'YI HER AN<br><span class="y">ISKALIYOR</span>', 100) },
    { t0: S5, t1: S6, html: T('NEWTON\'UN GÜLLESİ', 'YAVAŞ ATARSAN<br><span class="y">YERE DÜŞER</span>', 100) },
    { t0: S6, t1: S7, html: T('YETERİNCE HIZLIYSA', 'YERE HİÇ<br><span class="y">DEĞMEZ</span>', 116) },
    { t0: S7, t1: S8, html: T('BİR TUR', 'YAKLAŞIK<br><span class="y">27 GÜN</span>', 120) },
    { t0: S8, t1: S9, html: T('ÜSTELİK', 'AY BİZDEN<br><span class="y">UZAKLAŞIYOR</span>', 108) },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'BUZ NEDEN<br><span class="y">SUDA YÜZER?</span>', 108) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 37.96, shots, titles,
    update: () => {},
    follow: { t: 36.08, click: 37.02 },
    sfx: [[.3, 'whoosh', .5], [2.5, 'whoosh', .4], [2.6, 'pop', .35], [S1 + .3, 'click', .3], [S1 + 2.1, 'ding', .35], [S2 + .6, 'pop_low', .45],
      [S3 + .4, 'whoosh', .5], [S3 + 1.3, 'pop', .4], [S4 + .4, 'whoosh', .3], [S5 + .3, 'boom', .3], [S5 + 1.2, 'crunch', .4], [S5 + 1.4, 'boom', .3], [S5 + 2.3, 'crunch', .4],
      [S6 + .2, 'boom', .3], [S6 + 1.3, 'boom', .35], [S6 + 4.3, 'ding', .4], [S7 + 2.4, 'ding', .35], [S8 + 1.0, 'pop', .4], [S9 + .4, 'whoosh', .4], [S9 + .9, 'pop_low', .5]],
  };
};
