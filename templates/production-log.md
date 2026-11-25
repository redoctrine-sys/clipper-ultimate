# Production log — <ID_PRODUKSI>

Campaign: <nama> · Kasus: <K1/K2/K3/K6/K7…> · Lingkungan: A / B (langkah B dikerjakan user) · Skill versi: <x.y>

## Keputusan terkunci yang diperiksa
☐ encode sesuai `orientasi` brief: 1080×1920 (portrait, default) ATAU 1920×1080 (landscape — hanya K2 dari sumber landscape, F11; `size` project harus cocok dengan `orientasi`, qc_all --project + --brief) /30fps/H.264+AAC (bitrate = target, bukan syarat) ☐ −18 LUFS/TP −3,5 (tanpa pengecualian; konflik brief → diputuskan di G-BRIEF dan dicatat) ☐ kartu: **narasi = `prop`; dialog = manual `cards.json`** (island/words eksperimental → dikoreksi manual) ☐ teks kartu = ucapan (sub_voice_check lapis A) ☐ hook bukan kartu pernyataan ☐ freeze = frame sumber/PNG; layar hitam = segmen `color` (bukan tpad default / berkas hitam) ☐ celah kartu: tak ada tumpang-tindih; render `gte*lt` ☐ **`--cuts` = batas BEAT (bukan tiap shot)** ☐ crop diverifikasi ☐ G-HUMAN ☐ larangan AI dicek (klasifikasi tool + waiver) ☐ **manual_audit.json DIBEKUKAN bersama brief_audit.json saat G-FINAL (F8-1): salin ke folder versi + sha256 di production.json + brief_audit, chmod a-w**

## Metode timing kartu (wajib per grup)
| Grup | Jenis (narasi/dialog/ucapan alami K3) | Metode (`prop` / `manual` / `island` / `words`) | `hold` | `noise` | Dicek manusia (putar ulang)? |
|---|---|---|---|---|---|
| | | | | | |
Dialog dengan metode selain `manual` wajib kolom terakhir = ya + koreksi tercatat. K3: tiap grup per frasa-napas; `prop` hanya bila hasilnya sudah didengar ulang.

## Batas beat (`--cuts`)
<t1, t2, … dari beat map; BUKAN tiap ganti shot>

## Hanya K3 — sumber panjang → banyak klip (hapus bila bukan K3)
Sumber: <id sumber> · dasar izin: <materi campaign / lisensi terbuka / milik sendiri> · estimasi & waktu transkripsi aktual: <x> menit
| Klip | Judul | Durasi (dtk) | Timestamp sumber (in–out) | Momen (`moments.json` id) | Bukti contact sheet | Hal yang tidak ditemukan / diubah | Saran caption TikTok (berkas) |
|---|---|---|---|---|---|---|---|
| klip_1_<slug> | | | | m1 | contact_m1.png | | caption_tiktok.txt |
Momen yang diminta tetapi tidak ditemukan: <daftar + alasan>. Kuota diminta vs dihasilkan: <n>/<n>. Overlay/watermark: tidak dipakai / dipakai karena brief meminta (rujukan).

## Tool & kategori AI (wajib — dasar item larangan AI di `brief_audit`)
| Tool | Kategori (`generative` / `analytic-ml` / `none`) | Dipakai untuk |
|---|---|---|
| ffmpeg | none | render |
| whisper.cpp | analytic-ml | transkrip/span ucapan |
| OpenCV (Haar/YuNet) | analytic-ml | deteksi wajah |
| <TTS/musik/visual AI bila ada> | generative | |

## Waiver larangan AI (hanya bila brief melarang AI dan ada tool non-`none`)
| Diberikan oleh | Tanggal & jam (ISO) | Lingkup | Catatan (kata user, tanpa nama) |
|---|---|---|---|
| user | | | |
Tanpa baris yang terisi lengkap (oleh=user + tanggal + lingkup): tool `generative` = FAIL; item larangan AI tidak boleh ditandai N/A.

## Pengecualian QC yang dideklarasikan (`qc_exceptions` di `project.json`; hasil = WARN)
| Cek | Rentang | Alasan (wajib) | Disetujui user? |
|---|---|---|---|
| digital_silence / frame_hitam (hanya gelap-berkonten; hitam murni tak bisa) | | | |

## Jejak tahap
| Tahap | Waktu | Berkas/keluaran | Env | Catatan |
|---|---|---|---|---|
| S0 brief intake | | brief.json | A | |
| S1 sumber | | sources.json | A | asal & izin: |
| S2 probe | | probe.json, shots.json | A | |
| S3 transkrip | | transcript.json | A | model: , bahasa: id |
| S4 seleksi/naskah | | edl.json, naskah.txt (K3: moments.json) | A | G-STORY: |
| S5 reframe | | crop_plan.json | A | G-CROP: |
| S6–S7 audio+caption | | project.json, script_cards.json, cards.json | A | |
| S8–S9 draft + QC | | qc_report.json, svc_report.json | A | |
| S10 review | | review-sheet.md | — | versi: |
| S11 final + audit | | final.mp4, brief_audit.md | A | otomatis↔manual selaras: · **manual_audit.json DIBEKUKAN (F8-1): salinan di folder versi + sha256 tercatat di production.json + brief_audit; berkas beku chmod a-w** |
| S12 posting/submit | | posting-checklist.md | — | |

## Versi
| Versi | Hasil | Alasan penolakan (kata user) | Butir K8 |
|---|---|---|---|

## Verifikasi parent (F7-24) — SEBELUM tiap versi diserahkan ke user

Parent wajib memeriksa sendiri, dari disk — ringkasan subagent BUKAN bukti. Satu baris per versi.

| Versi | sha256 draft dicek dari disk | Path cocok dengan yang diserahkan? | qc_all + sub_voice_check dijalankan ulang (rc) | Frame QC dibuka sendiri (ya/tidak) | Oleh / tanggal-jam |
|---|---|---|---|---|---|
| V<N> | | | | | |

## Langkah PC (Skenario B) — instruksi untuk user
| Perintah dikirim | Berkas hasil diterima | Env report |
|---|---|---|

## Temuan baru → `evidence.md` / failure-catalog
-

## Waktu proses terukur (VM)
transkrip: <x> dtk/menit audio · render: <x>× realtime · stem: <x> · waktu menyusun kartu dialog manual (dengan/ tanpa `--list-pauses`): <x> menit
