# K6 — Modul angka/fakta (ditempel ke kasus lain)

Tanda: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi. Status resep: dari produksi GR-1 (verifikasi angka/teks pada materi) [D]; OCR otomatis belum ada [T].
Frekuensi: ada contoh campaign nyata (campaign finansial) [D via riset].

## Status K6 (audit K47, 23 Nov 2026)
**Resep TERPAKAI nyata, bukan sekadar draf — tetapi tidak pernah divalidasi sendirian.** K6 menempel ke kasus asal dan statusnya mengikuti kasus asal; **jangan klaim production grade untuk K6 sendiri.**
- **[D] Terpakai nyata:** GR-1/F2 (K2+K6: angka/teks di frame diverifikasi persis vs sumber; `facts.json` dipakai) · F7 K2 Hamka v1–v6 (angka dalam naskah 75–93 kata, pace 2,3–2,4 kata/dtk, VO Helio; koreksi kartu dari telinga user) · F9 k1/k6/k8 (kartu dialog: koreksi fakta/nama dari telinga user; selisih ucapan-vs-tampilan tercatat, lihat §"Ucapan vs tampilan").
- **[D] Aturan inti terbukti:** angka di layar, di ucapan, dan di sumber harus sama persis (kasus narasi K2/K6); tiap angka/fakta di kartu cocok dengan sumber; teknik naskah boleh ubah ritme/urutan, **TIDAK PERNAH ubah fakta**.
- **[T] Tetap terbuka:** OCR otomatis (Tesseract dkk.) · tabel ejaan TTS universal per jenis angka · ambang materialitas selisih HUD (kapan selisih cukup material untuk menahan G-FINAL vs cukup dicatat) · apakah angka sebagai keyword berwarna mengubah keterbacaan/retensi (tidak ada bukti; jangan klaim efek).
- **Hasil audit:** kerangka lama (facts.json + pipeline 5 langkah + QC gate) sudah benar tetapi **belum lengkap** — ia mengasumsikan layar = ucapan = sumber selalu sama, padahal bukti F9 menunjukkan ketiganya bisa berbeda. Bagian yang ditambah audit ini: aturan ucapan-vs-tampilan, angka di materi game/HUD, angka di caption TikTok, ejaan angka untuk TTS + normalisasi ASR-ganda, format tampil persis + pembulatan, kapan angka jadi keyword berwarna, dan tabel kegagalan khas dengan contoh nyata. Tidak ada aturan lama yang dihapus; yang diubah hanya penajaman (definisi "sama persis" kini dibedakan per jenis ucapan, lihat bawah).

## Definisi
Klip yang menyebut/menampilkan angka atau fakta (harga, persentase, tanggal, nama produk). **Angka di layar, di ucapan, dan di sumber harus sama persis — untuk narasi yang ditulis (K2/K6).** Untuk ucapan sumber (dialog/gameplay, K1/K3/K5) berlaku aturan ucapan-vs-tampilan di bawah: kartu mengikuti ucapan, tampilan sumber tidak diubah, selisih dicatat. Verifikasi angka/teks terhadap brief/materi sudah dilakukan di produksi nyata [D].

## Input
Materi sumber (gambar/postingan/dokumen brief) · `facts.json` yang diisi agen.

## `facts.json`
```json
[{"id":"F1","label":"CPM","nilai":"Rp10.000","satuan":"per 1.000 views","sumber":"brief hlm.1","tampil":"Rp10.000","diucapkan":"sepuluh ribu rupiah","diucapkan_pada_s":4.2}]
```
Aturan: `tampil` = format persis di layar (titik ribuan, simbol, huruf besar-kecil). Tidak ada pembulatan diam-diam.
- **Kunci baru (opsional, mundur-kompatibel):** `diucapkan` = bentuk verbatim yang diucapkan (untuk kartu dialog: kata yang benar-benar terdengar, mis. `"500"`); `ejaan_tts` = bentuk ejaan kata untuk masukan TTS (mis. `"lima ratus"` — lihat §"Ejaan angka untuk TTS"); `tampil_di` = frame/waktu sumber tempat tampilan itu terlihat (mis. `"poster hlm.1"`, `"HUD t=40.5"`); `selisih` = catatan bila ucapan ≠ tampilan (mis. `"diucapkan 500, HUD $547 — kartu mengikuti ucapan, lihat production-log"`); `pembulatan` = bila nilai dibulatkan, tulis asli + bulat + alasan (hanya sah sesudah G-HUMAN); `keyword` = `true` bila angka ini keyword berwarna (lihat §"Kapan angka jadi keyword").
- **Satu fakta = satu baris.** Jangan menggabung dua angka yang sumbernya berbeda dalam satu `F*`; tiap baris punya `sumber` sendiri (brief hlm./frame/poster).

