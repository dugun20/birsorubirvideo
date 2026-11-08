// Bilgi #3: Uçaklar havada nasıl durur? (koyu sinematik tarz, şablon: videos/asansor)
// Kaynaklar: Airbus A380 Facts & Figures (MTOW 575 t, Mach 0.85), Science Learning Hub "Wings and lift",
// AirHelp "How high do planes fly" (31.000–42.000 ft ≈ 9,5–12,8 km).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const steel = () => std(0xaeb6c0, { metalness: .85, roughness: .3 });
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
    const key = new THREE.SpotLight(0xfff1dc, o.key || 2200, 200, .5, .55, 1.2); key.position.set(-18, 44, 34); s.add(key); s.add(key.target);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, o.rimI || 700, 90); rim.position.set(20, 16, -14); s.add(rim);
    return key;
  }
  // ok: gövde silindir + koni, +y yönünde, uzunluk ölçekle
  function arrow(color, r = .32) {
    const g = new THREE.Group(); const m = std(color, { emissive: color, emissiveIntensity: .55, roughness: .4 });
    const sh = M(new THREE.CylinderGeometry(r, r, 1, 20), m); sh.position.y = .5; g.add(sh);
    const hd = M(new THREE.ConeGeometry(r * 2.4, r * 4, 24), m); g.add(hd);
    g.userData.set = len => { len = Math.max(.001, len); const b = Math.max(.001, len - r * 4); sh.scale.y = b; sh.position.y = b / 2; hd.position.y = b + r * 2; g.visible = len > .05; };
    g.userData.m = m; return g;
  }
  // yolcu uçağı (burun +x yönünde)
  function airliner(livery = 0xc0392b) {
    const g = new THREE.Group();
    const al = std(0xe9eef3, { metalness: .55, roughness: .3 });
    const body = M(new THREE.CapsuleGeometry(1, 10, 16, 32), al); body.rotation.z = Math.PI / 2; body.scale.set(1, 1, 1); g.add(body);
    const deck = M(new THREE.CapsuleGeometry(.85, 5.5, 12, 24), al); deck.rotation.z = Math.PI / 2; deck.position.set(1.2, .35, 0); g.add(deck);
    const win = M(rb(9, .16, 2.06, .06), new THREE.MeshBasicMaterial({ color: 0x1b2c44 })); win.position.set(.2, .25, 0); g.add(win);
    const cock = M(rb(.7, .25, 1.4, .1), new THREE.MeshBasicMaterial({ color: 0x0d1828 })); cock.position.set(5.7, .45, 0); g.add(cock);
    const wingShape = k => { const s = new THREE.Shape(); s.moveTo(2.2, 0); s.lineTo(-2.4, 8 * k); s.lineTo(-3.4, 8 * k); s.lineTo(-2.6, 0); s.closePath(); return s; };
    [-1, 1].forEach(k => {
      const w = M(new THREE.ExtrudeGeometry(wingShape(k), { depth: .22, bevelEnabled: true, bevelThickness: .08, bevelSize: .08, bevelSegments: 3 }), al);
      w.rotation.x = -Math.PI / 2; w.position.y = -.55; g.add(w);
      const tip = M(rb(.7, 1.1, .12, .05), std(livery, { metalness: .4 })); tip.position.set(-3.0, 0, 8 * -k); g.add(tip);
      [2.8, 5.2].forEach(z => { const zz = z * -k; const lx = 2.2 - 4.6 * (z / 8);
        const e = M(new THREE.CylinderGeometry(.48, .4, 1.6, 24), dark()); e.rotation.z = Math.PI / 2; e.position.set(lx + .3, -1.05, zz); g.add(e);
        const ring = M(new THREE.TorusGeometry(.45, .06, 8, 24), steel()); ring.rotation.y = Math.PI / 2; ring.position.set(lx + 1.1, -1.05, zz); g.add(ring); });
      const st = new THREE.Shape(); st.moveTo(0, 0); st.lineTo(-1.6, 3 * k); st.lineTo(-2.3, 3 * k); st.lineTo(-1.6, 0); st.closePath();
      const hs = M(new THREE.ExtrudeGeometry(st, { depth: .12, bevelEnabled: true, bevelThickness: .04, bevelSize: .04, bevelSegments: 2 }), al);
      hs.rotation.x = -Math.PI / 2; hs.position.set(-4.4, .1, 0); g.add(hs);
    });
    const fs = new THREE.Shape(); fs.moveTo(-3.6, .6); fs.lineTo(-5.8, 4.4); fs.lineTo(-6.8, 4.4); fs.lineTo(-6.2, .6); fs.closePath();
    const fin = M(new THREE.ExtrudeGeometry(fs, { depth: .16, bevelEnabled: true, bevelThickness: .05, bevelSize: .05, bevelSegments: 2 }), std(livery, { metalness: .4, roughness: .35 }));
    fin.position.z = -.08; g.add(fin);
    const nav = [0xff2a2a, 0x2aff6a].map((c, k) => { const m = M(new THREE.SphereGeometry(.16, 10, 10), new THREE.MeshBasicMaterial({ color: c })); m.position.set(-3.0, -.4, (k ? 8.1 : -8.1)); g.add(m); return m; });
    const strobe = M(new THREE.SphereGeometry(.14, 10, 10), new THREE.MeshBasicMaterial({ color: 0xffffff })); strobe.position.set(-6.5, 4.5, 0); g.add(strobe);
    g.userData.blink = t => { strobe.visible = (t * 1.3) % 1 < .12; };
    return g;
  }
  function clouds(s, n, sp, y, col = 0x6f7fa3, op = .9, size = 1) {
    const cm = new THREE.MeshStandardMaterial({ color: col, roughness: 1, transparent: true, opacity: op });
    const g = new THREE.Group(); s.add(g);
    for (let i = 0; i < n; i++) { const c = M(new THREE.SphereGeometry((2 + r1() * 3.5) * size, 20, 14), cm); c.position.set((r1() - .5) * sp[0], y + r1() * 2.5, (r1() - .5) * sp[1]); c.scale.y = .5; g.add(c); }
    return g;
  }
  // NACA 2412 benzeri kanat kesiti, veter 10 (x: -5..5)
  const CH = 10, TK = .15, CM = .04, CP = .4;
  const camber = u => u < CP ? CM / (CP * CP) * (2 * CP * u - u * u) : CM / ((1 - CP) ** 2) * ((1 - 2 * CP) + 2 * CP * u - u * u);
  const thick = u => 5 * TK * (.2969 * Math.sqrt(u) - .126 * u - .3516 * u * u + .2843 * u ** 3 - .1036 * u ** 4);
  function airfoil(depth, mat) {
    const s = new THREE.Shape(); const N = 60;
    for (let i = 0; i <= N; i++) { const u = (1 - Math.cos(Math.PI * i / N)) / 2; const x = u * CH - CH / 2, y = (camber(u) + thick(u)) * CH; i ? s.lineTo(x, y) : s.moveTo(x, y); }
    for (let i = N - 1; i > 0; i--) { const u = (1 - Math.cos(Math.PI * i / N)) / 2; s.lineTo(u * CH - CH / 2, (camber(u) - thick(u)) * CH); }
    s.closePath();
    const geo = new THREE.ExtrudeGeometry(s, { depth, bevelEnabled: true, bevelThickness: .1, bevelSize: .06, bevelSegments: 4, curveSegments: 24 });
    geo.translate(0, 0, -depth / 2); return M(geo, mat);
  }
  // akım çizgisi (ön kenar -x, hava +x yönünde); a = hücum açısı (rad)
  function flowY(x, y0, a) {
    const ta = Math.tan(a);
    let c, th = 0;
    if (x < -5) c = 5 * ta * Math.exp((x + 5) / 3.5);
    else if (x <= 5) { const u = (x + 5) / CH; c = camber(u) * CH - x * ta; th = thick(u) * CH; }
    else c = -5 * ta - (x - 5) * ta * .75 * Math.exp(-(x - 5) / 14);
    return y0 + c * Math.exp(-Math.abs(y0) / 5) + Math.sign(y0) * th * Math.exp(-Math.abs(y0) / 2.5);
  }
  function flowField(s, rows, perRow, layers, colorFn) {
    const n = rows.length * perRow * layers.length;
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3), col = new Float32Array(n * 3);
    g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const pts = new THREE.Points(g, new THREE.PointsMaterial({ size: .34, vertexColors: true, transparent: true, opacity: .95, depthWrite: false, blending: THREE.AdditiveBlending }));
    s.add(pts);
    const lines = [];
    rows.forEach(y0 => layers.forEach(z => {
      const lp = []; for (let x = -16; x <= 16; x += .25) lp.push(new THREE.Vector3(x, 0, z));
      const lg = new THREE.BufferGeometry().setFromPoints(lp);
      const ln = new THREE.Line(lg, new THREE.LineBasicMaterial({ color: colorFn(y0), transparent: true, opacity: .4 })); s.add(ln); lines.push({ ln, y0, z });
    }));
    const ph = []; for (let i = 0; i < n; i++) ph.push(r1());
    return (t, a, spd, vis = 1) => {
      let k = 0;
      rows.forEach(y0 => layers.forEach(z => { for (let j = 0; j < perRow; j++, k++) {
        const v = spd(y0); const x = ((ph[k] * 32 + j * 32 / perRow + t * v) % 32) - 16;
        p[k * 3] = x; p[k * 3 + 1] = flowY(x, y0, a); p[k * 3 + 2] = z;
        const c = new THREE.Color(colorFn(y0)); const fade = clamp((16 - Math.abs(x)) / 3) * vis; col[k * 3] = c.r * fade; col[k * 3 + 1] = c.g * fade; col[k * 3 + 2] = c.b * fade; } }));
      g.attributes.position.needsUpdate = true; g.attributes.color.needsUpdate = true;
      lines.forEach(L2 => { const pa = L2.ln.geometry.attributes.position; for (let i = 0; i < pa.count; i++) pa.setY(i, flowY(pa.getX(i), L2.y0, a)); pa.needsUpdate = true; L2.ln.material.opacity = .4 * vis; });
    };
  }
  function tunnel(s) {
    lights(s, { bg: ['#0c1f3c', '#02050c'], near: 30, far: 110, key: 1800 });
    const grid = new THREE.GridHelper(80, 40, 0x1d4a6e, 0x10263d); grid.position.y = -9; s.add(grid);
    const d = dust(300, [40, 24, 20], 0x9fc4ff, .12, .35); s.add(d); return d;
  }

  // 1) Gece pist: dev uçak kalkışa geçer
  shots.push({ t0: 0, t1: 6.0, fov: 40, build: (s, cam) => {
    const key = lights(s, { bg: ['#16335e', '#03070f'], near: 50, far: 200, key: 1700 });
    const gr = M(new THREE.PlaneGeometry(500, 500), std(0x0b1018, { roughness: .5, metalness: .3 })); gr.rotation.x = -Math.PI / 2; s.add(gr);
    const rw = M(new THREE.PlaneGeometry(300, 9), std(0x1a1f27, { roughness: .8 })); rw.rotation.x = -Math.PI / 2; rw.position.y = .02; s.add(rw);
    for (let x = -150; x < 150; x += 6) {
      const st = M(new THREE.PlaneGeometry(3, .3), new THREE.MeshBasicMaterial({ color: 0xdfe6ee })); st.rotation.x = -Math.PI / 2; st.position.set(x, .04, 0); s.add(st);
      [-1, 1].forEach(k => { const l = M(new THREE.SphereGeometry(.16, 8, 8), new THREE.MeshBasicMaterial({ color: x > 60 ? 0xff4040 : 0xffd27a })); l.position.set(x, .15, k * 5); s.add(l); });
    }
    for (let i = 0; i < 18; i++) { const h = 4 + r1() * 12, w = 3 + r1() * 4; const b = M(new THREE.BoxGeometry(w, h, w), std(0x141c28, { roughness: .8 })); b.position.set((r1() - .5) * 160, h / 2, -40 - r1() * 30); s.add(b);
      for (let k = 0; k < 5; k++) { const wn = M(new THREE.PlaneGeometry(.5, .7), new THREE.MeshBasicMaterial({ color: [0xffd27a, 0x9fd3ff][k % 2] })); wn.position.set(b.position.x + (r1() - .5) * (w - 1), 1 + r1() * (h - 2), b.position.z + w / 2 + .02); s.add(wn); } }
    const P = airliner(); s.add(P);
    const ll = new THREE.SpotLight(0xfff4d8, 600, 60, .35, .5, 1); P.add(ll); ll.position.set(6, -1, 0); const lt = new THREE.Object3D(); lt.position.set(30, -6, 0); P.add(lt); ll.target = lt;
    const d = dust(400, [120, 40, 60], 0x9fc4ff, .2, .35); d.position.y = 15; s.add(d);
    return t => {
      const x = -20 + t * 3 + t * t * 1.2; const lift = Math.max(0, t - 2.6);
      P.position.set(x, 2.3 + lift * lift * .55, 0); P.rotation.z = Math.min(.2, lift * .12); P.userData.blink(t);
      key.target.position.copy(P.position);
      d.rotation.y = t * .03;
      cam.position.set(x + lerp(-26, -6, ease(prog(t, 0, 6))), lerp(6, 12, prog(t, 0, 6)) + lift * lift * .3, lerp(44, 40, prog(t, 0, 6)));
      cam.lookAt(x + 1.5, P.position.y + 1.6, 0);
    };
  } });

  // 2) Bulutların üstünde gece uçuşu; kamera kanada yaklaşır, kanat parlar
  shots.push({ t0: 6.0, t1: 9.92, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1a3a6a', '#040a18'], near: 50, far: 170, key: 1400 });
    const moon = M(new THREE.SphereGeometry(4, 32, 24), new THREE.MeshBasicMaterial({ color: 0xf3f0e0, fog: false })); moon.position.set(40, 40, -90); s.add(moon);
    const ml = new THREE.DirectionalLight(0xbcd2ff, 1.4); ml.position.set(40, 40, -60); s.add(ml);
    const cl = clouds(s, 60, [160, 90], -10, 0x5a6c92, .85);
    const P = airliner(); s.add(P);
    const glowM = new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    [-1, 1].forEach(k => { const s2 = new THREE.Shape(); s2.moveTo(2.2, 0); s2.lineTo(-2.4, 8 * k); s2.lineTo(-3.4, 8 * k); s2.lineTo(-2.6, 0); s2.closePath();
      const gm = M(new THREE.ShapeGeometry(s2), glowM); gm.rotation.x = -Math.PI / 2; gm.position.y = -.2; P.add(gm); });
    const st = dust(300, [120, 30, 60], 0xffffff, .14, .5); st.position.y = 5; s.add(st);
    return t => {
      const lt = t - 6;
      P.position.set(0, Math.sin(lt * 1.2) * .25, 0); P.rotation.x = Math.sin(lt * .8) * .04; P.userData.blink(t);
      cl.position.x = -((lt * 14) % 40); st.position.x = -((lt * 20) % 30);
      glowM.opacity = prog(t, 8.4, .4) * (.45 + .2 * Math.sin(t * 8));
      const k = ease(prog(t, 6.0, 3.9));
      cam.position.set(lerp(14, 2, k), lerp(9, 7, k), lerp(46, 26, k)); cam.lookAt(lerp(0, -1.4, k), lerp(0, -.6, k), lerp(0, 4.5, k));
    };
  } });

  // 3) Rüzgâr tüneli: kanat kesiti, hücum açısı, hava aşağı sapar, kaldırma oku
  shots.push({ t0: 9.92, t1: 17.12, fov: 40, build: (s, cam) => {
    const d = tunnel(s);
    const wing = airfoil(9, std(0xd7dde4, { metalness: .7, roughness: .25 })); s.add(wing);
    const rows = [-6.5, -4.8, -3.3, -2.1, -1.1, -.55, .55, 1.1, 2.1, 3.3, 4.8, 6.5];
    const ff = flowField(s, rows, 9, [-3.5, 0, 3.5], () => 0x7ee0ff);
    const up = arrow(0xffcf2e, .4); up.position.set(-.5, 1.2, 0); s.add(up);
    const dn = []; for (let i = 0; i < 3; i++) { const a = arrow(0x7ee0ff, .22); a.rotation.z = Math.PI - .5; a.position.set(6.5 + i * 2, -1.2 - i * .9, 4.6); s.add(a); dn.push(a); }
    return t => {
      const a = lerp(0, .21, ease(prog(t, 10.3, 1.4)));
      wing.rotation.z = -a; ff(t, a, () => 7);
      dn.forEach((ar, i) => ar.userData.set(3 * easeOut(prog(t, 12.4 + i * .15, .5))));
      up.userData.set(7.5 * back(prog(t, 13.84, .7))); up.userData.m.emissiveIntensity = .5 + .3 * Math.sin(t * 6);
      d.rotation.y = t * .03;
      const k = ease(prog(t, 9.92, 7.2));
      cam.position.set(lerp(-6, 4, k), lerp(4, 2.5, k), lerp(40, 42, k)); cam.lookAt(.5, .8, 0);
    };
  } });

  // 4) Basınç farkı: üstte hızlı mavi akış, altta yavaş turuncu akış, alttan itme okları
  shots.push({ t0: 17.12, t1: 23.68, fov: 40, build: (s, cam) => {
    const d = tunnel(s); const a = .14;
    const wing = airfoil(9, std(0xd7dde4, { metalness: .7, roughness: .25 })); wing.rotation.z = -a; s.add(wing);
    const rows = [-6.5, -4.8, -3.3, -2.1, -1.1, -.55, .55, 1.1, 2.1, 3.3, 4.8, 6.5];
    const ff = flowField(s, rows, 9, [-3.5, 0, 3.5], y0 => y0 > 0 ? 0x5fd0ff : 0xff9a3a);
    const lowM = new THREE.MeshBasicMaterial({ color: 0x2f8fff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    const low = M(new THREE.SphereGeometry(1, 32, 16), lowM); low.scale.set(5.5, 1.6, 4.6); low.position.set(-.8, 2.1, 0); s.add(low);
    const hiM = new THREE.MeshBasicMaterial({ color: 0xff5a2a, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    const hi = M(new THREE.SphereGeometry(1, 32, 16), hiM); hi.scale.set(5.5, 1.4, 4.6); hi.position.set(0, -1.6, 0); s.add(hi);
    const pushes = []; [-3, -1, 1, 3].forEach((x, i) => { const ar = arrow(0xffcf2e, .26); ar.position.set(x, -4.6, 1.5); s.add(ar); pushes.push(ar); });
    return t => {
      ff(t, a, y0 => y0 > 0 ? 6 + 6 * Math.exp(-y0 / 2.5) * prog(t, 17.6, 1) : 6 - 2 * prog(t, 17.6, 1));
      lowM.opacity = .35 * prog(t, 19.6, .6) * (.8 + .2 * Math.sin(t * 5));
      hiM.opacity = .35 * prog(t, 20.96, .5) * (.8 + .2 * Math.sin(t * 5 + 1));
      pushes.forEach((ar, i) => { const k = back(prog(t, 21.2 + i * .12, .5)); ar.userData.set(2.6 * k + Math.sin(t * 6 + i) * .15 * k); });
      wing.position.y = prog(t, 21.4, 2) * .5 + Math.sin(t * 3) * .05;
      d.rotation.y = t * .03;
      const k = ease(prog(t, 17.12, 6.5));
      cam.position.set(lerp(5, -4, k), lerp(5, 1, k), lerp(42, 40, k)); cam.lookAt(0, .5, 0);
    };
  } });

  // 5) Dört kuvvet: itki, sürükleme, kaldırma, ağırlık; denge
  shots.push({ t0: 23.68, t1: 31.76, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#173562', '#030812'], near: 50, far: 170, key: 1600 });
    const cl = clouds(s, 70, [180, 100], -16, 0x52638a, .85);
    const st = dust(400, [120, 30, 60], 0xffffff, .14, .5); st.position.y = 2; s.add(st);
    const G = new THREE.Group(); s.add(G);
    const P = airliner(); G.add(P);
    const thrust = arrow(0x22c55e, .38); thrust.rotation.z = -Math.PI / 2; thrust.position.set(6.6, -.2, 0); G.add(thrust);
    const drag = arrow(0xef4444, .34); drag.rotation.z = Math.PI / 2; drag.position.set(-7.2, .3, 0); G.add(drag);
    const lift = arrow(0xffcf2e, .42); lift.position.set(-.6, 1.2, 0); G.add(lift);
    const wt = arrow(0x7ee0ff, .42); wt.rotation.z = Math.PI; wt.position.set(-.6, -1.4, 0); G.add(wt);
    const ring = M(new THREE.TorusGeometry(1, .06, 12, 64), new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: 0 })); ring.position.set(-.6, 0, 0); G.add(ring);
    let cx = 0, last = 23.68;
    return t => {
      const sp = lerp(8, 30, ease(prog(t, 24.2, 3))); cx += (t - last) * sp; last = t;
      cl.position.x = -(cx % 50); st.position.x = -(cx * 1.3 % 30);
      thrust.userData.set(lerp(1.5, 5, back(prog(t, 23.9, .8))) * (t > 23.75 ? 1 : 0));
      drag.userData.set(lerp(0, 3.2, ease(prog(t, 24.6, 1.5))));
      wt.userData.set(5 * easeOut(prog(t, 23.8, .5)));
      const L1 = lerp(1.5, 5, ease(prog(t, 25.6, 2.0))); lift.userData.set(L1 * easeOut(prog(t, 23.8, .5)));
      const eq = prog(t, 27.84, .4) * (1 - prog(t, 31.2, .5)); ring.material.opacity = eq * .8; ring.scale.setScalar(1 + ((t * .8) % 1) * 4); ring.rotation.y = Math.PI / 2;
      [lift, wt].forEach(a => a.userData.m.emissiveIntensity = .5 + eq * .5 * (1 + Math.sin(t * 9)));
      const bob = t < 27.84 ? lerp(-1.2, 0, ease(prog(t, 25.6, 2.2))) : Math.sin(t * 2) * .08;
      G.position.y = bob; P.rotation.z = t < 27.84 ? lerp(0, .08, prog(t, 25.6, 1)) * (1 - prog(t, 27.2, .6)) : 0; P.userData.blink(t);
      const k = ease(prog(t, 23.68, 8.1));
      cam.position.set(lerp(6, -4, k), lerp(9, 6, k), lerp(52, 50, k)); cam.lookAt(0, .3, 0);
    };
  } });

  // 6) Seyir: 11 km yükseklik, 900 km/sa; Dünya'nın eğrisi, yıldızlar
  shots.push({ t0: 31.76, t1: 37.41, fov: 40, build: (s, cam) => {
    s.background = gradTex('#1d4a86', '#01030a'); s.fog = new THREE.Fog(0x0b1a33, 120, 600);
    s.add(new THREE.HemisphereLight(0x9fc4ff, 0x05070c, .9));
    const sun = new THREE.DirectionalLight(0xbcd2ff, 1.6); sun.position.set(-30, 40, 20); s.add(sun);
    const earth = M(new THREE.SphereGeometry(400, 96, 64), std(0x1b3d6a, { roughness: .8 })); earth.position.set(0, -430, -60); s.add(earth);
    const atm = M(new THREE.SphereGeometry(406, 96, 64), new THREE.MeshBasicMaterial({ color: 0x4aa0ff, transparent: true, opacity: .18, side: THREE.BackSide, blending: THREE.AdditiveBlending })); atm.position.copy(earth.position); s.add(atm);
    const cl = clouds(s, 80, [220, 140], -32, 0x6d82ad, .85, 1.4);
    const stars = dust(600, [400, 160, 60], 0xffffff, .5, .8); stars.position.set(0, 70, -150); s.add(stars);
    const P = airliner(); s.add(P);
    const lineM = new THREE.LineDashedMaterial({ color: 0xffcf2e, dashSize: 1, gapSize: .7, transparent: true, opacity: 0 });
    const lg = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -30, 0)]);
    const ln = new THREE.Line(lg, lineM); ln.computeLineDistances(); s.add(ln);
    const trail = dust(200, [50, 1.5, 2], 0xffffff, .25, .5); s.add(trail);
    return t => {
      const lt = t - 31.76;
      P.position.set(lerp(-3, 3, lt / 5.65), 2 + Math.sin(lt) * .2, 0); P.rotation.y = -.1; P.userData.blink(t);
      ln.position.set(P.position.x - .5, P.position.y - 1.2, 0); ln.scale.y = ease(prog(t, 32.3, 1.4)); lineM.opacity = prog(t, 32.3, .3) * .9;
      trail.position.set(P.position.x - 30, P.position.y + .4, 0); trail.material.opacity = .25 + .25 * prog(t, 34.8, .5);
      cl.position.x = -lt * lerp(4, 10, prog(t, 34.8, 1)); stars.rotation.z = lt * .004;
      const k = ease(prog(t, 31.76, 5.65));
      cam.position.set(lerp(-4, 5, k), lerp(5, 8, k), lerp(60, 56, k)); cam.lookAt(P.position.x * .5, 1.2, 0);
    };
  } });

  // 7) Sıradaki soru: fırtınada açık arazi, yalnız ağaç, insan; yıldırım çakar
  shots.push({ t0: 37.41, t1: 99, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1a2133', '#04060b'], fog: 0x080b14, near: 30, far: 120, key: 900, rim: 0x8a7dff, rimI: 500 });
    const gr = M(new THREE.CylinderGeometry(40, 40, 1, 64), std(0x1a2a1c, { roughness: .95 })); gr.position.y = -.5; s.add(gr);
    const cm = new THREE.MeshStandardMaterial({ color: 0x2a3142, roughness: 1, transparent: true, opacity: .95 });
    const sky = new THREE.Group(); s.add(sky);
    for (let i = 0; i < 40; i++) { const c = M(new THREE.SphereGeometry(3 + r1() * 4, 20, 14), cm); c.position.set((r1() - .5) * 70, 22 + r1() * 4, (r1() - .5) * 40 - 8); c.scale.y = .55; sky.add(c); }
    const tree = new THREE.Group(); tree.position.set(-4, 0, -2); s.add(tree);
    const trunk = M(new THREE.CylinderGeometry(.35, .6, 6, 16), std(0x3b2a1e, { roughness: .9 })); trunk.position.y = 3; tree.add(trunk);
    [[0, 7, 0, 2.6], [-1.3, 6.2, .4, 1.9], [1.3, 6.4, -.3, 2]].forEach(([x, y, z, r]) => { const f = M(new THREE.SphereGeometry(r, 24, 16), std(0x1f3d24, { roughness: .9 })); f.position.set(x, y, z); tree.add(f); });
    const man = new THREE.Group(); man.position.set(3, 0, 2); s.add(man);
    const bm = std(0x2f6db5, { roughness: .7 });
    const torso = M(new THREE.CapsuleGeometry(.42, 1.1, 8, 16), bm); torso.position.y = 2.1; man.add(torso);
    const head = M(new THREE.SphereGeometry(.38, 24, 16), std(0xd9b49a, { roughness: .6 })); head.position.y = 3.3; man.add(head);
    [-1, 1].forEach(k => { const lg = M(new THREE.CapsuleGeometry(.17, 1.1, 6, 12), std(0x1f2a36)); lg.position.set(k * .2, .75, 0); man.add(lg); });
    const umb = M(new THREE.SphereGeometry(1.3, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), std(0xb91c1c, { roughness: .5 })); umb.position.y = 4.2; man.add(umb);
    const pole = M(new THREE.CylinderGeometry(.04, .04, 1.6, 8), steel()); pole.position.y = 3.6; man.add(pole);
    // yıldırım: tohumlu zikzak tüp
    const pts = []; let x = 1, y = 24; let sd = 5; const rr = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    while (y > 1) { pts.push(new THREE.Vector3(x, y, 0)); y -= 1.2 + rr() * .8; x += (rr() - .5) * 1.6; } pts.push(new THREE.Vector3(-.3, 0, 0));
    const hitM = new THREE.MeshBasicMaterial({ color: 0xbcd6ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    const hit = M(new THREE.CircleGeometry(3, 48), hitM); hit.rotation.x = -Math.PI / 2; hit.position.set(-.3, .05, 0); s.add(hit);
    const bolt = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0), 120, .14, 8), new THREE.MeshBasicMaterial({ color: 0xeaf2ff }));
    const glow = M(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0), 120, .5, 8), new THREE.MeshBasicMaterial({ color: 0x8fb8ff, transparent: true, opacity: .35, blending: THREE.AdditiveBlending, depthWrite: false }));
    s.add(bolt); s.add(glow);
    const flash = new THREE.PointLight(0xcfe0ff, 0, 80); flash.position.set(0, 6, 3); s.add(flash);
    const rain = dust(900, [50, 30, 30], 0x9fb8e0, .1, .45); s.add(rain);
    const strikes = [38.3, 40.2, 41.9];
    return t => {
      let f = 0; strikes.forEach(st => { const dt = t - st; if (dt >= 0 && dt < .45) f = Math.max(f, (dt < .08 || (dt > .16 && dt < .26) ? 1 : .25) * (1 - dt / .45)); });
      bolt.visible = glow.visible = f > .2; hitM.opacity = f * .8; hit.scale.setScalar(.6 + f * .6); flash.intensity = f * 3500; s.background && (s.backgroundIntensity = 1 + f);
      rain.position.y = 12 - ((t * 18) % 12); rain.position.x = -((t * 3) % 4);
      sky.position.x = Math.sin(t * .2) * 1.5;
      umb.rotation.z = Math.sin(t * 3) * .08;
      const k = ease(prog(t, 37.41, 5.5));
      cam.position.set(lerp(6, -2, k), lerp(8, 7, k), lerp(40, 36, k)); cam.lookAt(-.5, 2.2, 0);
    };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: 3.04, html: T('BİR SORU', 'UÇAKLAR HAVADA NASIL <span class="y">DURUR?</span>', 100) },
    { t0: 3.04, t1: 6.0, html: `<div class="grad"></div><div class="tagw"><span class="tag">A380 · KALKIŞ AĞIRLIĞI</span></div><div class="big" style="top:320px" id="ton"></div>` },
    { t0: 6.0, t1: 8.48, html: T('PEKİ', 'NASIL <span class="y">DURUYOR?</span>') },
    { t0: 8.48, t1: 9.92, html: T('SIR', '<span class="y">KANATLARDA</span>') },
    { t0: 9.92, t1: 13.84, html: T('HÜCUM AÇISI', 'HAVAYI <span class="y">AŞAĞI</span> İTER', 104) },
    { t0: 13.84, t1: 17.12, html: T('TEPKİ', 'KALDIRMA <span class="y">KUVVETİ</span>') },
    { t0: 17.12, t1: 20.96, html: T('ÜST YÜZEY', 'HIZLI HAVA <span class="y">DÜŞÜK BASINÇ</span>', 100) },
    { t0: 20.96, t1: 23.68, html: T('ALT YÜZEY', 'YÜKSEK BASINÇ <span class="y">YUKARI İTER</span>', 100) },
    { t0: 23.68, t1: 27.84, html: T('MOTORLAR', 'HIZ ARTTIKÇA <span class="y">KALDIRMA</span> ARTAR', 92) },
    { t0: 27.84, t1: 31.76, html: T('DENGE', 'KALDIRMA = <span class="y">AĞIRLIK</span>', 104) },
    { t0: 31.76, t1: 37.41, html: `<div class="grad"></div><div class="tagw"><span class="tag">YOLCU UÇAKLARI</span></div><div class="big" style="top:320px" id="alt"></div><div class="sub" style="top:540px" id="spd"></div>` },
    { t0: 37.41, t1: 99, html: T('SIRADAKİ SORU', 'YILDIRIM İNSANA <span class="y">ÇARPARSA?</span>', 100) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const fmt = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return {
    END: 42.84, shots, titles,
    update: (t, q) => {
      if (q('ton')) q('ton').innerHTML = fmt(575 * easeOut(prog(t, 3.3, 1.4))) + '<small style="font-size:90px"> TON</small>';
      if (q('alt')) q('alt').innerHTML = fmt(11 * easeOut(prog(t, 32.4, 1.2))) + '<small style="font-size:90px"> KM</small>';
      if (q('spd')) { const k = prog(t, 34.8, .3); q('spd').style.opacity = k; q('spd').innerHTML = 'SAATTE <span class="y">' + fmt(900 * easeOut(prog(t, 34.8, 1.2))) + ' KM</span>'; }
    },
    follow: { t: 41.04, click: 41.94 },
    sfx: [[2.6, 'whoosh', 1], [3.3, 'pop', .8], [8.48, 'ding', .8], [12.4, 'whoosh', .6], [13.84, 'pop', 1], [20.96, 'pop', .8], [23.9, 'whoosh', .8], [27.84, 'ding', .9], [32.4, 'pop', .8], [34.8, 'pop', .8], [38.3, 'boom', .9], [38.32, 'snap', .8], [40.2, 'snap', .6]],
  };
};
