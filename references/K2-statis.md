# K2 — Klip dari materi statis (+VO)

Tanda: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi. Status resep: **disusun dari satu produksi nyata (GR-1); render ulang GR-1 LULUS G3 (ronde 2 dan 3: 900 frame, 30,00 dtk, QC 0 FAIL, ΔI 0,05, ΔTP 0,17); deteksi span otomatis `audio`+`offset` (noise −50, hold per grup) LULUS G2 (ronde 3, maks Δ 0,044). Belum dibuktikan dengan materi statis BARU (F2).**
Frekuensi di campaign nyata: **langka** — belum ada contoh campaign lain [D via riset]. **GR-1 = K2 (+K6)** — materi statis + VO; K3 belum punya contoh campaign nyata.

## Definisi
Gambar/postingan → klip 20–30 dtk yang "hidup" (zoom/pan, VO, musik, caption). **GR-1**: 30 dtk dari 2 JPEG + 1 postingan Instagram; 3 VO terpisah (GR-1 memakai Gemini TTS, izin user — riwayat; sejak F8 default narasi = Helio, lihat S3), musik disintesis, kartu pause-anchored, transisi fade; v1 diposting lalu dihapus (tanpa VO), v2 terbit dan disubmit (Pending) [D].

## Format & orientasi
| Orientasi | Ukuran | Status |
|---|---|---|
| Portrait (default) | 1080×1920, 30 fps | Jalur utama; production grade dengan batasnya (lihat header) |
| Landscape | 1920×1080, 30 fps | **Tervalidasi n=1 (F11, 25 Nov 2026)** — hanya materi statis dari **sumber landscape**; klaim: "Jalur landscape tervalidasi n=1: K2 materi statis dari sumber landscape, 1920×1080, 30 fps, 35 dtk, VO Helio, kartu drawtext" (BUKAN production grade) |

`orientasi` ditetapkan di `brief.json` pada G-BRIEF (S0); `size` di `project.json` harus cocok; QC landscape wajib `qc_all.py --project … --brief …` (gerbang format membaca `size` + `orientasi`). Ukuran sah hanya dua baris tabel di atas.

