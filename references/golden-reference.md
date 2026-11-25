# Golden reference — protokol + HASIL (v0.4)

Tujuan: membuktikan skrip skill **mereproduksi** dua produksi yang sudah diterima user, dan cek-cek skill tidak salah-kalibrasi. **GR-1** = klip materi statis 30 dtk (v2 final). **GR-2** = klip trailer film 24,40 dtk (v4 final).
**Batas bukti:** golden hanya membuktikan reproduksi dua final lama — **bukan** kemampuan pada materi baru (itu F2). **K3 tidak punya final lama → bukan golden; lihat "Validasi K3" di bawah.**

> **Aturan: kriteria di "Kriteria lulus" DIKUNCI dan TIDAK berubah.** Bila ada yang gagal: jangan ubah ambang — kirim hasil, agen memperbaiki skrip. Pelonggaran hanya dengan alasan teknis **dan** kasus negatif di `selftest.py` yang tetap FAIL.
> Jalankan dari folder kerja baru berisi salinan `scripts/` dan salinan data asli. Jangan menimpa data asli. Tanpa nama orang/akun di berkas yang dikirim.

## Riwayat hasil
| Ronde | Versi | Hasil |
|---|---|---|
| 1 | v0.1 | G1–G4 FAIL |
| 2 | v0.2 | G0/G1/G4 PASS; G2 FAIL; G3-GR2 FAIL (bug audio `atrim`) |
| **3** | **v0.3** | **G0/G1/G3/G4 PASS; G2-narasi PASS; G2-dialog FAIL (keterbatasan diketahui)** |
| (ringan) | v0.4 | selftest di VM + render ulang G3-GR2 dengan segmen `color` (lihat "Verifikasi v0.4") — [T] |

### Hasil ronde 3 (VM, 22 Nov 2026) [D]
| Gate | Hasil |
|---|---|
| G0 | `core_siap_semua` true; render bench 5,84 dtk (1,71×); whisper 0,51×; semua filter + libass + `text_align`; Python ≥3.12; cv2 OK; YuNet [T] (model tak ada) |
| E3 | **Ambang YMAX 64 VALID**: poster CTA GR-2 (21,50–24,37) YMAX n=81, min 16, median 255, maks 255; freeze hitam `tpad` sintetis 2 dtk = 16 konstan (n=60) |
| G1 | 0 FAIL kedua final asli. GR-1 WARN bitrate 1,30 Mbps. GR-2 WARN digital_silence + frame_hitam (dideklarasikan); poster = `gelap_berkonten`, ymax_maks 255, frac_konten 0,67. Tanpa deklarasi → FAIL (probe terkonfirmasi) |
| G2 narasi (GR-1) | **PASS**: span eksplisit maks Δ 0,035; span+hold 0,035; `audio`+`offset` noise −50 dB hold 0,10/0,00/0,00 maks Δ 0,044; 10 kartu |
| G2 dialog (GR-2) | **FAIL**: `island` (mix mentah, −50 dB) maks Δ 0,640 (−25 dB: 1,065; −20 dB: 2,041); `words` maks Δ 1,450. Sebab island: musik mengisi jeda → tiap grup 1 pulau, onset terdeteksi di awal segmen; sebab words: salah dengar + bias timestamp kata pertama (t=0,00), seg3 hanya 2/6 kata cocok. Penolakan segmen kalimat PASS |
| G3 | GR-1 30,00 dtk, ΔI 0,05, ΔTP 0,17, QC 0 FAIL, SVC-A 0 FAIL, render 44 dtk. GR-2 24,40 dtk, I −18,13 (ΔI 0,01), TP −3,33 (ΔTP 0,17), QC 0 FAIL, SVC-A 0 FAIL, render 48 dtk; CTA 21,50 tepat (frame 645); luma title Δ 0,045, CTA Δ 0,0004. Hapus `atrim` (termasuk bus akhir) aman di ffmpeg 8.1.2 |
| G4 | GR-1 18 PASS selaras 3/3; GR-2 23 PASS + M13 N/A selaras 5/5 |
Temuan lain: `--cuts` = batas beat (kartu_lint GR-2 FAIL bila 13 batas segmen; PASS dengan 6 batas beat 2,7; 6,34; 9,74; 13,64; 16,22; 21,5) · `black.png` tak dibuat render (→ segmen `color` v0.4) · anomali luma sebelum cut 2,70/7,56 = beda fase 24→30 fps (bukan geser) · offset SVC lapis C −0,67/−1,36 pada kartu GR-1 #8/#9 ada di asli maupun rebuild (artefak timestamp whisper).

