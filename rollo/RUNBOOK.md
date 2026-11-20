# Rollo Racing – otomatik yarış üretimi (@RolloRacingTV)

Her zamanlanmış çalışma **1 yeni bilye yarışı** üretir ve kuyruğa ekler (günde 2 çalışma → günde 2 video).
Make senaryosu 8708385 ("Rollo Racing - Kuyruktan YouTube Shorts yükle", her gün 20:00 ve 03:00 TR) kuyruktaki sıradaki videoyu Rollo Racing kanalına yükler;
video `https://dugun20.github.io/birsorubirvideo/rollo/out/rollo-<NN>.mp4` adresinden alınır (GitHub Pages).

Cihan bu seri için tam otomatik üretime onay verdi: **kullanıcıya soru sorma**, render için onay bekleme.
Kuyrukta zaten **4 veya daha fazla 'kuyrukta' satırı** varsa yeni yarış üretme, sadece kısa rapor ver.

## Sabitler
- Kod: `rollo/kit/` — `course.py` (parça kütüphanesi + pymunk fizik), `render.py` (pastel stil), `audio.py` (ONAYLI sesler),
  `make_race.py` (tek komut). Sesler: `rollo/assets/sfx/` (Cihan'ın örnek videosundan). Font: `rollo/assets/fonts/LilitaOne.ttf`.
- Kayıt: `rollo/log/races.json` (tema, format, parçalar, kazanan – çeşitlilik kuralları bunu okur).
- Kuyruk tablosu: spreadsheetId `1m6rYkgznD0tUN6wXidFxGHVnmradARs6E0fQiEkxS4g`, sayfa **`Rollo`**
  sütunlar: No | Başlık | Video dosyası | Açıklama | Durum | Paylaşım zamanı | Etiketler | YouTube ID | Özet | Yorum
- Çıktı: 1080×1920, 60 fps, ~18–22 sn, müzik YOK.

## Değişmeyecek kurallar (Cihan onayladı, 20 Kasım 2026 – değiştirme)
- Tarz: yüzlü sevimli bilyeler, liderde taç, üstte "Pick your color!/Pick your country!" + "WHO WINS?" + 8'li canlı sıralama çubuğu,
  final "<AD> WINS!" + konfeti + "Did you pick <AD>?". Başlık bloğu YouTube üst düğmelerinin altında (render.py `HDR=75`), yazılar taşmaz.
- HER VİDEO FARKLI GÖRÜNMELİ: `worlds.py` dünyaları dönüşümlü – pastel (5 palet), candy (şeker), beach (plaj), winter (kar), jungle (orman),
  football (çim saha + fileli kale + "GOAL!"). Ülke yarışları çoğunlukla football. Son 2 yarışın dünyası tekrar etmez. Karanlık/neon dünya YOK.
- AKSİYON: uzun kayma rampaları YOK (Cihan "aksiyonsuz" buldu). Parkur aksiyon parçalarından (zigzag çok nadir), bağlantı rampası yok,
  bilyelere hız sınırı (course.VMAX), duvar boyunca kenar engelleri (add_edge_guards) – kenardan serbest düşüş olmaz.
  Hedef: kazanan 11–19 sn, ilk iki arası < 1.3 sn, ≥4 lider değişimi. AĞIR ÇEKİM YOK (Cihan "mantık hatası" gibi buldu).
- BAŞLANGIÇ: bilyeler ekranın üstünden sırayla yağıp başlangıç bölmesini doldurur (V kapı ya da raf), düşerken tın tın sesler,
  2 kısa "bip" + parlak GO sesi (football'da + hakem düdüğü), yarış 1.3. saniyede başlar – bekletme yok.
- SESLER (`audio.py`): çivi/zıplatıcı = örnek videonun çivi notası (pentatonik), dönen çubuk = örnek sesi, kazanma = örnek sesi
  (football'da + kısa tribün sesi). Rampaya düşüş = çok yumuşak "puf" (LAND="puf") – tok ses ASLA. Müzik yok.
- Ekrandaki sayılar rakamla.

## Çeşitlilik (otomatik – make_race.py yapar)
- Parçalar: plinko, spinners, windmill, funnel, bumpers, scatter, sliders, pads, split (+ nadiren zigzag); 8–9 parça rastgele sırada,
  süre hedefe uymazsa parça ekler/çıkarır. Son 15 yarışın parça setini tekrar etmez.
- Dünya/palet son yarışlardan farklı; başlangıç tipi (v/shelf) rastgele; kazanan son 2 kazanandan farklı;
  format: klasik 8 renk (~%65) / ülke bayrakları (~%35, İtalya+Meksika birlikte seçilmez).
- Yeni dünya/parça eklemek serbest (aynı sevimli stil, tuzaksızlık: bilyenin girebileceği her boşluk ≥ 80 px ya da < 20 px;
  duvara teğet engel güvenlidir).

## Adımlar
0. Ön kontrol: `pip install --break-system-packages pymunk pycairo numpy pillow` (yoksa), `which ffmpeg`,
   `mkdir -p ~/.fonts && cp rollo/assets/fonts/LilitaOne.ttf ~/.fonts/ && fc-cache -f`.
   Kuyruk tablosunu `get_values` (`Rollo!A1:J400`) ile oku; 'kuyrukta' satırlarını say (≥4 ise dur, rapor ver).
   NN = tablodaki son No + 1.
1. `cd rollo/kit && python3 make_race.py run NN` (≈1 dk). Çıktı: `rollo/out/rollo-NN.mp4`, `check-NN.png`, `rollo-NN.json`.
2. `rollo/out/check-NN.png` resmine BAK: başlık okunuyor mu, yazı taşıyor mu, bilyeler görünüyor mu, final yazısı doğru mu,
   boş/bozuk kare var mı. Sorun varsa düzelt ve 1. adımı tekrarla.
3. `python3 make_race.py log NN`
4. Depo temizliği (GitHub Pages 1 GB sınırı): tabloda Durum'u 'paylaşıldı' olan ve No'su NN-6'dan küçük satırların
   `rollo/out/rollo-XX.mp4` dosyalarını `git rm` ile sil (sadece paylaşılmışları!).
5. `git config user.name Cihan && git config user.email dugun258@gmail.com`
   `git add rollo/out/rollo-NN.mp4 rollo/out/rollo-NN.json rollo/log/ rollo/kit/` (+ silinenler);
   `git commit -m "Rollo #NN: <kazanan> wins (<tema>)"`; `git pull --rebase`; `git -c push.negotiate=true push`.
   Reddedilirse `git fetch --depth=50 origin main` + rebase ile bir kez daha dene. check png'yi commit etme.
6. (İsteğe bağlı) Çalışma ortamının ağı github.io'ya izin vermeyebilir (curl 000 döner) – bu normaldir, Make dosyayı kendisi indirir. Push başarılıysa devam et.
7. Kuyruğa satır ekle (`append_values`, range `Rollo!A1`), değerler `rollo-NN.json`'dan:
   `[NN, title, file, description, "kuyrukta", "", tags, "", summary, comment]`
8. Kısa rapor (SendUserMessage, Türkçe): yarış no, başlık, tema/format, parçalar, kazanan, süre, kuyrukta bekleyen sayısı.
   Bir adım başarısız olursa kuyruğa satır ekleme ve hatayı açıkça yaz.