### Jalur landscape (F11) [D n=1]
- **Panel 16:9 dibangun ulang dari sumber landscape** — JANGAN memakai panel portrait di canvas landscape (still selalu cover → hanya ~32% tinggi panel portrait yang tampil). Bukti F11: 3 panel PNG 1920×1080 di-crop dari satu key art landscape (`banner_clean.png` 1920×914): P1 ayah+bayi (crop 1132,268,1920,711; upscale 2,44×), P2 Ka'bah+kerumunan (20,415,907,914; 2,16×), P3 poster komposisi penuh (100,0,1725,914; 1,18×). Asal + koordinat crop + faktor upscale + sha256 tiap panel WAJIB dicatat (pola `sources.json`).
- **Hati-hati zoom pada panel landscape:** zoom terkunci (mis. 1,00→1,04) memotong ~4% tiap sisi pada frame akhir — teks kunci poster harus punya margin dari tepi crop. Bukti F11: P3 draf pertama (x0=135) memotong huruf 'A' awal judul poster di frame akhir (gagal G4 saat render); dibangun ulang x0=100 → lulus. Periksa frame AKHIR panel, bukan hanya frame awal.
- **Gaya kartu landscape TERUKUR (F11, kandidat terpilih user):** size kartu **46**, size judul **54**, wrap **42**, y kartu = **h−240**, y judul = **h−260**. Kotak terlebar terukur 1135 px = 59,1% lebar canvas (batas: ≤70%); margin bawah minimum terukur 104 px (batas: ≥80 px); margin sisi judul ≈392 px (batas: ≥96 px); WARN lebar 0. Semua 18 kartu narasi satu baris; judul 2 baris eksplisit via `lines`.
- **Catatan lingkup gaya kartu (S3, Opus FINAL F11):** gaya 46/54 + wrap 42 di atas terukur pada **SATU key art** (materi Hamka F11); pada materi itu pun tepi kotak kartu menyentuh dagu figur (P1, catatan G3). **Cek pita per panel (lock #25) tetap WAJIB untuk tiap materi** — gaya ini **bukan jaminan lolos G3** untuk materi lain.
- **Sumber vertikal di canvas landscape = berhenti dan lapor** — belum divalidasi [T]. Sumber video landscape juga [T]. **[T] lain yang menyertai klaim:** durasi selain 35 dtk; suara non-Helio untuk landscape; K1/K3–K7 landscape; kartu ASS landscape; ukuran/fps selain 1920×1080/30; submission/posting landscape.
- Bukti F11: final 35,000 dtk sha `84ed4565…`; audio bit-identik dengan kontrol vertikal v6 (MD5 ter-decode sama); loudness identik (−18,08 / −3,37); brief_audit FINAL 19 PASS / 0 FAIL / 0 PENDING (N/A hanya C13 hashtag + baris AUTO-sfx); G-HUMAN iterasi 1. Laporan: `f2-run/f11/laporan-final-F11.md`.

## Input
Gambar resolusi asli (jangan screenshot) · teks postingan · narasi pilihan dari brief · larangan (AI? reupload?) · angka/teks di materi (→ K6).

## Pipeline
| Tahap | Aksi | Repo/alat | Env |
|---|---|---|---|
| S0 | `brief.json`; **cek larangan AI sebelum memilih TTS**; catat waiver user (tanggal + lingkup) bila ada | — | A |
| S1 | Unduh gambar/postingan · **Motion poster → frame diam terpilih** (celah b: ekstrak kandidat tiap 0,5 dtk, pilih frame teks penuh dan diam; catat t + perintah + sha256 ke `sources.json`), atau segmen `clip` bila brief mengizinkan (wilayah K7) | gdown, instagram-cli [D] | A |
| S2 | Inventaris teks & angka di gambar → `facts.json` (K6) · **klaim teks layar hanya sah dari frame resolusi penuh** (lock #20; contact sheet = orientasi) | agen membaca visual | A |
| S3 | Naskah VO — tulis mengikuti `references/naskah-hook.md` (lock #34–#37): kalimat pertama = nama/peran subjek + taruhan dari fakta terverifikasi; 3 varian pembuka, pilih terkuat; premis substansi ≤10 dtk (siapa + mau apa + penghalang); gambar diam → naskah memberi gerakan verbal (jangan narasi datar + gambar diam). → rekam user **atau** TTS (hanya bila diizinkan). **TTS narasi default = Helio** (Shortwave, `avocado_v2:MAI_03`, keputusan user 23 Nov 2026, lock #45): `/opt/hatch/bin/tts speak --language id --voice avocado_v2:MAI_03 --text-stdin --output vo/narasi.wav` (voice default-nya sudah `avocado_v2:MAI_03`, jadi `--voice` boleh dihilangkan). **Isi VO wajib diverifikasi via whisper** (`whisper.cpp small -l id` — semua kalimat hadir berurutan, kata benar). Suara lain hanya lewat aturan override lock #45 (alasan + tanggal + pace diukur ulang). **Ukur durasi + pace tiap take TTS; pilih take yang masuk jendela** (F7-29; lock #45). **Span ucapan** = `silencedetect` pada tiap WAV VO, **noise −50 dB** (+ offset di timeline) | ffmpeg [D] | A |
| S4 | `edl.json`: urutan panel, durasi (≥ waktu baca teks); segmen `still` + `zoom`/`focus` — **still selalu cover; untuk fit/blurpad, pre-fit PNG 1080×1920 dulu (pola p3_poster_fit)** — `render.py` menolak still+mode lain (rc 2, F7-19/F8.2-a); transisi `fade` 0,5 dtk [D GR-1]; catat **batas beat** (untuk `--cuts`) · **Jumlah panel mengikuti materi yang tersedia, bukan tetap 5 (F7-15)** — panel boleh berupa pre-crop wilayah berbeda dari satu key art + poster akhir (bukti Hamka: 3 panel dari 1 key art + 1 poster) · **Perintah konstruksi tiap panel pre-fit WAJIB dicatat di production-log beserta sha256 hasilnya (F8-5)** — perintah `fjord_blurpad.png` dari F2 hilang (berkas terverifikasi sha `2494ce05…`, dipakai di 2 produksi G-FINAL, tapi perintahnya tidak bisa direkonstruksi — 2 varian ffmpeg dicoba 23 Nov 2026, sha tidak cocok; jangan ditebak) · **Zona panel/xfade** (lock #19): zona K2 dari `project.json` = [10.09,10.59], [13.79,14.29], [18.86,19.36], [22.79,23.29]; kartu tidak melintasi zona (`pause_anchor --zones-file`, `qc_all --zones`) · **Perpanjangan kanvas panel** (celah ag): bila pre-crop y0=0 dan teks mepet tepi, perpanjang kanvas ke arah tepi (replikasi baris/kolom tepi); catat E + sha256 panel baru + backup panel lama | agen | A |
| S5 | Komposisi 9:16 **grounded**; satu gambar saja tidak cukup, bila terlihat tempelan tambah gambar/konteks [D]. Upscale lanczos · **Semantik still/cover** (celah aa): `cover` membatasi jendela ke tengah (tepi kanan maks 90,18% pada poster r=0,700); ukur rentang-x teks kunci **sebelum** menentukan `focus`; bila lewat batas cover → pre-crop aspek 0,5625 (asal-usul dicatat di `sources.json`) atau `fit` · **Aturan pita kartu memeriksa FIGUR, bukan hanya teks poster** (celah af): kartu tidak boleh menutupi figur maupun teks; bila tak ada pita bersih, perlakuan kartu = [T] (bukan geser-y buta) | `render.py` | A |
| S6 | `audio.items` (VO per WAV `at`, musik `gain_db` + `loop`), `duck`, `master.fade_out`; loudnorm | `render.py` | A |
| S7 | **Kartu** (di bawah) | `pause_anchor.py --script` (`prop`) | A |
| S8–S11 | Render (preflight berkas) → QC → review → final + audit | skrip skill | A |

### Kartu GR-1 (narasi → `timing: prop`) [D ronde 1–3]
Teks narasi dibelah di batas frasa (2–7 kata) → durasi = bagian **proporsional jumlah karakter** dalam span ucapan; **lantai 1,0 dtk**. Mereproduksi 10 kartu GR-1: span eksplisit maks Δ 0,035; `audio`+`offset` maks Δ 0,044 [D ronde 3].
- **`noise` default −50 dB** (sweep VM: −35/−40/−45 melewatkan suku kata pelan; −55 salah di ujung; −50 ≤ 0,02 dtk di tiga VO) [D]. Sweep hanya pada VO TTS bersih.
- **`hold` PER GRUP, default 0**: grup 1 = **0,10**; grup 2–3 = **0,00**. Default universal 0,10 merusak grup 2–3 (Δ 0,10–0,11).
- Grup yang berdekatan: `hold` dijepit ke start grup berikut − gap (v0.4); tidak tumpang-tindih.
Kartu **bersambung (celah 0)** sah untuk kartu legacy GR-1 (setengah terbuka). Final GR-1 asli (`between()`) **menampilkan dua kartu sekaligus di frame 87 dan 117** [D ronde 2]. **Untuk kartu BARU berlaku lock #9: celah antar-kartu min 0,04 dtk** (harmonisasi F6, celah t).
- **Satu file VO per grup (F7-18).** Jangan jalankan `pause_anchor --script` dengan SATU file VO bersama untuk banyak grup — tiap grup akan mengukur span PENUH file (gejala: kartu terakhir grup dijepit ke awal grup, kartu bertabrakan antar-grup). Pecah dulu per grup, satu file per grup + `offset` klip: `ffmpeg -i vo/narasi.wav -ss <mulai-file> -t <durasi> vo/vo1.wav` (contoh K2 Hamka: `vo1.wav` 14,60 dtk offset 0,30; `vo2.wav` 8,70 dtk offset 14,60; `vo3.wav` 16,35 dtk offset 23,00). Ulangi re-encode (bukan `-c copy`) bila potongan harus eksak sampai ke ujung kata.
- **Offset = waktu klip saat file mulai diputar, BUKAN onset ucapan (F7-26).** Contoh K2 v5: offset grup 2 yang salah = 3,81 (onset ucapan dikurangi waktu file asal); yang benar = 15,82 (waktu klip saat file `vo2.wav` mulai diputar). Rumus: offset grup = `at` item VO itu di `project.json` (audio.items). Berlaku juga untuk re-timing satu blok (v6: VO satu file, offset grup 2/3 = onset beat klip 12,31 / 16,50, bukan onset ucapan).
- **Peringatan wrap title (F7-20).** `wrap` 28 dikalibrasi untuk size 46; untuk kartu title (size 54), pecah manual via `"lines"` bila baris >~18 huruf kapital atau >~24 huruf campuran — `kartu_lint` mengukur lebar tiap baris (F8.2-b: >1080 px → FAIL), tapi pecah manual tetap tanggung jawab produser. Bukti: title K2 v1 wrap 28/size 54, baris terlebar 1095 px, teks terpotong di kedua tepi; diperbaiki dengan `"lines"` 3 baris (`SUDAH TAYANG` / `AWAL MULA HAMKA` / `19 November 2026 di Bioskop`, 909 px → PASS).
**Dialog dalam materi statis** (jarang): ikuti jalur manual K1 S7.

### Parameter terukur GR-1 [D]
- Style: `DejaVuSans-Bold`; kartu 64 px (56 px untuk dua kartu panjang via `size`); border 3; box `black@0.45`; `boxborderw` 22; `y = h-280`.
- Audio: VO `adelay` 0,3 / 10,0 / 18,5 dtk; musik −6,02 dB; sidechain threshold 0,025, ratio 6, attack 80, release 400, makeup 1; loudnorm I −18, TP −3,0 (pass-1) / −3,5 (pass-2), LRA 11; `afade` out mulai 29 dtk, 1 dtk.
- Transisi: `xfade` fade 0,5 dtk, offset 5,0 / 18,0 / 26,0 (4 segmen: dur 5,5 / 13,5 / 8,5 / 4,0).
- Bitrate: konten dominan stills wajar di bawah target 3,4 Mbps (GR-1 asli 1,30 Mbps, WARN diterima — ambang tidak dilonggarkan; lock #2).

## Knobs
jumlah & durasi panel · `zoom:[z0,z1]`, `focus:[x,y]` · `vo_source` · `at` tiap VO · musik & `gain_db` · duck · gaya kartu · `transition_in` · `noise`, `hold` per grup.

## QC gate khusus K2
1. Semua angka/teks di frame = sumber **persis** (K6).
2. Tiap teks di layar terbaca ≥ waktu baca; tidak ada momen diam/mati.
3. Larangan AI: `brief_audit` larangan_ai (klasifikasi tool + waiver).
4. Zoom tidak bergetar (jitter): periksa frame berurutan [T].
5. Frame tidak terlihat tempelan (G-HUMAN).
6. `sub_voice_check` lapis A: kartu = naskah. (Offset lapis C pada beberapa kartu boleh besar — artefak timestamp whisper, ada di final asli juga [D ronde 3].)
7. Cek naskah (lock #35–#37, `naskah-hook.md` §6): premis substansi ≤10 dtk + 4 kegagalan + janji hook dibayar + 3 varian pembuka — di G-STORY dan review-sheet.

## Kegagalan khas
| Kegagalan | Sumber |
|---|---|
| v1 tanpa VO terasa mati → dihapus | GR-1 [D] |
| Gambar terlihat tempelan | brief §5 no.7 [D] |
| Zoompan bergetar | [A/T] |
| Kartu dari transkripsi whisper salah dengar | ronde 1–3 [D] → teks dari naskah |
| `between()` / celah dipaksa ≥0,04 → kartu ganda di frame batas | ronde 1–2 [D] → setengah terbuka, celah 0 sah |
| Deteksi span `-35dB` dan tanpa `hold` | ronde 2 [D] → noise −50, hold per grup |

## Catatan F6 (celah K2-L9 + zona panel)
- **K2-L9 FAIL tercatat, non-blocking** (lock #33): span otomatis `silencedetect` −50 dB vs tanda manusia — 15/18 tepi lulus, Δ maks 0,120 dtk (vo3 s1 onset, tepi awal file; 0,067 vo3 s1 akhir; 0,072 vo2 s5 akhir, tepi akhir file). K2 lanjut dengan span eksplisit (kartu K2.8 dari tanda manusia, bukan span otomatis). Tinjau-ulang default noise −50 dB = [T] Opus. Bukti: `f2-run/f2_k2_poster/span_k2.md`.
- **Zona panel/xfade** (lock #19): satu kartu = satu panel; zona K2 [10.09,10.59], [13.79,14.29], [18.86,19.36], [22.79,23.29] dari `project.json`; kartu final K2 (13 kartu) PASS, kartu auto K2.8 (17 kartu) FAIL 5 pelintas — belahan otomatis menghilangkan pelanggaran zona tetapi menyisakan serpihan 1 kata/<1,0 dtk yang tetap butuh perbaikan manual produser.

## Lingkungan
A penuh (whisper.cpp opsional, ffmpeg). **TTS narasi default = Helio** (`/opt/hatch/bin/tts`, tanpa browser, tanpa key — lock #45). Gemini TTS via AI Studio (browser) hanya untuk override suara non-Helio (butuh browser/user, lock #45); pengganti lain: rekaman suara user. TTS open source Bahasa Indonesia: belum dites [T]. B: Real-ESRGAN opsional [T].
