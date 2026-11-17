// Bilgi #19: Gökkuşağı nasıl oluşur? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Met Office "How are rainbows formed?" (ışık damlaya girerken kırılır ve renklere ayrılır, mavi/mor kırmızıdan biraz daha fazla bükülür;
// damlanın arka iç yüzeyinden yansır, çıkarken tekrar kırılır; Güneş izleyicinin arkasında, damlalar önünde olmalı; düz zeminde yay görünür).
// Avustralya Meteoroloji Bürosu (BoM) "Ask BoM: How do rainbows form?" (Güneş–damla–izleyici açısı 42°; kırmızı 42°, yeşil 41°, mor 40°;
// ikinci gökkuşağı damlada bir kez daha yansıyan ışıktan oluşur, renk sırası terstir, daha soluktur; havadan bakınca zemin alt yarıyı kesmez).
// Not: damla içi ışın yolları gerçek kırılma hesabıyla çizilir; görünür olsun diye renkler arası kırılma farkı büyütülmüştür.
export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std } = L;
  const shots = [];
  const M = (g, m) => new THREE.Mesh(g, m);
  const V = (x, y, z = 0) => new THREE.Vector3(x, y, z);
  let seed = 1919; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
  function qmark(s, x, y, sc = 1) { const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); q.position.set(x, y, .5); q.scale.setScalar(sc); s.add(q);
    const qa = M(new THREE.TorusGeometry(.42, .1, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.12, 12, 8), qm); qd.position.set(-.08, -.72, 0); q.add(qd); return q; }
  function person(body = 0x2a3550) { const g = new THREE.Group();
    g.add(M(new THREE.CapsuleGeometry(.3, .55, 8, 16), std(body, { roughness: .7 })));
    const head = M(new THREE.SphereGeometry(.26, 24, 16), std(0xd9b49a, { roughness: .6 })); head.position.y = .72; g.add(head); g.head = head; return g; }
  const COLS = [0xff3b30, 0xff9500, 0xffcc00, 0x34c759, 0x32ade6, 0x3a5aff, 0xaf52de];
  // gökkuşağı yayı: 7 renk, dıştan içe kırmızı → mor (rev: ikinci gökkuşağı)
  function bow(s, R, w, arc = Math.PI, op = .8, rev = false) { const g = new THREE.Group(); s.add(g);
    g.rings = COLS.map((c, i) => { const m = M(new THREE.TorusGeometry(R - (rev ? 6 - i : i) * w, w * .62, 10, 160, arc), glow(c, op)); g.add(m); m.userData.R = R - (rev ? 6 - i : i) * w; return m; });
    g.set = (k, a0 = Math.PI) => g.rings.forEach(m => { m.geometry.dispose(); m.geometry = new THREE.TorusGeometry(m.userData.R, w * .62, 10, 160, Math.max(.01, a0 * k)); });
    return g; }
  // parçalı çizgi tüpü (kısmi çizim)
  function poly(pts, u) { const L0 = []; let tot = 0; for (let i = 1; i < pts.length; i++) { const d = pts[i].distanceTo(pts[i - 1]); L0.push(d); tot += d; }
    let rem = tot * clamp(u); const out = [pts[0].clone()];
    for (let i = 1; i < pts.length && rem > 1e-4; i++) { const d = L0[i - 1]; if (rem >= d) { out.push(pts[i].clone()); rem -= d; } else { out.push(pts[i - 1].clone().lerp(pts[i], rem / d)); rem = 0; } }
    return out.length > 1 ? out : [pts[0].clone(), pts[0].clone().add(V(.001, 0))]; }
  function ray(c, r = .035, op = .95) { const m = M(new THREE.BufferGeometry(), glow(c, op)); m.r = r;
    m.set = P => { m.geometry.dispose(); const cp = new THREE.CurvePath(); for (let i = 1; i < P.length; i++) cp.add(new THREE.LineCurve3(P[i - 1], P[i])); m.geometry = new THREE.TubeGeometry(cp, 24 * (P.length - 1), m.r, 6); };
    return m; }
  // damlada gerçek kırılma–yansıma–kırılma hesabı (2B, z=0)
  function refr(d, n, eta) { const ci = -n.dot(d); const k = 1 - eta * eta * (1 - ci * ci); return d.clone().multiplyScalar(eta).add(n.clone().multiplyScalar(eta * ci - Math.sqrt(Math.max(0, k)))).normalize(); }
  function trace(c, R, b, nw, lenIn = 3, lenOut = 1.8) {
    const y = c.y + b * R; const P1 = V(c.x - Math.sqrt(R * R - b * b * R * R), y); const P0 = V(P1.x - lenIn, y); const d0 = V(1, 0);
    const N1 = P1.clone().sub(c).divideScalar(R); const d1 = refr(d0, N1, 1 / nw);
    const P2 = P1.clone().addScaledVector(d1, -2 * P1.clone().sub(c).dot(d1)); const N2 = P2.clone().sub(c).divideScalar(R);
    const d2 = d1.clone().addScaledVector(N2, -2 * d1.dot(N2)); const P3 = P2.clone().addScaledVector(d2, -2 * P2.clone().sub(c).dot(d2));
    const N3 = P3.clone().sub(c).divideScalar(R); const d3 = refr(d2, N3.clone().negate(), nw); const P4 = P3.clone().addScaledVector(d3, lenOut);
    return [P0, P1, P2, P3, P4]; }
  const NW = COLS.map((_, i) => 1.31 + i * .015); // görsel olarak büyütülmüş dağılım (gerçekte 1,331–1,343)
  function drop(s, R, x, y) { const g = new THREE.Group(); g.position.set(x, y, 0); s.add(g);
    g.add(M(new THREE.SphereGeometry(R, 64, 48), new THREE.MeshStandardMaterial({ color: 0x9fd0ff, emissive: 0x0a2a4a, transparent: true, opacity: .22, roughness: .05, metalness: .1, depthWrite: false })));
    const rim = M(new THREE.SphereGeometry(R * 1.02, 64, 48), new THREE.MeshBasicMaterial({ color: 0x7ee0ff, transparent: true, opacity: .18, side: THREE.BackSide, blending: THREE.AdditiveBlending, depthWrite: false })); g.add(rim);
    const hl = M(new THREE.SphereGeometry(R * .12, 16, 12), glow(0xffffff, .7)); hl.position.set(-R * .45, R * .5, R * .7); g.add(hl); return g; }
  function sun(s, r, x, y, z = 0) { const g = new THREE.Group(); g.position.set(x, y, z); s.add(g);
    g.add(M(new THREE.SphereGeometry(r, 48, 32), new THREE.MeshBasicMaterial({ color: 0xfff2c0 })));
    const h = [1.6, 2.4, 3.4].map((k, i) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0xffd070, transparent: true, opacity: [.7, .4, .2][i], blending: THREE.AdditiveBlending, depthWrite: false })); m.scale.setScalar(r * k * 2); g.add(m); return m; });
    g.halo = h; return g; }
  function rain(s, n, sx, y0, y1, sz, z0 = 0) { const a = Array.from({ length: n }, () => { const d = M(new THREE.CylinderGeometry(.012, .012, .32, 4), glow(0x9fd0ff, .45)); d.userData = { x: (r1() - .5) * sx, z: z0 + (r1() - .5) * sz, ph: r1() }; s.add(d); return d; });
    return t => a.forEach(d => { const c = (t * 1.2 + d.userData.ph) % 1; d.position.set(d.userData.x + c * .15, lerp(y0, y1, c), d.userData.z); d.rotation.z = .12; }); }

  const S0b = 3.28, S1 = 4.8, S2 = 8.48, S3 = 12.16, S4 = 14.88, S5 = 18.88, S6 = 23.92, S7 = 27.28, S8 = 32.2, S9 = 36.0;

  // 1) Tam çember gökkuşağı havada döner; soru işareti
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0e1c44', '#020308'], rim: 0x7ee0ff });
    const B = bow(s, 1.75, .1, Math.PI * 2, .85); B.position.set(0, 5.0, 0);
    const cl = dust(260, [6, 4, 3], 0x9fd0ff, .1, .5); cl.position.set(0, 5.0, -1); s.add(cl);
    const q = qmark(s, 2.0, 7.0, .65);
    return t => {
      E.d.rotation.y = t * .02; cl.rotation.z = t * .05;
      B.set(easeOut(prog(t, .1, 1.6)), Math.PI * 2); B.rotation.set(Math.sin(t * .5) * .2, Math.sin(t * .6) * .55, -Math.PI / 2);
      q.visible = t > S0b; q.rotation.y = Math.sin(t * 2) * .4; q.scale.setScalar(.65 * back(prog(t, S0b, .4)));
      cam.position.set(Math.sin(t * .2) * 1, 6.0, lerp(14.5, 13, ease(prog(t, 0, S1)))); cam.lookAt(0, 5.25, 0); };
  } });
  // 2) Beyaz ışık cam prizmadan geçince renklere ayrılır
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffd070 });
    const sh = new THREE.Shape(); sh.moveTo(0, 1.0); sh.lineTo(-.87, -.5); sh.lineTo(.87, -.5); sh.closePath();
    const pg = new THREE.ExtrudeGeometry(sh, { depth: 1.0, bevelEnabled: true, bevelThickness: .04, bevelSize: .04, bevelSegments: 3 }); pg.translate(0, 0, -.5);
    const P = M(pg, new THREE.MeshStandardMaterial({ color: 0xcfe8ff, transparent: true, opacity: .3, roughness: .05, metalness: .2, depthWrite: false })); P.position.set(0, 4.85, 0); s.add(P);
    const ed = new THREE.LineSegments(new THREE.EdgesGeometry(pg, 30), new THREE.LineBasicMaterial({ color: 0xbfe8ff, transparent: true, opacity: .85 })); P.add(ed);
    const Su = sun(s, .32, -2.25, 4.45, 0);
    const wb = ray(0xffffff, .05); s.add(wb);
    const fan = COLS.map(c => { const m = ray(c, .04); s.add(m); return m; });
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02; Su.halo.forEach((h, i) => h.material.opacity = [.7, .4, .2][i] * (1 + .15 * Math.sin(t * 4 + i)));
      wb.set(poly([V(-1.95, 4.5), V(-.42, 5.05)], ease(prog(a, .2, .8))));
      fan.forEach((m, i) => { const an = .05 - i * .07; const k = ease(prog(a, 1.0 + i * .05, 1.0)); m.set(poly([V(.4, 5.05), V(.4 + 2.2 * Math.cos(an), 5.05 + 2.2 * Math.sin(an))], k)); m.visible = a > 1.0; });
      P.rotation.y = Math.sin(t * .6) * .08;
      cam.position.set(Math.sin(a * .25) * .8, 5.7, 13); cam.lookAt(0, 5.1, 0); };
  } });
  // 3–5) Yağmur damlası: giriş kırılması + ayrışma, mor daha çok bükülür, arka yüzeyden yansıma ve çıkış
  shots.push({ t0: S2, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const R = 1.55, c = V(.45, 5.0); const D = drop(s, R, c.x, c.y);
    const paths = NW.map(n => trace(c, R, .84, n, 2.6, 1.7));
    const wb = ray(0xffffff, .05); s.add(wb);
    const rs = COLS.map(col => { const m = ray(col, .03); s.add(m); return m; });
    const flash = M(new THREE.SphereGeometry(.12, 16, 12), glow(0xffffff, 1)); flash.position.copy(paths[0][1]); s.add(flash);
    const bounce = M(new THREE.SphereGeometry(.14, 16, 12), glow(0xffcf2e, 1)); s.add(bounce);
    const cl = dust(150, [4, 3.5, 2], 0x9fd0ff, .09, .4); cl.position.set(0, 5, -1.5); s.add(cl);
    return t => {
      const a = t - S2; E.d.rotation.y = t * .02; cl.rotation.y = t * .1;
      D.scale.setScalar(lerp(.85, 1, easeOut(prog(a, 0, .6)))); D.rotation.y = t * .2;
      wb.set(poly([paths[0][0], paths[0][1]], ease(prog(a, .1, .7))));
      const kIn = ease(prog(a, .8, 1.4)); const kOut = ease(prog(t, S4 + .1, 2.6));
      rs.forEach((m, i) => { const P = paths[i]; const seg = kOut > 0 ? poly([P[1], P[2], P[3], P[4]], 1 / 3 + kOut * 2 / 3 * 1.0) : poly([P[1], P[2]], kIn);
        m.set(seg); m.visible = a > .8;
        const hi = t > S3 && t < S4 ? (i === 0 || i === 6 ? 1 : .18) : 1; m.material.opacity = .95 * hi; m.r = t > S3 && t < S4 && (i === 0 || i === 6) ? .05 : .03; });
      flash.visible = a > .7 && a < 1.6; flash.scale.setScalar(1 + 2 * prog(a, .7, .9)); flash.material.opacity = 1 - prog(a, .7, .9);
      bounce.visible = t > S4 + .6 && t < S4 + 2.2; bounce.position.copy(paths[3][2]); bounce.scale.setScalar(1 + .4 * Math.sin(t * 10));
      const zoom = t > S3 && t < S4 ? ease(prog(t, S3, .8)) * (1 - ease(prog(t, S4 - .4, .4))) : 0;
      cam.position.set(Math.sin(a * .15) * .6 + zoom * .6, 5.4 - zoom * .3, 13 - zoom * 2.2); cam.lookAt(zoom * .6, 5.0 - zoom * .1, 0); };
  } });
  // 6) Göze gelen açılar: kırmızı 42°, mor 40° (yan kesit)
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff8a3a });
    const P = person(); P.position.set(1.9, 3.75, 0); P.rotation.y = -Math.PI / 2; P.scale.setScalar(.85); s.add(P);
    const eye = V(1.75, 4.35);
    const ground = M(new THREE.BoxGeometry(8, .2, 3), std(0x16221c, { roughness: .95 })); ground.position.set(0, 3.15, 0); s.add(ground);
    const base = V(-Math.cos(.18), -Math.sin(.18)); // Güneşin tam karşısı (gölge doğrultusu)
    const anti = ray(0xffffff, .015, .5); s.add(anti); anti.set([eye, eye.clone().addScaledVector(base, 3.9)]);
    const rot = (v, a) => V(v.x * Math.cos(a) + v.y * Math.sin(a) * -1, v.x * Math.sin(a) + v.y * Math.cos(a));
    const dirR = rot(base, -.73), dirV = rot(base, -.6); // görünür olsun diye açı farkı büyütüldü
    const rr = ray(0xff3b30, .045); const rv = ray(0xaf52de, .045); s.add(rr, rv);
    const dR = drop(s, .2, 0, 0), dV = drop(s, .2, 0, 0);
    const arcR = M(new THREE.TorusGeometry(1.0, .02, 6, 64, .73), glow(0xff3b30, .9)); arcR.position.copy(eye); arcR.rotation.z = Math.PI + .18 - .73; s.add(arcR);
    const arcV = M(new THREE.TorusGeometry(.7, .02, 6, 64, .6), glow(0xaf52de, .9)); arcV.position.copy(eye); arcV.rotation.z = Math.PI + .18 - .6; s.add(arcV);
    const rf = rain(s, 50, 4.5, 7.2, 3.4, 2, -1);
    return t => {
      const a = t - S5; E.d.rotation.y = t * .02; rf(t);
      const kR = ease(prog(a, .3, 1.0)), kV = ease(prog(a, 2.3, 1.0));
      const eR = eye.clone().addScaledVector(dirR, 3.6), eV = eye.clone().addScaledVector(dirV, 3.5);
      rr.set(poly([eR, eye], kR)); rv.set(poly([eV, eye], kV)); rv.visible = a > 2.3;
      dR.position.copy(eR); dV.position.copy(eV); dR.visible = a > .2; dV.visible = a > 2.2;
      arcR.visible = a > 1.0; arcV.visible = a > 3.0; arcR.scale.setScalar(easeOut(prog(a, 1.0, .5))); arcV.scale.setScalar(easeOut(prog(a, 3.0, .5)));
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 13); cam.lookAt(0, 5.0, 0); };
  } });
  // 7) Güneş arkanda, yağmur önünde (yan görünüş)
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffd070 });
    const Su = sun(s, .42, 2.05, 6.35);
    const P = person(); P.position.set(.9, 3.95, 0); P.rotation.y = -Math.PI / 2; P.scale.setScalar(.8); s.add(P);
    const ground = M(new THREE.BoxGeometry(8, .2, 3), std(0x16221c, { roughness: .95 })); ground.position.set(0, 3.35, 0); s.add(ground);
    const cloud = new THREE.Group(); cloud.position.set(-1.6, 6.55, -.3); s.add(cloud);
    for (let i = 0; i < 9; i++) { const b = M(new THREE.SphereGeometry(.35 + r1() * .3, 24, 16), std(0x5a6478, { roughness: .9 })); b.position.set((r1() - .5) * 1.8, (r1() - .5) * .35, (r1() - .5) * .6); cloud.add(b); }
    const rf = rain(s, 70, 1.6, 6.3, 3.5, 1.2, 0); s.children.slice(-70).forEach(d => d.userData.x -= 1.6);
    const eye = V(.82, 4.55); const dp = V(-1.6, 5.4);
    const inR = ray(0xfff2c0, .04); const outR = COLS.map(c => { const m = ray(c, .022); s.add(m); return m; }); s.add(inR);
    const B = bow(s, 2.6, .07, Math.PI, .35); B.position.set(-3.4, 3.4, -4);
    return t => {
      const a = t - S6; E.d.rotation.y = t * .02; rf(t); Su.rotation.z = t * .3; Su.halo.forEach((h, i) => h.material.opacity = [.7, .4, .2][i] * (1 + .15 * Math.sin(t * 4 + i)));
      inR.set(poly([V(1.75, 6.15), dp], ease(prog(a, .3, .9))));
      outR.forEach((m, i) => { m.set(poly([dp, eye.clone().add(V(0, (i - 3) * .03))], ease(prog(a, 1.3, .9)))); m.visible = a > 1.3; });
      B.set(ease(prog(a, 1.6, 1.4)));
      cam.position.set(Math.sin(a * .2) * .8, 5.6, 13); cam.lookAt(0, 5.0, 0); };
  } });
  // 8) Çift gökkuşağı: dıştaki soluk ve ters sıralı
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#13224a', '#020308'], rim: 0x7ee0ff });
    const hill = M(new THREE.SphereGeometry(9, 64, 32), std(0x18241e, { roughness: .95 })); hill.position.set(0, -5.4, -3); s.add(hill);
    const B1 = bow(s, 1.75, .1, Math.PI, .85); B1.position.set(0, 3.7, -1);
    const B2 = bow(s, 2.45, .085, Math.PI, .38, true); B2.position.set(0, 3.7, -1);
    const rf = rain(s, 60, 6, 7.5, 3.4, 3, -1);
    return t => {
      const a = t - S7; E.d.rotation.y = t * .02; rf(t);
      B1.set(1); B2.set(ease(prog(a, .9, 1.6)));
      B2.rings.forEach(m => m.material.opacity = .38 + .08 * Math.sin(t * 3));
      cam.position.set(Math.sin(a * .2) * .8, 5.6, lerp(13.6, 12.8, ease(prog(a, 0, 4)))); cam.lookAt(0, 4.95, 0); };
  } });
  // 9) Yerden yay, uçaktan tam çember: zemin kaybolur, alt yarı görünür
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#13224a', '#020308'], rim: 0x7ee0ff });
    const B = bow(s, 1.6, .095, Math.PI * 2, .85); B.position.set(0, 4.9, -2);
    const gm = std(0x16221c, { roughness: .95, transparent: true, opacity: 1 });
    const ground = M(new THREE.PlaneGeometry(60, 60), gm); ground.rotation.x = -Math.PI / 2; ground.position.y = 4.9; s.add(ground);
    const clouds = dust(220, [10, 1.5, 6], 0xffffff, .5, 0, false); clouds.position.set(0, 2.6, -2); s.add(clouds);
    const pl = new THREE.Group(); s.add(pl); const pm = std(0xe8eef6, { metalness: .4, roughness: .3 });
    const fus = M(new THREE.CapsuleGeometry(.09, .9, 6, 16), pm); fus.rotation.z = Math.PI / 2; pl.add(fus);
    const wing = M(new THREE.BoxGeometry(.3, .03, 1.1), pm); pl.add(wing); const tail = M(new THREE.BoxGeometry(.18, .25, .03), pm); tail.position.set(-.45, .12, 0); pl.add(tail);
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02; const k = ease(prog(a, 1.6, 1.4));
      gm.opacity = 1 - k; ground.visible = k < .99; ground.position.y = 4.9 - k * 3; clouds.material.opacity = .25 * k;
      B.rotation.z = -Math.PI / 2; B.rings.forEach(m => m.material.opacity = .85);
      pl.position.set(lerp(-3.2, 3.2, prog(a, 1.4, 2.6)), 6.55, .5); pl.visible = a > 1.4 && a < 4.0; pl.rotation.y = 0;
      cam.position.set(Math.sin(a * .2) * .6, lerp(5.35, 6.0, k), 12.5); cam.lookAt(0, lerp(5.1, 4.95, k), -2); };
  } });
  // 10) Sıradaki soru: Güneş birden yok olsa? Güneş titreyip söner, Dünya karanlıkta kalır
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#1a1430', '#020308'], rim: 0xff8a3a });
    const Su = sun(s, 1.05, -.4, 5.15, -1);
    const core = Su.children[0];
    const earth = M(new THREE.SphereGeometry(.33, 48, 32), std(0x2a6fd0, { roughness: .5, emissive: 0x061630 })); s.add(earth);
    const orbit = M(new THREE.TorusGeometry(2.1, .01, 6, 128), glow(0xffffff, .3)); orbit.rotation.x = Math.PI / 2 - .25; orbit.position.copy(Su.position); s.add(orbit);
    const pt = new THREE.PointLight(0xffd070, 80, 12); Su.add(pt);
    const q = qmark(s, 2.0, 7.0, .65);
    return t => {
      const a = t - S9; E.d.rotation.y = t * .02;
      const on = a < 1.2 ? 1 : (a < 1.8 ? (Math.sin(a * 40) > 0 ? 1 : .2) : Math.max(0, 1 - (a - 1.8) * 1.5));
      core.material.color.setRGB(1 * on + .05, .95 * on + .05, .75 * on + .06); Su.halo.forEach((h, i) => h.material.opacity = [.7, .4, .2][i] * on); pt.intensity = 80 * on;
      const an = a * .5; earth.position.set(Su.position.x + Math.cos(an) * 2.1, Su.position.y + Math.sin(an) * 2.1 * Math.sin(.25), Su.position.z + Math.sin(an) * 2.1 * Math.cos(.25)); earth.rotation.y = t;
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * 1, 6.0, 13.5); cam.lookAt(0, 5.2, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:300px;font-size:190px" id="${id}">${html}</div><div class="sub" style="top:500px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S0b, html: T('ŞAŞIRTAN GERÇEK', 'GÖKKUŞAĞI<br><span class="y">TAM ÇEMBER!</span>', 108) },
    { t0: S0b, t1: S1, html: T('BİR SORU', 'GÖKKUŞAĞI<br>NASIL <span class="y">OLUŞUR?</span>', 108) },
    { t0: S1, t1: S2, html: T('GÜNEŞ IŞIĞI BEYAZ', 'İÇİNDE <span class="y">BÜTÜN</span><br><span class="y">RENKLER</span> VAR', 100) },
    { t0: S2, t1: S3, html: T('YAĞMUR DAMLASI', 'IŞIK <span class="y">KIRILIR</span><br>RENKLERE AYRILIR', 92) },
    { t0: S3, t1: S4, html: T('MOR IŞIK', 'KIRMIZIDAN DAHA<br>ÇOK <span class="y">BÜKÜLÜR</span>', 96) },
    { t0: S4, t1: S5, html: T('DAMLANIN İÇİNDE', '<span class="y">YANSIR</span> VE<br>TEKRAR KIRILIR', 100) },
    { t0: S5, t1: S6, html: BIG('KIRMIZI IŞIK', 'k42', 'MOR IŞIK: 40°', '42°') },
    { t0: S6, t1: S7, html: T('KURAL', 'GÜNEŞ <span class="y">ARKANDA</span><br>YAĞMUR ÖNÜNDE', 96) },
    { t0: S7, t1: S8, html: T('ÇİFT GÖKKUŞAĞI', 'RENKLER<br><span class="y">TERS SIRALI</span>', 108) },
    { t0: S8, t1: S9, html: T('UÇAKTAN BAKINCA', '<span class="y">TAM ÇEMBER</span>', 116) },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'GÜNEŞ BİRDEN<br>YOK OLSA<br>NE <span class="y">OLUR?</span>', 92) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k42', S5]];
  return {
    END: 41.16, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; }); },
    follow: { t: 39.28, click: 40.26 },
    sfx: [[.3, 'whoosh', .5], [1.6, 'ding', .4], [S0b + .2, 'pop', .4], [S1 + .5, 'whoosh', .4], [S1 + 1.2, 'ding', .5], [S2 + .9, 'snap', .4], [S2 + 1.2, 'pop', .3],
      [S3 + .2, 'pop', .4], [S4 + .7, 'click', .4], [S4 + 1.8, 'click', .3], [S5 + .3, 'pop', .5], [S5 + 1.0, 'ding', .4], [S5 + 3.0, 'ding', .3],
      [S6 + .4, 'whoosh', .4], [S6 + 1.4, 'pop', .3], [S7 + 1.0, 'ding', .4], [S8 + 1.6, 'whoosh', .5], [S8 + 2.6, 'ding', .4],
      [S9 + .4, 'whoosh', .5], [S9 + 1.3, 'snap', .4], [S9 + 2.0, 'pop_low', .5]],
  };
};
