// Mariana Çukuru'nun dibinde ne var? (örnek / şablon video)
export default (L, WORDS) => {
const { THREE, clamp, prog, ease, easeOut, back, lerp, hash, gradTex, snow, std, trenchFloor, mountain } = L;
const shots = [];

// A: Everest okyanusa batıyor
shots.push({ t0: 0, t1: 3.6, build: (s, cam, S) => {
  s.background = gradTex('#f2a65a', '#3a6ea5');
  s.fog = new THREE.Fog(0x7aa3c9, 120, 420);
  s.add(new THREE.HemisphereLight(0xffe2c0, 0x1d3b5c, 1.2));
  const sun = new THREE.DirectionalLight(0xffd7a8, 2.4); sun.position.set(-60, 50, 40); s.add(sun);
  const wg = new THREE.PlaneGeometry(600, 600, 120, 120); wg.rotateX(-Math.PI / 2);
  const water = new THREE.Mesh(wg, std(0x0d5a8a, { roughness: .18, metalness: .35 })); s.add(water);
  const base = wg.attributes.position.array.slice();
  const m = mountain(70, 34); m.position.set(0, 26, -20); s.add(m);
  const sp = snow(400, [200, 60, 200], 0xffffff, .4); sp.position.y = 40; sp.material.opacity = .0; s.add(sp);
  return t => {
    const p = wg.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = base[i * 3], z = base[i * 3 + 2]; p.setY(i, Math.sin(x * .05 + t * 1.6) * 1.2 + Math.cos(z * .07 + t * 1.2) * 1.0); }
    p.needsUpdate = true; wg.computeVertexNormals();
    const k = ease(prog(t, .5, 3.0)); m.position.y = lerp(26, -50, k); m.rotation.y = t * .08;
    cam.position.set(Math.sin(t * .2) * 10, lerp(30, 14, k), lerp(130, 110, t / 3.6)); cam.lookAt(0, lerp(18, 2, k), -20);
  };
} });

// B: 11 km aşağı iniş (kesit)
shots.push({ t0: 3.6, t1: 8.4, build: (s, cam, S) => {
  s.add(new THREE.AmbientLight(0x6688aa, .5));
  const head = new THREE.SpotLight(0xbfe6ff, 900, 220, .7, .6, 1.4); s.add(head); s.add(head.target);
  const fl = trenchFloor(); s.add(fl);
  const surf = new THREE.Mesh(new THREE.PlaneGeometry(800, 800), new THREE.MeshBasicMaterial({ color: 0x7fd3ff, transparent: true, opacity: .55, side: 2 }));
  surf.rotation.x = Math.PI / 2; s.add(surf);
  // derinlik cetveli
  const rul = new THREE.Group(); s.add(rul);
  rul.add(new THREE.Mesh(new THREE.BoxGeometry(.5, 112, .5), new THREE.MeshBasicMaterial({ color: 0xffcf2e })));
  rul.children[0].position.y = -56;
  for (let d = 0; d <= 110; d += 10) { const b = new THREE.Mesh(new THREE.BoxGeometry(d % 50 === 0 ? 6 : 3.4, .5, .5), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); b.position.set(1.5, -d, 0); rul.add(b); }
  rul.position.set(-7, 0, 6); rul.scale.set(.6, 1, .6);
  const sp = snow(1500, [120, 140, 80], 0xcfe8ff, .35); sp.position.y = -60; s.add(sp);
  const fog = new THREE.FogExp2(0x0a3a66, .012); s.fog = fog; s.background = new THREE.Color();
  return t => {
    const k = ease(prog(t, 3.75, 4.3)); const y = lerp(4, -100, k);
    cam.position.set(16, y, 38); cam.lookAt(0, y - 9, 0);
    head.position.set(10, y + 6, 30); head.target.position.set(0, y - 20, 0);
    const c = new THREE.Color(0x1a6fae).lerp(new THREE.Color(0x01060f), Math.pow(k, .7));
    s.background.copy(c); fog.color.copy(c);
    sp.rotation.y = t * .05; S.depthM = Math.round(10935 * k);
  };
} });

