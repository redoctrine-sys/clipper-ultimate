# Naskah & Hook — Doktrin Penulisan Naskah Clipper

Tanda: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi. Status: **dilipat dari F7-21 + F7-22 (23 Nov 2026)** — menjawab kegagalan nyata: naskah K2 Hamka v1 datar, nama subjek baru beat 3, tanpa taruhan; lalu pace VO + void antar beat (v3–v6). Aturan keras yang sudah ada dan TIDAK BOLEH dilanggar: hard fact rule (teknik boleh susun ulang fakta, jangan tambah/ubah fakta), register naskah diputuskan dulu + humanize gate, prinsip trailer (premis ≤10 dtk), lock #5 (teks kartu = kata yang diucapkan), lock #6 (hook dari cerita itu sendiri).
Sumber metode (semua diparafrase dengan kata sendiri, tanpa salin verbatim; atribusi lengkap di `THIRD_PARTY_LICENSES.md`): hook-master-skill, video-agent-skills/studio-script, vyralcontent/content-skills, instagram-agent-skill/ig-reel, ai-business-skills 04-script-video-global (semua MIT) + writing-youtube-narratives, story-and-shots, creative-writing-craft, dialogue-and-audio, sw-dialogue, sw-scene-craft, sw-series-structure, chekhov-dramaturgy, ozu-screenplay-style, video-prompt-craft, casting_suara (skill lokal, TANPA LISENSI — metode diparafrase saja).

## 1. Apa itu hook clipper
Hook = 10 detik pertama (VO + kartu pertama + frame pertama) yang membuat penonton tahu tiga hal: (a) ini tentang siapa/apa, (b) apa taruhannya, (c) apa yang belum diketahui. Hook punya tiga lapis yang harus bekerja bersama: suara (kalimat VO pertama), visual (frame pertama — gerak/kontras, bukan wajah diam atau logo), teks layar (kartu pertama, ≤6 kata, bukan pengulangan kata-per-kata VO). Satu lapis yang diam tidak ditambal dua lapis lain — ketiganya diperiksa di G-STORY.

## 2. Kalimat pertama (lock #34)
- Kalimat pertama naskah = nama/peran subjek + taruhan/pertanyaan, dari fakta terverifikasi. "Siapa" = peran/relevansi, bukan nama saja ("anak yang akan jadi Buya Hamka" > "Abdul Malik Karim Amrullah").
- Larangan pembuka: sapaan ("halo", "selamat datang"), housekeeping ("di video ini saya akan..."), biografi datar ("Di [tempat], tumbuh seorang anak..."), logo/kartu judul, kalimat "saya/kami" (mulai dengan "kamu" / nama / angka / masalah penonton).
- Tulis 3 pembuka berbeda (dari format berbeda — lihat §4) lalu pilih terkuat; dua sisanya dicatat di naskah sebagai varian. Satu pembuka = satu tebakan; tiga pembuka = satu keputusan.
- Uji taruhan: bila tokoh bisa diam saja tanpa konsekuensi, taruhannya tidak cukup — hook lemah, cari taruhan lain dari fakta.

## 3. Cek premis SUBSTANSI ≤10 dtk (lock #35 — C09 diperbaiki)
- C09 lama hanya mengecek WAKTU mulai hook (`hook_time_s`). Itu tidak cukup: hook bisa mulai di 0,49 dtk tapi premis tetap tidak mendarat (kasus Hamka v1).
- Cek baru: pada detik ke-10, orang asing yang lelah harus bisa menjawab — setelah SEKALI dengar/baca — siapa tokohnya, apa yang dia mau, apa penghalangnya. Ketiganya harus terdengar (VO) atau terbaca (kartu/panel). Satu unsur hilang = FAIL → perbaiki NASKAH, bukan geser timing.
- Empat kegagalan (cek dengan kutipan kata persis, bukan kesan):
  1. **Terlambat** — topik datang sesudah basa-basi/sapaan/biografi. Perbaiki: potong semua kata sebelum kata pertama yang membawa subjek.
  2. **Membingungkan** — lebih dari satu makna, kata dalam/jargon, kata ganti tanpa rujukan ("dia" sebelum nama disebut), kalimat pintar yang butuh dua kali dengar. Perbaiki: satu makna, kata kerja aktif, sebut nama/bendanya.
  3. **Tidak relevan** — tentang pembuat, bukan penonton ("perjalanan saya", logo, kartu judul, "sedikit tentang kami"). Perbaiki: masalah/keinginan/keyakinan penonton dulu; cerita pembuat boleh muncul belakangan sebagai bukti.
  4. **Membosankan** — jelas dan relevan tapi tanpa kontras/pertanyaan (penonton sudah menduga isinya). Perbaiki: tambah kontras — yang penonton kira vs yang benar, cara lama vs cara ini, gagal vs beres — dari fakta yang bisa dibuktikan materi.
