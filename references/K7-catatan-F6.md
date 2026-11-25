# K7 — Catatan F6 — ARSIP (sudah dilipat, jangan dipakai sebagai resep)

**ARSIP — 23 Nov 2026:** kesembilan butir patch F6 di bawah ini **sudah dilipat seluruhnya** ke `K7-footage-brand.md` (resep lengkap, BELUM tervalidasi — validasi F4). File ini dipertahankan sebagai arsip patch saja. **Jangan dipakai sebagai resep; resep yang berlaku adalah `K7-footage-brand.md`.** Verifikasi pelipatan: tiap butir terwakili di resep penuh (butir 1→S0, 2→S1, 3→S2, 4→S4, 5→S7, 6→S11, 7→QC khusus, 8→S4, 9→Definisi + S1-UGC; T2 kini TERJAWAB — UGC masuk K7).
**Asal:** analisis F6-D, 2026-11-22 (laporan lengkap: `f2-run/LAPORAN_F6_K7.md`).
**Status lama (beku):** USULAN, belum dilipat ke `K7-footage-brand.md` — status ini sudah tidak berlaku sejak pelipatan 23 Nov 2026. Setiap butir bertanda **[D]** (berdasar bukti produksi/riset), **[A]** (asumsi beralasan, wajib divalidasi F4), atau **[T]** (belum jelas polanya — TIDAK ditulis instruksinya, lihat daftar [T] di laporan).

**Bahan dasar yang dipakai (nyata, bukan karangan):** brief PDF Teh Pucuk "Angle Konten" (8 angle + kunci rasa, Always On; dibuka langsung dari tautan materi campaign, 2026-11-22); transkripsi brief Klik Film 5 Film (`files/brief-klik-film-5-film.md`); S&K konten.com (`riset-konten-com.md` §2). Perhatian: PDF Teh Pucuk mencantumkan larangan menjadikan isi brief sebagai konten — isinya dipakai sebagai bukti analisis saja, bukan sebagai konten klip.

---

## Butir 1 — S0: brief K7 dibaca dari DUA sumber, bukan PDF saja [D]

**Teks instruksi yang diusulkan:**

> S0 K7 memakai dua sumber, karena satu-satunya brief K7 nyata (Teh Pucuk) membuktikan PDF tidak memuat spesifikasi terukur:
> 1. **Halaman campaign konten.com** (perlu login; user yang membuka) → spesifikasi terukur: durasi klip (min–maks), hashtag wajib, tag akun, CTA + tempatnya (caption/video/keduanya), minimum views, platform, tautan materi/footage (mis. folder Drive), larangan khusus campaign.
> 2. **Brief PDF** (bila ada) → arah kreatif: angle konten (Teh Pucuk: 8 angle), kunci pesan rasa dari brief, elemen wajib, klaim terlarang, larangan (reupload utuh/AI).
> Bila salah satu sumber tidak ada isinya, catat eksplisit di `brief.json` ("tidak disebut di PDF" / "tidak ada di halaman campaign") — JANGAN isi dengan tebakan. Bila durasi tidak disebut di kedua sumber (seperti brief Klik Film yang durasinya kosong), durasi diputuskan user di G-BRIEF dan dicatat sebagai keputusan, bukan sebagai isi brief.

**Field `brief.json` yang diusulkan (tambahan pada `brief.schema.json`, di bawah kunci `k7`):**

```json
"k7": {
  "angle": {"chosen": "02 Skeptik rasa (reversal)", "options": ["01 Kaget: ada Less Sugar", "02 Skeptik rasa (reversal)", "..."]},
  "kunci_pesan": "<frasa kunci pesan dari brief>",
  "elemen_wajib": ["logo Teh Pucuk terlihat", "produk (botol Less Sugar) terlihat"],
  "klaim_terlarang": ["<salin verbatim dari brief; kosong bila brief tidak menyebut>"],
  "sumber_footage": ["<URL folder Drive / tautan materi dari halaman campaign>"]
}
```

**Sumber:** PDF Teh Pucuk (dibuka langsung: hanya angle + kunci, nol field terukur) [D] · `files/brief-klik-film-5-film.md` (spesifikasi terukur tinggal di halaman campaign; durasi kosong di sana) [D] · `brief.schema.json` (tidak ada field angle/elemen wajib/klaim terlarang) [D].

---

## Butir 2 — S1: standar bukti izin footage [D, pola dari S1 + schema yang ada]

**Teks instruksi yang diusulkan:**