// C: Everest hendeğe sığar
shots.push({ t0: 8.4, t1: 12.6, build: (s, cam, S) => {
  s.background = gradTex('#2a86c4', '#020a1a');
  s.add(new THREE.HemisphereLight(0xcfe8ff, 0x101820, 1.4));
  const d = new THREE.DirectionalLight(0xffffff, 1.6); d.position.set(30, 60, 80); s.add(d);
  s.add(trenchFloor());
  const surf = new THREE.Mesh(new THREE.BoxGeometry(320, .8, 60), new THREE.MeshBasicMaterial({ color: 0x9fe2ff, transparent: true, opacity: .8 })); s.add(surf);
  const m = mountain(88.5, 26); m.position.set(0, -109.35 + 44.25, 0); s.add(m);
  const yel = new THREE.MeshBasicMaterial({ color: 0xffcf2e });
  const br = new THREE.Group(); s.add(br);
  const v = new THREE.Mesh(new THREE.BoxGeometry(.9, 20.86, .9), yel); v.position.set(30, -10.43, 31); br.add(v);
  [0, -20.86].forEach(yy => { const h = new THREE.Mesh(new THREE.BoxGeometry(8, .9, .9), yel); h.position.set(30, yy, 31); br.add(h); });
  const dash = new THREE.Mesh(new THREE.BoxGeometry(70, .35, .35), yel); dash.position.set(0, -20.86, 31); br.add(dash);
  return t => {
    const k = easeOut(prog(t, 8.6, 1.8)); m.scale.set(1, Math.max(.01, k), 1); m.position.y = -109.35 + 44.25 * k;
    br.visible = t > 10.3; br.scale.y = 1; br.children.forEach(c => c.material.opacity = 1);
    const z = lerp(250, 228, ease(prog(t, 8.4, 4.2)));
    cam.position.set(lerp(-30, 20, prog(t, 8.4, 4.2)), -30, z); cam.lookAt(0, -36, 0);
  };
} });

// D: basınç: köpük bardak büzülür
shots.push({ t0: 12.6, t1: 15.7, build: (s, cam, S) => {
  s.background = gradTex('#0b2347', '#020814'); s.fog = new THREE.Fog(0x041026, 30, 90);
  s.add(new THREE.AmbientLight(0x4466aa, .6));
  const k1 = new THREE.SpotLight(0xffffff, 600, 120, .5, .5, 1.2); k1.position.set(-10, 30, 30); s.add(k1);
  const k2 = new THREE.PointLight(0x55c8ff, 300, 60); k2.position.set(12, 8, 10); s.add(k2);
  const prof = []; for (let i = 0; i <= 12; i++) { const y = i / 12 * 10; prof.push(new THREE.Vector2(2.6 + y * .16, y)); }
  prof.push(new THREE.Vector2(4.5, 10.3)); prof.push(new THREE.Vector2(4.1, 10.3)); prof.push(new THREE.Vector2(2.3, .4)); prof.push(new THREE.Vector2(0, .4));
  const cupG = new THREE.LatheGeometry(prof, 64);
  const cupM = std(0xf3f1ea, { roughness: .9 });
  const c1 = new THREE.Mesh(cupG, cupM); c1.position.set(-5.5, -6, 0); s.add(c1);
  const c2 = new THREE.Mesh(cupG, cupM.clone()); c2.position.set(5.5, -6, 0); s.add(c2);
  const ar = new THREE.Group(); s.add(ar); ar.position.set(5.5, -1, 0);
  for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2; const c = new THREE.Mesh(new THREE.ConeGeometry(.6, 2, 16), new THREE.MeshBasicMaterial({ color: 0xffcf2e }));
    c.position.set(Math.cos(a) * 9, (i % 2) * 4 - 2, Math.sin(a) * 9); c.lookAt(0, c.position.y, 0); c.rotateX(Math.PI / 2); ar.add(c); }
  const sp = snow(500, [60, 40, 40], 0x9fd8ff, .25); s.add(sp);
  return t => {
    const k = ease(prog(t, 13.2, 2.0));
    c2.scale.set(lerp(1, .42, k), lerp(1, .5, k), lerp(1, .42, k));
    ar.rotation.y = t * .6; ar.scale.setScalar(lerp(1.1, .65, k)); ar.visible = t > 13.0;
    cam.position.set(Math.sin(t * .3) * 4, 8, 62); cam.lookAt(0, -6, 0); sp.position.y = -t * 1.5 % 10;
  };
} });

