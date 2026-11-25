# Clipper Ultimate

Skill produksi klip vertikal TikTok 9:16 untuk campaign clipping — dari intake brief sampai berkas final dan paket posting — dengan gerbang QC otomatis, audit brief terprogram, dan review manusia pada titik-titik yang memang butuh telinga/mata manusia. Skill ini ditulis dan divalidasi lewat produksi nyata per kelas kasus: setiap aturan bertanda **[D]** (terverifikasi di produksi), **[T]** (butuh tes), atau **[A]** (asumsi), dan klaim status per kasus hanya diajukan sejauh bukti produksinya.

Dokumen utama: [`SKILL.md`](SKILL.md) — baca itu dulu; semua resep per kasus dan skrip dirujuk dari sana.

## Status validasi per kasus

| Kasus | Isi | Status |
|---|---|---|
| K1 | Klip trailer film | Production grade |
| K2 | Materi statis + voice-over | Production grade |
| K3 | Video panjang / VOD satu pembicara | Partially validated |
| K4 | Klip dialog banyak pembicara | Partially validated |
| K5 | Klip gameplay | Production grade (n=1) |
| K6 | Modul angka (doktrin angka di kartu) | Terpakai nyata, mengikuti kasus asal |
| K7 — cabang repurpose | Footage brand dipakai ulang sesuai brief | Partially validated |
| K7 — cabang UGC | Rekam sendiri sesuai brief | **Belum tervalidasi** |

Rincian bukti, cakupan, dan daftar yang belum teruji untuk tiap klaim ada di blok STATUS `SKILL.md` dan di header tiap berkas resep di `references/`.

**Orientasi:** portrait 9:16 adalah default semua kasus. Jalur landscape 16:9 (1920×1080, 30 fps) **tervalidasi n=1** untuk K2 materi statis dari sumber landscape (F11, v0.8.0) — bukan production grade; landscape untuk kasus/sumber lain belum divalidasi. Lihat `references/K2-statis.md` bagian "Format & orientasi".

## Struktur folder

```
.
├── SKILL.md                # dokumen utama: pipeline S0–S13, lock, gerbang QC
├── changelog.md            # riwayat versi dan lipatan per fase
├── THIRD_PARTY_LICENSES.md # lisensi perangkat lunak & pustaka pihak ketiga
├── references/             # resep per kasus (K1–K8) + dokumen pendukung
├── scripts/                # perkakas Python: render, QC, audit, selftest
└── templates/              # skema brief + contoh production.json, kartu, dsb.
```

## Kebutuhan

- **Python 3** (skrip di `scripts/` — hanya pustaka standar, kecuali pemeriksa lebar teks yang memakai PIL bila tersedia).
- **ffmpeg** (render, probe, loudnorm, QC audio/video).
- **whisper.cpp** (biner `whisper-cli` + model, untuk transkripsi dan span ucapan di tahap S3).
- Untuk produksi penuh: akses ke halaman campaign yang dituju dan, bila brief memakainya, voice-over TTS.

## Menjalankan selftest

Selftest memeriksa konsistensi internal skill (rujukan, lock, dan perilaku perkakas pada kasus uji bawaan):

```bash
cd scripts
python3 selftest.py            # pemeriksaan dokumen + logika
python3 selftest.py --render   # ditambah uji render perkakas
```

## Lisensi

Kode dan dokumen di repositori ini **tidak dilisensikan** — semua hak cipta dipertahankan oleh pembuatnya; tanpa izin tertulis, orang lain tidak berhak memakai ulang, menyalin, atau menyebarluaskannya. Komponen dan pustaka pihak ketiga yang dipakai perkakasnya tunduk pada lisensi masing-masing — daftar lengkapnya ada di [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md).