> Setiap berkas sumber K7 dicatat di `sources.json` dengan empat field: `url_asal` (tautan unduhan persis dari halaman campaign/brief), `tanggal_akses` (ISO), `campaign` (nama campaign), `dasar_izin` (satu dari: "materi campaign" / "repurpose talent yang disediakan brief" / "rekaman sendiri" / "lisensi terbuka <nama + URL>"). Gate S1 (SKILL.md §6: "asal = materi campaign / diizinkan brief") FAIL bila satu field kosong. Footage talent yang disebut brief tanpa tautan (contoh Teh Pucuk angle 07: Aldi Taher, The Dudas) TIDAK boleh diunduh dari kanal pihak ketiga (YouTube re-upload, TikTok clipper lain) — tunggu tautan resmi dari halaman campaign; bila tidak ada, laporkan sebagai blokir S1, jangan ganti sumber diam-diam.

**Sumber:** SKILL.md §6 S1 + `brief.schema.json` `footage.allowed_sources[]` [D] · riset konten.com: "jangan pakai klip clipper lain sebagai sumber; pakai materi dari brief/channel resmi" (`riset-konten-com.md` §4.2, §6) [D] · PDF Teh Pucuk angle 07 menyebut talent tanpa tautan [D].

---

## Butir 3 — S2: penandaan manual produk/logo + G-CROP per shot berproduk [D, pola dari K1 S2 + lock §3.10]

**Teks instruksi yang diusulkan:**

> S2 K7: deteksi scene ffmpeg (ambang mengikuti K1, `gt(scene,0.3)`, sampai ambang K7 terkalibrasi di F4 — [T]) → `shots.json` + contact sheet 1 fps (seperti K1 S2). Tambahan K7: tiap shot ditandai manual `produk: true/false` dan `logo: true/false` di `shots.json`, berdasarkan contact sheet — agen yang menandai, bukan alat (tidak ada deteksi produk/logo otomatis di skill). G-CROP (lock §3.10): tiap shot dengan `produk: true` dicek visual di frame lebar penuh SEBELUM render — produk tidak boleh terpotong, tidak boleh tertutup kartu/teks, dan harus terbaca sebagai produk itu (bukan blur/warna saja). Shot yang produknya terpotong di crop 9:16 → ubah mode reframe (`cover`/`blurpad`) atau pilih shot lain; jangan memaksa `crop`.

**Sumber:** K1-trailer.md S2 + S5 (scene detect 0,3 [T]; Haar salah 3/12 → verifikasi visual, lock §3.10) [D] · `qc_all.py` (tidak ada cek produk/logo — jadi penandaan manual adalah satu-satunya cara saat ini) [D] · `render.py` (mode `crop`/`cover`/`fit`/`blurpad` sudah ada) [D].

---

## Butir 4 — S4: struktur beat K7 [A — diturunkan dari brief nyata, wajib divalidasi F4]

**Teks instruksi yang diusulkan:**

> Beat map K7 (satu klip, satu angle):
>
> | Beat | Isi | Aturan |
> |---|---|---|
> | Hook | momen/pertanyaan dari angle yang dipilih (mis. angle yang membuka dengan anggapan negatif soal rasa → reversal) | ≤20% durasi (lock; `brief_audit` hook); hook = pertanyaan/momen, bukan kartu judul (lock §3.6) |
> | Bukti rasa/produk | adegan yang membuktikan kunci pesan brief (dari brief: bukti rasa produk) + produk/logo terlihat | kembali ke kunci pesan brief, apa pun angle-nya |
> | Penutup | CTA sesuai brief (teks + tempat: caption/video/keduanya) | CTA di video terbaca ≥1,5–2 dtk (lock §3.7); CTA di caption masuk `caption_tiktok.txt` |
>
> Angle dipilih SATU per klip, diputuskan di G-STORY (agen mengusulkan dari daftar angle brief, user menyetujui). Satu klip jangan mencampur dua angle. Batas beat dicatat untuk `--cuts` (lock §3.17: batas beat, bukan tiap ganti shot).

**Sumber:** PDF Teh Pucuk (8 angle + kunci pesan rasa dari brief) [D] · SKILL.md §3.6/§3.7/§3.17 + `brief_audit.py` cek `hook` [D] · K1-trailer.md beat map (pola tabelnya dipinjam; isinya K7) [D]. **Status [A]:** struktur ini belum pernah diuji pada klip K7 nyata — F4 membuktikan atau merevisi.

---

## Butir 5 — S7: routing caption menurut jenis audio K7 [D, pinjaman K1 + K3]

**Teks instruksi yang diusulkan:**

