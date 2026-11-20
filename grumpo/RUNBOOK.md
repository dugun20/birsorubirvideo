# Grumpo & Nibbo – otomatik bölüm üretimi

Global YouTube Shorts kanalı **@GrumpoAndNibbo** için her zamanlanmış çalışma **1 yeni bölüm** üretir ve
paylaşım kuyruğuna ekler. Günde 2 çalışma var. Make senaryosu kuyruktaki sıradaki videoyu YouTube'a yükler;
video `https://dugun20.github.io/birsorubirvideo/grumpo/out/grumpo-<NN>.mp4` adresinden alınır (GitHub Pages).

Cihan bu seri için tam otomatik üretime onay verdi: **kullanıcıya soru sorma**, render için onay bekleme.
Kuyrukta zaten **4 veya daha fazla 'kuyrukta' satırı** varsa yeni bölüm üretme, sadece kısa rapor ver.

## Sabitler
- Depo klasörü: `grumpo/` (bu klasör). Kit: `grumpo/kit/` (chars2.py, env2.py, still_v2.py, sfx.py, build.py)
- Örnek/referans bölüm: `grumpo/episodes/ep01_havuz.py` (kalite ve yapı referansı — kopyalama, ondan öğren)
- Bölüm kaydı: `grumpo/log/indeks.md` (tek satırlık parmak izleri – her zaman oku), `grumpo/log/bolumler.md` (ayrıntı)
- Konu bankası: `grumpo/log/konu_bankasi.md` (mekân/çatışma/yapı/son listeleri + özel gün takvimi)
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
6. **Diyalogsuz:** hikâye hareket, ifade, işaret (! ? ikonlar, tabelalar ikon ile) ve sesle anlaşılır. Sahnenin İÇİNDE kelime yok.
   TEK istisna aşağıdaki **başlık kancası** ve **sayaç** katmanı (ekran üstü, kısa İngilizce, sayılar rakamla).
8. **Bol ve senkron ses efekti** (`kit/sfx.py`; gerekirse yeni ses fonksiyonu ekle, eklediğin sesleri commit et).

## İzlenme kuralları (SEEDPIT gibi büyüyen kanallardan öğrenilen — kopyalama, kalıbı uygula)
A. **Başlık kancası ZORUNLU:** her bölümde `kit/hook.py` → `overlay(svg, hook_title(t, ÜST, ANA))`.
   0. saniyede patlayarak gelir, video boyunca üstte kalır, ilk kare kapak gibi okunur.
   - ÜST satır ≤ 22 karakter (beyaz, küçük), ANA satır ≤ 16 karakter, BÜYÜK HARF (sarı-turuncu). İngilizce, sayılar rakamla.
   - Merak sorusu/iddia olsun: `Can Nibbo get` / `GRUMPO'S PIZZA?`, `Grumpo said` / `ONLY 1 COOKIE`, `Nibbo tried` / `5 WAYS IN`,
     `Don't wake` / `GRUMPO`, `Grumpo vs Nibbo` / `LAST SEAT`. SEEDPIT'in "Can Kevin ___ Seed?" kalıbını birebir KULLANMA;
     son 5 bölümde kullanılan kalıbı tekrar etme (log'a hook'u da yaz).
   - Hook ile YouTube başlığı aynı fikri taşısın.
B. **Kadraj:** üstteki ~620 px yazıya ayrılmış — aksiyon ve karakter yüzleri y > 650'de olsun. Karakterler büyük:
   kamera zoom ≥ 1.25, ana anlarda yakın plan. Telefonda yüz ifadeleri net okunmalı.
