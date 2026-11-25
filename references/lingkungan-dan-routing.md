# Lingkungan & routing (A = VM tanpa GPU, B = PC dengan GPU)

Tanda: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi. (Diperbarui untuk DRAF v0.4 + routing K3.)

## 1. Dua lingkungan
| | **A — VM** | **B — PC user** |
|---|---|---|
| Spesifikasi | CPU saja, **1,5 vCPU, 6 GB RAM, tanpa GPU** [D]; ffmpeg 8.1.2, Python 3.12.3, cv2 5.1.0 [D ronde 2–3] | GPU ada, **model/VRAM belum terverifikasi [T]**. Petunjuk (bukan bukti): tool FreeVideo butuh 8 GB VRAM dan ditujukan untuk PC |
| Peran | Jalur utama; satu-satunya jalur wajib untuk "production grade" | Opsional: percepatan/kualitas untuk tahap berat |
| Dijalankan oleh | agen / Richy (golden) | **user, manual** (tidak ada jembatan otomatis VM↔PC saat ini [D]). Kandidat jembatan nanti: Tailscale — keputusan terpisah, **bukan sekarang** |
| Tool yang sudah gagal | faster-whisper gagal install di VM [D]; Demucs ronde 3: instal tidak selesai (lihat §4a) | — |
| Kecepatan terukur (VM) | render 10 dtk 1080×1920 = 5,84 dtk (1,71× realtime); whisper small **RTF 0,975** [D F9.0, n=1, sampel 297 dtk] — angka lama "0,51× realtime" (ronde 3) TIDAK terulang dan tidak dipakai lagi; whisper melambat ~10× bila dua job ASR berat jalan paralel (F9-18: serialkan) | — |

## 2. Aturan routing
1. Skill harus menghasilkan klip production grade hanya dengan A.
2. Tahap boleh dipindah ke B (manual): stem Demucs untuk sumber panjang, pyannote (bila benar-benar perlu), Real-ESRGAN, RIFE, model Whisper lebih besar. Semua **[T]**.
3. Tidak ada keputusan tool yang bergantung GPU sebelum `env_report.B.json` ada dan disetujui user.
4. Perpindahan hanya lewat **file data/aset**: `stems/vocals.wav`, `diarization.json`, `frames_upscaled/`, `transcript.json`.
5. Setiap baris `evidence.md` mencatat `env: A` atau `env: B`.
6. `env_report.*.json` tidak boleh memuat nama mesin, nama user OS, atau path berisi nama orang (skrip menyaring hostname/username dan mengganti path rumah dengan `~`) [D uji sandbox].

## 3. Python di VM: pakai venv (PEP 668) [D ronde 1]
`pip install` ke Python sistem **ditolak (PEP 668)**. Buat venv sekali, pakai untuk semua modul Python:
```bash
python3 -m venv ~/venv-clipper
~/venv-clipper/bin/pip install opencv-python-headless numpy      # BERHASIL di VM: cv2 5.1.0 [D ronde 1]
~/venv-clipper/bin/pip install pysubs2 norfair                   # opsional, belum dicoba [T]
python3 scripts/env_check.py --env A --venv ~/venv-clipper --out ./env_out/   # --out = DIREKTORI
```
- **`--out` adalah direktori** (bukan nama berkas); laporan ditulis sebagai `env_report.<ENV>.json` di dalamnya [D ronde 2]. Buat dulu bila belum ada (`mkdir -p`) — `env_check --out DIR` crash bila DIR belum ada (celah ai, PASCA-F6, perbaikan kode tertunda).
- Mengapa `--venv`: tanpa itu `env_check` berjalan di Python sistem dan melaporkan `cv2 GAGAL` padahal terpasang di venv. Alternatif: `export CLIPPER_VENV=~/venv-clipper`.
- **Venv utama TIDAK boleh berisi torch** (v0.4): ronde 3 menarik torch CUDA ±5,6 GB tanpa guna. Bila ada, hapus (dikerjakan Richy). Modul berat (Demucs dll.) hanya di venv terpisah (§4a).
- **Haar: cv2 5.x tidak punya `CascadeClassifier`** [D F2, F6-A3]. Venv utama (cv2 5.1.0) tidak bisa menjalankan Haar; untuk Haar pakai venv terpisah `~/venv-opencv4` (cv2 4.10.0, `CascadeClassifier` tersedia, `.empty()` = False). `env_check` kini menguji Haar **sungguhan** (`CascadeClassifier` + `.empty()`, kunci core `"Haar (CascadeClassifier)"`) — di venv utama `core_siap_semua` jujur false; G0 memakai `~/venv-opencv4` (keputusan di `golden-reference.md`). Tidak ada skrip skill yang memanggil Haar; G-CROP tetap manual; YuNet = detektor saran kandidat [T].
- `env_check` menguji API YuNet (`yunet_create_ok`) bila file model `face_detection_yunet*.onnx` ada — **model belum ada di VM → belum teruji [T]**.
- Skrip lain (`render.py`, `qc_all.py`, `pause_anchor.py`, …) hanya memakai pustaka standar + ffmpeg/ffprobe — tidak butuh venv.

