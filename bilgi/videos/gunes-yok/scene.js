// Bilgi #20: Güneş birden yok olsa ne olur? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Live Science, "What would happen to Earth if the sun suddenly vanished?" (ışık Dünya'ya yaklaşık 8 dakika 20 saniyede ulaşır, en az bu kadar
// süre fark etmeyiz; Güneş'in çekimi olmadan gezegenler yörüngeden çıkıp düz bir doğrultuda ilerler; Ay tamamen kararır, uzak yıldızlar görünmeye devam
// eder; Dünya ilk başta günde ortalama yaklaşık 20 °C soğur, 2–3 gün içinde neredeyse her yer donma noktasının altına iner; fotosentez yapan canlılar
// sonunda ölür; okyanuslar belki on yıllarca donmadan kalabilir, okyanus tabanındaki volkanik noktalar daha uzun süre sıvı kalabilir).
// NASA: Dünya–Güneş ortalama uzaklığı yaklaşık 150 milyon km (1 AB). Ay kendi ışığını üretmez, Güneş ışığını yansıtır.
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
  // Dünya dokusu (tohumlu gürültü): okyanus, kara, kutup buzu; gece şehir ışıkları ayrı doku
  const texE = (() => { const c = document.createElement('canvas'); c.width = 512; c.height = 256; const g = c.getContext('2d'); const id = g.createImageData(512, 256);
    const cc = document.createElement('canvas'); cc.width = 512; cc.height = 256; const gc = cc.getContext('2d'); gc.fillStyle = '#000'; gc.fillRect(0, 0, 512, 256);
    for (let y = 0; y < 256; y++) for (let x = 0; x < 512; x++) { const lo = x / 512 * Math.PI * 2, la = (y / 256 - .5) * Math.PI;
      const X = Math.cos(la) * Math.cos(lo) * 2, Y = Math.sin(la) * 2, Z = Math.cos(la) * Math.sin(lo) * 2;
      const h = hash(X, Y, Z) + .5 * hash(X * 2.3, Y * 2.3, Z * 2.3); const pol = Math.abs(la) > 1.25; let r, gg, b;
      if (pol) { r = 235; gg = 240; b = 248; } else if (h > .5) { const k = clamp((h - .5) * 1.5); r = lerp(70, 150, k); gg = lerp(130, 120, k); b = lerp(60, 80, k); } else { const k = clamp(h + .8); r = 15; gg = lerp(50, 90, k); b = lerp(120, 170, k); }
      const i = (y * 512 + x) * 4; id.data[i] = r; id.data[i + 1] = gg; id.data[i + 2] = b; id.data[i + 3] = 255;
      if (!pol && h > .55 && r1() > .975) { gc.fillStyle = 'rgba(255,200,120,.9)'; gc.fillRect(x, y, 2, 2); } }
    g.putImageData(id, 0, 0); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; const tc = new THREE.CanvasTexture(cc); tc.colorSpace = THREE.SRGBColorSpace; return { t, tc }; })();
  function earth(s, r) { const g = new THREE.Group(); s.add(g);
    const m = new THREE.MeshStandardMaterial({ map: texE.t, roughness: .7, metalness: 0, emissiveMap: texE.tc, emissive: 0xffffff, emissiveIntensity: 0 });
    const e = M(new THREE.SphereGeometry(r, 64, 48), m); g.add(e);
    const atm = M(new THREE.SphereGeometry(r * 1.06, 48, 32), new THREE.MeshBasicMaterial({ color: 0x5ab0ff, transparent: true, opacity: .2, side: THREE.BackSide, blending: THREE.AdditiveBlending, depthWrite: false })); g.add(atm);
    g.e = e; g.m = m; g.atm = atm; return g; }
  function moon(s, r) { const c = document.createElement('canvas'); c.width = 256; c.height = 128; const gg = c.getContext('2d'); gg.fillStyle = '#9a9a9a'; gg.fillRect(0, 0, 256, 128);
    for (let i = 0; i < 60; i++) { gg.fillStyle = `rgba(60,60,60,${.2 + r1() * .3})`; gg.beginPath(); gg.arc(r1() * 256, r1() * 128, 2 + r1() * 9, 0, 7); gg.fill(); }
    const t = new THREE.CanvasTexture(c); const m = M(new THREE.SphereGeometry(r, 48, 32), new THREE.MeshStandardMaterial({ map: t, roughness: .95 })); s.add(m); return m; }
  function sun(s, r, x, y, z = 0) { const g = new THREE.Group(); g.position.set(x, y, z); s.add(g);
    const core = M(new THREE.SphereGeometry(r, 48, 32), new THREE.MeshBasicMaterial({ color: 0xfff0b0 })); g.add(core);
    const h = [1.6, 2.6, 3.8].map((k, i) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0xffb040, transparent: true, opacity: [.8, .45, .22][i], blending: THREE.AdditiveBlending, depthWrite: false })); m.scale.setScalar(r * k * 2); g.add(m); return m; });
    g.core = core; g.halo = h; g.set = k => { core.scale.setScalar(Math.max(.001, k)); h.forEach((m, i) => m.material.opacity = [.8, .45, .22][i] * k); }; return g; }
  function stars(n, sp, size = .12) { const d = dust(n, sp, 0xffffff, size, .9); return d; }

  const S1 = 4.12, S2 = 7.68, S2b = 10.12, S3 = 13.36, S4 = 15.68, S5 = 20.69, S5b = 24.08, S6 = 26.64, S7 = 29.76, S8 = 35.04;

  // 1) Güneş bir anda yok olur ama Dünya hâlâ aydınlık
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1430', '#010206'], hemi: .15, key: 2.6, kp: [-10, 2, 4] });
    const st = stars(400, [30, 20, 10], .1); st.position.set(0, 5, -8); s.add(st);
    const Su = sun(s, 1.0, -2.3, 5.0, -2);
    const Ea = earth(s, 1.15); Ea.position.set(1.0, 5.0, 0);
    const ring = M(new THREE.TorusGeometry(1, .03, 8, 96), glow(0xffd070, 1)); ring.position.copy(Su.position); s.add(ring);
    return t => {
      E.d.rotation.y = t * .02; Ea.e.rotation.y = t * .15;
      const k = 1 - easeOut(prog(t, 1.0, .35)); Su.set(k * (1 + .03 * Math.sin(t * 6)));
      ring.visible = t > 1.0 && t < 2.2; ring.scale.setScalar(1 + 3 * prog(t, 1.0, 1.2)); ring.material.opacity = 1 - prog(t, 1.0, 1.2);
      cam.position.set(Math.sin(t * .2) * .8, 5.6, lerp(13.8, 12.8, ease(prog(t, 0, S1)))); cam.lookAt(0, 5.15, 0); };
  } });
  // 2) Işık cephesi 150 milyon km yol alır: 8 dk 20 sn
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1430', '#010206'], hemi: .15, key: 2.4, kp: [-10, 1, 3] });
    const st = stars(400, [30, 20, 10], .1); st.position.set(0, 5, -8); s.add(st);
    const ghost = M(new THREE.SphereGeometry(.45, 32, 24), new THREE.MeshBasicMaterial({ color: 0x1a1a22 })); ghost.position.set(-2.2, 5.0, 0); s.add(ghost);
    const gr = M(new THREE.TorusGeometry(.5, .015, 6, 64), glow(0xffb040, .5)); gr.position.copy(ghost.position); s.add(gr);
    const Ea = earth(s, .45); Ea.position.set(2.05, 5.0, 0);
    const front = new THREE.Group(); s.add(front);
    const ph = Array.from({ length: 40 }, (_, i) => { const m = M(new THREE.SphereGeometry(.05, 10, 8), glow(0xffe0a0, .95)); m.position.set((r1() - .5) * .15, (i / 39 - .5) * 3.2, (r1() - .5) * .5); front.add(m); return m; });
    const sheet = M(new THREE.PlaneGeometry(.5, 3.4), new THREE.MeshBasicMaterial({ color: 0xffc060, transparent: true, opacity: .12, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide })); sheet.position.x = -.25; front.add(sheet);
    const path = M(new THREE.CylinderGeometry(.01, .01, 4.2, 6), glow(0xffffff, .25)); path.rotation.z = Math.PI / 2; path.position.set(0, 5.0, 0); s.add(path);
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02; Ea.e.rotation.y = t * .15; const k = prog(a, .1, S2 - S1 - .3);
      front.position.set(lerp(-2.2, 2.05, k), 5.0, 0); ph.forEach((m, i) => m.scale.setScalar(1 + .4 * Math.sin(t * 8 + i)));
      E.key.intensity = 2.4; gr.scale.setScalar(1 + .1 * Math.sin(t * 3));
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 12.8); cam.lookAt(0, 5.05, 0); };
  } });
  // 3) Işık biter: Dünya kararır, gece tarafında şehir ışıkları; Ay söner
  shots.push({ t0: S2, t1: S2b, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1430', '#010206'], hemi: .15, key: 2.6, kp: [-10, 2, 4] });
    const st = stars(500, [30, 20, 10], .1); st.position.set(0, 5, -8); s.add(st);
    const Ea = earth(s, 1.2); Ea.position.set(-.45, 4.65, 0);
    const Mo = moon(s, .38); Mo.position.set(1.75, 6.1, .5);
    return t => {
      const a = t - S2; E.d.rotation.y = t * .02; Ea.e.rotation.y = t * .15 + 1; Mo.rotation.y = t * .1;
      const k = ease(prog(a, .5, 1.4)); E.key.intensity = 2.6 * (1 - k); E.hemi.intensity = .15 * (1 - k) + .03;
      Ea.m.emissiveIntensity = 1.4 * k; Ea.atm.material.opacity = .2 * (1 - k) + .04;
      cam.position.set(Math.sin(a * .2) * .6, 5.5, lerp(13, 12.3, ease(prog(a, 0, 2.4)))); cam.lookAt(0, 5.0, 0); };
  } });
  // 4) Ay kendi ışığını üretmez: güneş ışınları Ay'a çarpıp yansır, sonra kesilir
  shots.push({ t0: S2b, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1430', '#010206'], hemi: .05, key: 2.8, kp: [-10, 3, 3] });
    const st = stars(400, [30, 20, 10], .1); st.position.set(0, 5, -8); s.add(st);
    const Mo = moon(s, 1.15); Mo.position.set(.35, 5.0, 0);
    const beams = Array.from({ length: 6 }, (_, i) => { const y = 5.0 + (i - 2.5) * .32; const inn = M(new THREE.CylinderGeometry(.025, .025, 1, 8), glow(0xffe0a0, .9)); inn.rotation.z = Math.PI / 2; s.add(inn);
      const out = M(new THREE.CylinderGeometry(.02, .02, 1, 8), glow(0xffe0a0, .7)); s.add(out); const hx = .35 - Math.sqrt(Math.max(0, 1.15 * 1.15 - (y - 5) ** 2)); return { y, inn, out, hx }; });
    return t => {
      const a = t - S2b; E.d.rotation.y = t * .02; Mo.rotation.y = t * .1;
      const off = ease(prog(a, 1.7, .6)); E.key.intensity = 2.8 * (1 - off);
      beams.forEach((b, i) => { const L1 = Math.max(.01, (b.hx + 2.7) * easeOut(prog(a, .1 + i * .04, .5))); b.inn.scale.y = L1; b.inn.position.set(-2.7 + L1 / 2, b.y, .4);
        const L2 = 1.6 * easeOut(prog(a, .6 + i * .04, .5)); const an = .35 + (b.y - 5) * .35; b.out.scale.y = Math.max(.01, L2); b.out.rotation.z = Math.PI / 2 + an;
        b.out.position.set(b.hx - Math.cos(an) * L2 / 2, b.y - Math.sin(an) * L2 / 2, .4); b.inn.material.opacity = .9 * (1 - off); b.out.material.opacity = .7 * (1 - off); b.out.visible = a > .6; });
      cam.position.set(Math.sin(a * .2) * .6, 5.4, 12.8); cam.lookAt(0, 5.0, 0); };
  } });
  // 5) Yıldızlar parlamaya devam eder (kararmış Dünya önde)
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#060a1a', '#000104'], hemi: .02, key: 0 });
    const groups = [0, 1, 2].map(i => { const d = stars(260, [14, 14, 6], .16 + i * .06); d.position.set(0, 5.5, -4); s.add(d); return d; });
    const Ea = earth(s, 3.2); Ea.position.set(0, 1.1, -1); Ea.m.emissiveIntensity = 1.3; Ea.atm.material.opacity = .08;
    const big = Array.from({ length: 8 }, () => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0xcfe8ff, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); sp.position.set((r1() - .5) * 4.6, 5.0 + r1() * 2.2, (r1() - .5) * 2); sp.userData.ph = r1() * 6; s.add(sp); return sp; });
    return t => {
      const a = t - S3; E.d.rotation.y = t * .02; Ea.e.rotation.y = t * .05;
      groups.forEach((d, i) => d.material.opacity = (.55 + .35 * Math.sin(t * (2 + i) + i * 2)) * easeOut(prog(a, 0, .8)));
      big.forEach(sp => { const k = .5 + .5 * Math.sin(t * 3 + sp.userData.ph); sp.scale.setScalar(.25 + .35 * k); sp.material.opacity = .5 + .5 * k; });
      cam.position.set(Math.sin(a * .2) * .6, lerp(5.0, 5.6, ease(prog(a, 0, 2.3))), 12.8); cam.lookAt(0, 5.6, 0); };
  } });
  // 6) Çekim biter: Dünya yörüngeden çıkıp teğet doğrultuda dümdüz ilerler
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1430', '#010206'], hemi: .5 });
    const st = stars(400, [30, 20, 10], .1); st.position.set(0, 5, -8); s.add(st);
    const C = V(-.2, 4.8, 0), R = 1.75;
    const orbit = M(new THREE.TorusGeometry(R, .015, 6, 160), glow(0x7ee0ff, .45)); orbit.rotation.x = Math.PI / 2; orbit.position.copy(C); s.add(orbit);
    const ghost = M(new THREE.SphereGeometry(.35, 32, 24), new THREE.MeshBasicMaterial({ color: 0x15151c })); ghost.position.copy(C); s.add(ghost);
    const gr = M(new THREE.TorusGeometry(.4, .015, 6, 64), glow(0xffb040, .6)); gr.position.copy(C); s.add(gr);
    const Ea = earth(s, .3);
    const trail = M(new THREE.BufferGeometry(), glow(0xffcf2e, .9)); s.add(trail);
    const tg = M(new THREE.CylinderGeometry(.012, .012, 6, 6), glow(0xffffff, .3)); s.add(tg);
    const tRel = 16.4 - S4; const w = .9; const ang0 = -Math.PI / 2 - .3 - tRel * w;
    const posAt = a => { if (a < tRel) { const an = ang0 + a * w; return V(C.x + Math.cos(an) * R, C.y, C.z + Math.sin(an) * R); }
      const an = ang0 + tRel * w; const p = V(C.x + Math.cos(an) * R, C.y, C.z + Math.sin(an) * R); const d = V(-Math.sin(an), 0, Math.cos(an)); return p.addScaledVector(d, (a - tRel) * .55); };
    return t => {
      const a = t - S4; E.d.rotation.y = t * .02; Ea.e.rotation.y = t * .5;
      Ea.position.copy(posAt(a)); const cut = a >= tRel; ghost.visible = true; gr.visible = !cut || Math.sin(a * 20) > 0 && a < tRel + .5; gr.material.opacity = cut ? .3 : .6;
      orbit.material.opacity = cut ? .45 * (1 - prog(a, tRel, 1.5)) + .12 : .45;
      const P = []; for (let k = 0; k <= 30; k++) P.push(posAt(Math.max(0, a - 1.6 + k * 1.6 / 30)));
      trail.geometry.dispose(); trail.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(P), 60, .035, 6);
      const an = ang0 + tRel * w; const p = V(C.x + Math.cos(an) * R, C.y, C.z + Math.sin(an) * R); tg.position.copy(p).addScaledVector(V(-Math.sin(an), 0, Math.cos(an)), 2.5);
      tg.rotation.set(0, 0, 0); tg.lookAt(p); tg.rotateX(Math.PI / 2); tg.visible = cut;
      cam.position.set(Math.sin(a * .15) * .6, 9.6, 10.6); cam.lookAt(0, 4.75, 0); };
  } });
  // 7) Sıcaklık: termometre düşer, Dünya buzlanır
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010206'], hemi: .5, key: 1.4, rim: 0x9fd8ff });
    const Ea = earth(s, 1.15); Ea.position.set(-.75, 4.95, 0);
    const ice = M(new THREE.SphereGeometry(1.17, 64, 48), new THREE.MeshStandardMaterial({ color: 0xe8f6ff, roughness: .3, metalness: .1, transparent: true, opacity: 0 })); Ea.add(ice);
    const T = new THREE.Group(); T.position.set(1.65, 4.95, .3); s.add(T);
    const tube = M(new THREE.CapsuleGeometry(.2, 2.3, 8, 24), new THREE.MeshStandardMaterial({ color: 0xdfefff, transparent: true, opacity: .3, roughness: .05, depthWrite: false })); T.add(tube);
    const bulb = M(new THREE.SphereGeometry(.34, 32, 24), std(0x3fa0ff, { emissive: 0x1050a0, emissiveIntensity: .6 })); bulb.position.y = -1.35; T.add(bulb);
    const liq = M(new THREE.CylinderGeometry(.1, .1, 1, 24), std(0xff4030, { emissive: 0x801000, emissiveIntensity: .7 })); T.add(liq);
    for (let i = 0; i < 9; i++) { const tk = M(new THREE.BoxGeometry(.18, .025, .02), new THREE.MeshBasicMaterial({ color: 0xffffff })); tk.position.set(.3, -1.1 + i * .28, 0); T.add(tk); }
    const fr = dust(240, [4.5, 3.5, 2], 0xe8f6ff, .14, 0); fr.position.set(0, 5.0, .5); s.add(fr);
    return t => {
      const a = t - S5; E.d.rotation.y = t * .02; Ea.e.rotation.y = t * .1;
      const k = ease(prog(a, .2, S6 - S5 - .6)); const h = lerp(2.0, .25, k);
      liq.scale.y = h; liq.position.y = -1.2 + h / 2; const c = new THREE.Color(0xff4030).lerp(new THREE.Color(0x3fa0ff), k); liq.material.color.copy(c); liq.material.emissive.copy(c).multiplyScalar(.4);
      ice.material.opacity = .75 * ease(prog(t, S5b - .2, 2.0)); fr.material.opacity = .7 * prog(t, S5b - .4, 1.2); fr.rotation.y = t * .15; fr.position.y = 5.0 - ((t * .3) % 1) * .3;
      T.rotation.y = Math.sin(t * .6) * .3;
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 12.8); cam.lookAt(0, 5.0, 0); };
  } });
  // 8) Bitki solar: fotosentez durur, yapraklar kahverengileşip düşer
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010206'], hemi: .6, key: 1.8, rim: 0x9fd8ff });
    const pot = M(new THREE.CylinderGeometry(.75, .55, .9, 48), std(0x8a4a2a, { roughness: .8 })); pot.position.set(0, 3.85, 0); s.add(pot);
    const soil = M(new THREE.CylinderGeometry(.7, .7, .05, 48), std(0x3a2a1a)); soil.position.set(0, 4.28, 0); s.add(soil);
    const P = new THREE.Group(); P.position.set(0, 4.3, 0); s.add(P);
    const stem = M(new THREE.CylinderGeometry(.045, .06, 2.2, 16), std(0x3a8a3a)); stem.position.y = 1.1; P.add(stem);
    const lshape = new THREE.Shape(); lshape.moveTo(0, 0); lshape.quadraticCurveTo(.35, .25, .9, 0); lshape.quadraticCurveTo(.35, -.25, 0, 0);
    const lg = new THREE.ShapeGeometry(lshape, 16);
    const leaves = Array.from({ length: 8 }, (_, i) => { const piv = new THREE.Group(); piv.position.y = .5 + i * .2; piv.rotation.y = i * 2.4; P.add(piv);
      const lf = M(lg, std(0x4ab04a, { side: THREE.DoubleSide, roughness: .6, emissive: 0x143014 })); lf.rotation.x = -.3; piv.add(lf); piv.userData.lf = lf; return piv; });
    const sunrays = Array.from({ length: 5 }, (_, i) => { const m = M(new THREE.CylinderGeometry(.03, .03, 3, 8), glow(0xffe0a0, .5)); m.rotation.z = -.6; m.position.set(-1.6 + i * .25, 6.6 - i * .1, 0); s.add(m); return m; });
    const fr = dust(160, [4, 3.5, 2], 0xe8f6ff, .12, 0); fr.position.set(0, 5.2, .3); s.add(fr);
    return t => {
      const a = t - S6; E.d.rotation.y = t * .02; const k = ease(prog(a, .4, 2.4));
      sunrays.forEach(m => m.material.opacity = .5 * (1 - prog(a, 0, .6)));
      E.key.intensity = 1.8 * (1 - .6 * k);
      stem.material.color.copy(new THREE.Color(0x3a8a3a).lerp(new THREE.Color(0x5a4a2a), k)); P.rotation.z = -.35 * k; P.rotation.y = t * .15;
      leaves.forEach((piv, i) => { const lf = piv.userData.lf; lf.material.color.copy(new THREE.Color(0x4ab04a).lerp(new THREE.Color(0x7a5a2a), clamp(k * 1.3 - i * .03))); lf.rotation.x = -.3 - 1.0 * k; lf.rotation.z = -.9 * k; });
      fr.material.opacity = .6 * k; fr.rotation.y = t * .1;
      cam.position.set(Math.sin(a * .2) * .6, 5.5, 12.5); cam.lookAt(0, 5.0, 0); };
  } });
  // 9) Okyanus kesiti: üstte kalın buz, altta sıvı su; tabandaki volkanik baca ısı verir
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0b1838', '#010206'], hemi: .7, key: 1.8, rim: 0x7ee0ff });
    const B = new THREE.Group(); B.position.set(0, 5.0, 0); s.add(B);
    const water = M(new THREE.BoxGeometry(4.2, 2.6, 2), new THREE.MeshStandardMaterial({ color: 0x1a5aa0, transparent: true, opacity: .55, roughness: .2, depthWrite: false })); water.position.y = -.35; B.add(water);
    const iceM = new THREE.MeshStandardMaterial({ color: 0xdff2ff, roughness: .25, metalness: .05, transparent: true, opacity: .92 });
    const ice = M(new THREE.BoxGeometry(4.25, 1, 2.05), iceM); B.add(ice);
    const floor = M(new THREE.BoxGeometry(4.3, .3, 2.1), std(0x2a2620, { roughness: .95 })); floor.position.y = -1.8; B.add(floor);
    const vent = M(new THREE.ConeGeometry(.35, .7, 24), std(0x2a2020, { roughness: .9 })); vent.position.set(.6, -1.35, 0); B.add(vent);
    const hot = M(new THREE.SphereGeometry(.18, 16, 12), glow(0xff6a2a, .9)); hot.position.set(.6, -1.0, 0); B.add(hot);
    const vl = new THREE.PointLight(0xff6a2a, 20, 4); vl.position.set(.6, -.8, .4); B.add(vl);
    const bub = Array.from({ length: 20 }, () => { const b = M(new THREE.SphereGeometry(.04 + r1() * .04, 10, 8), glow(0xbfe8ff, .7)); b.userData = { x: .6 + (r1() - .5) * .3, z: (r1() - .5) * .3, ph: r1() }; B.add(b); return b; });
    const fish = Array.from({ length: 5 }, (_, i) => { const f = M(new THREE.SphereGeometry(.09, 16, 12), std(0xffcf2e, { emissive: 0x403000 })); f.scale.set(2, 1, 1); f.userData.ph = i * 1.3; B.add(f); return f; });
    return t => {
      const a = t - S7; E.d.rotation.y = t * .02; const k = easeOut(prog(a, .2, 1.4));
      ice.scale.y = lerp(.05, 1, k); ice.position.y = .95 - .5 * ice.scale.y; water.scale.y = 1; B.rotation.y = -.35 + Math.sin(t * .3) * .2;
      hot.scale.setScalar(1 + .25 * Math.sin(t * 6)); vl.intensity = 20 + 6 * Math.sin(t * 6);
      bub.forEach(b => { const c = (t * .4 + b.userData.ph) % 1; b.position.set(b.userData.x + Math.sin(c * 9) * .05, lerp(-1.0, .3, c), b.userData.z); });
      fish.forEach(f => { const u = t * .4 + f.userData.ph; f.position.set(Math.sin(u) * 1.5, -.9 + Math.sin(u * 1.7) * .3, Math.cos(u) * .5); f.rotation.y = -u + Math.PI / 2; });
      cam.position.set(Math.sin(a * .2) * .6, 5.6, 12.8); cam.lookAt(0, 4.9, 0); };
  } });
  // 10) Sıradaki soru: Ahtapotun neden 3 kalbi var? Ahtapot + şeffaf gövdede atan 3 kalp
  shots.push({ t0: S8, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a1a3a', '#010308'], rim: 0xff6a8a });
    const O = new THREE.Group(); O.position.set(-.2, 5.35, 0); s.add(O);
    const skin = std(0xd0603a, { roughness: .45, transparent: true, opacity: .6, depthWrite: false });
    const head = M(new THREE.SphereGeometry(.85, 48, 32), skin); head.scale.set(1, 1.25, 1); head.position.y = .45; O.add(head);
    [-1, 1].forEach(k => { const e = M(new THREE.SphereGeometry(.14, 20, 16), std(0xffffff)); e.position.set(k * .35, -.05, .72); O.add(e); const p = M(new THREE.SphereGeometry(.07, 16, 12), std(0x111111)); p.position.set(k * .35, -.05, .84); O.add(p); });
    const hearts = [V(0, .55, 0), V(-.35, .15, -.1), V(.35, .15, -.1)].map((p, i) => { const h = M(new THREE.SphereGeometry(i ? .13 : .2, 24, 16), new THREE.MeshBasicMaterial({ color: i ? 0x4aa0ff : 0xff3040 })); h.position.copy(p); O.add(h);
      const g = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: i ? 0x4aa0ff : 0xff3040, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })); g.position.copy(p); g.scale.setScalar(.7); O.add(g); h.userData.g = g; return h; });
    const arms = Array.from({ length: 8 }, (_, i) => { const m = M(new THREE.BufferGeometry(), std(0xd0603a, { roughness: .5 })); m.userData.an = i / 8 * Math.PI * 2; O.add(m); return m; });
    const bub = dust(120, [5, 4, 3], 0xbfe8ff, .1, .5); bub.position.set(0, 5, -1); s.add(bub);
    const q = qmark(s, 2.0, 7.0, .65);
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02; bub.position.y = 5 + (t * .2) % 1;
      O.rotation.y = Math.sin(t * .5) * .4; O.position.y = 5.35 + Math.sin(t * 1.5) * .08;
      hearts.forEach((h, i) => { const b = 1 + .25 * Math.max(0, Math.sin(t * 7 + i * 1.2)); h.scale.setScalar(b * back(prog(a, .3 + i * .25, .4))); h.userData.g.material.opacity = .8 * prog(a, .3 + i * .25, .4); });
      arms.forEach(m => { const an = m.userData.an; const P = []; for (let k = 0; k <= 12; k++) { const u = k / 12; const r = .45 + u * 1.1; const sw = Math.sin(t * 2 + an * 3 - u * 4) * .25 * u;
        P.push(V(Math.cos(an + sw) * r, -.35 - u * 1.0 + Math.sin(t * 2.5 + an + u * 5) * .15 * u, Math.sin(an + sw) * r * .7)); }
        m.geometry.dispose(); const tg = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(P), 40, .1, 10); const pa = tg.attributes.position; // uca doğru incelir
        m.geometry = tg; m.scale.setScalar(1); });
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * 1, 5.9, 13.2); cam.lookAt(0, 5.2, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:300px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('GÜNEŞ YOK OLSA', '<span class="y">8 DAKİKA</span><br>FARK ETMEZSİN', 104) },
    { t0: S1, t1: S2, html: BIG('IŞIK BİZE', 'kt', '150 MİLYON KM YOL', '0<small>DK</small> 0<small>SN</small>') },
    { t0: S2, t1: S2b, html: T('SONRA', 'GÖKYÜZÜ<br><span class="y">KARARIR</span>', 116) },
    { t0: S2b, t1: S3, html: T('AY DA SÖNER', 'IŞIĞI <span class="y">GÜNEŞ\'TEN</span><br>YANSIR', 100) },
    { t0: S3, t1: S4, html: T('AMA', 'YILDIZLAR<br><span class="y">PARLAMAYA DEVAM</span>', 96) },
    { t0: S4, t1: S5, html: T('ÇEKİM BİTER', 'DÜNYA <span class="y">DÜMDÜZ</span><br>İLERLER', 108) },
    { t0: S5, t1: S5b, html: BIG('İLK GÜNLERDE', 'kd', 'HER GÜN YAKLAŞIK', '−20<small>°C</small>') },
    { t0: S5b, t1: S6, html: T('2–3 GÜNDE', 'NEREDEYSE HER YER<br><span class="y">DONAR</span>', 92) },
    { t0: S6, t1: S7, html: T('FOTOSENTEZ BİTER', 'BESİN ZİNCİRİ<br><span class="y">ÇÖKER</span>', 104) },
    { t0: S7, t1: S8, html: T('OKYANUS DERİNLERİ', '<span class="y">ON YILLARCA</span><br>DONMAYABİLİR', 96) },
    { t0: S8, t1: 99, html: T('SIRADAKİ SORU', 'AHTAPOTUN NEDEN<br><span class="y">3 KALBİ</span> VAR?', 92) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['kt', S1], ['kd', S5]];
  return {
    END: 40.04, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; });
      const k = q('kt'); if (k) { const sec = Math.round(500 * prog(t, S1 + .1, S2 - S1 - .3)); k.innerHTML = `${Math.floor(sec / 60)}<small>DK</small> ${sec % 60}<small>SN</small>`; } },
    follow: { t: 38.16, click: 39.14 },
    sfx: [[.3, 'whoosh', .5], [1.0, 'boom', .6], [S1 + .3, 'whoosh', .4], [S2 - .4, 'ding', .4], [S2 + .6, 'pop_low', .5], [S2b + .2, 'whoosh', .3], [S2b + 1.7, 'snap', .4],
      [S3 + .3, 'ding', .3], [S3 + 1.2, 'ding', .25], [16.4, 'snap', .5], [16.6, 'whoosh', .4], [S5 + .3, 'pop', .4], [S5b + .2, 'crunch', .5], [S5b + 1.0, 'crunch', .4],
      [S6 + .5, 'pop_low', .4], [S7 + .3, 'crunch', .4], [S7 + 1.6, 'pop', .3], [S8 + .4, 'whoosh', .5], [S8 + .7, 'pop', .4], [S8 + .95, 'pop', .4], [S8 + 1.2, 'pop', .4]],
  };
};
