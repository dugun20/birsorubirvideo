// Bilgi #2: Asansörün halatı koparsa ne olur? (koyu sinematik tarz — ŞABLON)
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  const steel = () => std(0xaeb6c0, { metalness: .85, roughness: .3 });
  const dark = () => std(0x2a2f36, { metalness: .6, roughness: .45 });
  const concrete = () => std(0x3a3f47, { roughness: .9 });
  let seed = 11; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  function dust(n, sp, color = 0xcfe8ff, size = .25, op = .5) { // deterministik partikül (parçalı render için)
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
  function person(body, hat) {
    const g = new THREE.Group();
    g.add(M(new THREE.CapsuleGeometry(.3, .5, 8, 16), std(body, { roughness: .7 })));
    const head = M(new THREE.SphereGeometry(.27, 24, 16), std(0xd9b49a, { roughness: .6 })); head.position.y = .75; g.add(head);
    if (hat) { const h = M(new THREE.CylinderGeometry(.22, .22, .45, 20), std(0x111111)); h.position.y = 1.18; g.add(h);
      const br = M(new THREE.CylinderGeometry(.36, .36, .05, 24), std(0x111111)); br.position.y = .97; g.add(br); }
    g.userData.head = head; return g;
  }

  // kesit asansör kuyusu (koyu beton, çelik)
  function shaft(s) {
    const g = new THREE.Group(); s.add(g); const H = 22;
    const fl = M(new THREE.CylinderGeometry(14, 14, 1, 48), concrete()); fl.position.y = .2; g.add(fl);
    const bw = M(rb(9, H, .8), concrete()); bw.position.set(0, H / 2 + .7, -3); g.add(bw);
    [-1, 1].forEach(k => { const w = M(rb(.8, H, 6), std(0x30353d, { roughness: .9 })); w.position.set(k * 4.5, H / 2 + .7, 0); g.add(w); });
    for (let y = 3; y < H; y += 4) { const st = M(rb(8.2, .25, .3, .05), dark()); st.position.set(0, y, -2.5); g.add(st);
      const lp = M(new THREE.BoxGeometry(.6, .15, .1), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); lp.position.set(3.7, y + .4, -2.5); g.add(lp); }
    const roof = M(rb(10, .8, 7), concrete()); roof.position.set(0, H + 1.1, -.2); g.add(roof);
    [-1, 1].forEach(k => { const r = M(rb(.35, H - .5, .35, .08), steel()); r.position.set(k * 2.6, H / 2 + .7, -1.6); g.add(r); });
    const wheel = M(new THREE.TorusGeometry(1.1, .3, 16, 40), steel()); wheel.position.set(-.6, H - .8, -1.2); g.add(wheel);
    const spokes = new THREE.Group(); spokes.position.copy(wheel.position); g.add(spokes);
    for (let i = 0; i < 3; i++) { const sp = M(new THREE.BoxGeometry(2.1, .14, .14), dark()); sp.rotation.z = i * Math.PI / 3; spokes.add(sp); }
    const hub = M(new THREE.SphereGeometry(.38, 24, 16), std(0x991b1b, { emissive: 0x000000 })); hub.position.copy(wheel.position); hub.position.z += .25; g.add(hub);
    const car = new THREE.Group(); g.add(car);
    car.add(M(rb(4.4, 4.6, 3.6, .2), std(0xc3ccd6, { metalness: .8, roughness: .28 })));
    [-1, 1].forEach(k => { const d = M(rb(1.45, 3.6, .15, .05), std(0x8e99a6, { metalness: .9, roughness: .2 })); d.position.set(k * .75, -.3, 1.85); car.add(d); });
    const lamp = M(new THREE.BoxGeometry(2.4, .2, .1), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); lamp.position.set(0, 1.95, 1.86); car.add(lamp);
    const man = person(0x2f6db5); man.position.set(1.6, -1.1, 2.1); man.scale.setScalar(1.15); car.add(man);
    const shoes = []; [-1, 1].forEach(k => { const b = M(rb(.5, 1.1, .7, .1), std(0xb91c1c, { metalness: .4 })); b.position.set(k * 2.45, -1.2, -1.6); car.add(b); shoes.push(b); });
    const ropes = []; for (let i = 0; i < 6; i++) { const r = M(new THREE.CylinderGeometry(.08, .08, 1, 8), std(0x5d646d, { metalness: .9, roughness: .35 })); g.add(r); ropes.push(r); }
    const sp = new THREE.Group(); for (let i = 0; i < 18; i++) sp.add(M(new THREE.SphereGeometry(.09, 8, 8), new THREE.MeshBasicMaterial({ color: i % 2 ? 0xffd45c : 0xff7a1a })));
    g.add(sp); const d = dust(500, [16, 26, 10], 0xcfe0ff, .12, .45); d.position.y = 12; g.add(d);
    const cl = new THREE.PointLight(0xffd8a0, 180, 14); car.add(cl); cl.position.set(0, 0, 4);
    return { g, H, car, man, wheel, spokes, hub, ropes, shoes, sp, d };
  }
  function setRopes(S, carY, topY, cut = []) {
    S.ropes.forEach((r, i) => {
      const x = -1.25 + i * .5;
      if (cut[i] === undefined || cut[i] < 0) { const len = topY - (carY + 2.3); r.scale.y = Math.max(.01, len); r.position.set(x, carY + 2.3 + len / 2, -.2); r.rotation.z = 0; }
      else { const a = cut[i]; const len = Math.max(.6, 3.2 - a * 2); r.scale.y = len; r.position.set(x + Math.sin(a * 9 + i) * .4 * Math.exp(-a * 1.5), topY - len / 2, -.2); r.rotation.z = Math.sin(a * 7 + i) * .25 * Math.exp(-a); }
    });
  }

  // 1) Gece şehir, cam kuyulu bina, asansör yükselir
  shots.push({ t0: 0, t1: 5.2, fov: 32, build: (s, cam) => {
    lights(s, { bg: ['#16335e', '#03070f'], near: 60, far: 200, key: 1500 });
    const gr = M(new THREE.PlaneGeometry(400, 400), std(0x0b1018, { roughness: .4, metalness: .3 })); gr.rotation.x = -Math.PI / 2; s.add(gr);
    const winM = [0xffd27a, 0x9fd3ff, 0x1a2230].map(c => new THREE.MeshBasicMaterial({ color: c }));
    for (let i = 0; i < 26; i++) { const a = r1() * Math.PI * 2, rr = 12 + r1() * 30, h = 6 + r1() * 22, w = 3 + r1() * 4;
      const b = M(new THREE.BoxGeometry(w, h, w), std(0x141c28, { roughness: .8 })); b.position.set((r1() - .5) * 70 + a * 0, h / 2, -12 - rr * .8); s.add(b);
      for (let k = 0; k < 6; k++) { const wn = M(new THREE.PlaneGeometry(.5, .7), winM[(r1() * 3) | 0]); wn.position.set(b.position.x + (r1() - .5) * (w - 1), 1 + r1() * (h - 2), b.position.z + w / 2 + .02); s.add(wn); } }
    const B = new THREE.Group(); B.position.set(-1.5, 0, -1.5); s.add(B);
    const FH = 3.2, NF = 4, BW = 8, BD = 6;
    const bk = M(rb(BW, FH * NF + .6, .6), std(0x252b35, { roughness: .8 })); bk.position.set(0, FH * NF / 2 + .3, -BD / 2); B.add(bk);
    [-1, 1].forEach(k => { const w = M(rb(.6, FH * NF + .6, BD), std(0x2c333e, { roughness: .8 })); w.position.set(k * BW / 2, FH * NF / 2 + .3, 0); B.add(w); });
    for (let f = 0; f <= NF; f++) { const sl = M(rb(BW + .4, .45, BD + .2, .08), std(0x3b4350)); sl.position.set(0, f * FH + .2, .1); B.add(sl);
      if (f < NF) { const pl = new THREE.PointLight(0xffc98a, 60, 7); pl.position.set(-1, f * FH + 2.4, 0); B.add(pl);
        const pp = person([0xb91c1c, 0x2f6db5, 0x3f8f4a, 0x7d5bb5][f]); pp.position.set(-.8, f * FH + 1.0, .6); pp.scale.setScalar(.9); B.add(pp); } }
    const glass = M(new THREE.BoxGeometry(2.8, FH * NF, 2.8), new THREE.MeshStandardMaterial({ color: 0x9fd3ff, transparent: true, opacity: .15, roughness: .1 })); glass.position.set(2.3, FH * NF / 2 + .4, -.6); B.add(glass);
    const car = M(rb(2.2, 2.6, 2.2, .15), std(0xc3ccd6, { metalness: .8, roughness: .25, emissive: 0x332200 })); B.add(car);
    const cl = new THREE.PointLight(0xffd27a, 120, 9); B.add(cl);
    const rope = M(new THREE.CylinderGeometry(.06, .06, 1, 8), std(0x777f88, { metalness: .9 })); B.add(rope);
    const d = dust(400, [80, 40, 60], 0x9fc4ff, .2, .35); d.position.y = 18; s.add(d);
    return t => {
      const y = lerp(1.6, FH * 3 + 1.6, ease(prog(t, .2, 4.6)));
      car.position.set(2.3, y, -.6); cl.position.set(2.3, y, 1.5); const top = FH * NF + .9; rope.scale.y = top - (y + 1.3); rope.position.set(2.3, y + 1.3 + rope.scale.y / 2, -.6);
      d.rotation.y = t * .03;
      const ang = lerp(-.6, -.1, ease(prog(t, 0, 5.2))); const R = lerp(74, 64, ease(prog(t, 0, 5.2)));
      cam.position.set(Math.sin(ang) * R, lerp(40, 34, prog(t, 0, 5.2)), Math.cos(ang) * R); cam.lookAt(0, 11, 0);
    };
  } });

  // 2) Birden fazla halat, biri kopar
  shots.push({ t0: 5.2, t1: 12.75, fov: 32, build: (s, cam) => {
    const key = lights(s); const S = shaft(s); key.target.position.set(0, 10, 0);
    const cy = 9;
    return t => {
      const snap = 10.2; const cut = S.ropes.map((_, i) => i === 2 && t > snap ? t - snap : -1);
      const bob = t > snap && t < snap + .8 ? Math.sin((t - snap) * 30) * .12 * (1 - (t - snap) / .8) : 0;
      S.car.position.set(0, cy + bob, -.4); setRopes(S, cy + bob, S.H - .4, cut);
      S.wheel.rotation.z = S.spokes.rotation.z = t * .5; S.sp.visible = false; S.d.rotation.y = t * .04;
      const hl = prog(t, 7.8, .4) * (1 - prog(t, 9.8, .3)); S.ropes.forEach(r => r.material.emissive = new THREE.Color(0xffcf2e).multiplyScalar(hl * .9));
      const a = lerp(-.35, .2, ease(prog(t, 5.2, 7.5)));
      cam.position.set(Math.sin(a) * 52, 20, Math.cos(a) * 52); cam.lookAt(0, lerp(14, 12.5, prog(t, 5.2, 7.5)), 0);
    };
  } });

  // 3) Hepsi kopar: regülatör + fren
  shots.push({ t0: 12.75, t1: 18.6, fov: 32, build: (s, cam) => {
    const key = lights(s, { rim: 0xff4a3a }); const S = shaft(s); key.target.position.set(0, 10, 0);
    const red = new THREE.PointLight(0xff3b30, 0, 20); red.position.set(-.6, S.H - .8, 2); s.add(red);
    const top = 15, snap = 13.3, brake = 16.9;
    return t => {
      let y = top; if (t > snap) { const a = Math.min(t, brake) - snap; y = top - .45 * a * a; }
      const shake = t > brake && t < brake + .5 ? Math.sin(t * 80) * .1 : 0;
      S.car.position.set(shake, y, -.4); setRopes(S, y, S.H - .4, S.ropes.map(() => t > snap ? t - snap : -1));
      const spd = t > snap ? Math.min(14, (Math.min(t, brake) - snap) * 6) : .4;
      S.wheel.rotation.z = S.spokes.rotation.z = (t - 12.75) * spd;
      const glow = prog(t, 15.1, .3) * (t < brake + 1 ? 1 : .3);
      S.hub.material.emissive = new THREE.Color(0xff2a1a).multiplyScalar(glow); red.intensity = 250 * glow;
      S.shoes.forEach((b, k) => b.position.x = (k ? 1 : -1) * lerp(2.45, 2.75, prog(t, brake - .15, .15)));
      const sk = prog(t, brake, .9); S.sp.children.forEach((p, i) => { const k = i % 2 ? 1 : -1; const a = i / 18 * Math.PI * 2;
        p.visible = sk > 0 && sk < 1; p.position.set(k * 2.7 + Math.cos(a) * sk * 1.8 * k, y - 1.2 + Math.sin(a) * sk * 1.4, -1.4 + Math.sin(a * 3) * .6); });
      S.d.position.y = 12 + (t > snap && t < brake ? (t - snap) * 3 : 0);
      cam.position.set(18, lerp(22, 15, prog(t, 12.75, 5.8)), 46); cam.lookAt(0, lerp(14, 11, prog(t, 12.75, 5.8)), 0);
    };
  } });

  // 4) Kuyu dibi: tamponlar
  shots.push({ t0: 18.6, t1: 22.8, fov: 32, build: (s, cam) => {
    const key = lights(s, { bg: ['#10203a', '#020509'] }); key.target.position.set(0, 3, 0);
    const g = new THREE.Group(); s.add(g);
    const fl = M(new THREE.CylinderGeometry(14, 14, 1, 48), concrete()); fl.position.y = .2; g.add(fl);
    const bk = M(rb(9, 12, .8), concrete()); bk.position.set(0, 6.7, -3); g.add(bk);
    [-1, 1].forEach(k => { const w = M(rb(.8, 12, 6), std(0x30353d, { roughness: .9 })); w.position.set(k * 4.5, 6.7, 0); g.add(w); });
    const stripe = M(new THREE.BoxGeometry(8.2, .5, .1), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); stripe.position.set(0, 1.2, -2.55); g.add(stripe);
    const springs = []; [-1.3, 1.3].forEach(x => {
      const sp = new THREE.Group(); sp.position.set(x, .7, -.3); g.add(sp);
      const coil = M(new THREE.TorusKnotGeometry(.6, .14, 140, 12, 1, 6), std(0xd62828, { metalness: .5, roughness: .35 })); coil.rotation.x = Math.PI / 2; coil.scale.set(1, 1, 2.2); coil.position.y = 1.4; sp.add(coil);
      const cap = M(rb(1.6, .35, 1.6, .08), steel()); cap.position.y = 2.9; sp.add(cap); springs.push(sp);
    });
    const car = M(rb(4.4, 4.6, 3.6, .2), std(0xc3ccd6, { metalness: .8, roughness: .28 })); g.add(car);
    const d = dust(300, [14, 14, 10], 0xcfe0ff, .12, .4); d.position.y = 6; g.add(d);
    return t => {
      const k = ease(prog(t, 18.8, 2.4)); const comp = prog(t, 20.6, .9);
      car.position.set(0, lerp(12, 5.6, k) - comp * .9, -.3); springs.forEach(sp => sp.scale.y = 1 - comp * .32);
      d.rotation.y = t * .05;
      cam.position.set(-14, lerp(14, 10, prog(t, 18.6, 4.2)), 34); cam.lookAt(0, 4.5, 0);
    };
  } });

  // 5) 1854 Otis gösterisi (sepya, spot ışık)
  shots.push({ t0: 22.8, t1: 30.0, fov: 32, build: (s, cam) => {
    s.background = gradTex('#3a2614', '#0a0603'); s.fog = new THREE.Fog(0x140c06, 40, 120);
    s.add(new THREE.HemisphereLight(0xffd9a8, 0x1a0f08, .7));
    const key = new THREE.SpotLight(0xffe2b0, 2600, 120, .38, .5, 1.1); key.position.set(-6, 40, 28); s.add(key); key.target.position.set(0, 6, -1); s.add(key.target);
    const rim = new THREE.PointLight(0xff9a4a, 400, 60); rim.position.set(14, 10, -10); s.add(rim);
    const wood = c => std(c, { roughness: .8 });
    const fl = M(new THREE.CylinderGeometry(16, 16, 1, 48), wood(0x3d2a1a)); fl.position.y = .2; s.add(fl);
    const g = new THREE.Group(); s.add(g);
    const stage = M(rb(10, .8, 7), wood(0x6b4426)); stage.position.set(0, 1.1, -1); g.add(stage);
    [-1, 1].forEach(k => { const p = M(rb(.7, 11, .7, .1), wood(0x5a3a22)); p.position.set(k * 2.6, 6.8, -1.5); g.add(p); });
    const beam = M(rb(6.4, .7, .9, .1), wood(0x5a3a22)); beam.position.set(0, 12.3, -1.5); g.add(beam);
    const plat = new THREE.Group(); g.add(plat);
    plat.add(M(rb(4.6, .4, 3.4, .08), wood(0x8a5a34)));
    const otis = person(0x1f2a36, true); otis.position.set(0, 1.0, .3); otis.scale.setScalar(1.6); plat.add(otis);
    const arm = M(new THREE.CapsuleGeometry(.12, .6, 6, 12), std(0x1f2a36)); arm.position.set(.6, 1.9, .3); arm.rotation.z = -2.2; plat.add(arm);
    const rope = M(new THREE.CylinderGeometry(.1, .1, 1, 8), wood(0xb08a5a)); g.add(rope);
    const cutter = person(0x3f5f3a); cutter.position.set(3.6, 1.9, 1.5); cutter.scale.setScalar(1.4); g.add(cutter);
    const crowd = []; for (let i = 0; i < 9; i++) { const p = person([0x5a2020, 0x22344f, 0x3d2f4f, 0x5a4220, 0x2f4a2a][i % 5], i % 3 === 0);
      const a = -1.1 + i * .27; p.position.set(Math.sin(a) * 8.5, .75, Math.cos(a) * 8.5 + 1); p.lookAt(0, .75, -1); g.add(p); crowd.push(p); }
    const d = dust(400, [40, 24, 30], 0xffd9a8, .18, .4); d.position.y = 10; s.add(d);
    return t => {
      const cutT = 27.15; const drop = t > cutT ? Math.min(.35, (t - cutT) * 1.6) : 0;
      const shake = t > cutT + .2 && t < cutT + .5 ? Math.sin(t * 60) * .06 : 0;
      const py = 8.2 - drop; plat.position.set(shake, py, -1.2);
      if (t < cutT) { const len = 12 - py - .3; rope.scale.y = len; rope.position.set(0, py + .3 + len / 2, -1.2); }
      else { const a = t - cutT; rope.scale.y = Math.max(.5, 2 - a); rope.position.set(Math.sin(a * 9) * .4 * Math.exp(-a), 12 - rope.scale.y / 2, -1.2); }
      arm.rotation.z = -2.2 + (t > cutT + .6 ? Math.sin(t * 5) * .3 : 0);
      crowd.forEach((p, i) => p.position.y = .75 + (t > cutT + .6 ? Math.abs(Math.sin(t * 7 + i)) * .35 : 0));
      d.rotation.y = t * .03;
      const a = lerp(-.45, .15, ease(prog(t, 22.8, 7.2)));
      cam.position.set(Math.sin(a) * 50, lerp(22, 18, prog(t, 22.8, 7.2)), Math.cos(a) * 50); cam.lookAt(0, 5.5, 0);
    };
  } });

  // 6) Sıradaki soru: bulutların üstünde uçak (alacakaranlık)
  shots.push({ t0: 30.0, t1: 99, fov: 32, build: (s, cam) => {
    s.background = gradTex('#f08a4b', '#1b2a52'); s.fog = new THREE.Fog(0x6a5a7a, 50, 160);
    s.add(new THREE.HemisphereLight(0xffd0a0, 0x203050, 1.2));
    const sun = new THREE.DirectionalLight(0xffb070, 2.4); sun.position.set(-30, 20, -20); s.add(sun);
    const fill = new THREE.DirectionalLight(0xffd8c0, 1.6); fill.position.set(20, -10, 40); s.add(fill);
    const cm = new THREE.MeshStandardMaterial({ color: 0xffe3d0, roughness: 1, transparent: true, opacity: .92 });
    for (let i = 0; i < 40; i++) { const c = M(new THREE.SphereGeometry(2 + r1() * 3.5, 20, 14), cm); c.position.set((r1() - .5) * 70, -2 + r1() * 2.5, (r1() - .5) * 50 - 6); c.scale.y = .55; s.add(c); }
    const plane = new THREE.Group(); s.add(plane);
    const al = std(0xe8edf2, { metalness: .6, roughness: .3 });
    const body = M(new THREE.CapsuleGeometry(.9, 5, 12, 32), al); body.rotation.z = Math.PI / 2; plane.add(body);
    const wing = M(rb(1.6, .2, 9, .08), al); plane.add(wing);
    const tail = M(rb(1.2, 1.6, .18, .06), std(0xc0392b, { metalness: .4 })); tail.position.set(-3, .9, 0); plane.add(tail);
    const tw2 = M(rb(.9, .18, 3, .06), al); tw2.position.set(-3, .2, 0); plane.add(tw2);
    [-1, 1].forEach(k => { const e = M(new THREE.CylinderGeometry(.35, .35, 1.2, 20), dark()); e.rotation.z = Math.PI / 2; e.position.set(.4, -.4, k * 2.2); plane.add(e); });
    const nav = [0xff2a2a, 0x2aff6a].map((c, k) => { const m = M(new THREE.SphereGeometry(.15, 8, 8), new THREE.MeshBasicMaterial({ color: c })); m.position.set(0, 0, (k ? 1 : -1) * 4.5); plane.add(m); return m; });
    const streak = dust(200, [60, 10, 30], 0xffffff, .15, .5); streak.position.y = 8; s.add(streak);
    return t => {
      const a = (t - 30) * .55; plane.position.set(Math.cos(a) * 9, 10 + Math.sin(a * 2) * .6, Math.sin(a) * 6);
      plane.rotation.y = -a - Math.PI / 2 + Math.PI; plane.rotation.z = -.25;
      nav.forEach(n => n.visible = Math.floor(t * 2) % 2 === 0); streak.position.x = (t * 6) % 30 - 15;
      cam.position.set(Math.sin(.2) * 58, 30, Math.cos(.2) * 58); cam.lookAt(0, 8, 0);
    };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const titles = [
    { t0: 0, t1: 3.0, html: T('BİR SORU', 'ASANSÖRÜN HALATI <span class="y">KOPARSA?</span>') },
    { t0: 3.0, t1: 5.2, html: T('CEVAP', 'NEREDEYSE <span class="y">İMKÂNSIZ</span>') },
    { t0: 5.2, t1: 9.8, html: T('GÜVENLİK 1', 'BİRDEN FAZLA <span class="y">HALAT</span>') },
    { t0: 9.8, t1: 12.75, html: T('BİRİ KOPARSA', 'DİĞERLERİ <span class="y">TAŞIR</span>') },
    { t0: 12.75, t1: 18.6, html: T('GÜVENLİK 2', 'REGÜLATÖR + <span class="y">FREN</span>') },
    { t0: 18.6, t1: 22.8, html: T('GÜVENLİK 3', 'DEV <span class="y">TAMPONLAR</span>') },
    { t0: 22.8, t1: 30.0, html: T('1854 · İLK GÖSTERİ', 'ELISHA <span class="y">OTIS</span>') },
    { t0: 30.0, t1: 99, html: T('SIRADAKİ SORU', 'UÇAKLAR HAVADA NASIL <span class="y">DURUR?</span>', 92) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 35.25, shots, titles,
    follow: { t: 33.44, click: 34.34 },
    sfx: [[10.2, 'snap', .8], [13.3, 'snap', 1], [13.35, 'whoosh', .8], [16.9, 'crunch', 1], [16.95, 'boom', .7], [20.6, 'boom', .5], [23.9, 'pop', 1], [27.15, 'snap', 1], [27.5, 'pop_low', 1]],
  };
};