## 4. Tahap dan lingkungan default
| Tahap | Default | Boleh pindah ke B? |
|---|---|---|
| S0–S2, S4–S9, S11–S13 | A | tidak perlu |
| S3 transkrip (whisper.cpp small) | A [D terbukti produksi]; **sumber panjang K3: lihat §4b** | model medium/large lebih cepat di B [T] |
| S3b stem vokal (Demucs) | **tidak dipakai di v0.4** (retry = cabang v0.4.1, lihat §4a) | ya, untuk sumber panjang [T] |
| S3c diarization | **manual** (A) | pyannote di B bila perlu + token HF [T] |
| S5b upscale / interpolasi | A: lanczos / ffmpeg `minterpolate` | Real-ESRGAN / RIFE [T] |

### 4a. Demucs di VM — hasil ronde 3 dan batas retry
**Hasil ronde 3 [D, Richy]:** `pip install demucs --no-deps` berhasil (4.1.0), tetapi dependensi menarik **torch 2.15.0+cu132 (build CUDA, ±2,5 GB)**; indeks CPU PyTorch tidak menyediakan torchaudio; `python -m demucs` gagal (`No module named 'sphn'`, torchaudio tidak terpasang). **Separasi vokal tidak pernah berjalan.** Batas 20 menit terlampaui; venv membengkak 5,6 GB (disk bebas 136 GB). Status: **belum terbukti**.

**Keputusan:** v0.4 berjalan **tanpa Demucs**. Dialog di atas musik memakai `timing: "manual"` (default). Retry hanya bila user menyetujui (cabang v0.4.1) dengan aturan:
- venv **terpisah** `~/venv-demucs` (bukan venv utama);
- torch **CPU** dipasang eksplisit lebih dulu dari indeks CPU PyTorch, lalu `torchaudio` yang cocok versinya, lalu `sphn`/dependensi Demucs; pin versi (repo diarsipkan);
- tes tetap terbatas: trailer 2 menit, batas waktu total ditetapkan ulang oleh user;
- keberhasilan diukur: stem vokal membuat `island` lolos G2-dialog (Δ ≤ 0,15) — bila tidak, Demucs tidak dijadikan default.
Hasil dicatat di `evidence.md` §D no.4.