## Format tampil persis + pembulatan/satuan [D, diperluas audit K47]
- **Salin, jangan konversi:** pemisah ribuan, simbol mata uang dan posisinya, pemisah desimal, format tanggal, dan huruf besar-kecil mengikuti sumber persis seperti terlihat di frame penuh (lock #20). Contoh: `Rp10.000` (titik ribuan Indonesia) tetap `Rp10.000`, bukan `Rp10,000` dan bukan `10 ribu`; `$547` tetap `$547`, jangan dikonversi ke rupiah; `19 November 2026` tetap begitu, bukan `19/11/2026`.
- **Satuan tidak boleh hilang atau tertukar:** `Rp` vs `ribu` vs `per 1.000 views` adalah bagian dari nilai — kartu yang menulis `10.000` tanpa `Rp` bila sumbernya `Rp10.000` = FAIL (kelas kegagalan "satuan salah" [D]).
- **Pembulatan:** dilarang diam-diam. Bila kartu tidak muat atau naskah memang membulatkan (mis. ucapan "500" untuk nilai sumber 547 — itu BUKAN pembulatan agen, itu ucapan sumber; lihat §"Ucapan vs tampilan"), pembulatan oleh agen hanya sah bila: (1) dicatat di `facts.json.pembulatan` (nilai asli + nilai bulat + alasan), dan (2) disetujui di G-HUMAN. Tanpa keduanya = FAIL.
- **Tanggal/nama di poster vs brief (keputusan user D3, F2 K2 poster 5 film):** tanggal/nama di poster yang TERLIHAT boleh diucapkan; klaim award di luar brief TIDAK boleh diucapkan; tanggal poster yang bertentangan dengan brief TIDAK diucapkan. Aturan umum: bila dua sumber bertentangan, sumber yang dipakai adalah brief — yang lain tidak diucapkan dan dicatat sebagai konflik di `brief.json` (bukan dipilih diam-diam).

## Ucapan vs tampilan — aturan pemutus [D F9, baru audit K47]
Inilah celah utama modul lama: ia mengasumsikan layar = ucapan = sumber. Bukti F9 menunjukkan ketiganya bisa berbeda, dan pemutusnya bergantung pada **jenis ucapan**:
- **(A) Narasi yang ditulis (K2/K6, VO Helio dari naskah).** Ucapan = nilai = tampil. Selisih apa pun = FAIL: perbaiki **naskah/VO** (atau `facts.json` bila sumbernya yang salah), jangan pernah perbaiki kartu sendirian. Kartu = naskah verbatim (lock #5).
- **(B) Ucapan sumber (dialog trailer, ucapan di VOD/gameplay — K1/K3/K5).** **Kartu = ucapan verbatim** (lock #5). Tampilan di dalam footage (HUD game, teks di layar sumber) adalah materi sumber yang **tidak diubah**: jangan edit footage, jangan ubah kartu agar cocok dengan tampilan. **Selisihnya dicatat** di `production-log.md` dan di review-sheet §2a sebagai catatan (bukan diperbaiki diam-diam); bila selisihnya material (harga, CPM, tanggal, nama produk) tanyakan ke user di G-HUMAN sebelum final.
- **Bukti pemutus (F9 k6, belanja sepatu, 56 dtk, 26 kartu):** kartu `"Coba gua liat uang gua 500 nih."` — angka `"500"` diucapkan, HUD game menunjukkan `$547`. User mengonfirmasi yang diucapkan `"500"`; kartu mengikuti UCAPAN, bukan HUD. Selisih `500` vs `$547` dicatat, bukan "diperbaiki" menjadi `547`.
- **Nama/brand mengikuti aturan yang sama** (fakta, bukan hanya angka): kartu `"Buy and Wear"` dikoreksi dari ASR `"Bui N-Ware X"` via telinga user; kartu `"GTA6"` (bukan `"GT6"`) dan `"gua puter"` (bukan `"gue putar"`) dari telinga user (F9 k8); `"Malaysia"`→`"Malay"` dan `"sabah/sabar"`→`"sahabat"` dari telinga user (F9 k1). Fakta/nama di kartu hanya sah dari telinga user bila ASR berselisih (F7-8/F7-23); jangan ditebak dari konteks.
- **Contoh [T] dengar yang tidak boleh ditebak:** `"dapat"` vs `"dapet"` di kartu adsense k1 — **TERJAWAB 24 Nov 2026 06:45 WIB: kata benar "dapat" (telinga user)**; kartu #5/#7 dikoreksi di v3 (final sha `e269a910…`, QC 0 FAIL). Pelajaran: chat user "gak dapat adsense" ternyata KOREKSI, bukan pengetikan kasual — asumsi v2 salah; kedua model ASR sama-sama salah dengar "dapet". Kartu dengan [T] dengar terbuka menahan G-HUMAN (lock #11, urutan F7-23: tanyakan [T] dulu, baru minta "setuju?").

## Angka di materi game/HUD [D F9, baru audit K47]
- **HUD bukan `facts.json` kecuali diucapkan/dikonfirmasi.** Angka HUD (uang, skor, level) adalah keadaan di dalam dunia game: berubah tiap frame dan bukan klaim campaign. Jangan salin angka HUD ke `facts.json` sebagai fakta hanya karena terlihat — masukkan hanya bila angka itu diucapkan, atau bila brief menjadikannya klaim (mis. harga item yang ditampilkan).
- **Bila angka HUD dibaca, baca dari frame resolusi penuh pada detik kartu itu** (lock #20): HUD di frame kecil/contact sheet tidak sah sebagai bukti. Catat `tampil_di` dengan detiknya (`"HUD t=40.5"`).
- **Jangan konversi atau bulatkan HUD:** `$547` tetap `$547` (simbol + nilai apa adanya); jangan tulis `500` "agar cocok dengan ucapan" — itu dua sumber berbeda, dan selisihnya diselesaikan oleh aturan ucapan-vs-tampilan di atas, bukan dengan mengubah salah satunya.
- **Nama di HUD/UI game** (mis. tombol/menu) mengikuti aturan nama/brand di atas: ejaan di kartu = yang diucapkan/dikonfirmasi telinga user, bukan tebakan ASR atas teks kecil di layar.

## Angka di caption TikTok [D, baru audit K47]
- **Caption bukan tempat angka baru.** Angka di `caption_tiktok.txt` harus cocok dengan video: bila merujuk angka yang tampil, sama persis dengan `tampil`; bila merujuk angka yang diucapkan, sama persis dengan `diucapkan`. Angka yang hanya ada di caption (tidak di video, tidak di `facts.json`) = FAIL di `brief_audit` — caption bukan jalan pintas menambah klaim.
- **Tanpa pembulatan diam-diam di caption juga:** bila caption menulis bentuk pendek (mis. `"500"`), bentuk itu harus sama dengan ucapan/tampil yang sudah ada — bukan pembulatan baru atas angka lain.
- **Hashtag/tag angka** (bila ada) mengikuti aturan yang sama; hashtag tidak boleh ditebak (SKILL.md S1 butir 5) — bila tidak tercantum di brief, N/A beralasan + [T].

## Ejaan angka untuk TTS + normalisasi ASR-ganda [D prosedur, baru audit K47]
- **Dua naskah, dua bentuk, satu nilai.** `naskah.txt` (bersih, untuk `sub_voice_check` lapis A) memakai bentuk digit/tampil (`"500"`, `"Rp10.000"`); masukan TTS boleh memakai bentuk ejaan kata (`"lima ratus"`, `"sepuluh ribu rupiah"`) agar Helio mengucapkannya benar. **Kartu selalu memakai bentuk digit/tampil, bukan bentuk ejaan TTS.** Pasangan digit↔ejaan dicatat di `facts.json` (`nilai` + `ejaan_tts`).
- **Verifikasi dengan mendengar take-nya** (lock #45: ukur durasi + pace tiap take TTS, pilih take yang masuk jendela): ejaan yang benar adalah yang terdengar benar di take terpilih — jangan asumsikan satu ejaan selalu dibaca benar oleh TTS. **[T]:** belum ada tabel ejaan universal per jenis angka (mata uang, persen, tanggal, tahun) yang teruji untuk Helio; tiap ejaan dicatat per produksi sampai tabel itu ada.
- **Normalisasi angka sebelum membandingkan ASR-ganda** (SKILL.md S3; diulang di sini karena K6 yang paling sering kena): ASR-1 whisper.cpp small menulis **digit** (`"500"`), ASR-2 stable-ts tiny mengeja **kata** (`"lima ratus"`). Normalisasi digit↔kata dulu — `"500"` vs `"lima ratus"` = **SEPAKAT, bukan [T]**. Tanpa normalisasi, tiap angka jadi [T] palsu. Kata yang tetap tidak sepakat sesudah normalisasi = [T], hanya telinga user yang memutus (F7-8). **Batasnya:** ASR-ganda hanya menangkap ketidaksepakatan — kata yang kedua model salah dengar dengan cara sama tetap lolos (bukti uji F8); dan [T] dengar yang tidak dikonfirmasi user (mis. `"dapat"` vs `"dapet"`) tetap terbuka, bukan ditebak.

## Pipeline (tambahan di atas kasus asal)
1. **Ekstrak** semua angka/fakta dari sumber → `facts.json` (sumber + halaman/frame).
2. **Naskah/VO**: kalimat yang memuat angka ditandai; ucapan harus sama dengan `nilai`. VO narasi (bila ada) memakai suara kanonik **Helio** (`/opt/hatch/bin/tts speak --language id --voice avocado_v2:MAI_03`, lock #45); suara lain hanya lewat override lock #45.
3. **Insert card per angka** (kartu `kind: "title"` atau kartu angka) tepat saat diucapkan; tampil ≥1,5 dtk agar terbaca [D]; waktunya dari `pause_anchor` (bukan proporsional).
4. **QC frame:** ambil frame tiap insert (`qc_all --frames-dir` + perintah `ffmpeg -ss <t> -frames:v 1`) → bandingkan dengan `facts.json`.
5. Audit: butir manual "angka sesuai sumber" di `brief.json.manual_items` dengan bukti frame.

## Durasi insert angka [D, dipertegas audit K47]
- **Kartu angka (insert per angka / kartu `kind: "title"`) tampil ≥1,5 dtk** — lantai ini lebih ketat dari lantai `prop` umum 1,0 dtk (lock #4), karena angka butuh waktu baca lebih lama; judul/kover ≥1,5–2 dtk sudah lock #7.
- Bila pembelahan `prop` menghasilkan kartu angka <1,5 dtk: perpanjang dengan menahan sesudah ucapan (lock #26 langkah 4) atau gabung dengan frasa tetangga (≤7 kata); **jangan pernah memendekkan di bawah 1,5 dtk**. Bila perpanjangan bertabrakan dengan kartu berikut atau zona panel (lock #19), produser memutuskan dan mencatatnya — jangan longgarkan ambang diam-diam (SKILL.md §2 butir 6).
- **Waktu insert dari `pause_anchor`, bukan proporsional** — onset kartu angka = onset ucapan angka itu, bukan tengah kalimat.

## Kapan angka jadi keyword berwarna [D sebagian, baru audit K47]
- **Default: angka BUKAN keyword.** Angka menjadi keyword berwarna hanya bila angka itu **inti klaim klip** (harga, CPM, tanggal tayang, angka hook) dan naskah/brief menandainya — bukan tiap angka yang lewat.
- Bila jadi keyword: maks 0–2 keyword per kartu, warna aksen **`style.accent`, default `#FFD60A`** (lock #32); pewarnaan **tidak mengubah teks/nilai** — QC angka tetap berlaku penuh pada kartu ber-keyword.
- **Jalur ASS ber-keywords masih EKSPERIMENTAL** (lock #32: kotak ASS ≠ drawtext, presisi 0,01 dtk); G-HUMAN memutuskan apakah kotak ASS diterima. Tanpa keywords → jalur drawtext lama (aman).
- Bukti terkait (F9 k6): keyword kuning dipakai untuk frasa `"attention to detail"` — keyword menandai penekanan, bukan membuktikan angka; jangan jadikan tiap angka keyword dengan alasan "biar menonjol".

## Knobs
format tampilan angka · durasi insert · posisi (`y` per kartu) · apakah angka juga muncul di caption TikTok.

## QC gate khusus K6
Untuk **setiap** `F*`: (a) frame di waktu insert menampilkan `tampil`; (b) transkrip ulang (sub_voice_check/whisper) memuat angka yang sama; (c) cocok dengan `sumber`. Gagal salah satu = FAIL. OCR otomatis (mis. Tesseract, di luar 22 repo) **belum diputuskan [T]**; sementara: agen membaca frame secara visual dan mencatat buktinya.
- **Tambahan audit K47:** (d) teks kartu = `diucapkan` verbatim (lock #5) — untuk ucapan sumber, (d) diperiksa terhadap ucapan, BUKAN terhadap tampilan; selisih ucapan-vs-tampilan yang tercatat + dikonfirmasi user (contoh k6: `500` vs HUD `$547`) = PASS dengan catatan, bukan FAIL dan bukan diperbaiki diam-diam; (e) angka di `caption_tiktok.txt` cocok dengan `tampil`/`diucapkan` (lihat §"Angka di caption TikTok"); (f) perbandingan ASR-ganda memakai angka yang sudah dinormalisasi digit↔kata (lihat §"Ejaan angka untuk TTS").
- **Audit manual "angka sesuai sumber":** butir di `brief.json.manual_items` dengan bukti frame (langkah 5 pipeline); pemeriksa menulis frame + detik + nilai yang terlihat — bukan mengulang `facts.json` dari ingatan (lock #20, #22).

## Kegagalan khas
Satuan salah (Rp vs ribu) · pembulatan · angka diucapkan beda dari yang tampil · kartu angka hilang sebelum terbaca · angka di caption TikTok beda dari video.

| Kegagalan | Contoh nyata | Pencegah |
|---|---|---|
| Satuan salah (Rp vs ribu) | kartu menulis `10.000` tanpa `Rp` padahal sumber `Rp10.000` | `tampil` persis + satuan bagian dari nilai [D] |
| Pembulatan diam-diam | nilai sumber dibulatkan di kartu/caption tanpa catatan | `facts.json.pembulatan` + G-HUMAN [D] |
| Angka diucapkan beda dari yang tampil | F9 k6: diucapkan `500`, HUD `$547` | kartu = ucapan; selisih dicatat, bukan "diperbaiki" [D] |
| Nama/brand ditebak dari ASR | `"Bui N-Ware X"` → benar `"Buy and Wear"`; `"GT6"` → benar `"GTA6"`; `"Malaysia"` → benar `"Malay"`; `"sabah/sabar"` → benar `"sahabat"` | hanya telinga user yang memutus bila ASR berselisih [D F9] |
| [T] dengar ditebak diam-diam | `"dapat"` vs `"dapet"` (k1 adsense) TERJAWAB 24 Nov 2026 — "dapat" | dikoreksi di v3; pelajaran: jangan asumsikan chat user sebagai pengetikan kasual [D] |
| Klaim di luar brief diucapkan | klaim award di luar brief (F2 K2 poster 5 film) | hanya yang di brief/sumber yang diucapkan [D] |
| Tanggal bertentangan diucapkan | tanggal poster bertentangan dengan brief (F2 K2) | tanggal yang bertentangan TIDAK diucapkan [D] |
| Kartu angka hilang sebelum terbaca | insert <1,5 dtk | lantai 1,5 dtk + tahan sesudah ucapan [D] |
| Angka di caption beda dari video | angka baru hanya muncul di caption | caption = `tampil`/`diucapkan`; angka baru = FAIL [D] |
| Angka ASR-ganda jadi [T] palsu | small `"500"` vs stable-ts `"lima ratus"` | normalisasi digit↔kata sebelum banding [D] |
| HUD dijadikan fakta | angka HUD disalin ke `facts.json` tanpa diucapkan | HUD bukan fakta kecuali diucapkan/diklaim brief [D] |
| OCR otomatis diasumsikan ada | — | OCR tetap [T]; agen baca frame visual + catat bukti |

## Lingkungan
A penuh; tidak butuh key/GPU.