## Persiapan (venv — pip sistem ditolak PEP 668)
```bash
python3 -m venv ~/venv-clipper && ~/venv-clipper/bin/pip install opencv-python-headless numpy   # JANGAN pasang torch di venv ini
export WHISPER_MODEL=/path/ke/ggml-small.bin
export CAPTION_FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
python3 scripts/env_check.py --env A --bench --venv ~/venv-opencv4 --out ./env_out/ --sample <audio_uji.wav> --model "$WHISPER_MODEL"   # --out = DIREKTORI; --venv = venv-opencv4 (Haar; lihat "Keputusan F6 — G0 dan Haar" di bawah)
python3 scripts/selftest.py --render        # HARUS 100% sesuai (173/173 di sandbox v0.6.0)
```

## Keputusan F6 — G0 dan Haar (22 Nov 2026) [D]

**Keputusan: G0 menjalankan `env_check` di `~/venv-opencv4` (opsi i) — Haar tetap kunci core, tidak dikeluarkan.**

Bukti yang mendasari:
- `env_check` v4.2-F6 (F6-A3) menguji Haar **sungguhan** (`cv2.CascadeClassifier` + `.empty()`) dan menjadikannya kunci core (`"Haar (CascadeClassifier)"`), sehingga `core_siap_semua` kini jujur. Di venv utama (cv2 5.1.0) `CascadeClassifier` **tidak ada** — `core_siap_semua` di sana tidak bisa true, dan itu benar, bukan cacat.
- `~/venv-opencv4` (cv2 4.10.0): `CascadeClassifier` ada, load file menghasilkan `.empty()` = False — Haar tersedia (terverifikasi F6-A3, `env_report.A.json` sha256 `013961ae…`). `core_siap_semua` true di sana bila `whisper-cli` ada di PATH dan `CAPTION_FONT` ter-set (keduanya bukan soal Haar).
- Baris G0 ronde 3 ("`core_siap_semua` true") adalah **riwayat pra-perbaikan** — saat itu `env_check` belum menguji Haar sungguhan; laporan F2 bahkan mencatat `core_siap_semua: true` padahal `haar_frontalface: false` (salah-kalibrasi yang kini diperbaiki, celah c).
- **Tidak ada skrip skill yang memanggil Haar** (hanya `env_check` yang menyebutnya) — jadi tidak ada tahap pipeline yang terblokir oleh tidak tersedianya Haar di venv utama. G-CROP tetap manual (lock #10); YuNet adalah detektor saran kandidat [T] (model belum ada di VM).

Aturan G0 yang berlaku: jalankan `env_check --env A --bench --venv ~/venv-opencv4 --out ./env_out/` (dengan `whisper-cli` di PATH + `CAPTION_FONT` ter-set); `core_siap_semua` harus true **di venv itu**. Laporan `env_check` dari venv utama (cv2 5.1.0) yang mencatat Haar tidak tersedia + `core_siap_semua` false adalah hasil yang **diharapkan**, bukan FAIL G0 — venv utama bukan lingkungan Haar. Opsi (ii) — mengeluarkan Haar dari kunci core — **ditolak** di F6: Haar masih disebut resep (K1 S5) sebagai detektor yang pernah terbukti, dan menghapus kunci core akan menyembunyikan lagi ketidaktersediaan yang baru saja diperbaiki; bila suatu hari Haar resmi ditinggalkan demi YuNet, keputusan itu dicatat tersendiri (bukan diam-diam lewat satu baris kode).

## Verifikasi v0.4 (ringan; bukan ronde golden penuh)
Kode yang diuji golden tidak berubah selain `render.py` (segmen `color`, preflight) dan `pause_anchor.py` (jepit antar-grup, `--list-pauses`). Maka cukup:
1. `python3 scripts/selftest.py --render` di VM → 100% sesuai.
2. **Render ulang G3-GR2 dengan segmen `color`.** Di `project_gr2.json` ganti segmen layar hitam:
   `{"type":"still","src":"work_gr2/black.png","dur":D,...}` → `{"type":"color","color":"black","dur":D,...}` (kunci lain — `transition_in`, `at` — tetap). Hapus ketergantungan `black.png`.
   Kriteria **identik dengan ronde 3**: durasi 24,40 dtk (Δ ≤ 0,05), ΔTP 0,17 (≤ 0,5), ΔI ≤ 0,5, luma title/CTA Δ ≤ 10, CTA di frame 645 ±1, QC 0 FAIL, SVC-A 0 FAIL. Catat bila ada selisih frame di bagian yang tadinya `black.png`.
3. (Opsional) `python3 scripts/pause_anchor.py --list-pauses <trailer.mp4> --src-in 64 --dur 8 --offset 9.74` pada satu grup dialog GR-2 → bandingkan kandidat jeda dengan jeda ucapan asli (kartu GR-2 asli); catat berapa jeda asli yang tertangkap sebagai kandidat (informasi, bukan gate).

## Validasi K3 (BUKAN golden — tidak ada final lama) [T]
K3 (video panjang 1 pembicara → klip highlight; resep DRAF `references/K3-panjang.md`) tidak punya produksi lama yang diterima user, jadi tidak bisa direproduksi. Pengganti: **validasi pada materi baru**, dijalankan **setelah K7** (urutan keputusan Richy 22 Nov 2026). Kriteria **DIKUNCI sebelum uji** dan tidak boleh dilonggarkan setelah melihat hasil (aturan yang sama dengan golden):
| # | Kriteria | Ambang |
|---|---|---|
| V1 | QC (`qc_all`) pada tiap klip | **0 FAIL** (WARN boleh, tiap WARN ada alasan/pengecualian terdeklarasi) |
| V2 | `sub_voice_check` lapis A pada tiap klip | **0 FAIL** |
| V3 | Caption per frasa-napas: start/end kartu vs jeda yang ditandai **manusia** pada ±60 dtk ucapan | maks Δ ≤ **0,10 dtk** |
| V4 | `moments.json` lengkap per sumber | skor rubrik, alasan, **bukti contact sheet** per momen terpilih; momen yang diminta tapi tidak ada dilaporkan `tidak_ditemukan` |
| V5 | G-HUMAN (user) | disetujui dalam **≤ 2 iterasi** |
| V6 | `brief_audit` | **0 FAIL, 0 PENDING** |
- Materi: 1 sumber panjang 1 pembicara yang **sah dipakai** → 2–3 klip. **Materi BELUM ada** (daftar [T] #15): harus dipilih user sebelum validasi, mis. ceramah/podcast berlisensi terbuka (CC) atau long-form dari campaign dengan izin brief. G-HUMAN = user.
- Lulus V1–V6 → klaim production grade **hanya K3** (klaim per kasus). Gagal → kirim hasil, agen memperbaiki; ambang tidak diubah.
- Catatan: kata kunci berwarna statis (ASS, render v5-F6) **sudah ada** — validasi sintetis V1–V2 lulus (LAPORAN_F6_K3.md); V3–V6 tetap menunggu materi nyata. Overlay opsional **tidak** termasuk kriteria v1 — kodenya menunggu brief yang meminta ([T]).
- Estimasi transkripsi sumber panjang di VM ≈ 2 jam per 1 jam sumber → pakai jendela ±60 dtk (lihat `lingkungan-dan-routing.md` §4b).

## G0 — Audit lingkungan + selftest
Kirim `env_report.A.json` dan keluaran `selftest.py --render` (salin utuh).

## E1 / E3 (SUDAH dijalankan)
E1 sweep noise: default −50 dB (`evidence.md` §F). E3 YMAX 64 valid (di atas). Tidak diulang kecuali VM/ffmpeg berubah.

## G1 — QC pada klip FINAL asli (tanpa render ulang)
Pengecualian dideklarasikan **di file** (`qc_exceptions`, wajib alasan). GR-2: ekor sunyi `23.61–24.40` (digital_silence) dan poster CTA gelap `21.50–24.37` (frame_hitam — gelap-berkonten, WARN bila dideklarasikan; hitam murni tetap FAIL). **`--cuts` = batas BEAT.**
```bash
python3 scripts/qc_all.py --video <final>.mp4 --cards cards_<gr>.json --cuts <batas_beat> --exceptions exceptions_<gr>.json --frames-dir qc_<gr> --out qc_<gr>.json
```
GR-2 beat: `--cuts 2.7,6.34,9.74,13.64,16.22,21.5`.

## G2 — Kartu (`pause_anchor.py`)
**GR-1** (narasi, `timing: prop`): (a) span eksplisit; (b) `audio`+`offset`, noise −50 dB, **`hold` per grup** (grup 1 = 0,10; grup 2–3 = 0,00).
**GR-2** (dialog): **kriteria G2-dialog TIDAK berubah** (±0,05, 12 kartu) — status saat ini **FAIL tercatat (keterbatasan diketahui)** untuk `island`/`words`. **Jalur default dialog = manual**: `cards.json` eksplisit → `kartu_lint` → G-HUMAN; dibuktikan lewat G3-GR2 (cards asli → render identik).
```bash
python3 scripts/pause_anchor.py --script script_gr1.json --out cards_new_gr1.json --compare cards_gr1.json
python3 scripts/pause_anchor.py --mode word-pause --words work/transcript.json --out x.json    # HARUS menolak (segmen kalimat)
```

## G3 — Render ulang dari data (skema project v2)
`project_<gr>.json` dari build asli (`templates/project.example.json`). Render v4: tanpa `atrim` (bug ronde 2), preflight, `type:"color"` untuk layar hitam.
```bash
python3 scripts/render.py --config project_<gr>.json --print
python3 scripts/render.py --config project_<gr>.json
python3 scripts/qc_all.py --video final_baru.mp4 --cards cards_<gr>.json --cuts <batas_beat> --exceptions exceptions_<gr>.json --frames-dir qc_baru_<gr> --out qc_baru_<gr>.json
python3 scripts/sub_voice_check.py --cards cards_<gr>.json --script naskah_<gr>.txt --video final_baru.mp4 --model "$WHISPER_MODEL" --out svc_<gr>.json
```

## G4 — Audit brief
`brief_audit.py`; GR-1 12 manual + 6 AUTO; GR-2 18 PASS + M13 N/A + 5 AUTO; selaras.

## Kriteria lulus — DIKUNCI (tidak berubah sejak ronde 2)
| # | Kriteria | Ambang |
|---|---|---|
| G1 | QC pada final asli GR-1 & GR-2 | **0 FAIL** (WARN boleh, tiap WARN ada alasan/pengecualian terdeklarasi) |
| G1 | Suite negatif `selftest.py` | **semua FAIL sesuai harapan** (100% sesuai) |
| G2 | Jumlah kartu | GR-1 = **10**, GR-2 = **12** |
| G2 | Start/end tiap kartu vs tabel asli | **±0,05 dtk** (GR-1 juga lewat `audio`+`offset`) |
| G2 | Input segmen kalimat ke mode word-pause | **ditolak** dengan pesan jelas |
| G3 | Durasi render ulang vs asli | **Δ ≤ 0,05 dtk** |
| G3 | Loudness | ΔI ≤ **0,5 LU**, ΔTP ≤ **0,5 dB** |
| G3 | CTA GR-2 mulai | **21,50 dtk ±1 frame**; batas segmen ±1 frame |
| G3 | Region title/CTA | luma YAVG selisih ≤ **10** |
| G3 | Kartu | berkotak (box); QC render ulang **0 FAIL** |
| G3 | `sub_voice_check` lapis A pada final asli & render ulang | **0 FAIL** |
| G3 | Waktu render | dicatat (tanpa ambang) |
| G4 | `brief_audit` AUTO vs manual | **sama item per item** |

## Yang dikembalikan ke agen
`env_report.A.json` · keluaran `selftest.py --render` · `qc_*.json` (asli + baru) · `project_gr2.json` (versi `color`) · angka render ulang (durasi, I/TP, luma, frame CTA) · `svc_*.json` · bila `--list-pauses` dicoba: keluaran + perbandingan · `ffmpeg -version` · waktu render · seluruh pesan error (salin utuh).