// E: karanlık + sıcaklık
shots.push({ t0: 15.7, t1: 21.8, build: (s, cam, S) => {
  s.background = new THREE.Color(); const fog = new THREE.Fog(0x0b3d70, 20, 120); s.fog = fog;
  s.add(new THREE.AmbientLight(0x335577, .5));
  const rays = new THREE.Group(); s.add(rays);
  for (let i = 0; i < 9; i++) {
    const r = new THREE.Mesh(new THREE.ConeGeometry(4 + i % 3 * 2, 140, 24, 1, true), new THREE.MeshBasicMaterial({ color: 0xbfeaff, transparent: true, opacity: .08, blending: THREE.AdditiveBlending, depthWrite: false, side: 2 }));
    r.position.set(-30 + i * 7.5, 30, -20 + (i % 4) * 6); r.rotation.z = .12 - i * .03; rays.add(r);
  }
  const glass = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 26, 32), new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: .25, roughness: .1 }));
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(2.6, 32, 16), std(0xff3b30, { emissive: 0x661010 }));
  const liq = new THREE.Mesh(new THREE.CylinderGeometry(.9, .9, 1, 24), std(0xff3b30, { emissive: 0x661010 }));
  const th = new THREE.Group(); th.add(glass, bulb, liq); bulb.position.y = -14; s.add(th); th.position.set(0, 0, 0); th.scale.setScalar(.6);
  const pl = new THREE.PointLight(0xffb0a0, 260, 60); pl.position.set(4, 4, 18); s.add(pl);
  const sp = snow(1500, [120, 120, 80], 0xcfe8ff, .3); s.add(sp);
  return t => {
    const k = ease(prog(t, 15.8, 5.6));
    const c = new THREE.Color(0x0e4f8c).lerp(new THREE.Color(0x000207), clamp(k * 1.4));
    s.background.copy(c); fog.color.copy(c);
    rays.children.forEach((r, i) => r.material.opacity = .09 * (1 - clamp(k * 1.6)) * (0.7 + .3 * Math.sin(t * 2 + i)));
    const tk = ease(prog(t, 18.9, 2.2)); S.tempC = Math.round(lerp(20, 2, tk));
    const lv = lerp(22, 4, tk); liq.scale.y = lv; liq.position.y = -13 + lv / 2;
    th.visible = t > 18.6; th.rotation.y = Math.sin(t) * .3;
    cam.position.set(-6, lerp(10, -10, k), 46); cam.lookAt(0, lerp(4, -6, k), 0); sp.position.y = t * 1.2 % 20;
  };
} });

