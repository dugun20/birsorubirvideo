// Bilgi #14: Kara deliğe düşsen ne olur? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: NASA Goddard (J. Schnittman, Mayıs 2024) kara delik dalış simülasyonu, Universe Today / Live Science haberleri:
// simülasyondaki kara delik Sagittarius A* kütlesinde (~4,3 milyon Güneş kütlesi), kamera ufku geçtikten 12,8 saniye sonra
// spagettileşmeyle parçalanır; yıldız kütleli küçük kara deliklerde gelgit kuvvetleri cismi ufka varmadan parçalar.
// "Spagettileşme" gelgit kuvvetinin cismi uzatmasıdır (yakın uç daha güçlü çekilir). Olay ufkundan ışık bile kaçamaz.
// Dış gözlemci için düşen cisim ufka yaklaştıkça yavaşlar, kırmızıya kayar ve söner (genel görelilik, zaman genişlemesi).
// StarDate (McDonald Gözlemevi) Sagittarius A* bilgi kartı: ~4,1 milyon Güneş kütlesi.
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 1414; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const soft = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.4, 'rgba(255,255,255,.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
  function dust(n, sp, color = 0xcfe8ff, size = .2, op = .5, add = true) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
    for (let i = 0; i < n * 3; i += 3) { p[i] = (r1() - .5) * sp[0]; p[i + 1] = (r1() - .5) * sp[1]; p[i + 2] = (r1() - .5) * sp[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color, size, map: soft, transparent: true, opacity: op, depthWrite: false, blending: add ? THREE.AdditiveBlending : THREE.NormalBlending }));
  }
  function space(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#0a0820', '#000000'])); s.fog = new THREE.Fog(0x000000, 80, 300);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, o.hemi || .6));
    const sun = new THREE.DirectionalLight(0xfff4e0, o.sun || 2.4); sun.position.set(-10, 8, 10); s.add(sun);
    const rim = new THREE.PointLight(o.rim || 0xff8a2a, 700, 60); rim.position.set(0, 4, -4); s.add(rim);
    const stars = dust(1500, [140, 140, 40], 0xffffff, .25, .9); stars.position.z = -45; s.add(stars);
    return { stars, rim };
  }
  // kara delik: siyah küre + dönen sıcak disk + foton halkası + parlayan toz
  function blackHole(R = 1.6) {
    const B = new THREE.Group();
    B.add(M(new THREE.SphereGeometry(R, 64, 48), new THREE.MeshBasicMaterial({ color: 0x000000 })));
    const dg = new THREE.RingGeometry(R * 1.2, R * 3.3, 160, 8); const dc = []; const DP = dg.attributes.position;
    for (let i = 0; i < DP.count; i++) { const x = DP.getX(i), y = DP.getY(i); const r = Math.hypot(x, y); const k = (r - R * 1.2) / (R * 2.1);
      const n = .85 + .15 * Math.sin(Math.atan2(y, x) * 9 + r * 4); const c = new THREE.Color().setHSL(.09 - k * .06, 1, (.66 - k * .45) * n); dc.push(c.r, c.g, c.b); }
    dg.setAttribute('color', new THREE.Float32BufferAttribute(dc, 3));
    const disk = M(dg, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide, transparent: true, opacity: .95, blending: THREE.AdditiveBlending, depthWrite: false }));
    disk.rotation.x = -Math.PI / 2 + .22; B.add(disk);
    // diskin arkadan bükülen ışığı (kara deliğin üstünde/altında yay)
    const arcM = new THREE.MeshBasicMaterial({ color: 0xff8a30, transparent: true, opacity: .22, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
    const arc = M(new THREE.RingGeometry(R * 1.12, R * 1.7, 128, 2), arcM); arc.position.z = -.05; B.add(arc);
    const halo = M(new THREE.TorusGeometry(R * 1.08, R * .04, 12, 128), new THREE.MeshBasicMaterial({ color: 0xffe2b0 })); B.add(halo);
    const glow = dust(700, [R * 7, R * .35, R * 7], 0xffa040, .18, .7); glow.rotation.x = .22; B.add(glow);
    B.userData.spin = t => { disk.rotation.z = t * .45; glow.rotation.y = t * .35; };
    return B;
  }
  function astronaut() {
    const g = new THREE.Group(); const suit = std(0xeef1f5, { roughness: .55 }); const dk = std(0x3a4250, { metalness: .4, roughness: .5 });
    const body = M(new THREE.CapsuleGeometry(.75, 1.1, 10, 24), suit); g.add(body);
    const pack = M(rb(1.4, 1.7, .7, .15), std(0xd8dce2)); pack.position.set(0, .2, -.8); g.add(pack);
    const panel = M(rb(.8, .5, .2, .06), dk); panel.position.set(0, .35, .72); g.add(panel);
    [0xff3b30, 0x2ad15a, 0x3fb6ff].forEach((c, i) => { const b = M(new THREE.SphereGeometry(.07, 12, 8), new THREE.MeshBasicMaterial({ color: c })); b.position.set(-.2 + i * .2, .35, .84); g.add(b); });
    const helmet = M(new THREE.SphereGeometry(.85, 48, 32), std(0xeef1f5, { roughness: .4 })); helmet.position.y = 1.85; g.add(helmet);
    const visor = M(new THREE.SphereGeometry(.7, 48, 32, -Math.PI * .4, Math.PI * .8, Math.PI * .28, Math.PI * .42), new THREE.MeshStandardMaterial({ color: 0xffb040, metalness: 1, roughness: .1, emissive: 0x402000 }));
    visor.position.set(0, 1.85, .2); g.add(visor);
    const limbs = [];
    [-1, 1].forEach(k => { const a = new THREE.Group(); a.position.set(k * .85, .8, 0); g.add(a); const m = M(new THREE.CapsuleGeometry(.24, .9, 8, 16), suit); m.position.y = -.55; a.add(m);
      const gl = M(new THREE.SphereGeometry(.26, 16, 12), dk); gl.position.y = -1.15; a.add(gl); limbs.push(a);
      const l = new THREE.Group(); l.position.set(k * .38, -1.1, 0); g.add(l); const lm = M(new THREE.CapsuleGeometry(.3, 1.1, 8, 16), suit); lm.position.y = -.7; l.add(lm);
      const bt = M(rb(.6, .4, .8, .1), dk); bt.position.set(0, -1.45, .1); l.add(bt); limbs.push(l); });
    g.userData = { limbs, suit };
    return g;
  }
  function arrow(len, col) {
    const g = new THREE.Group(); const m = new THREE.MeshBasicMaterial({ color: col });
    const sh = M(new THREE.CylinderGeometry(.12, .12, 1, 16), m); g.add(sh); const hd = M(new THREE.ConeGeometry(.32, .6, 24), m); g.add(hd);
    g.userData.set = l => { l = Math.max(.01, l); sh.scale.y = l; sh.position.y = l / 2; hd.position.y = l + .3; }; g.userData.set(len); return g;
  }
  const wave = (A, t, k = 1) => A.userData.limbs.forEach((l, i) => l.rotation.z = Math.sin(t * 3 + i) * .35 * k + (i % 2 ? 0 : (i < 2 ? -.3 : .3)) * k);

  const S1 = 3.44, S2 = 5.84, S3 = 9.76, S4 = 12.64, S5 = 16.4, S6 = 20.0, S7 = 25.04, S8 = 29.76, S9 = 35.68;

  // 1) Astronot kara deliğe doğru düşer, uzar
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    const sp = space(s);
    const B = blackHole(1.8); B.position.set(0, 4.6, -6); s.add(B);
    const A = astronaut(); A.scale.setScalar(.75); s.add(A);
    return t => {
      B.userData.spin(t); sp.stars.rotation.z = t * .01;
      const k = ease(prog(t, .3, 3.0));
      A.position.set(lerp(1.6, .3, k), lerp(7.0, 5.6, k), lerp(1.5, -2.5, k)); A.rotation.set(-1.0 + k * .3, t * .3, .3);
      A.scale.set(.6 * (1 - k * .4), .6 * (1 + k * 1.0), .6 * (1 - k * .4)); wave(A, t, 1 - k);
      cam.position.set(Math.sin(t * .2) * 1.2, 7.0, lerp(17, 14.5, ease(prog(t, 0, S1)))); cam.lookAt(0, 6.0, 0); };
  } });
  // 2) Spagettileşme: astronot spagetti gibi incelir, yanında gerçek bir spagetti teli
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    const sp = space(s, { rim: 0xffb04a });
    const A = astronaut(); A.position.set(-1.2, 5.6, 0); A.scale.setScalar(.4); s.add(A);
    const pasta = new THREE.Group(); pasta.position.set(1.6, 5.6, 0); s.add(pasta);
    const curve = new THREE.CatmullRomCurve3(Array.from({ length: 9 }, (_, i) => new THREE.Vector3(Math.sin(i * 1.3) * .35, -3.2 + i * .8, Math.cos(i * 1.1) * .25)));
    const noodle = M(new THREE.TubeGeometry(curve, 120, .09, 12), std(0xf2c46a, { roughness: .45, emissive: 0x3a2200, emissiveIntensity: .3 })); pasta.add(noodle);
    const d = dust(400, [30, 20, 20], 0xffd8b0, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S1; const k = ease(prog(a, .2, 1.6));
      A.scale.set(.4 * (1 - k * .7), .4 * (1 + k * 1.5), .4 * (1 - k * .7)); A.rotation.set(0, t * .4, Math.sin(t * 2) * .05); wave(A, t, 1 - k);
      pasta.rotation.y = t * .5; pasta.scale.setScalar(.75 * Math.max(.01, back(prog(a, .9, .5))));
      sp.stars.rotation.z = t * .01; d.rotation.y = t * .03;
      cam.position.set(0, 6.0, 15); cam.lookAt(0, 5.6, 0); };
  } });
  // 3) Ayaklar baştan daha güçlü çekilir (alttaki ok büyük, üstteki küçük)
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    const sp = space(s);
    const B = blackHole(1.3); B.position.set(0, -.6, -3); s.add(B);
    const A = astronaut(); A.position.set(0, 6.4, 0); A.scale.setScalar(.5); s.add(A);
    const aF = arrow(2.2, 0xffcf2e), aH = arrow(.6, 0xffcf2e); aF.rotation.z = Math.PI; aH.rotation.z = Math.PI; s.add(aF); s.add(aH);
    return t => {
      const a = t - S2; B.userData.spin(t); sp.stars.rotation.z = t * .01;
      const k = ease(prog(a, 1.4, 2.4));
      A.scale.set(.5 * (1 - k * .35), .5 * (1 + k * .7), .5 * (1 - k * .35)); A.position.y = 6.4 - k * .6; A.rotation.y = .4 + Math.sin(t * .5) * .2; wave(A, t, 1 - k * .5);
      const top = A.position.y + 2.6 * A.scale.y * 1.0, bot = A.position.y - 2.9 * A.scale.y;
      aH.position.set(1.6, top + .2, 0); aF.position.set(1.6, bot + .4, 0);
      aH.userData.set(.5 + .1 * Math.sin(t * 6)); aF.userData.set((1.1 + .15 * Math.sin(t * 6)) * back(prog(a, .5, .5)) + .01);
      aH.visible = a > .3; aF.visible = a > .5;
      cam.position.set(0, 6.4, 18); cam.lookAt(0, 6.2, 0); };
  } });
  // 4) Küçük kara delik: daha kenara varmadan parçalanma
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    const sp = space(s);
    const B = blackHole(.7); B.position.set(0, 4.8, 0); s.add(B);
    const ring = M(new THREE.TorusGeometry(.75, .03, 8, 64), new THREE.MeshBasicMaterial({ color: 0x7ee0ff })); ring.position.copy(B.position); s.add(ring);
    const A = astronaut(); s.add(A);
    const bits = dust(260, [.6, 3, .6], 0xffe0c0, .14, .9); s.add(bits);
    return t => {
      const a = t - S3; B.userData.spin(t * 1.6); sp.stars.rotation.z = t * .01;
      const k = ease(prog(a, .1, 2.6)); const brk = a > 1.9;
      A.visible = !brk; A.position.set(0, lerp(7.2, 6.2, k), 0); A.rotation.set(0, t * .4, 0);
      A.scale.set(.32 * (1 - k * .7), .32 * (1 + k * 1.2), .32 * (1 - k * .7));
      bits.visible = brk; bits.position.set(0, 6.0 - prog(a, 1.9, 1.0) * 1.6, 0); bits.scale.set(1, 1 + prog(a, 1.9, 1) * .8, 1); bits.rotation.y = t;
      cam.position.set(0, 6.6, 16); cam.lookAt(0, 6.3, 0); };
  } });
  // 5) Olay ufku: ışık ışınları bükülüp içeri düşer
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    const sp = space(s);
    const B = blackHole(1.6); B.position.set(0, 5.6, 0); s.add(B);
    const hz = M(new THREE.SphereGeometry(1.62, 64, 48), new THREE.MeshBasicMaterial({ color: 0x7ee0ff, wireframe: true, transparent: true, opacity: 0 })); hz.position.copy(B.position); s.add(hz);
    const rays = []; for (let i = 0; i < 9; i++) { const y0 = -2.6 + i * .65; const pts = []; for (let j = 0; j <= 60; j++) { const x = -6 + j * .2; let y = y0; const r = Math.hypot(x, y); const bend = 2.2 / Math.max(.5, r); y -= Math.sign(y0 || .01) * bend * .35 * Math.exp(-Math.abs(x) * .3); pts.push(new THREE.Vector3(x, y, .5)); }
      const absorbed = Math.abs(y0) < 1.4; if (absorbed) { pts.length = 30; pts.push(new THREE.Vector3(-.2, y0 * .2, .5)); }
      const c = new THREE.CatmullRomCurve3(pts); const tube = M(new THREE.TubeGeometry(c, 120, .03, 6), new THREE.MeshBasicMaterial({ color: absorbed ? 0xff9a3a : 0xbfe8ff, transparent: true, opacity: .9 }));
      tube.position.copy(B.position); s.add(tube); const dot = M(new THREE.SphereGeometry(.09, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffffff })); s.add(dot); rays.push({ tube, c, dot, absorbed, ph: r1() }); }
    return t => {
      const a = t - S4; B.userData.spin(t); sp.stars.rotation.z = t * .01;
      hz.material.opacity = .25 * prog(a, .2, .5) * (1 - prog(a, 1.7, .3)) + .05;
      rays.forEach(R => { const show = a > 1.7; R.tube.visible = show; const u = (((a - 1.7) * .5 + R.ph) % 1 + 1) % 1; R.dot.visible = show; R.dot.position.copy(R.c.getPoint(u)).add(B.position);
        R.tube.material.opacity = .5 * prog(a, 1.7, .4); });
      cam.position.set(Math.sin(a * .2) * 1.2, 6.2, 17); cam.lookAt(0, 5.9, 0); };
  } });
  // 6) Dışarıdan izleyen: gemi uzakta, düşen astronottan gelen ışık atımları seyrekleşir
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    const sp = space(s);
    const B = blackHole(1.3); B.position.set(-1.4, 4.4, -1); s.add(B);
    const ship = new THREE.Group(); ship.position.set(2.0, 8.4, 0); ship.scale.setScalar(.55); s.add(ship);
    const hull = M(new THREE.CapsuleGeometry(.7, 2.4, 12, 32), std(0xd8dce2, { metalness: .6, roughness: .3 })); hull.rotation.z = Math.PI / 2; ship.add(hull);
    for (let i = 0; i < 3; i++) { const w = M(new THREE.CircleGeometry(.18, 24), new THREE.MeshBasicMaterial({ color: 0x7ee0ff })); w.position.set(-.8 + i * .7, .2, .7); ship.add(w); }
    [-1, 1].forEach(k => { const f = M(rb(1.2, .1, .8, .04), std(0x3a4250, { metalness: .6 })); f.position.set(.9, k * .7, 0); f.rotation.x = k * .3; ship.add(f); });
    const eng = M(new THREE.SphereGeometry(.3, 16, 12), new THREE.MeshBasicMaterial({ color: 0x7ee0ff })); eng.position.x = 1.9; ship.add(eng);
    const A = astronaut(); A.scale.setScalar(.28); s.add(A);
    const pulses = Array.from({ length: 8 }, () => { const p = M(new THREE.SphereGeometry(.1, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffe08a })); s.add(p); return p; });
    return t => {
      const a = t - S5; B.userData.spin(t); sp.stars.rotation.z = t * .01;
      const k = 1 - Math.exp(-a * .7); const ax = lerp(1.0, -.2, k), ay = lerp(6.8, 5.5, k);
      A.position.set(ax, ay, 0); A.rotation.set(.5, t * .3 * (1 - k), .4); wave(A, t, 1 - k);
      pulses.forEach((p, i) => { const em = i * .35 * (1 + i * .35); const u = (a - em) / 1.0; p.visible = u > 0 && u < 1; const tp = ship.position;
        p.position.set(lerp(ax, tp.x, u), lerp(ay, tp.y, u), 0); });
      ship.position.y = 8.4 + Math.sin(t) * .08;
      cam.position.set(0, 6.8, 17); cam.lookAt(.2, 6.4, 0); };
  } });
  // 7) Zaman yavaşlar: saat ibresi yavaşlar, astronot kızarır ve söner
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    const sp = space(s);
    const B = blackHole(2.2); B.position.set(0, 2.0, -5); s.add(B);
    const A = astronaut(); A.position.set(-1.1, 6.3, 0); A.scale.setScalar(.45); s.add(A);
    const clock = new THREE.Group(); clock.position.set(1.6, 6.6, .5); s.add(clock);
    { const fc = M(new THREE.CylinderGeometry(1.0, 1.0, .2, 64), std(0xf2efe8, { roughness: .4 })); fc.rotation.x = Math.PI / 2; clock.add(fc); }
    const rim = M(new THREE.TorusGeometry(1.0, .09, 16, 64), std(0xc0c6ce, { metalness: .9, roughness: .2 })); clock.add(rim);
    for (let i = 0; i < 12; i++) { const tk = M(new THREE.BoxGeometry(.06, .18, .05), new THREE.MeshBasicMaterial({ color: 0x222222 })); const an = i / 12 * Math.PI * 2; tk.position.set(Math.sin(an) * .8, Math.cos(an) * .8, .12); tk.rotation.z = -an; clock.add(tk); }
    const hand = new THREE.Group(); hand.position.z = .14; clock.add(hand);
    const hm = M(new THREE.BoxGeometry(.07, .75, .04), new THREE.MeshBasicMaterial({ color: 0xff3b30 })); hm.position.y = .35; hand.add(hm);
    const tint = new THREE.Color(); const white = new THREE.Color(0xeef1f5), red = new THREE.Color(0x8a1a10);
    return t => {
      const a = t - S6; B.userData.spin(t); sp.stars.rotation.z = t * .01;
      const sl = 1 - prog(a, .5, 3.5); const ang = 3 * (1 - Math.exp(-a * 1.2)) + .2 * a * sl;
      hand.rotation.z = -ang * 2.2;
      const rk = prog(a, 2.3, 1.8); tint.copy(white).lerp(red, rk); A.userData.suit.color.copy(tint); A.userData.suit.emissive = new THREE.Color(0x400000).multiplyScalar(rk);
      const fade = 1 - prog(a, 3.6, 1.2); A.scale.setScalar(.45 * Math.max(.02, fade)); A.visible = fade > .02;
      A.rotation.set(.3, t * .3 * sl, .2); wave(A, t * sl + 1, sl);
      clock.rotation.y = Math.sin(t * .4) * .25; clock.position.y = 6.6 + Math.sin(t * .8) * .1;
      cam.position.set(0, 6.6, 15); cam.lookAt(.2, 6.4, 0); };
  } });
  // 8) Samanyolu merkezi: spiral galaksi + dev kara delik
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    const sp = space(s, { bg: ['#0a0a24', '#000000'] });
    const G = new THREE.Group(); G.position.set(0, 6.0, 0); G.rotation.x = .9; s.add(G);
    const n = 5000; const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3); const c = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { const arm = i % 2; const r = Math.pow(r1(), .7) * 6.5 + .3; const an = arm * Math.PI + r * .9 + (r1() - .5) * .7;
      p[i * 3] = Math.cos(an) * r; p[i * 3 + 1] = (r1() - .5) * .25 * (1 + (6 - r) * .1); p[i * 3 + 2] = Math.sin(an) * r;
      const col = new THREE.Color().setHSL(.6 - (1 - r / 7) * .5, .7, .55 + (1 - r / 7) * .25); c[i * 3] = col.r; c[i * 3 + 1] = col.g; c[i * 3 + 2] = col.b; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('color', new THREE.BufferAttribute(c, 3));
    const gal = new THREE.Points(g, new THREE.PointsMaterial({ size: .12, map: soft, vertexColors: true, transparent: true, opacity: .9, depthWrite: false, blending: THREE.AdditiveBlending })); G.add(gal);
    const core = dust(300, [1.2, .3, 1.2], 0xffd08a, .25, .5); G.add(core);
    const B = blackHole(.45); B.position.set(0, 6.0, 0); B.scale.setScalar(.01); s.add(B);
    return t => {
      const a = t - S7; gal.rotation.y = t * .08; sp.stars.rotation.z = t * .01; B.userData.spin(t);
      const z = ease(prog(a, 1.2, 2.6));
      G.scale.setScalar(lerp(1, 3.0, z)); core.material.opacity = .6 * (1 - z);
      B.scale.setScalar(Math.max(.01, lerp(.1, 1.6, z))); B.visible = z > .02;
      cam.position.set(0, 7.0, lerp(20, 16, z)); cam.lookAt(0, 6.2, 0); };
  } });
  // 9) NASA simülasyonu: ufku geç, 12,8 saniye sonra parçalanma (sayaç)
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    const sp = space(s);
    const B = blackHole(2.0); B.position.set(0, 5.6, -2); s.add(B);
    const hz = M(new THREE.TorusGeometry(2.08, .04, 8, 96), new THREE.MeshBasicMaterial({ color: 0x7ee0ff, transparent: true, opacity: .8 })); hz.position.copy(B.position); s.add(hz);
    const A = astronaut(); A.scale.setScalar(.35); s.add(A);
    const bits = dust(300, [.5, 3, .5], 0xffe0c0, .12, .9); s.add(bits);
    return t => {
      const a = t - S8; B.userData.spin(t); sp.stars.rotation.z = t * .01;
      const k = ease(prog(a, .2, 2.2));
      A.position.set(lerp(2.4, 0, k), lerp(7.4, 5.6, k), lerp(1.0, 0, k)); A.rotation.set(.4, t * .5, .3);
      const st = prog(a, 2.6, 2.4); A.scale.set(.35 * (1 - st * .6), .32 * (1 + st * .8), .35 * (1 - st * .6)); A.visible = a < 5.0; wave(A, t, 1 - st);
      bits.visible = a >= 5.0; bits.position.set(0, 6.0, 0); bits.scale.set(1 + prog(a, 5, .8) * 2, 1 + prog(a, 5, .8) * 2, 1); bits.rotation.y = t;
      hz.material.opacity = .4 + .4 * Math.sin(t * 4);
      cam.position.set(Math.sin(a * .15) * 1.5, 6.8, lerp(17, 15, ease(prog(a, 0, 5)))); cam.lookAt(0, 6.3, 0); };
  } });
  // 10) Sıradaki soru: gökyüzü neden mavi — mavi gökyüzü, güneş ışığı, saçılan mavi partiküller
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    s.background = gradTex('#1e6fd0', '#bfe4ff'); s.fog = new THREE.Fog(0x9fd0ff, 40, 120);
    s.add(new THREE.HemisphereLight(0xbfe4ff, 0x3a5a2a, 1.2));
    const sun = new THREE.DirectionalLight(0xfff4e0, 2.6); sun.position.set(-10, 14, 8); s.add(sun);
    const ground = M(new THREE.CylinderGeometry(30, 30, 1, 64), std(0x4a7a3a, { roughness: .9 })); ground.position.y = 1.0; s.add(ground);
    const hills = []; for (let i = 0; i < 5; i++) { const h = M(new THREE.SphereGeometry(4 + r1() * 3, 48, 32), std(0x5a8a42, { roughness: .9 })); h.position.set(-12 + i * 6, -.5, -10 - r1() * 6); h.scale.y = .5; s.add(h); hills.push(h); }
    const sunB = M(new THREE.SphereGeometry(1.0, 32, 24), new THREE.MeshBasicMaterial({ color: 0xfff6d0, fog: false })); sunB.position.set(-2.4, 7.8, -3); s.add(sunB);
    const halo = dust(200, [3, 3, 1], 0xfff0c0, .8, .5); halo.position.copy(sunB.position); s.add(halo);
    const beam = M(new THREE.CylinderGeometry(.08, .08, 1, 12), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .8 })); s.add(beam);
    const blues = []; for (let i = 0; i < 26; i++) { const b = M(new THREE.SphereGeometry(.08, 12, 8), new THREE.MeshBasicMaterial({ color: 0x3a8aff })); b.userData.d = new THREE.Vector3(r1() - .5, r1() - .5, r1() - .5).normalize(); s.add(b); blues.push(b); }
    const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e });
    const q = M(new THREE.TorusGeometry(.5, .12, 12, 32, Math.PI * 1.4), qm); q.rotation.z = -Math.PI * .3; s.add(q);
    const qd = M(new THREE.SphereGeometry(.14, 12, 8), qm); s.add(qd);
    return t => {
      const a = t - S9; const hit = sunB.position;
      const from = sunB.position; const mid = from.clone().lerp(hit, .5); beam.visible = false; void mid;
      beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), hit.clone().sub(from).normalize());
      blues.forEach((b, i) => { const u = ((a * .6 + i / 26) % 1); b.position.copy(hit).addScaledVector(b.userData.d, 1.0 + u * 4.0); b.scale.setScalar(1 - u * .6); });
      halo.rotation.z = t * .2;
      q.position.set(2.4, 7.4, .5); qd.position.set(2.3, 6.55, .5); q.visible = qd.visible = Math.sin(a * 4) > -.6;
      cam.position.set(Math.sin(a * .2) * 1.5, 5.8, 16); cam.lookAt(0, 6.6, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'KARA DELİĞE<br>DÜŞSEN NE <span class="y">OLUR?</span>', 100) },
    { t0: S1, t1: S2, html: T('BİLİM İNSANLARI BUNA', '<span class="y">SPAGETTİLEŞME</span><br>DİYOR', 100) },
    { t0: S2, t1: S3, html: T('ÇEKİM KUVVETİ', 'AYAKLARI <span class="y">DAHA GÜÇLÜ</span><br>ÇEKER', 96) },
    { t0: S3, t1: S4, html: T('KÜÇÜK KARA DELİKTE', 'KENARA <span class="y">VARMADAN</span><br>PARÇALANIRSIN', 92) },
    { t0: S4, t1: 14.4, html: T('KENARIN ADI', 'OLAY <span class="y">UFKU</span>') },
    { t0: 14.4, t1: S5, html: T('BURADAN', 'IŞIK BİLE<br><span class="y">KAÇAMAZ</span>', 104) },
    { t0: S5, t1: S6, html: T('DIŞARIDAN İZLEYEN', 'SENİ İÇERİ DÜŞERKEN<br><span class="y">HİÇ GÖREMEZ</span>', 84) },
    { t0: S6, t1: 22.32, html: T('UFKA YAKLAŞTIKÇA', 'ZAMANIN <span class="y">YAVAŞLAR</span>', 100) },
    { t0: 22.32, t1: S7, html: T('VE SONUNDA', 'DONUP <span class="y">KIZARIRSIN</span>', 100) },
    { t0: S7, t1: S8, html: BIG('GALAKSİMİZİN MERKEZİ', 'k4', 'KAT GÜNEŞ KÜTLESİ', '4<small>MİLYON</small>') },
    { t0: S8, t1: S9, html: BIG('NASA SİMÜLASYONU', 'k128', 'SANİYE SONRA PARÇALANIRSIN', '0,0') },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'GÖKYÜZÜ NEDEN<br><span class="y">MAVİ?</span>', 104) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k4', S7], ['k128', S8]];
  return {
    END: 40.36, shots, titles,
    update: (t, q) => { pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; });
      const c = q('k128'); if (c) c.textContent = (12.8 * ease(prog(t, S8 + 2.2, 2.6))).toFixed(1).replace('.', ','); },
    follow: { t: 38.56, click: 39.46 },
    sfx: [[.4, 'whoosh', .5], [1.5, 'boom', .4], [S1 + 1.0, 'pop', .5], [S2 + .5, 'whoosh', .4], [S2 + 1.0, 'ding', .4], [S3 + 1.9, 'crunch', .9], [S3 + 1.92, 'snap', .6],
      [S4 + 1.7, 'whoosh', .6], [S5 + .3, 'ding', .3], [S5 + .9, 'ding', .25], [S5 + 1.9, 'ding', .2], [S6 + .3, 'click', .5], [S6 + 1.0, 'click', .4], [S6 + 2.0, 'click', .3],
      [S7 + 1.2, 'whoosh', .7], [S7 + 3.6, 'boom', .5], [S8 + 2.2, 'ding', .4], [S8 + 5.0, 'crunch', 1], [S8 + 5.02, 'boom', .7], [S9 + .5, 'ding', .5]],
  };
};
