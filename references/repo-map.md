# Peta 22 repo → tahap pipeline

Tanda: **[D]** terverifikasi (README/dokumentasi resmi yang dibaca 22 Nov 2026, inventaris, produksi, golden ronde 1; detail di `evidence.md`) · **[T]** butuh tes · **[A]** asumsi · **(via riset)** = temuan riset README oleh tim, belum saya baca sendiri.
Kolom **A** = VM tanpa GPU. Kolom **B** = PC dengan GPU (semua **[T]**; model GPU belum terverifikasi).
Hasil `env_check` per lingkungan menggantikan kolom kesiapan ini begitu F0 dijalankan. **Python di VM: venv (PEP 668)** — lihat `lingkungan-dan-routing.md` §3.

| # | Repo | Tahap · Kasus | Lisensi | Kesiapan A | Kesiapan B [T] | Peran & temuan dokumentasi | Alternatif |
|---|------|---------------|---------|-----------|----------------|----------------------------|-----------|
| 01 | yt-dlp | S1 · K3, K1/K7 bila link web | Unlicense (binari PyInstaller memuat GPLv3+) [D] | tersedia, belum dipakai untuk YouTube [D]; akses jaringan ke YouTube dari VM belum dites [T] | sama | Core. pip `yt-dlp`; **ffmpeg/ffprobe wajib** untuk merge; dukungan YouTube penuh butuh `yt-dlp-ejs` + runtime JS (deno/node) [D]. `--download-sections "*mulai-akhir"` ambil potongan [D] | unduh manual oleh user |
| 02 | OpenCut | edit GUI | MIT | tidak dipakai | opsional | Di luar core (rewrite besar) [D inventaris] | ffmpeg |
| 03 | OpenCV | S5 · K1, K3, K4, K7 | Apache-2.0 | Haar terbukti produksi [D]. **`opencv-python-headless` terpasang di venv: cv2 5.1.0 (±16,6 dtk) [D ronde 1]**; API `FaceDetectorYN` di cv2 5.x belum diuji (`env_check` menguji `create`) [T]. YuNet butuh model dari **opencv_zoo, BUKAN dari repo opencv** (via riset; tutorial resmi merujuk ke zoo) [D] | sama | Core deteksi. `cv2.FaceDetectorYN.create(model, config, input_size, score_threshold=0.9, nms_threshold=0.3, top_k=5000)`; baris hasil: x,y,w,h, 5 landmark, skor [D tutorial] | — |
| 04 | OBS Studio | perekaman · K5 (ditunda) | GPL-2.0 | tidak bisa | PC user [D] | Eksternal | rekaman layar OS |
| 05 | AI-Youtube-Shorts-Generator | konsep S3–S5 · K3 | MIT | **mode API butuh MuAPI key; mode local butuh faster-whisper (gagal install di VM) DAN API key LLM (OpenAI/Gemini)** [D README + riset] → praktis tertutup | sama | Hanya sumber **konsep** (kriteria viralitas, chunking, dedupe >50%), ditulis ulang dengan kata sendiri | pipeline core |
| 06 | Mediabunny | konversi di browser | MPL-2.0 | tidak dipakai | — | Di luar core | ffmpeg |
| 07 | Whisper (OpenAI) | S3 cadangan | MIT | butuh PyTorch + bobot, berat di 6 GB [A/T] | layak [T] | Cadangan | whisper.cpp |
| 08 | whisper.cpp | S3 · semua yang ada ucapan | MIT | **terbukti produksi** (ggml-small, Indonesia) [D]. **Ronde 1: `-ml 1 -sow -oj` terbaca benar (GR-1: 15/11/10 kata) [D]**; transkrip GR-2 asli = 39 **segmen kalimat** (tanpa token kata) — jangan diperlakukan sebagai word-level. Stokastik: file sama → hasil berbeda (cakupan 91% vs 100%) dan salah dengar nama/bahasa informal ("Suli"→"sulit") [D] | model lebih besar [T] | **Core.** Biner `whisper-cli`; hanya WAV 16-bit (16 kHz mono); `-l` default **en** → pakai `-l id`; `-ml 1` word-level **EKSPERIMENTAL**; opsi `-sow`, `-oj/-ojf`, `-of`, `-dtw`, `--vad`, `-nf` (tanpa fallback temperatur → lebih deterministik [T]), `--prompt` (glosarium nama [T]); memori small ≈852 MB, medium ≈2,1 GB [D README]. Dipakai untuk **span ucapan/sanity** dan (K3) **pencarian momen**, bukan sumber teks kartu | faster-whisper (re-test) |
| 09 | stable-ts | S3/S7 word timing · K1–K4 | MIT | PyTorch CPU di 6 GB belum dites [T] | layak [T] | **Pengembangan dijeda tanpa batas & repo diarsipkan** [D]. `align()` = forced alignment teks diketahui→audio (butuh `language`); varian **`stable-ts-whisperless`** tanpa dependensi Whisper [D]. **Jalur ketiga F3-A:** naskah + `align()` whisperless → lapis B `sub_voice_check` [T] | whisper.cpp + span-prop (terbukti) |
| 10 | pyannote.audio | S3c diarization · K4 | MIT (kode) | tidak di jalur utama (lambat) | opsional [T] | Pipeline **`pyannote/speaker-diarization-community-1`** butuh token Hugging Face + setuju syarat pengguna; **`precision-2` = layanan cloud pyannoteAI BERBAYAR**, bukan gratis [D README] | diarization manual |
| 11 | Supervision | QC overlay | MIT | ringan [A]; Python ≥3.10 [D] | sama | **Tidak mendeteksi apa pun sendiri** — hanya visualisasi/overlay (kotak crop di contact sheet) (via riset; README memakai `BoxAnnotator`) | gambar kotak via OpenCV |
| 12 | Norfair | S5 stabilisasi · K3, K4 | BSD-3-Clause | ringan [A] | sama | **Tidak mendeteksi** — butuh detektor. Rantai wajib: **detektor (Haar/YuNet) → Norfair (`Tracker(distance_function, distance_threshold)`, `Detection(points)`, `tracker.update(detections=…)`) → smoothing crop** [D README + riset] | smoothing moving-average |
| 13 | DeepFilterNet | S6 denoise · K3, K4 | MIT atau Apache-2.0 (dual) [D] | bobot dihapus saat install (unduh ulang) [D]; belum dites di CPU [T] | layak [T] | pip `deepfilternet`; CLI `deepFilter`; **biner `deep-filter` hanya WAV 48 kHz → resample dulu** [D] | ffmpeg `afftdn` [A] |
| 14 | Demucs | S3b stem vokal · K1, K4 | MIT | CPU lambat; ≤3 menit dites dulu [T] | layak [T] | **Repo diarsipkan: GitHub menampilkan "Public archive" / "Archived: Yes" [D terverifikasi ronde 1]; "tidak dimaintain lagi"; rujukan fork `adefossez/demucs`** → **pin versi** yang dipakai. **Tanggal arsip 1 Jan 2025 bersumber dari extractstems.com — halaman GitHub sendiri tidak menampilkan tanggal di teks yang terbaca** (kutip sumber ini bila menyebut tanggal). `--two-stems=vocals`, model default `htdemucs`, `-d cpu`, `-j` melipatgandakan RAM; keluaran `separated/<model>/<track>/vocals.wav` 44,1 kHz [D]. Doc menyebut waktu ≈1,5× durasi trek di bagian CPU (hardware tak disebut) → ukur di 1,5 vCPU [T]. **Ronde 3: instal di VM gagal (torch CUDA tertarik, `sphn`/torchaudio kurang); retry menunggu keputusan user, venv terpisah** | deteksi jeda dari mix + cek manual |
| 15 | pysubs2 | S7 ASS · K4 | MIT | pure Python [D] | sama | Edit/shift/simpan SRT/ASS; CLI `--shift`, `--to`; gaya SSAStyle: lihat API docs (README tak memuat) [D]. Kandidat jalur caption ASS untuk kata kunci berwarna K3 (render v5, setelah F2) [T] | tulis ASS manual |
| 16 | libass | S8 burn-in ASS | ISC | ffmpeg di VM harus `--enable-libass` (README libass tidak menyebut ffmpeg [D]) → cek `env_check`; **libass terpasang di VM ronde 3 [D]** | sama | Opsional; drawtext adalah jalur terbukti. Dibutuhkan bila render v5 memakai ASS (kata kunci berwarna K3) | drawtext |
| 17 | Editly | — | MIT | **ditolak** | ditolak | Butuh Node + ffmpeg, Linux perlu langkah headless-gl [D README]; transisi default `random` **non-deterministik** → bertentangan dengan pipeline yang butuh hasil berulang (via riset). Transisi diganti `xfade` di `render.py` v2 | ffmpeg (`render.py`) |
| 18 | Kdenlive | edit GUI | GPL-3.0 | tidak | PC user | Eksternal (handoff); dipanggil sebagai program, tanpa menyalin kode | — |
| 19 | Shotcut | edit GUI | GPL-3.0 | tidak | PC user | Eksternal (handoff) | — |
| 20 | Real-ESRGAN | S5b upscale · K2, K7 | BSD-3-Clause | **diganti lanczos** [D keputusan] | opsi **ncnn-vulkan tanpa PyTorch/CUDA** (GPU Intel/AMD/Nvidia), tak mendukung `outscale`; atau Python (PyTorch ≥1.7); bobot diunduh dari GitHub releases [D README] | Opsional di B | ffmpeg lanczos |
| 21 | RIFE | S5b interpolasi · K7 | MIT | **diganti `minterpolate`** [D keputusan] | butuh GPU realistis (rujukan README: 2080Ti); bobot dari Google Drive/Baidu (manual) [D README]; **`--fps` menghapus audio** → hanya untuk klip tanpa audio sinkron atau mux ulang | Opsional di B | ffmpeg `minterpolate` |
| 22 | PyAV | S2/S9 frame-level | BSD-3-Clause | wheel `av` membawa FFmpeg [D]; README menyarankan CLI ffmpeg bila CLI cukup; **butuh Python ≥3.12 (via riset) → cek di F0-A** | sama | Pembantu skrip untuk akses frame saja | ffmpeg CLI |

