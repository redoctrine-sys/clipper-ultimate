# Serah materi — template manifest + protokol (S1, F8.4)

Dipakai di G-BRIEF, sebelum produksi dimulai. Satu baris per materi yang dibutuhkan.
Sumber pengecekan klasifikasi publik: 23 Nov 2026 12:30–12:32 WIB, dari VM tanpa login —
halaman daftar campaign konten.com + halaman detail campaign + halaman /brief beserta daftar
"Materi yang tersedia" semuanya terbuka. Di balik login HANYA paket ALL MATERI (Drive) dan
materi yang link Drive-nya dibatasi.

## 1. Manifest kebutuhan (G-BRIEF)

| # | Materi | Sumber menurut brief | Wajib / opsional | Alasan |
|---|---|---|---|---|
| 1 | | | | |

## 2. Klasifikasi jangkauan — cek BERURUTAN, dari yang paling mudah

| Jalur | Cara cek | Bila berhasil | Bila gagal |
|---|---|---|---|
| **A. Publik VM** | Unduh langsung dari VM (curl / yt-dlp / fetch halaman) | Tersedia — catat URL + sha256 + hasil probe ke `sources.json` | Lanjut jalur B/C |
| **B. Halaman campaign + brief konten.com = PUBLIK** | Buka halaman daftar campaign, halaman detail campaign, lalu halaman `/brief` beserta daftar "Materi yang tersedia" — semuanya bisa dijangkau VM **tanpa login** (dicek 23 Nov 2026 12:30–12:32) | Tersedia — ambil dari halaman publik, **tanpa serah user** | Bila satu halaman saja meminta login, catat URL + jamnya; lanjut jalur D |
| **C. YouTube (bot-block intermiten, F7-13)** | (1) yt-dlp default → (2) `player_client=android` → (3) ulang nanti (jam/hari lain). Catat semua ID kandidat + status verifikasinya (sama/beda/belum) — jangan pakai ID yang belum terverifikasi | Tersedia — catat ID + sha256 | Setelah (3) masih gagal → [T] rute browser/PC user, atau pakai materi pengganti resmi (lihat F7-1) |
| **D. ALL MATERI (Drive) = serah user** | Paket ALL MATERI seperti 3726/Hamka + materi yang link Drive-nya dibatasi = di balik login | — | **Serah user** (§3). JANGAN tulis "dashboard konten.com → selalu serah user" — hanya paket/file di balik login yang diserah |
| **E. VO / AI Studio** | Produksi default memakai Helio (`/opt/hatch/bin/tts`, tanpa browser) — **tidak butuh serah VO**. Serah file VO dari user hanya diperlukan bila produksi memakai override suara non-Helio yang butuh browser (lock #45) | Tanpa serah | Serah file VO (§3) + catat override di `production.json` |

## 3. Format serah (bila jalur D/E)

- User meletakkan file di **folder serah** yang disepakati atau di **Project** (Claude).
- Agen mencatat per file: nama, **sha256 dari disk**, hasil probe (durasi/resolusi/format) → `sources.json`.
- Bila file tidak bisa diprobe (format aneh), catat alasannya — jangan diam-diam memakai file yang belum diprobe.

## 4. Status per item

| Status | Arti | Dicatat di |
|---|---|---|
| Tersedia | Didapat lewat jalur A/B/C + sha256 tercatat | `sources.json` |
| Deviasi | Sumber dipakai ≠ sumber brief (mis. teaser, bukan trailer utama) | Field `deviasi_sumber` di `brief.json` (sumber_brief + sumber_dipakai + alasan + dampak) |
| N/A beralasan + [T] | Item tidak tersedia / tidak tercantum, dengan alasan + pertanyaan terbuka ke user | Butir audit terkait + review-sheet |

## 5. Aturan "jangan tebak"

- **Hashtag tidak boleh ditebak (F7-17).** Bila hashtag wajib tidak tercantum di halaman publik, tetapkan N/A beralasan + [T] — jangan karang hashtag.
- **Bumper tidak ada → end card sementara (F7-3).** Bila bumper ending resmi tidak ada di sumber mana pun, pakai frame sumber (mis. kartu tanggal tayang) sebagai end card sementara + butir audit terkait = N/A beralasan.
- **Sumber yang 403 jangan diulang** (F7-16, TMDB). Catat sebagai "jangan diulang", bukan "coba lagi".

## 6. Label klip

- **Valid sebagai tes** — klip boleh dinilai/diuji walau ada item berstatus deviasi / N/A beralasan.
- **Valid sebagai submission** — hanya bila SEMUA item wajib berstatus tersedia. Selama ada item wajib yang deviasi/N/A, klip tetap "tes internal" dan tidak boleh disubmit/diposting sebagai submission.

## 7. Dry-run dokumen — kasus F7 (6/6)

| Kasus | Langkah protokol | Keluaran |
|---|---|---|
| F7-1 — trailer utama 3726 bot-blocked | Jalur C: default gagal → `player_client=android` gagal → [T]. Fallback resmi: teaser kanal yang sama boleh dipakai untuk tes internal, dengan deviasi tercatat | Teaser dipakai; deviasi di `brief.json` (`deviasi_sumber`); label "valid sebagai tes" |
| F7-2 — sumber K1 = teaser, bukan Trailer Hero/Utama | Jalur B: brief + daftar materi diambil dari halaman publik (tanpa serah); sumber yang dipakai menyimpang dari daftar brief | **Diambil dari halaman publik, tanpa serah**; deviasi di `brief.json` (`deviasi_sumber`) |
| F7-3 — bumper ending resmi tidak ada di teaser | §5: end card sementara dari frame sumber ("3 DESEMBER DI BIOSKOP") | Butir bumper = N/A beralasan; label "valid sebagai tes" |
| F7-13 — trailer Hamka bot-blocked; ID lain belum terverifikasi | Jalur C: catat semua ID kandidat + status verifikasi (sama/beda/belum); coba ulang nanti (bot-block intermiten) | ID terverifikasi dicatat; ID belum terverifikasi tidak dipakai |
| F7-17 — hashtag wajib Hamka tidak tercantum di halaman publik | §5: jangan tebak hashtag | Caption tanpa hashtag; butir hashtag = N/A beralasan + [T] |
| F7-14 — rute TTS resep (Gemini Charon via AI Studio) tidak bisa dijalankan agen VM | Jalur E: produksi default memakai Helio, tanpa browser | **Jalur default, tanpa serah** (Helio kini jalur utama, keputusan user U1 23 Nov 2026) |
