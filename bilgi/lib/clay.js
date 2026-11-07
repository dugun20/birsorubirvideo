// Clay diorama yapı taşları. Kullanım: const C = await clayKit(L) yerine scene.js içinde `import { clayKit } from '../../lib/clay.js'; const C = clayKit(L);`
import { RoundedBoxGeometry } from '../node_modules/three/examples/jsm/geometries/RoundedBoxGeometry.js';

export const PAL = {
  bg: ['#ffe9d6', '#f7c9b6'], soil: 0x8a5a44, grass: 0x8fcf7a, road: 0xb9b2aa, wall: 0xf2d4b8, wall2: 0xeec5a6, floor: 0xf7e3cf,
  roof: 0xd8826b, yellow: 0xffd45c, orange: 0xf2b134, red: 0xe06666, blue: 0x6fa8dc, purple: 0xb4a7d6, green: 0x5fb35a,
  skin: 0xf6d2b4, metal: 0x9aa3ad, dark: 0x3b3b3b, white: 0xffffff, water: 0x7cc6e8, text: '#4a2a22', accent: '#e2572f',
};

export function clayKit(L) {
  const { THREE, hash } = L;
  const mat = c => new THREE.MeshStandardMaterial({ color: c, roughness: .95, metalness: 0 });
  function lumpy(g, amt = .04, f = 3) {
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i); const n = hash(x * f, y * f, z * f) * amt; p.setXYZ(i, x + n, y + n * .6, z + n); }
    g.computeVertexNormals(); return g;
  }
  const rbox = (w, h, d, r = .25) => lumpy(new RoundedBoxGeometry(w, h, d, 4, Math.min(r, w / 2, h / 2, d / 2) * .99), .03, 2.2);
  const blob = (r, seg = 32) => lumpy(new THREE.SphereGeometry(r, seg, seg), r * .06, 2 / r);
  const mesh = (g, c, cast = true) => { const m = new THREE.Mesh(g, mat(c)); m.castShadow = cast; m.receiveShadow = true; return m; };

  // sıcak stüdyo ışığı + yumuşak gölge
  function studio(s, o = {}) {
    s.background = L.gradTex(...(o.bg || PAL.bg));
    s.add(new THREE.HemisphereLight(0xfff4e6, 0xd9a48f, 1.5));
    const sun = new THREE.DirectionalLight(0xfff0dd, 2.6); sun.position.set(-14, 26, 18); sun.castShadow = true;
    const e = o.shadow || 16; sun.shadow.mapSize.set(1024, 1024);
    Object.assign(sun.shadow.camera, { left: -e, right: e, top: e, bottom: -e, near: 1, far: 90 }); sun.shadow.radius = 6; sun.shadow.bias = -.0008;
    s.add(sun); const rim = new THREE.DirectionalLight(0xb9d4ff, .8); rim.position.set(16, 10, -14); s.add(rim);
    return sun;
  }
  // yuvarlak maket kaidesi
  function base(r = 11, top = PAL.grass) {
    const g = new THREE.Group();
    const b = mesh(new THREE.CylinderGeometry(r, r * 1.05, 3, 64), PAL.soil); b.position.y = -1.5; g.add(b);
    const t = mesh(lumpy(new THREE.CylinderGeometry(r * 1.005, r * 1.005, .7, 64, 1), .08, 1), top); t.position.y = .35; g.add(t);
    return g;
  }
  function tree(scale = 1, i = 0) {
    const g = new THREE.Group();
    const tr = mesh(new THREE.CylinderGeometry(.25, .35, 1.6, 12), 0x8a5a3c); tr.position.y = .8; g.add(tr);
    const top = mesh(blob(1.25 + (i % 2) * .3), [0x5fb35a, 0x77c26a, 0x4fa24f][i % 3]); top.position.y = 2.3 + (i % 2) * .3; g.add(top);
    g.scale.setScalar(scale); return g;
  }
  function cloud() {
    const c = new THREE.Group();
    [[0, 0, 1.6], [1.6, -.2, 1.2], [-1.5, -.3, 1.1], [.6, .7, 1.1]].forEach(([dx, dy, r]) => { const m = mesh(blob(r, 24), 0xffffff, false); m.position.set(dx, dy, 0); c.add(m); });
    return c;
  }
  // hamur insan (kafa, gövde, göz). opts: {body, hat}
  function person(o = {}) {
    const g = new THREE.Group();
    const body = mesh(new THREE.CapsuleGeometry(.3, .5, 8, 16), o.body || PAL.red); g.add(body);
    const head = mesh(blob(.28, 24), PAL.skin); head.position.y = .75; g.add(head);
    const eg = new THREE.SphereGeometry(.05, 8, 8); [-.1, .1].forEach(x => { const e = new THREE.Mesh(eg, mat(0x222222)); e.position.set(x, .8, .26); g.add(e); });
    if (o.hat) { const h = mesh(new THREE.CylinderGeometry(.22, .22, .45, 20), 0x2b2b2b); h.position.y = 1.18; g.add(h);
      const br = mesh(new THREE.CylinderGeometry(.36, .36, .05, 24), 0x2b2b2b); br.position.y = .97; g.add(br); }
    g.userData.head = head; return g;
  }
  function sparks(n = 14) { const g = new THREE.Group(); for (let i = 0; i < n; i++) g.add(new THREE.Mesh(new THREE.SphereGeometry(.09, 8, 8), new THREE.MeshBasicMaterial({ color: i % 2 ? 0xffd45c : 0xff8a3d }))); return g; }
  // HTML üst katman: maket hissi veren üst/alt bulanıklık + toprak tonlu etiket/başlık
  const tilt = `<div style="position:absolute;left:0;right:0;top:0;height:520px;backdrop-filter:blur(7px);-webkit-mask:linear-gradient(#000,transparent)"></div>
    <div style="position:absolute;left:0;right:0;bottom:0;height:560px;backdrop-filter:blur(7px);-webkit-mask:linear-gradient(transparent,#000)"></div>`;
  const tag = txt => `<div class="tagw"><span class="tag" style="color:#7a3b2e;border-color:#c98b72;background:rgba(255,240,228,.88)">${txt}</span></div>`;
  const title = (html, size) => `<div class="title" style="color:${PAL.text};text-shadow:0 4px 0 rgba(255,255,255,.6)${size ? `;font-size:${size}px` : ''}">${html.replace(/<y>/g, `<span class="y" style="color:${PAL.accent}">`).replace(/<\/y>/g, '</span>')}</div>`;
  const big = (id, top, size = 190) => `<div class="big" id="${id}" style="top:${top}px;font-size:${size}px;color:${PAL.accent};text-shadow:0 6px 0 rgba(255,255,255,.7)"></div>`;
  const setup = r => { r.shadowMap.enabled = true; r.shadowMap.type = L.THREE.PCFSoftShadowMap; r.toneMappingExposure = 1.15; };
  const css = `<style>.cap{color:#fff;text-shadow:0 3px 0 rgba(74,42,34,.9),0 0 18px rgba(74,42,34,.6)}.cap .on{color:#ffd45c}.cap .dim{color:#fff;opacity:.75}.brand{color:#7a3b2e}.brand b{color:#e2572f}.vig,.grad,.gradb{display:none}</style>`;
  return { mat, lumpy, rbox, blob, mesh, studio, base, tree, cloud, person, sparks, tilt, tag, title, big, setup, css, PAL };
}
