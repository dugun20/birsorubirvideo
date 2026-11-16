// Bilgi #18: Mikrodalga fırın yemeği nasıl ısıtır? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: ABD FDA "Microwave Ovens" (mikrodalgalar magnetron denen elektron tüpünde üretilir; fırının metal iç yüzeyinden yansır ve yemek
// tarafından emilir; su moleküllerini titreştirip ısı üretir; kalın yiyeceklerde dış katmanlar mikrodalgayla, iç kısım dıştan iletilen ısıyla
// pişer). Univ. of Florida, "Microwave Ovens" (U. H. Kurzweg): magnetronlar çoğunlukla 2450 MHz (2,45 GHz) üretir, dalga boyu ~12,2 cm;
// suyun dipol momenti; mikrodalgalar yemeğe yaklaşık 2,5 cm (1 inç) girer; döner tabla ısınmayı eşitlemeye yardım eder.
// Explain That Stuff "Microwave ovens" (birkaç santimden derine giremez; döner tabla eşit pişirme için).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  let seed = 1818; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
  function label(txt, col = '#ffffff', sz = .6) { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    g.fillStyle = col; g.font = 'bold 110px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(txt, 64, 70);
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, depthTest: false })); sp.scale.setScalar(sz); return sp; }
  const metal = () => std(0x3a3f48, { metalness: .7, roughness: .3 });
  // Fırın: açık ön, metal kabuk, turuncu iç ışık, cam kapak deseni, döner tabla + kâse
  function oven(s) {
    const O = new THREE.Group(); s.add(O); const sh = metal();
    [[4.2, .3, 2.6, 0, 1.1, 0], [4.2, .3, 2.6, 0, -1.1, 0], [.3, 2.5, 2.6, -2.0, 0, 0], [1.0, 2.5, 2.6, 1.6, 0, 0], [4.2, 2.5, .2, 0, 0, -1.2]].forEach(([w, h, d, x, y, z]) => { const p = M(rb(w, h, d, .1), sh); p.position.set(x, y, z); O.add(p); });
    const cav = M(new THREE.PlaneGeometry(2.9, 1.9), new THREE.MeshStandardMaterial({ color: 0xffb060, emissive: 0xff8a30, emissiveIntensity: .55 })); cav.position.set(-.5, 0, -1.08); O.add(cav);
    const il = new THREE.PointLight(0xffa040, 40, 6); il.position.set(-.5, .6, .4); O.add(il);
    const dc = document.createElement('canvas'); dc.width = dc.height = 128; { const g = dc.getContext('2d'); g.fillStyle = 'rgba(10,10,14,.55)';
      for (let y = 0; y < 128; y += 8) for (let x = 0; x < 128; x += 8) { g.beginPath(); g.arc(x + 4, y + 4, 1.6, 0, 7); g.fill(); } }
    const dt = new THREE.CanvasTexture(dc); dt.wrapS = dt.wrapT = THREE.RepeatWrapping; dt.repeat.set(6, 4);
    const door = M(new THREE.PlaneGeometry(2.9, 1.9), new THREE.MeshBasicMaterial({ map: dt, transparent: true, color: 0xffd8a0, opacity: .5, depthWrite: false })); door.position.set(-.5, 0, 1.32); O.add(door);
    const panel = M(rb(.8, 1.9, .1, .05), std(0x1a1d22, { metalness: .5 })); panel.position.set(1.55, 0, 1.3); O.add(panel);
    const dig = M(new THREE.PlaneGeometry(.6, .22), new THREE.MeshBasicMaterial({ color: 0x4ade80 })); dig.position.set(1.55, .6, 1.36); O.add(dig);
    const plate = new THREE.Group(); plate.position.set(-.5, -.85, .15); O.add(plate);
    plate.add(M(new THREE.CylinderGeometry(1, 1, .06, 64), new THREE.MeshStandardMaterial({ color: 0xdfe8f0, transparent: true, opacity: .7, roughness: .05 })));
    const bowl = M(new THREE.SphereGeometry(.55, 40, 20, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), std(0xe8e0d0, { side: THREE.DoubleSide })); bowl.position.y = .55; plate.add(bowl);
    const soup = M(new THREE.CircleGeometry(.5, 40), std(0xd06030, { emissive: 0x401000 })); soup.rotation.x = -Math.PI / 2; soup.position.y = .48; plate.add(soup);
    const steam = Array.from({ length: 18 }, () => { const b = M(new THREE.SphereGeometry(.07, 10, 8), glow(0xffffff, .5)); b.userData = { x: (r1() - .5) * .6, ph: r1() }; plate.add(b); return b; });
    O.up = t => { plate.rotation.y = t * .8; cav.material.emissiveIntensity = .5 + .1 * Math.sin(t * 6);
      steam.forEach(b => { const c = (t * .5 + b.userData.ph) % 1; b.position.set(b.userData.x, .5 + c * .9, Math.sin(c * 6) * .1); b.material.opacity = .5 * (1 - c); }); };
    O.plate = plate; return O;
  }
  function waveTube(pts, r = .025, c = 0x7ee0ff) { const m = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 80, r, 6), glow(c, .85)); m.set = P => { m.geometry.dispose(); m.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(P), 80, r, 6); }; return m; }
  // Su molekülü: O (kırmızı, −), iki H (beyaz, +)
  function water(sc = 1, lab = false) { const g = new THREE.Group(); g.scale.setScalar(sc);
    const o = M(new THREE.SphereGeometry(.5, 40, 28), std(0xff4a4a, { roughness: .3, emissive: 0x400808 })); g.add(o);
    [-1, 1].forEach(k => { const h = M(new THREE.SphereGeometry(.32, 32, 24), std(0xf4f6ff, { roughness: .3 })); const a = k * 52.25 * Math.PI / 180; h.position.set(Math.sin(a) * .62, -Math.cos(a) * .62, 0); g.add(h);
      if (lab) { const p = label('+', '#ffcf2e', .55); p.position.set(Math.sin(a) * 1.15, -Math.cos(a) * 1.15, .3); g.add(p); } });
    if (lab) { const m = label('−', '#7ee0ff', .7); m.position.set(0, .9, .3); g.add(m); }
    g.o = o; return g; }
  const heatCol = (k) => new THREE.Color(0x3a7ad0).lerp(new THREE.Color(0xff5a1a), clamp(k));

  const S0b = 2.96, S1 = 4.48, S1b = 6.56, S2 = 10.72, S3 = 13.84, S4 = 17.76, S5 = 20.68, S6 = 23.17, S7 = 25.96, S8 = 28.27, S9 = 31.48;

  // 1) Mikrodalga fırın: içten dışa pişirmez, peki nasıl ısıtır?
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff8a3a });
    const O = oven(s); O.position.set(0, 5.1, 0);
    const q = qmark(s, 2.0, 7.25, .7);
    return t => {
      E.d.rotation.y = t * .02; O.up(t); O.rotation.y = -.3 + t * .06;
      q.visible = t > S0b; q.rotation.y = Math.sin(t * 2) * .4; q.scale.setScalar(.7 * back(prog(t, S0b, .4)));
      cam.position.set(Math.sin(t * .2) * 1, 6.0, lerp(15, 13.2, ease(prog(t, 0, S1)))); cam.lookAt(0, 5.3, 0); };
  } });
  // 2) Magnetron: bakır anot, kanatçıklar, parlayan katot, mıknatıslar, dönen elektron bulutu
  shots.push({ t0: S1, t1: S1b, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff8a3a });
    const G = new THREE.Group(); G.position.set(0, 5.2, 0); s.add(G);
    const cu = std(0xd08040, { metalness: .85, roughness: .25 });
    const ring = M(new THREE.CylinderGeometry(1.6, 1.6, .9, 64, 1, true), Object.assign(cu.clone(), { side: THREE.DoubleSide })); G.add(ring);
    for (let i = 0; i < 8; i++) { const v = M(rb(.75, .9, .14, .04), cu); const a = i / 8 * Math.PI * 2; v.position.set(Math.cos(a) * 1.15, 0, Math.sin(a) * 1.15); v.rotation.y = -a; G.add(v); }
    const cat = M(new THREE.CylinderGeometry(.18, .18, 1.2, 32), std(0xffe0a0, { emissive: 0xff9a40, emissiveIntensity: 1.2 })); G.add(cat);
    [-1, 1].forEach(k => { const m = M(new THREE.CylinderGeometry(1.75, 1.75, .2, 64), std(k > 0 ? 0xc0392b : 0x2a5ad0, { metalness: .4, roughness: .4, transparent: k > 0, opacity: k > 0 ? .3 : 1, depthWrite: k < 0 })); m.position.y = k * 1.0; G.add(m); });
    const sp = Array.from({ length: 4 }, (_, i) => { const m = M(new THREE.ConeGeometry(.22, .8, 16), glow(0x9fd8ff, .7)); m.rotation.z = Math.PI / 2; const h = new THREE.Group(); h.add(m); m.position.x = .6; h.rotation.y = i * Math.PI / 2; G.add(h); return h; });
    const out = M(new THREE.CylinderGeometry(.12, .12, 1.4, 24), metal()); out.position.set(0, 1.8, 0); G.add(out);
    const wv = waveTube(Array.from({ length: 30 }, (_, j) => V(0, 0, 0))); wv.position.set(0, 7.0 + .1, 0); s.add(wv);
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02; G.rotation.set(.85, a * .4, 0); G.scale.setScalar(lerp(.7, .88, easeOut(prog(a, 0, .7))));
      sp.forEach((h, i) => h.rotation.y = i * Math.PI / 2 + t * 4);
      wv.visible = false;
      cam.position.set(Math.sin(a * .3) * 1, 5.9, 13.2); cam.lookAt(0, 5.2, 0); };
  } });
  // 3) Saniyede 2,45 milyar kez titreşen dalga: elektrik alan okları yön değiştirir
  shots.push({ t0: S1b, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s);
    const wv = waveTube([V(0, 0, 0), V(1, 0, 0)], .05); s.add(wv);
    const arrows = Array.from({ length: 15 }, (_, i) => { const g = new THREE.Group(); const sh = M(new THREE.CylinderGeometry(.04, .04, 1, 10), glow(0xffcf2e, .9)); sh.position.y = .5; g.add(sh);
      const hd = M(new THREE.ConeGeometry(.12, .25, 16), glow(0xffcf2e, .95)); hd.position.y = 1.05; g.add(hd); g.position.set(-2.0 + i * .3, 4.9, 0); s.add(g); return g; });
    const mag = M(rb(.8, .8, .8, .15), std(0xd08040, { metalness: .8, roughness: .25 })); mag.visible = false;
    return t => {
      const a = t - S1b; E.d.rotation.y = t * .02; const w = 1.6 + a * 1.1, amp = 1.1 * ease(prog(a, 0, .6));
      const P = Array.from({ length: 60 }, (_, j) => { const x = -2.1 + j * 4.4 / 59; return V(x, 4.9 + amp * Math.sin(x * w - t * 7), 0); }); wv.set(P);
      arrows.forEach((g, i) => { const x = g.position.x; const v = amp * Math.sin(x * w - t * 7); g.scale.y = Math.abs(v) < .02 ? .02 : v; g.visible = a > .3; });
      mag.rotation.set(t * .5, t * .7, 0);
      cam.position.set(Math.sin(a * .25) * 1.5, 5.6, 13); cam.lookAt(0, 5.0, 0); };
  } });
  // 4) Dalgalar metal duvarlardan sekerek yemeğe ulaşır (kesit)
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff8a3a });
    const B = new THREE.Group(); B.position.set(0, 5.0, 0); s.add(B); const sh = metal();
    [[4.6, .2, 3, 0, 1.6, 0], [4.6, .2, 3, 0, -1.6, 0], [.2, 3.4, 3, -2.3, 0, 0], [.2, 3.4, 3, 2.3, 0, 0], [4.6, 3.4, .2, 0, 0, -1.5]].forEach(([w, h, d, x, y, z]) => { const p = M(rb(w, h, d, .06), sh); p.position.set(x, y, z); B.add(p); });
    const bowl = M(new THREE.SphereGeometry(.7, 40, 20, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), std(0xe8e0d0, { side: THREE.DoubleSide })); bowl.position.set(0, -.8, 0); B.add(bowl);
    const soup = M(new THREE.CircleGeometry(.64, 40), std(0xd06030, { emissive: 0x401000 })); soup.rotation.x = -Math.PI / 2; soup.position.set(0, -.9, 0); B.add(soup);
    const box = M(rb(.5, .4, .4, .06), std(0xd08040, { metalness: .8 })); box.position.set(1.9, 1.3, 0); B.add(box);
    const paths = [[V(1.7, 1.3, .2), V(-2.15, .2, .2), V(1.4, -.4, .2), V(.3, -.75, .2)], [V(1.7, 1.2, -.3), V(.4, 1.45, -.3), V(-2.15, -.3, -.3), V(-.4, -.8, -.3)],
      [V(1.7, 1.1, .6), V(2.15, -.2, .6), V(-1, 1.45, .6), V(-.1, -.7, .6)]];
    const pulses = paths.map(p => { const c = new THREE.CurvePath(); for (let i = 0; i < p.length - 1; i++) c.add(new THREE.LineCurve3(p[i], p[i + 1]));
      const tube = M(new THREE.TubeGeometry(c, 120, .02, 6), glow(0x7ee0ff, .35)); B.add(tube);
      const dots = Array.from({ length: 4 }, () => { const d = M(new THREE.SphereGeometry(.08, 12, 8), glow(0xbff0ff, 1)); B.add(d); return d; }); return { c, dots, tube }; });
    return t => {
      const a = t - S2; E.d.rotation.y = t * .02; B.rotation.y = Math.sin(t * .3) * .25;
      pulses.forEach((p, i) => { p.tube.material.opacity = .35 * prog(a, .2 + i * .3, .5); p.dots.forEach((d, j) => { const u = (a * .5 + j / 4 + i * .1) % 1; d.position.copy(p.c.getPointAt(u)); d.visible = a > .2 + i * .3; }); });
      soup.material.emissive.setHex(0x401000).lerp(new THREE.Color(0xa03000), prog(a, 1.5, 1.5));
      cam.position.set(Math.sin(a * .2) * 1, 5.8, 13.4); cam.lookAt(0, 5.0, 0); };
  } });
  // 5) Su molekülü: bir ucu artı, bir ucu eksi
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const W = water(1.6, true); W.position.set(0, 5.1, 0); s.add(W);
    const cl = dust(200, [5, 4, 3], 0x7ee0ff, .12, .5); cl.position.set(0, 5.1, 0); s.add(cl);
    return t => {
      const a = t - S3; E.d.rotation.y = t * .02; cl.rotation.y = t * .1;
      W.scale.setScalar(1.6 * back(prog(a, 0, .6))); W.rotation.set(0, Math.sin(t * .8) * .5, Math.sin(t * .6) * .15);
      W.children.forEach(c => { if (c.isSprite) c.visible = a > 1.2; });
      cam.position.set(Math.sin(a * .2) * 1, 5.6, 13); cam.lookAt(0, 5.0, 0); };
  } });
  // 6) Alanın yönü değiştikçe moleküller dönüp titreşir
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const mols = []; for (let i = 0; i < 4; i++) for (let j = 0; j < 3; j++) { const w = water(.55); w.position.set(-1.8 + i * 1.2, 4.0 + j * 1.15, (r1() - .5) * .8); w.userData.ph = r1() * .4; s.add(w); mols.push(w); }
    const ar = new THREE.Group(); ar.position.set(2.55, 5.15, 0); s.add(ar);
    const sh = M(new THREE.CylinderGeometry(.08, .08, 2, 16), glow(0xffcf2e, .95)); ar.add(sh); const hd = M(new THREE.ConeGeometry(.25, .45, 24), glow(0xffcf2e, 1)); hd.position.y = 1.15; ar.add(hd);
    return t => {
      const a = t - S4; E.d.rotation.y = t * .02; const f = Math.sin(a * 4.5); const dir = Math.tanh(f * 4);
      ar.scale.y = dir; mols.forEach(w => { const tg = dir > 0 ? Math.PI : 0; w.rotation.z = lerp(w.rotation.z, tg + w.userData.ph - .2, .25) + Math.sin(t * 25 + w.userData.ph * 20) * .05; w.rotation.y = Math.sin(t + w.userData.ph * 9) * .3; });
      cam.position.set(Math.sin(a * .2) * .8, 5.7, 13.4); cam.lookAt(0, 5.1, 0); };
  } });
  // 7) Titreşim çarpışmalarla ısıya dönüşür: moleküller hızlanır, maviden kırmızıya
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff6a2a });
    const box = M(rb(4.6, 3.2, 2.2, .12), new THREE.MeshStandardMaterial({ color: 0xcfe8ff, transparent: true, opacity: .1, depthWrite: false })); box.position.set(0, 5.1, 0); s.add(box);
    const ms = Array.from({ length: 26 }, () => { const w = water(.3); w.userData = { p: V((r1() - .5) * 4, (r1() - .5) * 2.6, (r1() - .5) * 1.6), v: V(r1() - .5, r1() - .5, r1() - .5).normalize(), ph: r1() * 6 }; s.add(w); return w; });
    const sparks = dust(120, [4.2, 2.8, 1.8], 0xffa040, .14, 0, true); sparks.position.set(0, 5.1, 0); s.add(sparks);
    return t => {
      const a = t - S5; E.d.rotation.y = t * .02; const heat = ease(prog(a, .2, 2.2)); const sp = lerp(.4, 2.2, heat);
      ms.forEach(w => { const U = w.userData; const p = U.p.clone().addScaledVector(U.v, a * sp);
        ['x', 'y', 'z'].forEach((k, i) => { const h = [2.1, 1.4, .9][i]; let x = ((p[k] + h) % (4 * h) + 4 * h) % (4 * h); p[k] = x > 2 * h ? 4 * h - x - h : x - h; });
        w.position.set(p.x, 5.1 + p.y, p.z); w.rotation.set(t * sp * 2 + U.ph, t * sp + U.ph, 0); w.o.material.color.copy(heatCol(heat)); });
      sparks.material.opacity = .6 * heat; sparks.rotation.y = t * .3;
      cam.position.set(Math.sin(a * .2) * 1, 5.7, 13.6); cam.lookAt(0, 5.1, 0); };
  } });
  // 8–9) Kesit: dalgalar birkaç santim girer, iç kısım dıştan yayılan ısıyla pişer
  shots.push({ t0: S6, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff8a3a });
    const F = new THREE.Group(); F.position.set(0, 4.9, 0); s.add(F);
    const R = 1.7, H = 1.6, N = 8;
    const side = M(new THREE.CylinderGeometry(R, R, H, 64), std(0x9a5a2a, { roughness: .7 })); F.add(side);
    const rings = Array.from({ length: N }, (_, i) => { const r0 = R * i / N, r1_ = R * (i + 1) / N;
      const m = M(new THREE.RingGeometry(r0 + .001, r1_, 64), new THREE.MeshStandardMaterial({ side: THREE.DoubleSide, roughness: .6 }));
      m.rotation.x = -Math.PI / 2; m.position.y = H / 2 + .005; m.userData.d = (R - (r0 + r1_) / 2) / R; F.add(m); return m; });
    const waves = Array.from({ length: 10 }, (_, i) => { const an = i / 10 * Math.PI * 2; const g = new THREE.Group(); g.rotation.y = an;
      const w = M(new THREE.ConeGeometry(.14, .45, 16), glow(0x7ee0ff, .95)); w.rotation.z = Math.PI / 2; g.add(w); g.userData.an = i / 10; F.add(g); return g; });
    const depth = M(new THREE.TorusGeometry(R * .76, .02, 6, 96), glow(0xffcf2e, .9)); depth.rotation.x = -Math.PI / 2; depth.position.y = H / 2 + .02; F.add(depth);
    return t => {
      const a = t - S6; E.d.rotation.y = t * .02; F.rotation.set(.95, Math.sin(t * .3) * .2, 0);
      const k1 = ease(prog(a, .3, 1.6)), k2 = ease(prog(t, S7 + .2, 2.0));
      rings.forEach(m => { const d = m.userData.d; const h = d < .25 ? k1 : clamp(k2 * 1.5 - (d - .25) / .75); m.material.color.copy(heatCol(h)); });
      waves.forEach(g => { const c = (a * .9 + g.userData.an) % 1; const r = lerp(R + 1.2, R * .78, c); g.children[0].position.set(r, H / 2 + .05, 0); g.visible = t < S7 + .3; g.children[0].material.opacity = .95 * (1 - c * .6); });
      depth.visible = a > 1.2 && t < S7 + .3;
      cam.position.set(Math.sin(a * .2) * .8, 5.9, 13.2); cam.lookAt(0, 5.0, 0); };
  } });
  // 10) Döner tabla: sabit sıcak/soğuk noktalar arasından geçen yemek eşit ısınır
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0xff8a3a });
    const P = new THREE.Group(); P.position.set(0, 4.3, 0); s.add(P);
    const plate = M(new THREE.CylinderGeometry(2.2, 2.2, .1, 96), new THREE.MeshStandardMaterial({ color: 0xdfe8f0, transparent: true, opacity: .75, roughness: .05 })); P.add(plate);
    const rot = new THREE.Group(); P.add(rot);
    const bowls = [0, 1, 2].map(i => { const b = M(new THREE.SphereGeometry(.5, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), std(0xe8e0d0, { side: THREE.DoubleSide })); const an = i * Math.PI * 2 / 3;
      b.position.set(Math.cos(an) * 1.35, .55, Math.sin(an) * 1.35); rot.add(b); const sp = M(new THREE.CircleGeometry(.45, 32), std(0xd06030, { emissive: 0x401000 })); sp.rotation.x = -Math.PI / 2; sp.position.set(b.position.x, .48, b.position.z); rot.add(sp); return sp; });
    const hot = [[1.2, .6], [-1.1, 1.0], [.2, -1.4], [-1.5, -.6]].map(([x, z]) => { const h = M(new THREE.SphereGeometry(.5, 24, 16), glow(0xff6a2a, .35)); h.position.set(x, 5.0, z); s.add(h); return h; });
    const axis = M(new THREE.TorusGeometry(2.45, .03, 8, 96, Math.PI * 1.5), glow(0xffcf2e, .9)); axis.rotation.x = Math.PI / 2; axis.position.set(0, 4.3, 0); s.add(axis);
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02; rot.rotation.y = -a * 1.2; axis.rotation.z = -a * 1.2;
      hot.forEach((h, i) => h.scale.setScalar(1 + .15 * Math.sin(t * 5 + i)));
      bowls.forEach(b => b.material.emissive.copy(new THREE.Color(0x401000).lerp(new THREE.Color(0xc04000), prog(a, .3, 2.5))));
      cam.position.set(Math.sin(a * .2) * 1, 8.6, 11.8); cam.lookAt(0, 4.9, 0); };
  } });
  // 11) Sıradaki soru: Gökkuşağı nasıl oluşur? — yağmur damlası ışığı renklere ayırır, arkada gökkuşağı
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#101a3a', '#020308'], rim: 0x7ee0ff });
    const cols = [0xff3b30, 0xff9500, 0xffcc00, 0x34c759, 0x32ade6, 0x3a5aff, 0xaf52de];
    const arc = cols.map((c, i) => { const m = M(new THREE.TorusGeometry(3.0 - i * .13, .065, 12, 128, Math.PI), glow(c, .75)); m.position.set(0, 3.7, -2.5); s.add(m); return m; });
    const hill = M(new THREE.SphereGeometry(8, 64, 32), std(0x18241e, { roughness: .95 })); hill.position.set(0, -4.6, -3); s.add(hill);
    const drop = M(new THREE.SphereGeometry(.65, 48, 32), new THREE.MeshStandardMaterial({ color: 0x9fd0ff, emissive: 0x2a5a8a, transparent: true, opacity: .7, roughness: .05, metalness: .2 })); drop.position.set(0, 5.0, 1); s.add(drop);
    const beam = M(new THREE.CylinderGeometry(.06, .06, 2.4, 12), glow(0xffffff, .9)); beam.rotation.z = Math.PI / 2 - .25; beam.position.set(-1.7, 5.3, 1); s.add(beam);
    const fan = cols.map((c, i) => { const m = M(new THREE.CylinderGeometry(.03, .03, 2.0, 8), glow(c, .9)); s.add(m); return m; });
    const rain = Array.from({ length: 50 }, () => { const d = M(new THREE.CylinderGeometry(.01, .01, .35, 4), glow(0x9fd0ff, .4)); d.userData = { x: (r1() - .5) * 6, z: (r1() - .5) * 3, ph: r1() }; s.add(d); return d; });
    const q = qmark(s, 2.0, 7.25, .7);
    return t => {
      const a = t - S9; E.d.rotation.y = t * .02;
      arc.forEach((m, i) => { const k = ease(prog(a, .2 + i * .08, 1.0)); m.geometry.dispose(); m.geometry = new THREE.TorusGeometry(3.0 - i * .13, .065, 12, 128, Math.max(.01, Math.PI * k)); m.rotation.z = 0; });
      fan.forEach((m, i) => { const an = -.35 - i * .05; const L2 = 2.0 * ease(prog(a, .6, .6)); m.scale.y = Math.max(.01, L2 / 2); m.rotation.z = Math.PI / 2 + an; m.position.set(Math.cos(an) * (.6 + L2 / 2), 5.0 + Math.sin(an) * (.6 + L2 / 2), 1); });
      rain.forEach(d => { const c = (t * 1.3 + d.userData.ph) % 1; d.position.set(d.userData.x, lerp(7.5, 3.0, c), d.userData.z); });
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * 1, 6.0, 13.5); cam.lookAt(0, 5.2, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S0b, html: T('YANLIŞ BİLİNEN', 'İÇTEN DIŞA<br><span class="y">PİŞİRMEZ!</span>', 108) },
    { t0: S0b, t1: S1, html: T('BİR SORU', 'MİKRODALGA FIRIN<br>YEMEĞİ NASIL<br><span class="y">ISITIR?</span>', 88) },
    { t0: S1, t1: S1b, html: T('FIRININ KALBİ', '<span class="y">MAGNETRON</span>', 120) },
    { t0: S1b, t1: S2, html: BIG('SANİYEDE', 'k245', 'KEZ TİTREŞEN DALGA', '2,45<small>MİLYAR</small>') },
    { t0: S2, t1: S3, html: T('DALGALAR', 'METAL DUVARLARDAN<br><span class="y">SEKER</span>', 92) },
    { t0: S3, t1: S4, html: T('SU MOLEKÜLÜ', 'BİR UCU <span class="y">+</span><br>BİR UCU <span class="y">−</span>', 108) },
    { t0: S4, t1: S5, html: T('YÖN DEĞİŞTİKÇE', 'DÖNÜP<br><span class="y">TİTREŞİR</span>', 108) },
    { t0: S5, t1: S6, html: T('ÇARPIŞMALAR', 'TİTREŞİM<br><span class="y">ISIYA</span> DÖNÜŞÜR', 104) },
    { t0: S6, t1: S7, html: T('DALGALAR SADECE', 'BİRKAÇ <span class="y">SANTİM</span><br>GİRER', 104) },
    { t0: S7, t1: S8, html: T('İÇ KISIM', 'DIŞTAN YAYILAN<br><span class="y">ISIYLA</span> PİŞER', 96) },
    { t0: S8, t1: S9, html: T('DÖNER TABLA', 'ISIYI <span class="y">EŞİT</span><br>DAĞITIR', 108) },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'GÖKKUŞAĞI<br>NASIL <span class="y">OLUŞUR?</span>', 104) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k245', S1b]];
  return {
    END: 36.12, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; }); },
    follow: { t: 34.32, click: 35.22 },
    sfx: [[.3, 'whoosh', .5], [1.9, 'snap', .4], [S0b + .2, 'pop', .4], [S1 + .3, 'boom', .4], [S1b + .2, 'ding', .5], [S1b + 1.2, 'pop', .3],
      [S2 + .4, 'click', .3], [S2 + .9, 'click', .3], [S2 + 1.4, 'click', .3], [S3 + .2, 'pop', .5], [S3 + 1.3, 'ding', .4], [S4 + .4, 'snap', .3], [S4 + 1.1, 'snap', .3],
      [S5 + .5, 'crunch', .4], [S5 + 1.5, 'crunch', .4], [S6 + .4, 'whoosh', .4], [S7 + .3, 'pop_low', .5], [S8 + .3, 'whoosh', .4], [S8 + 2.0, 'ding', .4],
      [S9 + .4, 'whoosh', .5], [S9 + 1.0, 'ding', .4]],
  };
};
