// Bilgi #6: Karınca yüksekten düşünce neden ölmez? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: J.B.S. Haldane, "On Being the Right Size" (1926) — "An insect, therefore, is not afraid of gravity";
// kare-küp yasası ve limit hız (scienceabc.com; Univ. of Illinois Physics Van Q&A #2099: karıncanın limit hızı ~2 m/sn ≈ 7 km/sa);
// insan serbest düşüş limit hızı ~200 km/sa.
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const concrete = () => std(0x3a3f47, { roughness: .9 });
  let seed = 31; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
  function person(body) {
    const g = new THREE.Group();
    g.add(M(new THREE.CapsuleGeometry(.3, .5, 8, 16), std(body, { roughness: .7 })));
    const head = M(new THREE.SphereGeometry(.27, 24, 16), std(0xd9b49a, { roughness: .6 })); head.position.y = .75; g.add(head);
    const arms = []; for (const k of [-1, 1]) { const a = M(new THREE.CapsuleGeometry(.1, .55, 6, 12), std(body)); a.position.set(k * .42, .15, 0); g.add(a); arms.push(a); }
    const legs = []; for (const k of [-1, 1]) { const l = M(new THREE.CapsuleGeometry(.12, .6, 6, 12), std(0x22303f)); l.position.set(k * .16, -.75, 0); g.add(l); legs.push(l); }
    g.userData = { arms, legs }; return g;
  }
  // karınca: yürüme için bacak grupları
  function ant(col = 0x4a1d10) {
    const g = new THREE.Group(); const m = std(col, { roughness: .28, metalness: .3 });
    const ab = M(new THREE.SphereGeometry(.55, 32, 24), m); ab.scale.set(1.35, 1, 1); ab.position.set(-1.15, .15, 0); g.add(ab);
    const pet = M(new THREE.SphereGeometry(.14, 16, 12), m); pet.position.set(-.45, .05, 0); g.add(pet);
    const th = M(new THREE.SphereGeometry(.3, 24, 18), m); th.scale.set(1.6, .85, .85); g.add(th);
    const hd = M(new THREE.SphereGeometry(.34, 24, 18), m); hd.position.set(.78, .12, 0); g.add(hd);
    const eye = std(0x050505, { roughness: .1, metalness: .5 });
    for (const k of [-1, 1]) { const e = M(new THREE.SphereGeometry(.08, 12, 8), eye); e.position.set(.95, .2, k * .24); g.add(e); }
    const lm = std(0x2a0f08, { roughness: .4 }); const legs = [];
    for (let i = 0; i < 3; i++) for (const k of [-1, 1]) {
      const l = new THREE.Group(); l.position.set(-.3 + i * .3, 0, k * .18); g.add(l);
      const up = M(new THREE.CylinderGeometry(.045, .04, .6, 8), lm); up.rotation.x = k * -1.0; up.position.set(0, .14, k * .26); l.add(up);
      const lo = M(new THREE.CylinderGeometry(.04, .025, .75, 8), lm); lo.rotation.x = k * -.35; lo.position.set(0, -.18, k * .6); l.add(lo);
      l.rotation.y = (i - 1) * .45 * -k; l.userData = { i, k }; legs.push(l); }
    for (const k of [-1, 1]) { const an = M(new THREE.CylinderGeometry(.025, .018, .8, 6), lm); an.position.set(1.15, .5, k * .2); an.rotation.set(k * .35, 0, -.8); g.add(an); }
    g.userData.legs = legs;
    g.userData.walk = t => legs.forEach(l => { const ph = (l.userData.i + (l.userData.k > 0 ? 1 : 0)) % 2 ? 0 : Math.PI; l.rotation.z = Math.sin(t * 16 + ph) * .35; });
    return g;
  }
  function tower(s, x = -8, z = -4, H = 80) {
    const T = new THREE.Group(); s.add(T);
    const tw = M(rb(10, H, 10, .3), std(0x1d2633, { metalness: .6, roughness: .35 })); tw.position.set(x, -H / 2, z); T.add(tw);
    const wm = [0xffd27a, 0x9fd3ff, 0x101824, 0x101824].map(c => new THREE.MeshBasicMaterial({ color: c }));
    for (let y = -H + 2; y < -1; y += 2.2) for (let xx = x - 4; xx <= x + 4; xx += 2) { const w = M(new THREE.PlaneGeometry(1.1, 1.3), wm[(r1() * 4) | 0]); w.position.set(xx, y, z + 5.02); T.add(w); }
    const ledge = M(rb(11, .6, 11, .15), std(0x3a4350, { metalness: .5 })); ledge.position.set(x, .3, z); T.add(ledge);
    for (let i = 0; i < 16; i++) { const h = 10 + r1() * 40; const b = M(new THREE.BoxGeometry(6, h, 6), std(0x141c28, { roughness: .8 })); b.position.set(-50 + i * 7 + r1() * 3, -80 + h / 2, -45 - r1() * 30); s.add(b); }
    return T;
  }
  const streaks = (s, n, color = 0xcfe8ff) => { const a = []; for (let i = 0; i < n; i++) { const l = M(new THREE.BoxGeometry(.05, 2 + r1() * 4, .05), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .5, blending: THREE.AdditiveBlending, depthWrite: false }));
    l.userData = { x: (r1() - .5) * 26, z: (r1() - .5) * 14, o: r1() * 40 }; s.add(l); a.push(l); } return a; };

  const S1 = 3.1, S2 = 6.3, S3 = 8.1, S4 = 12.1, S5 = 15.9, S6 = 21.2, S7 = 24.3, S8 = 27.45, S9 = 32.6;

  // 1) Gökdelenin tepesinde karınca, aşağı düşer
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1a2f58', '#03060d'], near: 50, far: 170, key: 1800, rim: 0xff9a3a }); tower(s);
    const A = ant(); A.scale.setScalar(1.6); s.add(A); const d = dust(500, [60, 60, 40], 0x9fc4ff, .2, .45); s.add(d);
    const jump = 1.5;
    return t => {
      if (t < jump) { A.position.set(-4.2 + t * .6, 1.55, 0); A.rotation.set(0, 0, 0); A.userData.walk(t); }
      else { const a = t - jump; A.position.set(-3.3 + a * 1.4, 1.55 - a * a * 3.2, Math.sin(a * 1.7) * .8); A.rotation.set(a * 1.5, a * .8, -a * 2.4); }
      d.rotation.y = t * .03;
      const fy = t < jump ? 1.5 : 1.55 - (t - jump) * (t - jump) * 3.2 * .7;
      cam.position.set(10, fy + 5, 34); cam.lookAt(-1, fy + 1.2, 0); };
  } });
  // 2) Yere iner, silkelenir, yürür gider
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#16294a', '#03060d'], near: 30, far: 90 }); key.target.position.set(0, 0, 0);
    const gr = M(new THREE.CylinderGeometry(40, 40, 1, 64), std(0x3b3f45, { roughness: .95 })); gr.position.y = -.5; s.add(gr);
    for (let i = 0; i < 40; i++) { const p = M(new THREE.SphereGeometry(.15 + r1() * .35, 12, 8), std(0x55595f, { roughness: 1 })); p.position.set((r1() - .5) * 26, 0, (r1() - .5) * 14); p.scale.y = .5; s.add(p); }
    const A = ant(); A.scale.setScalar(1.6); s.add(A);
    const puff = dust(120, [3, 1, 3], 0xd8d0c0, .25, .6); s.add(puff);
    const land = S1 + .35;
    return t => {
      let y = 0.95, x = -2, rz = 0;
      if (t < land) { const a = (land - t); y = .95 + a * 14; rz = a * 6; }
      else { const a = t - land; y = .95 + Math.abs(Math.sin(a * 9)) * .9 * Math.exp(-a * 5); }
      const shake = t > land + .5 && t < land + 1.3 ? Math.sin(t * 60) * .12 : 0;
      if (t > land + 1.4) { x = -2 + (t - land - 1.4) * 2.4; A.userData.walk(t); }
      A.position.set(x, y, 0); A.rotation.set(shake, 0, rz);
      const pk = prog(t, land, .9); puff.position.set(-2, .3 + pk, 0); puff.scale.setScalar(.5 + pk * 2.5); puff.material.opacity = (1 - pk) * .6 * (t > land ? 1 : 0);
      cam.position.set(lerp(-4, 1, prog(t, S1, 3.2)), 6, 26); cam.lookAt(lerp(-1, 1, prog(t, S1, 3.2)), 3.4, 0); };
  } });
  // 3) Sırrı küçüklük: dev ayakkabının yanında minik karınca
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#16294a', '#03060d'], near: 30, far: 120 }); key.target.position.set(0, 0, 0);
    const gr = M(new THREE.CylinderGeometry(60, 60, 1, 64), std(0x3b3f45, { roughness: .95 })); gr.position.y = -.5; s.add(gr);
    const shoe = new THREE.Group(); s.add(shoe); shoe.position.set(4, 0, -2);
    const sole = M(rb(14, 1.2, 5.5, .5), std(0xeeeeee, { roughness: .6 })); sole.position.y = .6; shoe.add(sole);
    const up = M(new THREE.SphereGeometry(4, 40, 24, 0, Math.PI * 2, 0, Math.PI / 2), std(0x1f4fa8, { roughness: .55 })); up.scale.set(1.7, 1.2, .68); up.position.set(-.5, 1.2, 0); shoe.add(up);
    const A = ant(); A.scale.setScalar(.45); s.add(A);
    return t => { A.position.set(-6 + (t - S2) * .9, .28, 3); A.userData.walk(t);
      const k = ease(prog(t, S2, 1.8)); cam.position.set(lerp(-6, -2, k), lerp(1.6, 10, k), lerp(5, 34, k)); cam.lookAt(lerp(-5, 0, k), lerp(.4, 4.2, k), lerp(3, 0, k)); };
  } });
  // 4) Kare-küp: büyük küp 27 küçük küpe bölünür (ağırlık aynı, yüzey artar)
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#14264a', '#02050c'], rim: 0xffb02e }); key.target.position.set(0, 3, 0);
    const pl = M(new THREE.CylinderGeometry(9, 9, .6, 64), std(0x232a35, { metalness: .5, roughness: .4 })); pl.position.y = -.3; s.add(pl);
    const cubes = []; const m = std(0xffcf2e, { metalness: .4, roughness: .3, emissive: 0x2a1a00 });
    for (let i = 0; i < 27; i++) { const c = M(rb(1.96, 1.96, 1.96, .12), m.clone()); c.userData = { x: i % 3 - 1, y: ((i / 3) | 0) % 3 - 1, z: ((i / 9) | 0) - 1 }; s.add(c); cubes.push(c); }
    const d = dust(300, [20, 14, 14], 0xffe7a0, .12, .4); d.position.y = 4; s.add(d);
    return t => {
      const k = ease(prog(t, 9.2, 1.6)); const sh = lerp(2, .9, ease(prog(t, 10.4, 1.4)));
      cubes.forEach(c => { const u = c.userData; const sp = 2 + k * 1.6; c.position.set(u.x * sp, 3.2 + u.y * sp, u.z * sp); });
      cubes.forEach((c, i) => { const hide = i !== 13 && t > 10.4; c.visible = !hide || prog(t, 10.4, .6) < 1; c.material.transparent = true; c.material.opacity = i === 13 ? 1 : 1 - (t > 10.4 ? prog(t, 10.4, .6) : 0); });
      const center = cubes[13]; if (t > 10.4) { center.position.set(0, lerp(3.2, 2, prog(t, 10.4, 1.4)), 0); }
      d.rotation.y = t * .05;
      const a = .5 + (t - S3) * .12; cam.position.set(Math.sin(a) * 30, 11, Math.cos(a) * 30); cam.lookAt(0, 3.4, 0); };
  } });
  // 5) Hava paraşüt gibi: yavaş süzülen karınca, yukarı akan hava
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1b3563', '#040a18'], rim: 0x7fd8ff }); const A = ant(); A.scale.setScalar(1.6); s.add(A);
    const st = streaks(s, 70, 0xbfe6ff);
    const chute = new THREE.Group(); s.add(chute);
    const cm = M(new THREE.SphereGeometry(3.4, 40, 16, 0, Math.PI * 2, 0, Math.PI / 2.4), new THREE.MeshStandardMaterial({ color: 0x7fd8ff, transparent: true, opacity: .22, side: THREE.DoubleSide, emissive: 0x1a5a80, depthWrite: false })); chute.add(cm);
    const lines = []; for (let i = 0; i < 8; i++) { const l = M(new THREE.CylinderGeometry(.02, .02, 3.6, 4), new THREE.MeshBasicMaterial({ color: 0x9fe0ff, transparent: true, opacity: .4 })); chute.add(l); lines.push([l, i / 8 * Math.PI * 2]); }
    const d = dust(400, [30, 40, 20], 0xcfe8ff, .15, .4); s.add(d);
    return t => {
      const y = 3 + Math.sin(t * 1.3) * .4; A.position.set(0, y, 0); A.rotation.set(Math.sin(t * 1.7) * .3, t * .4, Math.sin(t * 1.1) * .25);
      const ck = easeOut(prog(t, 13.3, .8)); chute.visible = ck > 0; chute.scale.setScalar(Math.max(.01, ck)); chute.position.set(0, y + 3.2, 0); chute.rotation.y = t * .4;
      lines.forEach(([l, a]) => { l.position.set(Math.cos(a) * 1.6, -1.6, Math.sin(a) * 1.6); l.rotation.set(Math.sin(a) * .45, 0, -Math.cos(a) * .45); });
      st.forEach(l => { const u = l.userData; l.position.set(u.x, ((u.o + t * 10) % 40) - 18, u.z); });
      d.position.y = (t * 3) % 10;
      cam.position.set(Math.sin(t * .15) * 6, 5, 26); cam.lookAt(0, 5.7, 0); };
  } });
  // 6) Karıncanın limit hızı ~7 km/sa
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#14294f', '#03070f'], rim: 0x5fd0ff }); tower(s, -9, -6, 160);
    const A = ant(); A.scale.setScalar(1.4); s.add(A); const st = streaks(s, 40);
    return t => {
      const a = t - S5; A.position.set(1.5, 2 - a * 1.9, 0); A.rotation.set(Math.sin(t * 1.5) * .3, t * .5, .4 + Math.sin(t) * .2);
      st.forEach(l => { const u = l.userData; l.position.set(u.x, A.position.y + ((u.o + a * 3) % 40) - 20, u.z); l.scale.y = .4; });
      cam.position.set(9, A.position.y + 3.5, 26); cam.lookAt(-1, A.position.y + 2.6, 0); };
  } });
  // 7) İnsan ~200 km/sa
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#14294f', '#03070f'], rim: 0xff6a3a }); const st = streaks(s, 120, 0xffe0c0);
    const P = person(0xb91c1c); P.scale.setScalar(2.6); s.add(P);
    const d = dust(400, [30, 40, 20], 0xcfe8ff, .15, .4); s.add(d);
    return t => {
      P.position.set(0, 3.8 + Math.sin(t * 20) * .06, 0); P.rotation.set(-1.1, .3 + Math.sin(t * 2) * .1, Math.sin(t * 3) * .1);
      P.userData.arms.forEach((a, i) => a.rotation.z = (i ? -1 : 1) * (1.2 + Math.sin(t * 25 + i) * .15));
      st.forEach(l => { const u = l.userData; l.position.set(u.x, ((u.o + t * 60) % 40) - 18, u.z); l.scale.y = 2.2; });
      d.position.y = (t * 30) % 20 - 10;
      cam.position.set(Math.sin(t * .2) * 4 + 3, 6, 22 + Math.sin(t * 40) * .05); cam.lookAt(0, 4.4, 0); };
  } });
  // 8) Dış iskelet: parlayan zırh
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#1a2440', '#03050b'], rim: 0xffcf2e, key: 2600 }); key.target.position.set(0, 3, 0);
    const pl = M(new THREE.CylinderGeometry(8, 8, .6, 64), std(0x232a35, { metalness: .6, roughness: .35 })); pl.position.y = -.3; s.add(pl);
    const A = ant(0x5a2412); A.scale.setScalar(2.4); s.add(A);
    const sh = M(new THREE.SphereGeometry(4.4, 48, 32), new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: .0, wireframe: true, blending: THREE.AdditiveBlending, depthWrite: false })); s.add(sh);
    const d = dust(300, [20, 14, 14], 0xffe7a0, .12, .4); d.position.y = 4; s.add(d);
    return t => {
      A.position.set(0, 2.3, 0); A.rotation.y = (t - S7) * .9 + .6; A.userData.walk(t * .3);
      const k = prog(t, 25.6, .5); sh.position.set(0, 2.6, 0); sh.scale.set(1.4, .75, .75); sh.rotation.y = A.rotation.y; sh.material.opacity = k * (.25 + .1 * Math.sin(t * 8));
      d.rotation.y = t * .05;
      cam.position.set(4, 7, 22); cam.lookAt(0, 3.2, 0); };
  } });
  // 9) Haldane, 1926 (sepya): açık kitabın üstünde yürüyen karınca
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    s.background = gradTex('#3a2614', '#0a0603'); s.fog = new THREE.Fog(0x140c06, 30, 100);
    s.add(new THREE.HemisphereLight(0xffd9a8, 0x1a0f08, .7));
    const key = new THREE.SpotLight(0xffe2b0, 2400, 120, .4, .5, 1.1); key.position.set(-6, 30, 20); s.add(key); key.target.position.set(0, 0, 0); s.add(key.target);
    const rim = new THREE.PointLight(0xff9a4a, 300, 60); rim.position.set(14, 8, -10); s.add(rim);
    const desk = M(rb(40, 1, 24, .3), std(0x4a2f1a, { roughness: .75 })); desk.position.y = -.5; s.add(desk);
    const book = new THREE.Group(); s.add(book);
    const cover = M(rb(16, .4, 11, .1), std(0x6b2a1a, { roughness: .7 })); cover.position.y = .2; book.add(cover);
    const pg = std(0xf0e2c0, { roughness: .9 });
    for (const k of [-1, 1]) { const p = M(rb(7.6, .5, 10.2, .1), pg); p.position.set(k * 3.9, .6, 0); p.rotation.z = k * -.05; book.add(p);
      for (let i = 0; i < 9; i++) { const ln = M(new THREE.BoxGeometry(5.6 - (i % 3) * .8, .02, .18), std(0x5a4a3a)); ln.position.set(k * 3.9 - (i % 3) * .3, .87 + k * -.0, -3.8 + i * .9); book.add(ln); } }
    const A = ant(); A.scale.setScalar(.8); s.add(A);
    const lamp = new THREE.PointLight(0xffc070, 120, 30); lamp.position.set(-6, 8, 4); s.add(lamp);
    const d = dust(300, [30, 16, 20], 0xffd9a8, .14, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S8; A.position.set(-6 + a * 2.2, 1.35, 1.5 - a * .3); A.rotation.y = .12; A.userData.walk(t);
      d.rotation.y = t * .03;
      cam.position.set(lerp(-4, 4, ease(prog(t, S8, 5.1))), 11, 21); cam.lookAt(0, 1.6, 0); };
  } });
  // 10) Sıradaki soru: Ay'da zıplayan astronot
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    s.background = gradTex('#0a1430', '#000000'); s.fog = new THREE.Fog(0x02040a, 60, 160);
    s.add(new THREE.HemisphereLight(0x8fa8d0, 0x0a0a0a, .4));
    const sun = new THREE.DirectionalLight(0xffffff, 3); sun.position.set(-20, 18, 14); s.add(sun);
    const geo = new THREE.PlaneGeometry(120, 80, 160, 100); geo.rotateX(-Math.PI / 2); const P = geo.attributes.position;
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), z = P.getZ(i); let y = .5 * hash(x * .3, 0, z * .3);
      for (const [cx, cz, r] of [[-8, -6, 4], [10, -14, 6], [3, 6, 2.5], [-18, 4, 5]]) { const d = Math.hypot(x - cx, z - cz) / r; if (d < 1.3) y += d < 1 ? -1.4 * (1 - d * d) : .9 * (1.3 - d) / .3 * (d - 1) / .3; }
      P.setY(i, y); }
    geo.computeVertexNormals(); s.add(M(geo, std(0x9a9a9e, { roughness: 1 })));
    const st = dust(1200, [400, 200, 50], 0xffffff, .6, .8); st.position.set(0, 60, -120); s.add(st);
    const earth = M(new THREE.SphereGeometry(5, 48, 32), std(0x2f6fd0, { roughness: .6, emissive: 0x0a2050 })); earth.position.set(16, 40, -100); s.add(earth);
    const as = new THREE.Group(); s.add(as);
    const suit = std(0xf2f2f2, { roughness: .6 });
    const body = M(new THREE.CapsuleGeometry(.75, 1.1, 8, 20), suit); as.add(body);
    const helm = M(new THREE.SphereGeometry(.62, 32, 20), suit); helm.position.y = 1.45; as.add(helm);
    const visor = M(new THREE.SphereGeometry(.5, 32, 20, 0, Math.PI, 0, Math.PI), std(0xd4a020, { metalness: 1, roughness: .1 })); visor.position.set(0, 1.45, .18); as.add(visor);
    const pack = M(rb(1.2, 1.4, .6, .1), suit); pack.position.set(0, .3, -.7); as.add(pack);
    const legs = []; for (const k of [-1, 1]) { const l = M(new THREE.CapsuleGeometry(.28, .8, 6, 12), suit); l.position.set(k * .35, -1.4, 0); as.add(l); legs.push(l);
      const ar = M(new THREE.CapsuleGeometry(.22, .8, 6, 12), suit); ar.position.set(k * .95, .3, 0); ar.rotation.z = k * .4; as.add(ar); }
    const puff = dust(150, [3, .6, 3], 0xbdbdbd, .2, .6); s.add(puff);
    return t => {
      const a = (t - S9) % 3.2; const h = Math.max(0, 4.6 * Math.sin(a / 3.2 * Math.PI));
      as.position.set(0, 2.6 + h, 0); as.rotation.y = .4; legs.forEach(l => l.rotation.x = h > .2 ? .4 : 0);
      const pk = prog(a, 0, .8); puff.position.set(0, .4 + pk * .5, 0); puff.scale.setScalar(.5 + pk * 2); puff.material.opacity = (1 - pk) * .6;
      cam.position.set(6, 6.5, 26); cam.lookAt(0, 5.2, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'KARINCA GÖKDELENDEN <span class="y">DÜŞSE?</span>', 100) },
    { t0: S1, t1: S2, html: T('CEVAP', 'HİÇBİR <span class="y">ŞEY!</span>') },
    { t0: S2, t1: S3, html: T('SIRRI', '<span class="y">KÜÇÜKLÜK</span>') },
    { t0: S3, t1: S4, html: T('KÜÇÜLDÜKÇE', 'AĞIRLIK <span class="y">HIZLA</span> AZALIR', 104) },
    { t0: S4, t1: S5, html: T('HAVA DİRENCİ', 'BİR <span class="y">PARAŞÜT</span> GİBİ', 104) },
    { t0: S5, t1: S6, html: `<div class="grad"></div><div class="tagw"><span class="tag">KARINCANIN DÜŞÜŞ HIZI</span></div><div class="big" style="top:310px;font-size:170px" id="v1"></div><div class="sub" style="top:490px">KM/SAAT · YÜRÜYÜŞ HIZI</div>` },
    { t0: S6, t1: S7, html: `<div class="grad"></div><div class="tagw"><span class="tag">İNSANIN DÜŞÜŞ HIZI</span></div><div class="big" style="top:310px;font-size:170px" id="v2"></div><div class="sub" style="top:490px">KM/SAAT</div>` },
    { t0: S7, t1: S8, html: T('SERT ZIRH', 'DIŞ <span class="y">İSKELET</span>') },
    { t0: S8, t1: 30.3, html: T('J.B.S. HALDANE · 1926', 'TEK <span class="y">CÜMLE</span>') },
    { t0: 30.3, t1: S9, html: T('J.B.S. HALDANE · 1926', '"BÖCEKLER YERÇEKİMİNDEN <span class="y">KORKMAZ"</span>', 84) },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'AY\'DA NE KADAR YÜKSEĞE <span class="y">ZIPLARSIN?</span>', 88) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 38.28, shots, titles,
    update: (t, q) => {
      if (q('v1')) q('v1').innerHTML = '~' + Math.round(7 * easeOut(prog(t, 16.0, 1.6)));
      if (q('v2')) q('v2').innerHTML = '~' + Math.round(200 * easeOut(prog(t, 21.3, 1.6)));
    },
    follow: { t: 36.48, click: 37.38 },
    sfx: [[1.5, 'whoosh', .7], [S1 + .35, 'pop_low', 1], [S1 + .37, 'snap', .6], [9.2, 'pop', .9], [10.4, 'pop_low', .8], [13.3, 'pop', .8], [18.4, 'ding', .7], [22.6, 'whoosh', 1], [23.0, 'ding', .6], [25.6, 'ding', .8], [30.4, 'pop', .8], [S9 + .1, 'pop_low', .6], [S9 + 3.3, 'pop_low', .6]],
  };
};
