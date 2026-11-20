# Grumpo & Nibbo – otomatik bölüm üretimi

Global YouTube Shorts kanalı **@GrumpoAndNibbo** için her zamanlanmış çalışma **1 yeni bölüm** üretir ve
paylaşım kuyruğuna ekler. Günde 2 çalışma var. Make senaryosu kuyruktaki sıradaki videoyu YouTube'a yükler;
video `https://dugun20.github.io/birsorubirvideo/grumpo/out/grumpo-<NN>.mp4` adresinden alınır (GitHub Pages).

Cihan bu seri için tam otomatik üretime onay verdi: **kullanıcıya soru sorma**, render için onay bekleme.
Kuyrukta zaten **4 veya daha fazla 'kuyrukta' satırı** varsa yeni bölüm üretme, sadece kısa rapor ver.

## Sabitler
- Depo klasörü: `grumpo/` (bu klasör). Kit: `grumpo/kit/` (chars2.py, env2.py, still_v2.py, sfx.py, build.py)
- Örnek/referans bölüm: `grumpo/episodes/ep01_havuz.py` (kalite ve yapı referansı — kopyalama, ondan öğren)
- Bölüm kaydı: `grumpo/log/bolumler.md` — yazmadan ÖNCE oku, bitince yeni satır ekle
- Kuyruk tablosu: spreadsheetId `1m6rYkgznD0tUN6wXidFxGHVnmradARs6E0fQiEkxS4g`, sayfa `Kuyruk`
  sütunlar: No | Başlık | Video dosyası | Açıklama | Durum | Paylaşım zamanı | Etiketler | YouTube ID | Özet
- Çıktı: 1080×1920, 60 fps, H.264, sadece efekt sesleri (müzik YOK, seslendirme YOK, diyalog YOK)

## Karakterler (değiştirme)
- **Grumpo**: mor, huysuz, büyük top. Kaşları **ayrı** (asla birleşik değil). `grumpo(...)` (chars2)
- **Nibbo**: sarı, masum emoji gibi top, **siyah nokta gözler + beyaz parıltı**, pembe yanaklar. `bloop(...)` (chars2, `nibbo = bloop`)
- İkisi **aynı boyda** (Grumpo ölçek ~0.92 → r≈120, Nibbo r≈112). Tek Nibbo — kalabalık yok (çok nadir sürpriz hariç).
- Görsel stil: env2 (koyu lacivert tek tip dış çizgi `#221c2e`, düz renk + iki tonlu gölge, puslu tepeler, çim+kum şeridi,
  yer altı detayları, yumuşak gölgeler, hareketli kamera). Kalite ep01 seviyesinin altına düşmemeli.

## Hikâye kuralları (en önemli kısım)
1. **Her bölüm tamamen özgün.** `log/bolumler.md`'deki mekânları, ana fikirleri, gag'leri ve sonları TEKRARLAMA.
   YouTube "tekrar eden/özgün olmayan içerik" saymamalı.
2. **Yapı da değişsin.** Her seferinde "3 deneme + final" kullanma. Dönüşümlü kullan: ters rol (Grumpo istiyor, Nibbo engelliyor),
   ortak düşman (sinek, bozuk makine, rüzgar…), zincirleme büyüyen tek şaka, kovalamaca, yarış, taklit, yanlış anlaşılma, iş birliği.
3. **Sonlar değişsin:** bazen Nibbo kazanır, bazen Grumpo, bazen ikisi de rezil olur, bazen barışırlar, bazen üçüncü bir şey kazanır.
   "Fırlayıp yıldız olma", "kıpkırmızı buhar", "gözlüğü takıp içeceği içme" gibi önceki gag'leri tekrar kullanma.
4. **Genel kitle:** yetişkin ve gençlerin de güleceği gündelik durumlar (Wi-Fi şifresi, alarm/uyku, diyet, toplantı, kira, trafik,
   kuyruk, market, kumanda kavgası, son dilim pizza, şarj kablosu…). Çocuklara özel tema (oyuncak, alfabe, renk öğretme) yok.
