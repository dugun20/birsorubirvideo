# Rollo Racing (@RolloRacingTV) – global, konuşmasız bilye yarışı Shorts kanalı

Durum (20 Kasım 2026): kanal açık, #1 elle yüklendi. Otomatik üretim kuruldu → günlük iş akışı için `RUNBOOK.md`, kod `kit/`. (prototype/ eski deneme, kullanılmıyor)
Kanal adı: **Rollo Racing**, kullanıcı adı **@RolloRacingTV** (@RolloRacing boş bir hesapta dolu).

## Prototip (prototype/)
- `sim.py` – pymunk fizik: 8 renkli top, parkur (başlangıç kutusu + kapı, plinko, zikzak rampalar, 4 dönen çubuk, huni, tamponlar, damalı bitiş FINISH=6650). Seed ile çalışır; `python3 sim.py 0 6` seed tarar (lider değişimi, bitiş süresi).
- `render.py SEED out preview|full` – pycairo ile 1080x1920 60fps; zoom 1.55 lider takip kamerası, üstte "Pick your color! / WHO WINS?" kancası (y=350), canlı sıralama çubuğu (y=480), liderde taç, "GO!", final "<RENK> WINS!" + konfeti + "Did you pick <RENK>?". Çıktı video.mp4 + events.json.
- `sfx.py` – numpy sentez: çiviye çarpınca pentatonik tıngırtı, rampa tok vuruş, çubuk tak, kapı + whoosh, finiş zil + konfeti. Müzik yok.
- Gereken: `pip install --break-system-packages pymunk pycairo numpy pillow`, ffmpeg, Fredoka fontu (grumpo/kit/fonts → ~/.fonts).
- Örnek: seed 2 → PINK kazanır (sarıyı hunide geçer), ~28 sn.

## Yapılacaklar (onaylanan plan)
- Parça kütüphanesi: plinko, zikzak, dönen çubuk, huni, trambolin, asansör, ışınlanma, konveyör, sarkaç, açılır kapak, dar köprü, kırılan platform… her videoda 4–6 parça rastgele sıra.
- Temalar: uzay, şeker, buz, lav, orman, su altı, şehir, Cadılar Bayramı, Yılbaşı (renk/arka plan/engel görünümü).
- Formatlar: düz yarış, eleme yarışı, ülke yarışı (bayrak renkli toplar), 100 top yarışı, turnuva serisi (çeyrek/yarı/final ayrı videolar).
- Otomasyon kuruldu: Grumpo tablosunun "Rollo" sekmesi + günlük 2 üretim görevi + Make senaryosu 8708385 (YouTube bağlantısı "Rollo Racing YouTube" 13254106).
- Yazı kuralları: İngilizce, sayılar rakamla, üst yazı YouTube'un üst düğmelerinin altında (y≈350+).
