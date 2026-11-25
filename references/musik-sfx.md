# Musik Latar + Sound FX — DRAF resep clipper-ultimate

**Status: TIER 1–2 DILIPAT ke SKILL.md 23 Nov 2026** (lock #38–#44; dilipat saat v0.5.0-F6, kini v0.6.0). Ditulis 23 Nov 2026 dari riset sumber gratis/bebas hak cipta (laporan: `f2-run/LAPORAN_MUSIK_SFX.md`). Tier 3 (TikTok CML) + resep SFX sintetis + pustaka lokal Sonniss **DITUNDA** (lihat §10).
**Tanda:** **[D]** terverifikasi · **[T]** butuh tes/keputusan · **[A]** asumsi.
**Aturan yang menang bila bertentangan:** lock loudness skill (−18 LUFS / TP −3,5) mengalahkan angka dari skill lain (−14 di `video-sound`, −16 di skill open source). Lisensi dibaca per aset pada hari unduh — lisensi bisa berubah.

## 1. Tangga pilihan (pilih dari atas; jangan lompat ke bawah tanpa alasan tercatat)

| Tier | Pilihan | Kapan dipakai |
|---|---|---|
| 1 | **Bed sintetis ffmpeg** (selalu aman) | Default. Tidak ada musik yang cocok, waktu mepet, atau ragu soal lisensi. Resep yang sudah terbukti: `anoisesrc brown d=60 → lowpass 300 Hz, volume 0.2` [D F2 K2, C14]. |
| 2 | **Pustaka gratis terverifikasi** (§2) | Perlu musik/SFX nyata (mood, energi, aksen). Pilih dari tabel §2 saja — sumber di luar tabel = BELUM TERVERIFIKASI, jangan dipakai. **Tier 2 belum tervalidasi produksi** — lisensi tiap sumber sudah dibaca [D], tapi belum ada trek tier 2 yang dipakai di produksi nyata + G-HUMAN (uji dengar pertama = T-M2, masih [T]). |
| 3 | **Musik TikTok sendiri (CML, in-app)** | Hanya bila klip diedit/diposting lewat aplikasi TikTok. Bukan untuk edit eksternal (tidak bisa diunduh untuk Remotion/ffmpeg). Lisensi CML hanya untuk penayangan TikTok. |

**Catatan akun [T]:** jenis akun TikTok yang dipakai (Personal vs Business) belum dicatat di skill. Bila Business, pemilih musik in-app terkunci ke CML; musik berlisensi eksternal di dalam berkas video yang diunggah tetap boleh, dengan Music Usage Confirmation saat upload. Cek jenis akun sebelum mengandalkan tier 3.

## 2. Sumber terverifikasi (musik + SFX)

**Cara baca:** "Komersial" = boleh untuk klip konten.com (konten promosi/brand, dimonetisasi). "Atribusi" = kredit wajib, dan di mana diletakkan. "TikTok" = aman dipakai di klip TikTok (bukan hanya YouTube).

### 2a. Musik — tanpa atribusi (pilihan utama untuk TikTok)

| Sumber | Lisensi | Atribusi | Komersial | TikTok | Catatan |
|---|---|---|---|---|---|
| **Pixabay Music** (pixabay.com/music) | Pixabay Content License [D] | Tidak | Ya | Ya | 290.000+ trek. Dilarang jual/distribusi standalone; jangan pakai konten bermerek dagang. Sebagian trek terdaftar di Content ID — simpan URL + nama berkas + sertifikat lisensi Pixabay bila ada (perisai di situs). Konten pra-9 Jan 2019 = CC0. Unduh manual, catat URL. |
| **Mixkit Music** (mixkit.co) | Stock Music Free License [D, dibaca langsung 23 Nov 2026] | Tidak | Ya | Ya | 1.000+ trek. Boleh: web/sosmed, VOD, podcast, iklan. Dilarang: CD/DVD, TV/radio, video game, remix jadi trek musik saja, klaim sebagai milik sendiri, daftarkan ke rights-management service. Bila ada klaim: teruskan ke team@mixkit.co. **Dilarang unduh massal pakai bot/scraper** — unduh manual. |

### 2b. Musik — dengan atribusi (hanya bila kredit muat di caption)

| Sumber | Lisensi | Atribusi | Komersial | TikTok | Catatan |
|---|---|---|---|---|---|
| **Incompetech / Kevin MacLeod** (incompetech.com) | CC-BY 4.0 seragam [D] | Ya — format 4 baris: judul; Kevin MacLeod (incompetech.com); Licensed under Creative Commons: By Attribution 4.0; https://creativecommons.org/licenses/by/4.0/ | Ya | Ya | ~2.000 trek, tanpa akun. Kredit di deskripsi/caption (bukan hanya di dalam video). Lisensi berbayar Standard ($30/trek) menghapus kewajiban kredit. Trek FreePD = CC0. |
| **Uppbeat (free)** (uppbeat.io) | Lisensi free tier [D] | Ya — "Uppbeat Credit" per video, 1 video saja | Ya, kanal sendiri | Ya | 3 unduhan saat daftar + 1/bulan; ~25% katalog. Solo creator di kanal sendiri saja — TIDAK untuk client work / paid ads (butuh Pro/Business). Klaim: alat Claim Release (free: 5/bulan). |
| **Bensound (free)** (bensound.com) | Free License with Attribution [D] | Ya — teks atribusi per video, 1 teks = 1 video, tidak boleh dipakai ulang | Ya, video online gratis saja | Ya | Free Music section saja. Paid ads TIDAK tercakup (butuh lisensi berbayar). Client work butuh lisensi per klien. |

### 2c. Musik — per trek (cek lisensi tiap trek; jangan asumsi situs)

| Sumber | Lisensi | Atribusi | Komersial | TikTok | Catatan |
|---|---|---|---|---|---|
| **Free Music Archive** (freemusicarchive.org) | CC per trek [D] | Sesuai label trek | Hanya trek tanpa NC | Ya, bila label mengizinkan | CC-BY: boleh komersial + kredit (judul, artis, sumber, lisensi). CC-BY-SA: video ikut berlisensi sama — hindari untuk klip klien. CC-BY-ND: tidak boleh masuk video (video = karya turunan). CC-BY-NC: TIDAK boleh komersial. FMA-Limited: tidak boleh untuk video. FMA bukan pemberi lisensi — artisnya yang memberi. |
| **YouTube Audio Library** | Lisensi YT Audio Library / CC per trek [D] | Trek CC saja | Ya (YouTube) | **TIDAK direkomendasikan** | Jaminan Content ID hanya untuk YouTube. Ketentuan tidak eksplisit melarang luar-YouTube, tapi tidak ada janji apa pun untuk TikTok. Untuk klip TikTok-first, pilih §2a dulu. Perlu akun YouTube (YouTube Studio) untuk unduh. |

### 2d. Sound FX — tanpa atribusi (pilihan utama)

| Sumber | Lisensi | Atribusi | Komersial | TikTok | Catatan |
|---|---|---|---|---|---|
| **Pixabay SFX** (pixabay.com/sound-effects) | Pixabay Content License [D] | Tidak | Ya | Ya | 130.000+ efek. Aturan sama dengan musik Pixabay (§2a). |
| **Mixkit SFX** (mixkit.co) | Sound Effects Free License — TERPISAH dari lisensi musik [D] | Tidak | Ya | Ya | 3.000+ efek, WAV. Boleh: video game, film, TV/radio, CD/DVD (lebih longgar dari musik Mixkit). Dilarang: redistribusi standalone / sebagai stok / di dalam tool/template. Jangan pindahkan izin SFX ke musik. |
| **Sonniss GDC Bundle** (gdc.sonniss.com) | Sonniss Royalty-Free License v2.0 (berlaku 27 Agu 2026) [D] | Tidak | Ya | Ya | Bundle tahunan gratis (2026: 7,47 GB, 347+ berkas WAV profesional). Proyek tanpa batas, seumur hidup. Dilarang: jual/berikan suara sebagai sound pack; latih AI. Unduhan besar (gigabyte) — ambil sekali, simpan sebagai pustaka lokal. |
| **Kenney Audio** (kenney.nl) | CC0 [D, via LICENSES.md skill Barty-Bart + katalog] | Tidak | Ya | Ya | Paket jingle + SFX CC0. Konfirmasi di halaman paket sebelum pakai. |

### 2e. Sound FX — dengan atribusi (hanya bila kredit muat)

| Sumber | Lisensi | Atribusi | Komersial | TikTok | Catatan |
|---|---|---|---|---|---|
| **Zapsplat (free Basic)** (zapsplat.com) | Standard License [D, diperbarui 8 Mei 2026] | Ya — "Sound effects from zapsplat.com" di deskripsi/kredit | Ya | Ya | 130.000+ suara, MP3 di free tier, ada batas unduhan. Premium menghapus atribusi. Dilarang: bagikan/ jual / sublicense berkas mentah; suara tidak boleh jadi nilai utama proyek (mis. video yang hanya memutar satu suara). |
| **Freesound** (freesound.org) | CC per suara: CC0 / CC-BY / CC-BY-NC (+ legacy Sampling+) [D] | CC-BY: ya | CC0 + CC-BY saja | Ya, bila label mengizinkan | Filter ke CC0 bila tidak mau kredit. CC-BY-NC = TIDAK BOLEH komersial. Sampling+ = perlakukan seperti NC. Waspada: suara mentah bisa didaftarkan pihak lain ke Content ID — simpan URL + lisensi per suara. |

### 2f. Jalur ambil otomatis (opsional, bila perlu banyak aset)

- **Openverse API** (`api.openverse.org`, tanpa API key) — 5,2 juta audio gratis. Filter lisensi WAJIB: `license=cc0,by,pdm` + `source=freesound,jamendo`. Tulis `credits.txt` dari field `attribution` tiap berkas (wajib untuk CC-BY). Metode ini dari skill `openverse-sfx` (MIT, lihat §9).
- **Aturan unduh:** unduh manual per aset (tangan), bukan scraping massal — banyak situs melarang bot/scraper di ketentuannya (Mixkit eksplisit). Agen mencatat provenance; manusia mengunduh.

## 3. Sumber yang TIDAK boleh dipakai untuk klip

| Sumber | Alasan |
|---|---|
| **BBC Sound Effects** | Lisensi RemArc: personal/educational/research SAJA — TIDAK komersial. Arsip 33.000 rekaman yang menggoda, tapi bukan sumber komersial. |
| **Lagu komersial / trending TikTok** (di luar CML) | Berhak cipta; lisensi pustaka umum TikTok hanya untuk konten personal, bukan promosi/brand. |
| **YouTube Audio Library untuk klip TikTok-first** | Jaminan hanya YouTube (§2c). Bukan larangan mutlak, tapi jangan jadikan andalan. |
| **Freesound / FMA berlabel NC, SA (untuk klien), ND, Sampling+, FMA-Limited** | NC = tidak komersial; SA = video ikut berlisensi sama; ND = tidak boleh masuk video; FMA-Limited = bukan untuk video. |
| **Sumber apa pun berlabel BELUM TERVERIFIKASI** | Lisensi tidak bisa diverifikasi = jangan dipakai, jangan direkomendasikan. |

## 4. Aturan memilih musik (per kasus)

- **K1 (trailer):** musik datang bersama trailer — JANGAN tambah musik di atas dialog trailer (sudah terbukti gagal: `island`/`words` Δ besar di atas musik). Bila trailer bisu/tanpa musik, bed tier 1 saja.
- **K2 (statis + VO):** bed di bawah VO, ducking sidechain (lock §3.1). Pilih mood sesuai beat (muram = dingin, tegang = ritme lambat-berat, hangat = terang) — jangan pakai trek ceria untuk adegan sedih. Tanpa vokal yang bersaing dengan VO. Durasi trek ≥ durasi klip (loop bila perlu, potong di zero-crossing).
- **K3 (pembicara tunggal):** audio sumber adalah konten — musik tambahan hanya bila brief mengizinkan. Bila diizinkan: bed sangat pelan, hanya di jeda antar highlight.
- **K4 (dialog):** seperti K1 — jangan tambah musik di atas dialog.
- **K7 (brand/UGC):** musik dari footage asli, atau bed tier 1/2. Musik tambahan tanpa sumber = dilarang (K7 [T] T3 lama, kini terjawab §2).
- **Umum:** satu trek per klip (jangan gonta-ganti mood). Tempo tidak mengalahkan VO. Bila ragu antara dua trek, pilih yang lebih sederhana.

## 5. Aturan SFX (per kasus)

Taksonomi (dipinjam dari skill `video-sound`, disesuaikan ke clipper):

| Pemicu | SFX | Aturan clipper |
|---|---|---|
| Ganti panel / xfade (K2) | Whoosh udara cepat | 1 per transisi panel (maks 2 per klip). |
| Kartu akhir / CTA muncul (K2, K7) | Pop lembut / ding | 1 per klip, di kartu akhir saja — JANGAN per kartu (24 kartu = 24 pop = berisik). |
| Klimaks / twist (K1) | Sub-bass drop / impact sinematik | 1–2 per klip, hanya bila trailer belum punya. |
| Reveal angka/fakta (K3, K6) | Typewriter / cash register | Sinkron dengan angka di kartu. |
| Pertanyaan / misteri | Tension riser / reverse cymbal | Sebelum reveal jawaban. |

**Metode cue (dipinjam dari skill `sound-effects` Barty-Bart, MIT — diadaptasi):**
1. Buat daftar cue dari potongan/beat (transisi, reveal, CTA), bukan dari perasaan.
2. Satu SFX nyata per cue, dari pustaka §2d/§2e — jangan sintesis bunyi di kode bila ada rekaman nyata (aturan `openverse-sfx`).
3. Ratakan puncak one-shot SFX di bawah VO; cek pada berkas final yang diekspor (bukan hanya di timeline).
4. Bila tidak ada SFX yang pas di pustaka, lebih baik sunyi daripada SFX yang salah.

**SFX sintetis (cadangan tier 1) [T]:** whoosh = noise + bandpass sweep; pop = burst sinus pendek. Belum diuji di skill — resep ffmpeg-nya [T], jangan jadikan default sebelum ada uji dengar + ukur.

## 6. Mixing (angka yang berlaku)

- **Loudness lock skill: −18 LUFS / TP −3,5** — angka −14 LUFS (`video-sound`) dan −16 LUFS (skill open source) TIDAK dipakai.
- **Ducking (sudah terbukti di K2):** sidechain threshold 0,025, ratio 6, attack 80, release 400, makeup 1; musik `gain_db` −6,02 di `project.json`; `afade` out 1 dtk di akhir. Musik harus turun di bawah VO, naik di jeda napas.
- **SFX:** one-shot di bawah puncak VO; jangan pernah lebih keras dari VO. Cek akhir: `loudnorm` + dengar ulang bagian SFX (G-HUMAN).
- **Mastering:** `loudnorm I=-18, TP=-3.5, LRA=11` (target skill); tanpa digital silence (kecuali pengecualian terdeklarasi).

## 7. Audit & pencatatan (bukti lisensi)

- Tiap aset musik/SFX dicatat di `production.json` seperti C14 (K2): blok `musik` + blok baru `sfx` — per aset: `sumber`, `url`, `lisensi`, `atribusi` (teks persis + di mana diletakkan: caption/production.json), `sha256`, `format`, `durasi_dtk`.
- `brief_audit`: butir C14 (musik) tetap; butir audit SFX = **C21** (diputuskan saat lipat 23 Nov 2026; C01–C20 sudah terpakai, C21 bebas): tiap SFX punya sumber + lisensi tercatat. **C21 ditegakkan otomatis di `brief_audit.py` (F8.5-d):** tidak ada blok sfx → N/A beralasan otomatis; SFX tanpa sumber/lisensi/sha256 → FAIL; SFX lengkap → PASS.
- Simpan bukti lisensi: URL halaman lisensi + tanggal baca + (bila ada) sertifikat lisensi / teks atribusi yang dipakai. Untuk Pixabay: simpan URL trek + nama berkas (sertifikat bila trek ber-perisai Content ID). Untuk Mixkit: simpan URL trek. Untuk CC-BY: simpan judul, artis, sumber, lisensi.
- Atribusi yang wajib: tulis di `caption_tiktok.txt` (bila muat) dan SELALU di `production.json`. Kredit yang hanya ada di dalam video tidak cukup untuk lisensi yang menuntut kredit deskripsi (contoh: Incompetech — klaim bisa muncul bila kredit hanya di video).

## 8. Larangan

- Jangan pakai lagu komersial / trending di luar CML untuk klip promosi.
- Jangan pakai sumber BELUM TERVERIFIKASI.
- Jangan klaim "bebas royalti" / "bebas hak cipta" tanpa bukti lisensi di `production.json`.
- Jangan redistribusi berkas mentah (standalone) — musik/SFX hanya di dalam klip jadi.
- Jangan daftarkan trek/SFX ke Content ID atau rights-management service.
- Jangan scraping massal / bot untuk unduh (khususnya Mixkit — dilarang di ketentuan).
- Jangan impor angka loudness skill lain (−14/−16 LUFS) — lock skill −18 LUFS yang berlaku.
- Jangan tambah musik di atas dialog trailer (K1/K4) — sudah terbukti gagal.

## 9. Sumber & lisensi (untuk pelipatan)

- **Skill `video-sound`** (GrowKaz, terpasang di `~/workspace/custom-skills/video-sound/`) — teknik saja (taksonomi SFX, ducking, stem mixer). Tidak menyebut sumber musik/SFX apa pun. Angka −14 LUFS-nya TIDAK dilipat.
- **Barty-Bart/motion-graphics — skill `sound-effects`** (github.com/Barty-Bart/motion-graphics) — MIT (LICENSE file; GitHub NOASSERTION). Metode cue + beat grid (librosa) + mix terukur + pustaka CC0 (Kenney + Freesound, `LICENSES.md`) + Mixkit runtime. Bisa dilipat dengan atribusi; angka −16 LUFS-nya diadaptasi ke −18.
- **Varnan-Tech/opendirectory — skill `openverse-sfx`** (github.com/Varnan-Tech/opendirectory) — MIT. Metode: Openverse API + filter lisensi wajib + `credits.txt` + ukur (bukan rasa). Bisa dilipat dengan atribusi.
- **Naveen-S6/EditorThambi — skill `fetch-assets`** — lisensi repo TIDAK ditemukan → distilasi kata sendiri saja, jangan salin. Sumber pilihannya (Pixabay, Mixkit, Freesound CC0/CC-BY) sudah terverifikasi independen di §2.
- **nsudy-code/cappus** — MIT. Editor CapCut; musik/SFX-nya digenerate programatik (music.py/sfx.py) — dicatat sebagai metode (audio generate = tanpa masalah hak cipta), bukan dilipat (tergantung CapCut).
- **Pustaka §2** — lisensi masing-masing dibaca Nov 2026 (lihat laporan). Cek ulang pada hari unduh.

## 10. [T] terbuka

- T-M1: Jenis akun TikTok yang dipakai (Personal vs Business) — menentukan tier 3.
- T-M2: Uji dengar pertama: satu bed Pixabay + satu bed Mixkit di klip K2 berikutnya; nilai mood + klaim.
- T-M3: Resep SFX sintetis ffmpeg (whoosh/pop) — uji dengar + ukur sebelum jadi default.
- T-M4: Butir audit SFX — **TERJAWAB saat lipat 23 Nov 2026: C21** (tiap SFX punya sumber + lisensi tercatat; SKILL.md lock #43).
- T-M5: Pustaka lokal SFX (Sonniss bundle 7,47 GB) — unduh sekali di VM atau tidak (ruang disk)?
