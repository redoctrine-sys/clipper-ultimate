# K3 — Video panjang, 1 pembicara → klip highlight

Tanda: **[D]** terverifikasi · **[T]** butuh tes · **[A]** asumsi.
**Orientasi: landscape belum divalidasi [T]** — resep ini portrait 9:16; jalur landscape tervalidasi n=1 hanya untuk K2 materi statis dari sumber landscape (F11, v0.8.0; lihat `K2-statis.md`).

**STATUS: Tervalidasi sebagian [D n=1, F9, 23 Nov 2026] — BUKAN "production grade" penuh.** Yang tervalidasi [D n=1]: teknik VOD (§15) + gerbang produksi (V1/V2/V4/V5/V6, P1–P3, C1, C2). Yang BELUM: timing caption `prop` pada ucapan alami — berstatus [T] di semua kelas (koreksi pasca-review Opus FINAL F9, 24 Nov 2026). V1/V2/V4/V5/V6, P1–P3, C1, C2 terukur lulus pada satu VOD nyata (Windah Basudara GTA VI, 3 klip, G-FINAL lulus 23 Nov 2026 22:49 WIB). **V3 TIDAK DIUKUR** — dilewati atas keputusan user 23 Nov 2026 23:12 WIB (beban penandaan 42 batas terlalu besar; keadaan sekarang sudah cukup bagus); status V3 bukan lolos, bukan gagal. Konsekuensi: klaim "K3 production-grade (n=1)" **tidak** diajukan; timing `prop` pada ucapan alami tetap mengandung satu known limitation terbuka (F9-19, §7). Tidak ada contoh campaign K3 nyata dan tidak ada final lama untuk dibandingkan (bukan golden). Komponen yang dipakai ulang dari K1/K2 terbukti; **yang spesifik K3 di luar cakupan [D n=1] di atas tetap [T]** (mis. pencarian momen di luar jalur §15, timing caption pada ucapan alami, crop wajah pembicara). **Jangan mengklaim "production grade" K3** sebelum validasi K3 (§11) lulus dengan materi nyata + review user.
Frekuensi di campaign nyata: belum ada contoh [D via riset].
Asal metode: sebagian ide (rubrik momen, verifikasi gambar vs transkrip, kata kunci berwarna, laporan per klip) didistilasi dari sebuah skill luar berlisensi tidak diketahui; **tidak ada teks/kode yang disalin**, ditulis ulang dan dipasangkan ke gate skill ini (lihat `THIRD_PARTY_LICENSES.md`).

## 1. Definisi & input
Satu sumber panjang (VOD, podcast video, wawancara, siaran ulang) dengan **satu pembicara dominan** → N klip vertikal 9:16 (default 20–60 dtk, ikuti `duration` brief). Dua pembicara atau lebih → K4 (`K4-dialog.md`, TERVALIDASI SEBAGIAN (F5)).
Input: tautan/berkas sumber **yang diizinkan brief** · (opsional) daftar timestamp/poin dari user · jumlah klip · durasi · bahasa · larangan (AI? reupload? "sensitive branding"?) · apakah overlay diizinkan (default: **tidak**).

