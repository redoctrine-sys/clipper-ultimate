# Lisensi pihak ketiga & atribusi

Lisensi skill ini: tanpa lisensi — semua hak cipta dipertahankan oleh pembuatnya (keputusan 25 Nov 2026).
Kebijakan: **tidak ada kode atau teks README yang disalin** dari repo di bawah. Instruksi ditulis ulang dengan kata sendiri dan dilipat ke tahap pipeline. Repo ber-GPL dipanggil hanya sebagai **program eksternal** oleh user. Lisensi diambil dari README/halaman repo yang dibaca 22 Nov 2026 atau dari `inventaris-skill-clipper.md` (diverifikasi 21 Nov 2026).

| # | Alat | Lisensi | Cara skill memakainya | Catatan |
|---|------|---------|-----------------------|---------|
| 01 | yt-dlp | Unlicense | program eksternal (CLI) | rilis biner PyInstaller memuat kode GPLv3+ → bila mendistribusikan biner, ikuti GPLv3+ |
| 02 | OpenCut | MIT | tidak dipakai di core | |
| 03 | OpenCV | Apache-2.0 | pustaka Python (deteksi wajah) | model YuNet dari opencv_zoo: periksa lisensi model terpisah saat mengunduh [T] |
| 04 | OBS Studio | GPL-2.0 | program eksternal (PC user) | |
| 05 | AI-Youtube-Shorts-Generator | MIT | **konsep saja** (kriteria viralitas, chunking, dedupe) ditulis ulang | atribusi: repo asli SamurAIGPT/AI-Youtube-Shorts-Generator |
| 06 | Mediabunny | MPL-2.0 | tidak dipakai | |
| 07 | Whisper (OpenAI) | MIT | cadangan | |
| 08 | whisper.cpp | MIT | program eksternal (`whisper-cli`) | |
| 09 | stable-ts | MIT | kandidat (F3-A) | repo diarsipkan |
| 10 | pyannote.audio | MIT (kode) | opsional (B) | pipeline community-1: syarat pengguna Hugging Face harus disetujui user sendiri |
| 11 | Supervision | MIT | visualisasi debug | |
| 12 | Norfair | BSD-3-Clause | pustaka Python | |
| 13 | DeepFilterNet | MIT atau Apache-2.0 (dual) | opsional | |
| 14 | Demucs | MIT | opsional | repo diarsipkan; pin versi |
| 15 | pysubs2 | MIT | opsional | |
| 16 | libass | ISC | via ffmpeg | |
| 17 | Editly | MIT | **ditolak** | |
| 18 | Kdenlive | GPL-3.0 | program eksternal (PC user) | |
| 19 | Shotcut | GPL-3.0 | program eksternal (PC user) | |
| 20 | Real-ESRGAN | BSD-3-Clause | opsional (B) | bobot diunduh terpisah; periksa lisensi bobot [T] |
| 21 | RIFE | MIT | opsional (B) | bobot diunduh terpisah |
| 22 | PyAV | BSD-3-Clause | pembantu opsional | |
| — | ffmpeg | LGPL/GPL tergantung build [A] | program eksternal | renderer tunggal; catat opsi build dari `env_check` |
| — | gdown, instagram-cli | [belum diverifikasi — T] | program eksternal | catat lisensi saat pertama dipakai |
| — | skill luar "YouTube highlight clipper" (postingan publik di X; identitas sumber dicatat di `_internal/`) | **TIDAK DIKETAHUI** | **metode saja**, ditulis ulang dengan kata sendiri di `references/K3-panjang.md` | **Tidak ada teks, prompt, perintah, atau struktur bagian yang disalin.** Ide yang dipinjam: rubrik momen, verifikasi gambar vs transkrip lewat contact sheet, kata kunci berwarna, laporan per klip. Bagian yang ditolak/diubah (loudness −14, word timestamp, faster-whisper, overlay default) tercatat di `rencana-pelipatan-K3.md`. Karena lisensi tidak diketahui, jangan menyalin dari sumber itu ke berkas skill ini; bila perlu rujukan baru, baca ulang sumbernya dan tulis ulang |

