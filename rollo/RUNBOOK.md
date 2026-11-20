# Rollo Racing – otomatik yarış üretimi (@RolloRacingTV)

Her zamanlanmış çalışma **1 yeni bilye yarışı** üretir ve kuyruğa ekler (günde 2 çalışma → günde 2 video).
Make senaryosu 8693893 (Grumpo ile ortak, "Rollo" kolu) kuyruktaki sıradaki videoyu Rollo Racing kanalına yükler;
video `https://dugun20.github.io/birsorubirvideo/rollo/out/rollo-<NN>.mp4` adresinden alınır (GitHub Pages).

Cihan bu seri için tam otomatik üretime onay verdi: **kullanıcıya soru sorma**, render için onay bekleme.
Kuyrukta zaten **4 veya daha fazla 'kuyrukta' satırı** varsa yeni yarış üretme, sadece kısa rapor ver.

## Sabitler
- Kod: `rollo/kit/` — `course.py` (parça kütüphanesi + pymunk fizik), `render.py` (pastel stil), `audio.py` (ONAYLI sesler),
  `make_race.py` (tek komut). Sesler: `rollo/assets/sfx/` (Cihan'ın örnek videosundan). Font: `rollo/assets/fonts/LilitaOne.ttf`.
- Kayıt: `rollo/log/races.json` (tema, format, parçalar, kazanan – çeşitlilik kuralları bunu okur).
- Kuyruk tablosu: spreadsheetId `1m6rYkgznD0tUN6wXidFxGHVnmradARs6E0fQiEkxS4g`, sayfa **`Rollo`**
  sütunlar: No | Başlık | Video dosyası | Açıklama | Durum | Paylaşım zamanı | Etiketler | YouTube ID | Özet | Yorum
- Çıktı: 1080×1920, 60 fps, ~25 sn, müzik YOK.

## Değişmeyecek stil kuralları (Cihan onayladı – değiştirme)
- Örnek videosu (race_ornek.mp4) tarzı: pastel geçişli arka plan + baloncuklar, yüzlü sevimli bilyeler, liderde taç,
  üstte "Pick your color! / WHO WINS?" + 8'li canlı sıralama çubuğu, final "<AD> WINS!" + konfeti + "Did you pick <AD>?".
- Başlık bloğu YouTube'un üst düğmelerinin altında (render.py `HDR=75`), yazılar ekrandan taşmaz.
- Sesler `audio.py`'deki gibi (çivi/çubuk/GO/kazanma sesleri örnek videodan, rampaya düşüş = yumuşak 110 Hz tok ses).
  Cihan rampaya düşüş sesi konusunda çok hassas: ASLA değiştirme.
- Ekrandaki sayılar rakamla. Karanlık/neon tema YOK (Cihan beğenmedi) – sadece `render.THEMES` içindeki pastel temalar.

## Çeşitlilik (otomatik – make_race.py yapar)
- Parçalar: plinko, zigzag, spinners, windmill, funnel, bumpers, scatter, sliders, pads, split → her yarışta 4–5 tanesi rastgele sırada
  (aralarda yuvarlanma rampaları). Son 15 yarıştaki parça setini tekrar etmez.
- Tema son 2 yarıştan farklı; kazanan son 2 kazanandan farklı; format: klasik 8 renk (~%65) / ülke bayrakları (~%35).
- Yarış kalitesi: kazanan 15–26 sn, ilk iki arası < 1.3 sn, en az 5 lider değişimi (course.score).
- Yeni parça/tema/format eklemek serbest (aynı stil, aynı tuzaksızlık kuralı: bilyenin girebileceği her boşluk ≥ 80 px ya da < 20 px).

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
6. Push'tan sonra video adresi açılıyor mu kontrol et (GitHub Pages 1-2 dk gecikebilir; `curl -sI` ile 200 bekle, en fazla ~5 dk).
7. Kuyruğa satır ekle (`append_values`, range `Rollo!A1`), değerler `rollo-NN.json`'dan:
   `[NN, title, file, description, "kuyrukta", "", tags, "", summary, comment]`
8. Kısa rapor (SendUserMessage, Türkçe): yarış no, başlık, tema/format, parçalar, kazanan, süre, kuyrukta bekleyen sayısı.
   Bir adım başarısız olursa kuyruğa satır ekleme ve hatayı açıkça yaz.
