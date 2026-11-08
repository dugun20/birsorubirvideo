// Bilgi #4: Yıldırım insana çarparsa ne olur? (koyu sinematik tarz, şablon: videos/asansor)
// Kaynaklar: NWS weather.gov/safety/lightning-power (≈300 milyon volt, ≈30.000 amper),
// weather.gov/safety/lightning-temperature (havayı ~50.000 °F, Güneş yüzeyinden 5 kat sıcak),
// NWS Lightning Safety one-pager (kurbanların ~%10'u ölür, ölüm nedeni kalp durması, bina / kapalı metal araç güvenli,
// "When thunder roars, go indoors"), Live Science 2023 (≈%90 hayatta kalır, Lichtenberg figürleri).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const steel = () => std(0xaeb6c0, { metalness: .85, roughness: .3 });
  const dark = () => std(0x2a2f36, { metalness: .6, roughness: .45 });
  const concrete = () => std(0x3a3f47, { roughness: .9 });
  let seed = 41; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  function dust(n, sp, color = 0xcfe8ff, size = .25, op = .5) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
    for (let i = 0; i < n * 3; i += 3) { p[i] = (r1() - .5) * sp[0]; p[i + 1] = (r1() - .5) * sp[1]; p[i + 2] = (r1() - .5) * sp[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color, size, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending }));
  }
  function lights(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#1a2133', '#04060b'])); s.fog = new THREE.Fog(o.fog || 0x080b14, o.near || 40, o.far || 140);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x0a0a12, o.hemi || .9));
    const key = new THREE.SpotLight(0xfff1dc, o.key || 1600, 200, .5, .55, 1.2); key.position.set(-18, 44, 34); s.add(key); s.add(key.target);
    const rim = new THREE.PointLight(o.rim || 0x8a7dff, o.rimI || 600, 90); rim.position.set(20, 16, -14); s.add(rim);
    return key;
  }
  function person(body = 0x2f6db5, sc = 1) {
    const g = new THREE.Group(); const bm = std(body, { roughness: .7 });
    const torso = M(new THREE.CapsuleGeometry(.42, 1.1, 8, 16), bm); torso.position.y = 2.1; g.add(torso);
    const head = M(new THREE.SphereGeometry(.38, 24, 16), std(0xd9b49a, { roughness: .6 })); head.position.y = 3.3; g.add(head);
    const legs = [-1, 1].map(k => { const lg = M(new THREE.CapsuleGeometry(.17, 1.1, 6, 12), std(0x1f2a36)); lg.position.set(k * .2, .75, 0); g.add(lg); return lg; });
    const arms = [-1, 1].map(k => { const a = M(new THREE.CapsuleGeometry(.13, .9, 6, 12), bm); a.position.set(k * .55, 2.2, 0); g.add(a); return a; });
    g.scale.setScalar(sc); g.userData = { torso, head, legs, arms, bm }; return g;
  }
  // tohumlu zikzak yıldırım (tüp + parlama)
  function bolt(s, from, to, sd = 5, steps = 12, wob = 1.6) {
    let k = sd; const rr = () => (k = (k * 16807) % 2147483647) / 2147483647;
    const pts = []; for (let i = 0; i <= steps; i++) { const u = i / steps; const p = from.clone().lerp(to, u);
      if (i && i < steps) { p.x += (rr() - .5) * wob; p.z += (rr() - .5) * wob * .4; } pts.push(p); }
    const cur = new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0);
    const core = M(new THREE.TubeGeometry(cur, 160, .14, 8), new THREE.MeshBasicMaterial({ color: 0xf2f6ff }));
    const glow = M(new THREE.TubeGeometry(cur, 160, .55, 8), new THREE.MeshBasicMaterial({ color: 0x8fb8ff, transparent: true, opacity: .35, blending: THREE.AdditiveBlending, depthWrite: false }));
    const g = new THREE.Group(); g.add(core); g.add(glow);
    // dallar
    for (let b = 0; b < 3; b++) { const i0 = 2 + Math.floor(rr() * (steps - 5)); const p0 = pts[i0]; const bp = [p0.clone()];
      let q = p0.clone(); const dir = rr() > .5 ? 1 : -1; for (let j = 0; j < 3; j++) { q = q.clone(); q.y -= 1 + rr(); q.x += dir * (.6 + rr() * .8); bp.push(q); }
      const bc = new THREE.CatmullRomCurve3(bp, false, 'catmullrom', 0);
      g.add(M(new THREE.TubeGeometry(bc, 40, .07, 6), new THREE.MeshBasicMaterial({ color: 0xdfe9ff })));
      g.add(M(new THREE.TubeGeometry(bc, 40, .3, 6), new THREE.MeshBasicMaterial({ color: 0x8fb8ff, transparent: true, opacity: .25, blending: THREE.AdditiveBlending, depthWrite: false }))); }
    s.add(g); g.visible = false; g.userData.curve = cur; return g;
  }
  const flick = (t, list) => { let f = 0; list.forEach(st => { const dt = t - st; if (dt >= 0 && dt < .5) f = Math.max(f, (dt < .08 || (dt > .16 && dt < .26) ? 1 : .25) * (1 - dt / .5)); }); return f; };
  function stormSky(s, y = 22, n = 40, sp = [80, 40]) {
    const cm = new THREE.MeshStandardMaterial({ color: 0x2a3142, roughness: 1, transparent: true, opacity: .95 });
    const sky = new THREE.Group(); s.add(sky);
    for (let i = 0; i < n; i++) { const c = M(new THREE.SphereGeometry(3 + r1() * 4, 20, 14), cm); c.position.set((r1() - .5) * sp[0], y + r1() * 4, (r1() - .5) * sp[1] - 8); c.scale.y = .55; sky.add(c); }
    return sky;
  }
  function field(s, col = 0x1a2a1c) { const gr = M(new THREE.CylinderGeometry(60, 60, 1, 64), std(col, { roughness: .95 })); gr.position.y = -.5; s.add(gr); return gr; }

  // 1) Fırtına: yıldırım kuledeki paratonere çakar (0–4.72)
  shots.push({ t0: 0, t1: 4.72, fov: 40, build: (s, cam) => {
    lights(s, { near: 40, far: 150 }); field(s, 0x121a20); const sky = stormSky(s, 26, 50, [100, 50]);
    for (let i = 0; i < 16; i++) { const h = 4 + r1() * 10, w = 3 + r1() * 3; const b = M(new THREE.BoxGeometry(w, h, w), std(0x161d29, { roughness: .8 })); b.position.set((r1() - .5) * 70, h / 2, -18 - r1() * 20); s.add(b);
      for (let k = 0; k < 5; k++) { const wn = M(new THREE.PlaneGeometry(.5, .7), new THREE.MeshBasicMaterial({ color: [0xffd27a, 0x9fd3ff][k % 2] })); wn.position.set(b.position.x + (r1() - .5) * (w - 1), 1 + r1() * (h - 2), b.position.z + w / 2 + .02); s.add(wn); } }
    const tower = new THREE.Group(); s.add(tower);
    for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + Math.PI / 4; const leg = M(new THREE.CylinderGeometry(.12, .2, 14, 8), steel()); leg.position.set(Math.cos(a) * 1.1, 7, Math.sin(a) * 1.1); leg.rotation.set(Math.sin(a) * .08, 0, -Math.cos(a) * .08); tower.add(leg); }
    for (let y = 2; y < 14; y += 2.2) { const ring = M(new THREE.TorusGeometry(1.4 - y * .05, .07, 6, 4), steel()); ring.rotation.x = Math.PI / 2; ring.rotation.z = Math.PI / 4; ring.position.y = y; tower.add(ring); }
    const rod = M(new THREE.CylinderGeometry(.06, .06, 3, 8), steel()); rod.position.y = 15.2; tower.add(rod);
    const tip = M(new THREE.SphereGeometry(.22, 16, 12), new THREE.MeshBasicMaterial({ color: 0xfff2c0 })); tip.position.y = 16.7; tower.add(tip);
    const B = bolt(s, new THREE.Vector3(3, 32, -2), new THREE.Vector3(0, 16.7, 0), 9, 12, 2.2);
    const flash = new THREE.PointLight(0xcfe0ff, 0, 90); flash.position.set(1, 20, 6); s.add(flash);
    const rain = dust(1200, [70, 34, 40], 0x9fb8e0, .1, .45); s.add(rain);
    const sparks = dust(80, [3, 3, 3], 0xffe7a0, .25, 0); sparks.position.y = 16.7; s.add(sparks);
    const strikes = [.6, 2.75];
    return t => {
      const f = flick(t, strikes); B.visible = f > .2; flash.intensity = f * 4000; tip.scale.setScalar(1 + f * 2);
      sparks.material.opacity = f; sparks.rotation.y = t * 3; sparks.scale.setScalar(1 + f);
      rain.position.y = 14 - ((t * 18) % 12); sky.position.x = Math.sin(t * .2) * 2;
      const k = ease(prog(t, 0, 4.72));
      cam.position.set(lerp(-8, 6, k), lerp(9, 11, k), lerp(52, 48, k)); cam.lookAt(0, 13.5, 0);
    };
  } });

  // 2) Açık arazide insan; öncü kanal yavaşça iner (4.72–7.12)
  shots.push({ t0: 4.72, t1: 7.12, fov: 40, build: (s, cam) => {
    lights(s, { key: 900 }); field(s); const sky = stormSky(s, 20);
    const man = person(0x2f6db5, 1.2); s.add(man);
    const B = bolt(s, new THREE.Vector3(-2, 17, -1), new THREE.Vector3(0, 4.6, 0), 13, 10, 2.2);
    const core = B.children[0], glow = B.children[1];
    const rain = dust(900, [50, 30, 30], 0x9fb8e0, .1, .45); s.add(rain);
    const halo = M(new THREE.SphereGeometry(1, 24, 16), new THREE.MeshBasicMaterial({ color: 0x7ee0ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); halo.position.y = 4.4; s.add(halo);
    return t => {
      const k = prog(t, 4.8, 2.0); B.visible = true; B.children.forEach((c, i) => { if (i < 2) c.geometry.setDrawRange(0, Math.floor(c.geometry.index.count * k * .92)); else c.visible = false; });
      glow.material.opacity = .25 + .15 * Math.sin(t * 40);
      halo.material.opacity = .25 * k * (.6 + .4 * Math.sin(t * 30)); halo.scale.setScalar(1 + k * .6);
      man.userData.head.rotation.x = -.4 * ease(prog(t, 5.2, .6));
      rain.position.y = 12 - ((t * 18) % 12); sky.position.x = Math.sin(t * .2) * 1.5;
      const kk = ease(prog(t, 4.72, 2.4));
      cam.position.set(lerp(4, 1, kk), lerp(4.5, 5, kk), lerp(30, 25, kk)); cam.lookAt(0, 3.6, 0);
    };
  } });

  // 3) Sıcaklık: Güneş yüzeyi ile yıldırım kanalı, termometre çubukları (7.12–11.12)
  shots.push({ t0: 7.12, t1: 11.12, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#2a1608', '#05030a'], fog: 0x0a0604, rim: 0xff7a1a });
    const sunM = std(0xff8a1a, { emissive: 0xff6a00, emissiveIntensity: 1.1, roughness: .8 });
    const sun = M(new THREE.SphereGeometry(2.1, 64, 48), sunM); sun.position.set(-4.5, 8.4, 0); s.add(sun);
    const sg = M(new THREE.SphereGeometry(2.8, 32, 24), new THREE.MeshBasicMaterial({ color: 0xffa040, transparent: true, opacity: .25, blending: THREE.AdditiveBlending, depthWrite: false })); sg.position.copy(sun.position); s.add(sg);
    const B = bolt(s, new THREE.Vector3(4.5, 11.8, 0), new THREE.Vector3(4.5, 5.4, 0), 21, 7, 1.2); B.visible = true;
    const base = M(rb(16, .5, 5, .1), dark()); base.position.set(0, -.4, 0); s.add(base);
    const bars = [[-4.5, 0xff8a1a, .9], [4.5, 0xbcd6ff, 4.5]].map(([x, c, h]) => {
      const tube = M(new THREE.CylinderGeometry(.75, .75, 1, 32, 1, true), new THREE.MeshStandardMaterial({ color: 0x9fd3ff, transparent: true, opacity: .18, roughness: .1, side: THREE.DoubleSide })); tube.scale.y = 4.6; tube.position.set(x, 2.3 + .1, 0); s.add(tube);
      const fill = M(new THREE.CylinderGeometry(.55, .55, 1, 32), std(c, { emissive: c, emissiveIntensity: .7 })); fill.position.set(x, 0, 0); s.add(fill);
      return { fill, h };
    });
    const pl = new THREE.PointLight(0xbcd6ff, 300, 30); pl.position.set(4.5, 8, 3); s.add(pl);
    const d = dust(300, [30, 20, 14], 0xffc080, .15, .4); d.position.y = 6; s.add(d);
    return t => {
      bars.forEach((b, i) => { const k = (i ? ease(prog(t, 8.8, 1.8)) : easeOut(prog(t, 7.6, .8))); const hh = Math.max(.01, b.h * k * .95); b.fill.scale.y = hh; b.fill.position.y = hh / 2 + .1; });
      sun.rotation.y = t * .3; sunM.emissiveIntensity = 1 + .15 * Math.sin(t * 4); sg.scale.setScalar(1 + .04 * Math.sin(t * 3));
      const f = .6 + .4 * Math.abs(Math.sin(t * 23)) ; B.children[1].material.opacity = .25 * f + .1; pl.intensity = 200 + 200 * f;
      d.rotation.y = t * .04;
      const k = ease(prog(t, 7.12, 4));
      cam.position.set(lerp(-3, 3, k), 7, lerp(39, 37, k)); cam.lookAt(0, 6.6, 0);
    };
  } });

  // 4) Akım vücuttan geçer: cam insan, baştan ayağa ışık akışı (11.12–14.24)
  shots.push({ t0: 11.12, t1: 14.24, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#0c1f3c', '#02050c'], fog: 0x050d1c });
    const glass = new THREE.MeshStandardMaterial({ color: 0x7ec8ff, transparent: true, opacity: .28, roughness: .1, metalness: .2, depthWrite: false });
    const G = new THREE.Group(); s.add(G); G.scale.setScalar(2.6);
    const torso = M(new THREE.CapsuleGeometry(.42, 1.1, 12, 24), glass); torso.position.y = 2.1; G.add(torso);
    const head = M(new THREE.SphereGeometry(.38, 32, 24), glass); head.position.y = 3.3; G.add(head);
    [-1, 1].forEach(k => { const lg = M(new THREE.CapsuleGeometry(.17, 1.1, 8, 16), glass); lg.position.set(k * .2, .75, 0); G.add(lg);
      const a = M(new THREE.CapsuleGeometry(.13, .9, 8, 16), glass); a.position.set(k * .55, 2.2, 0); G.add(a); });
    const heart = M(new THREE.SphereGeometry(.13, 20, 16), std(0xd62828, { emissive: 0x550000 })); heart.position.set(.1, 2.4, .1); G.add(heart);
    const paths = [-1, 1].map(k => new THREE.CatmullRomCurve3([[0, 3.55], [0, 3.0], [.05 * k, 2.4], [.1 * k, 1.6], [.2 * k, 1.2], [.2 * k, .3], [.2 * k, .05]].map(([x, y]) => new THREE.Vector3(x, y, .05))));
    const N = 160; const g = new THREE.BufferGeometry(); const p = new Float32Array(N * 3); g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    const pm = new THREE.PointsMaterial({ color: 0xbfe6ff, size: .22, transparent: true, opacity: 1, depthWrite: false, blending: THREE.AdditiveBlending }); const pts = new THREE.Points(g, pm); G.add(pts);
    const B = bolt(s, new THREE.Vector3(1, 24, 0), new THREE.Vector3(0, 9.3, 0), 31, 8, 1.6);
    const ground = M(new THREE.CircleGeometry(1.4, 48), new THREE.MeshBasicMaterial({ color: 0x7ee0ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending })); ground.rotation.x = -Math.PI / 2; ground.position.y = .02; s.add(ground);
    const grid = new THREE.GridHelper(60, 30, 0x1d4a6e, 0x10263d); s.add(grid);
    const ph = []; for (let i = 0; i < N; i++) ph.push(r1());
    return t => {
      const strike = [11.5, 12.9]; const f = flick(t, strike); B.visible = f > .2;
      let flow = 0; strike.forEach(st => { flow = Math.max(flow, prog(t, st, .02) * (1 - prog(t, st + .35, .3))); });
      for (let i = 0; i < N; i++) { const u = ((ph[i] + (t - 11.12) * 2.2) % 1); const v = paths[i % 2].getPoint(u); p[i * 3] = v.x + (hash(i, t * 9, 1) * .05); p[i * 3 + 1] = v.y; p[i * 3 + 2] = v.z; }
      g.attributes.position.needsUpdate = true; pm.opacity = .15 + flow; pm.size = .14 + flow * .14;
      glass.emissive = new THREE.Color(0x3f8fff).multiplyScalar(flow * .6);
      ground.material.opacity = flow * .7; ground.scale.setScalar(1 + flow);
      heart.scale.setScalar(1 + .25 * Math.max(0, Math.sin(t * 7)));
      const k = ease(prog(t, 11.12, 3.1));
      cam.position.set(lerp(-5, 4, k), 7, lerp(30, 28, k)); cam.lookAt(0, 5.8, 0);
    };
  } });

  // 5) Kalp: atıyor, sonra duruyor; EKG düzleşir (14.24–17.52)
  shots.push({ t0: 14.24, t1: 17.52, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#2a0b12', '#05020a'], fog: 0x0a0306, rim: 0xff3b5c });
    const H = new THREE.Group(); H.position.set(0, 7, 0); s.add(H);
    const hm = std(0xc8102e, { roughness: .35, metalness: .1, emissive: 0x300008 });
    const hs = new THREE.Shape(); hs.moveTo(0, -2.6);
    hs.bezierCurveTo(-1.2, -1.5, -3.2, -.4, -3.0, 1.2); hs.bezierCurveTo(-2.8, 2.6, -1.0, 3.0, 0, 1.6);
    hs.bezierCurveTo(1.0, 3.0, 2.8, 2.6, 3.0, 1.2); hs.bezierCurveTo(3.2, -.4, 1.2, -1.5, 0, -2.6);
    const hg = new THREE.ExtrudeGeometry(hs, { depth: .8, bevelEnabled: true, bevelThickness: .9, bevelSize: .7, bevelSegments: 10, curveSegments: 40 }); hg.center();
    H.add(M(hg, hm));
    const aorta = M(new THREE.TorusGeometry(.9, .32, 16, 32, Math.PI), std(0x9e1a2a, { roughness: .5 })); aorta.position.set(.3, 2.4, -.3); 
    const ecgN = 240; const eg = new THREE.BufferGeometry(); const ep = new Float32Array(ecgN * 3); eg.setAttribute('position', new THREE.BufferAttribute(ep, 3));
    const em = new THREE.LineBasicMaterial({ color: 0x22ff88 }); const ecg = new THREE.Line(eg, em); ecg.position.set(0, 1.4, 1); s.add(ecg);
    const scr = M(rb(15, 3.2, .3, .2), std(0x05110c, { roughness: .4, metalness: .3 })); scr.position.set(0, 1.4, .7); s.add(scr);
    const beatF = x => { const u = ((x % 1) + 1) % 1; return u < .05 ? Math.sin(u / .05 * Math.PI) * .25 : u > .1 && u < .13 ? -(u - .1) / .03 * .5 : u >= .13 && u < .16 ? lerp(-.5, 2.2, (u - .13) / .03) : u >= .16 && u < .2 ? lerp(2.2, -.7, (u - .16) / .04) : u >= .2 && u < .23 ? lerp(-.7, 0, (u - .2) / .03) : u > .35 && u < .5 ? Math.sin((u - .35) / .15 * Math.PI) * .45 : 0; };
    const stopT = 16.4;
    const d = dust(250, [30, 20, 14], 0xff8aa0, .14, .35); d.position.y = 7; s.add(d);
    return t => {
      for (let i = 0; i < ecgN; i++) { const x = -7 + 14 * i / ecgN; const tt = t - (7 - x) / 6; ep[i * 3] = x; ep[i * 3 + 1] = tt < stopT ? beatF(tt * 1.4) * .55 : 0; ep[i * 3 + 2] = 0; }
      eg.attributes.position.needsUpdate = true; em.color.setHex(t > stopT + 1 ? 0xff3b3b : 0x22ff88);
      const ph = (t * 1.4) % 1; const beat = t < stopT ? Math.exp(-ph * 9) * .12 : 0;
      H.scale.setScalar(.85 * (1 + beat)); hm.emissive.setHex(t > stopT ? 0x0a0002 : 0x300008);
      H.rotation.y = Math.sin(t * .6) * .25;
      d.rotation.y = t * .04;
      const k = ease(prog(t, 14.24, 3.3));
      cam.position.set(lerp(-3, 3, k), 6, lerp(30, 27, k)); cam.lookAt(0, 4.9, 0);
    };
  } });

  // 6) 10 kişiden 9'u hayatta kalır (17.52–23.04)
  shots.push({ t0: 17.52, t1: 23.04, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#0f2a3a', '#02060c'] });
    const fl = M(new THREE.CylinderGeometry(16, 16, .6, 64), concrete()); fl.position.y = -.3; s.add(fl);
    const P = []; for (let i = 0; i < 10; i++) { const r = Math.floor(i / 5), c = i % 5; const p = person(0x5d6b7c, 1.05); p.position.set((c - 2) * 2.3 + (r ? 1.15 : 0), 0, r ? -2.6 : 1.4); s.add(p); P.push(p);
      const ring = M(new THREE.TorusGeometry(.75, .06, 8, 40), new THREE.MeshBasicMaterial({ color: 0x22c55e, transparent: true, opacity: 0 })); ring.rotation.x = Math.PI / 2; ring.position.set(p.position.x, .05, p.position.z); s.add(ring); p.userData.ring = ring; }
    const order = [0, 6, 3, 9, 1, 7, 4, 5, 8]; const lost = 2;
    const d = dust(300, [36, 18, 20], 0xbfe6ff, .14, .35); d.position.y = 6; s.add(d);
    return t => {
      order.forEach((i, j) => { const k = prog(t, 20.6 + j * .12, .3); const p = P[i]; p.userData.bm.color.setHex(k > .5 ? 0x22c55e : 0x5d6b7c); p.userData.bm.emissive = new THREE.Color(0x0b5a2a).multiplyScalar(k);
        p.userData.ring.material.opacity = k * .9; p.position.y = Math.abs(Math.sin((t - 20.6) * 5 + j)) * .25 * k; });
      const lk = prog(t, 21.9, .5); const L2 = P[lost]; L2.userData.bm.color.setHex(lk > .5 ? 0x7a1d1d : 0x5d6b7c); L2.userData.bm.transparent = true; L2.userData.bm.opacity = 1 - lk * .5;
      L2.userData.ring.material.color.setHex(0xef4444); L2.userData.ring.material.opacity = lk * .9;
      d.rotation.y = t * .03;
      const k = ease(prog(t, 17.52, 5.5));
      cam.position.set(lerp(-6, 5, k), lerp(9, 8, k), lerp(28, 26, k)); cam.lookAt(0, 1.0, 0);
    };
  } });

  // 7) Lichtenberg figürü: deride eğrelti otu deseni büyür (23.04–26.48)
  shots.push({ t0: 23.04, t1: 26.48, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1e1420', '#05030a'], fog: 0x0a060c, rim: 0xff9a6a, key: 1800 });
    const skin = M(new THREE.CapsuleGeometry(4, 10, 16, 64), std(0xd9a888, { roughness: .55 })); skin.rotation.z = Math.PI / 2; skin.position.set(0, 6.4, -4); s.add(skin);
    const sz = y => -4 + Math.sqrt(Math.max(0, 16 - (y - 6.4) ** 2)) + .06;
    const segs = []; let sd = 77; const rr = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    function grow(x, y, a, len, w, depth, ord) {
      if (depth > 6 || len < .25) return;
      const n = 3; let cx = x, cy = y, ca = a;
      for (let i = 0; i < n; i++) { const nx = cx + Math.cos(ca) * len / n, ny = cy + Math.sin(ca) * len / n; segs.push({ a: [cx, cy], b: [nx, ny], w, ord: ord + i * .3 });
        if (rr() < .75) grow(nx, ny, ca + (rr() > .5 ? 1 : -1) * (.5 + rr() * .5), len * .55, w * .65, depth + 1, ord + i * .3 + .3);
        cx = nx; cy = ny; ca += (rr() - .5) * .4; }
    }
    grow(-5.5, 8.4, -.3, 5, .14, 0, 0); grow(-5.5, 8.4, -.9, 4, .12, 0, .2); grow(-5.5, 8.4, .25, 3.2, .1, 0, .3);
    const fm = std(0x9a2a3a, { roughness: .6, emissive: 0x3a0008 });
    for (let i = segs.length - 1; i >= 0; i--) if (Math.abs(segs[i].a[1] - 6.4) > 3.4 || Math.abs(segs[i].b[1] - 6.4) > 3.4) segs.splice(i, 1);
    const maxO = Math.max(...segs.map(q => q.ord));
    const meshes = segs.map(q => { const a = new THREE.Vector3(q.a[0], q.a[1], sz(q.a[1])), b = new THREE.Vector3(q.b[0], q.b[1], sz(q.b[1])); const len = a.distanceTo(b);
      const m = M(new THREE.CapsuleGeometry(q.w, len, 4, 8), fm); m.position.copy(a).lerp(b, .5); m.position.z += .04; m.rotation.x = -Math.atan2(b.z - a.z, Math.hypot(b.x - a.x, b.y - a.y)) * 0; m.rotation.z = Math.atan2(b.y - a.y, b.x - a.x) - Math.PI / 2; m.userData.o = q.ord / maxO; s.add(m); return m; });
    const glow = new THREE.PointLight(0xff6a6a, 0, 20); glow.position.set(-2, 7, 4); s.add(glow);
    const d = dust(200, [24, 16, 10], 0xffd0c0, .12, .3); d.position.y = 7; s.add(d);
    return t => {
      const k = ease(prog(t, 23.3, 2.4)); meshes.forEach(m => { const v = clamp((k - m.userData.o) * 6); m.visible = v > 0; m.scale.set(1, Math.max(.01, v), 1); });
      fm.emissive.setHex(0x3a0008).multiplyScalar(1 + Math.sin(t * 4) * .3); glow.intensity = 120 * k;
      d.rotation.y = t * .03;
      const kk = ease(prog(t, 23.04, 3.4));
      cam.position.set(lerp(-6, 4, kk), lerp(8, 7, kk), lerp(30, 28, kk)); cam.lookAt(0, 6.4, 0);
    };
  } });

  // 8) Güvenli yer: metal tavanlı araç; yıldırım kabuktan geçip yere akar (26.48–31.36)
  shots.push({ t0: 26.48, t1: 31.36, fov: 40, build: (s, cam) => {
    lights(s, { key: 1100 }); const gr = M(new THREE.PlaneGeometry(200, 200), std(0x15191f, { roughness: .35, metalness: .4 })); gr.rotation.x = -Math.PI / 2; s.add(gr);
    const sky = stormSky(s, 22);
    const house = new THREE.Group(); house.position.set(-9, 0, -8); s.add(house);
    const hb = M(rb(7, 5, 6, .1), std(0x4a4f58, { roughness: .9 })); hb.position.y = 2.5; house.add(hb);
    const roof = M(new THREE.ConeGeometry(5.6, 3, 4), std(0x6b2a22, { roughness: .8 })); roof.rotation.y = Math.PI / 4; roof.position.y = 6.5; house.add(roof);
    [[-1.8, 2.6], [1.8, 2.6]].forEach(([x, y]) => { const w = M(new THREE.PlaneGeometry(1.4, 1.2), new THREE.MeshBasicMaterial({ color: 0xffd27a })); w.position.set(x, y, 3.02); house.add(w); });
    const car = new THREE.Group(); car.position.set(1.5, 0, 0); s.add(car);
    const paint = std(0x8a1c1c, { metalness: .7, roughness: .3 });
    const body = M(rb(7.2, 1.5, 3.2, .45), paint); body.position.y = 1.35; car.add(body);
    const cab = M(rb(4, 1.4, 2.9, .5), paint); cab.position.set(-.4, 2.6, 0); car.add(cab);
    const glassM = new THREE.MeshStandardMaterial({ color: 0x0d1828, metalness: .9, roughness: .1 });
    [-1, 1].forEach(k => { const w = M(new THREE.PlaneGeometry(3.4, .95), glassM); w.position.set(-.4, 2.65, k * 1.46); if (k < 0) w.rotation.y = Math.PI; car.add(w); });
    const ws = M(new THREE.PlaneGeometry(2.6, 1), glassM); ws.position.set(1.62, 2.6, 0); ws.rotation.y = Math.PI / 2; ws.rotation.x = 0; car.add(ws);
    const driver = M(new THREE.SphereGeometry(.35, 20, 14), std(0xd9b49a)); driver.position.set(.3, 2.55, .6); car.add(driver);
    [[-2.3, 1.6], [2.3, 1.6], [-2.3, -1.6], [2.3, -1.6]].forEach(([x, z]) => { const w = M(new THREE.CylinderGeometry(.7, .7, .5, 24), std(0x111111, { roughness: .8 })); w.rotation.x = Math.PI / 2; w.position.set(x, .7, z); car.add(w); });
    [-1, 1].forEach(k => { const hl = M(new THREE.SphereGeometry(.22, 12, 10), new THREE.MeshBasicMaterial({ color: 0xfff2c0 })); hl.position.set(3.6, 1.5, k * 1.1); car.add(hl); });
    const shellM = new THREE.MeshBasicMaterial({ color: 0x9fd3ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, wireframe: true });
    const shell = M(rb(4.2, 1.6, 3.1, .5), shellM); shell.position.set(-.4, 2.6, 0); car.add(shell);
    const shell2 = M(rb(7.4, 1.7, 3.4, .45), shellM); shell2.position.y = 1.35; car.add(shell2);
    const B = bolt(s, new THREE.Vector3(-1, 30, -1), new THREE.Vector3(1.1, 3.35, 0), 51, 12, 2.2);
    const pool = M(new THREE.RingGeometry(1, 1.3, 48), new THREE.MeshBasicMaterial({ color: 0x9fd3ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, side: THREE.DoubleSide })); pool.rotation.x = -Math.PI / 2; pool.position.set(1.5, .03, 0); s.add(pool);
    const flash = new THREE.PointLight(0xcfe0ff, 0, 60); flash.position.set(1, 8, 5); s.add(flash);
    const rain = dust(1000, [50, 30, 30], 0x9fb8e0, .1, .45); s.add(rain);
    const strikes = [27.3, 29.6];
    return t => {
      const f = flick(t, strikes); B.visible = f > .2; flash.intensity = f * 3500;
      let w = 0; strikes.forEach(st => { w = Math.max(w, prog(t, st, .05) * (1 - prog(t, st + .2, .6))); });
      shellM.opacity = w * .7; const pk = ((t - 27.3) % 2.3) / .8; pool.material.opacity = w * .8; pool.scale.setScalar(1 + clamp(pk) * 4);
      rain.position.y = 12 - ((t * 18) % 12); sky.position.x = Math.sin(t * .2) * 1.5;
      const k = ease(prog(t, 26.48, 4.9));
      cam.position.set(lerp(12, 6, k), lerp(9, 8, k), lerp(26, 25, k)); cam.lookAt(0, 3.4, -1);
    };
  } });

  // 9) Gök gürlerse içeri gir: kişi koşarak eve girer, kapı kapanır (31.36–33.52)
  shots.push({ t0: 31.36, t1: 33.52, fov: 40, build: (s, cam) => {
    lights(s, { key: 1100 }); field(s); const sky = stormSky(s, 20);
    const house = new THREE.Group(); s.add(house);
    const hb = M(rb(10, 6, 7, .1), std(0x4a4f58, { roughness: .9 })); hb.position.y = 3; house.add(hb);
    const roof = M(new THREE.ConeGeometry(7.8, 3.6, 4), std(0x6b2a22, { roughness: .8 })); roof.rotation.y = Math.PI / 4; roof.position.y = 7.8; roof.scale.z = .75; house.add(roof);
    const doorLight = M(new THREE.PlaneGeometry(1.8, 3.2), new THREE.MeshBasicMaterial({ color: 0xffd27a })); doorLight.position.set(0, 1.6, 3.52); house.add(doorLight);
    const door = new THREE.Group(); door.position.set(-.9, 0, 3.55); house.add(door);
    const dm = M(rb(1.8, 3.2, .15, .05), std(0x5a3a22, { roughness: .7 })); dm.position.set(.9, 1.6, 0); door.add(dm);
    [[-3.2, 3.2], [3.2, 3.2]].forEach(([x, y]) => { const w = M(new THREE.PlaneGeometry(1.6, 1.4), new THREE.MeshBasicMaterial({ color: 0xffd27a })); w.position.set(x, y, 3.52); house.add(w); });
    const pl = new THREE.PointLight(0xffc98a, 200, 12); pl.position.set(0, 2, 5); s.add(pl);
    const man = person(0x2f6db5, 1); s.add(man);
    const B = bolt(s, new THREE.Vector3(10, 30, -10), new THREE.Vector3(14, 0, -14), 61, 12, 3);
    const flash = new THREE.PointLight(0xcfe0ff, 0, 90); flash.position.set(8, 14, 2); s.add(flash);
    const rain = dust(900, [50, 30, 30], 0x9fb8e0, .1, .45); s.add(rain);
    return t => {
      const f = flick(t, [31.5]); B.visible = f > .2; flash.intensity = f * 3500;
      const k = ease(prog(t, 31.5, 1.3)); man.position.set(lerp(7, 0, k), Math.abs(Math.sin(t * 14)) * .2 * (k < 1 ? 1 : 0), lerp(7, 3.2, k)); man.rotation.y = lerp(-1.0, Math.PI, prog(t, 32.6, .2)) * 0 + Math.atan2(-7, -3.8);
      man.userData.legs.forEach((l, i) => l.rotation.x = Math.sin(t * 14 + i * Math.PI) * .6 * (k < 1 ? 1 : 0));
      man.visible = k < .98; door.rotation.y = -1.7 * (1 - ease(prog(t, 32.85, .45)));
      rain.position.y = 12 - ((t * 18) % 12); sky.position.x = Math.sin(t * .2) * 1.5;
      const kk = ease(prog(t, 31.36, 2.2));
      cam.position.set(lerp(9, 6, kk), lerp(7, 6.5, kk), lerp(28, 25, kk)); cam.lookAt(0, 3.7, 0);
    };
  } });

  // 10) Sıradaki soru: dönen Dünya yavaşlar (33.52–END)
  shots.push({ t0: 33.52, t1: 99, fov: 40, build: (s, cam) => {
    s.background = gradTex('#0b1a3a', '#01030a'); s.fog = new THREE.Fog(0x01030a, 200, 600);
    s.add(new THREE.HemisphereLight(0x9fc4ff, 0x05070c, .4));
    const sun = new THREE.DirectionalLight(0xfff1dc, 3); sun.position.set(-30, 15, 20); s.add(sun);
    const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 512; const x = cv.getContext('2d');
    const og = x.createLinearGradient(0, 0, 0, 512); og.addColorStop(0, '#16406e'); og.addColorStop(.5, '#1d5a96'); og.addColorStop(1, '#16406e'); x.fillStyle = og; x.fillRect(0, 0, 1024, 512);
    let sd = 99; const rr = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    for (let c = 0; c < 9; c++) { const cx = rr() * 1024, cy = 110 + rr() * 290; for (let i = 0; i < 40; i++) { x.fillStyle = ['#3f7a3a', '#5b8a3c', '#8a7a4a', '#4a6e34'][i % 4]; x.beginPath(); x.ellipse(cx + (rr() - .5) * 160, cy + (rr() - .5) * 90, 20 + rr() * 40, 12 + rr() * 26, rr() * 3, 0, Math.PI * 2); x.fill(); } }
    x.fillStyle = '#e8eef5'; x.fillRect(0, 0, 1024, 28); x.fillRect(0, 484, 1024, 28);
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    const E = new THREE.Group(); E.position.set(0, 8.6, 0); E.rotation.z = .41; s.add(E);
    const earth = M(new THREE.SphereGeometry(4, 96, 64), new THREE.MeshStandardMaterial({ map: tex, roughness: .8 })); E.add(earth);
    const cl = M(new THREE.SphereGeometry(4.1, 64, 48), new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: .12, roughness: 1 })); E.add(cl);
    const atm = M(new THREE.SphereGeometry(4.5, 64, 48), new THREE.MeshBasicMaterial({ color: 0x4aa0ff, transparent: true, opacity: .2, side: THREE.BackSide, blending: THREE.AdditiveBlending })); E.add(atm);
    const axis = M(new THREE.CylinderGeometry(.05, .05, 11, 8), new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: .7 })); E.add(axis);
    const stars = dust(800, [200, 120, 40], 0xffffff, .35, .8); stars.position.set(0, 8, -60); s.add(stars);
    let ang = 0, last = 33.52;
    return t => {
      const w = lerp(1.6, 0, ease(prog(t, 35.6, 2.2))); ang += (t - last) * w; last = t; earth.rotation.y = ang; cl.rotation.y = ang * 1.2;
      stars.rotation.z = t * .005;
      const k = ease(prog(t, 33.52, 5));
      cam.position.set(lerp(-3, 3, k), lerp(9, 8.5, k), lerp(34, 32, k)); cam.lookAt(0, 7.6, 0);
    };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: 2.72, html: `<div class="grad"></div><div class="tagw"><span class="tag">TEK BİR YILDIRIM</span></div><div class="big" style="top:320px;font-size:170px" id="v1"></div><div class="sub" style="top:520px">VOLT</div>` },
    { t0: 2.72, t1: 4.72, html: `<div class="grad"></div><div class="tagw"><span class="tag">TEK BİR YILDIRIM</span></div><div class="big" style="top:320px;font-size:170px" id="v2"></div><div class="sub" style="top:520px">AMPER</div>` },
    { t0: 4.72, t1: 7.12, html: T('BİR SORU', 'İNSANA <span class="y">ÇARPARSA?</span>') },
    { t0: 7.12, t1: 11.12, html: T('SICAKLIK', 'GÜNEŞ YÜZEYİNDEN <span class="y">5 KAT</span> SICAK', 96) },
    { t0: 11.12, t1: 14.24, html: T('AKIM', 'SANİYEDEN <span class="y">KISA</span> SÜREDE GEÇER', 96) },
    { t0: 14.24, t1: 17.52, html: T('EN BÜYÜK TEHLİKE', '<span class="y">KALP</span> DURABİLİR') },
    { t0: 17.52, t1: 23.04, html: T('ŞAŞIRTICI GERÇEK', '10 KİŞİDEN <span class="y">9\'U</span> YAŞAR') },
    { t0: 23.04, t1: 26.48, html: T('LICHTENBERG İZLERİ', 'EĞRELTİ OTU <span class="y">DESENİ</span>', 104) },
    { t0: 26.48, t1: 31.36, html: T('EN GÜVENLİ YER', 'BİNA YA DA <span class="y">KAPALI ARAÇ</span>', 100) },
    { t0: 31.36, t1: 33.52, html: T('KURAL', 'GÖK GÜRLERSE <span class="y">İÇERİ GİR</span>', 100) },
    { t0: 33.52, t1: 99, html: T('SIRADAKİ SORU', 'DÜNYA DÖNMEYİ <span class="y">DURDURSA?</span>', 100) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const fmt = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return {
    END: 38.6, shots, titles,
    update: (t, q) => {
      if (q('v1')) q('v1').innerHTML = fmt(300 * easeOut(prog(t, .2, 1.3))) + '<small style="font-size:80px"> MİLYON</small>';
      if (q('v2')) q('v2').innerHTML = fmt(30000 * easeOut(prog(t, 2.8, 1.2)));
    },
    follow: { t: 36.72, click: 37.7 },
    sfx: [[.6, 'boom', 1], [.62, 'snap', 1], [2.75, 'snap', .8], [2.78, 'boom', .6], [6.6, 'whoosh', .6], [11.5, 'snap', 1], [12.9, 'snap', .7], [14.6, 'pop_low', .7], [15.3, 'pop_low', .7], [16.0, 'pop_low', .7], [20.6, 'pop', .8], [21.9, 'pop_low', .9], [23.3, 'crunch', .5], [27.3, 'boom', 1], [27.32, 'snap', 1], [29.6, 'snap', .7], [31.5, 'boom', .8], [33.3, 'click', .6]],
  };
};