| 23 | hook-master-skill (Liamrjohnston) | MIT | **metode saja**, ditulis ulang (4 kegagalan hook, format kontras, lock-in, panel penonton) | SKILL.md dibaca dari klon riset; skrip repo tidak dijalankan |
| 24 | video-agent-skills — studio-script (Melvynx) | MIT | **metode saja**, ditulis ulang (3 hook dari formula berbeda + skor, re-hook tengah, payoff dulu, humanize) | SKILL.md dibaca dari klon riset |
| 25 | content-skills — viral-hooks + viral-short-form (Vyral) | MIT | **metode saja**, ditulis ulang (hook 3 lapis, batch varian, janji = payoff, anti-pattern) | SKILL.md dibaca dari klon riset |
| 26 | instagram-agent-skill — ig-reel (Jakeschincariol) | MIT | **metode saja**, ditulis ulang (bentuk 0–2 hook / 2–7 taruhan, 3 hook lalu skor, teks layar terpisah) | `hookscore.py`/`beats.py` TIDAK dijalankan |
| 27 | ai-business-skills — 04-script-video-global (abhayekanath/minhnv0807) | MIT | **metode saja**, ditulis ulang (5 tipe hook, struktur timestamp, kalimat ≤15 kata, satu gagasan) | dibaca via GitHub |
| — | writing-youtube-narratives, story-and-shots, creative-writing-craft, dialogue-and-audio, sw-dialogue, sw-scene-craft, sw-series-structure, chekhov-dramaturgy, ozu-screenplay-style, video-prompt-craft, casting_suara (skill lokal) | **TIDAK DIKETAHUI (tanpa lisensi)** | **metode saja**, diparafrase (janji penonton, beat = perubahan, delayed disclosure, tulis untuk telinga, teaser = cerita, value turn, dialog = tindakan, dst.) | **Tidak ada teks yang disalin verbatim.** |

| 28 | video-sound (GrowKaz, skill lokal terpasang) | **TIDAK DIKETAHUI (tanpa lisensi)** | **metode saja**, diparafrase (taksonomi SFX, ducking sidechain, stem mixer) | Angka −14 LUFS TIDAK dilipat (lock skill −18 menang). |
| 29 | sound-effects (Barty-Bart/motion-graphics) | MIT | **metode saja**, ditulis ulang (cue-dari-potongan → 1 SFX per cue, mix terukur, pustaka CC0 Kenney + Freesound) | Angka −16 LUFS TIDAK dilipat (lock skill −18 menang). |
| 30 | openverse-sfx (Varnan-Tech/opendirectory) | MIT | **metode saja**, ditulis ulang (Openverse API + filter lisensi wajib cc0/by/pdm + credits.txt + ukur, bukan rasa) | — |
| 31 | fetch-assets (Naveen-S6/EditorThambi) | **TIDAK DITEMUKAN** | **distilasi kata sendiri saja**, jangan salin (pilihan Pixabay/Mixkit/Freesound sudah terverifikasi independen di musik-sfx.md §2) | — |
| 32 | cappus (nsudy-code/cappus) | MIT | **dicatat sebagai metode saja** (musik/SFX digenerate programatik = tanpa masalah hak cipta), TIDAK dilipat (tergantung CapCut) | — |
| — | Pustaka musik/SFX (Pixabay, Mixkit, Incompetech CC-BY 4.0, Uppbeat, Bensound, FMA, YouTube Audio Library, Zapsplat, Freesound, Sonniss GDC, Kenney CC0) | Lisensi konten masing-masing (dibaca Nov 2026) | dipakai sebagai sumber aset, bukan kode; lisensi dicatat per aset di production.json (lock #43) | **Cek ulang lisensi pada hari unduh — lisensi bisa berubah.** |

Catatan: nama model/font/musik yang dipakai produksi punya lisensi sendiri; catat sumber tiap aset di `sources.json`.