// F: dipte ne var
shots.push({ t0: 21.8, t1: 27.9, build: (s, cam, S) => {
  s.background = new THREE.Color(0x01040b); s.fog = new THREE.Fog(0x01040b, 25, 90);
  s.add(new THREE.AmbientLight(0x223355, .7));
  const lamp = new THREE.SpotLight(0xd9f2ff, 1400, 120, .65, .55, 1.3); lamp.position.set(0, 40, 22); s.add(lamp); s.add(lamp.target);
  const fg = new THREE.PlaneGeometry(200, 200, 100, 100); fg.rotateX(-Math.PI / 2);
  const fp = fg.attributes.position; for (let i = 0; i < fp.count; i++) fp.setY(i, hash(fp.getX(i) * .15, 0, fp.getZ(i) * .15) * 1.2);
  fg.computeVertexNormals(); const floor = new THREE.Mesh(fg, std(0x5a5244, { roughness: 1 })); floor.position.y = -10; s.add(floor);
  // saydam balık (salyangoz balığı)
  const fish = new THREE.Group();
  const fm = new THREE.MeshPhysicalMaterial({ color: 0xffb8cc, transparent: true, opacity: .78, roughness: .2, clearcoat: 1, emissive: 0x4a1424 });
  const head = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), fm); head.scale.set(3.4, 2.6, 2.4); fish.add(head);
  const tl = new THREE.Mesh(new THREE.ConeGeometry(2.2, 10, 40, 1), fm); tl.rotation.z = Math.PI / 2; tl.position.x = 7; fish.add(tl);
  const tail = new THREE.Mesh(new THREE.PlaneGeometry(4.5, 4), new THREE.MeshStandardMaterial({ color: 0xffd0e0, transparent: true, opacity: .45, side: 2 })); tail.position.x = 12.5; fish.add(tail);
  const fin = new THREE.Mesh(new THREE.PlaneGeometry(9, 2.2), new THREE.MeshStandardMaterial({ color: 0xffd0e0, transparent: true, opacity: .4, side: 2 })); fin.position.set(6, 2, 0); fish.add(fin);
  const spine = new THREE.Mesh(new THREE.CylinderGeometry(.16, .05, 11, 8), std(0xfff3f6, { emissive: 0x332222 })); spine.rotation.z = Math.PI / 2; spine.position.x = 5; fish.add(spine);
  [1, -1].forEach(z => { const e = new THREE.Mesh(new THREE.SphereGeometry(.42, 16, 8), std(0x0a0a0a, { roughness: .1 })); e.position.set(-2.4, .7, z * 1.9); fish.add(e); });
  s.add(fish);
  // dev tek hücreli
  const xg = new THREE.IcosahedronGeometry(3.2, 5); const xp = xg.attributes.position;
  for (let i = 0; i < xp.count; i++) { const v = new THREE.Vector3().fromBufferAttribute(xp, i); v.multiplyScalar(1 + .22 * hash(v.x * 1.5, v.y * 1.5, v.z * 1.5)); xp.setXYZ(i, v.x, v.y, v.z); }
  xg.computeVertexNormals(); const xen = new THREE.Mesh(xg, std(0xc9a36f, { roughness: 1, flatShading: true })); xen.position.set(-2.5, -2.5, 9); xen.userData.s = .7; s.add(xen);
  // plastik poşet
  const bg = new THREE.PlaneGeometry(7, 9, 20, 24); const bb = bg.attributes.position.array.slice();
  const bag = new THREE.Mesh(bg, new THREE.MeshStandardMaterial({ color: 0xf4f4f4, transparent: true, opacity: .65, roughness: .3, side: 2 })); s.add(bag);
  const sp = snow(900, [90, 50, 60], 0xbfd9ff, .25); s.add(sp);
  return t => {
    const f = prog(t, 23.4, 3.2); fish.visible = t > 23.4;
    fish.scale.setScalar(.42); fish.position.set(lerp(9, -4, f), 3.5 + Math.sin(t * 2) * .4, 6); fish.rotation.y = Math.sin(t * 3) * .1; tail.rotation.y = Math.sin(t * 9) * .5;
    xen.visible = t > 24.75; xen.scale.setScalar((back(prog(t, 24.75, .6)) || .001) * .7); xen.rotation.y = t * .2;
    bag.visible = t > 26.6; const bk = prog(t, 26.6, 1.4);
    bag.scale.setScalar(.55); bag.position.set(1.8, lerp(12, 2, easeOut(bk)), 8); bag.rotation.set(.3 + Math.sin(t) * .2, t * .4, .2);
    const p = bg.attributes.position; for (let i = 0; i < p.count; i++) { const x = bb[i * 3], y = bb[i * 3 + 1]; p.setZ(i, Math.sin(x * .9 + t * 3) * .6 + Math.cos(y * .7 + t * 2) * .5); } p.needsUpdate = true; bg.computeVertexNormals();
    const a = Math.sin(t * .15) * .3; cam.position.set(Math.sin(a) * 34, 10, Math.cos(a) * 34); cam.lookAt(0, 4, 0);
    lamp.target.position.set(0, -6, 0); sp.position.y = -t % 10;
  };
} });

