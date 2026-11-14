// Bilgi #13: Hapşırırken gözlerimiz neden kapanır? (koyu sinematik tarz, videos/asansor şablonu)
// Kaynaklar: NBC News / Mayo Clinic (Bert Moritz): gözlerin kapanması diz refleksine benzer istemsiz bir refleks; gözün fırlaması
// modern tıpta kanıtı olmayan bir efsane, her göz 6 göz dışı kasla yuvasına bağlı; zorlanırsa gözler açık hapşırılabilir.
// Live Science "7 Tickling Facts About Sneezing": refleks göz kapaklarından sfinktere kadar kasları kasar, sebebi tam bilinmiyor.
// Bourouiba, JAMA 2020: hapşırık gaz bulutu ve damlacıklar 7–8 m'ye kadar yayılabilir. Hapşırık merkezi beyin sapındadır (medulla).
import { RoundedBoxGeometry } from '../../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export default (L, WORDS) => {
  const { THREE, prog, ease, easeOut, back, lerp, clamp, gradTex, std } = L;
  const shots = [];
  const rb = (w, h, d, r = .15) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2) * .99);
  const M = (g, m) => new THREE.Mesh(g, m);
  let seed = 1313; const r1 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
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
    const fill = new THREE.PointLight(0xffe2c8, 260, 40); fill.position.set(4, 8, 14); s.add(fill);
    return key;
  }
  const skin = () => std(0xd9b49a, { roughness: .55 });
  // kafa: gözler (göz kapaklı), burun, ağız
  function face() {
    const H = new THREE.Group();
    const head = M(new THREE.SphereGeometry(2, 64, 48), skin()); head.scale.set(1, 1.15, 1); H.add(head);
    const hair = M(new THREE.SphereGeometry(2.06, 64, 32, 0, Math.PI * 2, 0, Math.PI * .42), std(0x2a1c14, { roughness: .8 })); hair.rotation.x = -.05; hair.scale.set(1, 1.15, 1); H.add(hair);
    const nose = M(new THREE.SphereGeometry(.34, 32, 24), std(0xd0a088, { roughness: .55 })); nose.scale.set(.9, 1.1, 1); nose.position.set(0, -.15, 1.95); H.add(nose);
    [-1, 1].forEach(k => { const ear = M(new THREE.SphereGeometry(.4, 24, 16), skin()); ear.scale.set(.4, 1, .7); ear.position.set(k * 1.98, 0, 0); H.add(ear); });
    const eyes = [-1, 1].map(k => { const e = new THREE.Group(); e.position.set(k * .7, .45, 1.72); H.add(e);
      const w = M(new THREE.SphereGeometry(.32, 32, 24), std(0xffffff, { roughness: .25 })); w.scale.z = .5; e.add(w);
      const ir = M(new THREE.SphereGeometry(.17, 24, 16), std(0x3a6a9a, { roughness: .3 })); ir.position.z = .1; ir.scale.z = .5; e.add(ir);
      const p = M(new THREE.SphereGeometry(.09, 16, 12), new THREE.MeshBasicMaterial({ color: 0x0a0a0a })); p.position.z = .17; e.add(p);
      const lid = M(new THREE.SphereGeometry(.345, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), std(0xc99c84, { roughness: .6, side: THREE.DoubleSide })); e.add(lid);
      const brow = M(new THREE.CapsuleGeometry(.06, .4, 6, 12), std(0x2a1c14)); brow.rotation.z = Math.PI / 2; brow.position.set(0, .4, .08); e.add(brow);
      return { e, lid, brow }; });
    const mouth = M(new THREE.SphereGeometry(.4, 32, 16), new THREE.MeshBasicMaterial({ color: 0x5a1a1a })); mouth.scale.set(1.1, .3, .4); mouth.position.set(0, -.95, 1.8); H.add(mouth);
    // k: 0 = açık, 1 = kapalı (kapak yarım küresi yukarıdan aşağı iner)
    const setLids = k => eyes.forEach(({ lid }) => { lid.rotation.x = lerp(-Math.PI * .02, Math.PI * .5, k) - Math.PI * .5; });
    setLids(0);
    return { H, eyes, mouth, nose, setLids };
  }
  // hapşırık döngüsü: 0..1 içinde ön (nefes) -> patlama
  function burst(n, color = 0xdff4ff) {
    const g = new THREE.BufferGeometry(); const p = new Float32Array(n * 3); const v = [];
    for (let i = 0; i < n; i++) { const a = r1() * Math.PI * 2, r = Math.pow(r1(), .7); v.push([Math.cos(a) * r * .35, Math.sin(a) * r * .3 - .05, .8 + r1() * .6]); }
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    const pts = new THREE.Points(g, new THREE.PointsMaterial({ color, size: .16, map: soft, transparent: true, opacity: .9, depthWrite: false, blending: THREE.AdditiveBlending }));
    pts.userData.set = (k, len = 6) => { for (let i = 0; i < n; i++) { const [x, y, z] = v[i]; const d = len * Math.pow(k, .6) * z; p[i * 3] = x * d * 1.2; p[i * 3 + 1] = y * d * 1.2 - k * k * .6 * z; p[i * 3 + 2] = d; } g.attributes.position.needsUpdate = true; pts.material.opacity = .9 * (1 - prog(k, .6, .4)); };
    pts.userData.set(0); return pts;
  }

  const S1 = 2.96, S2 = 4.56, S3 = 7.36, S4 = 11.8, S5 = 14.6, S6 = 17.84, S7 = 22.4, S8 = 25.08, S9 = 31.44, S10 = 35.36;

  // 1) Yüz: gözleri açık tutmaya çalışır, hapşırır, gözler kapanır
  shots.push({ t0: 0, t1: S2, fov: 40, build: (s, cam) => {
    lights(s, { key: 1700 });
    const F = face(); F.H.position.set(0, 6.4, 0); F.H.scale.setScalar(.9); s.add(F.H);
    const sp = burst(500); sp.position.set(0, 5.5, 1.9); s.add(sp);
    const d = dust(400, [30, 20, 20], 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      // 0-2.4: gerilip gözleri açık tutar (kaşlar yukarı), 2.6'da hapşırık + kapanma, sonra tekrar
      const sn = t < 3.1 ? prog(t, 2.55, .12) * (1 - prog(t, 3.0, .2)) : (((t - 3.1) % 1.6) > .7 && ((t - 3.1) % 1.6) < 1.1 ? 1 : 0);
      const pre = t < 2.55 ? ease(prog(t, .3, 2.2)) : 0;
      F.setLids(Math.max(sn, .18 * pre * (.5 + .5 * Math.sin(t * 14))));
      F.eyes.forEach(({ brow }) => brow.position.y = .45 + pre * .12);
      F.H.rotation.set(-pre * .2 + sn * .3, Math.sin(t * .4) * .25, 0);
      F.mouth.scale.set(1.1, .3 + pre * .35 + sn * .2, .4);
      const k1 = prog(t, 2.6, 1.0), k2 = t > 3.1 ? prog((t - 3.1) % 1.6, .7, .9) : 0;
      sp.userData.set(t < 3.6 ? k1 : k2, 7); sp.visible = (t > 2.6 && t < 3.6) || k2 > 0;
      d.rotation.y = t * .03;
      cam.position.set(Math.sin(t * .2) * 1.5, 6.2, lerp(17, 15, ease(prog(t, 0, S2)))); cam.lookAt(0, 6.0, 0); };
  } });
  // 2) Toz buruna kaçar, sinir sinyali beyin sapına gider
  shots.push({ t0: S2, t1: S3, fov: 40, build: (s, cam) => {
    lights(s, { key: 1400, rim: 0xff4a8a });
    const G = new THREE.Group(); G.position.set(0, 6.2, 0); G.rotation.y = -Math.PI / 2 + .35; s.add(G);
    const shell = M(new THREE.SphereGeometry(2, 64, 48), new THREE.MeshPhysicalMaterial({ color: 0xd9b49a, roughness: .4, transparent: true, opacity: .22, depthWrite: false })); shell.scale.set(1, 1.15, 1.05); G.add(shell);
    const nose = M(new THREE.SphereGeometry(.4, 32, 24), new THREE.MeshPhysicalMaterial({ color: 0xd0a088, transparent: true, opacity: .35, depthWrite: false })); nose.position.set(0, -.2, 2.0); G.add(nose);
    const brain = M(new THREE.SphereGeometry(1.25, 64, 48), std(0xf0a0a8, { roughness: .5, emissive: 0x501020, emissiveIntensity: .3 }));
    { const P = brain.geometry.attributes.position; for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i); const n = 1 + .04 * Math.sin(x * 9 + y * 7) * Math.cos(z * 8 - y * 5); P.setXYZ(i, x * n, y * n, z * n); } brain.geometry.computeVertexNormals(); }
    brain.scale.set(1, .8, 1.2); brain.position.set(0, .7, -.2); G.add(brain);
    const stemM = std(0xff7a3a, { emissive: 0xff4a00, emissiveIntensity: .2 });
    const stem = M(new THREE.CapsuleGeometry(.28, 1.1, 8, 20), stemM); stem.position.set(0, -.6, -.6); stem.rotation.x = .25; G.add(stem);
    const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(0, -.25, 2.1), new THREE.Vector3(0, .0, 1.3), new THREE.Vector3(0, -.2, .3), new THREE.Vector3(0, -.45, -.45)]);
    const nerve = M(new THREE.TubeGeometry(curve, 64, .06, 10), new THREE.MeshBasicMaterial({ color: 0xffd27a, transparent: true, opacity: .25 })); G.add(nerve);
    const pulse = M(new THREE.SphereGeometry(.18, 20, 14), new THREE.MeshBasicMaterial({ color: 0xffe9a8 })); G.add(pulse);
    const pl = new THREE.PointLight(0xffc04a, 0, 6); G.add(pl);
    const motes = []; for (let i = 0; i < 14; i++) { const m = M(new THREE.IcosahedronGeometry(.07 + r1() * .06, 1), std(0xc9a46a, { roughness: .9, emissive: 0x302010 })); m.userData.o = [r1() * 2 - 1, r1() * 1.2 - .6, r1()]; G.add(m); motes.push(m); }
    const alarm = M(new THREE.TorusGeometry(.6, .05, 12, 48), new THREE.MeshBasicMaterial({ color: 0xff3b30, transparent: true, opacity: 0 })); alarm.position.set(0, -.5, -.6); alarm.rotation.y = Math.PI / 2; G.add(alarm);
    const d = dust(400, [30, 20, 20], 0xffc8d8, .12, .35); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S2;
      motes.forEach((m, i) => { const [ox, oy, ph] = m.userData.o; const k = clamp((a * .9 + ph * .5) % 1.6); m.position.set(ox * (1 - k) * .8, -.3 + oy * (1 - k), 4.2 - k * 2.0); m.visible = k < 1; m.rotation.set(t * 2 + i, t, 0); });
      const k = ease(prog(a, .8, 1.3)); pulse.position.copy(curve.getPoint(k)); pulse.visible = a > .8 && k < 1; pl.position.copy(pulse.position); pl.intensity = pulse.visible ? 80 : 0;
      nerve.material.opacity = .25 + .6 * prog(a, .8, .3);
      const al = prog(a, 2.1, .2); stemM.emissiveIntensity = .2 + al * (1.2 + .6 * Math.sin(t * 14));
      const rr = (a - 2.1) % .7; alarm.visible = a > 2.1; alarm.scale.setScalar(1 + rr * 3); alarm.material.opacity = .9 * (1 - rr / .7);
      G.rotation.y = -Math.PI / 2 + .35 + Math.sin(t * .3) * .12; d.rotation.y = t * .03;
      cam.position.set(0, 6.6, lerp(16, 14, ease(prog(a, 0, 2.8)))); cam.lookAt(0, 6.2, 0); };
  } });
  // 3) Akciğerler şişer, sonra hava bir anda dışarı fırlar
  shots.push({ t0: S3, t1: S4, fov: 40, build: (s, cam) => {
    lights(s, { key: 1700, rim: 0xff6a8a });
    const G = new THREE.Group(); G.position.set(0, 5.8, 0); s.add(G);
    const lm = new THREE.MeshPhysicalMaterial({ color: 0xe87a88, roughness: .45, clearcoat: .4, emissive: 0x401018, emissiveIntensity: .3 });
    const lungs = [-1, 1].map(k => { const l = M(new THREE.SphereGeometry(1, 64, 48), lm); { const P = l.geometry.attributes.position; for (let i = 0; i < P.count; i++) { const y = P.getY(i); P.setX(i, P.getX(i) * (1 - y * .25)); } l.geometry.computeVertexNormals(); }
      l.position.set(k * 1.25, -.2, 0); G.add(l); return l; });
    const trM = std(0xf2d0c8, { roughness: .5 });
    const tr = M(new THREE.CylinderGeometry(.22, .22, 2.6, 24), trM); tr.position.set(0, 2.3, 0); G.add(tr);
    [-1, 1].forEach(k => { const b = M(new THREE.CylinderGeometry(.16, .16, 1.2, 20), trM); b.position.set(k * .45, .8, 0); b.rotation.z = k * .9; G.add(b); });
    for (let i = 0; i < 8; i++) { const ring = M(new THREE.TorusGeometry(.24, .04, 8, 24), std(0xffffff, { roughness: .4 })); ring.rotation.x = Math.PI / 2; ring.position.set(0, 1.2 + i * .3, 0); G.add(ring); }
    const ribs = []; for (let i = 0; i < 6; i++) { const r = M(new THREE.TorusGeometry(2.6 - Math.abs(i - 2.5) * .15, .07, 10, 60, Math.PI * 1.3), std(0xf4ede0, { roughness: .4 })); r.rotation.set(Math.PI / 2, 0, -Math.PI * .15 + Math.PI); r.position.set(0, 1.2 - i * .55, 0); r.scale.set(1, 1, .55); G.add(r); ribs.push(r); }
    const air = burst(500, 0xbfe8ff); air.rotation.x = -Math.PI / 2; air.position.set(0, 3.6, 0); G.add(air);
    const inA = dust(300, [6, 4, 3], 0x9fd8ff, .14, .7); G.add(inA);
    const d = dust(300, [30, 20, 20], 0xffc8d8, .12, .35); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S3;
      const inh = ease(prog(a, .1, 1.4)), ex = easeOut(prog(a, 1.6, .45));
      const sc = 1 + inh * .32 - ex * .45 + .02 * Math.sin(t * 5);
      lungs.forEach(l => l.scale.set(sc, sc * 1.35, sc * .9));
      ribs.forEach((r, i) => r.scale.set(1 + (sc - 1) * .5, 1, .55 + (sc - 1) * .3));
      inA.visible = a < 1.5; inA.position.y = 4 - ((a * 3) % 3); inA.material.opacity = .7 * (1 - prog(a, 1.2, .3));
      const ak = prog(a, 1.55, 1.6); air.visible = ak > 0 && ak < 1; air.userData.set(ak, 9);
      G.position.y = 4.4 + Math.sin(t * 40) * .04 * prog(a, 1.55, .1) * Math.exp(-Math.max(0, a - 1.6) * 3);
      G.rotation.y = Math.sin(t * .4) * .35; d.rotation.y = t * .03;
      cam.position.set(0, 6.4, lerp(19, 17, ease(prog(a, 0, 4)))); cam.lookAt(0, 6.0, 0); };
  } });
  // 4) Refleks: göz yakın plan, kapak kendiliğinden kapanır
  shots.push({ t0: S4, t1: S5, fov: 40, build: (s, cam) => {
    lights(s, { key: 1800 });
    const F = face(); F.H.position.set(0, 6.4, 0); F.H.scale.setScalar(.9); s.add(F.H);
    const sp = burst(400); sp.position.set(0, 5.55, 1.7); s.add(sp);
    const d = dust(400, [30, 20, 20], 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S4; const cl = a > 1.0 && a < 2.4 ? ease(prog(a, 1.0, .08)) : (a >= 2.4 ? 1 - ease(prog(a, 2.4, .3)) : 0);
      F.setLids(cl); F.H.rotation.set(cl * .15, -.12 + Math.sin(t * .5) * .06, 0);
      const k = prog(a, 1.05, 1.1); sp.visible = k > 0 && k < 1; sp.userData.set(k, 8);
      d.rotation.y = t * .03;
      cam.position.set(0, 7.2, lerp(12.5, 11, ease(prog(a, 0, 2.8)))); cam.lookAt(0, 7.1, 0); };
  } });
  // 5) Diz refleksi: çekiç dize vurur, bacak sıçrar
  shots.push({ t0: S5, t1: S6, fov: 40, build: (s, cam) => {
    lights(s, { key: 1900 });
    const G = new THREE.Group(); G.position.set(0, 6.4, 0); s.add(G);
    const pants = std(0x2d4a7a, { roughness: .7 });
    const seat = M(rb(4.2, .5, 2.6, .12), std(0x5a3a28, { roughness: .6 })); seat.position.set(-1.6, -.55, 0); G.add(seat);
    [-1, 1].forEach(kx => [-1, 1].forEach(kz => { const lg = M(new THREE.CylinderGeometry(.1, .1, 3, 12), std(0x2a2f36, { metalness: .6 })); lg.position.set(-1.6 + kx * 1.8, -2.3, kz * 1.0); G.add(lg); }));
    const thigh = M(new THREE.CapsuleGeometry(.48, 2.4, 10, 24), pants); thigh.rotation.z = Math.PI / 2; thigh.position.set(-.9, 0, 0); G.add(thigh);
    const knee = M(new THREE.SphereGeometry(.52, 32, 24), pants); knee.position.set(.6, 0, 0); G.add(knee);
    const shin = new THREE.Group(); shin.position.set(.6, 0, 0); G.add(shin);
    const sm = M(new THREE.CapsuleGeometry(.4, 2.2, 10, 24), pants); sm.position.y = -1.5; shin.add(sm);
    const shoe = M(rb(.8, .5, 1.5, .2), std(0x1a1a1a, { roughness: .5 })); shoe.position.set(.25, -3.0, 0); shoe.rotation.y = Math.PI / 2; shin.add(shoe);
    const ham = new THREE.Group(); ham.position.set(2.6, -.2, .8); G.add(ham);
    const hh = M(new THREE.CylinderGeometry(.06, .06, 2.2, 12), std(0xc0c6ce, { metalness: .9, roughness: .2 })); hh.position.x = .9; hh.rotation.z = Math.PI / 2; ham.add(hh);
    const hd = M(new THREE.CapsuleGeometry(.22, .5, 8, 20), std(0xff5a3a, { roughness: .4 })); hd.position.x = -.2; ham.add(hd);
    const ring = M(new THREE.TorusGeometry(.45, .05, 12, 40), new THREE.MeshBasicMaterial({ color: 0xffcf2e, transparent: true, opacity: 0 })); ring.position.set(.95, -.8, .5); ring.rotation.y = Math.PI / 2; G.add(ring);
    const d = dust(400, [30, 20, 20], 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S5; const cyc = a % 1.6;
      const sw = cyc < .5 ? -ease(prog(cyc, 0, .5)) * .6 : -.6 + easeOut(prog(cyc, .5, .12)) * .6;
      ham.rotation.z = -sw; ham.position.set(1.45, -.8, .5);
      const kick = Math.sin(Math.PI * prog(cyc, .62, .5)) * .8; shin.rotation.z = kick;
      const rk = prog(cyc, .62, .4); ring.material.opacity = .9 * (1 - rk) * (rk > 0 ? 1 : 0); ring.scale.setScalar(.6 + rk * 1.6);
      G.rotation.y = -.25 + Math.sin(t * .3) * .1; d.rotation.y = t * .03;
      cam.position.set(0, 5.4, 17); cam.lookAt(0, 5.0, 0); };
  } });
  // göz küresi (göz dışı kaslar isteğe bağlı)
  function eyeball(muscles) {
    const G = new THREE.Group();
    const ball = M(new THREE.SphereGeometry(1.5, 64, 48), new THREE.MeshPhysicalMaterial({ color: 0xf8f4ee, roughness: .25, clearcoat: .8 })); G.add(ball);
    const iris = M(new THREE.SphereGeometry(1.505, 64, 32, 0, Math.PI * 2, 0, .45), std(0x3a7ab0, { roughness: .3 })); iris.rotation.x = Math.PI / 2; G.add(iris);
    const pup = M(new THREE.SphereGeometry(1.51, 48, 24, 0, Math.PI * 2, 0, .2), new THREE.MeshBasicMaterial({ color: 0x050505 })); pup.rotation.x = Math.PI / 2; G.add(pup);
    const veins = new THREE.MeshBasicMaterial({ color: 0xd04040, transparent: true, opacity: .5 });
    for (let i = 0; i < 6; i++) { const v = M(new THREE.TorusGeometry(1.51, .012, 6, 40, .6 + r1() * .4), veins); v.rotation.set(r1() * 6, r1() * 6, 0); G.add(v); }
    const ms = [];
    if (muscles) {
      const mm = std(0xc0453a, { roughness: .5, emissive: 0x401010, emissiveIntensity: .3 });
      const pts = [[0, 1.2, .5], [0, -1.2, .5], [1.2, 0, .5], [-1.2, 0, .5], [.9, .9, -.2], [-.9, -.9, -.2]];
      pts.forEach(([x, y, z]) => { const from = new THREE.Vector3(x, y, z); const to = new THREE.Vector3(x * .25, y * .25, -3.8); const len = from.distanceTo(to);
        const m = M(new THREE.CapsuleGeometry(.22, len, 8, 16), mm.clone()); m.position.copy(from).add(to).multiplyScalar(.5);
        m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), to.clone().sub(from).normalize()); G.add(m); ms.push(m); });
    }
    G.userData.ms = ms; return G;
  }
  // 6) Göz yerinden fırlar mı? -> EFSANE (kırmızı X)
  shots.push({ t0: S6, t1: S7, fov: 40, build: (s, cam) => {
    lights(s, { key: 1800, rim: 0xff3b30 });
    const sock = M(new THREE.TorusGeometry(1.9, .5, 24, 64), std(0xc99c84, { roughness: .6 })); sock.position.set(0, 6.0, 0); s.add(sock);
    const bk = M(new THREE.CircleGeometry(1.9, 48), std(0x2a1010, { roughness: .9 })); bk.position.set(0, 6.0, -1.2); s.add(bk);
    const E = eyeball(false); E.position.set(0, 6.0, 0); s.add(E);
    const xm = new THREE.MeshBasicMaterial({ color: 0xff3b30 });
    const X = new THREE.Group(); X.position.set(0, 6.0, 3.5); s.add(X);
    [1, -1].forEach(k => { const b = M(rb(5.2, .6, .3, .12), xm); b.rotation.z = k * Math.PI / 4; X.add(b); });
    const d = dust(400, [30, 20, 20], 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S6; const out = ease(prog(a, .6, 1.6)) * (1 - ease(prog(a, 2.9, .5)));
      E.position.z = out * 2.2 + Math.sin(t * 30) * .03 * out; E.rotation.set(Math.sin(t * 1.3) * .2, Math.sin(t * .9) * .3, 0);
      const xk = back(prog(a, 2.9, .4)); X.visible = a > 2.9; X.scale.setScalar(Math.max(.01, xk));
      d.rotation.y = t * .03;
      cam.position.set(Math.sin(a * .4) * 4, 7.0, 15); cam.lookAt(0, 6.0, 0); };
  } });
  // 7) Her göz 6 kasla yuvasına bağlı
  shots.push({ t0: S7, t1: S8, fov: 40, build: (s, cam) => {
    lights(s, { key: 1900, rim: 0xff6a5a });
    const E = eyeball(true); E.position.set(0, 5.6, 0); E.scale.setScalar(.95); s.add(E);
    const d = dust(400, [30, 20, 20], 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S7;
      E.userData.ms.forEach((m, i) => { const k = back(prog(a, .7 + i * .15, .35)); m.visible = k > .01; m.scale.set(1, Math.max(.01, k), 1);
        m.material.emissiveIntensity = .3 + .5 * Math.max(0, Math.sin(t * 6 - i)); });
      E.rotation.set(.25, .9 + a * .25, 0); d.rotation.y = t * .03;
      cam.position.set(0, 6.2, 15); cam.lookAt(0, 5.4, 0); };
  } });
  // 8) Sebebi tam bilinmiyor -> belki koruma: damlacıklar gözlere çarpmadan kapaklar kapanır
  shots.push({ t0: S8, t1: S9, fov: 40, build: (s, cam) => {
    lights(s, { key: 1700, rim: 0x7ee0ff });
    const F = face(); F.H.position.set(0, 5.8, 0); F.H.scale.setScalar(.95); s.add(F.H);
    const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e });
    const Q = new THREE.Group(); s.add(Q);
    const q = M(new THREE.TorusGeometry(.5, .13, 12, 32, Math.PI * 1.4), qm); q.rotation.z = -Math.PI * .3; Q.add(q);
    const qd = M(new THREE.SphereGeometry(.15, 12, 8), qm); qd.position.set(-.1, -.85, 0); Q.add(qd);
    const shield = M(new THREE.SphereGeometry(2.6, 48, 24, 0, Math.PI * 2, 0, Math.PI * .35), new THREE.MeshPhysicalMaterial({ color: 0x7ee0ff, transparent: true, opacity: 0, roughness: .1, side: THREE.DoubleSide, depthWrite: false, emissive: 0x2a8ac0, emissiveIntensity: .6 }));
    shield.rotation.x = Math.PI / 2; s.add(shield);
    const germs = []; for (let i = 0; i < 16; i++) { const g = M(new THREE.IcosahedronGeometry(.13, 1), std(0x7ad04a, { emissive: 0x2a6a10, emissiveIntensity: .6 })); g.userData.o = [(r1() - .5) * 3, (r1() - .5) * 1.4, r1()]; s.add(g); germs.push(g); }
    const d = dust(400, [30, 20, 20], 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S8; const p2 = a > 2.2;
      Q.visible = !p2; Q.position.set(2.6, 8.4 + Math.sin(t * 3) * .1, .5); Q.rotation.y = Math.sin(t * 2) * .4;
      const sn = p2 ? 1 - prog(a, 5.6, .3) : 0;
      F.setLids(sn ? 1 : (p2 ? 0 : .0)); F.H.rotation.set(sn * .2, Math.sin(t * .4) * .25, 0); F.mouth.scale.set(1.1, .3 + sn * .3, .4);
      germs.forEach(g => { const [ox, oy, ph] = g.userData.o; const k = p2 ? ((a * .6 + ph) % 1) : 0; g.visible = p2; g.position.set(ox * (.3 + k), 5.0 + oy + k * .5, 2.4 + k * 5); g.rotation.set(t * 2, t, 0); });
      shield.position.set(0, 6.1, 1.4); shield.material.opacity = p2 ? .25 * sn + .05 : 0; shield.scale.setScalar(.5);
      d.rotation.y = t * .03;
      cam.position.set(Math.sin(a * .2) * 2.5 + 1.5, 6.4, 17); cam.lookAt(0, 6.0, 0); };
  } });
  // 9) Hapşırık bulutu 7–8 metreye yayılır (yerde metre şeridi)
  shots.push({ t0: S9, t1: S10, fov: 40, build: (s, cam) => {
    lights(s, { key: 1500, rim: 0x7ee0ff, far: 160 });
    const W = new THREE.Group(); W.position.set(0, 3.0, 0); W.scale.setScalar(.6); s.add(W);
    const floor = M(new THREE.CylinderGeometry(30, 30, .4, 64), std(0x0c111a, { roughness: .9, metalness: .1 })); floor.position.y = -.2; W.add(floor);
    const P = new THREE.Group(); P.position.set(-4.6, 0, 0); P.rotation.y = Math.PI / 2; W.add(P);
    const body = M(new THREE.CapsuleGeometry(.55, 1.6, 10, 24), std(0x3f6aa8, { roughness: .6 })); body.position.y = 1.6; P.add(body);
    [-1, 1].forEach(k => { const lg = M(new THREE.CapsuleGeometry(.22, 1.1, 8, 16), std(0x2a2f36)); lg.position.set(k * .25, .6, 0); P.add(lg); });
    const head = M(new THREE.SphereGeometry(.45, 32, 24), skin()); head.position.y = 3.15; P.add(head);
    const hair = M(new THREE.SphereGeometry(.47, 32, 16, 0, Math.PI * 2, 0, Math.PI * .45), std(0x2a1c14)); hair.position.y = 3.18; hair.rotation.x = -.3; P.add(hair);
    const tape = new THREE.Group(); tape.position.set(-4.2, .05, 1.6); W.add(tape);
    { const tb = M(rb(9.8, .08, .45, .03), std(0xf2d14b, { roughness: .5 })); tb.position.x = 4.9; tape.add(tb); }
    for (let i = 0; i <= 8; i++) { const tk = M(new THREE.BoxGeometry(.08, .12, .45), new THREE.MeshBasicMaterial({ color: 0x222222 })); tk.position.set(i * 1.2, .06, 0); tape.add(tk); }
    const cloud = burst(900, 0xcfeeff); cloud.position.set(-4.0, 3.0, 0); cloud.rotation.y = Math.PI / 2; W.add(cloud);
    const haze = dust(500, [1, 1, 1], 0xbfe8ff, .5, .25); W.add(haze);
    const d = dust(400, [30, 20, 20], 0xcfe8ff, .12, .4); d.position.y = 6; s.add(d);
    return t => {
      const a = t - S9; const k = easeOut(prog(a, .3, 3.2));
      cloud.userData.set(Math.min(.62, k), 10.5); cloud.material.opacity = .85;
      haze.position.set(-4 + k * 4.5, 2.4 - k * .6, 0); haze.scale.set(.5 + k * 8, .5 + k * 2.5, .5 + k * 3); haze.material.opacity = .25 * k;
      body.rotation.x = Math.sin(Math.PI * prog(a, .2, .5)) * .25; head.position.z = Math.sin(Math.PI * prog(a, .2, .5)) * .25;
      d.rotation.y = t * .03;
      cam.position.set(lerp(1.0, 0, ease(prog(a, 0, 3.8))), 8.0, 17); cam.lookAt(0, 4.6, 0); };
  } });
  // 10) Sıradaki soru: kara delik — parlayan disk + içine çekilen astronot
  shots.push({ t0: S10, t1: 99, fov: 40, build: (s, cam) => {
    s.background = gradTex('#07071a', '#000000'); s.fog = new THREE.Fog(0x000000, 80, 300);
    s.add(new THREE.HemisphereLight(0x8fb4ff, 0x05050a, .4));
    const stars = dust(1500, [140, 140, 40], 0xffffff, .25, .9); stars.position.z = -45; s.add(stars);
    const B = new THREE.Group(); B.position.set(0, 6.4, 0); s.add(B);
    B.add(M(new THREE.SphereGeometry(1.6, 64, 48), new THREE.MeshBasicMaterial({ color: 0x000000 })));
    const dg = new THREE.RingGeometry(1.9, 5.2, 128, 6); const dc = []; const DP = dg.attributes.position;
    for (let i = 0; i < DP.count; i++) { const r = Math.hypot(DP.getX(i), DP.getY(i)); const k = (r - 1.9) / 3.3; const c = new THREE.Color().setHSL(.08 - k * .05, 1, .62 - k * .4); dc.push(c.r, c.g, c.b); }
    dg.setAttribute('color', new THREE.Float32BufferAttribute(dc, 3));
    const disk = M(dg, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide, transparent: true, opacity: .95, blending: THREE.AdditiveBlending, depthWrite: false })); disk.rotation.x = -Math.PI / 2 + .25; B.add(disk);
    const halo = M(new THREE.TorusGeometry(1.75, .08, 12, 96), new THREE.MeshBasicMaterial({ color: 0xffd9a0 })); B.add(halo);
    const glow = dust(600, [11, .6, 11], 0xffa040, .2, .7); glow.rotation.x = .25; B.add(glow);
    const man = new THREE.Group(); s.add(man);
    const mb = M(new THREE.CapsuleGeometry(.25, .7, 8, 16), std(0xeef1f5, { emissive: 0x332211 })); man.add(mb);
    const mh = M(new THREE.SphereGeometry(.24, 20, 14), new THREE.MeshPhysicalMaterial({ color: 0xbfe0ff, roughness: .05, transparent: true, opacity: .7 })); mh.position.y = .65; man.add(mh);
    const qm = new THREE.MeshBasicMaterial({ color: 0xffcf2e });
    const q = M(new THREE.TorusGeometry(.5, .12, 12, 32, Math.PI * 1.4), qm); q.rotation.z = -Math.PI * .3; s.add(q);
    const qd = M(new THREE.SphereGeometry(.14, 12, 8), qm); s.add(qd);
    return t => {
      const a = t - S10; disk.rotation.z = t * .5; glow.rotation.y = t * .4; stars.rotation.z = t * .01;
      const k = (a * .22) % 1; const ang = k * Math.PI * 3, rr = lerp(5.5, 1.7, ease(k));
      man.position.set(Math.cos(ang) * rr, 6.4 + Math.sin(ang) * rr * .25 + .3, Math.sin(ang) * rr * .6); man.lookAt(0, 6.4, 0); man.rotateX(Math.PI / 2);
      man.scale.set(1 - k * .5, 1 + k * 2.2, 1 - k * .5); man.visible = k < .97;
      q.visible = qd.visible = false;
      cam.position.set(Math.sin(a * .2) * 2, 8.6, 21); cam.lookAt(0, 6.4, 0); };
  } });

  const T = (tag, title, size) => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="title"${size ? ` style="font-size:${size}px"` : ''}>${title}</div>`;
  const BIG = (tag, id, sub, html = '') => `<div class="grad"></div><div class="tagw"><span class="tag">${tag}</span></div><div class="big" style="top:310px;font-size:170px" id="${id}">${html}</div><div class="sub" style="top:490px">${sub}</div>`;
  const titles = [
    { t0: 0, t1: S1, html: T('BİR SORU', 'HAPŞIRIRKEN GÖZLER<br>NEDEN <span class="y">KAPANIR?</span>', 92) },
    { t0: S1, t1: S2, html: T('GÖZLER AÇIK HAPŞIRMAK', 'NEREDEYSE <span class="y">İMKÂNSIZ</span>', 100) },
    { t0: S2, t1: 5.88, html: T('BURNA TOZ KAÇAR', 'SİNİRLER <span class="y">UYARILIR</span>', 100) },
    { t0: 5.88, t1: S3, html: T('BEYİN SAPI', '<span class="y">ALARM</span> VERİR!') },
    { t0: S3, t1: 8.88, html: T('ÖNCE', 'AKCİĞERLER <span class="y">DOLAR</span>', 104) },
    { t0: 8.88, t1: S4, html: T('SONRA', 'HAVA BİR ANDA<br><span class="y">FIRLAR!</span>', 100) },
    { t0: S4, t1: S5, html: T('BU BİR REFLEKS', 'GÖZ KAPAKLARI<br><span class="y">KENDİLİĞİNDEN</span> KAPANIR', 84) },
    { t0: S5, t1: S6, html: T('TIPKI', 'DİZ <span class="y">REFLEKSİ</span> GİBİ', 104) },
    { t0: S6, t1: 20.72, html: T('PEKİ', 'GÖZ YERİNDEN<br><span class="y">FIRLAR MI?</span>', 100) },
    { t0: 20.72, t1: S7, html: T('HAYIR', 'BU BİR <span class="y">EFSANE!</span>') },
    { t0: S7, t1: S8, html: BIG('HER GÖZÜ YUVASINDA', 'k6', 'KAS SIKICA TUTAR', '6') },
    { t0: S8, t1: 27.28, html: T('KAPANMANIN SEBEBİ', 'TAM <span class="y">BİLİNMİYOR</span>', 104) },
    { t0: 27.28, t1: S9, html: T('EN GÜÇLÜ TAHMİN', 'GÖZLERİ <span class="y">KORUMAK</span>', 104) },
    { t0: S9, t1: S10, html: BIG('HAPŞIRIK BULUTU', 'k8', 'METREYE KADAR YAYILIR', '7–8') },
    { t0: S10, t1: 99, html: T('SIRADAKİ SORU', 'KARA DELİĞE<br>DÜŞSEN NE <span class="y">OLUR?</span>', 96) + `<div class="btn" id="fb">Takip Et</div><div class="hand" id="hd">👆</div>` },
  ];
  const pops = [['k6', S7], ['k8', S9]];
  return {
    END: 40.2, shots, titles,
    update: (t, q) => pops.forEach(([id, t0]) => { const k = q(id); if (k) k.style.transform = `scale(${lerp(.6, 1, back(prog(t, t0, .5)))})`; }),
    follow: { t: 38.32, click: 39.3 },
    sfx: [[2.6, 'snap', .8], [2.62, 'whoosh', .7], [S2 + 1.6, 'pop', .5], [S2 + 2.1, 'ding', .6], [S2 + 2.8, 'ding', .4], [S3 + .2, 'whoosh', .3], [S3 + 1.55, 'whoosh', 1], [S3 + 1.58, 'snap', .6],
      [S4 + 1.0, 'snap', .7], [S5 + .55, 'click', .8], [S5 + 2.15, 'click', .8], [S6 + .8, 'whoosh', .4], [S6 + 2.9, 'boom', .6], [S6 + 2.95, 'pop_low', .8],
      [S7 + .7, 'pop', .4], [S7 + 1.0, 'pop', .4], [S7 + 1.3, 'pop', .4], [S7 + 1.6, 'pop', .4], [S7 + 1.9, 'pop', .4], [S7 + 2.2, 'ding', .6],
      [S9 + .3, 'whoosh', .9], [S9 + 3.0, 'ding', .5], [S10 + .5, 'boom', .5]],
  };
};
