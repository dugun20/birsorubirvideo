# @birsorubirvideo – günlük otomatik üretim

Her zamanlanmış çalışma (her gün 08:00) 2 yeni bulmaca videosu üretir ve paylaşım kuyruğuna ekler.
Make senaryosu (id 8298082) kuyruktaki sıradaki videoyu her gün 12:30 ve 20:30'da Instagram'a Reels olarak paylaşır;
video https://dugun20.github.io/birsorubirvideo/out/soru-<no>.mp4 adresinden alınır (GitHub Pages).
Kuyrukta zaten 4 veya daha fazla 'kuyrukta' satırı varsa yeni video üretme, sadece rapor ver.
Kullanıcıya soru sorma: bu seri için Cihan her gün sormadan üretim onayı verdi.

## Sabitler
- Depo: `dugun20/birsorubirvideo` (bu klasör)
- ElevenLabs sesi: Orcun Togan, `voice_id=c9eIhSvMHBxtYhLX4oBt`, model `eleven_v4`, `generations_count=1`
- Kuyruk tablosu: spreadsheetId `1p4LOorRwq6WQahWz8-MPTedTwoG_DqMc3mzt17BS7so`
  sütunlar: No | Tür | Video dosyası | Açıklama | Durum | Paylaşım zamanı | Kapak (ms)
- Kurallar: açıklamada hashtag yok, "Her gün yeni bir soru..." satırı yok, cevap videoda ve açıklamada asla yok,
  arka plan müziği yok, ekrandaki sayılar rakamla.

## Adımlar (her video için 1-6'yı tekrarla, toplam 2 video)
0. Ön kontrol: `python3 -c "import PIL, numpy"` (yoksa `pip install --break-system-packages pillow numpy`), `which ffmpeg`.
   Kuyruk tablosunu `get_values` (A1:G200) ile oku, 'kuyrukta' satırlarını say.
1. `python3 pipeline.py plan` → JSON çıktısındaki `tts` metnini ve `no` değerini al.
2. ElevenLabs `creative_generate_speech` ile `tts` metnini seslendir (yukarıdaki ses ve model, tek take).
   `creative_get_flow_run_status` ile bitene kadar bekle, `content_url`'yi
   `curl -sS -o out/soru-<no>.q.mp3 "<url>"` ile indir. Aynı üretimi asla ikinci kez başlatma.
3. `python3 pipeline.py build out/soru-<no>.plan.json out/soru-<no>.q.mp3`
4. Kontrol: `out/soru-<no>.cover.jpg` kapak karesine bak. `python3 check.py <no>` 4 kareyi `out/check-<no>.png` olarak çıkarır; resme bak.
   Yazı taşması, boş kart, üst üste binme varsa düzelt ve tekrar build et.
5. `git add out/soru-<no>.mp4 out/soru-<no>.txt out/soru-<no>.plan.json state/history.json`
   `git commit -m "Soru #<no>"` ve `git push`.
6. Kuyruk tablosuna satır ekle (Google Sheets `append_values`, range `A1`):
   `[<no>, <type>, "out/soru-<no>.mp4", <caption>, "kuyrukta", "", <cover_ms>]` (cover_ms build çıktısında)
7. Kısa rapor: hangi soru, cevap (sadece raporda), kuyrukta kaç video bekliyor.

Bir adım başarısız olursa kuyruğa bozuk satır ekleme; hatayı açıkça raporla.