## Di luar 22 repo (dipakai produksi atau wajib)
**ffmpeg** (renderer tunggal; build harus punya libx264, aac, drawtext (+`text_align` untuk kartu multi-baris), loudnorm, sidechaincompress, silencedetect, blackdetect, zoompan, xfade, amix `normalize`; libass opsional), **gdown** (Google Drive), **instagram-cli** (postingan IG), Shortwave TTS via `/opt/hatch/bin/tts` (default narasi, Helio `avocado_v2:MAI_03` — lock #45); Gemini TTS via AI Studio hanya untuk override suara non-Helio (butuh browser/user), browser untuk posting/submit [D produksi]. **faster-whisper = "butuh re-test"** (gagal install di VM) [D].

## Sumber metode di luar 22 repo — skill luar "YouTube highlight clipper" (K3)
Bukan repo; postingan publik berisi prompt + skill. **Lisensi tidak diketahui → hanya metode yang didistilasi, ditulis ulang di `references/K3-panjang.md`; tidak ada teks/kode yang disalin** (`THIRD_PARTY_LICENSES.md`; identitas sumber di `_internal/`). Peta peran alat:
| Unsur sumber | Peran di skill ini | Alat kita |
|---|---|---|
| unduh sumber | S1 K3 | yt-dlp (#01) bila diizinkan brief |
| transkripsi berwaktu kata | **hanya pencarian momen** (bukan caption) | whisper.cpp (#08) `-l id -nf` (bukan openai-whisper/faster-whisper) |
| rubrik skor momen | G-STORY K3 | penilaian agen → `moments.json` |
| contact sheet verifikasi | G-STORY K3 | ffmpeg `fps`+`tile` (S2) |
| caption ASS + kata kunci berwarna | statis per kartu (render v5, setelah F2) | ASS via libass (#16)/pysubs2 (#15) [T] |
| judul/watermark/avatar | opsional per-brief, default MATI | `overlays` render v5 (bila brief meminta) |
| TTS + ducking | ditunda (generative → waiver) | `audio.duck` ada |
| loudness −14/−16 | **ditolak** (lock −18) | — |
| format horizontal | **ditolak** (TikTok 9:16) | — |

## Koreksi dari browse dokumentasi (22 Nov 2026) + golden ronde 1
1. #05 mode local butuh **key LLM** selain faster-whisper → tertutup di A.
2. YuNet bukan dari repo opencv → opencv_zoo.
3. Demucs & stable-ts sama-sama tidak aktif dimaintain → pin versi. (Tanggal arsip Demucs: lihat baris #14 — sumber pihak ketiga.)
4. Biner DeepFilterNet hanya 48 kHz.
5. whisper.cpp `-l` default `en`.
6. `tpad` default = hitam, `stop_mode=clone` membekukan (uji sandbox).
7. (ronde 1) pip sistem ditolak PEP 668 → venv. whisper.cpp tak cocok sebagai sumber teks kartu (stokastik + salah dengar).
