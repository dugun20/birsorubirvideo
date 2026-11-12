// Bilgi #9: Volkan nasıl patlar? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: USGS "How do volcanoes erupt?" (kayalar erir → magma; çevresindeki kayadan hafif olduğu için yükselir ve magma
// odalarında birikir; akışkan magmada gaz kolay kaçar ve lav akar; koyu/yapışkan magmada gaz kaçamaz, basınç artar ve patlar);
// USGS "How hot is a Hawaiian volcano?" (Kīlauea lavı ~1.170 °C → "1.100 °C'yi aşan"); Science News Explores "How volcanoes erupt"
// (C. Till: volkan, gazoz şişesine benzer — basınç düşünce çözünmüş gaz kabarcık olur); Earth Observatory of Singapore:
// Pinatubo 15 Haziran 1991, 35 km yüksekliğinde kül sütunu.
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std, hash } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 97; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const soft = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(.4, 'rgba(255,255,255,.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
  function dust(n, sp, color = 0xffb27a, size = .25, op = .5, add = true) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3);
    for (let i = 0; i < n * 3; i += 3) { p[i] = (r1() - .5) * sp[0]; p[i + 1] = (r1() - .5) * sp[1]; p[i + 2] = (r1() - .5) * sp[2]; }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color, size, map: soft, transparent: true, opacity: op, depthWrite: false, blending: add ? THREE.AdditiveBlending : THREE.NormalBlending }));
  }
  function lights(s, o = {}) {
    s.background = gradTex(...(o.bg || ['#2a0f0a', '#030203'])); s.fog = new THREE.Fog(o.fog || 0x120604, o.near || 40, o.far || 150);
    s.add(new THREE.HemisphereLight(0xffc8a8, 0x0a0505, o.hemi || .7));
    const key = new THREE.SpotLight(0xfff1dc, o.key || 1800, 170, .5, .55, 1.2); key.position.set(-18, 44, 34); s.add(key); s.add(key.target);
    const rim = new THREE.PointLight(o.rim || 0xff6a2a, 800, 90); rim.position.set(20, 16, -14); s.add(rim);
    return key;
  }
  const lavaM = (i = 1.6) => new THREE.MeshStandardMaterial({ color: 0xff7a1a, emissive: 0xff4a00, emissiveIntensity: i, roughness: .6 });
  const rock = () => std(0x3a2d26, { roughness: .95 });
  // dış görünüş volkan (Lathe + gürültü)
  function volcano(h = 7, R = 12, rim = 1.8, pw = 1.8) {
    const pts = []; for (let i = 0; i <= 48; i++) { const k = i / 48; pts.push(new THREE.Vector2(rim + (R - rim) * Math.pow(1 - k, pw), h * k)); }
    pts.push(new THREE.Vector2(rim * .7, h - .5)); pts.push(new THREE.Vector2(.01, h - .6));
    const g = new THREE.LatheGeometry(pts, 180); const P = g.attributes.position; const col = [];
    const c1 = new THREE.Color(0x4a3a30), c2 = new THREE.Color(0x231a16), c3 = new THREE.Color(0x6a4a38);
    for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i); const k = y / h; const a = Math.atan2(z, x); const rr = Math.hypot(x, z) || 1;
      const n = (hash(x * .7, y * .7, z * .7) * .22 + Math.sin(a * 17) * .14 * (1 - k)) * Math.min(1, rr / 2) * (R / 12);
      P.setX(i, x + x / rr * n); P.setZ(i, z + z / rr * n);
      const c = c1.clone().lerp(c2, clamp(k * 1.2)).lerp(c3, clamp(hash(x * 2, y, z * 2) * .3)); col.push(c.r, c.g, c.b); }
    g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
    const grp = new THREE.Group(); grp.add(M(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .95 })));
    const cr = M(new THREE.CircleGeometry(rim * .78, 40), new THREE.MeshBasicMaterial({ color: 0xff8a2a })); cr.rotation.x = -Math.PI / 2; cr.position.y = h - .55; grp.add(cr);
    const gl = new THREE.PointLight(0xff5a1a, 600, 30); gl.position.y = h + 1.5; grp.add(gl);
    grp.userData = { h, R, rim, pw, crater: cr, glow: gl, rAt: k => rim + (R - rim) * Math.pow(1 - k, pw) };
    return grp;
  }
  function lavaStream(v, a, k0 = .98, k1 = .25, rad = .22) {
    const { h, rAt } = v.userData; const pts = [];
    for (let i = 0; i <= 30; i++) { const k = lerp(k0, k1, i / 30); const aa = a + Math.sin(i * .5) * .04; const r = rAt(k) + .12; pts.push(new THREE.Vector3(Math.cos(aa) * r, h * k + .05, Math.sin(aa) * r)); }
    const tg = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 90, rad, 10, false); const m = M(tg, lavaM(1.8));
    m.userData.grow = p => tg.setDrawRange(0, Math.floor(clamp(p) * 90) * 10 * 6); m.userData.grow(0); return m;
  }
  function ground(c = 0x1c1411) { const g = M(new THREE.CylinderGeometry(90, 90, 1, 64), std(c, { roughness: 1 })); g.position.y = -.5; return g; }
  function puffs(n, o = {}) { // kül bulutu küreleri
    const g = new THREE.Group(); const m = std(o.color || 0x6b625e, { roughness: 1, transparent: true, opacity: .95 }); const geo = new THREE.IcosahedronGeometry(1, 3);
    for (let i = 0; i < n; i++) { const p = M(geo, m); p.userData = { a: r1() * Math.PI * 2, r: r1(), f: i / n, s: .7 + r1() * .6 }; g.add(p); }
    g.userData.m = m; return g;
  }
  // kesit: kaya dilimi, baca + magma odası boşluğu
  const CX = 3.2, CY = 2.0, CRY = 1.3, CW = .35;
  function section() {
    const sh = new THREE.Shape(); sh.moveTo(-14, -1); sh.lineTo(-14, 4.5); sh.lineTo(-7, 4.5);
    for (let i = 1; i <= 20; i++) { const k = i / 20; sh.lineTo(-7 + 6 * k, 4.5 + 4.5 * Math.pow(k, 1.8)); }
    sh.lineTo(-CW, 8.6); const yT = CY + CRY * Math.sqrt(1 - (CW / CX) ** 2); sh.lineTo(-CW, yT);
    const a0 = Math.acos(-CW / CX), a1 = 2 * Math.PI + Math.acos(CW / CX);
    for (let i = 0; i <= 60; i++) { const a = lerp(a0, a1, i / 60); sh.lineTo(CX * Math.cos(a), CY + CRY * Math.sin(a)); }
    sh.lineTo(CW, 8.6); sh.lineTo(1, 9);
    for (let i = 1; i <= 20; i++) { const k = 1 - i / 20; sh.lineTo(7 - 6 * k, 4.5 + 4.5 * Math.pow(k, 1.8)); }
    sh.lineTo(14, 4.5); sh.lineTo(14, -1); sh.lineTo(-14, -1);
    const g = new THREE.ExtrudeGeometry(sh, { depth: 3, bevelEnabled: true, bevelSize: .08, bevelThickness: .08, bevelSegments: 2, curveSegments: 12 }); g.translate(0, 0, -1.5);
    const grp = new THREE.Group(); grp.add(M(g, std(0x3a2d26, { roughness: .95 })));
    // katman çizgileri (sadece ön yüzde, boşluk dışındaki şeritler)
    const lm = std(0x5e4a3c, { roughness: 1 });
    [[.2, 0x2e231e], [1.0, 0x5e4a3c], [3.9, 0x2e231e]].forEach(([y, c]) => { [-1, 1].forEach(k => { const b = M(new THREE.BoxGeometry(10, .18, .05), std(c, { roughness: 1 })); b.position.set(k * (CX + 5.4), y, 1.6); grp.add(b); }); });
    const mantle = M(new THREE.BoxGeometry(28.2, 3, 3), lavaM(1.1)); mantle.position.set(0, -2.5, 0); grp.add(mantle);
    const back = M(new THREE.PlaneGeometry(8, 9), new THREE.MeshBasicMaterial({ color: 0x1a0805 })); back.position.set(0, 4, -1.4); grp.add(back);
    const ch = M(new THREE.SphereGeometry(1, 48, 24), lavaM(1.4)); ch.scale.set(CX * .97, CRY * .95, 1.3); ch.position.set(0, CY, -.1); grp.add(ch);
    const cd = M(new THREE.CylinderGeometry(CW * .9, CW * .9, 1, 24), lavaM(1.6)); grp.add(cd);
    grp.userData = { ch, cd, mantle, setConduit: top => { const y0 = CY + CRY * .8; const hh = Math.max(.01, top - y0); cd.scale.y = hh; cd.position.set(0, y0 + hh / 2, 0); cd.visible = top > y0 + .02; } };
    return grp;
  }
  // göstergeli kaya baca (yakın plan)
  function conduitClose(o = {}) {
    const g = new THREE.Group(); const H = 9;
    [-1, 1].forEach(k => { const w = M(rb(3.2, H, 3, .3), rock()); w.position.set(k * 2.6, H / 2, 0); g.add(w);
      for (let i = 0; i < 6; i++) { const b = M(new THREE.DodecahedronGeometry(.3 + r1() * .4, 1), std(0x2c221d, { roughness: 1 })); b.position.set(k * (1.1 + r1() * .4), r1() * H, 1.4 + r1() * .3); g.add(b); } });
    const mag = M(new THREE.BoxGeometry(2, H, 1.6), new THREE.MeshStandardMaterial({ color: o.col || 0xff6a14, emissive: o.em || 0xff3a00, emissiveIntensity: o.ei || 1.1, transparent: true, opacity: .92, roughness: .5 }));
    mag.position.y = H / 2; g.add(mag);
    const n = o.n || 46; const bub = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 20, 14), new THREE.MeshStandardMaterial({ color: 0xffe9b0, emissive: 0xffb050, emissiveIntensity: .6, roughness: .15, metalness: .1, transparent: true, opacity: .9 }), n);
    g.add(bub); const bs = []; for (let i = 0; i < n; i++) bs.push([(r1() - .5) * 1.5, r1(), r1() * .6 + .4]);
    g.userData = { H, mag, bub, bs }; return g;
  }
  function gauge() {
    const g = new THREE.Group();
    g.add(M(new THREE.CylinderGeometry(1.3, 1.3, .3, 48).rotateX(Math.PI / 2), std(0x15181d, { metalness: .5, roughness: .4 })));
    const ring = M(new THREE.TorusGeometry(1.3, .14, 16, 64), std(0xaeb6c0, { metalness: .9, roughness: .25 })); g.add(ring);
    const red = M(new THREE.TorusGeometry(1.0, .09, 8, 40, Math.PI * .45), new THREE.MeshBasicMaterial({ color: 0xff2a1a })); red.rotation.z = -Math.PI * .2; red.position.z = .17; g.add(red);
    const grn = M(new THREE.TorusGeometry(1.0, .09, 8, 40, Math.PI * .55), new THREE.MeshBasicMaterial({ color: 0x2ad15a })); grn.rotation.z = Math.PI * .5; grn.position.z = .17; g.add(grn);
    const nd = new THREE.Group(); nd.position.z = .25; g.add(nd); const nb = M(new THREE.BoxGeometry(.08, 1.0, .06), new THREE.MeshBasicMaterial({ color: 0xffffff })); nb.position.y = .45; nd.add(nb);
    g.add(M(new THREE.SphereGeometry(.13, 16, 12), std(0xffcf2e, { metalness: .6 })).translateZ(.25));
    g.userData.set = k => nd.rotation.z = lerp(Math.PI * .75, -Math.PI * .6, k); return g;
  }
  function ship() {
    const sh = new THREE.Shape(); sh.moveTo(-4.8, -1); sh.lineTo(2.5, -1); sh.quadraticCurveTo(4.6, -.8, 5.4, 0); sh.quadraticCurveTo(4.6, .8, 2.5, 1); sh.lineTo(-4.8, 1); sh.quadraticCurveTo(-5.2, 0, -4.8, -1);
    const g = new THREE.ExtrudeGeometry(sh, { depth: 1.6, bevelEnabled: false, curveSegments: 24, steps: 8 }); g.rotateX(-Math.PI / 2);
    const P = g.attributes.position; const col = []; const cR = new THREE.Color(0x9b2a20), cW = new THREE.Color(0xe8e8e8), cB = new THREE.Color(0x1f2d44);
    for (let i = 0; i < P.count; i++) { const y = P.getY(i); const k = y / 1.6; P.setZ(i, P.getZ(i) * lerp(.45, 1, Math.pow(k, .6))); if (P.getX(i) > 2) P.setX(i, P.getX(i) + (1 - k) * -.5 * ((P.getX(i) - 2) / 3.4));
      const c = k < .36 ? cR : (k < .42 ? cW : cB); col.push(c.r, c.g, c.b); }
    g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
    const grp = new THREE.Group(); grp.add(M(g, new THREE.MeshStandardMaterial({ vertexColors: true, metalness: .55, roughness: .4 })));
    const deck = M(rb(9.6, .12, 1.9, .05), std(0x5a6068, { metalness: .5 })); deck.position.set(-.1, 1.62, 0); grp.add(deck);
    const sup = M(rb(1.6, 1.5, 1.7, .08), std(0xeef0f2, { roughness: .4 })); sup.position.set(-3.8, 2.4, 0); grp.add(sup);
    const win = M(new THREE.BoxGeometry(.05, .18, 1.5), new THREE.MeshBasicMaterial({ color: 0xffd98a })); win.position.set(-2.98, 2.8, 0); grp.add(win);
    const br = M(rb(2.0, .3, 2.1, .06), std(0xeef0f2)); br.position.set(-3.8, 3.25, 0); grp.add(br);
    const fn = M(new THREE.CylinderGeometry(.28, .34, 1.2, 24), std(0xc0392b, { roughness: .5 })); fn.position.set(-4.3, 3.9, 0); grp.add(fn);
    const cc = [0xc0392b, 0x2563eb, 0xf59e0b, 0x0d9488, 0xe5e7eb, 0x7c3aed];
    for (let x = 0; x < 6; x++) for (let z = 0; z < 2; z++) for (let y = 0; y < 2; y++) { if (y === 1 && (x + z) % 3 === 0) continue;
      const b = M(rb(.95, .6, .82, .04), std(cc[(x * 3 + z + y * 2) % 6], { roughness: .5, metalness: .3 })); b.position.set(-2.2 + x * 1.0, 1.98 + y * .62, (z - .5) * .86); grp.add(b); }
    const ml = new THREE.PointLight(0xffd98a, 60, 6); ml.position.set(-2.6, 2.9, 1.5); grp.add(ml);
    return grp;
  }
  function sea(size = 160, seg = 110, c = 0x0b2a44) {
    const g = new THREE.PlaneGeometry(size, size, seg, seg); g.rotateX(-Math.PI / 2); const P = g.attributes.position; const base = Float32Array.from(P.array);
    const m = M(g, std(c, { metalness: .35, roughness: .3 }));
    m.userData.upd = t => { for (let i = 0; i < P.count; i++) { const x = base[i * 3], z = base[i * 3 + 2]; P.setY(i, Math.sin(x * .35 + t * 1.3) * .14 + Math.sin(z * .5 + t * .9 + x * .2) * .1); } P.needsUpdate = true; g.computeVertexNormals(); };
    return m;
  }

  const W0 = t => WORDS.find(w => w[1] >= t - .01)[1];
  const S1 = 6.72, S2 = 9.92, S3 = 14.72, S4 = 18.72, S5 = 22.8, S6 = 26.88, S7 = 29.92, S8 = 33.36, S9 = 38.16;
  const BOOM = 32.25;

  // 1) Gece, kızgın kraterli volkan; lav akıntıları
  shots.push({ t0: 0, t1: S1, fov: 40, build: (s, cam) => {
    lights(s, { key: 1300 });
    const v = volcano(7, 12); s.add(v); s.add(ground());
    const st = [0.3, 1.5, 2.5, 4.0, 5.3].map(a => { const m = lavaStream(v, a + 1.2, .97, .2, .2); s.add(m); return m; });
    const sm = dust(700, [8, 14, 8], 0x7a6a64, .9, .35, false); sm.position.y = 14; s.add(sm);
    const emb = dust(300, [10, 10, 10], 0xff8a3a, .14, .9); emb.position.y = 10; s.add(emb);
    return t => {
      st.forEach((m, i) => m.userData.grow(prog(t, .2 + i * .3, 4.5)));
      v.userData.glow.intensity = 600 + 200 * Math.sin(t * 9) + (t > 4.5 ? 300 * Math.sin(t * 23) : 0);
      sm.position.y = 13 + (t * .8) % 3; sm.rotation.y = t * .1; emb.position.y = 9 + (t * 1.6) % 4;
      const sh = t > 4.6 ? .08 * Math.sin(t * 40) : 0;
      cam.position.set(Math.sin(t * .12) * 4 + sh, lerp(9, 7.5, ease(prog(t, 0, S1))), lerp(34, 29, ease(prog(t, 0, S1)))); cam.lookAt(0, 6.6, 0); };
  } });
  // 2) Yerin altında kayalar erir -> magma
  shots.push({ t0: S1, t1: S2, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1a0905', '#030203'], key: 1200, rim: 0xff4a1a });
    const blocks = []; const geo = rb(1.5, 1.2, 1.5, .25);
    for (let x = 0; x < 5; x++) for (let z = 0; z < 3; z++) { const m = new THREE.MeshStandardMaterial({ color: 0x4a3a30, roughness: .9, emissive: 0xff4a00, emissiveIntensity: 0 });
      const b = M(geo, m); b.position.set((x - 2) * 1.65, 4.2, (z - 1) * 1.65 - 1); b.rotation.y = r1() * .3; b.userData = { d: r1() * .8, base: b.position.clone() }; s.add(b); blocks.push(b); }
    const pool = M(new THREE.CylinderGeometry(5.2, 5.4, .3, 64), lavaM(1.6)); pool.position.set(0, 3.55, -1); s.add(pool);
    const heat = new THREE.PointLight(0xff5a1a, 0, 30); heat.position.set(0, 2, 3); s.add(heat);
    const bed = M(new THREE.CylinderGeometry(9, 9, 1, 64), std(0x231915, { roughness: 1 })); bed.position.y = 3; s.add(bed);
    const emb = dust(400, [12, 6, 8], 0xff8a3a, .14, .9); emb.position.y = 6; s.add(emb);
    return t => {
      blocks.forEach(b => { const u = b.userData; const k = prog(t, S1 + .3 + u.d, 1.4); const m2 = ease(prog(t, 8.2 + u.d * .6, 1.2));
        b.material.emissiveIntensity = k * 1.4; b.material.color.setRGB(lerp(.29, .9, k), lerp(.23, .3, k), lerp(.19, .05, k));
        b.scale.set(1 + m2 * .25, Math.max(.05, 1 - m2 * .92), 1 + m2 * .25); b.position.y = u.base.y - m2 * .55; });
      const pk = ease(prog(t, 8.4, 1.2)); pool.scale.set(Math.max(.01, pk), 1, Math.max(.01, pk)); pool.visible = pk > 0;
      heat.intensity = 900 * prog(t, S1, 2); emb.position.y = 5 + ((t - S1) * 1.5) % 3;
      cam.position.set(Math.sin(t * .3) * 2, 11, lerp(20, 17.5, ease(prog(t, S1, S2 - S1)))); cam.lookAt(0, 6.2, 0); };
  } });
  // 3) Kesit: magma yükselir, odada birikir
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    lights(s, { key: 800, near: 50, far: 160, hemi: .5 });
    const X = section(); s.add(X); const { ch, setConduit } = X.userData;
    const blobs = []; for (let i = 0; i < 14; i++) { const b = M(new THREE.SphereGeometry(.35 + r1() * .25, 24, 16), lavaM(.9)); b.userData = { x: (r1() - .5) * 4.5, o: r1() * 2.8 }; s.add(b); blobs.push(b); }
    const lbl = new THREE.PointLight(0xff6a1a, 500, 16); lbl.position.set(0, 2, 4); s.add(lbl);
    return t => {
      const fill = ease(prog(t, 12.6, 2.0)); ch.scale.set(CX * .97 * Math.max(.05, lerp(.25, 1, fill)), CRY * .95 * Math.max(.05, lerp(.25, 1, fill)), 1.3); ch.visible = t > 10.6; setConduit(0);
      blobs.forEach(b => { const u = b.userData; const f = ((t - S2 + u.o) % 2.8) / 2.8; b.position.set(u.x * (1 - f * .7), lerp(-1.6, CY, f), .9); b.scale.setScalar(Math.max(.01, Math.sin(f * Math.PI) * 1.2)); b.visible = t < 14.2; });
      lbl.intensity = 60 + 120 * fill;
      cam.position.set(Math.sin(t * .2) * 1.5, 4.6, 32); cam.lookAt(0, 4.4, 0); };
  } });
  // 4) Gazoz şişesi: çözünmüş gaz, kapak açılınca kabarcıklar
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1c1426', '#030203'], rim: 0xff8a3a, key: 1700 });
    const prof = [[0, 0], [1.2, 0], [1.35, .15], [1.4, .6], [1.4, 3.6], [1.2, 4.4], [.62, 5.5], [.5, 6.2], [.55, 6.35], [.5, 6.45]].map(([x, y]) => new THREE.Vector2(x, y));
    const B = new THREE.Group(); B.position.set(0, 1.8, 0); s.add(B);
    B.add(M(new THREE.LatheGeometry(prof, 64), new THREE.MeshPhysicalMaterial({ color: 0xbfe6d0, roughness: .05, metalness: .1, transparent: true, opacity: .32, side: THREE.DoubleSide })));
    const liq = M(new THREE.LatheGeometry(prof.slice(0, 7).map(v => new THREE.Vector2(v.x * .92, v.y * .98 + .04)), 64), new THREE.MeshStandardMaterial({ color: 0xe0661a, emissive: 0x7a2a00, emissiveIntensity: .7, roughness: .2, transparent: true, opacity: .8 }));
    B.add(liq);
    const cap = M(new THREE.CylinderGeometry(.62, .62, .4, 32), std(0xc0392b, { metalness: .6, roughness: .3 })); cap.position.y = 6.55; B.add(cap);
    const n = 70; const bub = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 16, 12), new THREE.MeshStandardMaterial({ color: 0xfff4d8, emissive: 0xffc070, emissiveIntensity: .5, roughness: .1, transparent: true, opacity: .9 }), n); B.add(bub);
    const bs = []; for (let i = 0; i < n; i++) bs.push([r1() * Math.PI * 2, r1(), r1()]);
    const foam = dust(260, [1, 3, 1], 0xfff4e0, .25, .8, false); foam.position.y = 7.5; B.add(foam);
    const d = dust(300, [30, 30, 20], 0xffb27a, .12, .5); d.position.y = 5; s.add(d);
    const OP = 17.35; const dm = new THREE.Object3D();
    return t => {
      const o = prog(t, OP, .4); cap.position.set(o * 1.4, 6.55 + o * 3.2, 0); cap.rotation.z = -o * 2.5; cap.visible = o < 1;
      bs.forEach(([a, f0, r], i) => { const sp = t < OP ? .02 : .5 + r * .6; const f = (f0 + (t - S3) * sp) % 1; const ri = r * 1.05 * (f < .75 ? 1 : .5);
        dm.position.set(Math.cos(a) * ri, .3 + f * 4.6, Math.sin(a) * ri); dm.scale.setScalar(t < OP ? .03 + .02 * r : (.06 + f * .16) * (.6 + r)); dm.updateMatrix(); bub.setMatrixAt(i, dm.matrix); });
      bub.instanceMatrix.needsUpdate = true;
      const fk = prog(t, OP + .2, 1); foam.visible = fk > 0; foam.scale.setScalar(Math.max(.01, fk)); foam.position.y = 6.6 + fk * 1.2;
      B.rotation.y = t * .3; d.rotation.y = t * .03;
      cam.position.set(0, 5.6, 19.5); cam.lookAt(0, 6.0, 0); };
  } });
  // 5) Baca: magma yükseldikçe basınç düşer, kabarcıklar büyür
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    lights(s, { key: 1400 });
    const C = conduitClose(); C.position.set(0, 1, 0); s.add(C); const { H, bub, bs } = C.userData;
    const G = gauge(); G.position.set(2.6, 5.4, 1.9); G.scale.setScalar(.75); s.add(G);
    const d = dust(400, [20, 20, 10], 0xff8a3a, .12, .6); d.position.y = 5; s.add(d); const dm = new THREE.Object3D();
    return t => {
      bs.forEach(([x, f0, r], i) => { const f = (f0 + (t - S4) * .22 * r) % 1; dm.position.set(x * (1 - f * .3), f * H, .5); const grow = prog(t, 20.6, 1.2);
        dm.scale.setScalar(lerp(.04, lerp(.12, .5, Math.pow(f, 1.3)), lerp(.25, 1, grow)) * (.7 + r * .5)); dm.updateMatrix(); bub.setMatrixAt(i, dm.matrix); });
      bub.instanceMatrix.needsUpdate = true;
      G.userData.set(lerp(.85, .2, ease(prog(t, 19.6, 1.4)))); G.rotation.y = -.3;
      d.position.y = 5 + ((t - S4) * 1) % 3;
      cam.position.set(Math.sin(t * .25) * 1.5, lerp(4.5, 7.5, ease(prog(t, S4, S5 - S4))), 21); cam.lookAt(0, lerp(5.6, 7.0, ease(prog(t, S4, S5 - S4))), 0); };
  } });
  // 6) Akışkan magma: kalkan volkan, sakin akan lav
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#1f0c08', '#030203'], key: 1300 });
    const v = volcano(3.4, 15, 1.6, 1.2); s.add(v); s.add(ground());
    const st = [0, .9, 1.9, 3.1, 4.2, 5.3].map(a => { const m = lavaStream(v, a, .96, .05, .3); s.add(m); return m; });
    const gas = dust(400, [3, 6, 3], 0xd8d0c8, .5, .35, false); gas.position.y = 6; s.add(gas);
    return t => {
      st.forEach((m, i) => m.userData.grow(prog(t, S5 + i * .15, 3.8)));
      v.userData.glow.intensity = 500 + 80 * Math.sin(t * 5); gas.position.y = 5.5 + ((t - S5) * .9) % 2.5; gas.rotation.y = t * .2;
      cam.position.set(Math.sin(t * .15) * 6, 15, 31); cam.lookAt(0, 4.6, 0); };
  } });
  // 7) Koyu, yapışkan magma: gaz hapsolur, basınç artar
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    lights(s, { key: 1400 });
    const C = conduitClose({ col: 0x8a1a08, em: 0x5a0a00, ei: 1.0, n: 40 }); C.position.set(0, 1, 0); s.add(C); const { H, bub, bs } = C.userData;
    const plug = M(new THREE.DodecahedronGeometry(1.6, 2), std(0x2a201b, { roughness: 1 })); plug.scale.set(1.25, .6, 1); plug.position.set(0, 1 + H - .3, .3); s.add(plug);
    const G = gauge(); G.position.set(2.6, 5.6, 1.9); G.scale.setScalar(.75); s.add(G);
    const cracks = []; for (let i = 0; i < 6; i++) { const c = M(new THREE.BoxGeometry(.06, .7 + r1(), .05), new THREE.MeshBasicMaterial({ color: 0xffa040 })); c.position.set((r1() - .5) * 2.2, 1 + H - .3 + (r1() - .5) * .6, 1.3); c.rotation.z = (r1() - .5) * 1.5; s.add(c); cracks.push(c); }
    const dm = new THREE.Object3D();
    return t => {
      const k = prog(t, S6, S7 - S6);
      bs.forEach(([x, f0, r], i) => { const f = Math.min(.93 - r * .1, f0 * .5 + .45 + k * .4 * r); dm.position.set(x, f * H, .5); dm.scale.setScalar((.18 + .32 * k * r) * (.7 + r * .4)); dm.updateMatrix(); bub.setMatrixAt(i, dm.matrix); });
      bub.instanceMatrix.needsUpdate = true;
      G.userData.set(lerp(.3, .97, ease(k)) + Math.sin(t * 30) * .02 * k); G.rotation.y = -.3;
      plug.position.x = Math.sin(t * 37) * .05 * k; cracks.forEach((c, i) => { c.visible = k > .3 + i * .1; });
      cam.position.set(Math.sin(t * 40) * .05 * k, 7.6, 20); cam.lookAt(0, 7.3, 0); };
  } });
  // 8) Patlama
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    lights(s, { key: 1300 });
    const v = volcano(7, 12); s.add(v); s.add(ground());
    const bombs = []; const bm = new THREE.MeshStandardMaterial({ color: 0x3a1a10, emissive: 0xff3a00, emissiveIntensity: .7, roughness: .8 }); for (let i = 0; i < 90; i++) { const b = M(new THREE.DodecahedronGeometry(.18 + r1() * .3, 1), bm); b.userData = { a: r1() * Math.PI * 2, v: 1.5 + r1() * 4, u: 7 + r1() * 9, o: r1() * .6 }; s.add(b); bombs.push(b); }
    const P = puffs(46, { color: 0x4a4440 }); s.add(P);
    const flash = new THREE.PointLight(0xffb060, 0, 80); flash.position.set(0, 10, 6); s.add(flash);
    const emb = dust(500, [12, 18, 12], 0xff8a3a, .16, .9); emb.position.y = 14; s.add(emb);
    return t => {
      const a = t - BOOM; const pre = prog(t, S7, BOOM - S7);
      v.userData.glow.intensity = 500 + 900 * pre + 400 * Math.sin(t * 25) * pre;
      bombs.forEach(b => { const u = b.userData; const tt = a - u.o; b.visible = tt > 0 && tt < 2.6; if (b.visible) b.position.set(Math.cos(u.a) * u.v * tt, 6.6 + u.u * tt - 4.9 * tt * tt, Math.sin(u.a) * u.v * tt); b.rotation.set(tt * 3, tt * 2, 0); });
      P.children.forEach(p => { const u = p.userData; const k = easeOut(prog(a, u.f * .5, 1.6)); p.visible = a > u.f * .5;
        const hgt = 6.8 + u.f * 9 * k + k * 1.5; const rad = (.6 + u.f * 1.8) * k * u.s; p.position.set(Math.cos(u.a) * u.r * rad * .8, hgt, Math.sin(u.a) * u.r * rad * .8); p.scale.setScalar(Math.max(.01, rad * 1.2)); });
      flash.intensity = a > 0 ? 1400 * Math.exp(-a * 3) : 0; emb.visible = a > 0; emb.position.y = 12 + (a * 2) % 4;
      const sh = (a > 0 ? .5 * Math.exp(-a * 2) : .15 * pre) * Math.sin(t * 45);
      cam.position.set(sh, 7.5 + sh * .5, lerp(31, 36, ease(prog(a, 0, 1)))); cam.lookAt(0, lerp(7.2, 8.6, ease(prog(a, 0, 1))), 0); };
  } });
  // 9) Pinatubo 1991: 35 km kül sütunu
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    lights(s, { bg: ['#2b1f1c', '#060404'], key: 1500, far: 220 });
    const v = volcano(2.6, 7, 1.0); s.add(v); s.add(ground(0x2a201a));
    const P = puffs(70, { color: 0x8a817c }); s.add(P);
    const strat = M(new THREE.PlaneGeometry(60, 60), new THREE.MeshBasicMaterial({ color: 0x9fd0ff, transparent: true, opacity: .08, side: THREE.DoubleSide, depthWrite: false })); strat.rotation.x = -Math.PI / 2; strat.position.y = 10; s.add(strat);
    const ash = dust(800, [20, 4, 20], 0x9a908a, .6, .35, false); s.add(ash);
    return t => {
      const a = t - S8; const k = ease(prog(a, 0, 3.6)); const top = 2.6 + 12.4 * k;
      P.children.forEach(p => { const u = p.userData; const y = lerp(2.4, top, u.f); const um = Math.max(0, (u.f - .8) / .2);
        const rad = .5 + u.f * 1.6 + um * 3.5; p.position.set(Math.cos(u.a + a * .2) * u.r * rad, y + Math.sin(a + u.a) * .15, Math.sin(u.a + a * .2) * u.r * rad * .6); p.scale.setScalar((.8 + u.f * 1.4 + um * 1.2) * u.s); p.visible = u.f * 12.4 + 2.4 < top + .5; });
      ash.position.y = top - 1; ash.scale.setScalar(Math.max(.01, k)); ash.rotation.y = a * .05;
      cam.position.set(Math.sin(a * .1) * 4, 6, 44); cam.lookAt(0, 8.4, 0); };
  } });
  // 10) Sıradaki soru: dalgalarda yüzen çelik gemi
  shots.push({ t0: S9, t1: 99, fov: 40, build: (s, cam) => {
    s.background = gradTex('#0d2240', '#02060e'); s.fog = new THREE.Fog(0x050d1c, 30, 120);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x0a0a12, .9));
    const key = new THREE.SpotLight(0xfff1dc, 2000, 160, .5, .55, 1.2); key.position.set(-18, 40, 30); s.add(key);
    const rim = new THREE.PointLight(0x3fb6ff, 700, 90); rim.position.set(20, 14, -14); s.add(rim);
    const W = sea(); s.add(W); const S = ship(); s.add(S);
    const d = dust(400, [40, 20, 30], 0xcfe8ff, .12, .5); d.position.y = 8; s.add(d);
    return t => {
      const a = t - S9; W.userData.upd(t);
      S.position.set(lerp(-3, 0, ease(prog(a, 0, 2))), -.58 + Math.sin(t * 1.3) * .08, 0); S.rotation.set(Math.sin(t * .9) * .03, -.75 + a * .05, Math.sin(t * 1.1) * .03);
      d.rotation.y = t * .03;
      cam.position.set(0, 8, 31); cam.lookAt(0, 3.6, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: 1.8, html: T('BİR SORU', 'VOLKAN NASIL <span class="y">PATLAR?</span>', 104) },
    { t0: 1.8, t1: 4.48, html: BIG('DERİNLERDE', 'tc', 'ERİMİŞ KAYA', '1.100°C+') },
    { t0: 4.48, t1: S1, html: T('PEKİ', 'NASIL <span class="y">PATLAR?</span>') },
    { t0: S1, t1: S2, html: T('YERİN ALTINDA', 'KAYA ERİR, <span class="y">MAGMA</span> OLUR', 92) },
    { t0: S2, t1: 12.96, html: T('MAGMA HAFİFTİR', 'YUKARI <span class="y">YÜKSELİR</span>', 100) },
    { t0: 12.96, t1: S3, html: T('BİRİKİR', 'MAGMA <span class="y">ODASI</span>') },
    { t0: S3, t1: S4, html: T('İÇİNDE ÇÖZÜNMÜŞ GAZ', 'TIPKI <span class="y">GAZOZ</span> GİBİ') },
    { t0: S4, t1: 20.88, html: T('MAGMA YÜKSELDİKÇE', 'BASINÇ <span class="y">DÜŞER</span>') },
    { t0: 20.88, t1: S5, html: T('GAZ', 'KABARCIKLAR <span class="y">BÜYÜR</span>', 100) },
    { t0: S5, t1: S6, html: T('AKIŞKAN MAGMA', 'LAV <span class="y">SAKİN</span> AKAR') },
    { t0: S6, t1: S7, html: T('KOYU VE YAPIŞKAN', 'GAZ <span class="y">HAPSOLUR</span>', 104) },
    { t0: S7, t1: 32.2, html: T('BASINÇ', 'KAYAYI <span class="y">YENER...</span>') },
    { t0: 32.2, t1: S8, html: T('VE', 'VOLKAN <span class="y">PATLAR!</span>', 120) },
    { t0: S8, t1: S9, html: BIG('PİNATUBO · 1991', 'km', 'KÜL BULUTU', '0 KM') },
    { t0: S9, t1: 99, html: T('SIRADAKİ SORU', 'TONLARCA ÇELİK GEMİ<br>NEDEN <span class="y">BATMAZ?</span>', 92) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  return {
    END: 43.72, shots, titles,
    update: (t, q) => {
      const km = q('km'); if (km) km.textContent = Math.round(35 * ease(prog(t - S8, 0, 3.6))) + ' KM';
      const tc = q('tc'); if (tc) tc.style.transform = `scale(${lerp(.6, 1, back(prog(t, 1.8, .5)))})`;
    },
    follow: { t: 41.92, click: 42.82 },
    sfx: [[.2, 'boom', .5], [1.85, 'ding', .7], [4.6, 'crunch', .5], [8.3, 'pop_low', .6], [10.6, 'pop_low', .5], [12.8, 'ding', .5], [17.35, 'pop', 1], [17.45, 'snap', .5],
      [20.6, 'pop', .5], [21.0, 'pop', .5], [23.0, 'whoosh', .5], [28.6, 'crunch', .5], [30.5, 'crunch', .6], [BOOM, 'boom', 1.2], [BOOM + .02, 'crunch', .8], [S8 + .3, 'whoosh', .7], [S8 + 3.6, 'ding', .7]],
  };
};
