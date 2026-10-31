"""Render edilen videodan kontrol için 4 kare çıkarır: python3 check.py <no>"""
import subprocess, sys, os
from PIL import Image

no = sys.argv[1]
mp4 = f'out/soru-{no}.mp4'
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4],
                           capture_output=True, text=True).stdout)
times = [1.2, 9.0, dur - 7.5, dur - 1.0]
ims = []
for i, t in enumerate(times):
    p = f'out/.chk{i}.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', mp4, '-frames:v', '1', '-vf', 'scale=360:640', p], check=True)
    ims.append(Image.open(p)); os.remove(p)
sheet = Image.new('RGB', (360 * len(ims), 640))
for i, im in enumerate(ims): sheet.paste(im, (i * 360, 0))
sheet.save(f'out/check-{no}.png')
print(f'out/check-{no}.png')