> Pilih jalur caption K7 dari jenis audionya — jangan satu jalur untuk semua:
> 1. **UGC rekam-sendiri / ucapan alami 1 pembicara, audio relatif bersih** → ikuti K3-panjang.md §7: grup per frasa-napas; `timing: prop` hanya untuk grup pendek (±1–3 kartu) dengan `audio` + `src_in` + `dur` + `offset` (noise −50 dB, `hold` per grup default 0); bila musik/latar ramai atau hasil `prop` meleset saat didengar → jalur manual.
> 2. **Dialog/talent di atas musik** (footage repurpose, TVC) → K1 S7 jalur manual (default dialog, lock §3.4): `pause_anchor.py --list-pauses` hanya kandidat jeda; dengar/lihat waveform, tulis `cards.json` eksplisit (teks verbatim 2–7 kata, celah 0,04); G-HUMAN putar ulang bagian dialog.
> 3. **VO bersih (narasi TTS/rekaman studio, bila brief mengizinkan)** → `timing: prop` (lock §3.4; kalibrasi K2 berlaku).
> Dilarang untuk semua jalur: teks kartu dari transkripsi bebas whisper; timestamp kata whisper mentah; `island`/`words` tanpa koreksi manual + G-HUMAN (lock §3.4–3.5, §9). Metode timing tiap grup dicatat di `production-log.md` (pola K3 §7 butir 4).

**Sumber:** SKILL.md §3.4/§3.5/§9 (lock) [D] · K1-trailer.md S7 (manual dialog; lembah RMS palsu di atas musik) [D] · K3-panjang.md §7 (aturan ucapan alami — statusnya [T], jadi routing ini pun ikut [T] sampai F4) [D] · K2-statis.md (noise −50 dB hanya terkalibrasi pada VO TTS bersih) [D].

---

## Butir 6 — S11: CTA/hashtag/tag — sumber data + CTA-di-video [D, pola dari brief_audit.py]

**Teks instruksi yang diusulkan:**

> Hashtag wajib, tag akun, dan CTA diambil dari **halaman campaign** di S0 (butir 1) — bukan dari PDF (PDF Teh Pucuk tidak memuat ketiganya). `brief_audit.py` memeriksa ketiganya di `caption_tiktok.txt` secara otomatis (cek `hashtag`, `tag`, `cta`) — berlaku bila `cta.where` = caption/keduanya. Bila `cta.where` = video (CTA tampil di dalam klip), cek otomatis TIDAK berlaku — wajib ada `manual_items` dengan bukti: timestamp kemunculan CTA di final + kutipan teks CTA yang terlihat di frame. Bila brief tidak menyebut CTA sama sekali, catat "tidak ada CTA di brief" sebagai `manual_items` (bukan diisi karangan).

**Sumber:** `brief_audit.py` `auto_checks` (hashtag/tag/cta hanya diperiksa di caption; `where="video"` tidak ditangani) [D] · PDF Teh Pucuk (tanpa hashtag/CTA/tag) [D] · `files/brief-klik-film-5-film.md` (hashtag wajib campaign ada di halaman campaign) [D].

---

## Butir 7 — S11: templat `manual_items` K7 untuk kelima butir QC [A] [D, pola dari brief_audit.py + K1/K2]

**Teks instruksi yang diusulkan:**

> Kelima butir QC khusus K7 (K7-footage-brand.md baris 21) ditulis sebagai `manual_items` di `brief.json`, masing-masing dengan standar bukti — tanpa ini kelimanya tidak bisa PASS/FAIL:
>
> | ID | Syarat | Bukti yang diterima (`evidence`) |
> |---|---|---|
> | K7-PRODUK | Produk/logo terlihat sesuai brief (elemen wajib butir 1) | Timestamp + nomor shot di final tempat produk/logo terlihat; bila brief menyebut durasi minimum, sebutkan durasinya |
> | K7-KLAIM | Tidak ada klaim terlarang (daftar klaim butir 1; kosong = "brief tidak menyebut klaim terlarang") | Kutipan teks kartu/naskah yang diperiksa + pernyataan "diperiksa terhadap daftar klaim" |
> | K7-CTA | CTA/hashtag/tag sesuai brief | Hasil cek otomatis `brief_audit` (caption) + bukti frame untuk CTA-di-video (butir 6) |
> | K7-REUPLOAD | Bukan reupload utuh — ada nilai tambah edit | Bukti pencatatan butir 8 (durasi sumber dipakai, jumlah potong, elemen tambah) |
> | K7-IZIN | Footage tidak di luar izin | `sources.json` lengkap per butir 2 (URL + tanggal + dasar izin) |
>
> Butir tanpa `auto` hanya dinilai manual; PENDING bila `evidence` kosong (`brief_audit.py`: bukti kosong = FAIL). N/A wajib `reason` + `waiver_by` (aturan `brief_audit.py` yang sama).