// G: 1960 Trieste
shots.push({ t0: 27.9, t1: 33.4, build: (s, cam, S) => {
  s.background = new THREE.Color(0x020610); s.fog = new THREE.Fog(0x020610, 40, 150);
  s.add(new THREE.HemisphereLight(0x9fc4ff, 0x221a10, 1.6));
  const key = new THREE.DirectionalLight(0xdde8ff, 2.6); key.position.set(-20, 30, 40); s.add(key);
  const fg = new THREE.PlaneGeometry(240, 240, 80, 80); fg.rotateX(-Math.PI / 2);
  const fp = fg.attributes.position; for (let i = 0; i < fp.count; i++) fp.setY(i, hash(fp.getX(i) * .1, 1, fp.getZ(i) * .1) * 1.6);
  fg.computeVertexNormals(); s.add(new THREE.Mesh(fg, std(0x4d463a, { roughness: 1 })));
  const tri = new THREE.Group(); s.add(tri);
  const fl = new THREE.Mesh(new THREE.CapsuleGeometry(5, 24, 12, 32), std(0xd8dde3, { metalness: .4, roughness: .45 })); fl.rotation.z = Math.PI / 2; tri.add(fl);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(5.15, 5.15, 3, 32), std(0x1d4e89)); band.rotation.z = Math.PI / 2; tri.add(band);
  const tower = new THREE.Mesh(new THREE.BoxGeometry(5, 4, 3), std(0xc9ced4)); tower.position.y = 6; tri.add(tower);
  const gon = new THREE.Mesh(new THREE.SphereGeometry(3.4, 40, 24), std(0x2b2f36, { metalness: .6, roughness: .35 })); gon.position.y = -7.5; tri.add(gon);
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 3, 16), std(0x444a52)); neck.position.y = -4.6; tri.add(neck);
  const win = new THREE.Mesh(new THREE.CircleGeometry(.8, 24), new THREE.MeshBasicMaterial({ color: 0xffd36b })); win.position.set(0, -7.5, 3.45); tri.add(win);
  const sl = new THREE.SpotLight(0xfff1c9, 1500, 80, .55, .5, 1.2); sl.position.set(0, -10, 0); tri.add(sl); sl.target.position.set(0, -40, 0); tri.add(sl.target);
  const dust = snow(600, [50, 6, 50], 0xb8a88a, .55); dust.material.opacity = 0; s.add(dust);
  const sp = snow(900, [120, 80, 80], 0xbfd9ff, .25); s.add(sp);
  return t => {
    const k = ease(prog(t, 27.9, 3.1)); tri.position.set(0, lerp(60, 12, k), 0); tri.rotation.y = -1.0 + (t - 27.9) * .06;
    const dk = prog(t, 31.0, 1.5); dust.material.opacity = .8 * Math.sin(Math.PI * dk); dust.scale.set(1 + dk * 1.5, 1 + dk, 1 + dk * 1.5); dust.position.y = 2 + dk * 3;
    S.timerMin = Math.round(lerp(0, 20, prog(t, 31.1, 1.9)));
    cam.position.set(46, lerp(62, 22, k), 66); cam.lookAt(0, lerp(52, 10, k) + 6, 0); sp.position.y = t * 2 % 20;
  };
} });

// H: sıradaki soru: asansör
shots.push({ t0: 33.4, t1: 99, build: (s, cam, S) => {
  s.background = gradTex('#0b2347', '#01050d'); s.fog = new THREE.Fog(0x04102a, 40, 140);
  s.add(new THREE.AmbientLight(0x6688bb, .8));
  const k = new THREE.SpotLight(0xffffff, 1500, 140, .5, .5, 1.2); k.position.set(-20, 50, 40); s.add(k);
  const shaft = new THREE.Group(); s.add(shaft);
  const rail = std(0x5b6573, { metalness: .6 });
  [-9, 9].forEach(x => { const r = new THREE.Mesh(new THREE.BoxGeometry(.8, 200, .8), rail); r.position.set(x, 0, -5); shaft.add(r); });
  for (let y = -90; y < 90; y += 12) { const b = new THREE.Mesh(new THREE.BoxGeometry(19, .5, .5), rail); b.position.set(0, y, -5); shaft.add(b); }
  const car = new THREE.Group(); s.add(car);
  car.add(new THREE.Mesh(new THREE.BoxGeometry(14, 18, 12), std(0xb9c2cc, { metalness: .7, roughness: .3 })));
  const d1 = new THREE.Mesh(new THREE.BoxGeometry(5.6, 14, .4), std(0x8f9aa6, { metalness: .8, roughness: .25 })); d1.position.set(-2.9, -1, 6.1); car.add(d1);
  const d2 = d1.clone(); d2.position.x = 2.9; car.add(d2);
  const lamp = new THREE.Mesh(new THREE.BoxGeometry(6, .6, .6), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); lamp.position.set(0, 8.4, 6.2); car.add(lamp);
  const cabT = new THREE.Mesh(new THREE.CylinderGeometry(.35, .35, 100, 8), std(0x30343a)); s.add(cabT);
  const cabB = new THREE.Mesh(new THREE.CylinderGeometry(.35, .35, 6, 8), std(0x30343a)); s.add(cabB);
  return t => {
    const snap = 35.75; const after = t - snap;
    const fall = after > 0 ? Math.min(14, 9 * after * after) : 0;
    const shake = after > 0 && after < .5 ? Math.sin(after * 80) * .6 : 0;
    car.position.set(shake, 6 - fall, 0); car.rotation.z = after > 0 ? Math.sin(after * 6) * .04 : Math.sin(t * 1.3) * .01;
    cabB.position.set(0, car.position.y + 9 + 3, 0);
    cabT.position.set(0, (after > 0 ? 70 + after * 30 : 15 + 50), 0);
    const cy = lerp(10, 0, prog(t, 33.4, 3));
    cam.position.set(Math.sin(t * .25) * 14, cy, 62); cam.lookAt(0, cy - 2, 0);
  };
} });


