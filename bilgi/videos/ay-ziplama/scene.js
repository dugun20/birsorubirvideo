// Bilgi #7: Ay'da zıplasan ne kadar yükseğe çıkarsın? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Space.com "How high can we jump on other worlds?" (Ay yerçekimi ~0,165 g; Dünya'da ~60 cm sıçrama -> Ay'da ~3,6 m);
// aynı kalkış hızıyla havada kalma süresi t = 2v/g -> 6 kat (Dünya 0,7 sn -> Ay ~4,2 sn);
// Business Insider (2019) Charlie Duke röportajı: Apollo 16'da ~4 ft (1,2 m) zıpladı, sırtüstü düştü; sırt çantası "benim kadar ağırdı",
// kırılsaydı havasız kalacaktı. Space.com: giysiler yüzünden astronotlar sekerek ilerledi.
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 47; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const U = 2.2; // 1 metre = 2.2 birim (astronot ~1,8 m)
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
  // Ay yüzeyi + gökyüzü
  function moon(s, o = {}) {
    s.background = gradTex(o.top || '#0b1838', '#000000'); s.fog = new THREE.Fog(0x02040a, o.near || 60, o.far || 170);
    s.add(new THREE.HemisphereLight(0x8fa8d0, 0x0a0a0a, .45));
    const sun = new THREE.DirectionalLight(0xfff4e0, 3); sun.position.set(-20, 22, 16); s.add(sun);
    const rim = new THREE.PointLight(o.rim || 0x5fb0ff, 500, 80); rim.position.set(16, 12, -10); s.add(rim);
    const geo = new THREE.PlaneGeometry(160, 110, 180, 120); geo.rotateX(-Math.PI / 2); const P = geo.attributes.position;
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), z = P.getZ(i); let y = .45 * hash(x * .3, 0, z * .3) + .15 * hash(x * 1.3, 1, z * 1.3);
      for (const [cx, cz, r] of [[-9, -7, 4], [11, -15, 6], [6, 7, 2.2], [-20, 3, 5], [24, -4, 3.5], [-4, -22, 7]]) { const d = Math.hypot(x - cx, z - cz) / r; if (d < 1.3) y += d < 1 ? -1.3 * (1 - d * d) : .8 * (1.3 - d) / .3 * (d - 1) / .3; }
      if (Math.abs(x) < 6 && Math.abs(z) < 4) y *= .3;
      P.setY(i, y); }
    geo.computeVertexNormals(); s.add(M(geo, std(0x8f8f94, { roughness: 1 })));
    const st = dust(1400, [420, 220, 60], 0xffffff, .55, .85); st.position.set(0, 70, -130); s.add(st);
    if (o.earth !== false) { const e = M(new THREE.SphereGeometry(5, 48, 32), std(0x2f6fd0, { roughness: .6, emissive: 0x0a2050 })); e.position.set(o.ex ?? 18, o.ey ?? 44, -110); s.add(e); }
    return sun;
  }
  // astronot: grup kökeni ayak tabanında
  function astro() {
    const g = new THREE.Group(); const inner = new THREE.Group(); inner.position.y = 1.96; g.add(inner);
    const suit = std(0xf2f2f2, { roughness: .6 }); const grey = std(0x9aa0a8, { roughness: .5, metalness: .3 });
    inner.add(M(new THREE.CapsuleGeometry(.75, 1.1, 10, 24), suit));
    const helm = M(new THREE.SphereGeometry(.62, 32, 24), suit); helm.position.y = 1.45; inner.add(helm);
    const visor = M(new THREE.SphereGeometry(.5, 32, 20, 0, Math.PI, 0, Math.PI), std(0xd4a020, { metalness: 1, roughness: .1 })); visor.position.set(0, 1.45, .18); inner.add(visor);
    const pack = M(rb(1.3, 1.6, .7, .12), suit); pack.position.set(0, .35, -.75); inner.add(pack);
    const pk2 = M(rb(1.0, .35, .5, .08), grey); pk2.position.set(0, 1.25, -.8); inner.add(pk2);
    const chest = M(rb(.7, .4, .3, .06), grey); chest.position.set(0, .3, .68); inner.add(chest);
    const arms = [], legs = [];
    for (const k of [-1, 1]) {
      const ap = new THREE.Group(); ap.position.set(k * .88, .75, 0); inner.add(ap);
      const a = M(new THREE.CapsuleGeometry(.22, .85, 6, 14), suit); a.position.y = -.55; ap.add(a);
      const gl = M(new THREE.SphereGeometry(.2, 16, 12), grey); gl.position.y = -1.1; ap.add(gl); ap.rotation.z = k * .25; arms.push(ap);
      const lp = new THREE.Group(); lp.position.set(k * .35, -.6, 0); inner.add(lp);
      const l = M(new THREE.CapsuleGeometry(.28, .8, 6, 14), suit); l.position.y = -.68; lp.add(l);
      const b = M(rb(.5, .3, .75, .1), grey); b.position.set(0, -1.2, .1); lp.add(b); legs.push(lp);
    }
    g.userData = { inner, arms, legs, pack };
    return g;
  }
  function crouch(A, k) { // k: 0 düz, 1 çömelmiş
    const u = A.userData; u.legs.forEach(l => l.rotation.x = -k * .5); u.inner.position.y = 1.96 - k * .25;
    u.arms.forEach((a, i) => { a.rotation.x = -k * .6; });
  }
  function person(body) {
    const g = new THREE.Group();
    g.add(M(new THREE.CapsuleGeometry(.3, .5, 8, 16), std(body, { roughness: .7 })));
    const head = M(new THREE.SphereGeometry(.27, 24, 16), std(0xd9b49a, { roughness: .6 })); head.position.y = .75; g.add(head);
    const arms = []; for (const k of [-1, 1]) { const a = M(new THREE.CapsuleGeometry(.1, .55, 6, 12), std(body)); a.position.set(k * .42, .15, 0); g.add(a); arms.push(a); }
    const legs = []; for (const k of [-1, 1]) { const l = M(new THREE.CapsuleGeometry(.12, .6, 6, 12), std(0x22303f)); l.position.set(k * .16, -.75, 0); g.add(l); legs.push(l); }
    g.userData = { arms, legs }; return g;
  }
  // ölçü direği (metre çizgileri)
  function pole(s, x, z, m) {
    const g = new THREE.Group(); g.position.set(x, 0, z); s.add(g);
    const p = M(rb(.35, m * U, .35, .1), std(0x2a3240, { metalness: .6, roughness: .35 })); p.position.y = m * U / 2; g.add(p);
    const tick = new THREE.MeshBasicMaterial({ color: 0x7ee0ff });
    for (let i = 1; i <= m * 2; i++) { const t = M(new THREE.BoxGeometry(i % 2 ? .45 : .8, .06, .06), tick); t.position.set(-.3, i * U / 2, .2); g.add(t); }
    const mk = M(rb(1.6, .14, .5, .05), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); g.add(mk);
    return mk;
  }
  function puff(s) { const p = dust(160, [3, .6, 3], 0xbdbdbd, .2, .6); s.add(p); p.material.opacity = 0;
    p.userData.at = (x, z, k) => { p.position.set(x, .3 + k * .6, z); p.scale.setScalar(.5 + k * 2.4); p.material.opacity = k > 0 && k < 1 ? (1 - k) * .65 : 0; }; return p; }
  function planetTex(kind) {
    const c = document.createElement('canvas'); c.width = 512; c.height = 256; const g = c.getContext('2d');
    if (kind === 'earth') { g.fillStyle = '#1d4fa8'; g.fillRect(0, 0, 512, 256);
      for (let i = 0; i < 28; i++) { g.fillStyle = r1() > .4 ? '#3f8a3a' : '#9a7b4a'; g.beginPath(); g.ellipse(r1() * 512, 40 + r1() * 176, 20 + r1() * 50, 10 + r1() * 30, r1() * 3, 0, 7); g.fill(); }
      g.fillStyle = 'rgba(255,255,255,.55)'; for (let i = 0; i < 40; i++) { g.beginPath(); g.ellipse(r1() * 512, r1() * 256, 10 + r1() * 40, 3 + r1() * 6, 0, 0, 7); g.fill(); }
      g.fillStyle = '#eef'; g.fillRect(0, 0, 512, 14); g.fillRect(0, 242, 512, 14);
    } else { g.fillStyle = '#9a9a9e'; g.fillRect(0, 0, 512, 256);
      for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(${r1() > .5 ? '60,60,66' : '190,190,196'},${.3 + r1() * .4})`; g.beginPath(); g.arc(r1() * 512, r1() * 256, 3 + r1() * 26, 0, 7); g.fill(); } }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  function arrow(color) { const g = new THREE.Group(); const m = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: .6 });
    const sh = M(new THREE.CylinderGeometry(.12, .12, 1, 16), m); sh.position.y = .5; g.add(sh); const hd = M(new THREE.ConeGeometry(.35, .7, 24), m); hd.rotation.x = Math.PI; g.add(hd);
    g.userData.set = len => { sh.scale.y = Math.max(.01, len); sh.position.y = len / 2 + .3; hd.position.y = .1; }; return g; }
  // kar tanesi (sıradaki soru)
  function flake(r = 3, col = 0xcfefff) {
    const g = new THREE.Group(); const m = new THREE.MeshStandardMaterial({ color: col, emissive: 0x2a5a8a, emissiveIntensity: .5, roughness: .15, metalness: .2, transparent: true, opacity: .92 });
    const c = M(new THREE.CylinderGeometry(r * .22, r * .22, .12, 6), m); c.rotation.x = Math.PI / 2; g.add(c);
    for (let i = 0; i < 6; i++) { const a = new THREE.Group(); a.rotation.z = i * Math.PI / 3; g.add(a);
      const arm = M(rb(r, .16, .1, .04), m); arm.position.x = r / 2; a.add(arm);
      for (const [p, l] of [[.4, .32], [.62, .26], [.82, .16]]) for (const k of [-1, 1]) { const b = M(rb(r * l, .12, .08, .03), m); b.position.set(r * p + Math.cos(k * Math.PI / 3) * r * l / 2, Math.sin(k * Math.PI / 3) * r * l / 2, 0); b.rotation.z = k * Math.PI / 3; a.add(b); }
      const tip = M(new THREE.CylinderGeometry(.18, .18, .1, 6), m); tip.rotation.x = Math.PI / 2; tip.position.x = r; a.add(tip); }
    return g;
  }

  const S1 = 3.15, S1b = 4.75, S2 = 7.55, S3 = 9.55, S4 = 12.25, S5 = 16.98, S6 = 19.62, S7 = 22.9, S8 = 26.75, S8b = 30.36, S8c = 31.3, S9 = 33.7;

  // 1) Ay'da basket potasının üstüne zıplayan astronot
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    moon(s, { ex: -14, ey: 40 }); const A = astro(); s.add(A);
    const hoop = new THREE.Group(); hoop.position.set(3.2, 0, -1.2); s.add(hoop);
    const pm = std(0x39414d, { metalness: .7, roughness: .3 });
    const p = M(new THREE.CylinderGeometry(.16, .2, 8.6, 20), pm); p.position.set(1.4, 4.3, -.6); hoop.add(p);
    const arm = M(rb(1.6, .2, .2, .05), pm); arm.position.set(.7, 7.4, -.6); hoop.add(arm);
    const bd = M(rb(3.6, 2.4, .12, .08), new THREE.MeshStandardMaterial({ color: 0xdfe8f0, transparent: true, opacity: .55, roughness: .2 })); bd.position.set(0, 7.5, -.5); bd.rotation.y = -Math.PI / 2 * 0; hoop.add(bd);
    const sq = M(new THREE.TorusGeometry(.5, .03, 6, 4), new THREE.MeshBasicMaterial({ color: 0xff7c09 })); sq.position.set(0, 7.1, -.42); sq.rotation.z = Math.PI / 4; hoop.add(sq);
    const rim = M(new THREE.TorusGeometry(.75, .06, 12, 40), std(0xff7c09, { metalness: .5, roughness: .3, emissive: 0x401800 })); rim.rotation.x = Math.PI / 2; rim.position.set(0, 6.7, .4); hoop.add(rim);
    const net = M(new THREE.CylinderGeometry(.75, .5, 1.1, 16, 3, true), new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true, transparent: true, opacity: .45 })); net.position.set(0, 6.15, .4); hoop.add(net);
    const pf = puff(s);
    return t => {
      const k = prog(t, .5, 1.9); const h = 7.9 * Math.sin(k * Math.PI / 2);
      crouch(A, t < .5 ? prog(t, .1, .4) : 1 - prog(t, .5, .3));
      A.position.set(-.6 + k * 1.2, h, 0); A.rotation.set(0, .35, 0);
      A.userData.arms.forEach((a, i) => { if (t > .5) a.rotation.z = (i ? 1 : -1) * lerp(.25, 2.4, easeOut(prog(t, .5, .8))); });
      pf.userData.at(-.6, 0, prog(t, .5, 1.2));
      const cy = lerp(4.6, 9.2, ease(prog(t, .3, 2.2)));
      cam.position.set(6, cy - 1.5, 30); cam.lookAt(.8, cy + .2, 0); };
  } });
  // 2) Dünya ve Ay: yerçekimi okları (Ay'da 1/6)
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    s.background = gradTex('#0b1838', '#000000'); s.add(new THREE.HemisphereLight(0x8fa8d0, 0x050505, .35));
    const sun = new THREE.DirectionalLight(0xfff4e0, 3.2); sun.position.set(-14, 10, 12); s.add(sun);
    const rim = new THREE.PointLight(0x5fb0ff, 400, 60); rim.position.set(8, 6, -8); s.add(rim);
    const st = dust(1400, [200, 160, 40], 0xffffff, .4, .8); st.position.z = -60; s.add(st);
    const E = M(new THREE.SphereGeometry(3.6, 72, 48), new THREE.MeshStandardMaterial({ map: planetTex('earth'), roughness: .7, emissive: 0x081a40, emissiveIntensity: .5 })); E.position.set(-1.3, 0, 0); s.add(E);
    const atm = M(new THREE.SphereGeometry(3.85, 48, 32), new THREE.MeshBasicMaterial({ color: 0x4fa8ff, transparent: true, opacity: .14, blending: THREE.AdditiveBlending, depthWrite: false })); atm.position.copy(E.position); s.add(atm);
    const Mo = M(new THREE.SphereGeometry(1.0, 64, 40), new THREE.MeshStandardMaterial({ map: planetTex('moon'), roughness: .95 })); Mo.position.set(4.1, -1.1, 1); s.add(Mo);
    const aE = arrow(0xffcf2e); aE.position.set(-1.3, 3.7, 0); s.add(aE); const aM = arrow(0xffcf2e); aM.position.set(4.1, -.05, 1); s.add(aM);
    return t => {
      E.rotation.y = t * .3; Mo.rotation.y = t * .2; st.rotation.z = t * .01;
      const k = easeOut(prog(t, 4.9, 1.0)); aE.userData.set(.01 + 1.8 * k); aM.userData.set(.01 + .4 * k); aE.visible = aM.visible = k > 0;
      const a = (t - S1) * .05; cam.position.set(Math.sin(a) * 31, 1.5, Math.cos(a) * 31); cam.lookAt(.6, 1.6, 0); };
  } });
  // 3) Dünya'da 60 cm
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#16294a', '#03060d'], near: 30, far: 90 }); key.target.position.set(0, 0, 0);
    const gr = M(new THREE.CylinderGeometry(40, 40, 1, 64), std(0x3b3f45, { roughness: .95 })); gr.position.y = -.5; s.add(gr);
    const P = person(0x1f4fa8); P.scale.setScalar(1.9); s.add(P); const mk = pole(s, 2.6, -.5, 2);
    const d = dust(300, [30, 20, 20], 0x9fc4ff, .14, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = (t - S2 - .3) % 1.0; const h = a > 0 ? .6 * U * Math.sin(clamp(a / .7) * Math.PI) : 0;
      P.position.set(-.6, 2.22 + h, 0); P.userData.arms.forEach((ar, i) => ar.rotation.z = (i ? 1 : -1) * (h > .1 ? 2.2 : .2));
      mk.position.set(0, .6 * U, .1); d.rotation.y = t * .04;
      cam.position.set(2.5, 3.6, 21); cam.lookAt(.6, 3.4, 0); };
  } });
  // 4) Ay'da 3,6 m
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    moon(s, { ex: 20, ey: 50 }); const A = astro(); s.add(A); const mk = pole(s, 3.2, -.6, 4); const pf = puff(s);
    return t => {
      const k = prog(t, S3 + .5, 2.0); const h = 3.6 * U * Math.sin(k * Math.PI / 2);
      crouch(A, t < S3 + .5 ? prog(t, S3, .4) : 1 - prog(t, S3 + .5, .3));
      A.position.set(-.8, h, 0); A.rotation.y = .5; A.userData.arms.forEach((a, i) => { a.rotation.z = (i ? 1 : -1) * lerp(.25, 2.3, easeOut(prog(t, S3 + .5, .8))); });
      mk.position.set(0, h, .1); pf.userData.at(-.8, 0, prog(t, S3 + .5, 1.2));
      const cy = lerp(4.5, 8.5, ease(prog(t, S3 + .3, 2.2)));
      cam.position.set(4, cy - 2, 32); cam.lookAt(1, cy, 0); };
  } });
  // 5) Havada kalma: 6 kat (zamanlayıcı halkası)
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    moon(s, { ex: -16, ey: 46, rim: 0xffb02e }); const A = astro(); s.add(A); const pf = puff(s);
    const ring = []; const off = new THREE.MeshBasicMaterial({ color: 0x23324a }), on = new THREE.MeshBasicMaterial({ color: 0xffcf2e });
    for (let i = 0; i < 48; i++) { const a = Math.PI / 2 - i / 48 * Math.PI * 2; const b = M(rb(.9, .35, .3, .08), off); b.position.set(Math.cos(a) * 6.5, 7 + Math.sin(a) * 6.5, -6); b.rotation.z = a; s.add(b); ring.push(b); }
    const T = 4.2;
    return t => {
      const a = t - S4 - .2; const k = clamp(a / T); const h = 3.6 * U * 4 * k * (1 - k);
      A.position.set(lerp(-5, 5, k), h, 0); A.rotation.set(0, .9, lerp(.12, -.12, k)); crouch(A, a < 0 ? prog(t, S4, .2) : (k >= 1 ? 1 - prog(a, T, .3) : 0));
      A.userData.arms.forEach((ar, i) => ar.rotation.z = (i ? 1 : -1) * (1.2 + Math.sin(t * 2) * .2));
      ring.forEach((b, i) => b.material = i / 48 < k ? on : off);
      pf.userData.at(-5, 0, prog(t, S4 + .2, 1.2));
      cam.position.set(0, 6, 36); cam.lookAt(0, 7.6, 0); };
  } });
  // 6) Sorun: giysi (yakın plan, dönen astronot)
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    moon(s, { earth: false, rim: 0x7fd8ff, near: 30, far: 120 }); const A = astro(); s.add(A);
    const spot = new THREE.SpotLight(0xffffff, 900, 40, .5, .5, 1); spot.position.set(0, 14, 8); spot.target = A; s.add(spot);
    return t => {
      A.position.set(0, 0, 0); A.rotation.y = (t - S5) * .8 - .4; A.userData.arms.forEach((a, i) => a.rotation.z = (i ? 1 : -1) * (.3 + Math.sin(t * 1.5) * .05));
      const k = ease(prog(t, S5, 2.6)); cam.position.set(0, lerp(4, 3.4, k), lerp(16, 12.5, k)); cam.lookAt(0, lerp(3.2, 3.1, k), 0); };
  } });
  // 7) Terazi: sırt çantası ≈ bir insan
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#1a2440', '#03050b'], rim: 0xffcf2e, key: 2600 }); key.target.position.set(0, 3, 0);
    const pl = M(new THREE.CylinderGeometry(9, 9, .6, 64), std(0x232a35, { metalness: .6, roughness: .35 })); pl.position.y = -.3; s.add(pl);
    const metal = std(0xc9a24a, { metalness: .9, roughness: .25 });
    const col = M(new THREE.CylinderGeometry(.25, .4, 5, 24), metal); col.position.y = 2.5; s.add(col);
    const beam = new THREE.Group(); beam.position.y = 5.1; s.add(beam); beam.add(M(rb(10, .3, .4, .1), metal));
    const pans = []; for (const k of [-1, 1]) { const pan = new THREE.Group(); s.add(pan); const d = M(new THREE.CylinderGeometry(1.6, 1.2, .2, 40), metal); pan.add(d);
      for (let i = 0; i < 3; i++) { const a = i / 3 * Math.PI * 2; const st = M(new THREE.CylinderGeometry(.03, .03, 2.6, 6), metal); st.position.set(Math.cos(a) * .7, 1.3, Math.sin(a) * .7); st.rotation.set(Math.sin(a) * -.28, 0, Math.cos(a) * .28); pan.add(st); }
      pans.push([pan, k]); }
    const suit = std(0xf2f2f2, { roughness: .6 }), grey = std(0x9aa0a8, { metalness: .3, roughness: .5 });
    const bag = new THREE.Group(); bag.add(M(rb(1.4, 1.7, .8, .14), suit)); const b2 = M(rb(1.1, .4, .6, .08), grey); b2.position.y = 1.05; bag.add(b2);
    const hose = M(new THREE.TorusGeometry(.45, .08, 10, 24, Math.PI), grey); hose.position.set(.5, .2, .4); hose.rotation.y = Math.PI / 2; bag.add(hose); s.add(bag);
    const P = person(0xb91c1c); P.scale.setScalar(1.1); s.add(P);
    const d = dust(300, [20, 14, 14], 0xffe7a0, .12, .4); d.position.y = 4; s.add(d);
    return t => {
      const k = easeOut(prog(t, S6 + .3, .6)); const tilt = -.3 * (1 - ease(prog(t, S6 + .9, 1.2))) + Math.sin(t * 3) * .008 * k;
      beam.rotation.z = tilt;
      pans.forEach(([p, kk]) => { const x = kk * 4.6 * Math.cos(tilt), y = 5.1 + kk * 4.6 * Math.sin(tilt); p.position.set(x, y - 2.7, 0); });
      bag.position.set(-4.6 * Math.cos(tilt), 5.1 - 4.6 * Math.sin(tilt) - 2.7 + .95 + lerp(4, 0, k), 0); bag.visible = t > S6 + .25;
      P.position.set(4.6 * Math.cos(tilt), 5.1 + 4.6 * Math.sin(tilt) - 2.7 + 1.4, 0);
      d.rotation.y = t * .05;
      const a = (t - S6) * .06; cam.position.set(Math.sin(a) * 4, 6.5, 33); cam.lookAt(0, 5.0, 0); };
  } });
  // 8) Tavşan gibi sekme
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    moon(s, { ex: 14, ey: 42 }); const A = astro(); s.add(A); const pfs = [puff(s), puff(s), puff(s), puff(s), puff(s)];
    return t => {
      const a = t - S7; const ph = a / .8; const i = Math.floor(ph), f = ph - i; const h = 1.3 * Math.sin(f * Math.PI);
      const x = -6 + a * 3.2; A.position.set(x, h, 0); A.rotation.set(0, Math.PI / 2 - .35, -.18 + h * .05);
      A.userData.legs.forEach(l => l.rotation.x = -.35 + h * .15); A.userData.arms.forEach((ar, j) => { ar.rotation.z = (j ? 1 : -1) * .5; ar.rotation.x = -.4; });
      pfs.forEach((p, j) => p.userData.at(-6 + j * .8 * 3.2, .3, j <= i ? prog(a, j * .8, 1) : 0));
      cam.position.set(x * .7 + 1, 4.5, 24); cam.lookAt(x * .7 + 1, 3.6, 0); };
  } });
  // 9) Apollo 16 (1972): Charlie Duke zıplar, sırtüstü düşer
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    moon(s, { ex: -18, ey: 44, top: '#14182a', rim: 0xffb070 });
    const LM = new THREE.Group(); LM.position.set(-9, 0, -12); s.add(LM);
    const gold = std(0xd8a630, { metalness: 1, roughness: .35 });
    const desc = M(new THREE.CylinderGeometry(3, 3, 2.6, 8), gold); desc.position.y = 3; LM.add(desc);
    const asc = M(rb(4, 3.2, 3.6, .3), std(0xb8bcc2, { metalness: .5, roughness: .45 })); asc.position.y = 5.9; LM.add(asc);
    const win = M(new THREE.PlaneGeometry(.9, .7), new THREE.MeshBasicMaterial({ color: 0x0a0f18 })); win.position.set(0, 6.4, 1.81); LM.add(win);
    for (let i = 0; i < 4; i++) { const a = i / 4 * Math.PI * 2 + Math.PI / 4; const l = M(new THREE.CylinderGeometry(.1, .1, 4, 8), gold); l.position.set(Math.cos(a) * 3.4, 1.8, Math.sin(a) * 3.4); l.rotation.set(Math.sin(a) * .5, 0, -Math.cos(a) * .5); LM.add(l);
      const f = M(new THREE.CylinderGeometry(.5, .6, .15, 20), gold); f.position.set(Math.cos(a) * 4.3, .1, Math.sin(a) * 4.3); LM.add(f); }
    const flag = new THREE.Group(); flag.position.set(5.5, 0, -6); s.add(flag);
    const fp = M(new THREE.CylinderGeometry(.06, .06, 6, 8), std(0xdddddd)); fp.position.y = 3; flag.add(fp);
    const fc = document.createElement('canvas'); fc.width = 120; fc.height = 70; const fg = fc.getContext('2d');
    for (let i = 0; i < 7; i++) { fg.fillStyle = i % 2 ? '#fff' : '#c22'; fg.fillRect(0, i * 10, 120, 10); } fg.fillStyle = '#224'; fg.fillRect(0, 0, 50, 38);
    const ft = new THREE.CanvasTexture(fc); ft.colorSpace = THREE.SRGBColorSpace;
    const fl = M(new THREE.PlaneGeometry(2.6, 1.5), new THREE.MeshStandardMaterial({ map: ft, side: THREE.DoubleSide, roughness: .8 })); fl.position.set(1.3, 5.1, 0); flag.add(fl);
    const A = astro(); s.add(A); const pf = puff(s); const pf2 = puff(s);
    const warn = new THREE.PointLight(0xff2a2a, 0, 14); s.add(warn);
    const j0 = S8 + .9, jA = 29.7, land = 30.85;
    return t => {
      let y = 0, rx = 0;
      if (t < j0) crouch(A, prog(t, j0 - .5, .4));
      else if (t < land) { crouch(A, 0); const k = (t - j0) / (land - j0); y = 1.2 * U * 4 * k * (1 - k) + .9 * ease(prog(t, jA, land - jA)); rx = -ease(prog(t, jA, land - jA)) * 1.45; }
      else { crouch(A, 0); y = .9 + Math.abs(Math.sin((t - land) * 7)) * .25 * Math.exp(-(t - land) * 4); rx = -1.45 - Math.sin((t - land) * 7) * .05 * Math.exp(-(t - land) * 4); }
      A.position.set(0, y, 0); A.rotation.set(rx, .6, 0);
      A.userData.arms.forEach((a, i) => a.rotation.z = (i ? 1 : -1) * (t > jA ? lerp(.3, 1.6, prog(t, jA, .6)) : .3));
      pf.userData.at(0, 0, prog(t, j0, 1.2)); pf2.userData.at(-.5, -1, prog(t, land, 1.4));
      warn.position.set(-.3, 1.2, -1.6); warn.intensity = t > S8c ? 200 * (.5 + .5 * Math.sin(t * 9)) : 0;
      const k = ease(prog(t, S8, 6)); cam.position.set(lerp(9, 6, k), lerp(4.5, 3.6, k), lerp(26, 18, k)); cam.lookAt(-.5, lerp(3.4, 2.4, k), 0); };
  } });
  // 10) Sıradaki soru: kar tanesi
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#12305a', '#02060e'], rim: 0x9fe6ff, key: 1600 });
    const F = flake(3.4); F.position.set(0, 5.2, 0); s.add(F);
    const small = []; for (let i = 0; i < 26; i++) { const f = flake(.5 + r1() * .5); f.userData = { x: (r1() - .5) * 26, z: -4 - r1() * 16, o: r1() * 30, r: r1() * 6 }; s.add(f); small.push(f); }
    const glow = new THREE.PointLight(0x9fe6ff, 300, 20); glow.position.set(0, 5.2, 4); s.add(glow);
    return t => {
      const k = back(prog(t, S9, .9)); F.scale.setScalar(Math.max(.01, k)); F.rotation.set(Math.sin(t * .7) * .3, Math.sin(t * .6) * .5, t * .15);
      small.forEach(f => { const u = f.userData; f.position.set(u.x + Math.sin(t + u.r) * .6, 22 - ((u.o + t * 2.2) % 30), u.z); f.rotation.set(t * .5 + u.r, t * .7, u.r); });
      cam.position.set(0, 5.6, 23); cam.lookAt(0, 6.2, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}"></div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'AY\'DA NE KADAR <span class="y">ZIPLARSIN?</span>', 100) },
    { t0: S1, t1: S1b, html: T('ÇÜNKÜ', 'AY\'IN KÜTLESİ <span class="y">KÜÇÜK</span>', 100) },
    { t0: S1b, t1: S2, html: BIG('YERÇEKİMİ', 'g', 'DÜNYA\'NIN ALTIDA BİRİ') },
    { t0: S2, t1: S3, html: BIG('DÜNYA\'DA', 'e', 'ZIPLAMA YÜKSEKLİĞİ') },
    { t0: S3, t1: S4, html: BIG('AY\'DA · AYNI GÜÇLE', 'm', '6 KAT YÜKSEK') },
    { t0: S4, t1: S5, html: BIG('HAVADA KALMA', 's', 'DÜNYA\'DA 0,7 SN') },
    { t0: S5, t1: S6, html: T('AMA', 'SORUN: <span class="y">GİYSİ</span>') },
    { t0: S6, t1: S7, html: T('SIRT ÇANTASI', 'BİR İNSAN <span class="y">KADAR AĞIR</span>', 100) },
    { t0: S7, t1: S8, html: T('BU YÜZDEN', 'TAVŞAN GİBİ <span class="y">SEKEREK</span>', 100) },
    { t0: S8, t1: S8b, html: T('APOLLO 16 · 1972', 'CHARLIE <span class="y">DUKE</span>') + `<div class="sub" style="top:450px">1 METREDEN FAZLA ZIPLADI</div>` },
    { t0: S8b, t1: S8c, html: T('TEHLİKE', 'SIRTÜSTÜ <span class="y">DÜŞTÜ</span>') },
    { t0: S8c, t1: S9, html: T('ÇANTA = HAVA', 'NEREDEYSE <span class="y">ÖLÜYORDU</span>', 100) },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'KAR TANELERİ NEDEN<br>HEP <span class="y">6 KÖŞELİ?</span>', 92) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const f1 = x => x.toFixed(1).replace('.', ',');
  return {
    END: 39.08, shots, titles,
    update: (t, q) => {
      if (q('g')) q('g').innerHTML = '1/6';
      if (q('e')) q('e').innerHTML = Math.round(60 * easeOut(prog(t, S2 + .2, 1.0))) + '<small>CM</small>';
      if (q('m')) q('m').innerHTML = f1(3.6 * easeOut(prog(t, S3 + .5, 1.9))) + '<small>M</small>';
      if (q('s')) q('s').innerHTML = '~' + Math.round(4 * clamp((t - S4 - .2) / 4.2)) + '<small>SN</small>';
    },
    follow: { t: 37.28, click: 38.18 },
    sfx: [[.5, 'pop_low', .8], [4.9, 'ding', .6], [S2 + .3, 'pop', .6], [S2 + 1.3, 'pop', .6], [S3 + .5, 'pop_low', .9], [11.6, 'ding', .7], [S4 + .2, 'pop_low', .6], [16.6, 'ding', .7], [S6 + .3, 'boom', .5],
      [S7 + .8, 'pop_low', .5], [S7 + 1.6, 'pop_low', .5], [S7 + 2.4, 'pop_low', .5], [S7 + 3.2, 'pop_low', .5], [S8 + .9, 'pop_low', .7], [30.85, 'boom', 1], [30.87, 'crunch', .6], [S9 + .1, 'ding', .6]],
  };
};
