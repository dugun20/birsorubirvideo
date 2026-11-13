// Bilgi #11: Uzayda kasksız kalsan ne olur? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: aerospaceweb.org "Human Exposure to the Vacuum of Space" (vücut patlamaz, deri ve doku sıvıları bir arada tutar;
// nefes tutmak akciğer yırtılmasına yol açabilir; dildeki tükürük kaynayabilir; dokulardaki su buharlaşır, vücut 2 katına kadar şişebilir;
// anında donmaz, ısı yavaş kaybolur; bilinç 10–15 sn; 90 sn içinde yeniden basınçlandırılırsa kurtulma mümkün).
// Live Science "What would happen to the human body in the vacuum of space?" (1966 NASA testi, Jim LeBlanc: "dilimdeki tükürüğün
// köpürdüğünü hissettim"; filmlerdeki gibi patlama yok).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 211; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
    s.background = gradTex(...(o.bg || ['#0d2240', '#02060e'])); s.fog = new THREE.Fog(o.fog || 0x050d1c, o.near || 40, o.far || 140);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x0a0a12, o.hemi || .9));
    const key = new THREE.SpotLight(0xfff1dc, o.key || 2000, 160, .45, .55, 1.2); key.position.set(-18, 44, 34); s.add(key); s.add(key.target);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 700, 90); rim.position.set(20, 16, -14); s.add(rim);
    return key;
  }
  function space(s, o = {}) { // uzay arka planı + yıldızlar (+ isteğe bağlı Dünya)
    s.background = gradTex('#060b1a', '#000000'); s.fog = new THREE.Fog(0x000000, 80, 300);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi || .5));
    const sun = new THREE.DirectionalLight(0xfff4e0, 3); sun.position.set(-10, 8, 10); s.add(sun);
    const rim = new THREE.PointLight(o.rim || 0x3fb6ff, 600, 60); rim.position.set(8, 6, -6); s.add(rim);
    const stars = dust(1500, [140, 140, 40], 0xffffff, .25, .9); stars.position.z = -45; s.add(stars);
    let E = null;
    if (o.earth) { const ec = []; const eg = new THREE.SphereGeometry(14, 96, 64); const P = eg.attributes.position;
      const cO = new THREE.Color(0x1a4f9a), cL = new THREE.Color(0x3f7a3a), cC = new THREE.Color(0xf4f8ff);
      for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i); const n = hash(x * .25, y * .25, z * .25) + .4 * hash(x * .7, z * .7, y * .7); const cc = (n > .55 ? cL : cO).clone(); if (hash(x * .5 + 3, y * .5, z * .5 + 1) > 1.0) cc.lerp(cC, .8); ec.push(cc.r, cc.g, cc.b); }
      eg.setAttribute('color', new THREE.Float32BufferAttribute(ec, 3)); E = M(eg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .7 })); E.position.set(0, -12, -10); s.add(E);
      const atm = M(new THREE.SphereGeometry(14.5, 64, 48), new THREE.MeshBasicMaterial({ color: 0x4aa8ff, transparent: true, opacity: .18, side: THREE.BackSide })); atm.position.copy(E.position); s.add(atm); }
    return { stars, E, sun };
  }
  const skinM = () => std(0xd9b49a, { roughness: .6 });
  function astronaut(o = {}) {
    const g = new THREE.Group(); const suit = std(0xeef1f5, { roughness: .6 }); const dk = std(0x3a4250, { metalness: .4, roughness: .5 });
    const body = M(new THREE.CapsuleGeometry(.75, 1.1, 10, 24), suit); g.add(body);
    const pack = M(rb(1.4, 1.7, .7, .15), std(0xd8dce2)); pack.position.set(0, .2, -.8); g.add(pack);
    const panel = M(rb(.8, .5, .2, .06), dk); panel.position.set(0, .35, .72); g.add(panel);
    [0xff3b30, 0x2ad15a, 0x3fb6ff].forEach((c, i) => { const b = M(new THREE.SphereGeometry(.07, 12, 8), new THREE.MeshBasicMaterial({ color: c })); b.position.set(-.2 + i * .2, .35, .84); g.add(b); });
    const ring = M(new THREE.TorusGeometry(.5, .12, 12, 32), dk); ring.rotation.x = Math.PI / 2; ring.position.y = 1.35; g.add(ring);
    const head = M(new THREE.SphereGeometry(.5, 32, 24), skinM()); head.position.y = 1.85; g.add(head);
    const hair = M(new THREE.SphereGeometry(.52, 32, 16, 0, Math.PI * 2, 0, Math.PI * .45), std(0x2a1c14, { roughness: .8 })); hair.position.y = 1.88; hair.rotation.x = -.3; g.add(hair);
    const eyes = []; [-1, 1].forEach(k => { const e = M(new THREE.SphereGeometry(.07, 12, 8), new THREE.MeshBasicMaterial({ color: 0x111111 })); e.position.set(k * .17, 1.92, .45); g.add(e); eyes.push(e); });
    const mouth = M(new THREE.SphereGeometry(.09, 16, 8), new THREE.MeshBasicMaterial({ color: 0x5a1a1a })); mouth.scale.set(1.4, .5, .5); mouth.position.set(0, 1.66, .46); g.add(mouth);
    const helmet = new THREE.Group(); helmet.position.y = 1.85; g.add(helmet);
    helmet.add(M(new THREE.SphereGeometry(.92, 48, 32), new THREE.MeshPhysicalMaterial({ color: 0xbfe0ff, roughness: .05, metalness: .2, transparent: true, opacity: .28, depthWrite: false })));
    const hr = M(new THREE.TorusGeometry(.62, .1, 12, 40), dk); hr.rotation.x = Math.PI / 2; hr.position.y = -.5; helmet.add(hr);
    helmet.visible = !!o.helmet;
    const limbs = [];
    [-1, 1].forEach(k => { const a = new THREE.Group(); a.position.set(k * .85, .8, 0); g.add(a); const m = M(new THREE.CapsuleGeometry(.24, .9, 8, 16), suit); m.position.y = -.55; a.add(m);
      const gl = M(new THREE.SphereGeometry(.26, 16, 12), dk); gl.position.y = -1.15; a.add(gl); limbs.push(a);
      const l = new THREE.Group(); l.position.set(k * .38, -1.1, 0); g.add(l); const lm = M(new THREE.CapsuleGeometry(.3, 1.1, 8, 16), suit); lm.position.y = -.7; l.add(lm);
      const bt = M(rb(.6, .4, .8, .1), dk); bt.position.set(0, -1.45, .1); l.add(bt); limbs.push(l); });
    g.userData = { limbs, helmet, head, eyes, mouth, body }; return g;
  }
  function arrow(len, col) {
    const g = new THREE.Group(); const m = new THREE.MeshBasicMaterial({ color: col });
    const sh = M(new THREE.CylinderGeometry(.1, .1, 1, 16), m); g.add(sh); const hd = M(new THREE.ConeGeometry(.26, .5, 24), m); g.add(hd);
    g.userData.set = l => { l = Math.max(.01, l); sh.scale.y = l; sh.position.y = l / 2; hd.position.y = l + .25; }; g.userData.set(len); return g;
  }
  const dm = new THREE.Object3D();
  function bubbles(n, sp, col = 0xdff4ff) { const g = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 16, 12), new THREE.MeshPhysicalMaterial({ color: col, emissive: 0x4aa0d0, emissiveIntensity: .25, transparent: true, opacity: .75, roughness: .05 }), n);
    const bs = []; for (let i = 0; i < n; i++) bs.push([(r1() - .5) * sp[0], r1(), (r1() - .5) * sp[2], .05 + r1() * .12]); g.userData.bs = bs; g.userData.h = sp[1]; return g; }
  function updBub(B, t, sp = .3, on = 1) { const { bs, h } = B.userData; bs.forEach(([x, f0, z, s], i) => { const f = (f0 + t * sp) % 1; dm.position.set(x, f * h, z); dm.scale.setScalar(Math.max(.001, s * on * Math.sin(f * Math.PI))); dm.updateMatrix(); B.setMatrixAt(i, dm.matrix); }); B.instanceMatrix.needsUpdate = true; }

  const S1 = 3.24, S2 = 4.0, S3 = 6.84, S3b = 8.96, S4 = 11.52, S5 = 14.52, S6 = 18.37, S7 = 20.92, S8 = 24.48, S9 = 28.52, S10 = 31.39;

  // 1) Dünya üstünde astronot, kaskı fırlar
  shots.push({ t0: 0, t1: S2, fov: 40, build: (s, cam) => {
    const { stars, E } = space(s, { earth: true });
    const A = astronaut({ helmet: true }); A.scale.setScalar(.8); s.add(A);
    const H = A.userData.helmet; const air = dust(160, [1.5, 1.5, 1.5], 0xcfefff, .2, .9); s.add(air);
    return t => {
      E.rotation.y = t * .03; stars.rotation.z = t * .01;
      A.position.set(Math.sin(t * .4) * .3, 6.6 + Math.sin(t * .8) * .12, 0); A.rotation.set(Math.sin(t * .5) * .15, -.3 + t * .12, .1);
      A.userData.limbs.forEach((l, i) => l.rotation.x = Math.sin(t * 1.2 + i) * .3);
      const off = easeOut(prog(t, 1.0, 2.6));
      if (off > 0) { A.remove(H); s.add(H); H.position.set(A.position.x + off * 2.0, A.position.y + 1.5 + off * 1.6, off * 1.5); H.rotation.set(off * 4, off * 3, 0); } else { if (H.parent !== A) { s.remove(H); A.add(H); } H.position.set(0, 1.85, 0); }
      const ak = prog(t, 1.0, 1.2); air.visible = ak > 0 && ak < 1; air.position.set(A.position.x, A.position.y + 1.5, .3); air.scale.setScalar(.3 + ak * 4); air.material.opacity = .9 * (1 - ak);
      cam.position.set(Math.sin(t * .2) * 1, 6.0, lerp(17, 15, t / S2)); cam.lookAt(0, 6.6, 0); };
  } });
  // 2) Patlamaz: deri torba gibi tutar (içe doğru oklar)
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const { stars } = space(s, { rim: 0xffcf2e });
    const A = astronaut(); A.scale.setScalar(.9); s.add(A);
    const shell = M(new THREE.CapsuleGeometry(1.2, 2.6, 16, 32), new THREE.MeshBasicMaterial({ color: 0xffcf2e, wireframe: true, transparent: true, opacity: .35 })); s.add(shell);
    const arrs = []; for (let i = 0; i < 8; i++) { const a = arrow(.7, 0xffcf2e); s.add(a); arrs.push(a); }
    return t => {
      const a = t - S2; stars.rotation.z = t * .01;
      A.position.set(0, 6.4 + Math.sin(t * .8) * .1, 0); A.rotation.set(0, Math.sin(t * .4) * .5, 0);
      A.userData.limbs.forEach((l, i) => l.rotation.x = Math.sin(t * 1.2 + i) * .25);
      const k = easeOut(prog(a, .2, .8)); shell.position.set(0, 6.9, 0); shell.scale.setScalar(Math.max(.01, k * .85 * (1 + .03 * Math.sin(t * 6)))); shell.rotation.y = t * .3; shell.visible = k > 0;
      arrs.forEach((ar, i) => { const ang = i / 8 * Math.PI * 2 + t * .2; const kk = easeOut(prog(a, .4 + i * .08, .5)); ar.visible = kk > 0;
        const rr = 2.5 - .25 * Math.sin(t * 5 + i); ar.position.set(Math.cos(ang) * rr, 6.9 + Math.sin(ang) * rr * 1.15, .5); ar.rotation.z = ang + Math.PI / 2; ar.userData.set(.6 * kk); });
      cam.position.set(Math.sin(a * .3) * 2, 7.6, 19.5); cam.lookAt(0, 7.6, 0); };
  } });
  // 3) Akciğerler: hava dışarı kaçar; nefes tutarsan yırtılır
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    lights(s, { key: 1700, rim: 0xff4a3a, bg: ['#1a0d24', '#030208'] });
    const G = new THREE.Group(); G.position.set(0, 6.2, 0); s.add(G);
    const torso = M(new THREE.CapsuleGeometry(1.9, 2.4, 16, 48), new THREE.MeshPhysicalMaterial({ color: 0xd9b49a, roughness: .5, transparent: true, opacity: .18, depthWrite: false })); G.add(torso);
    const lungM = new THREE.MeshPhysicalMaterial({ color: 0xe86a7a, roughness: .45, clearcoat: .4, emissive: 0x3a0510, emissiveIntensity: .4 });
    const lungs = [-1, 1].map(k => { const l = M(new THREE.SphereGeometry(1, 48, 32), lungM); l.scale.set(.75, 1.25, .6); l.position.set(k * .85, .1, 0); G.add(l); return l; });
    const tr = M(new THREE.CylinderGeometry(.16, .16, 1.8, 24), std(0xe9c0b0)); tr.position.set(0, 1.9, 0); G.add(tr);
    [-1, 1].forEach(k => { const b = M(new THREE.CylinderGeometry(.12, .12, .9, 16), std(0xe9c0b0)); b.position.set(k * .35, 1.05, 0); b.rotation.z = k * .7; G.add(b); });
    const out = dust(220, [1, 3, 1], 0xbfe8ff, .25, .9); s.add(out);
    const warn = M(new THREE.TorusGeometry(2.6, .07, 12, 64), new THREE.MeshBasicMaterial({ color: 0xff3b30, transparent: true, opacity: .8 })); warn.position.set(0, 6.3, .5); s.add(warn);
    const bg = dust(400, [30, 30, 20], 0xffc0c0, .12, .35); bg.position.y = 6; s.add(bg);
    return t => {
      const hold = prog(t, S3b + .2, 1.6);
      const exhale = t < S3b ? 1 - .25 * prog(t, S3 + .3, 1.6) : .75;
      lungs.forEach((l, i) => { const sw = exhale + hold * .45 + (hold > .9 ? .04 * Math.sin(t * 30) : 0); l.scale.set(.75 * sw, 1.25 * sw, .6 * sw); });
      lungM.emissive.setHex(hold > 0 ? 0x8a0a0a : 0x3a0510); lungM.emissiveIntensity = .4 + hold * .8 * (.6 + .4 * Math.sin(t * 10));
      const ok = t < S3b + .1; out.visible = ok; const f = ((t - S3) * .8) % 1; out.position.set(0, 6.2 + 3 + f * 3, 0); out.scale.setScalar(.6 + f * 1.5); out.material.opacity = .9 * (1 - f);
      warn.visible = hold > 0; warn.scale.setScalar(.9 + .1 * Math.sin(t * 8)); warn.material.opacity = .8 * hold;
      G.rotation.y = Math.sin(t * .4) * .3; bg.rotation.y = t * .03;
      cam.position.set(0, 6.9, 20.5); cam.lookAt(0, 6.9, 0); };
  } });
  // 4) Basınç yok: dildeki tükürük kaynar
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    lights(s, { key: 1800, rim: 0x7ee0ff, bg: ['#1a1030', '#03030a'] });
    const G = new THREE.Group(); G.position.set(0, 5.6, 0); s.add(G);
    const jawM = std(0xb85a5a, { roughness: .5 });
    const low = M(new THREE.SphereGeometry(2.2, 48, 24, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), jawM); low.scale.set(1, .45, .9); G.add(low);
    const tongue = M(new THREE.SphereGeometry(1, 48, 32), new THREE.MeshPhysicalMaterial({ color: 0xe0707a, roughness: .35, clearcoat: .8, clearcoatRoughness: .2 })); tongue.scale.set(1.3, .35, 1.6); tongue.position.y = -.2; G.add(tongue);
    const teeth = []; for (let i = 0; i < 12; i++) { const a = Math.PI * (.1 + .8 * i / 11); const th = M(rb(.32, .4, .28, .1), std(0xf5f0e6, { roughness: .3 })); th.position.set(Math.cos(a) * 1.95, .1, Math.sin(a) * 1.75 - .2); th.rotation.y = -a; G.add(th); teeth.push(th); }
    const B = bubbles(70, [2, 1.6, 2.4]); B.position.set(0, .05, 0); G.add(B);
    const vap = dust(240, [2.4, 3, 2.4], 0xffffff, .3, .5); G.add(vap);
    const gauge = new THREE.Group(); gauge.position.set(0, 9.3, -1); s.add(gauge);
    gauge.add(M(new THREE.CylinderGeometry(1, 1, .25, 48), std(0x1a2230, { metalness: .7 })).rotateX(Math.PI / 2));
    const face = M(new THREE.CircleGeometry(.85, 48), new THREE.MeshBasicMaterial({ color: 0xe8edf2 })); face.position.z = .14; gauge.add(face);
    const nd = M(new THREE.BoxGeometry(.06, .75, .04), new THREE.MeshBasicMaterial({ color: 0xff3b30 })); nd.geometry.translate(0, .35, 0); nd.position.z = .18; gauge.add(nd);
    gauge.visible = false;
    return t => {
      const a = t - S4; const boil = prog(a, .6, 1.2);
      updBub(B, t, .9, boil); vap.visible = boil > 0; vap.position.y = 1 + ((t * .6) % 1); vap.material.opacity = .5 * boil;
      tongue.position.y = -.2 + Math.sin(t * 9) * .02 * boil;
      G.rotation.set(.55, Math.sin(t * .3) * .25, 0);
      cam.position.set(0, 7.6, 14); cam.lookAt(0, 5.6, 0); };
  } });
  // 5) Gerçek olay: NASA vakum odası
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    lights(s, { key: 1800, rim: 0xff4a3a });
    const ch = new THREE.Group(); ch.position.set(0, 4.6, 0); s.add(ch);
    const shellM = std(0x8e99a6, { metalness: .85, roughness: .3, side: THREE.DoubleSide });
    const cyl = M(new THREE.CylinderGeometry(3, 3, 6, 64, 1, true, Math.PI * .15, Math.PI * 1.7), shellM); ch.add(cyl);
    const capT = M(new THREE.SphereGeometry(3, 64, 24, 0, Math.PI * 2, 0, Math.PI / 2), shellM); capT.position.y = 3; ch.add(capT);
    const fl = M(new THREE.CylinderGeometry(3, 3, .3, 64), std(0x2a2f36, { metalness: .6 })); fl.position.y = -3; ch.add(fl);
    for (let i = -1; i <= 1; i++) { const r = M(new THREE.TorusGeometry(3.05, .12, 12, 64), std(0x5d646d, { metalness: .9, roughness: .3 })); r.rotation.x = Math.PI / 2; r.position.y = i * 2.2; ch.add(r); }
    const A = astronaut({ helmet: true }); A.scale.setScalar(.75); A.position.set(0, -1.2, 0); ch.add(A);
    const hose = M(new THREE.CylinderGeometry(.08, .08, 1.6, 12), std(0x222222)); ch.add(hose);
    const leak = dust(120, [.6, .6, .6], 0xcfefff, .2, .9); ch.add(leak);
    const alarm = new THREE.PointLight(0xff2a1a, 0, 30); alarm.position.set(0, 9, 6); s.add(alarm);
    const bulb = M(new THREE.SphereGeometry(.35, 24, 16), new THREE.MeshBasicMaterial({ color: 0xff2a1a })); bulb.position.set(0, 8.2, 0); s.add(bulb);
    const d = dust(400, [30, 30, 20], 0xcfe8ff, .12, .45); d.position.y = 5; s.add(d);
    return t => {
      const a = t - S5; const disc = prog(a, .9, .5);
      hose.position.set(.9 + disc * .8, -.1 - disc * 1.2, .3); hose.rotation.z = .8 + disc * 1.2;
      leak.visible = disc > 0 && a < 3.2; leak.position.set(.9, .2, .5); leak.scale.setScalar(.5 + ((a * 1.5) % 1) * 2.5); leak.material.opacity = .9 * (1 - ((a * 1.5) % 1));
      alarm.intensity = disc > 0 ? 500 * (.5 + .5 * Math.sin(t * 9)) : 0; bulb.material.color.setHex(disc > 0 && Math.sin(t * 9) > 0 ? 0xff2a1a : 0x441010);
      const sag = ease(prog(a, 2.6, 1.2)); A.rotation.set(sag * .5, .4 + Math.sin(t * .4) * .1, sag * .3); A.position.y = -1.2 - sag * .3;
      A.userData.limbs.forEach((l, i) => l.rotation.x = (1 - sag) * Math.sin(t * 3 + i) * .4 + sag * (i % 2 ? .2 : -.4));
      ch.rotation.y = -.5 + a * .06; d.rotation.y = t * .04;
      cam.position.set(Math.sin(a * .2) * 1, 6.8, 29); cam.lookAt(0, 5.8, 0); };
  } });
  // 6) Dokulardaki su buharlaşır, vücut şişer
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const { stars } = space(s, { rim: 0xffcf2e });
    const A = astronaut(); A.scale.setScalar(.85); s.add(A);
    const vap = dust(300, [3, 4, 2], 0xffffff, .2, .6); s.add(vap);
    return t => {
      const a = t - S6; const sw = ease(prog(a, .5, 1.8)); stars.rotation.z = t * .01;
      A.position.set(0, 6.1 + Math.sin(t * .8) * .1, 0); A.rotation.set(.1, -.4 + Math.sin(t * .3) * .3, .05);
      A.userData.body.scale.set(1 + sw * .35, 1 + sw * .12, 1 + sw * .35); A.userData.head.scale.setScalar(1 + sw * .22);
      A.userData.limbs.forEach((l, i) => { l.scale.set(1 + sw * .4, 1, 1 + sw * .4); l.rotation.z = (i % 2 ? 1 : -1) * sw * .25 * (i < 2 ? 1 : .5); l.rotation.x = Math.sin(t + i) * .15; });
      vap.position.set(0, 6.8 + ((t * .3) % 1), 0); vap.rotation.y = t * .2; vap.material.opacity = .5 * prog(a, .3, .6);
      cam.position.set(0, 6.6, 14); cam.lookAt(0, 6.7, 0); };
  } });
  // 7) Anında donmazsın: termometre yavaş düşer
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const { stars, E } = space(s, { earth: true, rim: 0x7ee0ff });
    const A = astronaut(); A.scale.setScalar(.7); s.add(A);
    const th = new THREE.Group(); th.position.set(1.8, 6.7, .5); th.scale.setScalar(.75); s.add(th);
    th.add(M(new THREE.CylinderGeometry(.32, .32, 4, 32), new THREE.MeshPhysicalMaterial({ color: 0xeaf6ff, transparent: true, opacity: .3, roughness: .05, depthWrite: false })));
    const bulbT = M(new THREE.SphereGeometry(.55, 32, 24), new THREE.MeshStandardMaterial({ color: 0xff3b30, emissive: 0xaa1a10, emissiveIntensity: .8 })); bulbT.position.y = -2.2; th.add(bulbT);
    const liq = M(new THREE.CylinderGeometry(.18, .18, 1, 24), new THREE.MeshStandardMaterial({ color: 0xff3b30, emissive: 0xaa1a10, emissiveIntensity: .8 })); th.add(liq);
    const heat = dust(120, [1.6, 2.6, 1], 0xff9a5a, .25, .7); s.add(heat);
    return t => {
      const a = t - S7; E.rotation.y = t * .03; stars.rotation.z = t * .01;
      A.position.set(-.9, 6.5 + Math.sin(t * .8) * .12, 0); A.rotation.set(Math.sin(t * .5) * .2, .4 + t * .1, .15);
      A.userData.limbs.forEach((l, i) => l.rotation.x = Math.sin(t * 1.2 + i) * .3);
      const lv = 3.4 - a * .12; liq.scale.y = lv; liq.position.y = -2.2 + lv / 2;
      heat.position.set(-.9, 7 + ((t * .25) % 1) * 1.2, 0); heat.material.opacity = .5 * (1 - ((t * .25) % 1));
      th.rotation.y = Math.sin(t * .6) * .3;
      cam.position.set(0, 6.4, lerp(15, 14, a / 3.5)); cam.lookAt(0, 6.5, 0); };
  } });
  // 8) Oksijensizlik: 15 saniyede bayılırsın — O2 molekülleri kaybolur
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    const { stars } = space(s, { rim: 0xff4a3a, hemi: .6 });
    const A = astronaut(); A.scale.setScalar(.75); s.add(A);
    const o2 = []; const om = new THREE.MeshStandardMaterial({ color: 0xff4a4a, emissive: 0x6a0a0a, roughness: .3 });
    for (let i = 0; i < 14; i++) { const g = new THREE.Group(); [-1, 1].forEach(k => { const b = M(new THREE.SphereGeometry(.22, 24, 16), om); b.position.x = k * .2; g.add(b); });
      const ang = r1() * Math.PI * 2, rr = 1.8 + r1() * 1.2; g.userData = { ang, rr, h: (r1() - .5) * 3, sp: .2 + r1() * .3 }; s.add(g); o2.push(g); }
    return t => {
      const a = t - S8; stars.rotation.z = t * .01; const faint = ease(prog(a, 2.6, 1.2));
      A.position.set(0, 6.2 + Math.sin(t * .8) * .1, 0); A.rotation.set(faint * .6, .3 + Math.sin(t * .3) * .2, faint * .5);
      A.userData.eyes.forEach(e => e.scale.y = Math.max(.1, 1 - faint)); A.userData.limbs.forEach((l, i) => l.rotation.x = (1 - faint) * Math.sin(t * 2 + i) * .4 + faint * .3);
      o2.forEach((g, i) => { const { ang, rr, h, sp } = g.userData; const k = clamp(1 - prog(a, .5 + i * .14, .4)); g.visible = k > .01; g.scale.setScalar(Math.max(.01, k));
        const an = ang + t * sp; g.position.set(Math.cos(an) * rr, 6.8 + h, Math.sin(an) * rr); g.rotation.set(t, t * .7, 0); });
      cam.position.set(0, 6.4, lerp(14, 12.5, ease(prog(a, 0, 4)))); cam.lookAt(0, 6.6, 0); };
  } });
  // 9) 90 saniye içinde kurtarılırsan: hava kilidine çekilir
  shots.push({ t0: S9, t1: S10, fov: 40, build: (s, cam) => {
    const { stars } = space(s, { rim: 0x2ad15a });
    const st = new THREE.Group(); st.position.set(0, 6.4, -2); s.add(st);
    const mod = M(new THREE.CylinderGeometry(2.6, 2.6, 7, 64), std(0xd8dce2, { metalness: .5, roughness: .35 })); mod.rotation.z = Math.PI / 2; st.add(mod);
    [-1, 1].forEach(k => { const p = M(rb(4.5, .1, 2, .03), std(0x1d3a8a, { metalness: .6, roughness: .3, emissive: 0x0a1a4a })); p.position.set(k * 6, 0, 0); st.add(p); });
    const hatch = M(new THREE.CylinderGeometry(1.3, 1.3, .3, 48), std(0x3a4250, { metalness: .6 })); hatch.rotation.x = Math.PI / 2; hatch.position.set(0, 0, 2.62); st.add(hatch);
    const door = new THREE.Group(); door.position.set(1.3, 0, 2.8); st.add(door);
    const dm2 = M(new THREE.CylinderGeometry(1.2, 1.2, .2, 48), std(0x9aa3ad, { metalness: .8 })); dm2.rotation.x = Math.PI / 2; dm2.position.x = -1.3; door.add(dm2);
    const lamp = M(new THREE.SphereGeometry(.25, 24, 16), new THREE.MeshBasicMaterial({ color: 0xff3b30 })); lamp.position.set(0, 1.8, 2.7); st.add(lamp);
    const gl = new THREE.PointLight(0x2ad15a, 0, 14); gl.position.set(0, 7.8, 3); s.add(gl);
    const A = astronaut(); A.scale.setScalar(.55); s.add(A);
    return t => {
      const a = t - S9; stars.rotation.z = t * .01;
      const pull = ease(prog(a, .3, 1.8)); door.rotation.y = lerp(-1.6, -1.6, 0) * (1 - ease(prog(a, 2.0, .6)));
      A.position.set(lerp(2.2, 0, pull), lerp(5.4, 6.4, pull), lerp(4.5, .5, pull)); A.rotation.set(.3, -.6 + pull * .6, .4 * (1 - pull)); A.visible = pull < .98;
      A.userData.limbs.forEach((l, i) => l.rotation.x = .2 + Math.sin(i) * .2);
      const ok = a > 2.5; lamp.material.color.setHex(ok ? 0x2ad15a : 0xff3b30); gl.intensity = ok ? 300 : 0;
      st.rotation.y = -.25 + Math.sin(t * .2) * .08;
      cam.position.set(1.5, 7.4, 26); cam.lookAt(0, 6.6, 0); };
  } });
  // 10) Sıradaki soru: deprem — fay üstünde sallanan şehir bloğu
  shots.push({ t0: S10, t1: 99, fov: 40, build: (s, cam) => {
    lights(s, { key: 1900, rim: 0xff7a1a, bg: ['#24140a', '#050302'], fog: 0x0a0604 });
    const G = new THREE.Group(); G.position.set(0, 3.2, 0); s.add(G);
    const blocks = [-1, 1].map(k => { const b = new THREE.Group(); b.position.x = k * 2.05; G.add(b);
      const crust = M(rb(4, 1.6, 5, .1), std(0x6b4a32, { roughness: .9 })); crust.position.y = -.8; b.add(crust);
      const soil = M(rb(4, .3, 5, .08), std(0x3d5a2a, { roughness: .9 })); soil.position.y = .1; b.add(soil);
      const mantle = M(rb(4, 1.4, 5, .1), std(0xb3541e, { roughness: .7, emissive: 0x5a1a00, emissiveIntensity: .6 })); mantle.position.y = -2.3; b.add(mantle);
      for (let i = 0; i < 3; i++) { const h = 1 + r1() * 1.6; const bl = M(rb(.8, h, .8, .06), std(0x9aa3ad, { metalness: .3, roughness: .6 })); bl.position.set((r1() - .5) * 2.6, .25 + h / 2, (r1() - .5) * 3); b.add(bl);
        for (let w = 0; w < 3; w++) { const wn = M(new THREE.PlaneGeometry(.18, .22), new THREE.MeshBasicMaterial({ color: 0xffd27a })); wn.position.set(bl.position.x - .2 + w * .2, bl.position.y + h * .2, bl.position.z + .41); b.add(wn); } }
      return b; });
    const glow = new THREE.PointLight(0xff5a1a, 300, 12); glow.position.set(0, 1.5, 3); s.add(glow);
    const dd = dust(300, [10, 6, 6], 0xffc08a, .15, .5); dd.position.y = 4; s.add(dd);
    return t => {
      const a = t - S10; const sh = Math.sin(t * 24) * .06 * (.5 + .5 * Math.sin(t * 1.5));
      blocks[0].position.set(-2.05 + sh, 0, Math.sin(t * .6) * .3); blocks[1].position.set(2.05 - sh, 0, -Math.sin(t * .6) * .3);
      G.rotation.set(.2, -.5 + Math.sin(a * .3) * .15, 0); glow.intensity = 250 + 120 * Math.sin(t * 5); dd.rotation.y = t * .05;
      cam.position.set(0, 7.6, 25); cam.lookAt(0, 4.8, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'UZAYDA KASKSIZ<br><span class="y">PATLAR MISIN?</span>', 100) },
    { t0: S1, t1: S2, html: T('CEVAP', '<span class="y">HAYIR!</span>', 150) },
    { t0: S2, t1: S3, html: T('DERİN', 'SENİ BİR ARADA <span class="y">TUTAR</span>', 100) },
    { t0: S3, t1: S3b, html: T('CİĞERLERDEKİ HAVA', 'DIŞARI <span class="y">KAÇAR</span>') },
    { t0: S3b, t1: S4, html: T('SAKIN', 'NEFESİNİ <span class="y">TUTMA!</span>') },
    { t0: S4, t1: S5, html: T('BASINÇ YOK', 'TÜKÜRÜK <span class="y">KAYNAR</span>') },
    { t0: S5, t1: S6, html: T('GERÇEK OLAY', 'NASA <span class="y">VAKUM ODASI</span>', 100) },
    { t0: S6, t1: S7, html: BIG('VÜCUT ŞİŞER', 'k2', 'KATINA KADAR', '2') },
    { t0: S7, t1: S8, html: T('ISI YAVAŞ KAYBOLUR', 'ANINDA <span class="y">DONMAZSIN</span>', 100) },
    { t0: S8, t1: S9, html: BIG('ASIL TEHLİKE: OKSİJENSİZLİK', 'k15', 'SANİYEDE BAYILIRSIN', '15') },
    { t0: S9, t1: S10, html: BIG('KURTARILIRSAN', 'k90', 'SANİYE İÇİNDE YAŞARSIN', '90') },
    { t0: S10, t1: 99, html: T('SIRADAKİ SORU', 'DEPREM NASIL<br><span class="y">OLUŞUR?</span>', 104) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k2', S6], ['k15', S8], ['k90', S9]];
  return {
    END: 35.72, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; });
    },
    follow: { t: 33.92, click: 34.9 },
    sfx: [[1.0, 'pop', .8], [1.05, 'whoosh', .7], [S1 + .05, 'boom', .5], [4.6, 'ding', .5], [7.2, 'whoosh', .5], [9.2, 'pop_low', .7], [10.6, 'crunch', .5],
      [12.2, 'pop', .4], [12.6, 'pop', .4], [13.0, 'pop', .4], [S5 + .9, 'snap', .8], [S5 + 1.2, 'ding', .5], [19.0, 'pop_low', .6], [S8 + .5, 'click', .5], [27.3, 'boom', .4],
      [S9 + 2.5, 'ding', .7], [S10 + .3, 'boom', .6]],
  };
};