**Sumber:** K7-footage-brand.md baris 21 (lima butir [A]) [D] · `brief_audit.py` (mekanisme manual_items + aturan bukti/N/A) [D] · `brief.schema.json` (`manual_items[].auto` — kelima butir ini belum punya `auto` yang setara, jadi manual) [D].

---

## Butir 8 — S4: pencatatan bukti nilai-tambah edit, TANPA ambang [D pencatatan; ambang = T]

**Teks instruksi yang diusulkan:**

> Sampai ada ambang terkalibrasi (lihat [T4] di laporan), "bukan reupload utuh" dibuktikan dengan pencatatan, bukan angka: di `edl.json` + `manual_items` K7-REUPLOAD (butir 7), catat (a) total durasi sumber yang dipakai di klip, (b) jumlah potong/cut, (c) daftar elemen tambah yang benar-benar ada di final: hook, caption, CTA, musik (dengan sumber lisensi bila ada), reframe 9:16, potongan/penyusunan ulang urutan. JANGAN menulis ambang (mis. "≥30% dipotong" atau "≥3 elemen tambah = lolos") — tidak ada bukti yang mendukung angka mana pun. Keputusan "cukup nilai tambah" untuk F4 diambil user di G-HUMAN per klip, dengan catatan ini sebagai bahan.

**Sumber:** K7-footage-brand.md baris 15 ("nilai tambah edit (bukan reupload utuh)" — tanpa ukuran) [D] · `brief.schema.json` `prohibitions.reupload` (boolean saja) [D] · S&K konten.com (`riset-konten-com.md` §2: larangan "re-upload konten yang substansial identik" — tanpa angka) [D].

---

## Butir 9 — Koreksi + kesenjangan struktural: UGC rekam-sendiri [D koreksi; resep cabang = T]

**Koreksi yang diusulkan (untuk riset + K7-footage-brand.md saat dilipat):**

> Koreksi: `riset-referensi-kasus.md` §2.2 menyebut brief PDF Teh Pucuk "satu-satunya brief lengkap yang berhasil dibuka". Yang benar: PDF itu lengkap sebagai **lembar angle** (8 angle + kunci pesan), tetapi **bukan spesifikasi terukur** — durasi, hashtag, tag, CTA, klaim terlarang, dan tautan materi tidak ada di PDF (dibuktikan dengan membuka PDF langsung, 2026-11-22). Spesifikasi terukur campaign K7 ada di halaman campaign (perlu login). Definisi K7 "brief (sering PDF lengkap…)" (K7-footage-brand.md baris 7) harus diubah menjadi "brief PDF (sering hanya lembar angle) + halaman campaign (spesifikasi terukur)".

**Kesenjangan struktural yang dicatat (bukan resep jadi):**

> Campaign Teh Pucuk adalah UGC: bentuk kerja utamanya clipper **merekam sendiri dengan produk** (riset §2.2), dan hanya sebagian angle yang memakai repurpose footage talent. Pipeline K7 saat ini hanya punya S1 "unduh footage" — tidak ada cabang rekam-sendiri. Sketsa cabang yang masih [T] (butuh keputusan user/Opus, butir T2 laporan): S1-UGC = rekam dengan kamera sendiri (produk terlihat, pencahayaan cukup, audio sendiri direkam bersih); S2 = inventaris take sendiri; S3 = transkrip ucapan sendiri; S7 = routing butir 5 jalur 1. Jangan tulis resep S1-UGC lengkap sebelum diputuskan apakah UGC rekam-sendiri masuk K7 atau jadi kasus baru.

**Sumber:** PDF Teh Pucuk (isi aktual) [D] · `riset-referensi-kasus.md` §2.2 (bentuk kerja UGC + klaim "brief lengkap" yang dikoreksi) [D] · K7-footage-brand.md baris 7, 13 [D].

---

## Yang SENGAJA tidak ada di file ini (daftar [T] — lihat laporan §5)

- Daftar sumber musik royalty-free + cara catat lisensi (T3) — **TERJAWAB 23 Nov 2026** (lipatan musik tier 1–2): `references/musik-sfx.md` §2 + §7, SKILL.md lock #39 + #43; jawaban kanonik di tabel [T] `K7-footage-brand.md`.
- Ambang nilai-tambah reupload (T4).
- Deteksi otomatis produk/logo, ambang scene-detect K7, durasi minimum produk terlihat (T5).
- Kalibrasi caption pada audio UGC berisik (T6).
- Cek otomatis `brief_audit.py` untuk CTA-di-video, klaim terlarang, elemen wajib (T7).
- Durasi klip K7 + pemilihan angle (T8); sumber footage talent angle 07 (T9).