- Pengecualian: pembuka lisan yang samar BOLEH bila gambar/teks layar membawa hook (tiga lapis §1 dicek bersama, bukan satu-satu).

## 4. Format hook (pilih yang cocok dengan fakta — jangan pakai format yang butuh bukti yang tidak ada)
| Format | Bentuk | Butuh |
|---|---|---|
| Hasil dulu | Hasil/akhir dulu, lalu cara | Hasil nyata yang ada di materi |
| Pertanyaan | Pertanyaan yang penonton tidak bisa jawab "tidak" lalu swipe | Pertanyaan dari masalah penonton |
| Angka | Angka spesifik yang mengejutkan | Angka terverifikasi dari materi/brief |
| Kontras | "Berhenti [kebiasaan umum]. [Yang berhasil]" | Alternatif yang bisa ditunjukkan; jangan serang keyakinan yang tidak ada yang pegang |
| Penyelidik | "Kenapa [masalah], dan itu bukan [dugaan biasa]" | Sebab nyata yang dijelaskan video |
| Pengaku | Kesalahan/kerugian sendiri | Kejadian nyata dari materi (bukan karangan) |
| Guru | "Cara [hasil] tanpa [hal yang dibenci]" | Metode nyata yang ditunjukkan video |
- Kontras dulu, format belakangan: tulis satu baris "Penonton kira [A]. Video ini menunjukkan [B]." sebelum menulis hook. Bila tidak ada kontras yang bisa dibuktikan, idenya lemah — katakan begitu, jangan poles.
- Kejutan visual (Magician) hanya lapis tambahan di atas satu format di atas, bukan hook sendiri — frame-nya harus ada di materi.

## 5. Curiosity gap dari fakta (lock #36)
- Tahan SATU fakta kunci (twist/harga/akhir), BUKAN premis. Premis (siapa + mau apa + konflik) tidak pernah ditahan.
- Gap harus spesifik: penonton paham APA yang belum diketahui dan KENAPA itu penting. Beri pijakan dulu sebelum menahan info.
- Setiap setup dipasangkan payoff; jangan tumpuk gap tanpa jawaban. Beri jawaban sebagian (mini-payoff) di tengah; akhiri tiap seksi dengan tekanan maju (pertanyaan/kontras baru), bukan rekap.
- Larangan: clickbait (janji lebih kuat dari isi — janji yang tak terbayar = pelanggaran); angka/kutipan karangan; "rahasia / tidak ada yang memberitahu" tanpa bukti; pertanyaan yang bisa dijawab "tidak".
- Tahan-satu-fakta (delayed disclosure) hanya untuk SATU fakta per klip; wahyu belakangan yang mengubah makna awal hanya untuk penutup/button.

