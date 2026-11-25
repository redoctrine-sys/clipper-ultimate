# K5 — Gameplay / rekaman layar

Tanda: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi.
**Orientasi: landscape belum divalidasi [T]** — resep ini portrait 9:16; jalur landscape tervalidasi n=1 hanya untuk K2 materi statis dari sumber landscape (F11, v0.8.0; lihat `K2-statis.md`).

**STATUS: resep lengkap, TERVALIDASI — production grade n=1, F10 (2026-11-24, Diablo IV Co-Op, lihat §17).** V1–V6 lulus; **V3 LULUS 25/25** — lembar buta akhirnya diisi penuh oleh user (F10.9, 22:29–22:44 WIB): 24 Ya + 1 Ya uji ulang butir 20 (f17, "Fallen"); butir 16 lulus PER PUTUSAN USER (typo, 22:54) sebagai override atas definisi terkunci dan konfirmasi Opus 22:47. Klaim DIPUTUSKAN USER 22:56 WIB (F10.9c): K5 = **"production grade n=1" (validated)**. Riwayat: review Opus FINAL 21:12 WIB memutuskan "partially validated" (V3 terukur sebagian 1/25, klaim DITOLAK); konfirmasi Opus 22:47 WIB menghitung V3 FAIL 1/25 — keduanya di-override user, tetap tercatat di §17. Versi **MINOR v0.6.1 → v0.7.0** diterapkan di F10.9c. **Jangan klaim production grade di luar cakupan K-12** (stack, punch-in, kartu manual K5, sumber 60 fps, OBS, chat-replay, satu pembicara/satu facecam tetap [T]).
**Sifat dokumen: DOKUMEN REFERENSI kasus K5 — menggantung pada SKILL.md + scripts (`render.py`, `qc_all.py`, `sub_voice_check.py`, `pause_anchor.py`) + dokumen referensi lain (K3, `naskah-hook.md`). BUKAN prosedur mandiri: definisi lock SKILL.md, daftar periksa gate, dan sintaks perintah skrip tidak diulang di sini kecuali yang terbukti di F10 (§8 audio). Pembaca baru yang ingin menjalankan K5 dari nol mulai dari SKILL.md §6, bukan dari berkas ini. Itu desain, bukan cacat — tetapi jangan salah harap: berkas ini tidak cukup sendirian untuk menjalankan validasi/produksi end-to-end.**
Frekuensi di campaign nyata: belum ada contoh [D via riset].
Asal metode: pola pencarian momen + contact sheet dipakai ulang dari K3 (§5–§10) dengan adaptasi gameplay; sinyal chat-replay dan bukti crop/blurpad berasal dari F9 (VOD 45r3OyaxvFE, internal test only); tidak ada teks/kode skill luar yang disalin.

## 1. Definisi & batas dengan K3/K4
K5 = klip vertikal 9:16 yang intinya **aksi/visual di layar** — gameplay, rekaman layar, aksi game — bukan ucapan pembicara. Satu sumber (VOD gameplay, rekaman OBS, rekaman layar) → N klip (default 20–60 dtk, ikuti `duration` brief).

**Kapan momen = K5, bukan K3:** tidak ada ucapan pembicara yang menjadi konten klip; yang bicara adalah **aksi/visual** (momen gameplay, kejutan di layar, reaksi wajah terhadap aksi). Ucapan streamer boleh terdengar sebagai latar/reaksi, tetapi klip tidak bergantung pada kata-katanya untuk dimengerti.

**Batas:**
| Kasus | Inti klip | Contoh |
|---|---|---|
| K3 | Ucapan 1 pembicara yang jadi konten | highlight ceramah/podcast/VOD talk |
| K4 | Dialog ≥2 pembicara yang jadi konten | percakapan, debat, wawancara |
| **K5** | **Aksi/visual di layar yang jadi konten** | **momen gameplay, fail/epic play, reaksi terhadap aksi** |
| K1 | Cerita trailer film | trailer → cerita 15–60 dtk |

**Uji batas (diputuskan di S4, dicatat di `moments.json`):** bila klip tidak bisa dipahami dengan suara dimatikan DAN tanpa kartu — tetapi bisa dipahami dari ucapan streamer — itu **K3, bukan K5**; pindahkan ke resep K3. Sebaliknya bila klip dipahami dari gambar saja (aksi + reaksi wajah), itu K5 walaupun ada ucapan latar. Bila ucapan pendek streamer memang perlu teks agar klip dimengerti, dan ucapan itu adalah konten — itu K3. Bila ucapan pendek itu hanya penjelas aksi (mis. teriakan reaksi satu-dua kata), tetap K5 dan teksnya mengikuti §9 (jalur manual K1, bukan caption narasi).
**Hibrida K3+K5:** satu sumber boleh menghasilkan klip K3 dan klip K5 sekaligus (F9: 9 kandidat K3 + 3 catatan_k5 dari satu VOD yang sama [D]); tiap klip dicatat kasusnya sendiri di `moments.json` dan diproduksi di folder klipnya sendiri.

