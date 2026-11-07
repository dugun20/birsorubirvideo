# @birsorubirvideo: günlük 3D bilgi videosu üretimi

Sayfa, bulmaca konseptinden "merak edilen soru + 3D anlatım" konseptine döndü (Cihan'ın kararı, Kasım 2026; eski
bilgi videoları 400 takipçi getirmişti). Her sabah çalışan görev bu dosyayı izler. Make senaryosu 8298082 kuyruktaki
sıradaki videoyu her gün 12:30 ve 20:30'da Reels olarak paylaşır; video adresi
`https://dugun20.github.io/birsorubirvideo/<Video dosyası sütunu>`. Cihan bu seri için sormadan seslendirme ve render
yapılmasını onayladı: kullanıcıya soru sorma.

Örnek ve şablon video: `videos/mariana/` (onaylı son hali `out/bilgi-1.mp4`). Yeni her video bu kaliteyi ve tarzı tutturmalı.

## Tarz (değişmez)
- Ana görüntü **tamamen hareketli 3D** (Three.js, kodla). Her cümlenin arkasında konuyu anlatan bir 3D sahne. Düz infografik değil.
- Referans tarz: üstte küçük etiket (`.tag`, büyük harf, 2–3 kelime), altında büyük başlık (`.title`, Oswald, beyaz + sarı `.y` vurgu),
  gerekirse büyük sayı (`.big`), sayaç, liste satırları (`.row`). Ekranın altında kelime kelime altyazı (motor otomatik yapar).
  Sol üstte "● BİR SORU BİR VİDEO" (motor ekler). Koyu, sinematik ışık, sis, partiküller.
- Ses: ElevenLabs **Orçun Toğan** `voice_id=c9eIhSvMHBxtYhLX4oBt`, model `eleven_v4`, `generations_count=1`. Arka plan müziği yok.
  Efektler `build.py` ile (whoosh, boom, pop, crunch, snap, ding, click).
- Süre 35–45 sn. Ekrandaki sayılar her zaman rakamla (10.935 m, 1.000 KAT). Seslendirme metninde sayılar yazıyla.
- Kapanış her zaman: "Bir sonraki soru: <topics.json'da sıradaki konunun sorusu> Kaçırmamak için takip et!"
  Son sahnede o konuyu anlatan 3D bir merak sahnesi + "SIRADAKİ SORU" etiketi + Takip Et düğmesi (`follow`).
  Son altyazı videonun sonuna kadar ekranda kalır (motor böyle yapar).
- Açıklama (caption), hashtag yok:
  `<Soru> <emoji>` / boş satır / 1–2 cümlelik merak uyandırıcı özet / boş satır / `Merak ettiğin her şey bu sayfada. Şimdi takip et.`

## Sıra kuralı (çok önemli)
- `topics.json` sıralı listedir. Her zaman `done=false` olan **ilk** konuyu üret; atlama, sırayı değiştirme.
- Videonun kapanışında duyurulan "bir sonraki soru", listede kendisinden sonra gelen konudur. Listede ondan sonra konu
  yoksa önce listeye 7 yeni konu ekle (aşağıya bak), sonra üret.
- Bir konu üretilemezse kuyruğa hiçbir şey ekleme; ertesi gün aynı konuyu tekrar dene.
- Liste 7'den az `done=false` konuya düşerse sona yeni konular ekle: herkesin merak ettiği, görselleştirilebilir, doğruluğu
  kontrol edilebilir sorular ("…ne olur?", "…nasıl…?", "neden…?"). Daha önce işlenenleri tekrar etme (Titanic yapıldı).

## Adımlar (her video için; günde 2 video)
0. Ön kontrol: `python3 -c "import PIL, numpy"`, `which ffmpeg`, `node -e "require('playwright')"` (yüklü olmalı, tekrar kurma).
   `cd bilgi && npm install` (three, @fontsource/oswald). Depo kökünde `python3 -m http.server 8765 --bind 127.0.0.1 &`.
   Kuyruk tablosu `1p4LOorRwq6WQahWz8-MPTedTwoG_DqMc3mzt17BS7so`, sekme **Sayfa1** (`Sayfa1!A1:G400`).
   Tür sütunu "bilgi" olup Durum "kuyrukta" olan satır sayısı 4 veya fazlaysa üretme, rapor ver. Değilse 2 video üret.
