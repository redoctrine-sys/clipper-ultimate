# K1 — Klip trailer film

Tanda: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi. Status resep: **disusun dari produksi nyata GR-2 (4 iterasi); render ulang GR-2 LULUS golden ronde 3 (24,40 dtk, ΔI 0,01, ΔTP 0,17, CTA frame 645, QC 0 FAIL); timing kartu dialog = JALUR MANUAL (otomatis `island`/`words` GAGAL pada dialog di atas musik, ronde 3). Belum dibuktikan dengan trailer BARU (F2).**
**Orientasi: landscape belum divalidasi [T]** — resep ini portrait 9:16; jalur landscape tervalidasi n=1 hanya untuk K2 materi statis dari sumber landscape (F11, v0.8.0; lihat `K2-statis.md`).


## Definisi
Trailer 1–3 menit → cerita 15–60 dtk. **Premis (siapa, mau apa, konfliknya) mendarat dalam ±10 dtk pertama**, lewat adegan + dialog trailer sendiri, **tanpa teks karangan**. Hook = pertanyaan/momen dari cerita, bukan kartu judul. [D]
Contoh nyata **GR-2** — klip trailer 24,40 dtk, 4 iterasi (v4 diterima; audit brief 19 item: 18 PASS + 1 N/A larangan AI atas waiver user + 0 FAIL) [D].
Frekuensi di campaign nyata: **BANYAK — kategori terbesar** [D via riset tim].

## Input
Trailer resolusi tertinggi (Drive/link) · poster/kover resmi · `brief.json` · izin untuk apa pun yang bukan materi campaign.

