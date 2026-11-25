# K8 — Protokol revisi (proses, bukan sumber)

Tanda: **[D]** terverifikasi · **[T]** butuh tes. Status: diturunkan dari 4 iterasi GR-2 dan 2 iterasi GR-1 [D]; target kecepatan belum terbukti [T].

## Kapan
User menolak versi N (atau meminta ubahan). Berlaku di atas kasus asal (K1/K2/K3/K7…). Keputusan user mengalahkan metrik: QC otomatis PASS tidak membatalkan penolakan [D].

## Langkah
1. **Catat tiap keluhan sebagai butir terpisah** di `review-sheet.md` (kata-kata user, jangan diparafrase jauh). Satu keluhan = satu baris.
2. **Petakan butir → berkas data** yang diubah: urutan/potongan → `edl.json`; posisi crop → `crop_plan.json`; teks/timing → `cards.json`; suara/musik → blok `audio` di `project.json`; ukuran/gaya → blok `style`.
3. **Ubah data, bukan bangun ulang.** Jangan menyentuh butir yang tidak dikeluhkan.
4. **Render draft** (`render.py`) lalu `qc_all` + `sub_voice_check`.
5. **Tunjukkan diff per butir** ke user: apa yang berubah, di detik berapa, bukti frame/audio.
6. **Keluhan yang sama tidak boleh muncul di versi berikutnya** — tiap versi diperiksa terhadap seluruh butir lama (regresi).
7. Keluhan baru yang berpola → tambah ke `failure-catalog` (catatan di `production-log.md` + `evidence.md`) dan usulkan gate otomatis bila bisa.
8. G-HUMAN diulang pada tiap versi. Versi ditolak dicatat (v1, v2, …) dengan alasan.

## Setelah 2 penolakan — batas iterasi (F7-25)

Resep menetapkan maks 2 iterasi (v1 + 2 perbaikan). Bila user menolak untuk kedua kalinya:

1. **Berhenti.** Jangan render putaran ke-3 secara otomatis.
2. **Tulis laporan iterasi** (di `production-log.md` + `review-sheet.md`): diagnosis tiap penolakan (apa yang ditolak, kata-kata user, apa yang sudah diubah dan hasilnya) + opsi: (a) putaran tambahan, (b) ganti format/pendekatan, (c) tutup produksi.
3. **Putaran ke-3 dan seterusnya hanya dengan izin eksplisit user yang dicatat jamnya** (mis. "putaran tambahan atas keputusan user 10:08"). Tanpa izin tercatat, tidak ada putaran tambahan.
4. **Tiap putaran hanya mengubah satu variabel utama** (mis. hanya naskah, atau hanya re-timing — bukan naskah + timing + musik sekaligus) supaya hasilnya bisa diatribusikan ke perubahan itu. Bila satu putaran mengubah lebih dari satu variabel, catat alasannya dan akui atribusinya kabur.

Preseden: K2 Hamka memakai 4 putaran tambahan (v3–v6) di luar maks 2 iterasi, semuanya atas keputusan eksplisit user — tanpa aturan ini tercatat, putaran itu terjadi di luar resep.

## Template baris di `review-sheet.md`
`| V2-03 | "voice terpotong di detik 18" | cards.json #7 + edl potongan 4 | diubah: batas potong digeser ke jeda vokal 18,32s | frame/audio bukti | DITERIMA/DITOLAK |`

## Pola penolakan nyata → gate
| Penolakan | Gate/aturan |
|---|---|
| subtitle terlalu besar | ukuran kartu 46/54 px |
| hook bukan hook | locked #6 + G-STORY |
| tidak ada alur | beat map (K1) |
| subtitle↔voice mismatch | `sub_voice_check` |
| voice terpotong | potong di jeda vokal; cek energi audio di batas [T] |
| scene akhir terpotong | frame junction + `frame_hitam` |
| tanpa VO terasa mati (K2) | VO wajib di K2 |

## Target [T]
Diterima dalam ≤2 iterasi untuk kasus yang sudah punya resep. Bila lebih: tinjau apa yang tidak tertangkap gate dan perbaiki skill, bukan hanya klip.