1. Araştırma: konuyu web aramasıyla doğrula. Her sayıyı ve iddiayı güvenilir kaynaktan teyit et. Emin olmadığın bilgiyi koyma.
2. Senaryo (Türkçe, 90–110 kelime): ilk cümle güçlü bir kanca (şaşırtıcı bilgi ya da soru), 5–7 kısa bilgi cümlesi,
   kapanış cümlesi (yukarıda). Seslendirme metninde sayılar yazıyla.
3. Seslendirme: `creative_generate_speech` (Orçun Toğan). Bitince `content_url`'yi `curl -sS -o videos/<slug>/vo.mp3 "<url>"` ile indir.
   Aynı üretimi asla ikinci kez başlatma.
4. Kelime zamanlaması: `creative_transcribe_audio` (model `eleven_scribe_v1`, `flow_id` = seslendirmenin flow'u,
   `connect_from` = seslendirme node_id). Sonuçtaki `words` listesinden `videos/<slug>/w.json` yaz:
   `[["kelime", başlangıç, bitiş], ...]` (yalnızca type=word).
5. `videos/<slug>/scene.js` yaz. `videos/mariana/scene.js` yapısını örnek al (`shots`, `titles`, `update`, `follow`, `sfx`, `END`).
   - Sahne sınırlarını cümle başlangıçlarına göre `w.json`'dan al. `END` = son kelimenin bitişi + 0.2.
   - `follow.t` = "Kaçırmamak" kelimesinin başlangıcı, `follow.click` = "takip" kelimesinin başlangıcı + 0.1.
   - Kadraj: dikey 9:16, `fov` 40, yatay görüş dar (mesafenin yaklaşık ±0.2 katı). Ana obje ekranın 650–1350 px yüksekliği
     arasında dursun: üst 250–650 px başlık bölgesi, 1400 px altı altyazı bölgesi. Objeleri bu aralığa yerleştir.
   - Kalite: `flatShading` kullanma; yumuşak geometri (yeterli segment), sis, 2–3 ışık (hemisphere/ambient + key + renkli rim),
     partikül, yavaş kamera hareketi. Her sahnede bir şey hareket etsin. Gerekirse `lib/engine.js` yardımcılarını kullan
     (`gradTex`, `snow`, `std`, `mountain`, `trenchFloor`, `hash`, easing).
6. Kontrol: `node render.js frames <slug> <her sahneden 1-2 zaman, virgülle>` ve `videos/<slug>/chk_*.jpg` karelerine bak.
   Taşma, kadraj dışı obje, okunmayan yazı, boş/siyah sahne varsa düzelt, tekrar bak.
7. Render: `node render.js video <slug>` (yaklaşık 8–10 dk). Ardından
   `python3 build.py <slug> <no> <kapak_saniye>` (kapak: başlığın ve ana 3D objenin göründüğü ilk sahneden bir an, ör. 2.0).
   `videos/<slug>/check.jpg` kontrol sayfasına bak.
8. `topics.json`'da konuyu `done: true` yap. Git: `git add bilgi/videos/<slug> bilgi/out/bilgi-<no>.* bilgi/topics.json`
   (raw.mp4 ve chk dosyaları .gitignore'da), commit "Bilgi #<no>: <slug>", `git pull --rebase`, `git push`.
9. Tabloya satır ekle (`append_values`, range `Sayfa1!A1`), sadece push başarılıysa:
   `[<tablodaki en büyük No + 1>, "bilgi", "bilgi/out/bilgi-<no>.mp4", <açıklama>, "kuyrukta", "", <kapak_ms>]`
10. Rapor (SendUserMessage, kısa, Türkçe): üretilen konular, kuyrukta bekleyen video sayısı, sorunlar.
