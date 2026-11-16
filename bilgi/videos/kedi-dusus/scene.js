// Bilgi #17: Kediler neden hep ayaklarının üstüne düşer? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Wikipedia "Cat righting reflex" (refleks 3–4 haftalıkken başlar, 6–7 haftada tamamlanır; yön tayini görme ya da iç kulaktaki
// vestibüler sistemle; kedi ortadan bükülür, ön ayakları toplayıp ön yarıyı 90°'ye kadar çevirirken arka yarı ters yönde 10° kadar döner,
// sonra arka ayakları toplayıp arkayı çevirir; alışılmadık esnek omurga ve işlevsel köprücük kemiği yok; ortalama kedinin limit hızı
// ~97 km/sa (60 mph), ortalama insanınki ~190 km/sa (120 mph)). Live Science "How do cats land on their feet?" (vestibüler sistem,
// açısal momentumun korunumu, bel bükülmesi, ön/arka bacak toplama sırası).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  let seed = 1717; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
    s.background = gradTex(...(o.bg || ['#141032', '#020308'])); s.fog = new THREE.Fog(o.fog || 0x02050e, o.near || 30, o.far || 110);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi || .8));
    const key = new THREE.DirectionalLight(0xfff4e0, o.key || 2.2); key.position.set(-10, 12, 10); s.add(key);
    const rim = new THREE.PointLight(o.rim || 0xffb04a, 600, 60); rim.position.set(6, 9, -5); s.add(rim);
    const d = dust(500, [26, 18, 16], o.dust || 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return { d, rim };
  }
  const glow = (c, op = .9) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false });
  function qmark(s, x, y, sc = 1) { const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e }); const q = new THREE.Group(); q.position.set(x, y, .5); q.scale.setScalar(sc); s.add(q);
    const qa = M(new THREE.TorusGeometry(.42, .1, 12, 32, Math.PI * 1.4), qm); qa.rotation.z = -Math.PI * .3; q.add(qa); const qd = M(new THREE.SphereGeometry(.12, 12, 8), qm); qd.position.set(-.08, -.72, 0); q.add(qd); return q; }
  function streaks(s, n, w, y0, y1, op = .35) {
    const a = Array.from({ length: n }, () => { const m = M(new THREE.CylinderGeometry(.015, .015, 1.2, 6), glow(0xffffff, op)); m.userData = { x: (r1() - .5) * w, z: (r1() - .5) * 2, ph: r1() }; s.add(m); return m; });
    a.up = (t, sp = 1.2, dx = 0) => a.forEach(m => { const c = (t * sp + m.userData.ph) % 1; m.position.set(dx + m.userData.x, lerp(y0, y1, c), m.userData.z); m.material.opacity = op * Math.sin(c * Math.PI); });
    return a;
  }

  // İki yarılı kedi: F (ön yarı: göğüs, kafa, ön ayaklar), R (arka yarı: kalça, arka ayaklar, kuyruk). Gövde x ekseni boyunca, baş +x.
  function makeCat(col = 0xf0a040) {
    const fur = std(col, { roughness: .6 }), wh = std(0xfff4e6, { roughness: .6 });
    const root = new THREE.Group(); const F = new THREE.Group(), R = new THREE.Group(); root.add(F, R);
    const half = (G, sx) => { const b = M(new THREE.CapsuleGeometry(.42, .45, 12, 24), fur); b.rotation.z = Math.PI / 2; b.position.x = sx * .36; G.add(b);
      const be = M(new THREE.CapsuleGeometry(.3, .35, 10, 20), wh); be.rotation.z = Math.PI / 2; be.position.set(sx * .36, -.17, 0); be.scale.z = .9; G.add(be); };
    half(F, 1); half(R, -1);
    const head = new THREE.Group(); head.position.set(1.08, .22, 0); F.add(head); head.add(M(new THREE.SphereGeometry(.42, 40, 28), fur));
    const muz = M(new THREE.SphereGeometry(.2, 24, 16), wh); muz.position.set(.3, -.1, 0); muz.scale.set(.8, .7, 1.2); head.add(muz);
    [-1, 1].forEach(k => { const e = M(new THREE.ConeGeometry(.15, .32, 24), fur); e.position.set(.02, .4, k * .22); e.rotation.x = k * -.25; head.add(e);
      const ey = M(new THREE.SphereGeometry(.08, 16, 12), new THREE.MeshBasicMaterial({ color: 0x9cff5a })); ey.position.set(.34, .1, k * .16); head.add(ey);
      const pu = M(new THREE.SphereGeometry(.04, 12, 8), new THREE.MeshBasicMaterial({ color: 0x050505 })); pu.position.set(.41, .1, k * .16); head.add(pu); });
    const nose = M(new THREE.SphereGeometry(.05, 12, 8), std(0xff7a9a)); nose.position.set(.44, -.02, 0); head.add(nose);
    const leg = (G, x, z) => { const l = new THREE.Group(); l.position.set(x, -.22, z); G.add(l);
      const m = M(new THREE.CapsuleGeometry(.11, .42, 8, 16), fur); m.position.y = -.28; l.add(m); const p = M(new THREE.SphereGeometry(.13, 16, 12), wh); p.position.y = -.55; l.add(p); return l; };
    const fl = [leg(F, .6, .2), leg(F, .6, -.2)], rl = [leg(R, -.6, .2), leg(R, -.6, -.2)];
    const tc = new THREE.CatmullRomCurve3([V(-.85, 0, 0), V(-1.35, .25, 0), V(-1.6, .8, .1), V(-1.45, 1.25, .2)]);
    const tail = M(new THREE.TubeGeometry(tc, 40, .08, 12), fur); R.add(tail);
    // poz: rf/rr yuvarlanma (π = sırtüstü), bend = bel bükülmesi, tf/tr = ayak toplama (0 açık, 1 toplu)
    root.pose = (rf, rr, bend = 0, tf = 0, tr = 0) => {
      F.rotation.set(rf, 0, bend); R.rotation.set(rr, 0, -bend);
      fl.forEach(l => { l.rotation.z = lerp(-.15, 1.9, tf); l.scale.y = lerp(1, .8, tf); });
      rl.forEach(l => { l.rotation.z = lerp(.15, -1.9, tr); l.scale.y = lerp(1, .8, tr); });
      tail.rotation.x = (rr - rf) * .5; };
    // tam doğrulma dizisi k: 0..1
    root.seq = k => { const P = Math.PI; const bend = .45 * ease(prog(k, 0, .15)) * (1 - ease(prog(k, .85, .15)));
      const a = ease(prog(k, .15, .35)), b = ease(prog(k, .5, .35));
      const rf = lerp(lerp(P, P / 2, a), 0, b), rr = lerp(lerp(P, P + .17, a), 0, b);
      const tf = k < .5 ? ease(prog(k, .08, .1)) : 1 - ease(prog(k, .5, .1)), tr = k < .5 ? 0 : ease(prog(k, .5, .1)) * (1 - ease(prog(k, .85, .1)));
      root.pose(rf, rr, bend, tf, tr); };
    root.head = head; root.pose(0, 0); return root;
  }
  const S1 = 4.0, S2 = 6.0, S3 = 9.68, S4 = 12.8, S5 = 15.6, S6 = 18.96, S6b = 21.2, S7 = 23.6, S8 = 28.72, S9 = 34.72;

  // 1) Sırtüstü bırakılan kedi düşerken dönüp dört ayağı üstüne iner (döngü)
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const E = lights(s);
    const fl = M(rb(9, .5, 5, .1), std(0x2a2630, { roughness: .8 })); fl.position.set(0, 2.95, 0); s.add(fl);
    const wall = M(rb(9, 9, .4, .1), std(0x1a1828, { roughness: .9 })); wall.position.set(0, 7, -3); s.add(wall);
    const win = M(new THREE.PlaneGeometry(1.4, 1.8), new THREE.MeshBasicMaterial({ color: 0x18243e })); win.position.set(-2.6, 5.4, -2.78); s.add(win);
    const cat = makeCat(); s.add(cat);
    const st = streaks(s, 14, 3, 3.6, 8.5);
    return t => {
      E.d.rotation.y = t * .02; const P = 2.0, c = (t % P) / P; const fall = clamp(c / .7);
      cat.position.set(0, lerp(6.5, 3.95, fall * fall), 0); cat.seq(clamp(fall * 1.05)); cat.rotation.y = -.35;
      if (c > .7) { const sq = Math.sin(prog(c, .7, .12) * Math.PI) * .12; cat.scale.set(1 + sq * .5, 1 - sq, 1 + sq * .5); } else cat.scale.setScalar(1);
      st.up(t, 1.4); st.forEach(m => m.visible = c < .7);
      cam.position.set(Math.sin(t * .3) * 1, 6.0, 14); cam.lookAt(0, 5.3, 0); };
  } });
  // 2) Doğrulma refleksi: ağır çekimde dönen kedi ve parlayan dönüş halkası
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const cat = makeCat(); cat.position.set(0, 5.2, 0); cat.scale.setScalar(1.3); s.add(cat);
    const ring = M(new THREE.TorusGeometry(1.9, .04, 12, 120, Math.PI * 1.6), glow(0xffcf2e, .9)); ring.rotation.y = Math.PI / 2; ring.position.set(0, 5.2, 0); s.add(ring);
    const tip = M(new THREE.ConeGeometry(.16, .4, 24), glow(0xffcf2e, .95)); s.add(tip);
    return t => {
      const a = t - S1; E.d.rotation.y = t * .02; const k = ease(prog(a, .1, 1.8)); cat.seq(k); cat.rotation.y = -.5 + Math.sin(t * .4) * .15;
      ring.rotation.x = -k * Math.PI * 1.2; const ang = -k * Math.PI * 1.2 + Math.PI * 1.6; tip.position.set(0, 5.2 + Math.sin(ang) * 1.9, Math.cos(ang) * 1.9); tip.rotation.x = ang;
      cam.position.set(Math.sin(a * .3) * 2.5, 6.0, 13.5); cam.lookAt(0, 5.3, 0); };
  } });
  // 3) İç kulak: yarım daire kanalları ve "aşağı" oku
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const H = new THREE.Group(); H.position.set(-.5, 5.4, 0); s.add(H);
    const sk = M(new THREE.SphereGeometry(1.7, 48, 32), new THREE.MeshStandardMaterial({ color: 0xf0a040, transparent: true, opacity: .22, roughness: .4, depthWrite: false })); H.add(sk);
    [-1, 1].forEach(k => { const e = M(new THREE.ConeGeometry(.6, 1.2, 32), new THREE.MeshStandardMaterial({ color: 0xf0a040, transparent: true, opacity: .25, depthWrite: false })); e.position.set(k * 1, 1.55, 0); e.rotation.z = -k * .35; H.add(e); });
    const ear = new THREE.Group(); ear.position.set(.75, .1, .3); H.add(ear);
    const cols = [0x7ee0ff, 0xffcf2e, 0xff6a8a]; const fluid = [];
    cols.forEach((c, i) => { const r = M(new THREE.TorusGeometry(.42, .06, 16, 64), std(c, { emissive: c, emissiveIntensity: .7, roughness: .3 }));
      if (i === 1) r.rotation.y = Math.PI / 2; if (i === 2) r.rotation.x = Math.PI / 2; ear.add(r);
      const d = M(new THREE.SphereGeometry(.09, 16, 12), glow(0xffffff, 1)); r.add(d); fluid.push(d); });
    const ves = M(new THREE.SphereGeometry(.22, 24, 16), std(0xe0e8ff, { emissive: 0x4a6aa0, roughness: .3 })); ves.position.set(-.3, -.35, 0); ear.add(ves);
    const ar = new THREE.Group(); ar.position.set(2.1, 5.4, .5); s.add(ar);
    const sh = M(new THREE.CylinderGeometry(.12, .12, 2.2, 24), glow(0x4ade80, .95)); ar.add(sh); const hd = M(new THREE.ConeGeometry(.35, .6, 32), glow(0x4ade80, 1)); hd.position.y = -1.4; hd.rotation.x = Math.PI; ar.add(hd);
    const ground = M(rb(6, .2, 3, .08), std(0x2a2630)); ground.position.set(0, 3.1, 0); s.add(ground);
    return t => {
      const a = t - S2; E.d.rotation.y = t * .02; H.rotation.z = Math.sin(t * 1.2) * .5; H.rotation.y = Math.sin(t * .5) * .3;
      fluid.forEach((d, i) => { const an = t * 2.5 + i * 2; d.position.set(Math.cos(an) * .42, Math.sin(an) * .42, 0); });
      ar.scale.setScalar(Math.max(.01, back(prog(a, 1.6, .5)))); ar.position.y = 5.4 + Math.sin(t * 3) * .12;
      cam.position.set(Math.sin(a * .25) * 1.2, 5.9, 13); cam.lookAt(0, 5.3, 0); };
  } });
  // 4) Belinden bükülür, ön ayaklarını toplar
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const E = lights(s);
    const cat = makeCat(); cat.position.set(0, 4.75, 0); cat.scale.setScalar(1.35); s.add(cat);
    const hinge = M(new THREE.TorusGeometry(.75, .04, 12, 64), glow(0xffcf2e, .9)); hinge.rotation.y = Math.PI / 2; hinge.position.set(0, 4.75, 0); s.add(hinge);
    const st = streaks(s, 12, 4, 3.4, 8.2);
    return t => {
      const a = t - S3; E.d.rotation.y = t * .02; const bend = .5 * ease(prog(a, .2, .9)), tf = ease(prog(a, 1.75, .6));
      cat.pose(Math.PI, Math.PI, bend, tf, 0); cat.rotation.y = -.45 + Math.sin(t * .4) * .1;
      hinge.scale.setScalar(1 + .1 * Math.sin(t * 5)); hinge.material.opacity = .9 * prog(a, .2, .4) * (1 - prog(a, 2.6, .4));
      st.up(t, .6);
      cam.position.set(Math.sin(a * .25) * 1.2 + .5, 6.0, 13.5); cam.lookAt(0, 5.3, 0); };
  } });
  // 5) Ön yarı 90°'ye kadar döner, arka yarı ters yöne ~10°
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const cat = makeCat(); cat.position.set(0, 5.0, 0); cat.scale.setScalar(1.45); s.add(cat);
    const arc = new THREE.Group(); arc.position.set(.9, 5.0, 0); s.add(arc);
    const am = glow(0xffcf2e, .95); let tor = null;
    return t => {
      const a = t - S4; E.d.rotation.y = t * .02; const k = ease(prog(a, .2, 1.6));
      cat.pose(lerp(Math.PI, Math.PI / 2, k), lerp(Math.PI, Math.PI + .17, k), .5, 1, 0); cat.rotation.y = -.7 + Math.sin(t * .4) * .1;
      if (tor) arc.remove(tor); tor = M(new THREE.TorusGeometry(1.25, .05, 10, 64, Math.max(.01, k * Math.PI / 2)), am); tor.rotation.set(0, Math.PI / 2, Math.PI / 2); arc.add(tor);
      arc.rotation.y = cat.rotation.y; arc.position.set(Math.cos(cat.rotation.y) * .9, 5.0, -Math.sin(cat.rotation.y) * .9);
      cam.position.set(Math.sin(a * .2) * 1, 5.6, 13.5); cam.lookAt(0, 5.2, 0); };
  } });
  // 6) Arka ayaklar toplanır, arka yarı da döner, kedi dik iner
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const E = lights(s);
    const fl = M(rb(9, .4, 5, .1), std(0x2a2630, { roughness: .8 })); fl.position.set(0, 3.0, 0); s.add(fl);
    const cat = makeCat(); cat.scale.setScalar(1.3); s.add(cat);
    return t => {
      const a = t - S5; E.d.rotation.y = t * .02; const k = ease(prog(a, .4, 1.8)); const P = Math.PI;
      const tr = ease(prog(a, .4, .4)) * (1 - ease(prog(a, 2.3, .4))), tf = 1 - ease(prog(a, .4, .4));
      cat.pose(lerp(P / 2, 0, k), lerp(P + .17, 0, k), .5 * (1 - ease(prog(a, 2.0, .6))), tf, tr); cat.rotation.y = -.6 + Math.sin(t * .4) * .1;
      const land = ease(prog(a, 1.6, 1.1)); cat.position.set(0, lerp(5.15, 4.18, land), 0);
      cam.position.set(Math.sin(a * .25) * 1.2, 5.8, 13.5); cam.lookAt(0, 5.0, 0); };
  } });
  // 7) Çok esnek omurga (+ işlevsel köprücük kemiği yok)
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const E = lights(s, { rim: 0x7ee0ff });
    const bone = std(0xf2ead8, { roughness: .45, emissive: 0x2a2418 }); const disc = std(0x7ee0ff, { emissive: 0x2a8ab0, emissiveIntensity: .8, roughness: .3 });
    const vs = Array.from({ length: 26 }, (_, i) => { const g = new THREE.Group(); const v = M(rb(.2, .3, .3, .06), bone); g.add(v);
      const sp = M(new THREE.ConeGeometry(.06, .3, 12), bone); sp.position.y = .28; g.add(sp); const d = M(new THREE.CylinderGeometry(.11, .11, .05, 20), disc); d.rotation.z = Math.PI / 2; d.position.x = .13; g.add(d); s.add(g); return g; });
    const skull = M(new THREE.SphereGeometry(.42, 32, 24), bone); s.add(skull);
    const clav = new THREE.Group(); s.add(clav); const cb = M(new THREE.CapsuleGeometry(.04, .5, 8, 16), std(0xf2ead8, { transparent: true, opacity: .9 })); cb.rotation.z = Math.PI / 2 - .3; clav.add(cb);
    const x1 = M(new THREE.BoxGeometry(.9, .07, .07), glow(0xff4a4a, .95)), x2 = x1.clone(); x1.rotation.z = .8; x2.rotation.z = -.8; clav.add(x1, x2);
    return t => {
      const a = t - S6; E.d.rotation.y = t * .02; const amp = .9 * ease(prog(a, .2, .8));
      const P = i => { const u = i / 25; return V(lerp(-2.3, 1.6, u), 5.4 + amp * Math.sin(u * 5.5 - t * 3) * (.4 + u * .6), 0); };
      vs.forEach((g, i) => { const p = P(i), q = P(i + .5); g.position.copy(p); g.rotation.z = Math.atan2(q.y - p.y, q.x - p.x); g.scale.setScalar(Math.max(.01, back(prog(a, i * .03, .4)))); });
      const h = P(26.5); skull.position.copy(h); skull.scale.setScalar(Math.max(.01, back(prog(a, .8, .4))));
      const cv = prog(t, S6b - .1, .5); clav.position.set(1.4, 4.0, .5); clav.scale.setScalar(Math.max(.01, back(cv))); clav.visible = cv > 0;
      x1.scale.x = x2.scale.x = Math.max(.01, prog(t, S6b + .6, .3)); clav.rotation.y = Math.sin(t) * .4;
      cam.position.set(Math.sin(a * .2) * 1, 5.6, 13.2); cam.lookAt(0, 5.0, 0); };
  } });
  // 8) Yavrularda refleks: 3–4 haftada başlar, 6–7 haftada tamamlanır (yavru büyür, döner)
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const E = lights(s);
    const kit = makeCat(0xb0b4c0); s.add(kit); kit.head.scale.setScalar(1.25);
    const pl = M(new THREE.CylinderGeometry(1.8, 1.9, .3, 64), std(0x2a2630, { roughness: .7 })); pl.position.set(0, 3.5, 0); s.add(pl);
    const rg = M(new THREE.TorusGeometry(1.85, .03, 8, 96), glow(0x7ee0ff, .8)); rg.rotation.x = Math.PI / 2; rg.position.set(0, 3.68, 0); s.add(rg);
    return t => {
      const a = t - S7; E.d.rotation.y = t * .02; const g = lerp(.6, 1.05, ease(prog(a, .5, 4)));
      kit.scale.setScalar(g); const P = 1.7, c = (a % P) / P; const fall = clamp(c / .75);
      kit.seq(clamp(fall * (a < 2.6 ? .55 : 1.05))); // önce yarım dönüş, sonra tam
      kit.position.set(0, lerp(6.6, 3.65 + .75 * g, fall * fall), 0); kit.rotation.y = -.5 + a * .15;
      cam.position.set(Math.sin(a * .25) * 1, 5.7, 13.5); cam.lookAt(0, 5.2, 0); };
  } });
  // 9) Limit hız: kedi ~100 km/sa, insan ~190 km/sa
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#0a1838', '#010308'], rim: 0x7ee0ff });
    const cat = makeCat(); cat.position.set(-1.25, 5.6, 0); cat.scale.setScalar(.9); s.add(cat);
    const man = new THREE.Group(); man.position.set(1.4, 5.0, 0); s.add(man); const sk = std(0x3a6ad0, { roughness: .6 }), skin = std(0xd9b49a);
    const tb = M(new THREE.CapsuleGeometry(.3, .8, 8, 16), sk); man.add(tb); const hd = M(new THREE.SphereGeometry(.26, 24, 16), skin); hd.position.y = .82; man.add(hd);
    [[-.45, .4, .9], [.45, .4, -.9], [-.2, -.75, .25], [.2, -.75, -.25]].forEach(([x, y, r]) => { const l = M(new THREE.CapsuleGeometry(.1, .6, 6, 12), sk); l.position.set(x, y, 0); l.rotation.z = r; man.add(l); });
    man.rotation.x = Math.PI / 2 - .3;
    const sc = streaks(s, 12, 1.6, 3.4, 7.4, .35), sm = streaks(s, 12, 1.6, 3.4, 7.4, .5);
    const bars = [[-1.25, 0xffcf2e, .75], [1.4, 0xff6a3a, 1.42]].map(([x, c, h]) => { const b = M(rb(.5, 1, .2, .05), glow(c, .5)); b.userData = { x, h }; s.add(b); return b; });
    return t => {
      const a = t - S8; E.d.rotation.y = t * .02; cat.pose(0, 0, 0, 0, 0); cat.rotation.set(Math.sin(t * 2) * .05, -.4, 0); cat.position.y = 5.7 + Math.sin(t * 3) * .06;
      man.rotation.y = Math.sin(t * 1.5) * .2; man.position.y = 5.6 + Math.sin(t * 2.5) * .08;
      sc.up(t, 1.0, -1.25); sm.up(t, 2.0, 1.4);
      bars.forEach((b, i) => { const k = ease(prog(a, .5 + i * 3.4, .8)); const h = Math.max(.01, b.userData.h * k); b.scale.y = h; b.position.set(b.userData.x, 3.3 + h / 2, .3); });
      cam.position.set(Math.sin(a * .2) * .8, 5.6, 13.5); cam.lookAt(0, 5.2, 0); };
  } });
  // 10) Sıradaki soru: Mikrodalga fırın yemeği nasıl ısıtır?
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    const E = lights(s, { bg: ['#141032', '#020308'], rim: 0xff8a3a });
    const O = new THREE.Group(); O.position.set(0, 5.3, 0); s.add(O);
    const shell = std(0x3a3f48, { metalness: .7, roughness: .3 });
    [[4.2, .3, 2.6, 0, 1.1, 0], [4.2, .3, 2.6, 0, -1.1, 0], [.3, 2.5, 2.6, -2.0, 0, 0], [1.0, 2.5, 2.6, 1.6, 0, 0], [4.2, 2.5, .2, 0, 0, -1.2]].forEach(([w, h, d, x, y, z]) => { const p = M(rb(w, h, d, .1), shell); p.position.set(x, y, z); O.add(p); });
    const cav = M(new THREE.PlaneGeometry(2.9, 1.9), new THREE.MeshStandardMaterial({ color: 0xffb060, emissive: 0xff8a30, emissiveIntensity: .55 })); cav.position.set(-.5, 0, -1.08); O.add(cav);
    const il = new THREE.PointLight(0xffa040, 40, 6); il.position.set(-.5, .6, .4); O.add(il);
    const dc = document.createElement('canvas'); dc.width = dc.height = 128; { const g = dc.getContext('2d'); g.fillStyle = 'rgba(0,0,0,0)'; g.clearRect(0, 0, 128, 128); g.fillStyle = 'rgba(10,10,14,.55)';
      for (let y = 0; y < 128; y += 8) for (let x = 0; x < 128; x += 8) { g.beginPath(); g.arc(x + 4, y + 4, 1.6, 0, 7); g.fill(); } }
    const dt = new THREE.CanvasTexture(dc); dt.wrapS = dt.wrapT = THREE.RepeatWrapping; dt.repeat.set(6, 4);
    const door = M(new THREE.PlaneGeometry(2.9, 1.9), new THREE.MeshBasicMaterial({ map: dt, transparent: true, color: 0xffd8a0, opacity: .5, depthWrite: false })); door.position.set(-.5, 0, 1.32); O.add(door);
    const panel = M(rb(.8, 1.9, .1, .05), std(0x1a1d22, { metalness: .5 })); panel.position.set(1.55, 0, 1.3); O.add(panel);
    const dig = M(new THREE.PlaneGeometry(.6, .22), new THREE.MeshBasicMaterial({ color: 0x4ade80 })); dig.position.set(1.55, .6, 1.36); O.add(dig);
    const plate = new THREE.Group(); plate.position.set(-.5, -.85, .15); O.add(plate);
    plate.add(M(new THREE.CylinderGeometry(1, 1, .06, 64), new THREE.MeshStandardMaterial({ color: 0xdfe8f0, transparent: true, opacity: .7, roughness: .05 })));
    const bowl = M(new THREE.SphereGeometry(.55, 40, 20, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), std(0xe8e0d0, { side: THREE.DoubleSide })); bowl.position.y = .55; plate.add(bowl);
    const soup = M(new THREE.CircleGeometry(.5, 40), std(0xd06030, { emissive: 0x401000 })); soup.rotation.x = -Math.PI / 2; soup.position.y = .48; plate.add(soup);
    const waves = Array.from({ length: 4 }, (_, i) => { const pts = Array.from({ length: 40 }, (_, j) => V(-1.3 + j * 2.6 / 39, 0, 0)); const c = new THREE.CatmullRomCurve3(pts);
      const m = M(new THREE.TubeGeometry(c, 60, .025, 6), glow(0x7ee0ff, .8)); m.position.set(-.5, .55 - i * .25, -.6 + i * .35); O.add(m); m.userData = { pts, i }; return m; });
    const steam = Array.from({ length: 18 }, () => { const b = M(new THREE.SphereGeometry(.07, 10, 8), glow(0xffffff, .5)); b.userData = { x: (r1() - .5) * .6, ph: r1() }; plate.add(b); return b; });
    const q = qmark(s, 2.0, 7.3, .75);
    return t => {
      const a = t - S9; E.d.rotation.y = t * .02; plate.rotation.y = t * .8; O.rotation.y = -.25 + Math.sin(t * .4) * .12;
      waves.forEach(w => { w.geometry.dispose(); const P = w.userData.pts.map((p, j) => V(p.x, Math.sin(j * .6 - t * 8 + w.userData.i) * .1, 0)); w.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(P), 60, .025, 6); });
      steam.forEach(b => { const c = (t * .5 + b.userData.ph) % 1; b.position.set(b.userData.x, .5 + c * .9, Math.sin(c * 6) * .1); b.material.opacity = .5 * (1 - c); });
      cav.material.emissiveIntensity = .5 + .1 * Math.sin(t * 6);
      q.rotation.y = Math.sin(t * 2) * .4; q.visible = a > .3;
      cam.position.set(Math.sin(a * .2) * 1, 6.0, 13.5); cam.lookAt(0, 5.4, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'KEDİLER NEDEN HEP<br><span class="y">AYAKLARININ</span><br>ÜSTÜNE DÜŞER?', 84) },
    { t0: S1, t1: S2, html: T('ADI', 'DOĞRULMA<br><span class="y">REFLEKSİ</span>', 108) },
    { t0: S2, t1: S3, html: T('1. ADIM · İÇ KULAK', 'AŞAĞI<br><span class="y">NERESİ?</span>', 108) },
    { t0: S3, t1: S4, html: T('2. ADIM', 'BELİNDEN <span class="y">BÜKÜLÜR</span><br>ÖN AYAKLAR TOPLANIR', 82) },
    { t0: S4, t1: S5, html: BIG('ÖN YARI DÖNER', 'k90', 'DERECEYE KADAR', '90°') },
    { t0: S5, t1: S6, html: T('3. ADIM', 'ARKA YARI DA<br><span class="y">DÖNER</span>', 108) },
    { t0: S6, t1: S6b, html: T('SIRRI', 'ÇOK <span class="y">ESNEK</span><br>OMURGA', 108) },
    { t0: S6b, t1: S7, html: T('ÜSTELİK', 'İŞLEVSEL<br><span class="y">KÖPRÜCÜK KEMİĞİ</span> YOK', 84) },
    { t0: S7, t1: S8, html: `<div class="grad"></div><div class="tagw"><span class="tag">YAVRULARDA REFLEKS</span></div><div class="list" style="top:340px">
      <div class="row" id="r1">3-4 HAFTA <i>BAŞLAR</i></div><div class="row hl" id="r2">6-7 HAFTA <i>TAMAMLANIR</i></div></div>` },
    { t0: S8, t1: S9, html: BIG('DÜŞEN KEDİ EN FAZLA', 'k100', 'İNSANIN YARISI KADAR', '~100<small>KM/SA</small>') },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'MİKRODALGA FIRIN<br><span class="y">YEMEĞİ</span> NASIL<br>ISITIR?', 88) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k90', S4], ['k100', S8]];
  const rows = [['r1', 24.88], ['r2', 26.64]];
  return {
    END: 39.96, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; });
      rows.forEach(([id, t0]) => { const k = q(id); if (k) { const p = prog(t, t0, .35); k.style.opacity = p; k.style.transform = `translateX(${(1 - easeOut(p)) * -80}px)`; } }); },
    follow: { t: 38.16, click: 39.06 },
    sfx: [[.3, 'whoosh', .5], [1.4, 'pop_low', .5], [S1 + .2, 'whoosh', .4], [S1 + 1.5, 'ding', .4], [S2 + .3, 'pop', .4], [S2 + 1.6, 'ding', .5],
      [S3 + .3, 'whoosh', .4], [S3 + 1.8, 'snap', .4], [S4 + .3, 'whoosh', .5], [S4 + 1.6, 'ding', .4], [S5 + .4, 'snap', .4], [S5 + 2.6, 'pop_low', .6],
      [S6 + .3, 'click', .4], [S6b, 'pop', .4], [S6b + .6, 'snap', .5], [24.88, 'click', .4], [26.64, 'ding', .5], [S8 + .5, 'whoosh', .5], [S8 + 3.9, 'whoosh', .5],
      [S9 + .4, 'whoosh', .5], [S9 + 1.0, 'ding', .4]],
  };
};