## Pipeline
| Tahap | Aksi | Repo/alat | Env |
|---|---|---|---|
| S0 | `brief.json` (+`manual_items` ber-`auto`); larangan AI/reupload; waiver | — | A |
| S1 | Unduh trailer + poster — **Drive campaign = jalur utama** bila tersedia (celah a: yt-dlp dari VM diblokir bot-check YouTube, "Sign in to confirm you're not a bot"); yt-dlp = cadangan | gdown [D] / yt-dlp [T akses VM] | A |
| S2 | `ffprobe`; deteksi scene → `shots.json`; contact sheet 1 fps · **Frame-check tiap titik potong EDL** (celah i) · **Bila `gt(scene,0.3)` = 0 potong (F7-4): turun ke 0,1 + scan diff frame cv2 per 0,25 dtk + verifikasi visual** — prosedur standar, jangan tebak ambang sendiri (scene 0,3 melewatkan cut antar-adegan gelap/dissolve lambat; bukti F7: potong 1,75/5,29/10,63/19,08) · **Pair-check visual tiap batas** (celah m: tiap batas diperiksa berpasangan; waktu belah = rentang visual) | ffmpeg (`select='gt(scene,0.3)'`, lalu 0,1 bila 0 potong — F7-4) | A |
| S3 | Transkrip dialog: whisper.cpp small `-l id -nf` [D] — hanya untuk **menyusun naskah** (segmen kalimat; timestamp kalimat meleset 0,37–0,53 dtk; salah dengar berat bisa terjadi: 'Buat kau, però…' [D ronde 3]) → **bukan** sumber teks maupun timing kartu. Glosarium `--prompt` [T]. **Word-level resmi = stable-ts `align()`** (opsional, venv terpisah — instalasi di `lingkungan-dan-routing.md` §4c); tanpa itu telinga + waveform; **hanya onset ALIGN yang layak dibandingkan** (celah j). **Jangan pakai tepi segmen whisper mentah untuk batas beat/kartu (F7-11)** — verifikasi onset dengan pita ucap (300–3000 Hz) atau align word; segmen = kerangka luar saja (contoh: seg 1 mulai 0,00 vs onset benar 1,07). **WARN lapis B bukan perintah geser kartu (F7-12)** — verifikasi dengan model kedua (small word-level) bila |offset|>0,5 dtk; timing kata tidak bisa dipercaya di tepi awal/akhir grup — cross-check dengan pita ucap. **Verifikasi ASR-ganda (F7-8): ASR-1 whisper small + ASR-2 stable-ts tiny — lihat SKILL.md S3**; kata tak sepakat = [T], hanya telinga user yang memutus. Stem vokal Demucs: **opsional, belum terbukti** (instal di venv terpisah, torch CPU; ronde 3 gagal di `sphn`/torchaudio) | whisper.cpp | A |
| S4 | **Beat map** + `edl.json`; potong di jeda vokal; **catat batas BEAT** (dipakai `--cuts`) · **Onset dari klip lebar + telinga, bukan segmen transkrip** (celah h: segmen whisper bisa meleset ±2,4 dtk sesudah jeda panjang tanpa ucapan) · **EDL mencatat kartu yang menyentuh ujung segmen** (celah k) · **Sumber onset ditandai di EDL** (celah x) · **`hook_time_s` = start kartu pertama hook** (celah s: dari waveform/telinga, bukan start segmen whisper) | agen + `silencedetect` | A |
| S5 | `crop_plan.json`: deteksi wajah per shot → crop; **verifikasi visual** (G-CROP). Pan = `{"from","to"}`; shot diam = angka tetap · **Tinggi crop ≤ tinggi aktif dari `cropdetect`** (celah f: trailer ber-letterbox, area aktif 1920×1036 @ y=22 — bukan 1080) · **Bila lebar crop <500 px (F7-5): pertimbangkan pan untuk shot panorama dan fit untuk grafis full-width** (bukti F7: letterbox 804 → crop 452×804) · **Freeze mewarisi x akhir potongan; shot bergerak memakai pan `{from,to}`** (celah p: freeze dengan x berbeda meloncat di sambungan) · **Pratinjau awal + akhir (+ tengah bila pan)** per potongan (celah q) · **Cuplikan di dalam potongan: awal = src_in+0,05, akhir = src_out−0,05** (celah r: cuplikan tepat di titik potong mengambil frame shot tetangga) | OpenCV Haar (terbukti; di `~/venv-opencv4`, cv2 4.10.0 — cv2 5.x tak punya `CascadeClassifier`, lock #30) / YuNet (opencv_zoo) [T]; Norfair [T] | A |
| S6 | Audio: `audio.items` — audio sumber punya `src_in` **terpisah** dari video (GR-2: offset audio ≠ video); loudnorm −18 / TP −3,5. Render v4 tanpa `atrim`; uji regresi `selftest_render` | `render.py` | A |
| S7 | **Kartu dialog — JALUR MANUAL (default):** (1) span tiap grup dari EDL; (2) `pause_anchor.py --list-pauses trailer.mp4 --src-in <s> --dur <d> --offset <o>` → **kandidat** jeda (lembah RMS; di atas musik bisa ada lembah palsu/jeda hilang) — **dengarkan/lihat waveform dan pilih sendiri**; (3) tulis `cards.json` (teks dialog verbatim, 2–7 kata, dibelah per frasa, **celah antar-kartu 0,04**, start = onset frasa, end = start berikut − 0,04); (4) `qc_all` (`kartu_lint`) ; (5) **G-HUMAN: putar ulang bagian dialog** dan cek sinkron. Contoh bentuk: `templates/cards.dialog.example.json`. **Dilarang `prop`** (GR-2 Δ 0,65). `island`/`words` = eksperimental, hanya bantuan awal yang WAJIB dikoreksi manual · **Dialog cepat — urutan penyelesaian** (celah u): gabung frasa ≤7 kata → geser awal ≤0,35 dtk → mundur ≤1 frame dari onset → tahan sesudah ucapan; **jangan pernah terlambat >1 frame** dari onset · **Onset kartu dari waveform** (celah x); sumber onset ditandai di EDL | agen + manusia | A |
| S8–S11 | Render → QC → review → final + audit brief · render panjang dijalankan terlepas dari sesi exec (`setsid nohup ... &` — exec restart pernah membunuh render di frame 474/867) · teks `reason` di `project.json` dibiarkan apa adanya sesudah render (mengubahnya = selisih berkas-vs-render) | skrip skill | A |

### Beat map
| Beat | Waktu | Isi | Aturan |
|---|---|---|---|
| Hook | 0–≈3 dtk (≤20% durasi; GR-2: 2,70 dtk = 11,1%) | momen/pertanyaan dari dialog/adegan | bukan kartu pernyataan |
| Premis | ≤10 dtk | siapa, mau apa, konflik | adegan + dialog asli |
| Eskalasi | tengah | 2–3 momen yang menaikkan taruhan | potong di jeda vokal |
| Penutup | akhir | poster/judul + CTA end card, **durasi = max(butir brief B10, 1,5 dtk), diukur dari frame judul utuh pertama** (celah l/ac: freeze judul utuh ≥1,5 dtk; tafsir "reveal + judul utuh" ditolak), scene akhir utuh; **G-STORY mencocokkan tiap beat penutup dengan butir brief** | `fit` + bar hitam (bukan blurpad); freeze = frame sumber/PNG; layar hitam = segmen `color` |

**Batas beat GR-2 (untuk `--cuts`):** 2,70 · 6,34 · 9,74 · 13,64 · 16,22 · 21,50. Satu beat boleh berisi beberapa potong shot internal; kartu boleh menjangkaunya (desain asli yang diterima user). Memberi `--cuts` semua 13 batas segmen → FAIL palsu [D ronde 3].

### Parameter terukur GR-2 [D]
- Style: font `DejaVuSans-Bold`; kartu 46 px, border 3, box `black@0.45`, `boxborderw` 20, `y = h-280`. 12 kartu, **timing dibuat manual dari jeda ucapan nyata** (celah tepat 0,04) — hardcode di build asli [D Richy].
- Crop 482×858 (piksel sumber) per shot: S0 x=580 · S1 x=1040/450 · S2c 1295 · S3 460 + pan 1150→1028 · S4 pan 537→885 · S5a 850 · S5b pan 824→1008 · freeze 1008.
- Judul + CTA: mode **`fit`** (`scale 1080:452/453` + pad hitam) — **bukan** blurpad. Layar hitam dalam proyek = `{"type":"color","color":"black",...}` (v0.4; sebelumnya `black.png`).
- Audio: offset audio ≠ video (S0 audio 90,85 vs video 94,21; S4 musik 98,40 vs 101,75; S5 101,30 vs 100,04); loudnorm TP −3,5. Dialog **di atas musik trailer** (mix master MP4) [D].
- Ekor: CTA poster gelap + ekor sunyi (23,61–24,40) **disengaja & diterima user** → `qc_exceptions`: `digital_silence` (WARN) dan `frame_hitam` 21,50–24,37 (gelap-berkonten → WARN **bila dideklarasikan**; tanpa deklarasi FAIL; hitam murni tetap FAIL). YMAX poster: min 16, median 255, maks 255 [D E3].
- CTA mulai 21,50 dtk (frame 645) [D ronde 2, 3].

## Knobs
durasi (brief) · jumlah beat · ambang scene · mode reframe per shot · kartu poster · ukuran kartu (46/54 px) · gain audio sumber · `timing` kartu (**`manual` default**; `island`/`words` eksperimental) · `hold` per grup · `noise` (default −50 dB).

## QC gate khusus K1
1. **Premis teruji:** ringkasan 1 kalimat dari 10 dtk pertama = logline film (agen **dan** user, G-STORY).
2. **Tidak ada kata terpotong** di titik potong (energi audio di batas ±80 ms [T]).
3. **Scene akhir utuh**; end card gelap disengaja → `qc_exceptions` (gelap-berkonten WARN; hitam murni FAIL).
4. **`sub_voice_check` lapis A:** kartu = naskah/dialog; tidak ada narasi brief yang ditempel [D].
5. Crop diverifikasi di frame lebar penuh; kartu tidak menutupi wajah/objek kunci.
6. Hook ≤20% durasi (`brief_audit` hook, butuh `hook_time_s`).
7. **Audio per item:** audio sumber mendarat di `at` (bukan t=0) — uji regresi `selftest_render`.
8. **Sinkron dialog diperiksa manusia** (jalur manual): putar ulang tiap grup; kartu muncul pada onset frasa (±0,05 dtk sebagai target, bukan gate otomatis).

## Kegagalan khas (nyata, GR-2) [D]
| Versi | Penolakan user | Pencegah |
|---|---|---|
| v1 | subtitle terlalu besar; hook bukan hook; tidak ada alur | beat map + locked #6; kartu 46 px; G-STORY |
| v2 | subtitle↔voice mismatch; voice terpotong; scene akhir terpotong | teks dari naskah/dialog; potong di jeda vokal; cek scene akhir |
| v3 | premis diterima, scene penutup dipertanyakan | G-HUMAN + K8: tiap keluhan jadi butir |
| (v1) | Haar salah baca 3 dari 12 shot | locked #10, G-CROP |
Tambahan: `tpad` default → frame hitam. Ronde 1: render lama tanpa `fit`/kotak/offset audio/pan → `render.py` v2. Ronde 2: bug `atrim` → v3 + regresi; kartu proporsional-karakter gagal. **Ronde 3:** `island` (musik mengisi jeda, Δ 0,64) dan `words` (salah dengar + bias, Δ 1,45) gagal → manual default; `--cuts` berisi tiap shot → FAIL palsu; `black.png` hilang → `color`.

## Lingkungan
| | A (VM) | B (PC) [T] |
|---|---|---|
| Transkrip | whisper.cpp small 0,51× realtime [D ronde 3] | model lebih besar |
| Stem vokal | Demucs: belum berhasil (ronde 3); retry opsional di venv terpisah | cepat |
| Deteksi wajah | Haar/YuNet CPU (YuNet: model belum ada di VM [T]) | sama |

## Bukti yang masih dibutuhkan [T]
**Klip dengan trailer BARU + review user (F2)** · waktu & manfaat Demucs (opsional) · ambang scene · YuNet vs Haar pada 12 shot GR-2 (F3-A) · `--prompt` whisper-cli · apakah `--list-pauses` benar-benar mempercepat penyusunan manual (diukur di F2).
