// Bilgi #10: Tonlarca çelikten gemi neden batmaz? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: Gard "Why do ships float?" (çelik sudan yaklaşık 8 kat yoğun; Arşimet: cisim, yerini değiştirdiği akışkanın
// ağırlığı kadar yukarı itilir; geminin deplasmanı = kendi ağırlığı; gövdenin içi büyük ölçüde hava, ortalama yoğunluk sudan az;
// gövde delinip hava yerine su dolarsa gemi batabilir). Çelik yoğunluğu ~7.850 kg/m³ (Engineering ToolBox), su ~1.000 kg/m³.
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 101; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
  const steel = () => std(0xaeb6c0, { metalness: .85, roughness: .3 });
  const waterM = (op = .5) => new THREE.MeshPhysicalMaterial({ color: 0x2a8fd6, emissive: 0x06345a, emissiveIntensity: .5, roughness: .1, metalness: 0, transparent: true, opacity: op, depthWrite: false });
  function tank(w, h, d, lvl) { // cam akvaryum + su
    const g = new THREE.Group();
    const glass = M(rb(w, h, d, .1), new THREE.MeshPhysicalMaterial({ color: 0xcfe8ff, roughness: .05, transparent: true, opacity: .12, depthWrite: false, side: THREE.DoubleSide })); glass.position.y = h / 2; g.add(glass);
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)), new THREE.LineBasicMaterial({ color: 0x9fd0ff, transparent: true, opacity: .6 })); edges.position.y = h / 2; g.add(edges);
    const base = M(rb(w + .4, .3, d + .4, .08), std(0x1a2230, { metalness: .6, roughness: .4 })); base.position.y = -.15; g.add(base);
    const wat = M(new THREE.BoxGeometry(w - .1, 1, d - .1), waterM()); g.add(wat);
    const top = M(new THREE.PlaneGeometry(w - .1, d - .1), new THREE.MeshStandardMaterial({ color: 0x7ec8ff, emissive: 0x1a5a8a, emissiveIntensity: .6, transparent: true, opacity: .55, roughness: .05, metalness: .3, depthWrite: false })); top.rotation.x = -Math.PI / 2; g.add(top);
    g.userData.level = y => { wat.scale.y = y; wat.position.y = y / 2; top.position.y = y + .001; }; g.userData.level(lvl); return g;
  }
  function arrow(len, col) {
    const g = new THREE.Group(); const m = new THREE.MeshBasicMaterial({ color: col });
    const sh = M(new THREE.CylinderGeometry(.12, .12, 1, 16), m); g.add(sh); const hd = M(new THREE.ConeGeometry(.32, .6, 24), m); g.add(hd);
    g.userData.set = l => { l = Math.max(.01, l); sh.scale.y = l; sh.position.y = l / 2; hd.position.y = l + .3; }; g.userData.set(len); return g;
  }
  function ship(o = {}) {
    const sh = new THREE.Shape(); sh.moveTo(-4.8, -1); sh.lineTo(2.5, -1); sh.quadraticCurveTo(4.6, -.8, 5.4, 0); sh.quadraticCurveTo(4.6, .8, 2.5, 1); sh.lineTo(-4.8, 1); sh.quadraticCurveTo(-5.2, 0, -4.8, -1);
    const g = new THREE.ExtrudeGeometry(sh, { depth: 1.6, bevelEnabled: false, curveSegments: 24, steps: 8 }); g.rotateX(-Math.PI / 2);
    const P = g.attributes.position; const col = []; const cR = new THREE.Color(0x9b2a20), cW = new THREE.Color(0xe8e8e8), cB = new THREE.Color(0x1f2d44);
    for (let i = 0; i < P.count; i++) { const y = P.getY(i); const k = y / 1.6; P.setZ(i, P.getZ(i) * lerp(.45, 1, Math.pow(k, .6))); if (P.getX(i) > 2) P.setX(i, P.getX(i) + (1 - k) * -.5 * ((P.getX(i) - 2) / 3.4));
      const c = k < .36 ? cR : (k < .42 ? cW : cB); col.push(c.r, c.g, c.b); }
    g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
    const grp = new THREE.Group(); const hullM = new THREE.MeshStandardMaterial({ vertexColors: true, metalness: .55, roughness: .4, transparent: !!o.cut, opacity: o.cut ? .35 : 1, depthWrite: !o.cut });
    const hull = M(g, hullM); grp.add(hull);
    const deck = M(rb(9.6, .12, 1.9, .05), std(0x5a6068, { metalness: .5 })); deck.position.set(-.1, 1.62, 0); grp.add(deck);
    const sup = M(rb(1.6, 1.5, 1.7, .08), std(0xeef0f2, { roughness: .4 })); sup.position.set(-3.8, 2.4, 0); grp.add(sup);
    const win = M(new THREE.BoxGeometry(.05, .18, 1.5), new THREE.MeshBasicMaterial({ color: 0xffd98a })); win.position.set(-2.98, 2.8, 0); grp.add(win);
    const br = M(rb(2.0, .3, 2.1, .06), std(0xeef0f2)); br.position.set(-3.8, 3.25, 0); grp.add(br);
    const fn = M(new THREE.CylinderGeometry(.28, .34, 1.2, 24), std(0xc0392b, { roughness: .5 })); fn.position.set(-4.3, 3.9, 0); grp.add(fn);
    const cc = [0xc0392b, 0x2563eb, 0xf59e0b, 0x0d9488, 0xe5e7eb, 0x7c3aed];
    for (let x = 0; x < 6; x++) for (let z = 0; z < 2; z++) for (let y = 0; y < 2; y++) { if (y === 1 && (x + z) % 3 === 0) continue;
      const b = M(rb(.95, .6, .82, .04), std(cc[(x * 3 + z + y * 2) % 6], { roughness: .5, metalness: .3 })); b.position.set(-2.2 + x * 1.0, 1.98 + y * .62, (z - .5) * .86); grp.add(b); }
    const ml = new THREE.PointLight(0xffd98a, 60, 6); ml.position.set(-2.6, 2.9, 1.5); grp.add(ml);
    grp.userData = { hull, hullM }; return grp;
  }
  function sea(size = 160, seg = 110, c = 0x0b2a44) {
    const g = new THREE.PlaneGeometry(size, size, seg, seg); g.rotateX(-Math.PI / 2); const P = g.attributes.position; const base = Float32Array.from(P.array);
    const m = M(g, std(c, { metalness: .35, roughness: .3 }));
    m.userData.upd = t => { for (let i = 0; i < P.count; i++) { const x = base[i * 3], z = base[i * 3 + 2]; P.setY(i, Math.sin(x * .35 + t * 1.3) * .14 + Math.sin(z * .5 + t * .9 + x * .2) * .1); } P.needsUpdate = true; g.computeVertexNormals(); };
    return m;
  }
  // deniz kesiti: geniş, saydam su bloğu (gemi altını görmek için)
  function seaSection(lvl = 4) {
    const g = new THREE.Group(); const w = 22, d = 8;
    const wat = M(new THREE.BoxGeometry(w, lvl, d), waterM(.42)); wat.position.y = lvl / 2; g.add(wat);
    const top = M(new THREE.PlaneGeometry(w, d, 60, 20), new THREE.MeshStandardMaterial({ color: 0x5fb4ef, emissive: 0x0f4a7a, emissiveIntensity: .6, transparent: true, opacity: .5, roughness: .1, metalness: .3, depthWrite: false, side: THREE.DoubleSide }));
    top.rotation.x = -Math.PI / 2; top.position.y = lvl; g.add(top);
    const fl = M(new THREE.BoxGeometry(w, .4, d), std(0x1a2a36, { roughness: .9 })); fl.position.y = -.2; g.add(fl);
    const P = top.geometry.attributes.position; const base = Float32Array.from(P.array);
    g.userData = { lvl, upd: t => { for (let i = 0; i < P.count; i++) P.setZ(i, Math.sin(base[i * 3] * .6 + t * 1.6) * .06); P.needsUpdate = true; } };
    return g;
  }
  function bubbles(n, sp) { const g = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 12, 10), new THREE.MeshStandardMaterial({ color: 0xdff4ff, emissive: 0x4aa0d0, emissiveIntensity: .4, transparent: true, opacity: .7, roughness: .1 }), n);
    const bs = []; for (let i = 0; i < n; i++) bs.push([(r1() - .5) * sp[0], r1(), (r1() - .5) * sp[2], .05 + r1() * .1]); g.userData.bs = bs; g.userData.h = sp[1]; return g; }
  const dm = new THREE.Object3D();
  function updBub(B, t, sp = .3, on = 1) { const { bs, h } = B.userData; bs.forEach(([x, f0, z, s], i) => { const f = (f0 + t * sp) % 1; dm.position.set(x, f * h, z); dm.scale.setScalar(Math.max(.001, s * on)); dm.updateMatrix(); B.setMatrixAt(i, dm.matrix); }); B.instanceMatrix.needsUpdate = true; }
  function astronaut() {
    const g = new THREE.Group(); const suit = std(0xeef1f5, { roughness: .6 }); const dk = std(0x3a4250, { metalness: .4, roughness: .5 });
    const body = M(new THREE.CapsuleGeometry(.75, 1.1, 10, 24), suit); g.add(body);
    const pack = M(rb(1.4, 1.7, .7, .15), std(0xd8dce2)); pack.position.set(0, .2, -.8); g.add(pack);
    const panel = M(rb(.8, .5, .2, .06), dk); panel.position.set(0, .35, .72); g.add(panel);
    [0xff3b30, 0x2ad15a, 0x3fb6ff].forEach((c, i) => { const b = M(new THREE.SphereGeometry(.07, 12, 8), new THREE.MeshBasicMaterial({ color: c })); b.position.set(-.2 + i * .2, .35, .84); g.add(b); });
    const ring = M(new THREE.TorusGeometry(.5, .12, 12, 32), dk); ring.rotation.x = Math.PI / 2; ring.position.y = 1.35; g.add(ring);
    const head = M(new THREE.SphereGeometry(.5, 32, 24), std(0xd9b49a, { roughness: .6 })); head.position.y = 1.85; g.add(head);
    const hair = M(new THREE.SphereGeometry(.52, 32, 16, 0, Math.PI * 2, 0, Math.PI * .45), std(0x2a1c14, { roughness: .8 })); hair.position.y = 1.88; hair.rotation.x = -.3; g.add(hair);
    [-1, 1].forEach(k => { const e = M(new THREE.SphereGeometry(.07, 12, 8), new THREE.MeshBasicMaterial({ color: 0x111111 })); e.position.set(k * .17, 1.92, .45); g.add(e); });
    const limbs = [];
    [-1, 1].forEach(k => { const a = new THREE.Group(); a.position.set(k * .85, .8, 0); g.add(a); const m = M(new THREE.CapsuleGeometry(.24, .9, 8, 16), suit); m.position.y = -.55; a.add(m);
      const gl = M(new THREE.SphereGeometry(.26, 16, 12), dk); gl.position.y = -1.15; a.add(gl); limbs.push(a);
      const l = new THREE.Group(); l.position.set(k * .38, -1.1, 0); g.add(l); const lm = M(new THREE.CapsuleGeometry(.3, 1.1, 8, 16), suit); lm.position.y = -.7; l.add(lm);
      const bt = M(rb(.6, .4, .8, .1), dk); bt.position.set(0, -1.45, .1); l.add(bt); limbs.push(l); });
    g.userData.limbs = limbs; return g;
  }

  const S1 = 2.8, S2 = 6.08, S3 = 6.96, S4 = 10.0, S5 = 11.68, S6 = 16.96, S7 = 22.0, S8 = 26.16, S9 = 31.32, S10 = 36.0;

  // 1) Cam tankta batan çelik bilye
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    lights(s, { key: 1800 });
    const T = tank(6, 5.2, 3.6, 4); T.position.set(0, 2.6, 0); s.add(T);
    const ball = M(new THREE.SphereGeometry(.55, 48, 32), steel()); s.add(ball);
    const sp = dust(80, [1.6, .6, 1.6], 0xcfefff, .2, .9); s.add(sp);
    const B = bubbles(16, [.6, 4, .6]); s.add(B);
    const d = dust(400, [30, 30, 20], 0xcfe8ff, .12, .45); d.position.y = 5; s.add(d);
    return t => {
      const hit = 1.25; const y = t < hit ? lerp(11.5, 6.6, Math.pow(prog(t, .15, hit - .15), 2)) : lerp(6.6, 3.2, easeOut(prog(t, hit, 1.1)));
      ball.position.set(0, y, 0); ball.rotation.x = t * 2;
      const sk = prog(t, hit, .5); sp.visible = sk > 0 && sk < 1; sp.position.set(0, 6.7 + sk * 1.2, 0); sp.scale.setScalar(.3 + sk * 1.6); sp.material.opacity = .9 * (1 - sk);
      B.position.set(0, 3, 0); updBub(B, t, .5, t > hit ? 1 : 0);
      d.rotation.y = t * .04;
      cam.position.set(Math.sin(t * .2) * 1.5, 5.6, 19); cam.lookAt(0, 6.0, 0); };
  } });
  // 2) Dalgalarda dev çelik gemi
  shots.push({ t0: S1, t1: S3, fov: 40, build: (s, cam) => {
    lights(s, { key: 2200 });
    const W = sea(); s.add(W); const S = ship(); S.scale.setScalar(1.25); s.add(S);
    const d = dust(400, [40, 20, 30], 0xcfe8ff, .12, .5); d.position.y = 8; s.add(d);
    return t => {
      const a = t - S1; W.userData.upd(t);
      S.position.set(lerp(1.5, -.5, a / 4), -.72 + Math.sin(t * 1.3) * .08, 0); S.rotation.set(Math.sin(t * .9) * .03, -.85 + a * .05, Math.sin(t * 1.1) * .025);
      d.rotation.y = t * .03;
      cam.position.set(lerp(-3, 2, ease(prog(a, 0, 4))), lerp(9, 7, ease(prog(a, 0, 4))), lerp(30, 27, ease(prog(a, 0, 4)))); cam.lookAt(0, 3.8, 0); };
  } });
  // 3) Terazi: 1 çelik küp = 8 su küpü
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    lights(s, { key: 2000, rim: 0xffcf2e });
    const G = new THREE.Group(); G.position.set(0, 3.6, 0); G.scale.setScalar(.75); s.add(G);
    const post = M(new THREE.CylinderGeometry(.18, .26, 4, 24), steel()); post.position.y = 2; G.add(post);
    const bse = M(new THREE.CylinderGeometry(1.4, 1.6, .35, 48), std(0x1a2230, { metalness: .6 })); G.add(bse);
    const beam = new THREE.Group(); beam.position.y = 4.1; G.add(beam);
    beam.add(M(rb(8.4, .25, .35, .1), std(0xffcf2e, { metalness: .7, roughness: .3 })));
    const pans = [-1, 1].map(k => { const p = new THREE.Group(); p.position.x = k * 4; beam.add(p);
      const str = M(new THREE.CylinderGeometry(.03, .03, 3.3, 8), steel()); str.position.y = -1.65; p.add(str);
      const pan = M(new THREE.CylinderGeometry(1.5, 1.3, .18, 48), steel()); pan.position.y = -3.3; p.add(pan); return p; });
    const cube = M(rb(1.2, 1.2, 1.2, .08), std(0x9aa3ad, { metalness: .9, roughness: .25 })); pans[0].add(cube);
    const wm = new THREE.MeshPhysicalMaterial({ color: 0x3fa0ff, emissive: 0x0a3a6a, emissiveIntensity: .7, roughness: .05, transparent: true, opacity: .6 });
    const wc = []; for (let i = 0; i < 8; i++) { const c = M(rb(1.2, 1.2, 1.2, .1), wm); c.userData.p = new THREE.Vector3(((i % 2) - .5) * 1.25, -2.6 + Math.floor(i / 4) * 1.25, (((i >> 1) % 2) - .5) * 1.25 * .8); pans[1].add(c); wc.push(c); }
    const d = dust(400, [30, 30, 20], 0xcfe8ff, .12, .45); d.position.y = 5; s.add(d);
    return t => {
      const ck = easeOut(prog(t, S3 + .1, .6)); cube.position.set(0, lerp(4, -2.6, ck), 0); cube.visible = t > S3 + .1;
      let n = 0; wc.forEach((c, i) => { const k = easeOut(prog(t, 7.6 + i * .17, .4)); c.visible = k > 0; if (k > 0) n++; c.position.copy(c.userData.p); c.position.y += (1 - k) * 4; });
      const tilt = (ck * 1 - n / 8) * .32; beam.rotation.z = tilt; pans.forEach(p => p.rotation.z = -beam.rotation.z);
      G.rotation.y = Math.sin(t * .4) * .2; d.rotation.y = t * .04;
      cam.position.set(0, 6.2, 22); cam.lookAt(0, 6.2, 0); };
  } });
  // 4) Sır şekilde: çelik blok -> yassı plaka -> içi boş tekne -> suda yüzer
  shots.push({ t0: S4, t1: S6, fov: 40, build: (s, cam) => {
    lights(s, { key: 2000, rim: 0x7ee0ff });
    const blk = M(rb(1.6, 1.6, 1.6, .1), std(0x9aa3ad, { metalness: .9, roughness: .25 })); s.add(blk);
    const tray = new THREE.Group(); s.add(tray); const sm = std(0x9aa3ad, { metalness: .85, roughness: .3, side: THREE.DoubleSide });
    const B = 3.2, Hs = 1.0, th = .08; tray.add(M(new THREE.BoxGeometry(B, th, B), sm));
    const flaps = [[0, 1], [0, -1], [1, 0], [-1, 0]].map(([x, z]) => { const p = new THREE.Group(); p.position.set(x * B / 2, 0, z * B / 2); p.rotation.y = Math.atan2(x, z); tray.add(p);
      const f = M(new THREE.BoxGeometry(B, Hs, th), sm); f.rotation.x = 0; f.position.set(0, 0, 0); const h = new THREE.Group(); p.add(h); h.add(f); f.position.set(0, Hs / 2, 0); return h; });
    const T = tank(9, 4, 5, 2.4); T.position.set(0, -.2, 0); s.add(T);
    const lv = arrow(.8, 0xffcf2e); lv.position.set(4.9, 2.6, 0); s.add(lv);
    const d = dust(400, [30, 30, 20], 0xcfe8ff, .12, .45); d.position.y = 6; s.add(d);
    return t => {
      const morph = ease(prog(t, 11.9, .9)); blk.visible = morph < .5; blk.scale.set(1 + morph * 1.2, Math.max(.05, 1 - morph * .95), 1 + morph * 1.2);
      tray.visible = morph >= .5; const fold = ease(prog(t, 12.9, 1.4)); flaps.forEach(h => h.rotation.x = lerp(Math.PI / 2, 0, fold));
      const tk = ease(prog(t, 14.6, .8)); T.scale.setScalar(Math.max(.01, tk)); T.visible = tk > 0;
      const dn = ease(prog(t, 15.0, 1.1)); const fy = lerp(5.6, 2.2 + .15, dn) + (dn >= 1 ? Math.sin(t * 2) * .04 : 0);
      blk.position.set(0, 5.6, 0); tray.position.set(0, fy, 0);
      T.userData.level(lerp(2.0, 2.45, ease(prog(t, 15.5, 1)))); lv.visible = t > 15.6; lv.userData.set(.6 + .2 * Math.sin(t * 5)); lv.position.y = T.position.y + 2.3;
      const ry = Math.sin(t * .5) * .3 + .5; blk.rotation.y = ry; tray.rotation.y = ry; tray.rotation.x = lerp(.35, 0, dn);
      d.rotation.y = t * .04;
      cam.position.set(0, lerp(6.4, 6.6, dn), lerp(16, 20, ease(prog(t, 14.4, 1.4)))); cam.lookAt(0, lerp(6.0, 4.9, ease(prog(t, 14.4, 1.4))), 0); };
  } });
  // 5) Arşimet: kaldırma kuvveti = yerinden edilen suyun ağırlığı
  const LV = 4, DR = .58 * .7;
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    lights(s, { key: 2000 });
    const X = seaSection(LV); s.add(X); const S = ship(); S.scale.setScalar(.7); s.add(S); S.position.set(0, LV - DR, 0); S.rotation.y = -.25;
    const disp = M(new THREE.BoxGeometry(9.4, .58, 1.6), new THREE.MeshStandardMaterial({ color: 0xffcf2e, emissive: 0xffaa00, emissiveIntensity: .8, transparent: true, opacity: .45, depthWrite: false })); disp.position.set(-.1, -.29 + .58, 0); S.add(disp); disp.position.y = .29;
    const up = arrow(2.6, 0xffcf2e); up.position.set(1.2, LV - 3.6, 2.2); s.add(up);
    const pts = []; for (let i = 0; i < 5; i++) { const a = arrow(.8, 0x9fe6ff); a.position.set(-4 + i * 2, LV - 1.9, 1.6); s.add(a); pts.push(a); }
    const d = dust(400, [24, 6, 8], 0xcfefff, .1, .5); d.position.y = 2; s.add(d);
    return t => {
      X.userData.upd(t); S.position.y = LV - DR + Math.sin(t * 1.3) * .05;
      const k = easeOut(prog(t, 19.2, .7)); up.userData.set(lerp(.01, 2.6, k)); up.visible = k > 0;
      pts.forEach((a, i) => { const kk = easeOut(prog(t, 17.6 + i * .1, .5)); a.visible = kk > 0; a.userData.set(.8 * kk + .1 * Math.sin(t * 6 + i)); });
      disp.material.opacity = (.25 + .25 * Math.sin(t * 5)) * prog(t, 18.9, .5); disp.visible = t > 18.9;
      d.rotation.y = t * .02;
      cam.position.set(Math.sin(t * .2) * 2, 5.0, 26); cam.lookAt(0, 4.6, 0); };
  } });
  // 6) Gemi kendi ağırlığı kadar suyu itene dek batar, sonra denge
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    lights(s, { key: 2000, rim: 0xffcf2e });
    const X = seaSection(LV); s.add(X); const S = ship(); S.scale.setScalar(.7); s.add(S); S.rotation.y = .25;
    const dn = arrow(1.4, 0xff4a3a); dn.rotation.z = Math.PI; s.add(dn); const up = arrow(2, 0xffcf2e); s.add(up);
    const sp = dust(160, [10, .6, 3], 0xffffff, .25, .8); s.add(sp);
    const d = dust(400, [24, 6, 8], 0xcfefff, .1, .5); d.position.y = 2; s.add(d);
    return t => {
      X.userData.upd(t);
      const k = prog(t, S7 + .1, 2.6); const sink = 1 - Math.exp(-k * 4) * Math.cos(k * 9); const y = lerp(LV + 2.2, LV - DR, sink);
      S.position.set(0, y + Math.sin(t * 1.3) * .04 * k, 0);
      const sub = clamp((LV - y) / DR); up.userData.set(.2 + 1.2 * sub); dn.userData.set(1.4);
      dn.position.set(-.6, y + 4.3, 1.4); up.position.set(.6, LV - 2.6, 1.4);
      const sk = prog(t, S7 + .45, .8); sp.visible = sk > 0 && sk < 1; sp.position.set(0, LV + .2 + sk * .6, 0); sp.scale.set(.6 + sk, 1 + sk * 2, .6 + sk); sp.material.opacity = .8 * (1 - sk);
      cam.position.set(0, 5.6, 27); cam.lookAt(0, 5.4, 0); };
  } });
  // 7) Gövde kesiti: içi hava dolu, ortalama yoğunluk < su
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    lights(s, { key: 1900 });
    const X = seaSection(LV); s.add(X); const S = ship({ cut: true }); S.scale.setScalar(.7); s.add(S); S.position.set(0, LV - DR, 0);
    const air = M(new THREE.BoxGeometry(8.4, 1.3, 1.3), new THREE.MeshStandardMaterial({ color: 0xbfe8ff, emissive: 0x7ec8ff, emissiveIntensity: .9, transparent: true, opacity: .5, depthWrite: false })); air.position.set(-.1, .85, 0); S.add(air);
    const motes = dust(260, [8, 1.2, 1.2], 0xffffff, .12, .9); motes.position.set(-.1, .85, 0); S.add(motes);
    const bars = new THREE.Group(); bars.position.set(0, LV + 3.7, 0); bars.scale.setScalar(.8); s.add(bars);
    const bl = [[-2.2, 0x9aa3ad, 2.4], [0, 0x3fa0ff, .3], [2.2, 0xffcf2e, .2]].map(([x, c, h]) => { const b = M(rb(1.3, 1, 1, .08), std(c, { metalness: .5, roughness: .3, emissive: c, emissiveIntensity: .25 })); b.position.x = x; bars.add(b); b.userData.h = h; return b; });
    return t => {
      X.userData.upd(t); S.position.y = LV - DR + Math.sin(t * 1.3) * .05; S.rotation.y = -.35 + Math.sin(t * .3) * .1;
      air.material.opacity = .35 + .2 * Math.sin(t * 4); motes.rotation.x = t * .2;
      bars.visible = t > 28.8; bl.forEach((b, i) => { const k = easeOut(prog(t, 28.9 + i * .3, .5)); b.scale.y = Math.max(.01, b.userData.h * k); b.position.y = b.userData.h * k / 2; });
      bars.rotation.y = -.25;
      cam.position.set(0, lerp(5.0, 6.6, ease(prog(t, 28.6, 1))), 26); cam.lookAt(0, lerp(4.6, 5.8, ease(prog(t, 28.6, 1))), 0); };
  } });
  // 8) Gövde delinir, su dolar, gemi batar
  shots.push({ t0: S9, t1: S10, fov: 40, build: (s, cam) => {
    lights(s, { key: 1800, rim: 0xff4a3a });
    const X = seaSection(LV); s.add(X); const S = ship({ cut: true }); S.scale.setScalar(.7); s.add(S);
    const fill = M(new THREE.BoxGeometry(8.6, 1, 1.4), waterM(.75)); S.add(fill);
    const hole = M(new THREE.CircleGeometry(.3, 24), new THREE.MeshBasicMaterial({ color: 0x050a12 })); hole.position.set(3.2, .35, .82); hole.rotation.y = .1; S.add(hole);
    const jet = dust(120, [.5, .5, 1.2], 0x9fe6ff, .18, .9); jet.position.set(3.2, .35, .3); S.add(jet);
    const B = bubbles(40, [6, 4.5, 2]); s.add(B);
    const alarm = new THREE.PointLight(0xff2a1a, 0, 30); alarm.position.set(0, 8, 6); s.add(alarm);
    return t => {
      X.userData.upd(t);
      const f = ease(prog(t, 32.0, 2.6)); fill.scale.y = Math.max(.01, f * 1.5); fill.position.set(-.1, .1 + f * .75, 0); fill.visible = f > 0;
      hole.visible = t > 31.9; jet.visible = t > 32.0 && f < 1; jet.rotation.z = t * 3;
      const sink = ease(prog(t, 33.3, 2.6)); S.position.set(0, LV - DR - sink * 3.0, 0); S.rotation.set(0, -.3, -sink * .28);
      B.position.set(1, LV - 4.4, 0); updBub(B, t, .4, sink > 0 ? 1 : 0);
      alarm.intensity = t > 32.6 ? 400 * (.5 + .5 * Math.sin(t * 8)) : 0;
      cam.position.set(0, 5.0, 26); cam.lookAt(0, 4.6, 0); };
  } });
  // 9) Sıradaki soru: uzayda kasksız astronot
  shots.push({ t0: S10, t1: 99, fov: 40, build: (s, cam) => {
    s.background = gradTex('#060b1a', '#000000'); s.fog = new THREE.Fog(0x000000, 80, 300);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, .4));
    const sun = new THREE.DirectionalLight(0xfff4e0, 3); sun.position.set(-10, 8, 10); s.add(sun);
    const rim = new THREE.PointLight(0x3fb6ff, 600, 60); rim.position.set(8, 6, -6); s.add(rim);
    const ec = []; const eg = new THREE.SphereGeometry(14, 96, 64); const P = eg.attributes.position;
    const cO = new THREE.Color(0x1a4f9a), cL = new THREE.Color(0x3f7a3a), cC = new THREE.Color(0xf4f8ff);
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i); const n = hash(x * .25, y * .25, z * .25) + .4 * hash(x * .7, z * .7, y * .7); const c = n > .55 ? cL : cO; const cc = c.clone(); if (hash(x * .5 + 3, y * .5, z * .5 + 1) > 1.0) cc.lerp(cC, .8); ec.push(cc.r, cc.g, cc.b); }
    eg.setAttribute('color', new THREE.Float32BufferAttribute(ec, 3)); const E = M(eg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .7 })); E.position.set(0, -12, -8); s.add(E);
    const atm = M(new THREE.SphereGeometry(14.5, 64, 48), new THREE.MeshBasicMaterial({ color: 0x4aa8ff, transparent: true, opacity: .18, side: THREE.BackSide })); atm.position.copy(E.position); s.add(atm);
    const stars = dust(1500, [120, 120, 40], 0xffffff, .25, .9); stars.position.z = -40; s.add(stars);
    const A = astronaut(); A.scale.setScalar(.7); s.add(A);
    const q = M(new THREE.TorusGeometry(.5, .12, 12, 32, Math.PI * 1.4), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); q.rotation.z = -Math.PI * .3; s.add(q);
    const qd = M(new THREE.SphereGeometry(.14, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffcf2e })); s.add(qd);
    return t => {
      const a = t - S10; E.rotation.y = t * .03;
      A.position.set(Math.sin(a * .3) * .4, 6.9 + Math.sin(a * .8) * .15, 0); A.rotation.set(Math.sin(a * .5) * .2, a * .25, .2 + Math.sin(a * .4) * .15);
      A.userData.limbs.forEach((l, i) => l.rotation.x = Math.sin(a * 1.2 + i) * .35);
      q.position.set(A.position.x + 1.7, A.position.y + 1.2, .5); qd.position.set(A.position.x + 1.6, A.position.y + .35, .5); q.visible = qd.visible = Math.sin(a * 4) > -.6;
      stars.rotation.z = a * .01;
      cam.position.set(0, 6.0, 16); cam.lookAt(0, 6.3, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'ÇELİK GEMİ NEDEN<br><span class="y">BATMAZ?</span>', 100) },
    { t0: S1, t1: S2, html: T('BİNLERCE TON ÇELİK', 'AMA <span class="y">YÜZER</span>') },
    { t0: S2, t1: S3, html: T('PEKİ', '<span class="y">NASIL?</span>', 130) },
    { t0: S3, t1: S4, html: BIG('ÇELİK, SUDAN', 'k8', 'DAHA YOĞUN', '8 KAT') },
    { t0: S4, t1: S5, html: T('SIR', '<span class="y">ŞEKİLDE</span> SAKLI') },
    { t0: S5, t1: 14.96, html: T('YASSILAŞTIR', 'İÇİ <span class="y">BOŞ</span> TEKNE') },
    { t0: 14.96, t1: S6, html: T('SONUÇ', 'DAHA ÇOK <span class="y">SU</span> İTER', 104) },
    { t0: S6, t1: S7, html: T('ARŞİMET İLKESİ', 'SU, CİSMİ <span class="y">YUKARI</span> İTER', 92) },
    { t0: S7, t1: S8, html: T('DENGE', 'AĞIRLIK = <span class="y">İTİLEN SU</span>', 96) },
    { t0: S8, t1: 28.8, html: T('GÖVDENİN İÇİ', 'HAVA <span class="y">DOLU</span>') },
    { t0: 28.8, t1: S9, html: T('ORTALAMA YOĞUNLUK', 'ÇELİK · SU · <span class="y">GEMİ</span>', 96) },
    { t0: S9, t1: S10, html: T('GÖVDE DELİNİRSE', 'GEMİ <span class="y">BATAR</span>') },
    { t0: S10, t1: 99, html: T('SIRADAKİ SORU', 'UZAYDA KASKSIZ<br>KALSAN NE <span class="y">OLUR?</span>', 96) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 41.24, shots, titles,
    update: (t, q) => { const k = q('k8'); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, S3, .5)))})`; },
    follow: { t: 39.44, click: 40.34 },
    sfx: [[1.25, 'snap', .8], [1.3, 'pop_low', .7], [3.0, 'whoosh', .5], [S3 + .7, 'crunch', .5], [7.6, 'pop', .5], [8.2, 'pop', .5], [8.8, 'ding', .7],
      [11.9, 'crunch', .6], [12.9, 'snap', .4], [14.0, 'ding', .5], [15.9, 'pop_low', .6], [19.2, 'whoosh', .6], [22.5, 'pop_low', .8], [24.5, 'ding', .6],
      [28.9, 'pop', .5], [29.2, 'pop', .5], [29.5, 'pop', .5], [32.0, 'crunch', .7], [33.4, 'boom', .7], [S10 + .3, 'whoosh', .6]],
  };
};