## 6. Struktur beat + QC naskah (lock #37)
- Bentuk: 0–3 dtk HOOK (klaim) · 3–10 dtk TARUHAN (kenapa penting bagi penonton, satu kalimat) · 10 dtk–akhir ISI (satu gagasan per beat; tiap beat = satu perubahan — penonton tahu/merasa/mau sesuatu yang baru; beat tanpa perubahan = eksposisi → potong) · 3 dtk terakhir PAYOFF (bayar janji hook) + satu ajakan.
- Tulis payoff dulu, baru hook (janji hook = apa yang dibayar di akhir).
- Re-hook di tengah: pertanyaan/kontras baru sebelum penonton pergi. Tiap segmen harus membalik nilai (ragu → yakin, aman → terancam, tidak tahu → tahu); segmen yang keadaannya sama di awal dan akhir = eksposisi → potong.
- Satu gagasan utama per klip; dua gagasan = dua klip. Maks 2 poin kunci.
- Aturan napas kalimat (lock #37 — menggantikan batas lama "kalimat maks ~15 kata", yang bertentangan dengan data): **kalimat > ~12 kata wajib punya ≥1 jeda tanda baca** (koma/titik dua); **frasa napas ≤ ~16 kata**; **hindari ≥3 kalimat deklaratif pendek berturut-turut dalam 10 dtk pertama**; **titik dua sebelum kata kunci = pola terbukti**. Uji pada teks asli K2: hook Kontras v4/v6 — "Anak yang kelak dikenal sebagai Buya Hamka ini lebih cinta adat dan sastra daripada pelajaran pesantren, dan bergumul dengan satu keinginan: belajar." (22 kata, koma + titik dua, frasa napas 16/5/1 kata) → **LOLOS**; hook Pertanyaan v3 — "Bagaimana anak yang lebih cinta adat dan sastra daripada pelajaran pesantren bisa menjadi Buya Hamka?" (15 kata, tanpa jeda) disusul "Di Maninjau, ia bergumul dengan satu keinginan: belajar." (8 kata) + "Tapi ia kerap berselisih dengan ayahnya." (6 kata) + "Kemudian, orang tuanya bercerai." (4 kata) → **GAGAL** (kalimat >12 kata tanpa jeda + 3 deklaratif pendek beruntun). Status [D, n=2 — validasi ke-2 out-of-sample parsial (naskah baru, materi F2); lingkup: K2 narasi, Helio, ID, ~28–35 dtk] (efektif n≈1,5; lihat LAPORAN_F8 §1.2). Satu gagasan per kalimat; tulis untuk telinga — baca keras sebelum rekam (cek baca keras tetap ada di QC naskah); bila tersendat dibaca, TTS juga tersendat.
- Kausalitas: gerak narasi karena/tapi/maka, bukan rentetan "lalu... lalu...".
- Audit fakta per kalimat: tiap kalimat naskah punya jejak ke `facts.json`/brief (klaim–sumber). Jangan karang kutipan, dialog, motif, kronologi, ukuran, detail adegan, atau kepastian.
- Checklist QC naskah (G-STORY + review-sheet): (a) 4 kegagalan §3 — PASS/FAIL per butir + kutipan; (b) premis substansi ≤10 dtk — siapa + mau apa + penghalang; (c) janji hook dibayar di akhir (ya/tidak + detik); (d) tiap beat mengubah sesuatu (ya/tidak); (e) 3 varian pembuka ditulis (ya/tidak); (f) panel penonton — 2 yang paling penting per klip (doom-scroller: gambar bergerak/teks terbaca? sceptic: klaim spesifik + bukti di layar? beginner: masalahnya dengan kata mereka sendiri? buyer: ketakutan/keinginan disebut?) — tiap panel SWIPE/STAY + alasan satu baris; (g) baca keras lolos (humanize gate).

## 7. Hook per kasus
- **K1 (trailer):** hook dari trailer itu sendiri — pilih momen/pertanyaan trailer yang paling tajam; jangan karang narasi di luar trailer. Premis dari adegan + dialog trailer. Boleh buka dari tengah/akhir aksi trailer, asal tidak membocorkan jawaban pertanyaan dramatisnya.
- **K2 (narasi statis):** hook DITULIS (lock #34–#37). Gambar diam → naskah harus memberi gerakan verbal: jangan biarkan narasi datar + gambar diam berjalan bersamaan tanpa perubahan. Panel berubah tiap beat.
- **K3 (highlight ucapan):** hook = kalimat sumber yang paling bertekanan (momen emosional terkuat biasanya kalimat TERPENDEK) — pilih momen, jangan tulis ulang ucapannya. Jangan pilih kutipan panjang yang menjelaskan perasaan.
- **K4 (dialog):** hook = pertukaran pertama yang menunjukkan keinginan tokoh; tiap baris dialog harus MELAKUKAN sesuatu (menantang, memohon, menolak), bukan menyampaikan fakta. Baris yang bisa diucapkan siapa saja = slogan → potong atau personalisasi (cover-the-names test).
- **K5 (gameplay):** hook = aksi/kejutan visual di frame pertama + reaksi streamer; premis (game apa, apa taruhannya, apa yang belum diketahui) terbaca dari gambar ≤10 dtk; tanpa kartu judul, tanpa teks penjelasan — bila aksi tidak terbaca tanpa teks, potong ke momen yang lebih terbaca atau punch-in, jangan menambal dengan kartu.
- **K7 (UGC/brand):** hook dari footage/reaksi nyata; jangan buka dengan logo/brand. Satu objek yang berulang lebih kuat dari lima objek sekali pakai.
- **K6 (angka):** buka dengan angka spesifik yang mengejutkan dari materi — bukan karangan.
- **K8 (revisi):** satu revisi = satu perubahan (hook, atau premis, atau register) — bukan ketiganya sekaligus.

## 8. Yang TIDAK diambil dari sumber riset
- Skor hook otomatis (skrip `hookscore.py`/`beats.py`, ig-reel) — skrip TIDAK dijalankan; metodenya didistilasi jadi checklist §6. (Keamanan: repo riset gagal pemeriksaan eksekusi — hanya teks SKILL.md yang dibaca.)
- Panel penonton sebagai data/survei/prediksi — hanya alat berpikir; jangan sajikan sebagai persentase penonton nyata.
- Arketipe bernama kreator (Kallaway/MrBeast/Hormozi/dsb.) — dipakai bentuknya, bukan mereknya.
- Funnel TOFU/MOFU/BOFU, mode produk/personal-brand, panduan syuting, strategi hashtag, viral score — kerangka pemasaran, bukan alur brief campaign.
- Alur kerja long-form, channel profile, "jangan buat shot list" — skala salah / berlawanan dengan clipper.
- Estetika drama lambat/anti-klimaks (Chekhov), peristiwa utama di luar layar (Ozu), aturan fiksi bebas (invent freely, unreliable narration, nonlinear) — berlawanan dengan hook cepat + hard fact rule.
- Struktur serial multi-episode, jumlah babak/halaman — skala film/TV, bukan klip 10–120 dtk.
- Rute produksi audio (casting_suara, dialogue-and-audio) — eksekusi suara, bukan doktrin hook; register tetap mengikat penyampaian.

## 9. Contoh (F7-21 — Hamka v1 vs arah v2)
- **v1 (GAGAL §3):** "Di Maninjau, Sumatera Barat, tumbuh seorang anak bernama Abdul Malik Karim Amrullah. Ia lebih cinta adat dan sastra daripada pelajaran pesantren." — Terlambat (biografi sebelum subjek dikenal); Membingungkan (nama panjang tanpa peran — penonton belum tahu ini Buya Hamka); Membosankan (tanpa kontras/taruhan). Nama "Hamka" baru beat 3.
- **Arah v2 (bukan naskah final):** kalimat pertama menyebut peran + taruhan dari fakta yang sama — anak yang akan jadi Buya Hamka, memberontak terhadap pesantren sampai berselisih dengan ayahnya. Fakta sama, susunan di balik: nama/peran dulu, konflik dulu, latar belakangan.

## 10. Pace narasi (lock #45) [D, n=2 — validasi ke-2 out-of-sample parsial (naskah baru, materi F2); lingkup: K2 narasi, Helio, ID, ~28–35 dtk]
- **Suara kanonik narasi = Helio (Shortwave TTS, `avocado_v2:MAI_03`), keputusan user 23 Nov 2026.** Angka pace di bawah dikalibrasi pada Helio, jadi tidak perlu kalibrasi ulang. Perintah: `/opt/hatch/bin/tts speak --language id --voice avocado_v2:MAI_03`. Suara lain hanya lewat aturan override lock #45 (alasan + tanggal + pace diukur ulang untuk suara itu; lihat SKILL.md lock #45 dan `templates/production.example.json`).
- **Pace ideal narasi Indonesia ≈ 2,3–2,4 kata/detik (0,42–0,44 dtk/kata)**, diukur dari VO final: jumlah kata naskah ÷ durasi file VO (bukan durasi klip). Di luar jendela ini intonasi memburuk — terlalu cepat terdengar datar/terburu-buru, terlalu lambat kehilangan tekanan.
- **≥1 hening internal per ~4 dtk** — jeda antar kalimat/frasa yang terdengar sebagai napas. Hening internal adalah bagian dari intonasi, bukan jeda kosong: kalimat pendek berurutan tanpa hening berbunyi datar walau pace-nya benar.
- **Anggaran kata per durasi VO (lock #45): anggaran kata = pace × durasi VO target; durasi VO target ≈ (awal title) − offset awal, yaitu durasi klip − title (≥1,5 dtk) − offset awal.** Jeda napas sebelum title adalah sisa (slack) di dalam jendela itu — idealnya ≥ ~1 dtk (v6: 1,29 dtk) — dan JANGAN dikurangkan dua kali (rumusan lama "klip − offset − jeda − title" salah kurangkan jeda; sudah dibetulkan di sini, 23 Nov 2026). Angka lama "klip ~40 dtk ≈ 75 kata" DIHAPUS — angka itu berasal dari v5 yang ditolak user; yang benar adalah anggaran per durasi VO, bukan per durasi klip. Uji rumus pada data nyata: **v4 — jendela VO tersedia 39,00 dtk** (klip 40,80; title mulai 39,30; offset 0,30); kebutuhan pada pace terukur 2,30 kata/dtk = 90 ÷ 2,30 = **39,13 dtk > 39,00 → LEBIH dari anggaran** (terbukti: ucapan berakhir 39,49, menabrak title 0,19 dtk). **v6 — jendela VO tersedia 33,20 dtk** (klip 35,00; title mulai 33,50; offset 0,30); kebutuhan pada pace terukur 2,35 kata/dtk = 75 ÷ 2,35 = **31,91 dtk ≤ 33,20 → DALAM anggaran** (sisa 1,29 dtk di dalam jendela; jeda napas aktual 1,43 dtk — selisih 0,14 dtk = ekor sunyi file VO setelah ucapan berakhir 32,07). Rasa terburu-buru v4 take 3 (2,30 kata/dtk) datang dari jumlah kata, bukan pace.
- **Pace saja tidak memperbaiki rasa terburu-buru — kepadatan isi yang menentukan.** Bila narasi terasa terburu-buru padahal pace sudah di jendela ideal, potong isi dulu (prinsip user: potong yang tidak pengaruh ke cerita/film), baru atur pace. Jangan perlambat TTS untuk menutupi naskah yang terlalu padat.
- **Hening antar beat: napas normal ≤~1,5 dtk.** Hening beberapa detik tanpa narasi = void — jelek (putusan user atas K2 v5: dua jeda 3,87 dtk). Bila hening antar beat <0,5 dtk, xfade antar panel dipersingkat mengikuti hening (v6: 0,5→0,25 dtk).
- **Durasi total mengikuti VO, bukan sebaliknya.** Bila jeda antar beat dirapatkan, durasi total dipendekkan mengikuti VO — mempertahankan durasi hanya memindahkan void ke sebelum title (v6: 40,80→35,00 dtk).
- **Bukti ukur (K2 Hamka, suara Helio, narasi Indonesia):** v1 2,38 kata/dtk (11 hening) = intonasi terbaik yang didengar user; v3 2,54 (4 hening) = flat; v4 take 2 2,50 (8 hening) = terlalu cepat; v4 take 3 2,30 (20 hening) = masih terasa terburu-buru karena 90 kata terlalu padat; v5/v6 2,35 (12 hening) = disetujui user (G-HUMAN v6, 23 Nov 2026). Angka ideal tervalidasi pada dua produksi K2 (Hamka v6 + Klik Film F8.7 v1, pace 2,3825 kata/dtk).
- **Kecepatan TTS nondeterministik per take (F7-29) — ukur durasi dan pace tiap take; pilih take yang masuk jendela.** Satu naskah yang sama bisa keluar dengan durasi berbeda jauh per take: v4 (Helio, 90 kata) take 2 = 36,048 dtk vs take 3 = 39,192 dtk (selisih 3,144 dtk); v5 (75 kata) take 1 = 31,920 dtk vs take 2 = 31,128 dtk. Jendela take = durasi VO target dari rumus lock #45 (± toleransi produksi) + pace terukur 2,3–2,4 kata/dtk. Take yang salah bisa terasa terburu-buru walau pace rata-ratanya dalam jendela — karena itu durasi take-lah yang dipilih, bukan hanya pace rata-rata. Catat tiap take (durasi, pace, hening internal) di production-log; hanya take terpilih yang dipakai. Verifikasi akhir via peta hening −20 dB mix akhir, bukan hanya angka pace.