const titles = [
  { t0: 0, t1: 3.6, html: `<div class="grad"></div><div class="tagw"><span class="tag">OKYANUSUN EN DERİNİ</span></div><div class="title">MARİANA <span class="y">ÇUKURU</span></div>` },
  { t0: 3.6, t1: 8.4, html: `<div class="grad"></div><div class="tagw"><span class="tag">DERİNLİK</span></div><div class="big" style="top:330px" id="dep"></div>` },
  { t0: 8.4, t1: 12.6, html: `<div class="grad"></div><div class="tagw"><span class="tag">KARŞILAŞTIRMA</span></div><div class="title">EVEREST <span class="y">SIĞAR</span></div>
     <div class="sub" id="evl" style="top:1170px;color:#fff">EVEREST · 8.849 m</div><div class="sub" id="wl" style="top:540px;color:#ffcf2e">+2.086 m SU</div>` },
  { t0: 12.6, t1: 15.7, html: `<div class="grad"></div><div class="tagw"><span class="tag">BASINÇ</span></div><div class="big" style="top:330px" id="pr">1.000<small>KAT</small></div>` },
  { t0: 15.7, t1: 21.8, html: `<div class="grad"></div><div class="tagw"><span class="tag">GÜNEŞ IŞIĞI YOK</span></div><div class="title">ZİFİRİ <span class="y">KARANLIK</span></div><div class="big" style="top:520px;font-size:150px" id="tc"></div>` },
  { t0: 21.8, t1: 27.9, html: `<div class="grad"></div><div class="tagw"><span class="tag">DİPTE NE VAR?</span></div><div class="list">
     <div class="row" id="r1">SAYDAM BALIKLAR <i>8.000 m</i></div><div class="row" id="r2">DEV TEK HÜCRELİLER <i>20 cm</i></div><div class="row" id="r3">PLASTİK POŞET <i>10.898 m</i></div></div>` },
  { t0: 27.9, t1: 33.4, html: `<div class="grad"></div><div class="tagw"><span class="tag">1960 · TRIESTE</span></div><div class="title">İLK <span class="y">İNİŞ</span></div><div class="big" style="top:500px;font-size:160px" id="tm"></div>` },
  { t0: 33.4, t1: 99, html: `<div class="grad"></div><div class="tagw"><span class="tag">SIRADAKİ SORU</span></div><div class="title" style="font-size:96px">ASANSÖRÜN HALATI <span class="y">KOPARSA?</span></div>
     <div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
];

return {
  END: 38.75, state: { depthM: 0, tempC: 20, timerMin: 0 }, shots, titles,
  follow: { t: 36.9, click: 37.85 },
  sfx: [[1.0, 'boom', .7], [14.2, 'crunch', 1], [14.25, 'pop_low', 1], [23.5, 'pop', 1], [24.75, 'pop', 1], [26.8, 'pop', 1], [31.0, 'boom', .8], [35.75, 'snap', 1], [35.8, 'boom', .9]],
  update(t, q, S) {
  if (q('dep')) q('dep').innerHTML = S.depthM.toLocaleString('tr-TR') + '<small>m</small>';
  if (q('evl')) { q('evl').style.opacity = prog(t, 9.4, .4); q('wl').style.opacity = prog(t, 10.4, .4); }
  if (q('pr')) { const k = back(prog(t, 14.2, .5)); q('pr').style.transform = `scale(${Math.max(.01, k)})`; q('pr').style.opacity = prog(t, 14.2, .2); }
  if (q('tc')) { q('tc').innerHTML = t > 18.9 ? (t > 20.5 ? '1–4 °C' : S.tempC + ' °C') : ''; }
  [['r1', 23.5], ['r2', 24.75], ['r3', 26.8]].forEach(([id, s]) => { const e = q(id); if (!e) return; const k = easeOut(prog(t, s, .35)); e.style.opacity = k; e.style.transform = `translateX(${(1 - k) * -60}px)`;
    e.classList.toggle('hl', t >= s && t < s + 1.25); });
  if (q('tm')) { q('tm').innerHTML = t > 29.1 ? (t > 31.0 ? `${S.timerMin} DK` : '1960') : ''; }
  },
};
};
