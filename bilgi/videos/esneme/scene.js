// Bilgi #23: Neden esneriz? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Eric Chudler, Neuroscience for Kids "Yawning" (faculty.washington.edu/chudler/yawning.html: bir esneme ortalama ~6 sn sürer;
// Provine ve ark. 1987: CO2 ya da %100 oksijen solumak esnemeyi artırmadı; ilk esneme döllenmeden ~11 hafta sonra; esnemeyi düşünmek ya da
// okumak bile esnetir; 2007'de esnemenin beyni soğuttuğu öne sürüldü). ScienceNorway "Why do we yawn and why is it contagious?" (havadaki
// oksijen/CO2 değişse de esneme değişmez; derin nefes beyne giden kanı soğutur, çene gerilmesi kan akışını hızlandırır; resim görmek ya da
// okumak bile yetebilir). Sleep Review "Yawning cools brain" (Gallup: serin ortam havasıyla ısı alışverişi beyin sıcaklığını düşürebilir).
export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const M = (g, m) => new THREE.Mesh(g, m);
  const V = (x, y, z = 0) => new THREE.Vector3(x, y, z);
  let seed = 2323; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
    s.background = gradTex(...(o.bg || ['#0f1a3a', '#020308'])); s.fog = new THREE.Fog(o.fog || 0x02050e, o.near || 30, o.far || 110);
    const hemi = new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi ?? .8); s.add(hemi);
    const key = new THREE.DirectionalLight(o.keyc || 0xffe6cc, o.key ?? 2.2); key.position.set(...(o.kp || [-10, 12, 10])); s.add(key);
    const rim = new THREE.PointLight(o.rim || 0xffb070, 600, 60); rim.position.set(6, 9, -5); s.add(rim);
    const d = dust(500, [26, 18, 16], o.dust || 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return { d, rim, key, hemi };
  }
  const glow = (c, op = .9) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false });
  const halo = (c, sc, op = .5) => { const h = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false })); h.scale.setScalar(sc); return h; };
  function qmark(s, x, y, sc = 1) { const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); q.position.set(x, y, .5); q.scale.setScalar(sc); s.add(q);
    const qa = M(new THREE.TorusGeometry(.42, .1, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.12, 12, 8), qm); qd.position.set(-.08, -.72, 0); q.add(qd); return q; }
  const textTex = (txt, col = '#ffffff', w = 256, h = 128, font = 'bold 90px Oswald, sans-serif') => { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
    g.fillStyle = col; g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(txt, w / 2, h / 2 + 4); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  // 3D esneyen kafa: yawn(k) 0..1
  const SKINS = [0xf0b48a, 0xd9956a, 0xf5c8a0, 0xb97a52], HAIRS = [0x3a2418, 0x1a1210, 0x8a5a2a, 0x2a1a12];
  function head(si = 0) {
    const Hd = new THREE.Group(); const skin = std(SKINS[si % 4], { roughness: .55 });
    const hd = M(new THREE.SphereGeometry(1.25, 64, 48), skin); hd.scale.set(1, 1.12, 1); Hd.add(hd);
    const hair = M(new THREE.SphereGeometry(1.28, 48, 32, 0, Math.PI * 2, 0, Math.PI * .42), std(HAIRS[si % 4], { roughness: .8 })); hair.position.y = .12; hair.rotation.x = -.25; Hd.add(hair);
    [-1, 1].forEach(k => { const ear = M(new THREE.SphereGeometry(.25, 24, 16), skin); ear.scale.set(.5, 1, .8); ear.position.set(k * 1.22, 0, 0); Hd.add(ear); });
    const lids = [-1, 1].map(k => { const e = M(new THREE.SphereGeometry(.17, 24, 16), std(0xffffff, { roughness: .3 })); e.position.set(k * .42, .22, 1.08); Hd.add(e);
      const p = M(new THREE.SphereGeometry(.08, 16, 12), std(0x2a1a10)); p.position.set(k * .42, .22, 1.24); Hd.add(p);
      const lid = M(new THREE.SphereGeometry(.185, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), skin); lid.position.copy(e.position); Hd.add(lid); return lid; });
    const nose = M(new THREE.SphereGeometry(.13, 20, 14), skin); nose.position.set(0, -.08, 1.24); Hd.add(nose);
    const mouth = M(new THREE.SphereGeometry(.3, 32, 24), std(0x5a1a1a, { roughness: .7 })); mouth.position.set(0, -.55, 1.05); Hd.add(mouth);
    const tongue = M(new THREE.SphereGeometry(.18, 24, 16), std(0xd06070)); tongue.position.set(0, -.75, 1.12); tongue.scale.set(1.2, .5, .6); Hd.add(tongue);
    Hd.yawn = k => { const yy = ease(clamp(k)); mouth.scale.set(lerp(.8, 1.2, yy), lerp(.15, 1.6, yy), lerp(.5, .9, yy)); tongue.visible = yy > .3;
      lids.forEach(l => l.rotation.x = lerp(-1.4, .15, yy * .9)); hd.scale.y = 1.12 + .06 * yy; };
    Hd.mouth = mouth; return Hd;
  }
  const yawnCurve = (a, s, d) => Math.sin(clamp((a - s) / d) * Math.PI);
  // Kıvrımlı 3D beyin
  function brain() { const g = new THREE.SphereGeometry(1, 128, 96); const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      const n = .06 * Math.sin(x * 14 + Math.sin(y * 9) * 2) * Math.cos(z * 12 + y * 4) + .04 * hash(x * 6, y * 6, z * 6); const fis = Math.abs(x) < .06 ? -.12 * (1 - Math.abs(x) / .06) : 0;
      const k = 1 + n + fis; p.setXYZ(i, x * k * 1.15, y * k * .85, z * k * 1.3); }
    g.computeVertexNormals(); return M(g, std(0xf0a0a8, { roughness: .45, metalness: .05, emissive: 0x200508 })); }

  const S1 = 4.4, S2 = 6.96, S3 = 10.12, S4 = 13.72, S5 = 16.48, S6 = 22.44, S7 = 26.16, S8 = 32.08;

  // 1) Kanca: büyük esneyen kafa + soru işareti
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s); const H = head(0); H.position.set(0, 4.75, 0); H.scale.setScalar(1.05); s.add(H);
    const q = qmark(s, 1.85, 6.0, .6);
    return t => { E.d.rotation.y = t * .02; H.yawn(yawnCurve(t, .5, 3.4)); H.rotation.x = -.22 * yawnCurve(t, .5, 3.4); H.rotation.y = Math.sin(t * .5) * .25;
      q.scale.setScalar(.6 * Math.max(.001, back(prog(t, 2.6, .5)))); q.rotation.y = Math.sin(t * 2) * .4;
      cam.position.set(Math.sin(t * .3) * .6, 5.4, lerp(13.4, 12.2, ease(prog(t, 0, S1)))); cam.lookAt(0, 4.9, 0); };
  } });
  // 2) Ortalama 6 saniye: kafanın çevresinde dolan sarı halka
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffcf2e }); const H = head(1); H.position.set(0, 4.7, 0); H.scale.setScalar(.85); s.add(H);
    const ringBg = M(new THREE.TorusGeometry(1.75, .05, 12, 96), std(0x2a3550, { roughness: .5 })); ringBg.position.set(0, 4.7, -.4); s.add(ringBg);
    const arcs = []; for (let i = 0; i < 6; i++) { const a = M(new THREE.TorusGeometry(1.75, .09, 14, 32, Math.PI * 2 / 6 - .06), glow(0xffcf2e, .95)); a.position.copy(ringBg.position); a.rotation.z = Math.PI / 2 - (i + 1) * Math.PI * 2 / 6 + .03; s.add(a); arcs.push(a); }
    return t => { const a = t - S1; E.d.rotation.y = t * .02; H.yawn(yawnCurve(a, 0, 2.6)); H.rotation.y = Math.sin(t * .6) * .2;
      arcs.forEach((m, i) => { const k = prog(a, .2 + i * .33, .2); m.visible = k > 0; m.scale.setScalar(lerp(.9, 1, easeOut(k))); });
      cam.position.set(Math.sin(a * .3) * .5, 5.3, 12.4); cam.lookAt(0, 4.85, 0); };
  } });
  // 3) Eski teori: oksijen molekülleri kafaya doğru akar
  const o2 = (s) => { const g = new THREE.Group(); const m = std(0xe8333a, { roughness: .25, metalness: .1, emissive: 0x200000 });
    [-1, 1].forEach(k => { const b = M(new THREE.SphereGeometry(.28, 32, 24), m); b.position.x = k * .2; g.add(b); }); s.add(g); return g; };
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff5050 }); const H = head(2); H.position.set(-.5, 4.6, 0); H.scale.setScalar(.8); H.rotation.y = .5; s.add(H);
    const mol = Array.from({ length: 8 }, (_, i) => { const m = o2(s); m.userData = { ph: i / 8, y: 3.6 + r1() * 2.2, z: (r1() - .5) * 1.5 }; return m; });
    const tt = textTex('O₂', '#ffffff'); const lab = new THREE.Sprite(new THREE.SpriteMaterial({ map: tt, transparent: true, depthWrite: false })); lab.scale.set(1.2, .6, 1); lab.position.set(1.6, 6.15, .5); s.add(lab);
    const q = qmark(s, -.5, 6.35, .45);
    return t => { const a = t - S2; E.d.rotation.y = t * .02; H.yawn(yawnCurve(a, .4, 2.6));
      mol.forEach(m => { const u = (a * .35 + m.userData.ph) % 1; m.position.set(lerp(2.6, -.1, u), lerp(m.userData.y, 4.1, u * u), m.userData.z * (1 - u) + .8 * u); m.rotation.set(t, t * 1.3, 0); m.scale.setScalar(Math.sin(u * Math.PI) * .9 + .1); });
      lab.material.opacity = ease(prog(a, .3, .5)); q.rotation.y = Math.sin(t * 2) * .4; q.scale.setScalar(.45 * Math.max(.001, back(prog(a, 1.8, .5))));
      cam.position.set(Math.sin(a * .25) * .5, 5.3, 12.4); cam.lookAt(0, 4.85, 0); };
  } });
  // 4) Deney: oksijen tüpü + büyük kırmızı çarpı
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x4fc3ff });
    const tank = new THREE.Group(); tank.position.set(-.9, 4.3, 0); tank.scale.setScalar(.8); s.add(tank);
    const body = M(new THREE.CapsuleGeometry(.6, 2.0, 16, 48), std(0x2f8f4a, { metalness: .6, roughness: .3 })); tank.add(body);
    const tex = textTex('O₂', '#ffffff', 256, 256, 'bold 150px Oswald, sans-serif'); const lab = M(new THREE.CylinderGeometry(.605, .605, .8, 48, 1, true, -.9, 1.8), new THREE.MeshStandardMaterial({ map: tex, transparent: true, roughness: .4 })); tank.add(lab);
    const valve = M(new THREE.CylinderGeometry(.18, .22, .4, 24), std(0xc8ccd4, { metalness: .9, roughness: .2 })); valve.position.y = 1.8; tank.add(valve);
    const hose = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V(-.9, 5.9), V(-.2, 6.15), V(.7, 5.9), V(1.0, 5.2)]), 60, .05, 10), std(0x8a8f99, { roughness: .4 })); s.add(hose);
    const H = head(3); H.position.set(1.3, 4.4, -.3); H.scale.setScalar(.62); H.rotation.y = -.5; s.add(H);
    const X = new THREE.Group(); X.position.set(0, 4.7, 1.5); s.add(X);
    [1, -1].forEach(k => { const b = M(new THREE.BoxGeometry(3.4, .32, .25), std(0xe0302a, { emissive: 0x500000, roughness: .3 })); b.rotation.z = k * Math.PI / 4; X.add(b); });
    const gas = dust(60, [1.5, 1.5, 1.5], 0x9fe0ff, .15, .6); gas.position.set(.9, 5.6, .3); s.add(gas);
    return t => { const a = t - S3; E.d.rotation.y = t * .02; tank.rotation.y = Math.sin(t * .5) * .3; gas.rotation.y = t; gas.material.opacity = .5 * (1 - prog(a, 2.2, .5));
      H.yawn(yawnCurve(a, .3, 1.8)); X.scale.setScalar(Math.max(.001, back(prog(a, 2.0, .45)))); X.rotation.y = Math.sin(t * 1.5) * .2;
      cam.position.set(Math.sin(a * .3) * .5, 5.3, 12.4); cam.lookAt(0, 4.85, 0); };
  } });
  // 5) Beyin soğuyor: kırmızımsı → mavi ışıltı, termometre düşer
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x4fc3ff }); const B = brain(); B.position.set(-.45, 4.75, 0); B.scale.setScalar(1.15); s.add(B);
    const hh = halo(0xff5a3a, 5.5, .5); hh.position.copy(B.position); s.add(hh);
    const th = new THREE.Group(); th.position.set(1.65, 4.4, .5); s.add(th);
    const tube = M(new THREE.CylinderGeometry(.13, .13, 2.2, 24), new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: .25, roughness: .1 })); th.add(tube);
    const bulb = M(new THREE.SphereGeometry(.26, 24, 16), std(0xe0302a, { emissive: 0x400000 })); bulb.position.y = -1.2; th.add(bulb);
    const liq = M(new THREE.CylinderGeometry(.08, .08, 1, 16), std(0xe0302a, { emissive: 0x400000 })); th.add(liq);
    const frost = dust(140, [4, 3, 2], 0x9fe0ff, .12, 0); frost.position.copy(B.position); s.add(frost);
    const red = new THREE.Color(0xff5a3a), blue = new THREE.Color(0x4fc3ff);
    return t => { const a = t - S4; E.d.rotation.y = t * .02; B.rotation.y = .4 + t * .3; const k = ease(prog(a, .8, 1.6));
      hh.material.color.copy(red).lerp(blue, k); B.material.emissive.copy(new THREE.Color(0x200508)).lerp(new THREE.Color(0x0a2a50), k);
      const h = lerp(1.8, .7, k); liq.scale.y = h; liq.position.y = -1.1 + h / 2; [bulb, liq].forEach(m => m.material.color.copy(red).lerp(blue, k));
      frost.material.opacity = .6 * k; frost.rotation.y = -t * .3;
      cam.position.set(Math.sin(a * .3) * .6, 5.3, 12.4); cam.lookAt(0, 4.85, 0); };
  } });
  // 6) Mekanizma: serin hava ağza akar, çene gerilir, boyundan beyne giden damar maviye döner
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x4fc3ff });
    const H = head(0); H.position.set(.3, 4.85, 0); H.scale.setScalar(.95); H.rotation.y = -.75; s.add(H);
    const head2 = H.children[0]; head2.material = head2.material.clone(); head2.material.transparent = true; head2.material.opacity = .55; head2.material.depthWrite = false;
    const B = brain(); B.scale.setScalar(.62); B.position.set(.3, 5.35, -.05); s.add(B);
    const vpts = [V(.15, 2.6, .2), V(.25, 3.3, .25), V(.35, 4.0, .3), V(.4, 4.6, .15), V(.3, 5.0, 0)];
    const vessel = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(vpts), 80, .09, 14), std(0xd0303a, { emissive: 0x400000, roughness: .35 })); s.add(vessel);
    const neck = M(new THREE.CylinderGeometry(.55, .65, 1.4, 32), std(SKINS[0], { roughness: .55, transparent: true, opacity: .5, depthWrite: false })); neck.position.set(.3, 3.35, -.1); s.add(neck);
    const airN = 70; const air = Array.from({ length: airN }, (_, i) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: soft, color: 0x9fe0ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); m.scale.setScalar(.22); m.userData = { ph: i / airN, oy: (r1() - .5) * 1.2, oz: (r1() - .5) * 1.0 }; s.add(m); return m; });
    const flow = Array.from({ length: 10 }, (_, i) => { const m = halo(0xff6060, .35, .9); m.userData = { ph: i / 10 }; s.add(m); return m; });
    const curve = new THREE.CatmullRomCurve3(vpts); const red = new THREE.Color(0xd0303a), blue = new THREE.Color(0x3fa8ff);
    return t => { const a = t - S5; E.d.rotation.y = t * .02;
      const y = clamp(ease(prog(a, .2, 1.0)) - ease(prog(a, 5.0, .8))); H.yawn(y); H.rotation.x = -.18 * y;
      const mouthW = V(); H.mouth.getWorldPosition(mouthW);
      air.forEach(m => { const u = (a * .5 + m.userData.ph) % 1; const on = prog(a, .6, .4) * (1 - prog(a, 5.2, .5));
        m.position.set(lerp(-2.6, mouthW.x, u), lerp(mouthW.y + m.userData.oy, mouthW.y, u), lerp(m.userData.oz + .8, mouthW.z, u)); m.material.opacity = .8 * on * Math.sin(u * Math.PI); });
      const k = ease(prog(a, 3.4, 1.6)); vessel.material.color.copy(red).lerp(blue, k); vessel.material.emissive.copy(new THREE.Color(0x400000)).lerp(new THREE.Color(0x002050), k);
      flow.forEach(m => { const u = (a * .45 + m.userData.ph) % 1; m.position.copy(curve.getPoint(u)); m.position.z += .1; m.material.color.copy(new THREE.Color(0xff6060)).lerp(new THREE.Color(0x9fe0ff), k); });
      B.material.emissive.copy(new THREE.Color(0x200508)).lerp(new THREE.Color(0x0a3060), ease(prog(a, 4.4, 1.2)));
      cam.position.set(lerp(-.6, .6, ease(prog(a, 0, S6 - S5))), 5.2, 12.0); cam.lookAt(0, 4.6, 0); };
  } });
  // 7) Anne karnında bebek esner: yarı saydam rahim küresi, kıvrılmış bebek
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#2a0f22', '#060208'], rim: 0xff7aa8, keyc: 0xffd6c8, dust: 0xffc0d8 });
    const W0 = new THREE.Group(); W0.position.set(0, 4.95, 0); W0.scale.setScalar(.88); s.add(W0);
    const womb = M(new THREE.SphereGeometry(1.95, 64, 48), new THREE.MeshStandardMaterial({ color: 0xff8fb0, transparent: true, opacity: .22, roughness: .2, depthWrite: false, side: THREE.DoubleSide })); W0.add(womb);
    W0.add(halo(0xff6a9a, 6, .35));
    const skin = std(0xf5b8a0, { roughness: .5, emissive: 0x200808 });
    const bb = new THREE.Group(); W0.add(bb); bb.rotation.z = .35;
    const hd = M(new THREE.SphereGeometry(.62, 48, 32), skin); hd.position.set(-.15, .45, 0); bb.add(hd);
    const body = M(new THREE.SphereGeometry(.7, 48, 32), skin); body.scale.set(.8, 1, .85); body.position.set(.25, -.45, 0); bb.add(body);
    const legs = M(new THREE.TorusGeometry(.35, .17, 16, 32, Math.PI * 1.2), skin); legs.position.set(.35, -.85, .25); legs.rotation.set(.3, .4, 1.6); bb.add(legs);
    const arm = M(new THREE.CapsuleGeometry(.12, .45, 8, 16), skin); arm.position.set(-.05, -.15, .45); arm.rotation.z = 1.0; bb.add(arm);
    const eye = M(new THREE.SphereGeometry(.05, 12, 8), std(0x5a2a2a)); eye.position.set(-.38, .58, .52); bb.add(eye);
    const mouth = M(new THREE.SphereGeometry(.11, 24, 16), std(0x6a2028, { roughness: .7 })); mouth.position.set(-.3, .2, .55); bb.add(mouth);
    const cord = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V(.3, -.3, .4), V(.9, -.6, .6), V(1.3, .2, .3), V(1.6, .8, 0)]), 60, .06, 10), std(0xd88aa0, { roughness: .4 })); W0.add(cord);
    const hb = textTex('11. HAFTA', '#ffcf2e', 512, 128, 'bold 96px Oswald, sans-serif'); const lab = new THREE.Sprite(new THREE.SpriteMaterial({ map: hb, transparent: true, depthWrite: false })); lab.scale.set(2.4, .6, 1); lab.position.set(0, 3.55, 2.2); s.add(lab);
    return t => { const a = t - S6; E.d.rotation.y = t * .02; W0.rotation.y = Math.sin(t * .4) * .3; bb.position.y = Math.sin(t * 1.2) * .05;
      const y = yawnCurve(a, 1.2, 2.2); mouth.scale.set(lerp(.6, 1.1, y), lerp(.2, 1.8, y), .8); hd.rotation.x = -.2 * y; womb.scale.setScalar(1 + .015 * Math.sin(t * 2));
      lab.material.opacity = ease(prog(a, 1.4, .5)); lab.scale.set(2.4 * (.8 + .2 * back(prog(a, 1.4, .5))), .6, 1);
      cam.position.set(Math.sin(a * .3) * .6, 5.2, 12.2); cam.lookAt(0, 4.6, 0); };
  } });
  // 8) Bulaşıcı: sıradaki kafalar zincirleme esner
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xffcf2e });
    const hs = [[-1.55, 5.75], [.15, 5.6], [1.6, 5.75], [-.75, 3.9], [.95, 3.9]].map(([x, y], i) => { const h = head(i); h.position.set(x, y, i > 2 ? .8 : -.3); h.scale.setScalar(.55); h.rotation.y = -x * .25; s.add(h); return h; });
    const rings = hs.map(h => { const r = M(new THREE.TorusGeometry(.95, .03, 8, 64), glow(0xffcf2e, 0)); r.position.copy(h.position); s.add(r); return r; });
    return t => { const a = t - S7; E.d.rotation.y = t * .02;
      hs.forEach((h, i) => { const st = .3 + i * 1.0; const y = yawnCurve(a, st, 2.2); h.yawn(y); h.rotation.x = -.2 * y; h.position.y += 0;
        const r = rings[i]; const u = prog(a, st, 1.0); r.scale.setScalar(.8 + u * .9); r.material.opacity = .8 * Math.sin(u * Math.PI); });
      cam.position.set(Math.sin(a * .2) * .6, 5.3, 12.6); cam.lookAt(0, 4.85, 0); };
  } });
  // 9) Sıradaki soru: Ay neden Dünya'ya düşmez? Dünya + yörüngede Ay
  shots.push({ t0: S8, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a1430', '#010208'], rim: 0x4fc3ff, keyc: 0xfff4e0 });
    const et = (() => { const c = document.createElement('canvas'); c.width = 512; c.height = 256; const g = c.getContext('2d'); g.fillStyle = '#1d4f9a'; g.fillRect(0, 0, 512, 256);
      g.fillStyle = '#3f8a46'; for (let i = 0; i < 26; i++) { g.beginPath(); g.ellipse(r1() * 512, 40 + r1() * 176, 20 + r1() * 50, 12 + r1() * 30, r1() * 3, 0, Math.PI * 2); g.fill(); }
      g.fillStyle = 'rgba(255,255,255,.55)'; for (let i = 0; i < 30; i++) { g.beginPath(); g.ellipse(r1() * 512, r1() * 256, 20 + r1() * 40, 4 + r1() * 6, 0, 0, Math.PI * 2); g.fill(); }
      const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
    const earth = M(new THREE.SphereGeometry(1.15, 64, 48), new THREE.MeshStandardMaterial({ map: et, roughness: .6 })); earth.position.set(0, 4.7, 0); s.add(earth);
    const atm = halo(0x4fa8ff, 3.4, .45); atm.position.copy(earth.position); s.add(atm);
    const mt = (() => { const c = document.createElement('canvas'); c.width = 256; c.height = 128; const g = c.getContext('2d'); g.fillStyle = '#b8b8b8'; g.fillRect(0, 0, 256, 128);
      for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(80,80,80,${.2 + r1() * .4})`; g.beginPath(); g.arc(r1() * 256, r1() * 128, 3 + r1() * 12, 0, Math.PI * 2); g.fill(); } const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
    const moon = M(new THREE.SphereGeometry(.38, 48, 32), new THREE.MeshStandardMaterial({ map: mt, roughness: .9 })); s.add(moon);
    const orbit = M(new THREE.TorusGeometry(2.1, .012, 6, 128), glow(0x7ee0ff, .5)); orbit.position.copy(earth.position); orbit.rotation.x = Math.PI / 2 - .35; s.add(orbit);
    const q = qmark(s, -1.9, 6.0, .45);
    return t => { const a = t - S8; E.d.rotation.y = t * .02; earth.rotation.y = t * .4;
      const ang = a * .9 + 2.2; const p = V(Math.cos(ang) * 2.1, 0, Math.sin(ang) * 2.1).applyAxisAngle(V(1, 0, 0), -.35 + 0); moon.position.set(p.x, 4.7 + Math.sin(ang) * 2.1 * Math.sin(.35) * -1, Math.sin(ang) * 2.1 * Math.cos(.35)); moon.rotation.y = t * .3;
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * .6, 5.4, 12.6); cam.lookAt(0, 4.85, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('ŞU AN BİLE', 'NEDEN<br><span class="y">ESNERİZ?</span>', 120) },
    { t0: S1, t1: S2, html: T('BİR ESNEME', 'ORTALAMA<br><span class="y">6 SANİYE</span>', 116) },
    { t0: S2, t1: S3, html: T('ESKİ TEORİ', 'VÜCUT <span class="y">OKSİJEN</span><br>İSTİYOR', 108) },
    { t0: S3, t1: S4, html: T('DENEYLER', 'FAZLA OKSİJEN<br><span class="y">İŞE YARAMADI</span>', 100) },
    { t0: S4, t1: S5, html: T('GÜÇLÜ TEORİ', 'BEYNİ<br><span class="y">SOĞUTUR</span>', 120) },
    { t0: S5, t1: S6, html: T('NASIL?', 'SERİN HAVA<br>KANI <span class="y">SERİNLETİR</span>', 100) },
    { t0: S6, t1: S7, html: T('ANNE KARNINDA', 'BEBEKLER<br><span class="y">BİLE</span> ESNER', 112) },
    { t0: S7, t1: S8, html: T('ÜSTELİK', 'ESNEME<br><span class="y">BULAŞICI</span>', 120) },
    { t0: S8, t1: 99, html: T('SIRADAKİ SORU', 'AY NEDEN<br><span class="y">DÜNYA\'YA</span> DÜŞMEZ?', 100) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 36.92, shots, titles,
    update: () => {},
    follow: { t: 35.12, click: 36.02 },
    sfx: [[.3, 'whoosh', .5], [2.6, 'pop', .4], [S1 + .3, 'ding', .3], [S1 + 2.2, 'ding', .35], [S2 + .5, 'pop_low', .4], [S2 + 1.8, 'pop', .35],
      [S3 + 2.0, 'snap', .6], [S4 + .9, 'whoosh', .4], [S4 + 2.2, 'ding', .3], [S5 + .6, 'whoosh', .5], [S5 + 3.5, 'pop_low', .35],
      [S6 + 1.4, 'pop', .4], [S7 + .3, 'pop', .35], [S7 + 1.3, 'pop', .35], [S7 + 2.3, 'pop', .35], [S7 + 3.3, 'pop', .35], [S7 + 4.3, 'pop', .35], [S8 + .4, 'whoosh', .5]],
  };
};