## 2. Keputusan terkunci yang berlaku (ringkas; sumber: SKILL.md §3)
| Hal | K5 |
|---|---|
| Format | 1080×1920, 30 fps, H.264+AAC (**tidak ada varian horizontal**) |
| Loudness | **−18 LUFS; TP akhir AAC ≤ −3,5 (lock #42) — target rantai −3,8 (§8, headroom overshoot AAC); jangan menarget −3,5 di tengah rantai** |
| Teks kartu | **umumnya TANPA kartu narasi** (§9); teks hanya dari ucapan yang benar-benar terdengar (lock #5) |
| Timing | bila ada kartu ucapan pendek → jalur **manual** K1 (lock #4); `prop` **dilarang** untuk ucapan apa pun yang bukan VO TTS bersih |
| Hook | **hook VISUAL** — aksi/kejutan di frame pertama, tanpa kata (§6) |
| Overlay | judul permanen / watermark / logo **TIDAK masuk K5 v1**; opsional per-brief, baru dikerjakan bila ada brief yang memintanya |
| Crop | diverifikasi visual di frame lebar penuh (lock #10); **keputusan layout §7** |
| Musik game | **risiko Content ID** (§8) — dicatat, tidak diselesaikan di resep ini |

## 3. Pipeline K5
S0–S3 dikerjakan **sekali per sumber**; S4–S13 **satu folder produksi per klip** (`klip_<n>_<slug>/`), masing-masing dengan G-STORY, G-CROP, G-HUMAN, `brief_audit`, dan `production-log` sendiri. `probe.json`, `shots.json`, `transcript.json` (bila ada), `moments.json` hidup di folder sumber dan dirujuk tiap klip — sama seperti K3 (§7 SKILL.md, multi-klip).

| Tahap | Isi K5 | Keluaran | Gate |
|---|---|---|---|
| S0 | `brief.json` + keputusan K5 (jumlah klip, durasi, overlay diizinkan? hak materi game? musik game?). **Skema:** `brief.schema.json` TIDAK punya blok `k5` (kunci atas ada k3/k7, tidak ada k4/k5/k6) — tetapi skema tidak menyetel `additionalProperties`, sehingga kunci tambahan diizinkan dan validasi lolos 0 error; blok `k5.*` ditulis sebagai data tambahan (bukan field skema), item K5 yang divalidasi skema masuk `manual_items`. | `brief.json` | **G-BRIEF** |
| S1 | Akuisisi sumber (§4) | `sources.json`, `source.mp4` | asal = materi campaign/diizinkan brief |
| S2 | Probe + `shots.json` + **contact sheet** sumber (§5) | `probe.json`, `contact_*.png` | — |
| S3 | Transkripsi **hanya bila perlu** (§5.4) — bukan default K5 | `transcript.json` (opsional) | bahasa benar bila dipakai |
| S4 | Pilih momen gameplay-only (§5) → beat map → hook visual (§6). **Cek eksplisit akhir S4 (EG-7 [D F10]): `moments.json` WAJIB lengkap sebelum S5 — uji_batas + contact sheet 1 frame/2 dtk + frame hook per klip; S4 F10 tidak menghasilkannya dan S5 yang melengkapi — jangan biarkan lolos ke S5 tanpa cek ini.** | `moments.json`, `edl.json` | **G-STORY** |
| S5 | Layout 9:16 — blurpad vs stack (§7) | `crop_plan.json` + preview | **G-CROP** |
| S6 | Audio: sumber game sebagai role `source` (§8) | blok `audio` | — |
| S7 | Caption: umumnya tanpa kartu (§9) | `cards.json` (boleh kosong) | `kartu_lint` bila ada kartu |
| S8–S13 | Render (preflight) → QC → review → final + audit → posting → log | seperti pipeline universal | G-AUTO, G-HUMAN, G-FINAL |

## 4. S1 — akuisisi sumber
- Sumber hanya dari yang **diizinkan brief** (periksa `prohibitions.reupload` dan `footage.allowed_sources`; game/streaming sering punya larangan reupload dan aturan platform).
- **Dua jalur akuisisi:**
  - **(a) VOD/streaming yang sudah ada** (mis. VOD YouTube): `yt-dlp` sebagai program eksternal. Bukti F9 [D]: hanya **AVC 1080p = format 312** (1080p60 HLS, ~6,2 Mbps) yang tersedia untuk VOD uji; **format generik kini resolve ke AV1 → pin `134+140`** (F9-8); **yt-dlp bot-block intermiten** — retry ~8 menit kemudian lolos; **yt-dlp melewati file yang sudah ada** — hapus dulu atau pakai `--force-overwrites`. Konversi 60→30 fps terverifikasi di QC F9.8 (930/1680/1440 frame, tanpa judder kentara) — 60 fps sumber **boleh** dipakai, render akhir tetap 30 fps (lock #2).
  - **Format 1080p (tier B): pilih dari daftar format nyata** (`yt-dlp -F <url>`), pin AVC 1080p + AAC. Untuk PHBA9-1Y2R8: **137+140** — angka ini khusus materi itu, BUKAN aturan umum; aturan umumnya: pin dari daftar nyata, jangan pakai selektor generik (resolve ke AV1).
  - **(b) Rekaman baru di PC user (Skenario B): OBS Studio** (GPL-2.0, program eksternal, sudah baris 04 `THIRD_PARTY_LICENSES.md`). Langkah PC = instruksi untuk user, **bukan** otomatis (lock #14). Minta user merekam **game dan facecam sebagai sumber terpisah bila bisa** (dua track/sumber OBS terpisah) — ini yang memungkinkan layout stack di S5 tanpa memotong apa pun; bila hanya ada satu komposit (game + facecam PiP menempel), layout mengikuti §7 aturan komposit.
- **Format rekaman OBS [T K5-T1]:** belum ada format yang teruji untuk K5. Default operasional: minta user merekam **1080p60, H.264, bitrate tinggi** (alasan: sumber 60 fps memberi kebebasan konversi ke 30 fps seperti bukti F9; bitrate tinggi menjaga HUD/teks tetap terbaca setelah reframe). Format persis dicatat di `sources.json` saat materi diterima; bila user merekam 30 fps, itu diterima — bukan alasan menolak materi.
- **Hak materi game — DICATAT, JANGAN DISELESAIKAN:** siapa pemilik footage game (streamer? publisher game? platform?), apakah brief mengizinkan pemakaian cuplikan game, dan apakah ada musik berlisensi di dalam stream (§8) — ketiganya dicatat di `brief.json`/`sources.json` sebagai pertanyaan G-BRIEF. Agen **tidak** memutuskan legalitas; bila brief tidak menjawab, klip diberi label "valid sebagai tes" (bukan submission) sampai user memutuskan.
- Tautan privat/anggota-saja/butuh login: **berhenti dan minta berkas dari user** (lock #13).
- Catat asal + izin + format + sha256 di `sources.json` (protokol serah materi SKILL.md §6a berlaku bila materi diserahkan user).

## 5. S2/S4 — pencarian momen gameplay-only
K5 memakai ulang pola K3 (rubrik momen + contact sheet wajib + verifikasi visual) dengan sinyal pencarian yang berbeda: **tanpa transkrip penuh**. Prosedur F9.4 [D] — sinyal dipakai **berurutan**, berhenti di sinyal pertama yang memberi kandidat cukup:

### 5.1 Sinyal pencarian (berurutan)
1. **Chapters/deskripsi + timestamp komentar.** Chapters video, timestamp di deskripsi, dan komentar ber-timestamp yang menunjuk momen ("3:45:35 …"). Paling murah; bila tersedia dan cukup → pakai ini saja.
2. **Heatmap.** Bila platform menyediakan heatmap tontonan — untuk VOD uji F9 **TIDAK ADA** (0 heatmap [D]) — jadi sinyal ini sering kosong; kekosongan dicatat, bukan kegagalan.
3. **Lonjakan chat-replay.** Bila ada chat replay: hitung pesan per **bin 10 dtk** vs **median bergulir**; tandai bin yang melonjak. Hitung **token tawa/kaget** per bin (daftar F9: `wkwk, wkwkw, haha, anjir, gila, ngakak, hihu, hihuu` — sesuaikan dengan bahasa/komunitas streamer, dicatat di `moments.json`). **Geser jendela mundur karena chat lag 5–20 dtk** (F9: geser 15 dtk [D]). Kandidat = bin lonjakan + jangkar komentar ber-timestamp di dekatnya.

### 5.2 Heuristik gameplay-only (koreksi F9 — PENTING)
- **Ambang absolut densitas token TIDAK berlaku** [D F9]: baseline densitas token Windah hanya **0,0301** — ambang absolut dari materi lain akan salah mengklasifikasi semua jendela.
- Pakai **ambang RELATIF: densitas token < 0,5× baseline = curiga gameplay-only** (volume chat tinggi tapi token sangat sedikit → penonton bereaksi pada aksi di layar, bukan pada ucapan).
- **Heuristik mati bila baseline < 0,02** — di bawah itu densitas token terlalu tipis untuk membedakan apa pun; tandai semua kandidat sebagai "tidak terklasifikasi, perlu tonton manual" dan jangan pakai label gameplay-only dari angka.
- Label `kemungkinan_gameplay_only` di `moments.json`/`kandidat.json` adalah **dugaan dari angka, bukan putusan** — putusan akhir selalu dari **menonton jendela** (contact sheet + tonton langsung, §5.3).

### 5.3 Rubrik momen K5 (skor 0–2 per butir, dicatat di `moments.json`)
| Butir | Pertanyaan |
|---|---|
| Hook visual | Apakah 1–2 detik pertama sudah berupa aksi/kejutan visual yang terlihat tanpa suara? (§6) |
| Aksi/kejutan | Ada play epik, fail lucu, momen tak terduga, atau perubahan besar di layar? |
| Emosi/reaksi | Ada reaksi wajah streamer (kaget, ngakak, kecewa) yang memperkuat aksi? |
| Utuh | Apakah aksi **selesai** di akhir klip (hasil terlihat: menang/kalah/lolos/gagal), dan tidak bergantung pada konteks sebelum klip? |
| Layak tayang | Aman terhadap larangan brief; tidak ada info pribadi, konten eksplisit, atau jendela/overlay di luar topik di layar; musik game dinilai risikonya (§8) |
Skor ini penilaian agen (tidak ada skrip skor otomatis). Total kecil → jangan dipilih; lebih baik melapor "hanya N momen layak" daripada mengisi kuota.
**Ambang pilih P4 (kriteria-F10.md §3): total ≥7/10, Hook ≥1, Utuh ≥1, Layak tayang ≥1.** "Total kecil" = di bawah ambang ini.

**Cara memilih:**
1. User memberi poin/timestamp → petakan tiap poin ke jendela momen → tentukan awal dan akhir persis dengan **menonton** (bukan dari angka chat).
2. Tanpa poin ("cari sendiri") → jalankan sinyal §5.1 berurutan, shortlist 2–3× kuota, beri skor rubrik, pilih terbaik; urutan akhir = skor, bukan urutan waktu.
3. **Momen yang diminta user tidak ada / ada di timestamp lain → laporkan apa adanya.** Jangan memalsukan atau menyambung potongan agar terlihat ada.

**Verifikasi visual (WAJIB di G-STORY):**
- Buat contact sheet jendela momen (1 frame tiap 2 detik, kisi 6×N; ffmpeg `fps`, `scale`, `tile`) dan **lihat**. Cocokkan: aksi yang diklaim memang terlihat, facecam tidak terpotong oleh layout yang direncanakan (§7), HUD/teks penting terbaca di frame resolusi penuh (lock #20 — contact sheet hanya orientasi), tidak ada jendela aplikasi lain/info pribadi/konten eksplisit.
- Catat frame bukti di `moments.json` (`verifikasi_visual`). Tanpa bukti → momen tidak boleh lolos G-STORY.
- Wilayah bermasalah di layar: **v1 = hindari lewat layout atau potongan lain**. Blur wilayah = fitur render [T], ditunda (sama seperti K3).

### 5.4 S3 — transkripsi: hanya bila perlu, dengan mitigasi loop
- **Default K5: TIDAK ada transkripsi penuh.** Pencarian momen tidak butuh transkrip (§5.1); caption umumnya tidak ada (§9).
- Transkripsi hanya bila ada ucapan pendek yang perlu diverifikasi teksnya (§9) atau bila momen diduga K3 (lalu ikuti K3 §9).
- Bila transkripsi diperlukan, bukti F9 [D] mengikat:
  - **whisper small `-l id` HALUSINASI loop repetisi pada 5/9 chunk** (frasa identik diulang tiap 2,0 dtk; dialog game berbahasa Inggris "diterjemahkan" paksa ke kata Indonesia). Jangan percaya segmen whisper pada audio game tanpa verifikasi dengar.
  - **stable-ts tiny KOSONG pada audio game** — ASR-2 **harus divalidasi per materi**; kosong pada materi ini bukan bukti ASR-2 rusak, dan tidak boleh diasumsikan bekerja pada materi game lain.
  - **Dialog tumpang-tindih:** sumber naskah = transkrip kalimat + telinga user; word-level hanya alignment waktu.
  - **Mitigasi loop yang terbukti: transkripsi per-15-dtk-slice** (25 segmen koheren pada F9) — potong audio per 15 dtk sebelum whisper, bukan satu pass panjang.
  - Kata yang tidak bisa diverifikasi dengan mendengar = **[T]** di review-sheet §2a; hanya telinga user yang memutus (lock #11).

### 5.5 Contoh window gameplay-only (bukti F9, VOD 45r3OyaxvFE, 4h 3m / 14631 dtk, 193.036 pesan chat, 826 komentar ber-timestamp; chapters 0, heatmap 0)
Ketiga window ini berasal dari `f2-run/f9/kandidat.json` bagian `catatan_k5` — **BUKAN** `moments.json` (belum pernah diproduksi menjadi klip; jangan dikutip sebagai klip yang sudah jadi):
| # | Window (dtk) | Jam VOD | Sinyal | Skor |
|---|---|---|---|---|
| (a) | 13535–13565 | 3:45:35 | lonjakan 629 pesan/bin puncak, 7 token, jangkar komentar @13576/@13506 | 4,89 |
| (b) | 12775–12805 | 3:32:55 | 552 pesan, 5 token, jangkar komentar @12799 | 4,74 |
| (c) | 11455–11485 | 3:10:55 | 648 pesan, 4 token, tanpa jangkar komentar | 2,34 |
Pola ketiganya: volume chat tinggi, token sangat sedikit → diduga gameplay-only (aksi di layar, bukan ucapan). Window (c) berskor paling rendah (2,34) karena tanpa jangkar komentar — contoh bahwa skor angka saja tidak cukup; ketiganya tetap butuh tonton manual sebelum dipilih. Pembanding K3 dari VOD yang sama: kandidat skor tertinggi 13835–13865 (965 pesan, 25 token, skor 6,25, `kemungkinan_gameplay_only: false`) — token banyak = momen ucapan, bukan gameplay.
**Dua skala — jangan dicampur (koreksi F10.6b, K7).** Skor desimal di tabel ini (4,89 / 4,74 / 2,34 / 6,25) adalah **skor sinyal chat F9, bukan rubrik §5.3**; rumusnya **tidak tercatat** dalam berkas yang dirujuk di sini — yang tercatat hanya masukan mentahnya (pesan/bin puncak, token tawa/kaget, jangkar komentar) di `f2-run/f9/kandidat.json`. Skor rubrik §5.3 adalah bilangan bulat 0–10 (0–2 × 5 butir) dengan ambang P4 di atas. Pembanding K3 6,25 memakai skala sinyal yang sama. **Jangan membandingkan angka desimal ini dengan total rubrik 9/9/8 di §17.**
**Definisi densitas token (F9): token tawa/kaget ÷ pesan dalam jendela/bin.** Baseline Windah 0,0301; jendela K5 di atas 0,006–0,011 (7/629, 5/552, 4/648); jendela K3 #1 0,026 (25/965) — angka-angka ini memeriksa terhadap definisi tersebut. Sinyal chat-replay (§5.1 butir 3) memakai bin 10 dtk + geser lag 5–20 dtk (F9: 15 dtk); skrip penghitungnya rencana (K5-T11), belum ada.

## 6. Hook VISUAL tanpa kata
K5 tidak punya VO narasi dan umumnya tidak punya kartu — maka hook harus bekerja **dari gambar saja**. Aturan ini melengkapi `naskah-hook.md` §7 (baris K5 sudah ditambahkan di K47).
- **Frame pertama = aksi atau reaksi, bukan layar tenang.** Penonton harus melihat DALAM 1–2 detik pertama: sesuatu yang bergerak/berubah (tabrakan, ledakan, nyaris lolos, angka berubah) ATAU wajah streamer bereaksi keras (kaget/ngakak). Layar game yang statis + wajah diam = bukan hook — potong pemanasannya.
- **Premis visual ≤10 dtk:** pada detik ke-10, orang asing harus bisa menjawab dari gambar saja: game/aktivitas apa ini, apa yang sedang dipertaruhkan (menang/kalah/lolos/gagal), dan apa yang belum diketahui (apakah berhasil?). Satu unsur hilang = FAIL → potong ulang, bukan tambah teks.
- **Pengecualian tercatat, bukan pelonggaran [D F10 — K6, klarifikasi yang dibuat di F10 dari satu kasus (M-B)]:** bila ketiga pertanyaan premis di atas terjawab dari gambar di detik ke-10 tetapi satu unsur *identifikasi* (mis. nama boss) baru terbaca sesudahnya, itu BUKAN unsur premis yang hilang — aturan FAIL di atas tidak terpicu. Keterlambatan unsur identifikasi dicatat sebagai catatan P7 ("LULUS dengan catatan") dan disetujui G-HUMAN apa adanya; aturan untuk produksi berikutnya tidak berubah. Preseden F10: M-B — game + lawan boss terbaca di t=10, nama boss baru di t~15 (bar boss mulai ~1035); P7 "LULUS dengan catatan", G-HUMAN setuju 20:32 WIB.
- **Tiga lapis `naskah-hook.md` §1, versi K5:** suara = audio game/reaksi (bukan VO); visual = frame aksi; teks layar = umumnya TIDAK ADA — maka dua lapis yang ada harus bekerja lebih keras. Bila aksi tidak terbaca tanpa teks, pertimbangkan punch-in (§7) atau potong ke momen yang lebih terbaca — jangan menambal dengan kartu penjelasan (kartu penjelasan = sinyal momennya lemah).
- **Curiosity gap visual:** tahan HASIL aksi (apakah lolos?), bukan konteksnya. Setup = aksi dimulai; payoff = hasil terlihat di akhir klip (rubrik "Utuh" §5.3).
- **Jangan buka dengan logo/intro game, kartu judul, atau layar loading** — sama seperti larangan kartu judul di lock #6.
- **Baris K5 di `naskah-hook.md` §7** (sudah dilipat; asal usulan: FOLD SPEC): lihat §16/FOLD SPEC di bawah — satu baris K5: hook = aksi/kejutan visual di frame pertama + reaksi streamer; premis terbaca dari gambar ≤10 dtk; tanpa kartu judul, tanpa teks penjelasan.

## 7. S5 — layout 9:16: KEPUTUSAN stack vs blurpad
### 7.1 Keputusan (diputuskan di resep ini, dari bukti F9.7)
**Default K5 = blurpad. Stack dipakai hanya bila facecam/reaksi adalah hook atau harus besar — diputuskan per klip di G-CROP.**
**Peringatan [D F10 EG-2]: mode stack TIDAK ADA di `render.py` — stack TIDAK DAPAT dipilih di G-CROP sampai ada fase kode; default dan satu-satunya layout saat ini = blurpad. Tabel §7.2 dibaca dengan peringatan ini: baris "stack" adalah aturan bersyarat untuk masa depan, bukan opsi yang bisa dipilih hari ini.**

Alasan: bukti F9.7 [D] — tiap contact sheet VOD uji menunjukkan **gameplay 16:9 penuh + facecam PiP kecil di kanan-bawah**; crop cover 9:16 akan **MEMOTONG facecam**, dan reaksi Windah ADALAH konten klip. Untuk K5, aksi game penuh adalah konten — memotongnya dengan crop cover merusak momen; blurpad mempertahankan seluruh frame game + facecam utuh. Stack (facecam atas / game bawah) membesarkan facecam dengan mengorbankan ukuran area game — benar hanya bila reaksi wajah memang yang dijual klip itu.

### 7.2 Aturan kapan masing-masing
| Layout | Pakai bila | Jangan pakai bila |
|---|---|---|
| **Blurpad (default)** | aksi game penuh harus utuh (peta, HUD, banyak objek di tepi); facecam kecil sudah cukup (reaksi terbaca walau kecil); sumber komposit PiP menempel | facecam adalah hook utama dan tidak terbaca dalam ukuran kecil; HUD/teks penting tidak terbaca dalam ukuran blurpad (cek §7.3) |
| **Stack (facecam atas / game bawah)** | reaksi wajah adalah hook atau isi utama klip; facecam harus besar agar ekspresi terbaca; sumber OBS terpisah tersedia (game dan facecam sebagai sumber terpisah, §4) — **SEMUA ini hanya berlaku bila mode stack sudah ada; saat ini TIDAK ADA (§7.1), jadi baris ini tidak bisa dipakai** | area game jadi terlalu kecil sampai aksi/HUD tidak terbaca; sumber hanya komposit PiP (stack dari komposit = crop facecam dari frame lalu susun ulang — kualitas dan posisi tidak terjamin, [T K5-T5]) |

**Bila sumber komposit PiP dan stack diputuskan:** catat sebagai [T K5-T5] — cara memisahkan facecam dari komposit (crop wilayah PiP + upscale) belum teruji; default bila ragu = blurpad.
**Crop cover 9:16 pada frame game penuh = DILARANG sebagai default** — hanya boleh bila contact sheet membuktikan tidak ada konten penting di luar jendela crop (facecam, HUD tepi, objek aksi) dan dicatat alasannya di `crop_plan.json`.

### 7.3 HUD/teks penting harus terbaca
- **Cara cek: frame resolusi penuh, lock #20.** Klaim "HUD terbaca" hanya sah dari frame 1080×1920 hasil render (atau frame sumber resolusi penuh), bukan dari tile contact sheet atau preview kecil.
- **Cara ukur bbox elemen kunci [D F10]:** estimasi posisi persen dari gambar yang dirender di chat DUA KALI salah (±70–250 px) — jangan pakai. Yang benar: deteksi geometri (HoughCircles untuk orb/lingkaran) + masker warna + crop uji di koordinat terhitung; skala ×3 dari tier A (360p) ke 1080p meleset ~70 px — ukur ulang dari frame 1080p. Bbox acuan dicatat di `elemen_kunci_1080p.md` / `moments.json` sebelum G-STORY.
- Cek tiap elemen yang membawa informasi klip: skor/nyawa/waktu, nama misi, teks dialog game, minimap bila relevan. Bila satu elemen tidak terbaca pada layout yang dipilih → ganti layout (blurpad ↔ stack), atau punch-in (§7.4), atau potong ke momen lain. Jangan memperkecil elemen dengan menambahkan kartu di atasnya.
- **Durasi minimum HUD terlihat = [T K5-T6]** — tidak ada bukti untuk angka. Default operasional: elemen yang membawa informasi klip harus terbaca **selama ia relevan dengan aksi** (tidak ada angka detik yang diklaim); bila elemen hanya berkedip sesaat dan tidak terbaca, itu bukan elemen yang boleh dijadikan sandaran pemahaman klip.
- **Pelajaran F10.9 [D]:** baca frame agen salah 2 kali dari 25 butir lembar (f15: label elite diklaim terbaca padahal tidak ada; f12: banner diklaim terbaca penuh padahal transkripsi manusia 2 dari 4 kata meleset) — baca agen tidak pernah menggantikan tanda manusia. Ukuran piksel saja tidak memprediksi keterbacaan: teks banner ~9 px di bawah blurpad tidak andal terbaca, sementara nama boss ~6 px terbaca.

### 7.4 Facecam tidak menutup aksi
- Pada blurpad: facecam PiP sumber tetap di posisinya; pastikan ia tidak menutupi objek aksi/HUD penting pada momen kunci — bila menutupi, geser jendela blurpad/crop atau pilih stack; jangan menimpa facecam dengan kartu.
- Pada stack: batas antara facecam dan game tidak boleh memotong kepala streamer atau baris HUD atas game; periksa frame awal + tengah + akhir tiap klip (G-CROP).

### 7.5 Punch-in 1,2–1,5× pada event [A]
- Punch-in (zoom) pada event kunci: **1,2–1,5×** [A — asumsi kerangka awal, belum teruji]. **Punch-in belum teruji sebagai mode K5 (K5-T9; default 0 di F10) — jangan jadikan andalan; bila dipakai, buktikan dari frame (mendarat sebelum puncak, kedua cam utuh).** Pakai bila: aksi terjadi di wilayah kecil frame (mis. duel jarak jauh, teks kecil, objek penting di sudut) dan tanpa punch-in penonton tidak melihat apa yang penting.
- Jangan pakai bila: aksi sudah memenuhi frame; punch-in memotong HUD/facecam yang sedang relevan; atau zoom membuat gambar pecah (cek frame resolusi penuh).
- Punch-in harus **mulus**: mulai sebelum event, mendarat sebelum momen puncak, dan kembali (bila kembali) sesudah aksi selesai — loncat zoom di tengah aksi = cacat QC (§11). Aturan durasi transisi zoom = [T K5-T7] (default operasional: samakan dengan ritme potongan klip, jangan lebih cepat dari ~0,3 dtk — angka ini asumsi, bukan bukti).

## 8. S6 — audio
- **Sumber game sebagai role `source`** (seperti K3 §6): audio campuran stream/game + mic streamer dipakai apa adanya dari sumber; tidak ada VO tambahan kecuali brief meminta (bila brief meminta VO → itu narasi K2, bukan K5 murni — catat sebagai hibrida).
- **Musik game = risiko Content ID (DICATAT, TIDAK DISELESAIKAN):** stream GTA hampir pasti berisi musik radio berlisensi [A — dari sifat game; bukan hasil audit trek]. Untuk **uji internal boleh**; untuk **submission nyata = risiko Content ID** (klaim, demonetisasi, atau penolakan campaign). Agen tidak memutuskan "aman/tidak" — risiko dicatat di `brief.json` (blok `k5.musik_game` — blok `k5.*` tidak didefinisikan di skema, tetapi skema tidak melarang kunci tambahan sehingga validasi lolos 0 error; lihat §3 S0) + `production.json` + review-sheet, dan user yang memutuskan. Bukti yang bisa dicari (bukan diselesaikan): frame yang menunjukkan "Mute Licensed Music: On" — k1 membuktikan pengaturan ini bisa dibaca dari frame bila ada [D F9] — bila pengaturan itu ON, catat sebagai mitigasi yang mengurangi (bukan menghilangkan) risiko.
- **Tidak ada musik tambahan di atas audio game** (lock #40: K1/K4 dilarang tambah musik di atas dialog; analogi K5: audio game + reaksi sudah penuh — bed tier 1 hanya bila brief meminta dan audio game nyaris sunyi; bila dipakai, ikuti tangga tier lock #38–#44 dan catat di `production.json`).
- **DeepFilterNet untuk mic bising [opsional, 48 kHz]** (baris 13 `THIRD_PARTY_LICENSES.md`, MIT/Apache-2.0 dual): hanya bila mic streamer bising dan suara streamer relevan dengan klip; WAV 48 kHz; hasilnya dicek dengan mendengar (bukan angka). Bukan default — jangan proses audio yang sudah bersih.
- **Loudness — target rantai dulu, spesifikasi kemudian [D F10].** Spesifikasi akhir (lock #42): **I −18 LUFS (±1,0), TP AAC ≤ −3,5**. **Target rantai: I −18 / TP −3,8 / LRA 11** — dipakai di SEMUA pass loudnorm di bawah (pass 1 ukur, pass 2 dinamis, loudnorm linear `render.py`). **Jangan pernah menarget TP −3,5 di tengah rantai:** overshoot AAC terukur +0,06…+0,22 dB, sehingga target −3,5 menghasilkan AAC ≈ −3,28 dan MELANGGAR spesifikasi (preseden F4: WAV −3,60 → AAC −3,38, diterima saat itu hanya karena gate implementasi `qc_all` −3,0 — itu celah spec-vs-implementasi, bukan preseden yang boleh diulang). Target rantai −3,8 memberi headroom overshoot sehingga AAC tetap ≤ −3,5. Ini target rantai, bukan perubahan spesifikasi lock #42. Audio game yang dinamis (ledakan keras, bisik pelan) tetap diukur pada mix akhir; jangan normalisasi per segmen.
- **Audio game crest tinggi — resep loudnorm dinamis 2-pass [D F10, n=1, TERVERIFIKASI DAPAT DIEKSEKUSI ULANG].** Bila crest klip (TP − I) > anggaran 14,5 dB, gain/loudnorm linear saja TIDAK bisa mencapai −18 LUFS + TP −3,5 (bukti F10: crest 17,76–21,08 dB; loudnorm linear berakhir I ≈ −24,6/−24,2/−21,3 = GAGAL gate). Perintah di bawah disalin dari yang benar-benar dipakai F10 S6 dan **dieksekusi ulang 2026-11-24 dengan hasil byte-identik** (M-B: ekstraksi sha `30aeaf11…`, pass 2 sha `4d5745bf…`, ukur ulang I −18,52 / TP −3,80 / LRA 7,50). Ganti `<...>` dengan angka klipmu; `measured_*` dan `offset` diambil dari JSON pass 1.
  - **Langkah 0 — potong audio sumber dari jendela** (input-seek `-ss` sebelum `-i`; `src_in` = awal klip di dalam jendela, `dur` = durasi klip):
    `ffmpeg -y -ss <src_in> -t <dur> -i <window.mp4> -vn -c:a pcm_s16le audio-src.wav`
    (M-B: `-ss 5 -t 38 -i ../s4/window-M-B.mp4` → `audio-src-M-B.wav`, 6.703.278 B, sha `30aeaf11…`.)
  - **Langkah 1 — pass 1, ukur (dinamis, TANPA `measured_*`)**: filter `loudnorm` tanpa `measured_*` mengukur SEKALIGUS menormalisasi dinamis, dan mencetak JSON. Catat `input_i`, `input_tp`, `input_lra`, `input_thresh`, `target_offset` dari JSON itu:
    `ffmpeg -hide_banner -nostats -i audio-src.wav -af "loudnorm=I=-18:TP=-3.8:LRA=11:print_format=json" -f null -`
    (M-B: input_i −26,20 / input_tp −5,12 / input_lra 11,30 / input_thresh −37,06 / target_offset 1,26.)
  - **Langkah 2 — pass 2, terapkan (dinamis, DENGAN `measured_*` + `offset`)**: TANPA `linear=true` (default `loudnorm` = dinamis; `linear=true` hanya untuk pass linear `render.py` di langkah 3):
    `ffmpeg -y -hide_banner -i audio-src.wav -af "loudnorm=I=-18:TP=-3.8:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:print_format=json" -c:a pcm_s16le audio-s6.wav`
    (M-B: `measured_I=-26.20:measured_TP=-5.12:measured_LRA=11.30:measured_thresh=-37.06:offset=1.26` → `audio-s6.wav`, 29.184.102 B, sha `4d5745bf…`.)
    **Catatan sample rate (nit A, Opus FINAL):** tanpa `-ar`, filter `loudnorm` mengeluarkan **192 kHz** — terverifikasi dari disk: ketiga `audio-s6.wav` F10 = 192.000 Hz (M-B 29.184.102 B, M-F dan M-O juga 192.000 Hz). `render.py` menanganinya di langkah 3 (loudnorm linear + mux AAC 48 kHz; AAC akhir ketiga klip terverifikasi 48.000 Hz) — jadi perintah di atas dipertahankan apa adanya (byte-identik dengan yang dieksekusi F10). Bila pipeline lain memakai `audio-s6.wav` langsung tanpa `render.py`, tambah `-ar 48000` di pass 2 — opsi itu **belum diuji** byte-identik, jangan klaim sama.
  - **Verifikasi pass 2 — ukur ulang berkas hasilnya** (langkah 1 diulang pada `audio-s6.wav`): angka `output_i` yang dicetak filter pass 1 adalah estimasi internal (−19,26 pada M-B) dan **tidak sama** dengan ukur ulang berkas (−19,54); yang dicatat sebagai hasil pass 1/2 adalah **ukur ulang**. (M-B: ukur ulang pass 1 = I −19,54 / TP −3,80 / LRA 8,30 — meleset 1,54 LU dari target, jadi pass 2 WAJIB; ukur ulang pass 2 = I −18,52 / TP −3,80 / LRA 7,50.)
  - **Langkah 3 — loudnorm linear `render.py` di atasnya** (target yang sama I −18 / TP −3,8 / LRA 11; `render.py` menjalankan 2-pass linear sendiri: pass 1 ukur, pass 2 terapkan dengan `measured_*` + `linear=true` — lihat `render.py` `ln_args`/`sh`, baris ~467–478), lalu mux AAC 128k. **Verifikasi akhir: AAC harus I −18±1,0 dan TP ≤ −3,5** (M-B −18,37/−3,58; M-F −18,01/−3,74; M-O −18,05/−3,63).
  - **Nilai `measured_*` ketiga klip F10 (contoh kerja):** M-B `measured_I=-26.20, measured_TP=-5.12, measured_LRA=11.30, measured_thresh=-37.06, offset=1.26` (crest 21,08); M-F `measured_I=-26.74, measured_TP=-6.06, measured_LRA=6.80, measured_thresh=-37.07, offset=0.74` (crest 20,68); M-O `measured_I=-19.01, measured_TP=-1.25, measured_LRA=25.10, measured_thresh=-33.81, offset=-0.48` (crest 17,76; klip paling panas, TP −1,25 dekat clipping). Tanpa `gain_db` statis (gain 0 di `project.json`). Dugaan "butuh ~3 dB atenuasi ekstra" (S2 F10) TERBUKTI SALAH sebagai alat — atenuasi statis bukan alat yang tepat; kompresi dinamis yang tepat.
- **LRA bukan gate QC [D F10].** LRA M-O tetap 24,50–24,90 LU vs target 11 — dinamika ekstrem sifat asli klip (intro sunyi + ledakan); loudnorm dinamis tidak mengompresnya menjadi LRA 11. LRA dicatat, bukan disembunyikan; bila G-HUMAN menilai ledakan terlalu menghentak, itu keputusan pendengaran.
- **Tanpa digital silence** kecuali pengecualian terdeklarasi (lock #3).

## 9. S7 — caption
- **K5 umumnya TANPA caption narasi.** Tidak ada naskah, tidak ada VO, tidak ada kartu narasi. `cards.json` boleh kosong — kartu kosong bukan FAIL (catat "tanpa kartu, sesuai §9" di production-log).
- **Kapan caption diperlukan:** bila ada **ucapan streamer yang menjadi konten** (penonton harus membaca kata-katanya untuk mengerti klip) → itu **K3, bukan K5** — pindahkan kasusnya ke resep K3 dan ikuti K3 §7.
- **Bila ada ucapan pendek yang perlu teks** (satu-dua kata reaksi yang tidak terdengar jelas, atau istilah game yang perlu ditegaskan) → **jalur manual K1**: `cards.json` eksplisit dari jeda ucapan yang didengar/dilihat, celah 0,04, 2–7 kata, teks = kata yang benar-benar diucapkan (lock #4–#5). Jangan pakai `prop`; jangan pakai timestamp kata whisper mentah (§5.4). **Skema kartu (yang dibaca `render.py`):** tiap kartu wajib `id`, `start`, `end`, `text`; opsional `kind` (`"title"`), `size`, `y`, `boxborderw`, `lines`, `keywords` (0–2 kata). `speaker` hanya metadata — tidak dirender. `cards.json` = daftar kartu, atau `[]` bila tanpa kartu.
- **Kata kunci berwarna TIDAK relevan bila tanpa kartu** — mekanisme ASS/keywords (lock #32) hanya aktif bila ada kartu ber-`keywords`; pada klip K5 tanpa kartu, jalur caption ASS tidak dipakai dan tidak perlu diuji.
- Bila kartu ada, `--cuts` = batas beat klip (lock #17) dan kartu tidak boleh menutupi aksi/HUD/facecam (§11).

## 10. S8–S13 — render / QC / review / final / audit / posting / log
Mengikuti pipeline universal (SKILL.md §6) dengan penekanan K5:
- **S8 Render:** preflight (lock #18); render panjang terlepas dari sesi exec (`setsid nohup ... &`); sumber 60 fps → render 30 fps (lock #2); `crop_plan.json` mencatat layout yang dipilih per klip (blurpad/stack + alasan G-CROP).
- **S9 QC otomatis:** `qc_all` 0 FAIL (WARN beralasan); `sub_voice_check` lapis A dijalankan tiap klip — bila 0 kartu, hasilnya `ada_fail: false` atas himpunan kosong → dicatat **N/A beralasan**, bukan PASS atas isi kartu; QC khusus K5 §11 diperiksa pada frame resolusi penuh.
- **S10 Review manusia (G-HUMAN):** tanyakan [T] dengar dulu (lock #11) — untuk K5, [T] utamanya: kata ucapan pendek yang diragukan (§5.4), risiko musik game (§8), dan keterbacaan HUD yang hanya bisa diputuskan mata manusia. Batas iterasi K8 berlaku (2 penolakan → berhenti + laporan).
- **S11 Final + audit brief:** `brief_audit` 0 FAIL, 0 PENDING; risiko Content ID musik game dicatat sebagai N/A beralasan + keputusan user (bukan PASS diam-diam); `manual_audit.json` dibekukan (lock #11/S11).
- **S12 Posting & submit:** verifikasi tayang publik (TikTok kadang mengubah ke "Only me"), submit ≤24 jam, tayang ≥5 hari (§10 SKILL.md).
- **S13 Log:** `production-log.md` mencatat: sinyal pencarian yang dipakai (§5.1), skor rubrik + alasan tiap momen, keputusan layout + alasan G-CROP, risiko musik game + keputusan user, dan tiap [T] yang masih terbuka.

## 11. QC khusus K5 (di atas `qc_all` + §10 SKILL.md)
1. **HUD/teks penting terbaca** di frame resolusi penuh pada tiap momen kunci (lock #20); elemen yang tidak terbaca = FAIL, bukan WARN.
2. **Facecam utuh** — tidak terpotong layout (blurpad: PiP utuh; stack: kepala utuh; crop cover: bila dipakai, buktikan dari contact sheet tidak ada yang terpotong).
3. **Aksi tidak terpotong** — objek aksi/HUD tepi tidak hilang di luar jendela layout; momen puncak terlihat penuh.
4. **Punch-in mulus** — tidak ada loncat zoom di tengah aksi; zoom mendarat sebelum momen puncak.
5. **Tanpa kartu menutupi aksi** — bila ada kartu, tidak menutupi objek aksi, HUD penting, atau wajah pada saat ia tampil.
6. **Hook visual ≤2 dtk pertama** terbukti dari frame (aksi/reaksi terlihat, §6) — dicek di G-STORY, bukan gate otomatis.
7. **Audio game tidak terpotong** di batas beat (energi audio di batas ±80 ms [T — target, bukan gate otomatis; analogi K1 QC #2]).
8. **Musik game dicatat** risikonya di audit (bukan lolos diam-diam) — butir audit C-musik-game: sumber musik + keputusan user tercatat → PASS; tanpa catatan → PENDING.

## 12. Validasi K5 (F10) — SELESAI 2026-11-24 (hasil di §17)
Dikerjakan **di F10, setelah validasi K3**. Materi: **"Diablo IV Co-Op Gameplay with Terrorskull | Full Face Cam Playthrough", YouTube `PHBA9-1Y2R8`, kanal Kali719's Gaming Corner** — 3.313 dtk, 1920×1080 30 fps, CC BY, 2 facecam komposit tepi kiri, upload 2025-06-18. VOD F9 (45r3OyaxvFE) hanya **internal test**, bukan materi validasi submission (hak + musik game belum diputuskan).
Kriteria — **DIKUNCI sebelum uji, tidak berubah selama uji** (tiru pola K3 §11 / K4 §11; ambang JANGAN dilonggarkan):
| # | Kriteria | Ambang |
|---|---|---|
| V1 | 2–3 klip dari satu sumber, semua lolos `qc_all` | **0 FAIL** (WARN beralasan) |
| V2 | `sub_voice_check` lapis A (bila ada kartu; tanpa kartu → N/A beralasan) | **0 FAIL** |
| V3 | **P-pengukuran: layout + HUD** — HUD/teks penting terbaca di frame resolusi penuh pada tiap momen kunci (penanda manusia, ≥60 dtk aksi total); facecam utuh; aksi tidak terpotong | **0 elemen kunci tidak terbaca; 0 facecam terpotong; 0 aksi terpotong** di jendela uji |
| V4 | `moments.json` | lengkap: skor rubrik §5.3, alasan, **bukti contact sheet** tiap klip, momen yang tidak ditemukan dilaporkan; **plus keputusan layout per klip + alasan G-CROP** |
| V5 | G-HUMAN | disetujui user dalam **≤ 2 iterasi** |
| V6 | `brief_audit` | 0 FAIL, 0 PENDING |
Lulus → klaim production grade **hanya untuk K5**. Gagal → perbaiki resep (bukan ambang). Tidak ada kriteria pengganti yang dilonggarkan.

### 12.1 V3-sebagian (aturan pencatatan [D F10])
Bila user menjawab butir penentu V3 di chat (nama elemen kunci) tanpa mengembalikan lembar buta penuh, catat V3 **"terukur sebagian"** — butir penentu terkonfirmasi langsung oleh mata/telinga user; sisa butir bersandar pada cek agen (pembacaan frame render) dan dicatat apa adanya. **JANGAN klaim lembar penuh terisi. Mute-test BUKAN butir lembar V3** — itu kriteria P2 (premis dari gambar saja); jangan hitung jawaban mute-test sebagai butir V3. Aturan ini tetap berlaku untuk penandaan sebagian di masa depan. **F10.9 (2026-11-24):** lembar akhirnya DIISI PENUH oleh user (25/25, 22:29–22:44 WIB) — status "terukur sebagian" berakhir; V3 lulus per putusan user atas butir 16 (override 22:56 WIB, lihat §17). Konsekuensi klaim yang dulu DIPUTUSKAN review Opus FINAL 2026-11-24 21:12 WIB ("partially validated", klaim DITOLAK; versi PATCH v0.6.1 di F10.8) **di-override user 22:56 WIB** — klaim kini production grade n=1, versi MINOR v0.7.0.
**Pelajaran F10.9 (tetap benar, dari konfirmasi Opus 22:47):** (1) saat membangun lembar, pastikan tiap elemen benar-benar tampil di frame sampelnya — f15 tidak memuat label elite sama sekali, jadi butir 20 di sana cacat (bukan tidak terbaca); (2) tiap butir teks meminta transkripsi — jawaban blanket "Ya" TIDAK dihitung untuk teks (butir 20 adalah Ya blanket yang ternyata salah); (3) baca frame agen salah 2 kali dari 25 (f15 dan f12) — baca agen tidak pernah menggantikan tanda manusia.
**Cara membangun lembar buta (prosedur F10, `f2-run/f10/s5/v3/`):** (1) ekstrak 15–20 frame PNG dari **render draft 1080×1920** (bukan jendela sumber) — tiap peristiwa kunci + hook + akhir, cakupan total ≥60 dtk aksi; (2) beri nama file netral (`v3_f01.png`… — tanpa bocoran isi); (3) tulis pertanyaan ya/tidak per frame; untuk teks kunci tanyakan "tulis apa yang terbaca" TANPA menulis jawaban yang diharapkan di lembar; (4) kolom jawaban kosong, TANPA kolom penilaian agen (buta — cek buta: 0 kemunculan "lulus/pass/gagal/ragu/piksel" di lembar); (5) jawab dalam satu sesi dengan G-HUMAN, tanpa zoom. **Ambang "lulus" V3 (diputus review Opus FINAL 21:12 WIB): V3 lulus HANYA bila setiap butir lembar ditandai manusia dan memenuhi ambang terkunci (0 elemen tidak terbaca; 0 facecam terpotong; 0 aksi terpotong); tidak ada ambang berbasis hitungan sebagian butir — penandaan sebagian = partially validated.** F10: lembar akhirnya diisi penuh user (25/25, F10.9) — 24 Ya + 1 Ya uji ulang butir 20; butir 16 lulus per putusan user (override atas definisi ini, 22:56 WIB) → V3 LULUS.
**Rujukan definisi (K10):** V1–V6 di `kriteria-F10.md` §1 (cara ukur V3 §2); P1–P11 §3; K-1…K-13 §5 — syarat K-4 (2) = mode stack terbukti ada di EG-2 (P5 §3; gagal di F10 karena stack tidak ada); cakupan K-12 = ruang lingkup klaim production grade (§5, baris K-12); U1…U10 di `rencana-F10.md` §2; EG-1…EG-7 di §3. Singkatan: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi.

## 13. Dependensi kode yang MENUNGGU (tidak dikerjakan sekarang; dicatat sebagai [T]/rencana, JANGAN tulis kode)
| Item | Isi | Syarat uji (terbukti FAIL di versi lama) |
|---|---|---|
| `render.py` — layout stack | bila stack butuh render baru (dua sumber terpisah disusun vertikal: facecam atas / game bawah) — apakah `render.py` sekarang sudah bisa, atau butuh mode layout baru | klip stack: facecam utuh + game utuh di frame 1080×1920; versi tanpa mode stack tidak bisa menyusunnya — **[T K5-T8]** |
| `render.py` — punch-in | apakah punch-in 1,2–1,5× sudah didukung `crop_plan.json` (pan/zoom) atau butuh kunci baru | event dengan punch-in: zoom mendarat sebelum puncak, tanpa loncat — **[T K5-T9]** |
| `render.py`/`qc_all.py` — cek HUD | cek otomatis keterbacaan HUD (mis. deteksi teks/HUD di wilayah kunci) — kandidat, belum tentu layak; G-HUMAN tetap penentu | negatif: HUD tidak terbaca → FAIL — **[T K5-T10]** |
| Skrip sinyal chat-replay | bila F10 memakai sinyal §5.1 butir 3 secara rutin: skrip hitung bin 10 dtk + token + geser lag (bukan manual) | kandidat yang sama ditemukan skrip vs manual — **[T K5-T11]** |
| `qc_all.py` — butir C-musik-game | butir audit §11 #8 (risiko musik game tercatat) — ditegakkan otomatis bila ada field musik di `production.json` | tanpa catatan musik → PENDING — **[T K5-T12]** |
Tidak ada perubahan kode pada batch dokumen ini.

## 14. Kegagalan yang diantisipasi
| Kegagalan | Mitigasi |
|---|---|
| Momen yang diminta tidak ada / hanya ada sebagai ucapan | lapor apa adanya; bila ucapan → pindahkan ke K3, jangan dipalsukan |
| Chat-replay tidak ada / heatmap tidak ada / chapters kosong | sinyal berurutan §5.1 — turun ke sinyal berikut; bila semua kosong → tonton manual + laporkan |
| Heuristik token salah klasifikasi (baseline rendah/aneh) | ambang relatif §5.2 + mati bila baseline <0,02; putusan akhir selalu tonton manual |
| Whisper halusinasi loop pada audio game | slice 15 dtk (§5.4); jangan percaya segmen tanpa dengar; kata ragu = [T] |
| ASR-2 kosong pada audio game | ASR-2 divalidasi per materi; jangan asumsikan bekerja |
| Crop cover memotong facecam/HUD | default blurpad (§7); crop cover hanya dengan bukti contact sheet |
| Stack mengecilkan game sampai HUD tak terbaca | aturan §7.2; bila ragu → blurpad; cek frame resolusi penuh |
| Punch-in meloncat / memotong HUD | §7.5; cek frame berurutan; bila ragu jangan punch-in |
| Musik game berlisensi → Content ID | catat risiko (§8); user memutuskan; jangan klaim aman |
| HUD tidak terbaca setelah reframe | ganti layout / punch-in / potong ke momen lain; jangan tambah kartu penjelas |
| Mengisi kuota dengan momen lemah | boleh melapor kurang dari kuota |
| Rekaman OBS satu komposit, stack diinginkan | [T K5-T5]; default blurpad |
| yt-dlp bot-block / format AV1 / file sudah ada | retry ~8 menit; pin 134+140; hapus dulu/`--force-overwrites` (§4) |
| Loudness mengikuti angka lain tanpa sadar | lock −18; konflik brief diputuskan di G-BRIEF |

## 15. Done criteria khusus K5 (di atas §10 SKILL.md)
1. Tiap klip: `moments.json` dengan bukti contact sheet + skor rubrik + **keputusan layout dan alasan G-CROP**; momen tak ditemukan dilaporkan.
2. Tiap klip: G-HUMAN disetujui eksplisit; `brief_audit` 0 FAIL (risiko musik game tercatat + diputuskan user).
3. Laporan per sumber: daftar klip (judul, durasi, timestamp sumber, layout, saran caption TikTok), plus hal yang tidak ditemukan/diubah → `production-log.md` + `caption_tiktok.txt` per klip.
4. QC khusus K5 (§11): 0 elemen kunci tidak terbaca, 0 facecam terpotong, 0 aksi terpotong.

## 16. Daftar [T] K5 (keputusan butuh user/Opus/F10 — dicatat, resep tetap jalan)
| # | Butir | Default + alasan |
|---|---|---|
| K5-T1 | Format rekaman OBS | Default: 1080p60 H.264 bitrate tinggi. Alasan: sumber 60 fps terbukti bisa dikonversi ke 30 fps tanpa judder kentara (F9.8); bitrate tinggi menjaga HUD terbaca. Format persis dicatat di `sources.json`; 30 fps diterima. **Tetap [T] setelah F10 — F10 memakai VOD YouTube, bukan OBS; tidak diputuskan.** |
| K5-T2 | Ambang scene-detect K5 | Default: pakai prosedur K1 S2 (0,3 → 0,1 + scan diff cv2 per 0,25 dtk + verifikasi visual). Alasan: tidak ada bukti ambang khusus gameplay (potongan game ≠ potongan kamera trailer); prosedur K1 adalah yang terdekat dan sudah terbukti. Angka khusus K5 TIDAK diklaim. **Tetap [T] — tidak dikalibrasi di F10.** |
| K5-T3 | Ambang relatif densitas token (0,5× baseline) | Default: <0,5× baseline = curiga gameplay-only; heuristik mati bila baseline <0,02. Alasan: ambang absolut terbukti tidak berlaku (baseline Windah 0,0301); 0,5× adalah pemisah operasional sementara, bukan hasil kalibrasi. **Tetap [T] — tidak ada kalibrasi di F10; tidak ada materi kedua.** |
| K5-T4 | Daftar token tawa/kaget per streamer/bahasa | Default: daftar F9 (`wkwk, wkwkw, haha, anjir, gila, ngakak, hihu, hihuu`). Alasan: satu-satunya daftar yang teruji; komunitas lain pasti berbeda. Daftar per materi dicatat di `moments.json`. **Tetap [T] — sinyal chat-replay tidak dipakai di F10; tidak diputuskan.** |
| K5-T5 | Stack dari sumber komposit PiP | Default: bila sumber hanya komposit → blurpad. Alasan: memisahkan facecam dari komposit (crop PiP + upscale) belum teruji kualitas/posisinya. **Tetap [T] — F10 memakai komposit dengan blurpad; stack dari komposit tidak diuji.** |
| K5-T6 | Durasi minimum HUD terlihat | Default operasional: elemen harus terbaca selama ia relevan dengan aksi; TIDAK ADA angka detik yang diklaim. Alasan: tidak ada bukti untuk angka; mengklaim angka = mengarang. **Tetap [T] — hanya data kalibrasi px terkumpul di F10; tidak dikalibrasi.** |
| K5-T7 | Durasi transisi punch-in | Default operasional: samakan dengan ritme potongan klip, jangan lebih cepat dari ~0,3 dtk (asumsi). Alasan: tidak ada bukti; 0,3 dtk adalah batas bawah kewajaran visual, bukan hasil ukur. **Tetap [T] — tidak dikalibrasi di F10.** |
| K5-T8 | Mode layout stack di `render.py` | **TIDAK ADA [D F10 EG-2]** (0 kecocokan "stack" di seluruh `scripts/*.py`; mode yang ada: crop, cover, fit, blurpad). F10 berjalan blurpad saja; stack tetap [T], butuh fase kode terpisah. Diputuskan di F10: syarat K-4 (2) gagal → stack tidak dapat diuji |
| K5-T9 | Dukungan punch-in di `crop_plan.json` | **Belum teruji sebagai mode K5 di F10** (default 0; mekanisme pan/zoom ada di `render.py`, belum teruji sebagai punch-in) — tetap [T]. Diputuskan di F10 |
| K5-T10 | Cek otomatis keterbacaan HUD | Rencana: kandidat deteksi teks/HUD; G-HUMAN tetap penentu sampai ada bukti cek otomatis bisa dipercaya. **Tetap [T] — cek otomatis tidak dibangun di F10.** |
| K5-T11 | Skrip sinyal chat-replay | Rencana: skrip bin 10 dtk + token + geser lag bila F10 memakai sinyal ini rutin. **Tetap [T] — skrip tidak dibangun; sinyal chat-replay tidak dipakai di F10.** |
| K5-T12 | Butir audit C-musik-game di `brief_audit.py` | Rencana: penegakan otomatis bila ada field musik di `production.json`. **Tetap [T] — butir audit tidak dibangun di F10.** |
| K5-T13 | Hak materi game + musik game untuk submission | TIDAK ADA default — dicatat sebagai risiko, user memutuskan per produksi (G-BRIEF). Alasan: keputusan legal/risiko bukan wewenang agen. Bukan blocker resep; klip tanpa keputusan = "valid sebagai tes" |
| K5-T14 | Validasi seluruh resep K5 | **F10 SELESAI 2026-11-24 (lihat §17):** V1–V6 lulus (V3 lulus 25/25 per putusan user, F10.9c); klaim DIPUTUSKAN USER 22:56 WIB: "production grade n=1" (validated) — override atas putusan Opus FINAL 21:12 ("partially validated") dan konfirmasi Opus 22:47 (V3 FAIL 1/25); versi MINOR v0.6.1 → v0.7.0 diterapkan di F10.9c |

## 17. Hasil validasi F10 [D, 2026-11-24] — Diablo IV Co-Op (PHBA9-1Y2R8)

Materi: 3.313 dtk, 1920×1080 30 fps, CC BY, upload 2025-06-18, kanal Kali719's Gaming Corner; 2 facecam komposit tepi kiri (Terrorskull atas, Kali719 bawah). Kriteria dikunci user 17:37 WIB (sha saat dikunci `b784d947…`); **tidak ada ambang yang berubah selama uji**. G-HUMAN disetujui user apa adanya 20:32 WIB (0 iterasi, jawaban: "1. Kebaca 2. Kebaca 3. Layak"); G-FINAL LULUS ketiga klip 20:32–20:36 WIB; final = salinan draft (sha identik). Laporan lengkap: `LAPORAN_F10.md` (goal root).

| Klip | Jendela sumber | Durasi | final.mp4 sha256 | qc_all | brief_audit |
|---|---|---|---|---|---|
| M-B — boss X'FAL | 1020–1058 | 38 dtk | `ea05020c…` | 7 PASS / 0 FAIL | 14 PASS / 0 FAIL / 0 PENDING |
| M-F — Ancient Syphon | 2436–2494 | 58 dtk | `10535405…` | 7 PASS / 0 FAIL | 14 PASS / 0 FAIL / 0 PENDING |
| M-O — dungeon api, ledakan skill | 840–898 | 58 dtk | `bc90d510…` | 7 PASS / 0 FAIL | 14 PASS / 0 FAIL / 0 PENDING |

**V1 LULUS** (3 klip, qc_all 0 FAIL) · **V2 LULUS** (sub_voice_check lapis A `ada_fail: false` — dijalankan atas himpunan kosong, 0 kartu diperiksa → N/A beralasan, §9) · **V3 LULUS 25/25 (F10.9, per putusan user)** (lembar buta 25 butir / 19 frame disiapkan, `lembar-V3.md` sha `6ac9d935…`, cakupan 154 dtk ≥60 dtk — diisi penuh oleh user 22:29–22:44 WIB, `lembar-V3-terisi.md`: 24 Ya + 1 Ya uji ulang butir 20 (f17, "Fallen"); butir 16 lulus per putusan user bahwa kesalahannya typo — override atas definisi terkunci dan konfirmasi Opus 22:47. Riwayat: di G-HUMAN 20:32 WIB user hanya menjawab 3 pertanyaan di chat, verbatim "1. Kebaca 2. Kebaca 3. Layak" — saat itu yang dikonfirmasi langsung hanya 1/25 (nama boss, self-report); 24 butir bersandar cek agen — lihat §12.1) · **V4 LULUS** (`moments.json` sha `b3cbded5…`: skor rubrik 9/9/8, alasan, contact sheet 1 frame/2 dtk, keputusan layout + alasan per klip) · **V5 LULUS** (disetujui 0 iterasi, ≤2) · **V6 LULUS** (brief_audit 14/0/0/0 per klip). **P1–P11: LULUS** (P5, P7, P8, P11 dengan catatan — lihat `LAPORAN_F10.md` §1.2). **Klaim DIPUTUSKAN USER 22:56 WIB (F10.9c): K5 = "production grade n=1" (validated)** — V1–V6 dan P1–P11 lulus; V3 lulus 25/25 per putusan user. Riwayat: review Opus FINAL 21:12 WIB memutuskan "partially validated" (V3 terukur sebagian 1/25, klaim DITOLAK; versi PATCH v0.6.1 di F10.8); konfirmasi Opus 22:47 WIB menghitung V3 FAIL 1/25 (butir 16 tidak terbaca) — keduanya di-override user. Versi **MINOR v0.6.1 → v0.7.0** diterapkan di F10.9c.

**Audio (S6, bukti resep §8):** crest 21,08 / 20,68 / 17,76 dB; loudnorm dinamis 2-pass; AAC akhir M-B −18,37 LUFS / TP −3,58 (WAV −18,32/−3,80, overshoot +0,22), M-F −18,01/−3,74 (WAV −17,94/−3,80, +0,06), M-O −18,05/−3,63 (WAV −18,02/−3,80, +0,17); LRA M-O 24,50–24,90 LU (bukan gate).

**Catatan ketelitian S2→S4 (bukan aturan baru — fakta yang dikoreksi pengukuran ulang dari jendela 1080p):** ejaan banner **"ANCIENT SYPHON"** (bukan "SIPHON"); quest M-B **"QUEST COMPLETE / DARKNESS WITHIN"** (bukan "A Hero's Reward" — itu quest berikutnya); bar boss M-B mulai **~1035** (bukan ~1032); puncak ledakan M-O **~889** (bukan ~888). Catatan S2 yang salah tidak dihapus dari sejarah — koreksinya dicatat di `f2-run/f10/s2/koreksi-S4.md` (sha `7a9e447d…`) dan dilipat ke sini sebagai pengingat: klaim S2 dari tier A (360p) wajib diukur ulang dari 1080p sebelum dibekukan di G-STORY.

**Yang tetap [T] setelah F10 (pemetaan 1:1 ke §16):** K5-T1 format rekaman OBS; K5-T2 ambang scene-detect K5; K5-T3 ambang relatif densitas token; K5-T4 daftar token per streamer/bahasa; K5-T5 stack dari sumber komposit PiP; K5-T6 durasi minimum HUD (hanya data kalibrasi px yang terkumpul); K5-T7 durasi transisi punch-in; K5-T8 mode stack di `render.py` (TIDAK ADA, EG-2); K5-T9 dukungan punch-in (belum teruji); K5-T10 cek HUD otomatis; K5-T11 skrip sinyal chat-replay; K5-T12 butir audit C-musik-game; K5-T13 hak materi game + musik game untuk submission (dicatat sebagai risiko, user memutuskan per produksi). Di luar nomor T: sumber 60 fps, satu pembicara/satu facecam, kartu manual K5 (tidak dipakai — semua klip tanpa kartu). Musik game: risiko Content ID TERCATAT (terdengar di mix sumber; trek belum teridentifikasi), tidak diklaim aman; klip "valid sebagai tes", tanpa posting; G-POST masih terbuka.

## Catatan integrasi (FOLD SPEC — untuk dilipat koordinator; JANGAN dikerjakan di batch ini)
**⚠️ FOLD SPEC HISTORIS — SUDAH TERLEWATI OLEH F10 + F10.9c (koreksi F10.6b, K3). Ditulis 2026-11-23 saat K5 masih DRAF / BELUM tervalidasi. F10 (2026-11-24) mengubah status menjadi "TERVALIDASI SEBAGIAN" (klaim "partially validated" diputus review Opus FINAL 21:12 WIB; versi PATCH v0.6.1 di F10.8); F10.9c (2026-11-24 22:56 WIB) mengubah status menjadi "TERVALIDASI — production grade n=1" (klaim diputus user sebagai override atas putusan Opus; versi MINOR v0.7.0). Butir 1/3/6 di bawah ini sudah disesuaikan ke status BARU itu; bila koordinator melipatnya ke SKILL.md, yang dilipat adalah status BARU itu, bukan "BELUM tervalidasi" atau "TERVALIDASI SEBAGIAN". Jangan terapkan perintah lama yang menulis "BELUM tervalidasi" tanpa penyesuaian ini.**
Perubahan SKILL.md yang diperlukan:
1. **§4 tabel kasus, baris K5:** `K5 Gameplay | rekaman layar/OBS | belum ada contoh | **DITUNDA** — kerangka saja` → `K5 Gameplay | rekaman layar/OBS | belum ada contoh | **references/K5-gameplay.md — TERVALIDASI — production grade n=1 — F10** (klaim diputus user 22:56 WIB, F10.9c, sebagai override atas putusan Opus FINAL 21:12 WIB; versi MINOR v0.7.0; keputusan layout: default blurpad, stack bila facecam adalah hook — K5 §7)`.
2. **§4 pohon cepat:** tambah di akhir: `aksi di layar yang bicara (bukan ucapan) → K5`.
3. **§11 peta references:** `K5-gameplay.md` (ditunda) → `K5-gameplay.md` (TERVALIDASI — production grade n=1 — F10; klaim diputus user 22:56 WIB, F10.9c; versi MINOR v0.7.0).
4. **§9 daftar larangan:** tambah butir K5: memakai crop cover 9:16 sebagai default pada frame game penuh (default = blurpad, K5 §7); mengklaim HUD terbaca dari tile contact sheet (hanya frame resolusi penuh, lock #20); menambahkan kartu penjelasan untuk menambal momen yang tidak terbaca; mengklaim musik game aman dari Content ID tanpa keputusan user; memakai timestamp kata whisper mentah untuk caption pada audio game.
5. **§10 done criteria:** tambah penunjuk: kriteria khusus K5 di `K5-gameplay.md` §15.
6. **Blok STATUS di kepala SKILL.md:** tambah kalimat bahwa `K5-gameplay.md` ditulis sebagai resep lengkap dari bukti F9 dan **TERVALIDASI — production grade n=1 — di F10** (klaim diputus user 22:56 WIB, F10.9c; versi MINOR v0.7.0).
7. **§6 tabel pipeline, baris S5:** tambah "(K5: blurpad default, stack bila facecam adalah hook — `K5-gameplay.md` §7)" di samping "(K3: `moments.json`)".
8. **`references/naskah-hook.md` §7, baris K5 baru:** `**K5 (gameplay):** hook = aksi/kejutan visual di frame pertama + reaksi streamer; premis (game apa, apa taruhannya, apa yang belum diketahui) terbaca dari gambar ≤10 dtk; tanpa kartu judul, tanpa teks penjelasan — bila aksi tidak terbaca tanpa teks, potong ke momen yang lebih terbaca atau punch-in, jangan menambal dengan kartu.`
9. **`changelog.md` — entri baru:** `v0.5.2-F8+K5 (23 Nov 2026): K5-gameplay.md ditulis sebagai resep lengkap dari bukti F9 (VOD 45r3OyaxvFE, internal test only) — definisi & batas K3/K4/K5, sinyal pencarian momen tanpa transkrip penuh (chat-replay, ambang relatif token, heuristik mati bila baseline <0,02), rubrik momen K5, hook visual, KEPUTUSAN layout default blurpad (stack bila facecam adalah hook), audio game + risiko Content ID, caption umumnya tanpa kartu, QC khusus K5, kriteria validasi F10 (V1–V6 + P-pengukuran), daftar [T] K5-T1…K5-T14. BELUM tervalidasi; tanpa perubahan kode; SKILL.md belum diubah (fold spec di K5 §16).` — **catatan status saat ditulis (23 Nov); status kini ada di §17 ("TERVALIDASI — production grade n=1", klaim diputus user 22:56 WIB, F10.9c, versi MINOR v0.7.0) — jangan baca entri ini sebagai status kini.**
10. **`THIRD_PARTY_LICENSES.md`:** TIDAK ADA baris baru — OBS Studio sudah baris 04 (GPL-2.0), DeepFilterNet sudah baris 13 (MIT/Apache-2.0 dual); tidak ada sumber baru berlisensi jelas yang dipakai K5.
11. **Daftar [T]:** masukkan K5-T1 s/d K5-T14 (§16) ke daftar [T] yang dikelola koordinator.
