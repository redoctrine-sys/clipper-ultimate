# Review sheet (G-HUMAN) — <ID_PRODUKSI> · versi V<N>

Diisi agen sebelum diberikan ke user; user mengisi kolom keputusan. **Tidak ada status "selesai" tanpa persetujuan eksplisit user.**

## 1. Paket yang ditunjukkan
- File draft/final: `<nama>.mp4` (durasi `<..>` dtk) · frame bukti: `qc_frames/`
- Hasil otomatis: `qc_report.json` (FAIL = <n>), `svc_report.json` (FAIL = <n>)
- Ringkasan cerita 1 kalimat dari 10 dtk pertama (premis): "<...>"
- Hook (detik berapa, apa): "<...>"

## 2. Pertanyaan untuk user (jawab ya/tidak + catatan)
| # | Pertanyaan | Jawaban |
|---|---|---|
| 1 | Hook terasa seperti hook (pertanyaan/momen dari cerita), bukan kartu pernyataan? | |
| 2 | Premis (tentang apa) jelas dalam ±10 dtk pertama? | |
| 3 | Ukuran & posisi subtitle nyaman; tidak menutupi objek kunci? | |
| 4 | Teks kartu sama dengan yang diucapkan? | |
| 5 | Tiap kartu judul/kover sempat terbaca? | |
| 6 | Tidak ada suara/adegan terpotong; scene akhir utuh? | |
| 7 | Crop/komposisi tidak terlihat tempelan; wajah/objek tidak terpotong? | |
| 8 | Angka/teks di layar benar (jika ada)? | |

### 2b. Tambahan untuk K3 (klip highlight dari video panjang) — hapus bila bukan K3
| # | Pertanyaan | Jawaban |
|---|---|---|
| K3-1 | Detik pertama sudah momen/kalimat kuat dari sumber (tanpa pemanasan)? | |
| K3-2 | Klip berakhir di pikiran utuh/punchline, tidak menggantung? | |
| K3-3 | Gambar sesuai dengan yang diucapkan (cek contact sheet `moments.json`)? | |
| K3-4 | Tidak ada jendela aplikasi lain, info pribadi, atau konten eksplisit tersisa di layar? | |
| K3-5 | Caption mengikuti napas/jeda pembicara (tidak mendahului atau terlambat)? | |
| K3-6 | Kata kunci berwarna (bila sudah dirender) jatuh di kata yang tepat? Jika belum dirender: tandai "belum berlaku" | |
| K3-7 | Tidak ada watermark/judul permanen/logo kecuali brief memintanya? | |
| K3-8 | Momen yang diminta tetapi tidak ada di sumber sudah dilaporkan (bukan dipalsukan)? | |

## 2a. Pertanyaan dengar [T] — DIISI DULU, DI ATAS KOLOM PERSETUJUAN (F7-23, lock #11)

Verifikasi ASR-ganda (S3, F7-8 + F7-6): 2 model ASR berbeda; kata yang tidak disepakati = [T],
dilarang ditebak dari konteks (bukti K1 v1: 2 dari 4 tebakan konteks ternyata salah).
Tulis tiap kata [T] di sini beserta detiknya. **Persetujuan di §5 TIDAK SAH selama ada baris
berstatus TERBUKA di bawah ini** — agen menanyakan [T] dulu, baru meminta "setuju?".
`brief_audit.py --review-sheet` membaca tabel ini: baris TERBUKA = PENDING (G-FINAL tertahan).
Status diisi produser dari jawaban telinga user: `TERTUTUP — <putusan>` / `DIJAWAB — <putusan>`.
Bila tidak ada kata [T]: hapus tabel, tulis "Tidak ada pertanyaan dengar — kedua ASR sepakat."

| # | Detik | Kata yang didengar (ASR 1) | ASR 2 mendengar | Pertanyaan | Putusan telinga user | Status |
|---|---|---|---|---|---|---|
| 1 | | | | | | TERBUKA |

## 3. Butir keluhan (K8) — satu baris per keluhan
| ID | Kata-kata user | Berkas data yang diubah | Perubahan (detik, bukti) | Status |
|---|---|---|---|---|
| V<N>-01 | | | | |

## 4. Regresi
Butir dari versi sebelumnya yang diperiksa ulang: <daftar ID> — semua tetap terselesaikan? ya/tidak.

## 5. Keputusan
☐ DISETUJUI (lanjut S11) ☐ DITOLAK (kembali ke K8) — oleh: user · tanggal/jam: <..>
