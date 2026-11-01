# @ingilizcekodla (Sıfırdan İngilizce Öğren): günlük otomatik üretim

Her sabah çalışan zamanlanmış görev bu dosyayı izler. Görev, kuyrukta 6'dan az video varsa 3 yeni kelime videosu üretip
paylaşım kuyruğuna ekler. Make senaryosu 8314263 kuyruktaki sıradaki videoyu her gün 09:30, 14:30 ve 21:30'da
@ingilizcekodla'ya Reels olarak atar. Videolar şu adresten okunur:
https://dugun20.github.io/birsorubirvideo/kelime/out/kelime-<no>.mp4 (GitHub Pages).
Cihan bu seri için her gün sormadan üretim onayı verdi: kullanıcıya soru sorma.

## Sabitler
- Klasör: depo kökünde `kelime/` (render motoru `../engine.py` ve `../assets/fonts` kullanır).
- Kuyruk tablosu: spreadsheetId `1p4LOorRwq6WQahWz8-MPTedTwoG_DqMc3mzt17BS7so`, sekme **Kelime**.
  Sütunlar: No | Kelime | Video dosyası | Açıklama | Durum | Paylaşım zamanı | Kapak (ms)
- ElevenLabs (model `eleven_v4`, `generations_count=1`, aynı üretimi asla ikinci kez başlatma):
  - Türkçe anlatıcı: Hale, `voice_id=SBqwqJrrVooSHZ6ofGmf`
  - İngilizce ses: Clamon, `voice_id=cdnpdcqt2HW1XtKv2f3V`
  - Flow: `KiFsuCUewA2F2jzdOfU3` (yoksa yeni flow kullanılabilir)
- Ortak sesler `audio/fixed/` içinde hazır, yeniden üretme: ask.wav ("Peki bunu nasıl unutmayacaksın? Hemen beynine kodluyoruz."),
  outro.wav ("Her gün 3 yeni kelime, beynine kodla ve unutma!"), takip.wav ("Şimdi takip et!").
- Görsel: Higgsfield `generate_image`, model `gpt_image_2_5`, `aspect_ratio` "1:1", `use_unlim` false.
  Prompt = sahne + şu stil eki:
  `Funny, vivid 3D cartoon illustration (Pixar-like style), absurd and playful, warm cinematic lighting, rich saturated colors, centered composition. Absolutely no text, no letters, no numbers, no writing on signs or objects.`
- Kurallar: arka plan müziği yok, ekrandaki sayılar rakamla, açıklamada hashtag yok.

## Kelime verisi (data/words.json)
Her numara için alanlar: word, pron (Türkçe okunuş), mean, me (anlam emojisi), key (BÜYÜK HARF Türkçe çağrışım),
ke (çağrışım emojisi), frag (key'in kelimeye benzeyen başı, ör. "Ber"), hook (sesli giriş, cevabı doğrudan söylemeyen
merak cümlesi), hs (ekrandaki 2 satır giriş, satır başına en çok ~20 karakter, son satır emojiyle bitebilir),
story ("<Key>! <komik sahne>! Artık <mean> deyince aklına <key> gelecek. <frag>..."), sub1 (sahnenin kısa altyazısı),
sent (İngilizce örnek cümle, 2 satıra bölünmüş, ikisi de kısa), hl (sarı vurgulanacak kelime, noktalama dahil),
trans (cümlenin Türkçesi).
- 30'dan sonraki numaralar için yeni kelimeyi sen seç ve words.json'a ekle: başlangıç seviyesi, günlük hayatta çok
  kullanılan, daha önce kullanılmamış bir kelime olsun. Türkçe çağrışım kelimenin İngilizce okunuşuna gerçekten
  benzemeli ve komik, görsel bir sahneye dönüşebilmeli. Zorlama eşleşme varsa o kelimeyi atla. Aile dostu içerik.
  Hook ve story kalıbı mevcut örneklerle aynı olsun.

## Adımlar
0. Ön kontrol: `python3 -c "import PIL, numpy"` (yoksa `pip install --break-system-packages pillow numpy`), `which ffmpeg`.
   Tablonun Kelime sekmesini `get_values` (`Kelime!A1:G400`) ile oku. 'kuyrukta' satırı 6 veya fazlaysa üretme, kısa rapor ver.
   Yeni numaralar: tablodaki en büyük No + 1, +2, +3.
1. Her numara için words.json kaydı yoksa oluştur (yukarıdaki kurallar).
2. `img/<no>.jpg` yoksa görseli üret:
   - Higgsfield `generate_image` (tek tek ya da `generate_image_batch`; 429 hız sınırı gelirse birkaç saniye bekleyip
     sadece başarısız olanları tekrar gönder), `jobs_wait` ile bekle.
   - cloudfront adresi bu ortamdan indirilemez. ElevenLabs `creative_attach_reference_file` ile result_url'yi ekle
     (name: `k<no>.png`), sonra `creative_get_available_assets` (`asset_ids`) ile `preview_url` al ve
     `curl -sS -o img/<no>.webp "<preview_url>"` ile indir. Ardından jpg'ye çevir (1024x1024, quality 90).
   - Görsele bak. Yazı varsa ya da sahne çağrışımı anlatmıyorsa bir kez yeniden üret.
3. Seslendirme (her numara için 2 çağrı):
   - Hale: `<hook> [long pause] Anlamı: <mean>. [long pause] <story> [long pause] Yani: <trans>`
   - Clamon: `<Word>. [long pause] <sent[0]> <sent[1]>`
   - `creative_get_flow_run_status` ile bitmesini bekle, content_url'leri
     `curl -sS -o audio/v<no>/tr.mp3 "<url>"` ve `audio/v<no>/en.mp3` olarak indir.
4. `python3 kgen.py prep <no>`. "temiz bölünemedi" hatası verirse Hale metnini bir kez yeniden üret
   (aynı metin, yeni üretim), yine olmazsa o numarayı atla ve raporla.
5. `python3 kgen.py frames <no> 1.2 6 <kapak> 16` ile kontrol karesi al (`check.png`) ve bak: taşma, üst üste binme,
   eksik emoji (kutucuk) olmamalı. Sorun varsa words.json metnini kısaltıp düzelt.
   Sonra `python3 kgen.py build <no>`. Çıktı: `out/kelime-<no>.mp4`, `.cover.jpg`, `.json` (caption ve cover_ms içinde).
6. Git: `git add kelime/out/kelime-<no>.* kelime/data/words.json kelime/img/<no>.jpg`, commit "Kelime #<no>",
   `git pull --rebase` ve `git push`.
7. Tabloya satır ekle (`append_values`, range `Kelime!A1`):
   `[<no>, <word>, "kelime/out/kelime-<no>.mp4", <caption>, "kuyrukta", "", <cover_ms>]`
   Sadece push başarılı olduysa ekle. Bozuk satır ekleme.
8. Kısa rapor: üretilen kelimeler, kuyrukta bekleyen video sayısı, sorunlar.
