// Bilgi #15: Gökyüzü neden mavi? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Royal Museums Greenwich "Why is the sky blue?" (Rayleigh saçılması; mor neden görünmez: güneş ışığında mor daha az,
// göz mora daha az duyarlı; gün batımında ışık daha uzun yol alır, mavi saçılır, kırmızı/turuncu kalır).
// Atmospheric Optics (Les Cowley) "Why is the sky blue?": "450 nm mavi ışık, 650 nm kırmızı ışıktan 4,4 kat daha güçlü saçılır."
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const Y = new THREE.Vector3(0, 1, 0); const V = (x, y, z) => new THREE.Vector3(x, y, z);
  let seed = 1515; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const soft = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.4, 'rgba(255,255,255,.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
  function dust(n, sp, color = 0xcfe8ff, size = .2, op = .5) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
    for (let i = 0; i < n * 3; i += 3) { p[i] = (r1() - .5) * sp[0]; p[i + 1] = (r1() - .5) * sp[1]; p[i + 2] = (r1() - .5) * sp[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color, size, map: soft, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending }));
  }
  function lights(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#0a1838', '#010308'])); s.fog = new THREE.Fog(o.fog || 0x02050e, 30, 110);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi || .7));
    const key = new THREE.DirectionalLight(0xfff4e0, o.key || 2.2); key.position.set(-10, 12, 10); s.add(key);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 600, 60); rim.position.set(6, 9, -5); s.add(rim);
    const d = dust(500, [26, 18, 16], o.dust || 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return { d, rim };
  }
  const glow = (c, op = .9) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false });
  function beam(c, r = .07) { // ışık ışını: iç çekirdek + dış hale
    const g = new THREE.Group(); const core = M(new THREE.CylinderGeometry(r, r, 1, 16, 1, true), glow(c, .95));
    const halo = M(new THREE.CylinderGeometry(r * 3.2, r * 3.2, 1, 16, 1, true), glow(c, .18)); g.add(core); g.add(halo);
    g.userData.set = (a, b) => { const d = b.clone().sub(a); const l = d.length(); g.visible = l > .01; g.scale.set(1, Math.max(.001, l), 1);
      g.position.copy(a).addScaledVector(d, .5); g.quaternion.setFromUnitVectors(Y, d.normalize()); };
    g.userData.op = k => { core.material.opacity = .95 * k; halo.material.opacity = .18 * k; };
    return g;
  }
  function molecule(r = .22, c = 0x9cc4ff) { const g = new THREE.Group(); const m = std(c, { roughness: .3, metalness: .2, emissive: c, emissiveIntensity: .15 });
    [-1, 1].forEach(k => { const a = M(new THREE.SphereGeometry(r, 32, 24), m); a.position.x = k * r * .85; g.add(a); }); g.userData.m = m; return g; }
  const ground = s => { const gr = M(new THREE.CylinderGeometry(40, 40, 1, 64), std(0x0e1c18, { roughness: .95 })); gr.position.y = 1.2; s.add(gr);
    for (let i = 0; i < 6; i++) { const h = M(new THREE.SphereGeometry(4 + r1() * 3, 48, 32), std(0x12241e, { roughness: .9 })); h.position.set(-15 + i * 6, 1.0, -12 - r1() * 6); h.scale.y = .45; s.add(h); } };

  const S1 = 3.84, S2 = 8.0, S3 = 11.84, S4 = 15.04, S5 = 18.72, S6 = 21.44, S6b = 23.12, S7 = 27.04, S7b = 29.52, S8 = 33.2;

  // 1) Güneşten beyaz ışık iner, havada maviye saçılır
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#06163a', '#2a64b0'], fog: 0x0b2850, rim: 0x6fb8ff }); ground(s);
    const sun = M(new THREE.SphereGeometry(.7, 48, 32), new THREE.MeshBasicMaterial({ color: 0xfff6dc, fog: false })); sun.position.set(-1.9, 7.4, -4); s.add(sun);
    const halo = dust(220, [3.2, 3.2, 1], 0xfff0c0, .9, .45); halo.position.copy(sun.position); s.add(halo);
    const B = beam(0xffffff, .09); s.add(B); const end = V(1.3, 3.9, 0);
    const blues = Array.from({ length: 46 }, () => { const b = M(new THREE.SphereGeometry(.08, 12, 8), glow(0x4a9cff)); b.userData = { u: r1(), d: V(r1() - .5, r1() - .5, r1() - .5).normalize(), ph: r1() }; s.add(b); return b; });
    const sky = dust(400, [14, 8, 8], 0x5aa8ff, .35, .35); sky.position.set(0, 6.6, -2); s.add(sky);
    return t => {
      const k = ease(prog(t, .2, 1.4)); B.userData.set(sun.position, sun.position.clone().lerp(end, k));
      blues.forEach(b => { const U = b.userData; const c = ((t * .5 + U.ph) % 1); const st = sun.position.clone().lerp(end, U.u);
        b.visible = k > U.u; b.position.copy(st).addScaledVector(U.d, c * 3.2); b.scale.setScalar(1.2 - c); });
      halo.rotation.z = t * .2; sky.rotation.y = t * .03; sky.material.opacity = .15 + .3 * prog(t, 1, 2); E.d.rotation.y = t * .02;
      cam.position.set(Math.sin(t * .25) * .8, 6.0, lerp(17, 15, ease(prog(t, 0, S1)))); cam.lookAt(0, 6.0, 0); };
  } });
  // 2) Prizma: beyaz ışık renklerine ayrılır
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xb06bff });
    const P = new THREE.Group(); P.position.set(0, 6.0, 0); s.add(P);
    const pg = new THREE.CylinderGeometry(1.25, 1.25, 1.6, 3, 1); pg.rotateX(Math.PI / 2);
    P.add(M(pg, new THREE.MeshStandardMaterial({ color: 0xcfe8ff, transparent: true, opacity: .35, roughness: .05, metalness: .3, emissive: 0x16305a, depthWrite: false })));
    P.add(new THREE.LineSegments(new THREE.EdgesGeometry(pg), new THREE.LineBasicMaterial({ color: 0xe8f6ff })));
    const inB = beam(0xffffff, .07); s.add(inB);
    const cols = [0xff3b30, 0xff8a2a, 0xffe02e, 0x2fd16a, 0x2fb8ff, 0x2f5bff, 0x8a3cff];
    const outs = cols.map(c => { const b = beam(c, .055); s.add(b); return b; });
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02; P.rotation.z = Math.sin(t * .6) * .05; P.rotation.y = Math.sin(t * .4) * .25;
      const k = ease(prog(a, .1, .9)); const hit = V(-.55, 6.15, 0);
      inB.userData.set(V(-5, 5.2, 0), V(-5, 5.2, 0).lerp(hit, k));
      const k2 = easeOut(prog(a, 1.0, 1.4));
      outs.forEach((b, i) => { const st = V(.5, 5.95, 0); const en = V(5.5, 5.4 - i * .42, 0); b.userData.set(st, st.clone().lerp(en, k2)); b.visible = k2 > .01; });
      cam.position.set(Math.sin(a * .2) * 1, 6.1, lerp(15.5, 14, ease(prog(a, 0, 4)))); cam.lookAt(0, 6.0, 0); };
  } });
  // 3) Havadaki milyarlarca molekül (azot ve oksijen), ışık aralarından geçer
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#081a3c', '#010308'], rim: 0x3fb6ff });
    const mols = Array.from({ length: 60 }, (_, i) => { const m = molecule(.17, i % 5 === 0 ? 0xff8a8a : 0x9cc4ff); m.position.set((r1() - .5) * 8, 3.7 + r1() * 3.9, -5 + r1() * 6);
      m.userData.r = V(r1(), r1(), r1()); m.userData.ph = r1() * 6; s.add(m); return m; });
    const B = beam(0xffffff, .08); s.add(B);
    return t => {
      const a = t - S2; E.d.rotation.y = t * .03; const k = ease(prog(a, .3, 1.6)); const A = V(-6, 6.6, 0), Bb = V(6, 5.4, 0); const tip = A.clone().lerp(Bb, k);
      B.userData.set(A, tip);
      mols.forEach(m => { const U = m.userData; m.rotation.set(t * U.r.x * 1.5, t * U.r.y * 1.5, t * U.r.z); m.position.y += Math.sin(t * 1.3 + U.ph) * .002;
        const dd = Math.abs(m.position.y - lerp(6.6, 5.4, (m.position.x + 6) / 12)) + Math.abs(m.position.z) * .3; const lit = m.position.x < tip.x && dd < 1.0;
        U.m && (m.children.forEach(c => c.material.emissiveIntensity = lit ? .9 + .3 * Math.sin(t * 9 + U.ph) : .15)); });
      cam.position.set(lerp(-.8, .8, ease(prog(a, 0, 3.8))), 6.1, 15); cam.lookAt(0, 6.0, -1); };
  } });
  // 4) Saçılma: molekül maviyi her yöne saçar, kırmızı düz geçer
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x3f7bff });
    const mo = molecule(.55, 0x9cc4ff); mo.position.set(0, 6.0, 0); s.add(mo);
    const inB = beam(0xffffff, .08); s.add(inB); const red = beam(0xff3b30, .06); s.add(red);
    const rings = Array.from({ length: 4 }, (_, i) => { const r = M(new THREE.TorusGeometry(1, .03, 8, 96), glow(0x4a9cff, .7)); r.position.copy(mo.position); r.rotation.set(r1() * 3, r1() * 3, 0); r.userData.ph = i / 4; s.add(r); return r; });
    const blues = Array.from({ length: 60 }, () => { const b = M(new THREE.SphereGeometry(.07, 12, 8), glow(0x58a8ff)); b.userData = { d: V(r1() - .5, r1() - .5, r1() - .5).normalize(), ph: r1() }; s.add(b); return b; });
    return t => {
      const a = t - S3; E.d.rotation.y = t * .03; mo.rotation.set(t * .5, t * .7, t * .2);
      inB.userData.set(V(-5, 6, 0), V(-5, 6, 0).lerp(V(-.5, 6, 0), ease(prog(a, 0, .6))));
      const on = prog(a, .6, .3);
      red.userData.set(V(.5, 6, 0), V(.5, 6, 0).lerp(V(5.5, 6, 0), easeOut(prog(a, .6, .8)))); red.visible = on > 0;
      rings.forEach(r => { const c = ((a - .6) * .6 + r.userData.ph) % 1; r.visible = a > .6; r.scale.setScalar(.3 + c * 4); r.material.opacity = .7 * (1 - c) * on; });
      blues.forEach(b => { const c = ((a * .55 + b.userData.ph) % 1); b.visible = a > .6; b.position.copy(mo.position).addScaledVector(b.userData.d, .6 + c * 3.4); b.scale.setScalar(1.3 - c); });
      cam.position.set(Math.sin(a * .3) * 2, 6.3, 14.5); cam.lookAt(0, 6.0, 0); };
  } });
  // 5) İki dalga: kısa dalgalı mavi çok saçılır, uzun dalgalı kırmızı az (4,4 kat)
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7f6bff });
    const mk = (c, n) => Array.from({ length: n }, () => { const b = M(new THREE.SphereGeometry(.075, 12, 8), glow(c)); s.add(b); return b; });
    const bw = mk(0x4a9cff, 110), rw = mk(0xff4a3a, 110);
    const sc = (c, n) => Array.from({ length: n }, () => { const b = M(new THREE.SphereGeometry(.06, 10, 8), glow(c, .8)); b.userData = { x: (r1() - .5) * 6, d: V(r1() - .5, r1() - .5, r1() - .5).normalize(), ph: r1() }; s.add(b); return b; });
    const bs = sc(0x6ab4ff, 44), rs = sc(0xff6a5a, 10);
    return t => {
      const a = t - S4; E.d.rotation.y = t * .03; const k = ease(prog(a, .1, 1.0));
      const wave = (arr, y0, lam, sp) => arr.forEach((b, i) => { const x = -3.4 + i / (arr.length - 1) * 6.8; b.visible = (x + 3.4) / 6.8 < k;
        b.position.set(x, y0 + .42 * Math.sin((x / lam - t * .6) * Math.PI * 2), 0); });
      wave(bw, 7.0, .9); wave(rw, 4.4, 2.1);
      const sct = (arr, y0) => arr.forEach(b => { const c = ((a * .6 + b.userData.ph) % 1); b.visible = a > 1.0; b.position.set(b.userData.x, y0, 0).addScaledVector(b.userData.d, c * 1.8); b.scale.setScalar(1 - c * .8); });
      sct(bs, 7.0); sct(rs, 4.4);
      cam.position.set(Math.sin(a * .3) * 1.2, 5.9, 14.5); cam.lookAt(0, 5.8, 0); };
  } });
  // 6) Atmosferi mavi parlayan Dünya
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    s.background = gradTex('#050a1c', '#000000'); s.add(new THREE.HemisphereLight(0x8fb4ff, 0x000000, .25));
    const sunL = new THREE.DirectionalLight(0xfff4e0, 3); sunL.position.set(-10, 4, 6); s.add(sunL);
    const stars = dust(1400, [140, 140, 40], 0xffffff, .25, .9); stars.position.z = -45; s.add(stars);
    const G = new THREE.Group(); G.position.set(0, 5.3, 0); s.add(G);
    const eg = new THREE.SphereGeometry(2.2, 96, 64); const P = eg.attributes.position; const cc = [];
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i); const n = hash(x * 1.3, y * 1.3, z * 1.3) + .5 * hash(x * 3, y * 3, z * 3);
      const c = Math.abs(y) > 1.9 ? new THREE.Color(0xeef4ff) : (n > .55 ? new THREE.Color().setHSL(.29 - n * .04, .5, .26) : new THREE.Color(0x0d3a7a)); cc.push(c.r, c.g, c.b); }
    eg.setAttribute('color', new THREE.Float32BufferAttribute(cc, 3));
    const earth = M(eg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .7 })); G.add(earth);
    const clouds = dust(900, [1, 1, 1], 0xffffff, .14, .5); { const p = clouds.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const v = V(p.getX(i), p.getY(i), p.getZ(i)).normalize().multiplyScalar(2.27); p.setXYZ(i, v.x, v.y, v.z); } } G.add(clouds);
    const atm = M(new THREE.SphereGeometry(2.62, 64, 48), new THREE.ShaderMaterial({ side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      uniforms: { k: { value: 0 } },
      vertexShader: 'varying vec3 vN; void main(){ vN = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
      fragmentShader: 'uniform float k; varying vec3 vN; void main(){ float i = pow(clamp(0.72 - dot(vN, vec3(0.0,0.0,1.0)), 0.0, 1.0), 2.2); gl_FragColor = vec4(0.25,0.6,1.0,1.0) * i * 1.6 * k; }' }));
    G.add(atm);
    return t => {
      const a = t - S5; earth.rotation.y = t * .15; clouds.rotation.y = t * .18; stars.rotation.z = t * .01;
      atm.material.uniforms.k.value = .3 + .7 * ease(prog(a, .2, 1.2)); G.scale.setScalar(lerp(.75, .92, easeOut(prog(a, 0, 1.2))));
      cam.position.set(0, 5.8, lerp(15, 13.5, ease(prog(a, 0, 2.7)))); cam.lookAt(0, 5.7, 0); };
  } });
  // 7) Tayf çubukları: mor az; göz mora daha az duyarlı
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x8a3cff });
    const fl = M(rb(7.4, .25, 2.4, .1), std(0x1a2230, { metalness: .5, roughness: .4 })); fl.position.set(0, 3.45, 0); s.add(fl);
    const cols = [0x8a3cff, 0x2f6bff, 0x2fd16a, 0xffe02e, 0xff8a2a, 0xff3b30], hs = [1.5, 2.55, 2.75, 2.7, 2.6, 2.35];
    const bars = cols.map((c, i) => { const m = std(c, { emissive: c, emissiveIntensity: .35, roughness: .35, metalness: .2 }); const b = M(rb(.7, 1, .7, .1), m); b.position.x = -2.375 + i * .95; s.add(b); return b; });
    const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); s.add(q);
    const qa = M(new THREE.TorusGeometry(.32, .08, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.09, 12, 8), qm); qd.position.set(-.06, -.55, 0); q.add(qd);
    const eye = new THREE.Group(); eye.position.set(1.5, 7.15, .5); s.add(eye);
    eye.add(M(new THREE.SphereGeometry(.62, 48, 32), std(0xf4f6fa, { roughness: .25 })));
    const iris = M(new THREE.CircleGeometry(.3, 40), std(0x2f7bff, { roughness: .3 })); iris.position.z = .6; eye.add(iris);
    const pupil = M(new THREE.CircleGeometry(.14, 32), new THREE.MeshBasicMaterial({ color: 0x050505 })); pupil.position.z = .61; eye.add(pupil);
    const lid = M(new THREE.SphereGeometry(.66, 48, 32, 0, Math.PI * 2, 0, Math.PI * .32), std(0xd9b49a, { roughness: .6 })); eye.add(lid);
    const sight = beam(0x8a3cff, .03); s.add(sight);
    return t => {
      const a = t - S6; E.d.rotation.y = t * .03;
      bars.forEach((b, i) => { const h = Math.max(.02, hs[i] * easeOut(prog(a, .1 + i * .1, .7))); b.scale.y = h; b.position.y = 3.58 + h / 2; });
      const p2 = a > S6b - S6; q.visible = !p2 && a > .5; q.position.set(-2.375, 3.6 + hs[0] + .9 + Math.sin(t * 3) * .08, 0); q.rotation.y = Math.sin(t * 2) * .3;
      bars[0].material.emissiveIntensity = p2 ? .35 - .3 * prog(a, S6b - S6 + .5, 1.2) : .35 + .3 * Math.sin(t * 5) * (a > .5 ? 1 : 0);
      bars[1].material.emissiveIntensity = p2 ? .35 + .4 * prog(a, S6b - S6 + 1.6, .6) : .35;
      const ek = back(prog(a, S6b - S6 + .3, .5)); eye.visible = p2; eye.scale.setScalar(Math.max(.01, ek));
      eye.rotation.set(.25, -.35 + Math.sin(t * 1.5) * .25, 0); lid.rotation.x = -Math.PI * .1 + (Math.abs(Math.sin(t * 1.3)) > .97 ? .6 : 0);
      sight.visible = p2 && a > S6b - S6 + 1.0; sight.userData.set(eye.position, eye.position.clone().lerp(V(-2.375, 3.6 + hs[0], 0), easeOut(prog(a, S6b - S6 + 1.0, .6))));
      sight.userData.op(.4 + .2 * Math.sin(t * 6));
      cam.position.set(Math.sin(a * .25) * 1.2, 6.0, 15); cam.lookAt(0, 5.6, 0); };
  } });
  // 8) Gün batımı: ışık uzun yol alır, mavi saçılıp kaybolur, kızıl kalır
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    s.fog = new THREE.Fog(0x2a1838, 30, 110);
    const sg = new THREE.SphereGeometry(90, 32, 32); const sp = sg.attributes.position; const sc = [];
    for (let i = 0; i < sp.count; i++) { const k = clamp((sp.getY(i) + 10) / 70); const c = new THREE.Color(0xffffff).lerp(new THREE.Color(0x1a1446), Math.pow(k, .6)); sc.push(c.r, c.g, c.b); }
    sg.setAttribute('color', new THREE.Float32BufferAttribute(sc, 3));
    const skyM = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide, fog: false }); s.add(M(sg, skyM));
    s.add(new THREE.HemisphereLight(0xffb070, 0x100818, .6)); const key = new THREE.DirectionalLight(0xff9a50, 2); key.position.set(8, 3, -10); s.add(key);
    const gr = M(new THREE.CylinderGeometry(40, 40, 1, 64), std(0x120a14, { roughness: .95 })); gr.position.y = 1.2; s.add(gr);
    for (let i = 0; i < 7; i++) { const h = M(new THREE.SphereGeometry(3 + r1() * 3, 48, 32), std(0x1a0e1c, { roughness: .9 })); h.position.set(-16 + i * 5.5, 1.4, -14 - r1() * 5); h.scale.y = .5; s.add(h); }
    const sun = M(new THREE.SphereGeometry(1.4, 48, 32), new THREE.MeshBasicMaterial({ color: 0xffd090, fog: false })); s.add(sun);
    const halo = dust(260, [4.5, 4.5, 1], 0xffa050, 1.0, .5); s.add(halo);
    const B = beam(0xffffff, .09); s.add(B);
    const blues = Array.from({ length: 50 }, () => { const b = M(new THREE.SphereGeometry(.08, 12, 8), glow(0x4a9cff)); b.userData = { u: r1(), d: V(r1() - .5, r1() * .8, r1() - .5).normalize(), ph: r1() }; s.add(b); return b; });
    const d = dust(400, [26, 14, 14], 0xffc090, .12, .35); d.position.y = 6; s.add(d);
    const day = new THREE.Color(0x9cc8ff), dusk = new THREE.Color(0xffa060), wc = new THREE.Color(0xffffff), oc = new THREE.Color(0xff7a30);
    return t => {
      const a = t - S7; const k = ease(prog(a, .3, 4.5));
      skyM.color.copy(day).lerp(dusk, k); sun.position.set(2.4, lerp(6.4, 3.7, k), -10); halo.position.copy(sun.position); halo.rotation.z = t * .15;
      sun.material.color.setHSL(lerp(.13, .06, k), 1, lerp(.85, .62, k));
      const end = V(-4.5, 5.2, 3); B.userData.set(sun.position, sun.position.clone().lerp(end, ease(prog(a, 0, 1.2))));
      B.children[0].material.color.copy(wc).lerp(oc, prog(a, 2.3, 2.5)); B.children[1].material.color.copy(B.children[0].material.color);
      blues.forEach(b => { const U = b.userData; const c = ((t * .5 + U.ph) % 1); const st = sun.position.clone().lerp(end, U.u * .8);
        b.visible = a > 1.0 && a < 6.0; b.position.copy(st).addScaledVector(U.d, c * 3.5); b.scale.setScalar((1.2 - c) * (1 - prog(a, 4.2, 1.5))); });
      d.rotation.y = t * .02;
      cam.position.set(lerp(-1, 1, ease(prog(a, 0, 6))), 5.6, 15.5); cam.lookAt(0, 5.6, 0); };
  } });
  // 9) Sıradaki soru: okyanuslar neden tuzlu? — gece okyanusu, havada tuz kristalleri
  shots.push({ t0: S8, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#020a1e', '#0a2a4a'], fog: 0x041428, rim: 0x3fe0ff, key: 1.6 });
    const wg = new THREE.PlaneGeometry(40, 30, 80, 60); wg.rotateX(-Math.PI / 2); const WP = wg.attributes.position; const base = WP.array.slice();
    const water = M(wg, std(0x0b4a7a, { metalness: .55, roughness: .22 })); water.position.y = 3.0; s.add(water);
    const cry = Array.from({ length: 9 }, (_, i) => { const c = M(rb(.6, .6, .6, .06), std(0xf4f8ff, { roughness: .25, metalness: .1, transparent: true, opacity: .92, emissive: 0x334455 }));
      c.userData = { x: -2.6 + (i % 3) * 1.4 + (r1() - .5) * .6, y: 5.6 + Math.floor(i / 3) * .85 + r1() * .3, z: -1 - r1() * 2, ph: r1() * 6 }; s.add(c); return c; });
    const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); q.position.set(2.2, 7.6, .5); s.add(q);
    const qa = M(new THREE.TorusGeometry(.42, .1, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.12, 12, 8), qm); qd.position.set(-.08, -.72, 0); q.add(qd);
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02;
      for (let i = 0; i < WP.count; i++) { const x = base[i * 3], z = base[i * 3 + 2]; WP.setY(i, .28 * Math.sin(x * .55 + t * 1.6) + .18 * Math.sin(z * .8 + t * 1.1) + .08 * Math.sin((x + z) * 1.7 + t * 2.3)); }
      WP.needsUpdate = true; wg.computeVertexNormals();
      cry.forEach((c, i) => { const U = c.userData; const k = back(prog(a, .2 + i * .08, .5)); c.scale.setScalar(Math.max(.01, k)); c.position.set(U.x, U.y + Math.sin(t * 1.4 + U.ph) * .15, U.z); c.rotation.set(t * .5 + U.ph, t * .7, U.ph); });
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .4;
      cam.position.set(Math.sin(a * .2) * 1.2, 7.2, 15); cam.lookAt(0, 6.0, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'GÖKYÜZÜ NEDEN<br><span class="y">MAVİ?</span>', 108) },
    { t0: S1, t1: S2, html: T('BEYAZ IŞIK', 'BÜTÜN <span class="y">RENKLERİN</span><br>KARIŞIMI', 100) },
    { t0: S2, t1: S3, html: T('HAVAYA GİRİNCE', 'MİLYARLARCA<br><span class="y">MOLEKÜL</span>', 104) },
    { t0: S3, t1: S4, html: T('KISA DALGALI MAVİ', 'HER YÖNE<br><span class="y">SAÇILIR</span>', 108) },
    { t0: S4, t1: S5, html: BIG('MAVİ IŞIK, KIRMIZIDAN', 'k44', 'KAT DAHA FAZLA SAÇILIR', '0') },
    { t0: S5, t1: S6, html: T('BİLİM İNSANLARI BUNA', 'RAYLEIGH<br><span class="y">SAÇILMASI</span> DİYOR', 96) },
    { t0: S6, t1: S6b, html: T('PEKİ', 'MOR NEDEN<br><span class="y">YOK?</span>', 110) },
    { t0: S6b, t1: S7, html: T('GÜNEŞ IŞIĞINDA MOR AZ', 'GÖZÜMÜZ MORA<br><span class="y">AZ DUYARLI</span>', 96) },
    { t0: S7, t1: S7b, html: T('GÜN BATIMINDA', 'IŞIK <span class="y">DAHA UZUN</span><br>YOL ALIR', 100) },
    { t0: S7b, t1: S8, html: T('MAVİ SAÇILIP KAYBOLUR', 'GERİYE <span class="y">KIZIL</span><br>KALIR', 108) },
    { t0: S8, t1: 99, html: T('SIRADAKİ SORU', 'OKYANUSLAR NEDEN<br><span class="y">TUZLU?</span>', 96) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 37.88, shots, titles,
    update: t => { const e = document.getElementById('k44'); if (e) { e.style.transform = `scale(${lerp(.6, 1, back(prog(t, S4, .5)))})`;
      e.textContent = (4.4 * ease(prog(t, S4 + 1.3, 1.0))).toFixed(1).replace('.', ','); } },
    follow: { t: 36.08, click: 36.98 },
    sfx: [[.3, 'whoosh', .5], [.4, 'ding', .3], [S1 + .2, 'whoosh', .4], [S1 + 1.1, 'ding', .5], [S2 + .4, 'whoosh', .5], [S3 + .6, 'pop', .6], [S3 + .7, 'ding', .3],
      [S4 + 1.3, 'click', .4], [S4 + 2.3, 'ding', .5], [S5 + .3, 'boom', .4], [S6 + .5, 'pop', .5], [S6b + .3, 'pop', .5], [S6b + 1.0, 'whoosh', .3],
      [S7 + .3, 'whoosh', .5], [S7b + .2, 'ding', .3], [S8 + .3, 'pop', .4], [S8 + .6, 'pop', .4], [S8 + .9, 'pop', .4]],
  };
};
