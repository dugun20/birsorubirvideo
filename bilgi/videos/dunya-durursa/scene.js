// Bilgi #5: Dünya dönmeyi durdursa ne olur? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: ekvator dönüş hızı ~1.670 km/sa (sciencenotes.org, NASA); sular kutuplara göçer, ekvatorda tek dev kıta
// (Esri ArcUser 2010, W. Fraczek); dönüş tamamen dursa 1 gün = 1 yıl (6 ay gündüz, 6 ay gece).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const dark = () => std(0x2a2f36, { metalness: .6, roughness: .45 });
  const concrete = () => std(0x3a3f47, { roughness: .9 });
  let seed = 23; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  function dust(n, sp, color = 0xcfe8ff, size = .25, op = .5) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
    for (let i = 0; i < n * 3; i += 3) { p[i] = (r1() - .5) * sp[0]; p[i + 1] = (r1() - .5) * sp[1]; p[i + 2] = (r1() - .5) * sp[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color, size, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending }));
  }
  function lights(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#0d2240', '#02060e'])); s.fog = new THREE.Fog(o.fog || 0x050d1c, o.near || 40, o.far || 140);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x0a0a12, o.hemi || .9));
    const key = new THREE.SpotLight(0xfff1dc, o.key || 2200, 160, .45, .55, 1.2); key.position.set(-18, 44, 34); s.add(key); s.add(key.target);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 700, 90); rim.position.set(20, 16, -14); s.add(rim);
    return key;
  }

  // ---------- Dünya küresi (vertex renkli, deniz seviyesi enleme göre değişebilir) ----------
  const RG = 10;
  function landN(x, y, z) { return .9 * Math.sin(x * 2.1 + 1.3) * Math.cos(y * 1.7 - .4) + .7 * Math.sin(z * 2.6 + x * .8) + .45 * hash(x * 2.2, y * 2.2, z * 2.2) + .25 * hash(x * 5, y * 5, z * 5); }
  function space(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#071430', '#010205'])); s.fog = null;
    s.add(new THREE.HemisphereLight(0x6f8fcf, 0x05060a, o.hemi ?? .35));
    const sun = new THREE.DirectionalLight(0xfff2dc, o.sun ?? 3.2); sun.position.set(-30, 12, 22); s.add(sun);
    const rim = new THREE.DirectionalLight(o.rim || 0x3f9bff, 1.4); rim.position.set(30, 6, -25); s.add(rim);
    const st = dust(1600, [500, 500, 200], 0xffffff, .6, .8); st.position.z = -160; s.add(st);
    return { sun, rim, st };
  }
  function globe(s) {
    const g = new THREE.Group(); s.add(g);
    const geo = new THREE.SphereGeometry(RG, 160, 110); const pos = geo.attributes.position; const n = pos.count;
    const E = new Float32Array(n), LAT = new Float32Array(n);
    for (let i = 0; i < n; i++) { const x = pos.getX(i) / RG, y = pos.getY(i) / RG, z = pos.getZ(i) / RG; E[i] = landN(x, y, z); LAT[i] = Math.abs(y); }
    const col = new Float32Array(n * 3); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const cDeep = new THREE.Color(0x0a3a78), cSh = new THREE.Color(0x1f74b8), cG = new THREE.Color(0x4f7d3a), cB = new THREE.Color(0x9a7b4f), cI = new THREE.Color(0xeef4ff), c = new THREE.Color();
    function paint(k, ice = 1) {
      for (let i = 0; i < n; i++) {
        const sea = .35 + k * (3.4 * LAT[i] - 1.75); const e = E[i] - sea;
        if (e > 0) { c.copy(cG).lerp(cB, clamp(e * 1.1 + (1 - LAT[i]) * .25 * k)); }
        else c.copy(cSh).lerp(cDeep, clamp(-e * 2.2));
        if (ice && LAT[i] > .93) c.lerp(cI, clamp((LAT[i] - .93) * 25) * ice);
        col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
      }
      geo.attributes.color.needsUpdate = true;
    }
    paint(0);
    const earth = M(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .75, metalness: .05 })); g.add(earth);
    // bulutlar
    const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 512; const x = cv.getContext('2d');
    for (let i = 0; i < 420; i++) { const cx = r1() * 1024, cy = 60 + r1() * 392, r = 6 + r1() * 22; const gr = x.createRadialGradient(cx, cy, 0, cx, cy, r);
      gr.addColorStop(0, 'rgba(255,255,255,.4)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.beginPath(); x.ellipse(cx, cy, r * 2.2, r, 0, 0, 7); x.fill(); }
    const ct = new THREE.CanvasTexture(cv); ct.colorSpace = THREE.SRGBColorSpace;
    const clouds = M(new THREE.SphereGeometry(RG * 1.018, 96, 64), new THREE.MeshStandardMaterial({ map: ct, transparent: true, opacity: .85, depthWrite: false })); g.add(clouds);
    const atm = M(new THREE.SphereGeometry(RG * 1.09, 64, 48), new THREE.MeshBasicMaterial({ color: 0x4aa8ff, transparent: true, opacity: .16, side: THREE.BackSide, blending: THREE.AdditiveBlending, depthWrite: false })); g.add(atm);
    g.rotation.z = .41;
    return { g, earth, clouds, atm, paint };
  }
  function camOrbit(cam, D, a = 0, y = 0, ly = .8) { cam.position.set(Math.sin(a) * D, y, Math.cos(a) * D); cam.lookAt(0, ly, 0); }

  // karınca
  function ant() {
    const g = new THREE.Group(); const m = std(0x4a1d10, { roughness: .32, metalness: .25 });
    const ab = M(new THREE.SphereGeometry(.55, 32, 24), m); ab.scale.set(1.35, 1, 1); ab.position.x = -1.1; g.add(ab);
    const th = M(new THREE.SphereGeometry(.32, 24, 18), m); th.scale.set(1.5, .9, .9); g.add(th);
    const hd = M(new THREE.SphereGeometry(.36, 24, 18), m); hd.position.x = .75; hd.position.y = .1; g.add(hd);
    const lm = std(0x2a0f08, { roughness: .4 });
    for (let i = 0; i < 3; i++) for (const k of [-1, 1]) { const l = new THREE.Group(); l.position.set(-.25 + i * .25, -.05, k * .2); g.add(l);
      const a = M(new THREE.CylinderGeometry(.045, .04, .7, 8), lm); a.position.set(0, .1, k * .3); a.rotation.x = k * 1.1; l.add(a);
      const b = M(new THREE.CylinderGeometry(.04, .03, .8, 8), lm); b.position.set((i - 1) * .15, -.3, k * .62); b.rotation.x = -k * .35; l.add(b); }
    for (const k of [-1, 1]) { const an = M(new THREE.CylinderGeometry(.025, .02, .8, 6), lm); an.position.set(1.15, .45, k * .18); an.rotation.z = -.9; an.rotation.x = k * .3; g.add(an); }
    return g;
  }

  const S1 = 2.9, S2 = 5.3, S3 = 9.2, S4 = 12.3, S5 = 16.8, S6 = 19.7, S7 = 26.9, S8 = 31.3, S9 = 34.6;

  // 1) Uzayda dönen Dünya
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const sp = space(s); const G = globe(s);
    return t => { G.earth.rotation.y = t * .5; G.clouds.rotation.y = t * .55; sp.st.rotation.z = t * .01;
      camOrbit(cam, lerp(92, 76, ease(prog(t, 0, S1))), -.15 + t * .03, 3); };
  } });
  // 2) Aniden durur — kırmızı uyarı
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const sp = space(s, { rim: 0xff3b2a }); const G = globe(s);
    const ring = M(new THREE.TorusGeometry(RG * 1.1, .12, 12, 128), new THREE.MeshBasicMaterial({ color: 0xff4a2a, transparent: true, opacity: .8, blending: THREE.AdditiveBlending }));
    s.add(ring); const red = new THREE.PointLight(0xff3020, 0, 80); red.position.set(14, 0, 18); s.add(red);
    const stopT = S1 + .9;
    return t => {
      const a = t < stopT ? (t - S1) * 1.6 : (stopT - S1) * 1.6 + .25 * (1 - Math.exp(-(t - stopT) * 8));
      G.earth.rotation.y = a; G.clouds.rotation.y = a + Math.max(0, t - stopT) * 1.4;
      const k = prog(t, stopT, 1.2); ring.scale.setScalar(1 + k * .8); ring.material.opacity = (1 - k) * .9 * (t > stopT ? 1 : 0); red.intensity = 900 * (t > stopT ? (1 - k * .6) : 0);
      const sh = t > stopT && t < stopT + .4 ? Math.sin(t * 90) * .5 : 0;
      camOrbit(cam, 74, .1 + sh * .01, 3 + sh); };
  } });
  // 3) Ekvator hızı 1.670 km/sa
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    space(s); const G = globe(s); G.g.rotation.z = .12;
    const eq = M(new THREE.TorusGeometry(RG * 1.03, .1, 12, 160), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); eq.rotation.x = Math.PI / 2; G.g.add(eq);
    const mk = new THREE.Group(); G.g.add(mk);
    const pin = M(new THREE.SphereGeometry(.45, 24, 16), new THREE.MeshBasicMaterial({ color: 0xffffff })); mk.add(pin);
    const tr = []; for (let i = 0; i < 14; i++) { const p = M(new THREE.SphereGeometry(.32 - i * .02, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: .8 - i * .05, blending: THREE.AdditiveBlending })); G.g.add(p); tr.push(p); }
    return t => {
      const a = (t - S2) * 1.1; G.earth.rotation.y = a; G.clouds.rotation.y = a * 1.02;
      const put = (o, b) => o.position.set(Math.sin(b) * RG * 1.04, 0, Math.cos(b) * RG * 1.04);
      put(pin, a + .3); tr.forEach((p, i) => put(p, a + .3 - i * .06));
      camOrbit(cam, lerp(90, 84, ease(prog(t, S2, 3.9))), .1, lerp(10, 16, ease(prog(t, S2, 3.9))), -3.2); };
  } });
  // 4) Dünya durdu, atmosfer dönmeye devam
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    space(s); const G = globe(s); G.earth.rotation.y = 1.2;
    const st = []; for (let i = 0; i < 70; i++) { const lat = (r1() - .5) * 1.8; const r = RG * (1.05 + r1() * .12) * Math.cos(lat * .9);
      const c = M(new THREE.TorusGeometry(r, .05 + r1() * .05, 6, 64, .5 + r1() * .8), new THREE.MeshBasicMaterial({ color: i % 3 ? 0xbfe6ff : 0x5fb8ff, transparent: true, opacity: .7, blending: THREE.AdditiveBlending, depthWrite: false }));
      c.rotation.x = Math.PI / 2; c.position.y = Math.sin(lat * .9) * RG * 1.05; c.userData = { sp: 1.5 + r1() * 1.8, o: r1() * 7 }; G.g.add(c); st.push(c); }
    return t => {
      G.clouds.rotation.y = (t - S3) * 1.6; st.forEach(c => c.rotation.z = c.userData.o + (t - S3) * c.userData.sp);
      camOrbit(cam, lerp(66, 72, ease(prog(t, S3, 3.1))), -.25 + (t - S3) * .04, 6); };
  } });
  // 5) Yerde: ses hızından hızlı rüzgâr
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#1b2f52', '#04070f'], near: 30, far: 110 }); key.target.position.set(0, 2, 0);
    const gr = M(new THREE.CylinderGeometry(60, 60, 1, 64), std(0x2b3a2a, { roughness: .95 })); gr.position.y = -.5; s.add(gr);
    const houses = [], trees = [], deb = [];
    for (let i = 0; i < 5; i++) { const h = new THREE.Group(); h.position.set(-12 + i * 6, 0, -3 - (i % 2) * 5); s.add(h);
      const b = M(rb(3.4, 2.6, 3, .1), std([0xb9a68c, 0x9a8a78, 0xc8b8a0][i % 3], { roughness: .8 })); b.position.y = 1.3; h.add(b);
      const win = M(new THREE.PlaneGeometry(.8, .8), new THREE.MeshBasicMaterial({ color: 0xffd27a })); win.position.set(0, 1.4, 1.51); h.add(win);
      const roof = M(new THREE.ConeGeometry(2.7, 1.6, 4), std(0x8b2b20, { roughness: .7 })); roof.rotation.y = Math.PI / 4; roof.position.y = 3.4; h.add(roof);
      houses.push({ h, roof, d: r1() }); }
    for (let i = 0; i < 9; i++) { const tr = new THREE.Group(); tr.position.set(-16 + i * 4 + r1(), 0, 3 + r1() * 3); s.add(tr);
      const tk = M(new THREE.CylinderGeometry(.18, .26, 2.6, 12), std(0x4a3222)); tk.position.y = 1.3; tr.add(tk);
      const cr = M(new THREE.SphereGeometry(1.2, 20, 14), std(0x2f6a34, { roughness: .8 })); cr.position.y = 3; cr.scale.y = 1.2; tr.add(cr); trees.push({ tr, d: r1() }); }
    for (let i = 0; i < 60; i++) { const d = M(rb(.3 + r1() * .4, .1, .3, .03), std([0x8b2b20, 0x6b5a4a, 0x2f6a34][i % 3])); d.userData = { y: .5 + r1() * 7, z: -8 + r1() * 14, o: r1() * 50, s: 18 + r1() * 14 }; s.add(d); deb.push(d); }
    const streak = []; for (let i = 0; i < 90; i++) { const l = M(new THREE.BoxGeometry(3 + r1() * 5, .04, .04), new THREE.MeshBasicMaterial({ color: 0xcfe8ff, transparent: true, opacity: .55, blending: THREE.AdditiveBlending, depthWrite: false }));
      l.userData = { y: r1() * 10, z: -12 + r1() * 22, o: r1() * 60, s: 40 + r1() * 30 }; s.add(l); streak.push(l); }
    const W0 = S4 + .4;
    return t => {
      const w = prog(t, W0, .8); const lt = t - W0;
      streak.forEach(l => { const u = l.userData; l.position.set(((u.o + t * u.s) % 60) - 30, u.y, u.z); l.visible = w > 0; });
      trees.forEach(({ tr, d }) => { tr.rotation.z = -w * (.55 + .2 * Math.sin(t * 9 + d * 9)); if (lt > 1.5 + d * 2) { const a = lt - 1.5 - d * 2; tr.position.x += .0; tr.rotation.z = -.6 - a * 2; tr.children[1].position.x = a * 6; tr.children[1].position.y = 3 + a * 1.5; } });
      houses.forEach(({ roof, d }) => { const a = Math.max(0, lt - .6 - d * 1.5); roof.position.set(a * 9, 3.4 + a * 1.2 - a * a * .3, 0); roof.rotation.z = -a * 2.5; });
      deb.forEach(d => { const u = d.userData; d.visible = w > 0; d.position.set(((u.o + t * u.s) % 50) - 25, u.y + Math.sin(t * 5 + u.o) * .5, u.z); d.rotation.set(t * 5 + u.o, t * 3, t * 7); });
      cam.position.set(lerp(-6, 2, ease(prog(t, S4, 4.5))), 9, 50); cam.lookAt(0, 5.2, 0); cam.position.y += w * Math.sin(t * 50) * .08; };
  } });
  // 6) Dev dalga kıyı şehrini yutar
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#13284a', '#02050b'], near: 40, far: 140, rim: 0x2f9bff }); key.target.position.set(0, 4, 0);
    const land = M(rb(40, 2, 40, .3), std(0x30353d, { roughness: .9 })); land.position.set(22, -1, 0); s.add(land);
    const blds = []; for (let i = 0; i < 22; i++) { const h = 3 + r1() * 9; const b = M(rb(2.2, h, 2.2, .08), std(0x2a3240, { roughness: .7, metalness: .3 }));
      b.position.set(6 + (i % 6) * 3.2 + r1(), h / 2, -10 + Math.floor(i / 6) * 5 + r1()); s.add(b);
      const wn = M(new THREE.PlaneGeometry(1.2, h * .7), new THREE.MeshBasicMaterial({ color: 0xffd27a, transparent: true, opacity: .35 })); wn.position.set(b.position.x, h / 2, b.position.z + 1.12); s.add(wn); blds.push({ b, wn, h }); }
    const geo = new THREE.PlaneGeometry(110, 50, 180, 60); geo.rotateX(-Math.PI / 2); const P = geo.attributes.position; const X0 = Float32Array.from({ length: P.count }, (_, i) => P.getX(i)); const Z0 = Float32Array.from({ length: P.count }, (_, i) => P.getZ(i));
    const water = M(geo, std(0x1a5d92, { roughness: .2, metalness: .35 })); water.position.x = -10; s.add(water);
    const foam = dust(500, [4, 3, 40], 0xffffff, .35, .8); s.add(foam);
    return t => {
      const k = ease(prog(t, S5, 2.7)); const xc = lerp(-40, 26, k);
      for (let i = 0; i < P.count; i++) { const x = X0[i] - 10, z = Z0[i]; const d = x - xc;
        const crest = 7 * Math.exp(-d * d / (d > 0 ? 6 : 60)); const behind = d < 0 ? 2.5 * clamp(-d / 4) : 0;
        P.setY(i, crest + behind + .4 * Math.sin(x * .5 + t * 3) * Math.cos(z * .4 + t * 2)); }
      P.needsUpdate = true; geo.computeVertexNormals();
      foam.position.set(xc + 1, 7, 0); foam.rotation.x = t * .5;
      blds.forEach(({ b, wn, h }) => { const a = clamp((xc - b.position.x + 2) / 6); b.rotation.z = -a * .5; b.position.y = h / 2 - a * h * .6; wn.visible = a < .2; });
      cam.position.set(lerp(-14, -6, k), 22, 66); cam.lookAt(6, 9, 0); };
  } });
  // 7) Yavaşça dursa: sular kutuplara, ekvatorda dev kıta
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    space(s, { sun: 3.6 }); const G = globe(s); G.g.rotation.z = .05; G.clouds.visible = false;
    let lastK = -1;
    return t => {
      const spin = Math.max(0, 1 - (t - S6) / 3.2); G.earth.rotation.y = .4 + (t - S6) * .5 * spin + (t - S6 > 3.2 ? 0 : 0) + (t - S6) * .12;
      const k = ease(prog(t, 22.9, 3.4)); const kq = Math.round(k * 60) / 60; if (kq !== lastK) { G.paint(kq, 1 - kq); lastK = kq; }
      camOrbit(cam, lerp(78, 70, ease(prog(t, S6, 7.2))), -.1, lerp(4, 16, ease(prog(t, 22.9, 3.4))), .2); };
  } });
  // 8) 1 gün = 1 yıl: Güneş etrafında, yarısı karanlık
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    s.background = gradTex('#050b1c', '#000000');
    s.add(new THREE.HemisphereLight(0x6f8fcf, 0x05060a, .06));
    const st = dust(1600, [500, 500, 200], 0xffffff, .6, .8); st.position.z = -160; s.add(st);
    const sunL = new THREE.DirectionalLight(0xfff2dc, 4); s.add(sunL);
    const G = globe(s); G.g.rotation.z = .05; G.paint(0);
    const sunM = M(new THREE.SphereGeometry(2.4, 32, 24), new THREE.MeshBasicMaterial({ color: 0xffd36a })); s.add(sunM);
    const halo = M(new THREE.SphereGeometry(4.5, 32, 24), new THREE.MeshBasicMaterial({ color: 0xff9a2a, transparent: true, opacity: .25, blending: THREE.AdditiveBlending, depthWrite: false })); sunM.add(halo);
    const orbit = M(new THREE.TorusGeometry(17, .05, 6, 160), new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: .4 })); orbit.rotation.x = Math.PI / 2; s.add(orbit);
    return t => {
      const a = 2.45 + (t - S7) * .3; sunM.position.set(Math.cos(a) * 17, 0, Math.sin(a) * 17); sunL.position.copy(sunM.position);
      halo.scale.setScalar(1 + .06 * Math.sin(t * 6));
      camOrbit(cam, 92, 0, 24, -1.2); G.earth.rotation.y = .3 + (t - S7) * .02; };
  } });
  // 9) Neyse ki: Dünya dönmeye devam ediyor
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    space(s, { sun: 3.4, rim: 0x6fd0ff }); const G = globe(s);
    return t => { G.earth.rotation.y = 2 + t * .35; G.clouds.rotation.y = 2 + t * .38;
      camOrbit(cam, lerp(80, 70, ease(prog(t, S8, 3.3))), .2 - (t - S8) * .04, 4); };
  } });
  // 10) Sıradaki soru: gökdelenden düşen karınca
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#1a2f58', '#03060d'], near: 50, far: 170, key: 1800, rim: 0xff9a3a }); key.target.position.set(0, 0, 0);
    const tower = new THREE.Group(); s.add(tower);
    const tw = M(rb(10, 80, 10, .3), std(0x1d2633, { metalness: .6, roughness: .35 })); tw.position.set(-8, -40, -4); tower.add(tw);
    const wm = [0xffd27a, 0x9fd3ff, 0x101824].map(c => new THREE.MeshBasicMaterial({ color: c }));
    for (let y = -78; y < -1; y += 2.2) for (let x = -12; x <= -4; x += 2) { const w = M(new THREE.PlaneGeometry(1.1, 1.3), wm[(r1() * 3.4) | 0 % 3] || wm[2]); w.position.set(x, y, 1.02); tower.add(w); }
    const ledge = M(rb(11, .6, 11, .15), std(0x3a4350, { metalness: .5 })); ledge.position.set(-8, .3, -4); tower.add(ledge);
    for (let i = 0; i < 14; i++) { const h = 10 + r1() * 40; const b = M(new THREE.BoxGeometry(6, h, 6), std(0x141c28, { roughness: .8 })); b.position.set(-40 + i * 7 + r1() * 3, -80 + h / 2, -40 - r1() * 30); s.add(b); }
    const A = ant(); A.scale.setScalar(1.6); s.add(A);
    const d = dust(500, [60, 60, 40], 0x9fc4ff, .2, .45); s.add(d);
    const jump = S9 + 1.4;
    return t => {
      if (t < jump) { A.position.set(-3.9 + (t - S9) * .5, 1.55, 0); A.rotation.set(0, 0, 0); A.children.forEach((c, i) => { if (c.type === 'Group') c.rotation.y = Math.sin(t * 14 + i) * .3; }); }
      else { const a = t - jump; A.position.set(-3.2 + a * 1.2, 1.55 - a * 2.6 + Math.sin(a * 3) * .3, Math.sin(a * 1.7) * .8); A.rotation.set(a * 1.3, a * .9, -a * 2.1); }
      d.rotation.y = t * .03;
      const fy = t < jump ? 1.5 : 1.55 - (t - jump) * 2.6;
      cam.position.set(10, fy + 5, 34); cam.lookAt(-1, fy + 1.2, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'DÜNYA DÖNMEYİ <span class="y">DURDURSA?</span>', 104) },
    { t0: S1, t1: S2, html: T('CEVAP', 'TAM BİR <span class="y">FELAKET</span>') },
    { t0: S2, t1: S3, html: `<div class="grad"></div><div class="tagw"><span class="tag">EKVATORDA DÖNÜŞ HIZI</span></div><div class="big" style="top:310px;font-size:160px" id="v1"></div><div class="sub" style="top:478px">KM/SAAT</div>` },
    { t0: S3, t1: S4, html: T('DÜNYA DURSA BİLE', 'ATMOSFER <span class="y">DURMAZ</span>') },
    { t0: S4, t1: S5, html: T('RÜZGÂR', 'SES HIZINDAN <span class="y">HIZLI</span>') },
    { t0: S5, t1: S6, html: T('OKYANUSLAR', 'DEV <span class="y">DALGALAR</span>') },
    { t0: S6, t1: 22.88, html: T('YAVAŞ YAVAŞ DURSA', 'HER ŞEY <span class="y">DEĞİŞİR</span>') },
    { t0: 22.88, t1: S7, html: T('SULAR KUTUPLARA', 'EKVATORDA <span class="y">TEK DEV KITA</span>', 100) },
    { t0: S7, t1: 29.1, html: T('GÜN UZUNLUĞU', '1 GÜN = <span class="y">1 YIL</span>') },
    { t0: 29.1, t1: S8, html: T('GÜN UZUNLUĞU', '6 AY GÜNDÜZ <span class="y">6 AY GECE</span>', 100) },
    { t0: S8, t1: S9, html: T('NEYSE Kİ', 'BİLİNEN BİR <span class="y">SEBEP YOK</span>', 104) },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'KARINCA DÜŞÜNCE NEDEN <span class="y">ÖLMEZ?</span>', 92) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const fmt = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return {
    END: 40.52, shots, titles,
    update: (t, q) => { if (q('v1')) q('v1').innerHTML = fmt(1670 * easeOut(prog(t, S2 + .3, 2.6))); },
    follow: { t: 38.64, click: 39.62 },
    sfx: [[S1 + .9, 'boom', 1], [S1 + .92, 'crunch', .8], [6.9, 'ding', .7], [S3 + .3, 'whoosh', .8], [S4 + .4, 'whoosh', 1], [S4 + 1.2, 'crunch', .7], [S4 + 2.2, 'snap', .6], [S5 + .3, 'whoosh', 1], [S5 + 1.6, 'boom', 1], [S5 + 1.8, 'crunch', 1], [22.9, 'pop_low', .9], [27.3, 'pop', .8], [29.2, 'pop', .8], [S8 + .2, 'ding', .6], [S9 + 1.4, 'pop', .8]],
  };
};