C. **Tırmanan format (her 3 bölümden ~1'i):** ekranda büyüyen sayaç/seviye — `counter(t, değer, "ETİKET", adım, toplam, bump_t=...)`.
   Örn: deneme sayısı (`TRY 3/5`), her seferinde ikiye katlanan şey (`1,024`), seviye barı. Her adım bir öncekinden büyük/absürt,
   son adım sürprizle bağlanır. Diğer bölümler normal slapstick hikâye (sayaçsız).
D. **İlk 1 saniye:** olay hemen başlasın (çatışma ilk karede görünsün), giriş/yavaş açılış yok.

## Adımlar
0. Ön kontrol: `which rsvg-convert ffmpeg`, `python3 -c "import numpy, scipy"`
   (yoksa `apt-get install -y librsvg2-bin ffmpeg` / `pip install --break-system-packages numpy scipy`).
   Kuyruk tablosunu `get_values` (A1:I400) ile oku; 'kuyrukta' satırlarını say (≥4 ise dur, rapor ver). Son No'yu bul → NN = son No + 1 (iki haneli: 02, 03…).
1. `log/indeks.md` (tamamı) ve `log/konu_bankasi.md`'yi oku. Önce özel gün takvimine bak (tarihe 1–5 gün varsa özel gün bölümü yap).
   Değilse bankadan kullanılmamış 1 MEKÂN + 1 ÇATIŞMA + son 5 bölümde olmayan 1 YAPI + 1 SON seç (banka kurallarına uy).
   Yeni bölümün hikâyesini yaz: saniye saniye akış, gag'ler, son, başlık kancası. İndeksteki gag anahtar kelimeleriyle çakışmadığını kontrol et.
   Seçtiğin banka satırlarına `✔NN` ekle.
2. `episodes/epNN_<slug>.py` dosyasını yaz (ep01_havuz.py'deki gibi: `W,H,FPS=1080,1920,60`, `DUR`, `frame(t)`, `EV`, `sfx()`, `build_sfx()`).
   Kitteki yardımcıları kullan; yeni sahne/prop gerekiyorsa aynı stilde çiz (dış çizgi OL, iki ton gölge).
3. Önizleme: `python3 kit/build.py preview episodes/epNN_<slug>.py <8-12 zaman>` → `out/preview-epNN.png` resmine BAK.
   Kontrol et: başlık kancası okunuyor ve kenardan taşmıyor mu, yazı karakterlerin yüzüne biniyor mu, karakterler kadrajda mı, kesilme/üst üste binme/boş sahne var mı, kaşlar ayrı mı, hikâye karelerden okunuyor mu.
   Sorun varsa düzelt, tekrar önizle. (En az 2 tur bak.)
4. Render: `python3 kit/build.py full episodes/epNN_<slug>.py NN` → `out/grumpo-NN.mp4` ve `out/check-NN.png`. Check resmine bak.
5. Başlık/açıklama/etiket (İngilizce):
   - Başlık: ekrandaki kancayla aynı fikir, merak uyandıran, ≤ 70 karakter, sonu ` #shorts`. Örn: `Nibbo Is NOT Allowed in Grumpo's Pool! 🏊 #shorts`
   - Açıklama: 1–2 kısa cümle + yorum sorusu + boş satır + `#shorts #cartoon #animation #funny`
   - Etiketler: virgül+boşlukla ayrılmış: `Grumpo, Nibbo, Grumpo and Nibbo, Grumpo & Nibbo, cartoon, funny cartoon, animation, shorts, cartoon shorts, animated shorts, silent cartoon, slapstick cartoon, <konuya özel 2-4 etiket>`
   - Başlık ve açıklamada `<` `>` karakteri kullanma.
6. Önce `git config user.name Cihan` ve `git config user.email dugun258@gmail.com`.
   `git add grumpo/episodes/epNN_<slug>.py grumpo/out/grumpo-NN.mp4 grumpo/log/ grumpo/kit/`
   `git commit -m "Grumpo #NN: <kısa ad>"`, sonra `git pull --rebase` (aynı depoya başka sayfaların görevleri de push ediyor)
   ve `git -c push.negotiate=true push`. Reddedilirse `git fetch --depth=50 origin main` + rebase ile bir kez daha dene.
   Preview/check png'lerini commit etme.
7. Kuyruğa satır ekle (Google Sheets `append_values`, sayfa `Kuyruk`, range `A1`):
   `[NN, "<başlık>", "grumpo/out/grumpo-NN.mp4", "<açıklama>", "kuyrukta", "", "<etiketler>", "", "<1 cümle özet>"]`
8. `log/bolumler.md`'ye ayrıntılı satır, `log/indeks.md`'ye tek satırlık parmak izi ekle; `konu_bankasi.md` işaretlerini kaydet.
   Hepsini 6. adımdaki commit'e dahil et (`git add grumpo/log/`).
9. Kısa rapor: bölüm no, başlık, süre, hikâye özeti, kuyrukta kaç video bekliyor.

Bir adım başarısız olursa kuyruğa bozuk satır ekleme; hatayı açıkça raporla. Push başarısızsa kuyruğa ekleme.