## 2. Keputusan terkunci yang berlaku (ringkas; sumber: SKILL.md §3)
| Hal | K3 |
|---|---|
| Format | 1080×1920, 30 fps, H.264+AAC (**tidak ada varian horizontal**) |
| Loudness | **−18 LUFS, TP −3,5**, tanpa pengecualian. *Konflik yang diputuskan:* skill luar memakai −14 s/d −16 LUFS; **ditolak** karena −18 diterima user di dua campaign nyata dan tidak ada brief yang pernah menyebut loudness. Bila suatu brief kelak menyebut angka lain → konflik per-proyek, diputuskan user di G-BRIEF dan dicatat (bukan override otomatis; lock #3 tidak diubah) |
| Teks kartu | dari **naskah yang dikoreksi** (§6), bukan transkrip mentah (lock #5) |
| Timing | grup `prop` per frasa-napas atau `manual` (§7); `island`/`words` eksperimental |
| Hook | momen/pertanyaan dari sumber itu sendiri (lock #6) |
| Overlay | judul permanen / watermark / logo **TIDAK masuk K3 v1**; opsional per-brief, baru dikerjakan bila ada brief yang memintanya |
| Kartu berwarna | lihat §8 |
| Crop | diverifikasi visual di frame lebar penuh (lock #10) |

## 3. Pipeline K3
S0–S3 dikerjakan **sekali per sumber**; S4–S13 **satu folder produksi per klip** (`klip_<n>_<slug>/`), masing-masing dengan G-STORY, G-CROP, G-HUMAN, `brief_audit`, dan `production-log` sendiri. `transcript.json`, `probe.json`, `shots.json`, `moments.json` hidup di folder sumber dan dirujuk tiap klip.

| Tahap | Isi K3 | Keluaran | Gate |
|---|---|---|---|
| S0 | `brief.json` + keputusan K3 (jumlah klip, durasi, overlay diizinkan? ada konflik loudness?) | `brief.json` | **G-BRIEF** |
| S1 | Akuisisi sumber (§4) | `sources.json`, `source.mp4` | asal = materi campaign/diizinkan brief |
| S2 | Probe + `shots.json` + **contact sheet** sumber (§5) | `probe.json`, `contact_*.png` | — |
| S3 | Transkripsi whisper.cpp (§9) | `transcript.json` | bahasa benar (`-l id`) |
| S4 | Pilih momen (§5) → naskah klip (§6) → batas beat | `moments.json`, `naskah.txt`, `edl.json` | **G-STORY** |
| S5 | Crop wajah 9:16 (§10) | `crop_plan.json` + preview | **G-CROP** |
| S6 | Audio: sumber sebagai role `source`; (musik/VO tambahan hanya bila brief mengizinkan) | blok `audio` | — |
| S7 | Caption (§7, §8) | `cards.json` | `kartu_lint` + dengar ulang |
| S8–S13 | Render (preflight) → QC → review → final + audit → posting → log | seperti pipeline universal | G-AUTO, G-HUMAN, G-FINAL |

## 4. S1 — akuisisi sumber
- Sumber hanya dari yang **diizinkan brief** (campaign sering melarang reupload; periksa `prohibitions.reupload` dan `footage.allowed_sources`).
- Tautan web: `yt-dlp` sebagai program eksternal (README yt-dlp: ffmpeg wajib; dukungan YouTube penuh butuh komponen tambahan dan runtime JS [D]). **Akses jaringan YouTube dari VM belum teruji [T #9]**; bila gagal → minta user mengunduh dan mengunggah berkas. Sumber panjang bisa diambil sebagian (`--download-sections`) bila poin waktu diketahui [D].
- Tautan privat/anggota-saja/butuh login: **berhenti dan minta berkas dari user** (lock #13: login/OAuth/cookie dikerjakan user).
- Catat asal + izin di `sources.json`.

## 5. S2/S4 — pencarian momen + verifikasi visual
**Rubrik momen (ditulis ulang; skor 0–2 per butir, dicatat di `moments.json`):**
| Butir | Pertanyaan |
|---|---|
| Hook | Apakah 1–2 detik pertama sudah berupa pertanyaan/pernyataan kuat/kejutan dari sumber, tanpa pemanasan? |
| Pernyataan kuat | Ada opini tajam, klaim berani, atau sudut pandang tidak biasa? |
| Kejutan/pengungkapan | Ada fakta, angka, atau pembalikan yang membuat orang berhenti menggulir? |
| Emosi | Tawa, marah, haru, konflik? |
| Utuh | Apakah gagasan **selesai** di akhir klip (punchline atau pikiran lengkap), dan tidak bergantung pada konteks sebelum klip? |
| Layak tayang | Aman terhadap larangan brief; tidak ada info pribadi, konten eksplisit, atau jendela/overlay di luar topik di layar |
Skor ini penilaian agen (tidak ada skrip skor otomatis: heuristik "kejutan/tawa" tidak bisa diuji jujur). Total kecil → jangan dipilih; lebih baik melapor "hanya N momen layak" daripada mengisi kuota.

**Cara memilih:**
1. User memberi poin/timestamp → petakan tiap poin ke transkrip (segmen kalimat cukup untuk *mencari*) → tentukan awal dan akhir persis dengan mendengar.
2. Tanpa poin ("cari sendiri") → baca transkrip, shortlist 2–3× kuota, beri skor, pilih terbaik; urutan akhir = skor, bukan urutan waktu.
3. **Momen yang diminta user tidak ada / ada di timestamp lain → laporkan apa adanya.** Jangan memalsukan atau menyambung potongan agar terlihat ada.

**Verifikasi gambar vs transkrip (WAJIB di G-STORY):**
- Buat contact sheet jendela momen (mis. 1 frame tiap 2 detik, kisi 6×N; ffmpeg `fps`, `scale`, `tile`) dan **lihat**. Cocokkan: pembicara memang terlihat/menyebut hal itu, tidak ada pergantian layar yang membuat klaim transkrip salah, tidak ada jendela aplikasi lain/info pribadi/konten eksplisit.
- Catat frame bukti di `moments.json` (`verifikasi_visual`). Tanpa bukti → momen tidak boleh lolos G-STORY.
- Wilayah bermasalah di layar: **v1 = hindari lewat crop atau potongan lain**. Blur wilayah = fitur render [T], ditunda.

## 6. Naskah klip (dasar teks kartu)
- Transkrip whisper adalah **draf**. Naskah klip = transkrip yang **dikoreksi sambil didengar** (nama, istilah, bahasa informal; whisper terbukti salah dengar: "Suli"→"sulit", "Rp" hilang [D ronde 2–3]). Disimpan di `naskah.txt`.
- Glosarium nama/istilah dikumpulkan dari brief + sumber; whisper-cli `--prompt` untuk glosarium = [T]. **Terukur F9.6 (k1): netral — tidak direkomendasikan sebagai default** (lihat §15.4).
- Kartu dibelah per frasa. Target gaya K3: **2–5 kata per kartu** (batas lint tetap 2–7, lock #4). Bahasa campur/informal dipertahankan persis seperti diucapkan.
- Bagian ucapan yang tidak disertakan (jeda panjang, "eh/anu" yang dipotong di edit) tidak masuk naskah klip.

## 7. S7 — timing caption (bagian paling berisiko, [T])
Pembicara tunggal mirip narasi, tetapi ucapan alami: tempo bervariasi, jeda tak teratur, kadang ada musik/latar. `prop` terbukti hanya pada VO TTS bersih (GR-1); pada ucapan alami **belum**.
**Aturan:**
1. Bagi tiap klip menjadi **grup per frasa-napas**: satu grup = ucapan di antara dua jeda nyata. Cari kandidat jeda: `pause_anchor.py --list-pauses <sumber> --src-in <t> --dur <d> --offset <o>`; **pilih dengan mendengar**.
2. Grup pendek (±1–3 kartu) → `timing: prop` dengan `audio` + `src_in` + `dur` + `offset` (silencedetect noise −50 dB; `hold` per grup default 0). Grup pendek membatasi drift proporsional.
3. Ada musik/latar ramai/tawa penonton atau hasil `prop` meleset saat didengar → **jalur manual** (`cards.json` eksplisit, celah 0,04, seperti dialog K1).
4. Tulis metode tiap grup di `production-log.md` (kolom metode timing).
5. Dilarang: timestamp kata whisper mentah untuk caption; `island`/`words` tanpa koreksi manual + G-HUMAN.
6. `--cuts` = **batas beat** klip (mis. pergantian ide/poin), bukan tiap pindah shot kamera (lock #17).
7. **Presisi `prop` pada ucapan alami vs word-level [T — BELUM TERUKUR, V3 dilewati; koreksi pasca-review Opus FINAL F9, 24 Nov 2026]:** batas internal grup `prop` BISA jatuh di tengah kata pada ucapan tanpa jeda — Δ vs word-level (whisper small `-ml 1 -sow`): k1 **2/14 batas >0,10 dtk, maks 0,122 dtk**; k6 **5/11 batas >0,10 dtk, maks 0,480 dtk**, tetapi 2 dari 5 itu artefak kuantisasi word-level (F9-22) sehingga Δ vs word-level adalah **BATAS ATAS**, bukan galat `prop` itu sendiri. Batas luar grup (awal/akhir ucapan) tepat: k1 Δ=0,000 dtk semua; k6 maks 0,090 dtk. **Koreksi status: label lama "[D n=1]" DICABUT** — batas atas yang LEBIH BESAR dari ambang 0,10 dtk tidak membuktikan lulus; artinya hanya "belum diketahui". Timing `prop` berstatus **[T] di semua kelas** (k1, k6, maupun k8) sampai V3 terukur dengan jeda bertanda manusia. Ini bukan kegagalan gate (`kartu_lint` + lapis A lolos di ketiga klip F9.8); presisi `prop` pada ucapan tanpa jeda dicatat apa adanya, bukan disembunyikan.
8. **Aturan jepit `pause_anchor` [D n=1, F9-16]:** bila kartu terakhir grup dijepit 0,04 dtk oleh grup berikut yang mulai tepat di batas kalimat tanpa jeda (ucapan kontinu) dan durasi hasil jepit **<1,0 dtk**, **pindahkan batas kata antar-kartu** (belah ulang dua kartu yang bersebelahan) — **jangan longgarkan lantai 0,9667 dtk** (`kartu_lint`). Bukti k1: kartu "Ah serius." 0,960 dtk setelah jepit → dibelah ulang menjadi "Itu tandanya lu rakus duit" / "bang. Ah serius.", hasil 1,088 dtk.
9. **Known limitation TERBUKA [T, F9-19 — bukan [D]]:** `prop` meleset jauh pada grup bertempo tidak merata. Bukti k8 (satu-satunya pengukuran): **5/5 batas internal >0,10 dtk (0,422 / 0,302 / 0,332 / 0,691 / 0,139)**, vs k1 maks 0,122 dtk. **Generalisasi mekanisme (koreksi pasca-review Opus FINAL F9, 24 Nov 2026):** `prop` membagi waktu grup menurut **proporsi karakter** — jadi SETIAP grup bertempo tidak merata / berhening internal akan meleset, bukan khas kelas-k8: k1 sudah 2/14 batas >0,10 dtk dan k6 5/11, hanya lebih kecil karena temponya lebih merata; k8 bukan kelas khusus, melainkan ujung spektrum yang sama. Dua penyebab terukur: (a) tempo tidak merata di dalam grup — frasa pertama lambat, kedua cepat (G8: "Sampah lu gak nyalain lagu" 3,0 dtk vs "Youtuber lain…" 2,0 dtk, porsi karakter 26:30 ≈ setara → kartu 11 berakhir 0,69 dtk sebelum kata "lagu" selesai); (b) hening internal ~1 dtk di dalam satu grup ("kenapa ya?" lalu jeda lalu "lu ngecewain…") menggeser belahan proporsional 0,54 dtk lebih awal. **Jalur caption manual yang diusulkan [T] (belum divalidasi, bukan [D]):** pakai timing manual (bukan `prop`) untuk grup yang memenuhi salah satu pemicu — **tempo tidak merata di dalam grup** (terdengar/terukur dari word-level: porsi durasi frasa jauh dari porsi karakternya) atau **hening internal ≥~1 dtk dalam satu grup**. **Kandidat perbaikan untuk diuji [T]: pause-snap** — geser batas kartu ke hening internal terdekat yang terdeteksi VAD (`silencedetect`) sebelum memakai `prop` untuk sisa grup; bila tidak ada hening internal, pakai jalur manual. Ambang V3 (0,10 dtk) **tidak** dilonggarkan untuk "meloloskan" temuan ini. V3 yang akan memutus `prop` vs manual pada grup seperti ini belum diukur (dilewati atas keputusan user, 23 Nov 2026).

## 8. Kata kunci berwarna (statis per kartu)
- Keputusan Richy: **default ON untuk klip highlight K3**, **statis per kartu** (satu atau dua kata kunci diwarnai sepanjang kartu tampil). **Tidak pernah karaoke per kata** (butuh timestamp kata whisper yang tidak bisa diandalkan).
- Tiap kartu boleh punya `keywords: ["kata", ...]` (subset kata kartu; 0–2 kata) di `cards.json`. Pilihan kata kunci dicatat dan dicek G-HUMAN ("warna jatuh di kata yang benar?").
- **Rendering warna memakai jalur caption ASS di `render.py` v5-F6** (F6-C, `LAPORAN_F6_K3.md`): bila ada kartu ber-`keywords`, SEMUA kartu dirender lewat satu filter ASS (`work/captions.ass`); kata kunci diwarnai aksen `style.accent` (**default `#FFD60A`** — kunci baru; resep DRAF tidak mendefinisikan warna aksen, celah ak). Tanpa `keywords` di kartu mana pun → jalur drawtext lama (`--print` identik v4.2). **EKSPERIMENTAL — belum aman produksi:** jalur ber-`keywords` ini belum boleh dipakai untuk produksi sampai celah aj selesai dan ada tes escaping karakter `{ } \` pada teks kartu (celah baru ao, [T] validasi K3; LAPORAN_F6 §7 #25–#29). Kata kunci berwarna "aktif" sejak v5 lulus uji sintetis — G-HUMAN memutuskan apakah kotak ASS diterima per klip.
- **Batasan yang diketahui (celah aj/al/am):** kotak ASS ≠ kotak drawtext — padding ~7 px (bukan `boxborderw` 20), selalu hitam pekat (alfa `BackColour` diabaikan libass build ini), dan digambar **per baris** (bukan satu blok); ASS tidak mengenal `line_spacing` — baris ke-2 ~8 px lebih rapat; presisi waktu ASS 0,01 dtk (maks 5 ms dari interval kartu, < 1 frame). Teks (posisi, ukuran, warna, timing) menyamai drawtext dalam ±2 px (1 baris).
- Warna aksen mengikuti brief/gaya proyek; satu warna per proyek; kontras terhadap kotak kartu dicek (G-HUMAN).

## 9. S3 — transkripsi & routing (Skenario A, VM)
- `whisper-cli -m ggml-small.bin -f a16.wav -l id -nf -oj` (WAV 16-bit 16 kHz mono; `-l` default `en` [D]). Kecepatan terukur: **RTF 0,975** (F9.0, n=1, sampel 297 dtk campuran narasi/trailer/dialog; wall 289,7 dtk) → **VOD 5 jam penuh ≈ 4,9 jam** transkripsi. **Catatan estimasi (koreksi pasca-review Opus FINAL F9, 24 Nov 2026):** rata-rata RTF per chunk F9.6 ≈ **1,04** (rentang 0,72–1,43, §15.4) lebih representatif daripada sampel tunggal F9.0 0,975 — VOD 5 jam ≈ **5,2 jam** (rentang 3,6–7,1 jam). Angka 0,975 tetap tercatat di atas; pakai 1,04 (rentang 0,72–1,43) untuk estimasi waktu dinding. **Angka lama "±0,51× realtime → 1 jam sumber ≈ 2 jam" (terukur ronde 3) TIDAK terulang dan DIHAPUS dari resep** — yang berlaku angka ukur terbaru; rencana F9.6 "optimistik 0,51×" (≈11 menit untuk 22 menit audio) juga tidak terulang (RTF 0,975 memberi ≈21 menit). Opsi transkripsi penuh di VM **DIHAPUS** — sumber >20 menit dikerjakan lewat jalur §15 (sinyal → potongan → transkrip per potongan), dan transkripsi penuh hanya dengan izin eksplisit user + estimasi waktu dinding dari RTF terukur terbaru (lock #46 [D n=1]).
- Bila user memberi timestamp/poin: transkripsi **hanya jendela ±60 dtk** di sekitar tiap poin (ekstrak dengan `ffmpeg -ss/-t`).
- "Cari sendiri" dan sumber > 20 menit: **sebut estimasi waktu ke user dulu**, tawarkan: (a) jalur §15 (sinyal → potongan → transkrip per potongan), (b) user menjalankan transkripsi di PC GPU (instruksi manual, [T]), (c) user memberi daftar poin.
- Hasil = segmen kalimat (bukan word-level) → cukup untuk pencarian; jangan dipakai sebagai teks kartu.
- **Serialkan ASR berat antar produksi paralel [D n=1, F9-18]:** whisper.cpp small melambat ~10× saat dua produksi klip berjalan paralel di VM (k8: kalimat RTF 10,6 / kata-level RTF 13,1, vs k1 RTF 1,08 dan F9.0 RTF 0,975 pada VM yang sama; load average 5,63 pada 1,5 vCPU + proses whisper k6 terlihat bersamaan; CPU time k8 hanya ~0,77 core rata-rata — kelaparan CPU, bukan lambat sendiri). Jalankan job ASR berat berurutan, atau terima wall time ~10×.
- Detail lingkungan: `lingkungan-dan-routing.md`.

## 10. S5 — crop wajah pembicara
- Default K3: crop 9:16 yang mengikuti pembicara (deteksi wajah Haar/YuNet → rencana crop; verifikasi **tiap shot** di frame lebar penuh; lock #10, Haar pernah salah 3 dari 12 shot [D]). Pan linear `{from,to}` untuk pembicara bergerak; stabilisasi (Norfair) opsional [T].
- Pembicara tidak terdeteksi / layar berbagi / slide: mode `fit` atau `blurpad` (di tengah, ruang atas-bawah dipakai caption); tanyakan G-CROP bila ragu.
- Wajah terpotong, mata di luar, atau crop meloncat → perbaiki sebelum render.

## 11. Validasi K3 (pengganti golden; dijalankan di F9; hasil di bawah tabel)
Materi F9 (23 Nov 2026): VOD Windah Basudara GTA VI — hasil di bawah tabel.
Kriteria — **DIKUNCI sebelum uji, tidak berubah selama uji**:
| # | Kriteria | Ambang |
|---|---|---|
| V1 | 2–3 klip dari satu sumber, semua lolos `qc_all` | **0 FAIL** (WARN beralasan) |
| V2 | `sub_voice_check` lapis A | **0 FAIL** |
| V3 | Caption per frasa-napas vs jeda yang ditandai manusia (±60 dtk ucapan) | maks Δ start/end **≤ 0,10 dtk** |
| V4 | `moments.json` | lengkap: skor rubrik, alasan, **bukti contact sheet** tiap klip, momen yang tidak ditemukan dilaporkan |
| V5 | G-HUMAN | disetujui user dalam **≤ 2 iterasi** |
| V6 | `brief_audit` | 0 FAIL, 0 PENDING |
Lulus → klaim production grade **hanya untuk K3**. Gagal → perbaiki resep (bukan ambang). Tidak ada kriteria pengganti yang dilonggarkan.

**Status hasil validasi F9 (23 Nov 2026, VOD Windah GTA VI, n=1):** V1 LULUS (3 klip, qc_all 0 FAIL tiap klip) · V2 LULUS (sub_voice_check lapis A 0 FAIL: 15/15 + 26/26 + 16/16) · **V3 TIDAK DIUKUR** (dilewati atas keputusan user 23 Nov 2026 23:12 WIB — beban penandaan 42 batas terlalu besar; bukan lolos, bukan gagal) · V4 LULUS (`moments.json` lengkap, contact sheet diverifikasi parent) · V5 LULUS (ketiga klip disetujui user apa adanya 22:44 WIB, ≤2 iterasi, tanpa [T] terbuka) · V6 LULUS (brief_audit 11 PASS / 0 FAIL / 1 N/A / 0 PENDING tiap klip). P1–P3 LULUS, C1 tertutup (tes regresi), C2 diputuskan di G-HUMAN (kotak ASS diterima). **K3 = "partially validated"** — klaim production-grade tidak diajukan sampai V3 terukur dan F9-19 tertutup.

## 12. Dependensi kode yang MENUNGGU (setelah F2; tidak dikerjakan sekarang)
| Item | Isi | Syarat uji (terbukti FAIL di versi lama) |
|---|---|---|
| `render.py` v5 — caption ASS | kata kunci berwarna statis per kartu; timing sama dengan drawtext | kartu dengan `keywords` → warna aksen muncul di piksel kata yang benar; v4 tidak mewarnai — **SELESAI di F6** (v5-F6; piksel aksen 2.497/1.737 pada proyek mini; `--print` K1/K2 identik v4.2; selftest 117/117). Batasan aj/al/am tercatat di §8; jalur ber-keywords **EKSPERIMENTAL** sampai aj selesai + tes escaping (ao) |
| `render.py` v5 — `overlays` (opsional) | judul permanen, watermark, logo — **hanya bila ada brief yang memintanya** | posisi + opasitas terverifikasi; tidak menutupi kartu — **[T], tidak dikerjakan di F6** (tidak ada brief yang meminta) |
| `qc_all.py` | overlay tidak dihitung sebagai kartu caption di `kartu_lint` (tidak memicu tumpang-tindih palsu); cek margin aman [T] | negatif: overlay yang menimpa kartu → FAIL — **[T], hanya relevan bila overlay diimplementasikan** |
Kode ASS selesai di F6; overlay + qc overlay masih [T].

## 13. Kegagalan yang diantisipasi
| Kegagalan | Mitigasi |
|---|---|
| Whisper salah dengar nama/istilah/bahasa informal | naskah dikoreksi sambil mendengar; teks kartu tidak dari transkrip mentah |
| Momen yang diminta tidak ada | lapor, jangan dipalsukan |
| Gambar tidak cocok dengan klaim transkrip (pergantian layar, bagian lain) | contact sheet wajib di G-STORY |
| Jendela aplikasi/info pribadi/konten eksplisit di layar | hindari lewat crop/potongan lain; blur [T] ditunda |
| Klip dibuka dengan pemanasan / diakhiri menggantung | rubrik "Hook" dan "Utuh"; potong ulang |
| Caption `prop` meleset pada ucapan alami | grup per frasa-napas pendek; dengar ulang; manual bila ragu |
| Loudness mengikuti skill luar (−14) tanpa sadar | lock −18; konflik brief diputuskan di G-BRIEF |
| Overlay/watermark ditambahkan tanpa diminta brief | default mati; brief People Pleaser melarang branding sensitif [D] |
| Mengisi kuota dengan momen lemah | boleh melapor kurang dari kuota |
| Transkripsi 1 jam sumber di VM = ±1 jam (RTF ≈1,04; rentang 0,72–1,43, §9) | jendela ±60 dtk bila ada poin; sebut estimasi dulu |

## 14. Done criteria khusus K3 (di atas §10 SKILL.md)
1. Tiap klip: `moments.json` dengan bukti contact sheet; momen tak ditemukan dilaporkan.
2. Tiap klip: G-HUMAN disetujui eksplisit; `brief_audit` 0 FAIL.
3. Laporan per sumber: daftar klip (judul, durasi, timestamp sumber, saran caption TikTok), plus hal yang tidak ditemukan/diubah → `production-log.md` + `caption_tiktok.txt` per klip.

## 15. Jalur sumber panjang (VOD) [D n=1 — tervalidasi F9 pada satu VOD Windah GTA VI, 23 Nov 2026; pengecualian: F9-19 tetap [T], lihat §7 butir 9]

Sumber > 20 menit (VOD/stream, podcast panjang) TIDAK dikerjakan seperti sumber pendek.
Urutan kerja: **sinyal dulu → unduh potongan → transkrip per potongan → kerja per potongan**.
Transkripsi penuh di VM **dilarang** tanpa izin eksplisit + estimasi (lock #46 [D n=1]) —
menggantikan opsi (a) "jalan penuh di VM" di §9.

### 15.1 Sinyal dulu (tanpa transkripsi) [D n=1]
Cari momen dari sinyal non-transkrip, berurutan:
1. **Chapters / timestamp di deskripsi dan komentar** — poin waktu yang ditulis pembuat/penonton.
2. **Heatmap "paling sering diputar ulang"** (bila tersedia di metadata) — puncak = momen yang ditonton ulang.
3. **Lonjakan chat replay** (unduh `live_chat` = teks; butuh persetujuan per manifest) — bin 10 dtk,
   bandingkan jumlah pesan per bin dengan **median bergulir**; token tawa/kaget
   (`wkwk`, `HAHA`, `anjir`, `gila`) [A] menaikkan skor bin. **Chat tertinggal 5–20 dtk** dari
   kejadian di layar [A] — jendela kandidat **digeser mundur** sejauh itu.
   - Lonjakan = bin > 2× median bergulir (30 bin) dan ≥10 pesan/bin [A]; bin berdekatan digabung.
   - Heuristik **gameplay-only RELATIF** [D n=1, temuan F9]: jendela dicurigai gameplay-only bila
     densitas token tawa/kagetnya < **0,5× densitas baseline** seluruh chat; bila baseline
     < 2% heuristik tidak dipakai (tidak bisa membedakan). Ambang absolut 10% yang lama
     DITARIK — pada chat Windah nyata baseline hanya ~3%, jadi ambang absolut menandai
     SEMUA lonjakan sebagai gameplay-only (k3 = 0).
   - Bila k3 dari lonjakan < minimum, **jangkar (chapter/deskripsi/komentar) melengkapi**
     sampai 9 jendela (klaster per 60 dtk, urutan jumlah jangkar, dedup tumpang tindih).
   - Lonjakan di awal VOD (< 15 dtk) **dilewati** — tidak bisa diberi pad 15 dtk untuk F9.5.
   - Praktis: `live_chat` VOD 4 jam = **258 MB, unduh 46 menit** (~330 KB/s, android client);
     parse harus **streaming** (`iter_json_array`) — `json.load` penuh butuh >1 GB RAM.
     `videoOffsetTimeMsec` dan `timestampUsec` berupa **string**; `timestampUsec` adalah
     epoch dinding, BUKAN offset video — jangan dipakai sebagai waktu.
4. Opsional, hanya dengan izin terpisah: unduh **audio-only VOD penuh** (≈100 MB per 5 jam [A])
   untuk analisis energi audio, bila sinyal 1–3 tidak cukup.
Hasil: `kandidat.json` 6–9 jendela (2–3× kuota), tiap jendela: waktu absolut, sinyal
pendukung, skor sinyal. Jendela **gameplay-only** (tanpa ucapan pembicara yang menonjol)
dicatat sebagai `catatan_k5` — hanya dicatat, tidak diunduh, tidak dibangun (K5 = F10).
Tanpa sinyal apa pun → `vod_signals.py` rc ≠ 0 (bukan kandidat kosong yang diam-diam).

### 15.2 Unduh potongan (rendah dulu, 1080p belakangan) [D n=1]
- Manifest dulu (nama, sumber, ukuran, format) — disetujui user sebelum unduh apa pun.
- Potongan kandidat: `--download-sections "*HH:MM:SS-HH:MM:SS"` dengan **padding**
  (±15 dtk [A]) agar momen tidak terpotong di tepi; **maks 150 dtk** per potongan (F9.5),
  format 360–480p+audio.
- **Pin format untuk potongan di VM CPU-only [D n=1, F9-8]:** selector generik
  `bv[height<=360]+ba/b[height<=360]` kini resolve ke **AV1 396+251**, dan stream-cut
  ffmpeg atas AV1 di VM 1,5 vCPU hanya 0,5× realtime → sesi TLS putus di ~60 dtk
  (k1 percobaan 1 gagal, rc=1). Paksa **`134+140`** (AVC 360p + m4a) — semua 9 chunk
  F9.5 sukses. Jangan pakai AV1 untuk potongan di VM.
- **Rute yt-dlp [D n=1, F9-9]:** urutan **default → `player_client=android` (metadata saja)
  → ulang di waktu lain**. Bot-block 403 intermiten (F7-13): k4 gagal 403 pada URL
  itag=134, percobaan android gagal (format https dilewati — eksperimen SABR-only,
  134+140 tidak tersedia), retry default ~8 menit kemudian OK. **Android BUKAN
  fallback unduhan media yang andal saat ini — hanya metadata.**
- **Unduh ulang: hapus dulu / `--force-overwrites` [D n=1, F9-10]:** yt-dlp melewati
  berkas yang sudah ada ("has already been downloaded", rc tetap 0) — berkas korup
  tetap dipakai bila tidak dihapus dulu. **QA decode + cek durasi audio vs video tiap
  potongan sebelum transkrip:** 2 dari 12 berkas F9.5 mengalami audio putus di tengah
  (k9: audio 81,28/90,07 dtk; p2/k3: 24,35/120,10 dtk) karena satu paket AAC korup
  (`decode_band_types: Input buffer exhausted`) membuat decoder berhenti mengeluarkan
  audio sesudahnya; video utuh. Keduanya bersih sesudah unduh ulang (QA 0 error).
- Potongan terpilih (F9.8): hanya jendela terpilih + handle **±3 dtk**, maks 90 dtk,
  1080p, manifest kedua.
- **Format 1080p [D n=1, F9-14]:** 137 (1080p30 AVC) **tidak tersedia** untuk video ini;
  satu-satunya AVC 1080p adalah **312 (1920×1080 60fps, avc1.64002A, HLS/m3u8)** —
  pin **`312+140`** (alternatif 303 VP9 1080p60; 399 AV1 dilarang F9-8). Estimasi ukuran
  naik (±130 MB total untuk 3 jendela vs ±30–60 MB), tetap << batas P3 1 GB.
  **Sumber 60fps → konversi 30fps diverifikasi di QC:** output 30 fps CFR (filter
  `fps=30`, tiap frame kedua dibuang); k1/k6/k8 lolos qc_all 0 FAIL, tidak ada
  judder/duplikasi kasat pada frame QC yang dibaca.
- Batas hemat (P3): **tidak ada unduhan media ≥600 dtk** per berkas, **tidak ada unduhan
  VOD penuh**, total media **≤ 1,0 GB** [A] (rasio terhadap VOD penuh dilaporkan).

### 15.3 Pemetaan waktu absolut ↔ potongan [D n=1]
- Tiap potongan dicatat: `abs_start` (detik absolut di VOD), `dur`, `sha256`, `pad_start`.
  Waktu absolut = `abs_start + t_dalam_potongan`.
- Verifikasi P2 pada ≥3 potongan: unduh ulang dengan padding berbeda, korelasi audio
  (offset silang), selisih offset **≤ 0,05 dtk**. **Terukur F9.5: 3/3 lag 0,000 dtk** (k1/k2/k3).
- `vod_chunks.py`: manifest → perintah yt-dlp + tabel pemetaan; **menolak potongan ≥600 dtk**;
  mendukung resume (P5): potongan yang sudah ada + sha cocok dilewati saat jalankan ulang.

### 15.4 Transkrip per potongan [D n=1]
- `whisper-cli -m ggml-small.bin -l id`, WAV 16 kHz mono, **satu potongan per job, berurutan**,
  dengan checkpoint; tiap job direncanakan <10 menit. Potongan yang sudah ada transkripnya dilewati (P5).
- Anggaran P1: total audio ditranskrip **≤ 30 menit DAN ≤ 10% durasi VOD**; waktu dinding
  whisper tercatat per potongan. **Terukur F9.6: 13,0 menit audio (780,1 dtk) ≤ 30 menit DAN
  ≤ 10% VOD (1.463 dtk) — P1 LULUS**; RTF per chunk 0,724–1,427 (rata-rata bersih ≈1,04,
  konsisten dengan F9.0 0,975 dalam variasi isi audio; k1 1,781 tercemar contact-sheet
  paralel — lihat F9-18).
- Kecepatan terukur F9.0: **RTF 0,975** (n=1, sampel 297 dtk campuran narasi/trailer/dialog) —
  **§9 lama (±0,51× realtime, 1 jam ≈ 2 jam) TIDAK terulang** dan tidak lagi dipakai sebagai
  dasar estimasi; yang berlaku angka ukur terbaru. 30 menit audio ≈ 29 menit waktu dinding.
- Glosarium `--prompt` (judul/deskripsi + dari user) diuji pada 1 potongan dengan dan tanpa
  prompt, hasilnya informasi [T]. **Terukur F9.6 (k1): netral — tidak direkomendasikan
  sebagai default** (17 vs 18 segmen; perbedaan hanya tanda baca/kapitalisasi + 2 kata;
  tidak ada istilah glosarium yang muncul/membaik).
- **Detektor loop whisper [D n=1, F9-11]:** whisper small `-l id` menghalusinasi loop pada
  **5 dari 9 chunk** (k2, k3, k4, k7, k9) — frasa identik berulang dalam potongan 2,0 dtk
  ("Bagaimana kita bisa mengalurkan dia?" ×17, "Masih!" ~60 dtk, "Saya mau ke kantongan
  esok" ×12, "Kamu harus berbincang dengan aku" ×~30, "Kau harus menjelaskan kali ini,
  kawan" ×25), pola khas repetition loop saat audio bukan ucapan Indonesia yang jelas
  (dialog game Inggris/Melayu, musik, ambience); dialog Inggris "diterjemahkan" paksa
  menjadi kata Indonesia. **Aturan: segmen identik berulang ≥3× = flag HALUSINASI,
  chunk ditandai tidak-terpercaya; segmen loop DILARANG dikutip di naskah.**
- **ASR-2 harus divalidasi per-material [D n=1, F9-12]:** stable-ts tiny SAH sebagai ASR-2
  untuk **VO bersih** (F8-2: 49/64 kata GT vs small 43/64) tetapi **KOSONG (0 segmen /
  0 kata) pada audio game** — smoke test F9.8 (audio k1 + k6 30–60 dtk, 16 kHz mono):
  tiny = 0 segmen bahkan dengan `vad=False`, `no_speech_threshold=0.0`, `language=None`;
  kontrol pada VO bersih bekerja (13 segmen koheren). Pengganti
  **faster-whisper base** hanya **opini kedua yang lemah, bukan ASR-2 setara**: k1 smoke
  14 segmen/76 kata tapi garbled, k6 smoke hanya 2 segmen/12 kata; perbandingan kata
  (dual_asr.py) k1 sepakat 43/76 token, 33 ketidaksepakatan — kebanyakan kesalahan base.
  **[T] harus dikurasi, bukan auto-diff mentah:** filter segmen (ratio ≥0,5) + nama
  diri/angka/istilah Inggris otomatis [T]; ketidaksepakatan hanya dipakai bila kedua
  bacaan sama-sama masuk akal.
- **Sumber naskah [D n=1, F9-13]:** sumber naskah = **transkrip kalimat small + base
  kalimat + telinga user; kata-level HANYA untuk alignment waktu kartu.** Bukti k6:
  pada audio tumpang tindih (dialog NPC GTA VI + komentar Windah), run kata-level
  mendengar dialog NPC ("Ayo, ayo!", "Apa yang kau berikan?") di 0–25 dtk, sementara
  run kalimat mendengar Windah ("Off.", "Toh, tokos batu, Toh!") — diverifikasi berkas
  audio benar (ekstraksi `-ss` sebelum/sesudah `-i` memberi WAV berbeda byte tapi
  keduanya mentranskrip "tokos batu" dalam mode kalimat). k1/k8 tidak terkontaminasi
  (kata-level cocok kalimat).
- **ASR full-file dilarang sebagai satu-satunya sumber untuk audio game / dialog
  tumpang tindih [D n=1, F9-20]:** whisper.cpp small `-l id` full-file (66 dtk) jatuh
  ke loop halusinasi pada audio yang SAMA yang ditranskrip koheren di chunk 360p 90 dtk
  (F9.6) — korelasi audio 1080p vs 360p = 1,000 pada lag 0, jadi bukan isi audio yang
  berbeda, melainkan sensitivitas jendela/konteks decoder: loop "Mereka/Kau akan
  melakukan itu selanjutnya." ×15 segmen 2,0 dtk (chunk-rel 0–31,3) dipicu ucapan NPC
  tak jelas di awal berkas, lalu tidak pernah pulih; ekor "Terima kasih sudah menonton."
  juga halusinasi. faster-whisper base full-file IKUT loop ("Mereka akan melakukannya."
  ×6, 18 kata) — kedua ASR gagal bersamaan pada berkas yang sama. **Mitigasi yang
  TERBUKTI: potong per-slice ≤15–20 dtk** (parameter identik → 25 segmen koheren;
  beat "liat-liat dulu deh" ×3 TERBUKTI ucapan nyata, bukan loop). **P1 tidak
  bertambah:** audio yang sama, hanya dipecah job-nya.
- **Kata di tepi slice [D n=1, F9-21]:** kata di awal slice kehilangan konteks → salah
  dengar sistematis di tepi. Bukti: slice1 (15–30) dengar "Tidak apaan sih Argus
  batunya" sementara micro-slice 13–19 (lead-in 2 dtk) dengar "berapaan sih harga
  sepatunya?" — cocok 360p full-file; timing kata identik, hanya fonem yang salah.
  **Aturan: kata/ucapan di ±2 dtk tepi slice yang diragukan → verifikasi dengan
  micro-slice ber-lead-in** (atau run 360p/full-file sebagai pembanding).
- **Word-level mengkuantisasi ke bucket 2,0 dtk [D n=1, F9-22]:** `-ml 1 -sow` tetap
  mengkuantisasi ke bucket 2,0 dtk pada ucapan tak jelas/cepat ("Nah," 2,09 dtk;
  "liat-liat" 1,38 dtk; token nol-durasi di 22,00) — sehingga Δ batas internal kartu
  vs word-level (F9-15) adalah **BATAS ATAS**, bukan galat `prop`: k6 Δ maks 0,480 dtk
  (g2, g5) vs k1 0,122, tapi 2 dari 5 batas >0,10 adalah artefak bucket; di wilayah
  beresolusi kata normal, Δ maks 0,071 dtk. **V3 wajib memakai jeda yang ditandai
  manusia sebagai pembanding, bukan word-level.**
- Setelah transkrip per potongan ada, kerja lanjut mengikuti §5–§7 biasa, dengan
  `transcript.json` per potongan (bukan satu transkrip VOD penuh).

### 15.5 Yang tetap berlaku dari jalur K3 biasa
Rubrik momen (§5), verifikasi contact sheet (§5), naskah dikoreksi sambil didengar (§6),
timing caption per frasa-napas (§7), kata kunci berwarna (§8), crop dari frame nyata (§10),
dan semua gate (G-STORY, G-CROP, G-HUMAN, G-FINAL) — tidak ada yang dilonggarkan untuk VOD.
**Pengecualian yang tetap terbuka:** timing `prop` pada grup bertempo tidak merata
(F9-19, §7 butir 9) — jalur manual yang diusulkan masih [T]; V3 belum diukur.