### 4b. Transkripsi sumber panjang (K3) — routing Skenario A [D kecepatan F9.0; kebijakan = rencana K3, tervalidasi F9 n=1]
- whisper.cpp small di VM ≈ **RTF 0,975** (F9.0, n=1, sampel 297 dtk) → **VOD 5 jam penuh ≈ 4,9 jam** transkripsi. Angka lama "0,51× realtime → 1 jam ≈ 2 jam" (ronde 3) TIDAK terulang dan DIHAPUS. **Serialkan ASR berat antar produksi paralel** — whisper melambat ~10× saat paralel (F9-18: k8 RTF 10,6/13,1 vs 0,975).
- Ada timestamp/poin dari user → ekstrak dan transkripsikan **hanya jendela ±60 dtk** di sekitar tiap poin (`ffmpeg -ss/-t` → WAV 16 kHz mono).
- "Cari sendiri" dan sumber > 20 menit → **sebut estimasi waktu ke user dulu**; tawarkan: (a) jalur K3 §15 (sinyal → potongan → transkrip per potongan), (b) user menjalankan transkripsi di PC GPU (instruksi manual, model lebih besar [T], mengikuti §6–§7), (c) user memberi daftar poin. Transkripsi penuh di VM hanya dengan izin eksplisit + estimasi (lock #46 [D n=1]).
- Hasil = segmen kalimat untuk **mencari momen** (bukan teks kartu, bukan word-level). Caption K3 mengikuti `references/K3-panjang.md` §7.
- Jangan memasang openai-whisper/faster-whisper untuk ini di VM (faster-whisper gagal dipasang [D]; torch dilarang di venv utama §3).

### 4b1. Rute unduh YouTube + QA potongan [D n=1, F9]
- Rute yt-dlp: **default → `player_client=android` (metadata saja) → ulang di waktu lain** (bot-block 403 intermiten, F7-13/F9-9; android BUKAN fallback unduhan media yang andal — eksperimen SABR-only).
- **Pin format:** potongan kandidat 360p → **`134+140`** (AVC + m4a; selector generik kini resolve ke AV1 396+251 dan stream-cut AV1 di VM hanya 0,5× realtime, F9-8); potongan 1080p → **`312+140`** (satu-satunya AVC 1080p untuk video ini adalah 312, 60fps; 137 tidak tersedia, F9-14). Sumber 60fps → konversi 30fps diverifikasi di QC.
- **Unduh ulang: hapus dulu / `--force-overwrites`** — yt-dlp melewati berkas yang sudah ada (rc tetap 0), berkas korup tetap dipakai (F9-10).
- **QA decode + cek durasi audio vs video tiap potongan sebelum transkrip** (F9-10): satu paket AAC korup bisa membuat audio putus di tengah (k9: 81,28/90,07 dtk; p2/k3: 24,35/120,10 dtk) sementara video utuh.

### 4c. stable-ts — instalasi (celah g, F2 T0.3b) [D]
Pin torch CPU dulu, lalu `pip install --no-deps stable-ts==2.19.1` + dependensi minimal. **Dilarang** `pip install stable-ts` polos (resolver meng-upgrade torch ke build CUDA). `align()` teruji ±6,5 detik pada trailer 2 menit (venv terpisah, torch 2.5.1+cpu).
**ASR-2 (F8-2, teruji 23 Nov 2026):** stable-ts tiny juga dipakai sebagai ASR ke-2 (transkrip kata independen, bukan hanya `align()` timing) — pemanggilan yang BENAR: `stable_whisper.load_faster_whisper('tiny', device='cpu', compute_type='int8')` lalu `transcribe(audio, language='id', word_timestamps=True)`; **JANGAN** `load_model('tiny')` — gagal (`ModuleNotFoundError`, butuh openai-whisper yang tidak terpasang). Model tiny ada di HF cache `~/.cache/huggingface/hub/models--Systran--faster-whisper-tiny/snapshots/d90ca5fe260221311c53c58e660288d3deb8d356/model.bin` (75.538.270 B, sha256 `dcb76c65…`), BUKAN di `~/venv-stablets` (venv hanya berisi paket). Bukti uji: `f2-run/f8/asr2-test/ASR2-TEST.md` (65 kata vs small 61, 46 sepakat, 13 blok beda — ASR-2 sah). Perintah contoh: `f2-run/f8/asr2-test/run_stablets.py`.

## 5. Timing kartu dari audio — pengaturan lingkungan [D sweep ronde 2, sintetis TTS bersih]
- `silencedetect` default `noise=-50dB`, `d=0,1` (per grup `noise` dapat diubah). Nilai −35/−40/−45/−55/−60 gagal pada 3 VO TTS GR-1. **Tidak** menjamin untuk dialog di atas musik — **terbukti gagal** (ronde 3: island Δ 0,640; −25 dB 1,065; −20 dB 2,041). Untuk ucapan alami satu pembicara (K3) belum diuji [T].
- `timing: "words"` butuh whisper.cpp `-ml 1 -sow` (`pause_anchor.py --whisper-words`); `transcript.json` berisi segmen kalimat **bukan** word-level. Pada dialog GR-2 gagal (Δ 1,450: salah dengar + bias timestamp kata pertama).
- Dialog: default **`manual`**; `--list-pauses` hanya mencetak kandidat jeda dari lembah RMS (membantu, tidak menulis kartu) [pada dialog asli: T].
- `whisper -nf` deterministik tetapi bisa salah dengar ('Suli'→'sulit', 'Rp' hilang) → sifatnya gerbang peringatan, bukan kebenaran.

## 6. Instruksi untuk USER — menjalankan `env_check` di PC (B)
> Langkah manual. Agen tidak bisa menjalankannya.
1. Pastikan Python 3.x dan ffmpeg terpasang di PC. Salin folder `scripts/` skill ini ke PC.
2. Jalankan: `python3 env_check.py --env B --bench --out ./env_out/` (Windows: `py env_check.py --env B --bench --out .\env_out\`).
3. Kirim kembali `env_out/env_report.B.json` ke agen (hanya spesifikasi hardware/software; tanpa nama mesin/user).
4. (Opsional) Jalankan `nvidia-smi` dan kirim hasilnya bila laporan menulis GPU "tidak terdeteksi" padahal PC punya GPU (AMD/Intel tidak terdeteksi oleh nvidia-smi) [D].

## 7. Pemindahan aset (manual)
- Agen menulis perintah persis + nama berkas masukan/keluaran; user menjalankan di PC dan mengirim hasilnya.
- Tiap berkas hasil diberi nama pasti (mis. `stems_<id>.zip`) dan dicatat di `production-log.md`.
- Model/bobot (RIFE dari Google Drive/Baidu, Real-ESRGAN dari GitHub releases, DeepFilterNet) diunduh user di PC sendiri; tidak ada bobot di repo [D README].
- **DeepFilterNet biner**: hanya WAV 48 kHz → resample dulu. **Demucs**: repo diarsipkan (lihat `evidence.md`) → pin versi.

## 8. Hal yang diperiksa `env_check` per lingkungan
ffmpeg + encoder libx264/aac + filter (drawtext, loudnorm, sidechaincompress, silencedetect, blackdetect, signalstats, minterpolate, zoompan, tpad, ass/subtitles, concat, amix) · libass/freetype · whisper-cli + model ggml · OpenCV (cv2 versi, `FaceDetectorYN`, Haar — **diuji sungguhan** `CascadeClassifier` + `.empty()`, kunci core; `whisper-cli` di PATH) · modul Python (av, norfair, supervision, pysubs2, torch, stable_whisper, pyannote.audio, faster_whisper) · **Python ≥3.12 untuk PyAV** · font kartu (`CAPTION_FONT`) · info GPU · waktu render 10 dtk 1080×1920 dan whisper per menit audio · `text_align` pada drawtext (bila tidak ada, set `style.text_align:"none"` [T VM]).
**Catatan v0.4:** render v4 tidak memakai `atrim` (aman di ffmpeg 8.1.2 [D ronde 3]) dan menjalankan `preflight` (berkas hilang → rc 2) sebelum ffmpeg.