5. **Süre hikâyeye göre:** 15–45 sn. Uzatma yok, **boşluk/ölü an yok**; ilk 1 sn içinde olay başlasın. Kısa hikâye kısa kalsın.
6. **Diyalogsuz, yazısız:** her şey hareket, ifade, işaret (! ? ikonlar, tabelalar ikon ile) ve sesle anlaşılır. Ekranda kelime yok.
7. **Bol ve senkron ses efekti** (`kit/sfx.py`; gerekirse yeni ses fonksiyonu ekle, eklediğin sesleri commit et).

## Adımlar
0. Ön kontrol: `which rsvg-convert ffmpeg`, `python3 -c "import numpy, scipy"`
   (yoksa `apt-get install -y librsvg2-bin ffmpeg` / `pip install --break-system-packages numpy scipy`).
   Kuyruk tablosunu `get_values` (A1:I400) ile oku; 'kuyrukta' satırlarını say (≥4 ise dur, rapor ver). Son No'yu bul → NN = son No + 1 (iki haneli: 02, 03…).
1. `log/bolumler.md`'yi oku. Yeni bölümün hikâyesini yaz: mekân, yapı türü, saniye saniye akış, son. Önceki bölümlerle çakışmadığını kontrol et.
2. `episodes/epNN_<slug>.py` dosyasını yaz (ep01_havuz.py'deki gibi: `W,H,FPS=1080,1920,60`, `DUR`, `frame(t)`, `EV`, `sfx()`, `build_sfx()`).
   Kitteki yardımcıları kullan; yeni sahne/prop gerekiyorsa aynı stilde çiz (dış çizgi OL, iki ton gölge).
3. Önizleme: `python3 kit/build.py preview episodes/epNN_<slug>.py <8-12 zaman>` → `out/preview-epNN.png` resmine BAK.
   Kontrol et: karakterler kadrajda mı, kesilme/üst üste binme/boş sahne var mı, kaşlar ayrı mı, hikâye karelerden okunuyor mu.
   Sorun varsa düzelt, tekrar önizle. (En az 2 tur bak.)
4. Render: `python3 kit/build.py full episodes/epNN_<slug>.py NN` → `out/grumpo-NN.mp4` ve `out/check-NN.png`. Check resmine bak.
5. Başlık/açıklama/etiket (İngilizce):
   - Başlık: merak uyandıran, ≤ 70 karakter, sonu ` #shorts`. Örn: `Nibbo Is NOT Allowed in Grumpo's Pool! 🏊 #shorts`
   - Açıklama: 1–2 kısa cümle + yorum sorusu + boş satır + `#shorts #cartoon #animation #funny`
   - Etiketler: virgül+boşlukla ayrılmış: `Grumpo, Nibbo, Grumpo and Nibbo, Grumpo & Nibbo, cartoon, funny cartoon, animation, shorts, cartoon shorts, animated shorts, silent cartoon, slapstick cartoon, <konuya özel 2-4 etiket>`
   - Başlık ve açıklamada `<` `>` karakteri kullanma.
6. Önce `git config user.name Cihan` ve `git config user.email dugun258@gmail.com`.
   `git add grumpo/episodes/epNN_<slug>.py grumpo/out/grumpo-NN.mp4 grumpo/log/bolumler.md grumpo/kit/sfx.py`
   `git commit -m "Grumpo #NN: <kısa ad>"`, sonra `git pull --rebase` (aynı depoya başka sayfaların görevleri de push ediyor)
   ve `git -c push.negotiate=true push`. Reddedilirse `git fetch --depth=50 origin main` + rebase ile bir kez daha dene.
   Preview/check png'lerini commit etme.
7. Kuyruğa satır ekle (Google Sheets `append_values`, sayfa `Kuyruk`, range `A1`):
   `[NN, "<başlık>", "grumpo/out/grumpo-NN.mp4", "<açıklama>", "kuyrukta", "", "<etiketler>", "", "<1 cümle özet>"]`
8. `log/bolumler.md`'ye satır ekle (bkz. dosya biçimi) ve commit/push et (6. adımla birlikte yapılabilir).
9. Kısa rapor: bölüm no, başlık, süre, hikâye özeti, kuyrukta kaç video bekliyor.

Bir adım başarısız olursa kuyruğa bozuk satır ekleme; hatayı açıkça raporla. Push başarısızsa kuyruğa ekleme.
