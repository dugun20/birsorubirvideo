// Bilgi #2: Asansörün halatı koparsa ne olur? (clay diorama)
import { clayKit } from '../../lib/clay.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp } = L;
  const C = clayKit(L); const P = C.PAL;
  const shots = [];

  // ---- ortak: kesit asansör kuyusu maketi ----
  function shaft(s, o = {}) {
    const g = new THREE.Group(); s.add(g);
    const H = 22;
    const bs = C.base(9, P.grass); g.add(bs);
    const backW = C.mesh(C.rbox(9, H, .8, .3), P.wall); backW.position.set(0, H / 2 + .7, -3); g.add(backW);
    [-1, 1].forEach(k => { const w = C.mesh(C.rbox(.8, H, 6, .3), P.wall2); w.position.set(k * 4.5, H / 2 + .7, 0); g.add(w); });
    const roof = C.mesh(C.rbox(10, .8, 7, .3), P.roof); roof.position.set(0, H + 1.1, -.2); g.add(roof);
    const rails = []; [-1, 1].forEach(k => { const r = C.mesh(C.rbox(.35, H - .5, .35, .12), P.metal); r.position.set(k * 2.6, H / 2 + .7, -1.6); g.add(r); rails.push(r); });
    const wheel = C.mesh(new THREE.TorusGeometry(1.1, .35, 16, 32), 0x7d8792); wheel.position.set(-.6, H - .8, -1.2); g.add(wheel);
    const hub = C.mesh(C.blob(.4), P.red); hub.position.copy(wheel.position); hub.position.z += .2; g.add(hub);
    const car = new THREE.Group(); g.add(car);
    car.add(C.mesh(C.rbox(4.4, 4.6, 3.6, .5), P.yellow));
    const door = C.mesh(C.rbox(3, 3.6, .2, .1), P.orange); door.position.z = 1.85; car.add(door);
    const win = C.mesh(C.rbox(1.6, .8, .12, .06), 0x9fd3f0); win.position.set(0, 1.1, 1.97); car.add(win);
    const man = C.person({ body: P.blue }); man.position.set(1.05, -1.0, 1.25); man.scale.setScalar(1.3); car.add(man);
    const shoes = []; [-1, 1].forEach(k => { const b = C.mesh(C.rbox(.5, 1.1, .7, .15), P.red); b.position.set(k * 2.45, -1.2, -1.6); car.add(b); shoes.push(b); });
    const ropes = []; for (let i = 0; i < (o.ropes || 6); i++) { const r = new THREE.Mesh(new THREE.CylinderGeometry(.09, .09, 1, 8), C.mat(P.dark)); r.castShadow = true; g.add(r); ropes.push(r); }
    const sp = C.sparks(18); g.add(sp);
    return { g, H, car, man, wheel, hub, ropes, shoes, sp, rails };
  }
  function setRopes(S, carY, topY, cut = []) {
    S.ropes.forEach((r, i) => {
      const x = -1.25 + i * .5;
      if (cut[i] === undefined || cut[i] < 0) { const len = topY - (carY + 2.3); r.scale.y = Math.max(.01, len); r.position.set(x, carY + 2.3 + len / 2, -.2); r.rotation.z = 0; }
      else { const a = cut[i]; const len = Math.max(.6, 3.2 - a * 2); r.scale.y = len; r.position.set(x + Math.sin(a * 9 + i) * .4 * Math.exp(-a * 1.5), topY - len / 2, -.2); r.rotation.z = Math.sin(a * 7 + i) * .25 * Math.exp(-a); }
    });
  }

  // 1) Kanca: maket bina, asansör yukarı çıkıyor
  shots.push({ t0: 0, t1: 5.2, fov: 32, build: (s, cam) => {
    C.studio(s); const D = new THREE.Group(); s.add(D);
    D.add(C.base(11));
    const road = C.mesh(C.rbox(5, .2, 22, .1), P.road); road.position.set(6.5, .8, 0); road.rotation.y = .1; D.add(road);
    [[-8, -4], [-7.5, 3.5], [-4.5, 7], [8.5, 6.5], [3.5, 8.5]].forEach(([x, z], i) => { const t = C.tree(1, i); t.position.set(x, .7, z); D.add(t); });
    const B = new THREE.Group(); B.position.set(-1.5, .7, -1.5); D.add(B);
    const FH = 3.2, NF = 4, BW = 8, BD = 6;
    const bk = C.mesh(C.rbox(BW, FH * NF + .6, .6), P.wall); bk.position.set(0, FH * NF / 2 + .3, -BD / 2); B.add(bk);
    [-1, 1].forEach(k => { const w = C.mesh(C.rbox(.6, FH * NF + .6, BD), P.wall2); w.position.set(k * BW / 2, FH * NF / 2 + .3, 0); B.add(w); });
    for (let f = 0; f <= NF; f++) { const sl = C.mesh(C.rbox(BW + .4, .45, BD + .2, .15), f === NF ? P.roof : P.floor); sl.position.set(0, f * FH + .2, .1); B.add(sl); }
    for (let f = 0; f < NF; f++) { const so = C.mesh(C.rbox(1.8, .8, .9, .3), [P.blue, 0xf6b26b, P.purple, 0x93c47d][f]); so.position.set(-2.4, f * FH + .85, -1.8); B.add(so);
      const pp = C.person({ body: [P.red, P.blue, 0x93c47d, P.purple][f] }); pp.position.set(-.4, f * FH + 1.0, .6); pp.scale.setScalar(.9); B.add(pp); }
    const car = C.mesh(C.rbox(2.2, 2.6, 2.2, .35), P.yellow); B.add(car);
    const rope = new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, 1, 8), C.mat(P.dark)); B.add(rope);
    const clouds = [[-9, 23, -6], [8, 25, -8], [1, 28, -12]].map(([x, y, z]) => { const c = C.cloud(); c.position.set(x, y, z); s.add(c); return c; });
    return t => {
      const y = lerp(1.6, FH * 3 + 1.6, ease(prog(t, .2, 4.6)));
      car.position.set(2.3, y, -.6); const top = FH * NF + .9; rope.scale.y = top - (y + 1.3); rope.position.set(2.3, y + 1.3 + rope.scale.y / 2, -.6);
      clouds.forEach((c, i) => c.position.x += Math.sin(t * .3 + i) * .01);
      const ang = lerp(-.6, -.1, ease(prog(t, 0, 5.2))); const R = lerp(74, 64, ease(prog(t, 0, 5.2)));
      cam.position.set(Math.sin(ang) * R, lerp(40, 34, prog(t, 0, 5.2)), Math.cos(ang) * R); cam.lookAt(0, 11, 0);
    };
  } });

  // 2-3) Birden fazla halat, biri kopar, diğerleri taşır
  shots.push({ t0: 5.2, t1: 12.75, fov: 32, build: (s, cam) => {
    C.studio(s, { shadow: 14 }); const S = shaft(s);
    const cy = 9;
    return t => {
      const snap = 10.2; const cut = S.ropes.map((_, i) => i === 2 && t > snap ? t - snap : -1);
      const bob = t > snap && t < snap + .8 ? Math.sin((t - snap) * 30) * .12 * (1 - (t - snap) / .8) : 0;
      S.car.position.set(0, cy + bob, -.4); setRopes(S, cy + bob, S.H - .4, cut);
      S.wheel.rotation.z = t * .5; S.sp.visible = false;
      S.man.userData.head.scale.setScalar(t > snap && t < snap + 1 ? 1.12 : 1);
      // halatlar parlasın (vurgu)
      const hl = prog(t, 7.8, .4) * (1 - prog(t, 9.8, .3)); S.ropes.forEach(r => r.material.emissive = new THREE.Color(0xffd45c).multiplyScalar(hl * .6));
      const a = lerp(-.35, .2, ease(prog(t, 5.2, 7.5)));
      cam.position.set(Math.sin(a) * 52, 20, Math.cos(a) * 52); cam.lookAt(0, lerp(14, 12.5, prog(t, 5.2, 7.5)), 0);
    };
  } });

  // 4) Hepsi kopar: regülatör + fren
  shots.push({ t0: 12.75, t1: 18.6, fov: 32, build: (s, cam) => {
    C.studio(s, { shadow: 14 }); const S = shaft(s);
    const top = 15, snap = 13.3, brake = 16.9;
    return t => {
      let y = top;
      if (t > snap) { const a = Math.min(t, brake) - snap; y = top - .45 * a * a; }
      const shake = t > brake && t < brake + .5 ? Math.sin(t * 80) * .1 : 0;
      S.car.position.set(shake, y, -.4);
      setRopes(S, y, S.H - .4, S.ropes.map(() => t > snap ? t - snap : -1));
      // regülatör: hızlanınca döner ve kırmızı parlar
      const spd = t > snap ? Math.min(14, (Math.min(t, brake) - snap) * 6) : .4;
      S.wheel.rotation.z += 0; S.wheel.rotation.z = (t - 12.75) * spd;
      S.hub.material.emissive = new THREE.Color(0xff3b30).multiplyScalar(prog(t, 15.1, .3) * (t < brake + 1 ? 1 : .3));
      // fren pabuçları raylara kapanır
      S.shoes.forEach((b, k) => b.position.x = (k ? 1 : -1) * lerp(2.45, 2.75, prog(t, brake - .15, .15)));
      const sk = prog(t, brake, .9); S.sp.children.forEach((p, i) => { const k = i % 2 ? 1 : -1; const a = i / 18 * Math.PI * 2;
        p.visible = sk > 0 && sk < 1; p.position.set(k * 2.7 + Math.cos(a) * sk * 1.8 * k, y - 1.2 + Math.sin(a) * sk * 1.4, -1.4 + Math.sin(a * 3) * .6); });
      S.man.userData.head.scale.setScalar(t > snap && t < brake + .8 ? 1.15 : 1);
      cam.position.set(18, lerp(22, 15, prog(t, 12.75, 5.8)), 46); cam.lookAt(0, lerp(14, 11, prog(t, 12.75, 5.8)), 0);
    };
  } });

  // 5) Kuyu dibinde tamponlar
  shots.push({ t0: 18.6, t1: 22.8, fov: 32, build: (s, cam) => {
    C.studio(s, { shadow: 12 });
    const g = new THREE.Group(); s.add(g); g.add(C.base(9, 0xc9b8a6));
    const bk = C.mesh(C.rbox(9, 12, .8, .3), P.wall); bk.position.set(0, 6.7, -3); g.add(bk);
    [-1, 1].forEach(k => { const w = C.mesh(C.rbox(.8, 12, 6, .3), P.wall2); w.position.set(k * 4.5, 6.7, 0); g.add(w); });
    const springs = []; [-1.3, 1.3].forEach(x => {
      const sp = new THREE.Group(); sp.position.set(x, .7, -.3); g.add(sp);
      const coil = C.mesh(new THREE.TorusKnotGeometry(.6, .16, 120, 12, 1, 6), 0xe06666); coil.rotation.x = Math.PI / 2; coil.scale.set(1, 1, 2.2); coil.position.y = 1.4; sp.add(coil);
      const cap = C.mesh(C.rbox(1.6, .35, 1.6, .15), P.metal); cap.position.y = 2.9; sp.add(cap); springs.push(sp);
    });
    const car = C.mesh(C.rbox(4.4, 4.6, 3.6, .5), P.yellow); g.add(car);
    const door = C.mesh(C.rbox(3, 3.6, .2, .1), P.orange); door.position.z = 1.85; car.add(door);
    return t => {
      const k = ease(prog(t, 18.8, 2.4)); const comp = prog(t, 20.6, .9);
      const y = lerp(12, 5.6, k) - comp * .9; car.position.set(0, y, -.3);
      springs.forEach(sp => sp.scale.y = 1 - comp * .32);
      cam.position.set(-14, lerp(14, 10, prog(t, 18.6, 4.2)), 34); cam.lookAt(0, 4.5, 0);
    };
  } });

  // 6) 1854 Elisha Otis gösterisi
  shots.push({ t0: 22.8, t1: 30.0, fov: 32, build: (s, cam) => {
    C.studio(s, { bg: ['#fde2c4', '#e9b38f'] });
    const g = new THREE.Group(); s.add(g); g.add(C.base(11, 0xd8b98c));
    const stage = C.mesh(C.rbox(10, .8, 7, .3), 0xa0603f); stage.position.set(0, 1.1, -1); g.add(stage);
    [-1, 1].forEach(k => { const p = C.mesh(C.rbox(.7, 11, .7, .25), 0x8a5a3c); p.position.set(k * 2.6, 6.8, -1.5); g.add(p); });
    const beam = C.mesh(C.rbox(6.4, .7, .9, .25), 0x8a5a3c); beam.position.set(0, 12.3, -1.5); g.add(beam);
    const plat = new THREE.Group(); g.add(plat);
    const floor = C.mesh(C.rbox(4.6, .4, 3.4, .15), 0xc28a5c); plat.add(floor);
    const otis = C.person({ body: 0x34495e, hat: true }); otis.position.set(0, 1.0, .3); otis.scale.setScalar(1.6); plat.add(otis);
    const arm = C.mesh(new THREE.CapsuleGeometry(.12, .6, 6, 12), 0x34495e); arm.position.set(.6, 1.9, .3); arm.rotation.z = -2.2; plat.add(arm);
    const rope = new THREE.Mesh(new THREE.CylinderGeometry(.1, .1, 1, 8), C.mat(P.dark)); g.add(rope);
    const cutter = C.person({ body: 0x93c47d }); cutter.position.set(3.6, 1.9, 1.5); cutter.scale.setScalar(1.4); g.add(cutter);
    const crowd = []; for (let i = 0; i < 9; i++) { const p = C.person({ body: [P.red, P.blue, P.purple, 0xf6b26b, 0x93c47d][i % 5], hat: i % 3 === 0 });
      const a = -1.1 + i * .27; p.position.set(Math.sin(a) * 8.5, .75, Math.cos(a) * 8.5 + 1); p.lookAt(0, .75, -1); g.add(p); crowd.push(p); }
    return t => {
      const cutT = 27.15; const drop = t > cutT ? Math.min(.35, (t - cutT) * 1.6) : 0;
      const shake = t > cutT + .2 && t < cutT + .5 ? Math.sin(t * 60) * .06 : 0;
      const py = 8.2 - drop; plat.position.set(shake, py, -1.2);
      if (t < cutT) { const len = 12 - py - .3; rope.visible = true; rope.scale.y = len; rope.position.set(0, py + .3 + len / 2, -1.2); }
      else { const a = t - cutT; rope.scale.y = Math.max(.5, 2 - a); rope.position.set(Math.sin(a * 9) * .4 * Math.exp(-a), 12 - rope.scale.y / 2, -1.2); }
      arm.rotation.z = -2.2 + (t > cutT + .6 ? Math.sin(t * 5) * .3 : 0);
      crowd.forEach((p, i) => p.position.y = .75 + (t > cutT + .6 ? Math.abs(Math.sin(t * 7 + i)) * .35 : 0));
      const a = lerp(-.45, .15, ease(prog(t, 22.8, 7.2)));
      cam.position.set(Math.sin(a) * 50, lerp(22, 18, prog(t, 22.8, 7.2)), Math.cos(a) * 50); cam.lookAt(0, 5.5, 0);
    };
  } });

  // 7) Sıradaki soru: uçak
  shots.push({ t0: 30.0, t1: 99, fov: 32, build: (s, cam) => {
    C.studio(s, { bg: ['#d8efff', '#ffe2cf'] });
    const g = new THREE.Group(); s.add(g); g.add(C.base(10));
    const run = C.mesh(C.rbox(16, .2, 3, .1), P.road); run.position.set(0, .8, 2); run.rotation.y = -.3; g.add(run);
    const tw = C.mesh(new THREE.CylinderGeometry(.8, 1, 6, 24), P.wall); tw.position.set(-5, 3.7, -4); g.add(tw);
    const cab = C.mesh(C.rbox(2.6, 1.4, 2.6, .4), 0x9fd3f0); cab.position.set(-5, 7.3, -4); g.add(cab);
    [[6, -4], [-7, 4], [4, 6.5]].forEach(([x, z], i) => { const t = C.tree(.9, i); t.position.set(x, .7, z); g.add(t); });
    const plane = new THREE.Group(); s.add(plane);
    const body = C.mesh(new THREE.CapsuleGeometry(.9, 5, 12, 24), 0xffffff); body.rotation.z = Math.PI / 2; plane.add(body);
    const wing = C.mesh(C.rbox(1.6, .25, 8, .12), P.red); plane.add(wing);
    const tail = C.mesh(C.rbox(1.2, 1.6, .2, .1), P.red); tail.position.set(-3, .9, 0); plane.add(tail);
    const tw2 = C.mesh(C.rbox(.9, .2, 3, .1), P.red); tw2.position.set(-3, .2, 0); plane.add(tw2);
    const nose = C.mesh(C.blob(.55), 0x9fd3f0); nose.position.set(2.9, .3, 0); plane.add(nose);
    const prop = C.mesh(C.rbox(.15, 2.2, .3, .07), P.dark); prop.position.set(3.55, 0, 0); plane.add(prop);
    const clouds = [[-7, 15, -3], [7, 17, -6]].map(([x, y, z]) => { const c = C.cloud(); c.position.set(x, y, z); s.add(c); return c; });
    return t => {
      const a = (t - 30) * .55; plane.position.set(Math.cos(a) * 9, 10 + Math.sin(a * 2) * .6, Math.sin(a) * 6);
      plane.rotation.y = -a - Math.PI / 2 + Math.PI; plane.rotation.z = -.25; prop.rotation.x = t * 30;
      clouds.forEach((c, i) => c.position.x += .008 * (i ? -1 : 1));
      cam.position.set(Math.sin(.2) * 58, 30, Math.cos(.2) * 58); cam.lookAt(0, 8, 0);
    };
  } });

  const T = (html) => C.css + C.tilt + html;
  const titles = [
    { t0: 0, t1: 3.0, html: T(C.tag('BİR SORU') + C.title('ASANSÖRÜN HALATI <y>KOPARSA?</y>')) },
    { t0: 3.0, t1: 5.2, html: T(C.tag('CEVAP') + C.title('NEREDEYSE <y>İMKÂNSIZ</y>')) },
    { t0: 5.2, t1: 9.8, html: T(C.tag('GÜVENLİK 1') + C.title('BİRDEN FAZLA <y>HALAT</y>')) },
    { t0: 9.8, t1: 12.75, html: T(C.tag('BİRİ KOPARSA') + C.title('DİĞERLERİ <y>TAŞIR</y>')) },
    { t0: 12.75, t1: 18.6, html: T(C.tag('GÜVENLİK 2') + C.title('REGÜLATÖR + <y>FREN</y>')) },
    { t0: 18.6, t1: 22.8, html: T(C.tag('GÜVENLİK 3') + C.title('DEV <y>TAMPONLAR</y>')) },
    { t0: 22.8, t1: 30.0, html: T(C.tag('1854 · İLK GÖSTERİ') + C.title('ELISHA <y>OTIS</y>')) },
    { t0: 30.0, t1: 99, html: T(C.tag('SIRADAKİ SORU') + C.title('UÇAKLAR HAVADA NASIL <y>DURUR?</y>', 92) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>`) },
  ];
  return {
    END: 35.25, shots, titles, setup: C.setup,
    follow: { t: 33.44, click: 34.34 },
    update(t, q) { const y = q('yr'); if (y) { y.textContent = t > 23.9 ? '1854' : ''; y.style.transform = `scale(${Math.max(.01, back(prog(t, 23.9, .45)))})`; } },
    sfx: [[10.2, 'snap', .8], [13.3, 'snap', 1], [13.35, 'whoosh', .8], [16.9, 'crunch', 1], [16.95, 'boom', .7], [20.6, 'boom', .5], [23.9, 'pop', 1], [27.15, 'snap', 1], [27.5, 'pop_low', 1]],
  };
};
