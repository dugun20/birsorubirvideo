// Kullanım (depo kökünde `python3 -m http.server 8765 --bind 127.0.0.1` açıkken, bilgi/ klasöründen):
//   node render.js frames <slug> 1.5,6,12        -> videos/<slug>/chk_<t>.jpg
//   node render.js video <slug> [i0 i1]          -> videos/<slug>/raw.mp4 (+ meta.json: END, SFX)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
(async () => {
  const [mode, slug] = process.argv.slice(2, 4);
  const dir = `videos/${slug}`;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('PAGE:', m.text()));
  page.on('pageerror', e => console.log('HATA:', e.message));
  await page.goto(`http://127.0.0.1:8765/bilgi/index.html?v=${slug}`);
  await page.waitForFunction('window.READY === true', null, { timeout: 90000 });
  const END = await page.evaluate('window.END');
  fs.writeFileSync(`${dir}/meta.json`, JSON.stringify({ END, SFX: await page.evaluate('window.SFX') }));
  if (mode === 'frames') {
    for (const t of process.argv[4].split(',').map(Number)) {
      await page.evaluate(t => window.setTime(t), t);
      await page.screenshot({ path: `${dir}/chk_${t}.jpg`, type: 'jpeg', quality: 80 });
    }
  } else {
    const FPS = 30, n = Math.ceil(END * FPS);
    const i0 = +(process.argv[4] || 0), i1 = +(process.argv[5] || n);
    const out = process.argv[4] ? `${dir}/seg_${i0}_${i1}.mp4` : `${dir}/raw.mp4`;
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out]);
    const t0 = Date.now();
    for (let i = i0; i < i1; i++) {
      await page.evaluate(t => window.setTime(t), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(i, '/', n, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    console.log('bitti', out);
  }
  await browser.close();
})();
