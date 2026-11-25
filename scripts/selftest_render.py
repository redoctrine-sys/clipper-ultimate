"""selftest_render.py — uji regresi render.py v2 (dipanggil selftest.py --render). Data sintetis; tanpa berkas besar.
Memeriksa: jumlah frame total, batas segmen tepat di grid frame (tanpa akumulasi 24->30 fps), mode fit (bar hitam, tinggi ganjil 453),
freeze + crop, xfade, still, kartu berkotak, audio terpisah dari video (musik tidak terpotong saat VO habis), QC 0 FAIL."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import qc_all
import render

def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode: raise RuntimeError("gagal: " + " ".join(cmd)[:200] + "\n" + p.stderr[-800:])
    return p

def px(path, n, x, y):
    """RGB satu piksel pada frame ke-n."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"select=eq(n\\,{n}),crop=2:2:{x}:{y}", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return tuple(p.stdout[:3]) if len(p.stdout) >= 3 else None

def red(c): return c and c[0] > 180 and c[1] < 90 and c[2] < 90
def blue(c): return c and c[2] > 180 and c[0] < 90 and c[1] < 90
def black(c): return c and max(c) < 40

def run(w, cal, expect):
    os.chdir(w)
    for name, col in (("red", "red"), ("blue", "blue"), ("green", "green"), ("yellow", "yellow")):
        sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c={col}:s=1920x1080:r=24:d=8", "-f", "lavfi", "-i", "sine=f=300:d=8",
            "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", f"{name}.mp4"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=s=1920x1080:r=24:d=8", "-f", "lavfi", "-i", "sine=f=300:d=8", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", "test.mp4"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=green:s=1600x1200:d=1", "-frames:v", "1", "poster.png"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=200:d=3", "-c:a", "pcm_s16le", "vo.wav"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=110:d=30", "-c:a", "pcm_s16le", "bed.wav"])
    cards = [{"id": 1, "kind": "caption", "text": "kartu satu dua", "start": 0.5, "end": 2.0}, {"id": 2, "kind": "caption", "text": "kartu dua tiga empat", "start": 2.04, "end": 3.2}]
    cfg = {"schema": 2, "out": "rt.mp4", "work": "work", "size": [1080, 1920], "fps": 30,
           "segments": [
               {"type": "clip", "src": "red.mp4", "src_in": 0.5, "dur": 3.2, "mode": "cover"},
               {"type": "clip", "src": "blue.mp4", "src_in": 0.5, "dur": 2.55, "mode": "fit", "fit_h": 453},
               {"type": "clip", "src": "green.mp4", "src_in": 1.0, "dur": 4.9, "mode": "crop", "crop": {"x": {"from": 100, "to": 400}, "y": 0, "w": 608, "h": 1080}},
               {"type": "freeze", "src": "test.mp4", "src_in": 3.0, "dur": 1.22, "mode": "crop", "crop": {"x": 656, "y": 0, "w": 608, "h": 1080}},
               {"type": "clip", "src": "yellow.mp4", "src_in": 0.0, "dur": 3.33, "mode": "cover", "transition_in": {"type": "fade", "dur": 0.5}},
               {"type": "still", "src": "poster.png", "dur": 2.0, "zoom": [1.0, 1.05]},
               {"type": "clip", "src": "red.mp4", "src_in": 2.0, "dur": 4.0, "mode": "cover"}],
           "audio": {"items": [
               {"role": "source", "src": "red.mp4", "src_in": 4.0, "at": 0, "dur": 3.2, "gain_db": -6},       # audio dari offset BERBEDA dari video (src_in 0,5)
               {"role": "vo", "src": "vo.wav", "at": 1.0},
               {"role": "music", "src": "bed.wav", "loop": True, "dur": 21.0, "gain_db": -10, "fade_out": 1.0}],
               "duck": {"key": ["vo"], "target": ["music"], "threshold": 0.025, "ratio": 6, "attack": 80, "release": 400, "makeup": 1}},
           "cards": cards, "style": {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "size": 46, "border": 3, "box": True, "boxborderw": 20, "y": "h-280"},
           "loudness": {"I": -18, "TP": -3.5, "TP_pass1": -3.0, "LRA": 11}}
    json.dump(cfg, open("rt.json", "w"), indent=1)
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "rt.json"], capture_output=True, text=True)
    expect("render v2 selesai tanpa error", p.returncode, 0)
    if p.returncode: print(p.stderr[-1500:]); return
    # xfade memotong 0,5 dtk: total = 3.2+2.55+4.9+1.22+3.33-0.5+2.0+4.0 = 20.7 -> 621 frame
    n = int(sh(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", "rt.mp4"]).stdout.strip())
    expect("jumlah frame total = round(20.7*30)=621", n, 621)
    expect("frame 95 (akhir segmen merah) merah; frame 96 awal fit-biru: tengah biru", (red(px("rt.mp4", 95, 540, 960)), blue(px("rt.mp4", 96, 540, 960))), (True, True))
    expect("mode fit (453 ganjil): bar atas HITAM, tengah biru", (black(px("rt.mp4", 100, 540, 100)), blue(px("rt.mp4", 100, 540, 960))), (True, True))
    # CTA merah mulai tepat di 20.7-4.0 = 16.7 s -> frame 501
    expect("batas CTA tepat di frame 501 (16,7 s) tanpa akumulasi", (red(px("rt.mp4", 500, 540, 960)), red(px("rt.mp4", 501, 540, 960))), (False, True))
    d = qc_all.probe("rt.mp4"); a = type("A", (), dict(bitrate=3.4, tol_bitrate=0.1, tol_lufs=1.0, tp_max=-3.0))()
    fmt, dur = qc_all.check_format(d, a)
    expect("format akhir 1080x1920 30fps h264+aac", fmt[0]["status"], "PASS")
    expect("QC hening digital: musik tidak terpotong saat VO/source habis", qc_all.check_silence("rt.mp4", dur, [])["status"], "PASS")
    expect("QC loudness ±1 dari -18", qc_all.check_loudness("rt.mp4", a)["status"], "PASS")
    expect("QC kartu lint", qc_all.check_cards(cards, [], dur)["status"], "PASS")
    expect("durasi mux ≈ 20,7 s (±0,05)", abs(dur - 20.7) <= 0.05, True)


def run_audio_regression(w, expect):
    """Regresi bug ronde 2: atrim=duration=T per item MENGHANCURKAN adelay pada input MP4 dengan -ss.
    Item MP4 (src_in>0, at>0) + item WAV (at>0). Mix harus = T, hening sebelum `at`, sinyal di [at, at+dur]."""
    os.chdir(w)
    # MP4 sumber 10 dtk: sinus 500 Hz hanya pada 6-9 dtk (hening sebelum), agar src_in=6 menghasilkan sinyal tepat sepanjang dur
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=gray:s=640x360:r=24:d=10", "-f", "lavfi", "-i", "sine=f=500:d=10",
        "-af", "volume=0:enable='lt(t,6)'", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", "src_ar.mp4"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=800:d=2", "-c:a", "pcm_s16le", "wavar.wav"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=blue:s=1920x1080:r=30:d=12", "-c:v", "libx264", "-preset", "ultrafast", "bg.mp4"])
    cfg = {"schema": 2, "out": "ar.mp4", "work": "work_ar", "size": [1080, 1920], "fps": 30,
           "segments": [{"type": "clip", "src": "bg.mp4", "src_in": 0, "dur": 12.0, "mode": "cover"}],
           "audio": {"items": [
               {"role": "source", "src": "src_ar.mp4", "src_in": 6.0, "at": 4.0, "dur": 3.0},     # sinyal diharapkan 4,0-7,0
               {"role": "vo", "src": "wavar.wav", "at": 9.0}]},                                  # sinyal diharapkan 9,0-11,0
           "cards": [], "style": {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"},
           "loudness": {"I": -18, "TP": -3.5, "TP_pass1": -3.0, "LRA": 11}}
    json.dump(cfg, open("ar.json", "w"), indent=1)
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "ar.json"], capture_output=True, text=True)
    expect("regresi audio: render selesai", p.returncode, 0)
    if p.returncode: print(p.stderr[-800:]); return
    dur = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "ar.mp4"]).stdout.strip())
    expect("regresi audio: durasi mix = 12,0 (±0,05)", abs(dur - 12.0) <= 0.05, True)

    def level(t0, t1):
        """RMS (dB) audio pada [t0,t1] di ar.mp4; -inf dipetakan -120."""
        import re
        e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{t0}", "-t", f"{t1-t0}", "-i", "ar.mp4", "-vn", "-af", "astats=metadata=1:reset=0", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        m = re.findall(r"RMS level dB:\s*(-?[\d.]+|-inf)", e)
        v = m[-1] if m else "-inf"
        return -120.0 if v == "-inf" else float(v)
    expect("regresi audio: HENING sebelum item MP4 (0,5-3,5 s)", level(0.5, 3.5) < -70, True)
    expect("regresi audio: SINYAL item MP4 di 4,3-6,7 s", level(4.3, 6.7) > -50, True)
    expect("regresi audio: hening di antara item (7,4-8,6 s)", level(7.4, 8.6) < -70, True)
    expect("regresi audio: SINYAL item WAV di 9,2-10,8 s", level(9.2, 10.8) > -50, True)


def run_color_preflight(w, expect):
    """v4: segmen type=color (tanpa berkas) + preflight berkas hilang (rc 2) + QC hitam murni tetap FAIL."""
    os.chdir(w)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=gray:s=1920x1080:r=30:d=4", "-f", "lavfi", "-i", "sine=f=300:d=4",
        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", "gray.mp4"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=250:d=4", "-c:a", "pcm_s16le", "tone4.wav"])
    cards = [{"id": 1, "kind": "caption", "text": "kartu di atas hitam", "start": 3.1, "end": 4.9}]
    cfg = {"schema": 2, "out": "cl.mp4", "work": "work_cl", "size": [1080, 1920], "fps": 30,
           "segments": [{"type": "clip", "src": "gray.mp4", "src_in": 0, "dur": 3.0, "mode": "cover"},
                        {"type": "color", "color": "black", "dur": 2.0}],
           "audio": {"items": [{"role": "vo", "src": "tone4.wav", "at": 0.5}]},
           "cards": cards, "style": {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"},
           "loudness": {"I": -18, "TP": -3.5, "TP_pass1": -3.0, "LRA": 11}}
    json.dump(cfg, open("cl.json", "w"), indent=1)
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "cl.json"], capture_output=True, text=True)
    expect("color: render selesai tanpa berkas hitam", p.returncode, 0)
    if p.returncode: print(p.stderr[-800:]); return
    n = int(sh(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", "cl.mp4"]).stdout.strip())
    expect("color: jumlah frame = 150 (5,0 dtk)", n, 150)
    expect("color: frame 100 hitam (luar kartu), frame 20 abu-abu", (black(px("cl.mp4", 100, 100, 100)), black(px("cl.mp4", 20, 100, 100))), (True, False))
    d = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "cl.mp4"]).stdout.strip())
    expect("QC: segmen color hitam tanpa deklarasi = FAIL (hitam murni)", qc_all.check_black("cl.mp4", [])["status"], "FAIL")
    # NEGATIF preflight: berkas hilang -> rc 2 + nama berkas di pesan
    cfg2 = json.loads(json.dumps(cfg)); cfg2["segments"][0]["src"] = "tidak_ada.mp4"; cfg2["audio"]["items"][0]["src"] = "juga_tidak_ada.wav"; cfg2["cards"] = "cards_hilang.json"
    json.dump(cfg2, open("cl2.json", "w"))
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "cl2.json"], capture_output=True, text=True)
    expect("NEGATIF preflight: berkas hilang -> rc 2", p.returncode, 2)
    expect("NEGATIF preflight: pesan memuat ketiga berkas hilang", all(x in p.stderr for x in ("tidak_ada.mp4", "juga_tidak_ada.wav", "cards_hilang.json")), True)
    cfg3 = json.loads(json.dumps(cfg)); cfg3["segments"][1] = {"type": "color", "dur": 2.0}
    json.dump(cfg3, open("cl3.json", "w"))
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "cl3.json", "--print"], capture_output=True, text=True)
    expect("NEGATIF color tanpa kunci 'color' -> rc 2", p.returncode, 2)


def run_still_xfade_range(w, expect):
    """F6-A1 (b): kasus sintetis still->xfade — celah yang membuat bug range lolos v0.4.
    2 still warna berbeda + xfade 0,5 -> ffprobe pix_fmt HARUS yuv420p.
    Terbukti GAGAL (yuvj420p) bila filter scale=out_range=tv dinonaktifkan (v4.1-fix-range
    dinonaktifkan sementara); lulus bila filter aktif. Sumber sintetis lavfi, tanpa aset K1/K2.
    Still WAJIB .jpg (bukan .png): JPEG decode native ke yuvj420p pc-range seperti poster
    JPG K2 — PNG decode ke rgb24 dan range-nya hilang di konversi, sehingga bug TIDAK
    tereproduksi (diverifikasi F6-A1: PNG+zoom tetap yuv420p walau filter nonaktif)."""
    os.chdir(w)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=red:s=1080x1920:r=30:d=1", "-frames:v", "1", "still_red.jpg"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=blue:s=1080x1920:r=30:d=1", "-frames:v", "1", "still_blue.jpg"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=250:d=4", "-c:a", "pcm_s16le", "tone_x.wav"])
    cfg = {"schema": 2, "out": "sx.mp4", "work": "work_sx", "size": [1080, 1920], "fps": 30,
           "segments": [{"type": "still", "src": "still_red.jpg", "dur": 2.0, "zoom": [1.0, 1.05]},
                        {"type": "still", "src": "still_blue.jpg", "dur": 2.0, "zoom": [1.0, 1.05], "transition_in": {"type": "fade", "dur": 0.5}}],
           "audio": {"items": [{"role": "vo", "src": "tone_x.wav", "at": 0.0}]},
           "cards": [], "style": {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"},
           "loudness": {"I": -18, "TP": -3.5, "TP_pass1": -3.0, "LRA": 11}}
    json.dump(cfg, open("sx.json", "w"), indent=1)
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "sx.json"], capture_output=True, text=True)
    expect("still->xfade: render selesai", p.returncode, 0)
    if p.returncode: print(p.stderr[-800:]); return
    fmt = sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=pix_fmt", "-of", "csv=p=0", "sx.mp4"]).stdout.strip()
    expect("still->xfade: pix_fmt = yuv420p (bukan yuvj420p)", fmt, "yuv420p")
    n = int(sh(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", "sx.mp4"]).stdout.strip())
    expect("still->xfade: jumlah frame = 105 (3,5 dtk)", n, 105)
    expect("still->xfade: frame 0 merah, frame akhir biru", (red(px("sx.mp4", 0, 540, 960)), blue(px("sx.mp4", 104, 540, 960))), (True, True))


def run_still_mode_preflight(w, expect):
    """F8.2-a (F7-19): segmen still + mode selain cover DITOLAK preflight rc 2 (dulu rc 0, mode
    diabaikan diam-diam — vchain() still tidak pernah membaca mode). --print saja (preflight jalan
    sebelum perintah dicetak); tanpa render. Terbukti FAIL di kode lama (rc 0 untuk fit/blurpad)."""
    os.chdir(w)
    MSG = "still hanya mendukung cover; pre-buat PNG 1080×1920 untuk fit/blurpad"

    def cfg_for(mode):
        seg = {"type": "still", "src": "still_red.jpg", "dur": 2.0}
        if mode is not None:
            seg["mode"] = mode
        return {"schema": 2, "out": "sm.mp4", "work": "work_sm", "size": [1080, 1920], "fps": 30,
                "segments": [seg],
                "audio": {"items": [{"role": "vo", "src": "tone_x.wav", "at": 0.0}]},
                "cards": [], "style": {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"},
                "loudness": {"I": -18, "TP": -3.5, "TP_pass1": -3.0, "LRA": 11}}

    def run_cli(mode):
        json.dump(cfg_for(mode), open(f"sm_{mode or 'nomode'}.json", "w"))
        p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", f"sm_{mode or 'nomode'}.json", "--print"], capture_output=True, text=True)
        return p.returncode, p.stderr
    rc, err = run_cli("fit")
    expect("NEGATIF F8.2-a still + mode:fit -> rc 2", rc, 2)
    expect("F8.2-a pesan penolakan persis (fit)", MSG in err, True)
    rc, _ = run_cli("blurpad")
    expect("NEGATIF F8.2-a still + mode:blurpad -> rc 2", rc, 2)
    rc, _ = run_cli("crop")
    expect("NEGATIF F8.2-a still + mode:crop -> rc 2", rc, 2)
    rc, _ = run_cli("cover")
    expect("F8.2-a still + mode:cover -> rc 0", rc, 0)
    rc, _ = run_cli(None)
    expect("F8.2-a still tanpa mode -> rc 0", rc, 0)
    expect("F8.2-a unit: preflight() mengembalikan pesan persis", render.preflight(cfg_for("fit")), [MSG])


def _scan_band(path, n, y0=1550, h=300):
    """Klasifikasi piksel pita caption (y0..y0+h) pada frame ke-n: piksel putih (caption biasa),
    kuning-aksen (#FFD60A sesudah yuv round-trip ~ (240,208,0)), + bbox glif (putih+kuning)."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"select=eq(n\\,{n}),crop=1080:{h}:0:{y0}",
                        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    buf = p.stdout; W = 1080
    white = yellow = 0; xw, yw, xy, yy = [], [], [], []
    for y in range(h):
        for x in range(W):
            i = (y * W + x) * 3
            if i + 2 >= len(buf): break
            r, g, b = buf[i], buf[i + 1], buf[i + 2]
            if r > 200 and g > 200 and b > 200: white += 1; xw.append(x); yw.append(y + y0)
            elif r > 200 and 150 < g < 245 and b < 90: yellow += 1; xy.append(x); yy.append(y + y0)
    def bb(xs, ys): return (min(xs), max(xs), min(ys), max(ys)) if xs else None
    return {"white": white, "yellow": yellow, "white_bb": bb(xw, yw), "yellow_bb": bb(xy, yy),
            "glyph_bb": bb(xw + xy, yw + yy)}


def run_ass_keywords(w, expect):
    """F6-C (K3, render.py v5-F6): kartu ber-keywords dirender lewat ASS, kata kunci berwarna aksen.
    Terbukti GAGAL di v4.2 (kata kunci tetap putih: yellow=0 pada frame kartu; dibuktikan manual di
    ~/workspace/tmp/f6k3/t_kw sebelum perbaikan, lalu lulus di v5). Sumber sintetis lavfi, tanpa materi K3 nyata.
    Aksen default #FFD60A -> piksel ~(240,208,0) sesudah yuv420p round-trip (diukur, bukan diasumsikan)."""
    os.chdir(w)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=blue:s=1920x1080:r=30:d=6", "-f", "lavfi", "-i", "sine=f=300:d=6",
        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", "ass_bg.mp4"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=250:d=6", "-c:a", "pcm_s16le", "ass_tone.wav"])
    cards = [{"id": 1, "kind": "caption", "text": "apel JERUK mangga", "start": 0.5, "end": 2.5, "keywords": ["JERUK"]},
             {"id": 2, "kind": "caption", "text": "satu dua TIGA empat", "start": 3.0, "end": 5.0, "keywords": ["TIGA"]},
             {"id": 3, "kind": "caption", "text": "apel JERUK mangga dan satu dua", "start": 5.0, "end": 6.0, "keywords": ["JERUK"]}]
    cfg = {"schema": 2, "out": "ass.mp4", "work": "work_ass", "size": [1080, 1920], "fps": 30,
           "segments": [{"type": "clip", "src": "ass_bg.mp4", "src_in": 0, "dur": 6.0, "mode": "cover"}],
           "audio": {"items": [{"role": "vo", "src": "ass_tone.wav", "at": 0.0}]},
           "cards": cards, "style": {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "size": 46, "border": 3, "box": True, "boxborderw": 20, "y": "h-280"},
           "loudness": {"I": -18, "TP": -3.5, "TP_pass1": -3.0, "LRA": 11}}
    json.dump(cfg, open("ass.json", "w"), indent=1)
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "ass.json"], capture_output=True, text=True)
    expect("ASS keywords: render selesai", p.returncode, 0)
    if p.returncode: print(p.stderr[-800:]); return
    apath = os.path.join("work_ass", "captions.ass")
    expect("ASS keywords: berkas work/captions.ass terbentuk", os.path.exists(apath), True)
    ass = open(apath, encoding="utf-8").read() if os.path.exists(apath) else ""
    expect("ASS keywords: tag aksen pada JERUK", r"{\1c&H000AD6FF&}JERUK{\r}" in ass, True)
    expect("ASS keywords: tag aksen pada TIGA", r"{\1c&H000AD6FF&}TIGA{\r}" in ass, True)
    def _t(s):
        h, m, rest = s.split(":"); sec, cc = rest.split("."); return int(h) * 3600 + int(m) * 60 + int(sec) + int(cc) / 100
    dlg = [( _t(m.group(1)), _t(m.group(2))) for m in re.finditer(r"Dialogue: 0,([^,]+),([^,]+),", ass)]
    expect("ASS keywords: waktu Dialogue == interval kartu (±0,01 dtk)",
           len(dlg) == 3 and max(max(abs(a - c["start"]), abs(b - c["end"])) for (a, b), c in zip(dlg, cards)) <= 0.01, True)
    f1 = _scan_band("ass.mp4", 45)
    expect("ASS keywords: kartu1 piksel aksen > 500 (v4.2: 0)", f1["yellow"] > 500, True)
    expect("ASS keywords: kartu1 piksel putih > 1000 (kata non-kunci tetap putih)", f1["white"] > 1000, True)
    expect("ASS keywords: kartu1 kata kunci di TENGAH (x kuning di dalam rentang x putih)",
           f1["yellow_bb"] and f1["white_bb"] and f1["yellow_bb"][0] > f1["white_bb"][0] and f1["yellow_bb"][1] < f1["white_bb"][1], True)
    g1 = f1["glyph_bb"]
    expect("ASS keywords: kartu1 geometri glif == drawtext ±12 px (atas 1640, bawah 1684)",
           g1 and abs(g1[2] - 1640) <= 12 and abs(g1[3] - 1684) <= 12, True)
    f2 = _scan_band("ass.mp4", 120)
    expect("ASS keywords: kartu2 aksen > 500 dan putih > 1000", (f2["yellow"] > 500, f2["white"] > 1000), (True, True))
    expect("ASS keywords: kartu2 kata kunci bukan kata pertama/terakhir",
           f2["yellow_bb"] and f2["white_bb"] and f2["yellow_bb"][0] > f2["white_bb"][0] and f2["yellow_bb"][1] < f2["white_bb"][1], True)
    fg = _scan_band("ass.mp4", 80)
    expect("ASS keywords: jeda antar-kartu tanpa caption (frame 80: kuning=0, putih=0)", (fg["yellow"], fg["white"]), (0, 0))
    f3 = _scan_band("ass.mp4", 165)
    g3 = f3["glyph_bb"]
    expect("ASS keywords: kartu3 2-baris aksen > 500, atas 1640±12, bawah 1736±12",
           (f3["yellow"] > 500, bool(g3 and abs(g3[2] - 1640) <= 12), bool(g3 and abs(g3[3] - 1736) <= 12)), (True, True, True))
    # --- unit (tanpa render): escape, warna, pencocokan kata utuh, y, waktu
    expect("ASS unit: escape { } dan baris baru; backslash TIDAK digandakan (F9/C1: libass VM merender \\\\ ganda)",
           render.ass_escape("a{b\\c}d,e\nf") == "a\\{b\\c\\}d,e\\Nf", True)
    expect("ASS unit: aksen #FFD60A -> &H000AD6FF&, black@0.45 -> (0,0,0,0.45)",
           (render.ass_color(render.parse_color("#FFD60A")), render.parse_color("black@0.45")), ("&H000AD6FF&", (0, 0, 0, 0.45)))
    expect("ASS unit: keyword hanya cocok kata UTUH (JERUK tak mewarnai JERUKAN; koma di luar tag)",
           (render.colorize_line("apel JERUKAN mangga", ["JERUK"], "&H000AD6FF&")[1],
            r"{\1c&H000AD6FF&}JERUK{\r}," in render.colorize_line("apel JERUK, mangga", ["jeruk"], "&H000AD6FF&")[0]), (False, True))
    expect("ASS unit: eval_y h-280 = 1640; ass_time 2.5 = 0:00:02.50",
           (render.eval_y("h-280", 1080, 1920), render.ass_time(2.5)), (1640.0, "0:00:02.50"))
    # --- kontrol tanpa keywords: jalur drawtext LAMA (tanpa ass, tanpa berkas .ass, kata tetap putih)
    cfg2 = json.loads(json.dumps(cfg)); cfg2["out"] = "ass_nokw.mp4"; cfg2["work"] = "work_nokw"
    for c in cfg2["cards"]: c.pop("keywords", None)
    json.dump(cfg2, open("ass_nokw.json", "w"))
    p2 = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "ass_nokw.json", "--print"], capture_output=True, text=True)
    p3 = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "ass_nokw.json"], capture_output=True, text=True)
    fn = _scan_band("ass_nokw.mp4", 45) if p3.returncode == 0 else {"yellow": -1}
    expect("ASS kontrol: tanpa keywords -> --print drawtext (bukan ass), render rc 0, kuning=0",
           (p2.returncode, "drawtext=" in p2.stdout, "ass=" not in p2.stdout, p3.returncode,
            fn["yellow"], os.path.exists(os.path.join("work_nokw", "captions.ass"))), (0, True, True, 0, 0, False))


def run_ass_escape(w, expect):
    """C1 / celah ao (F9): kartu berisi `{ } \\` harus tampil LITERAL lewat jalur ASS.
    TEMUAN saat menulis tes ini: kode lama MENGGANDAKAN backslash (`\\` -> `\\\\` di .ass),
    tapi build libass VM merender `\\\\` sebagai DUA backslash (probe: `A\\\\B` -> dua goresan,
    `A\\B` -> satu) — jadi 1 backslash kartu tampil 2 di layar. C1 GAGAL di kode lama untuk
    backslash (kurung `{ }` benar dari awal). Perbaikan: ass_escape tidak lagi menggandakan
    backslash. Tes ini membuktikannya tiga arah: .ass benar + frame dibaca + kontrol kode lama
    (penggandaan) dan tanpa-escape (identitas) keduanya GAGAL pada asersi yang sama."""
    os.chdir(w)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=blue:s=1920x1080:r=30:d=6", "-f", "lavfi", "-i", "sine=f=300:d=6",
        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", "esc_bg.mp4"])
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=250:d=6", "-c:a", "pcm_s16le", "esc_tone.wav"])
    cards = [{"id": 1, "kind": "caption", "text": "harga {diskon} 50% \\ murah",
              "start": 0.5, "end": 2.5, "keywords": ["diskon"]},
             {"id": 2, "kind": "caption", "text": "kode {A} dan {B}",
              "start": 3.0, "end": 5.0, "keywords": []}]
    cfg = {"schema": 2, "out": "esc.mp4", "work": "work_esc", "size": [1080, 1920], "fps": 30,
           "segments": [{"type": "clip", "src": "esc_bg.mp4", "src_in": 0, "dur": 6.0, "mode": "cover"}],
           "audio": {"items": [{"role": "vo", "src": "esc_tone.wav", "at": 0.0}]},
           "cards": cards, "style": {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "size": 46, "border": 3, "box": True, "boxborderw": 20, "y": "h-280"},
           "loudness": {"I": -18, "TP": -3.5, "TP_pass1": -3.0, "LRA": 11}}
    json.dump(cfg, open("esc.json", "w"), indent=1)
    p = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "--config", "esc.json"], capture_output=True, text=True)
    expect("ASS escape C1: render selesai", p.returncode, 0)
    if p.returncode: print(p.stderr[-800:]); return
    apath = os.path.join("work_esc", "captions.ass")
    ass = open(apath, encoding="utf-8").read() if os.path.exists(apath) else ""
    dlg = [m.group(0) for m in re.finditer(r"Dialogue: 0,[^,]+,[^,]+,[^,]+,,0,0,\d+,,(.+)", ass)]
    body = "\n".join(dlg)
    # Hapus tag override yang sah ({\1c...} dan {\r}) lalu pastikan tak ada '{' mentah tersisa.
    stripped = re.sub(r"\{\\1c&H[0-9A-F]+&\}|\{\\r\}", "", body)
    expect("ASS escape C1: .ass mengandung \\{ \\} dan backslash TUNGGAL (bukan ganda)",
           ("\\{" in body and "\\}" in body and "\\\\" not in body), True)
    expect("ASS escape C1: tak ada '{' mentah di luar tag override ('{' tanpa backslash di depannya)",
           re.search(r"(?<!\\)\{", stripped) is None, True)
    expect("ASS escape C1: kata kunci 'diskon' tetap terwarnai",
           r"{\1c&H000AD6FF&}diskon{\r}" in body, True)
    f1 = _scan_band("esc.mp4", 45)
    expect("ASS escape C1: kartu1 glif putih+kuning > 1500 (teks utuh, bukan dimakan libass)",
           f1["white"] + f1["yellow"] > 1500, True)
    sh(["ffmpeg", "-y", "-v", "error", "-i", "esc.mp4", "-vf", "select=eq(n\\,45)",
        "-frames:v", "1", "ass_escape_frame.png"])
    # --- kontrol FAIL-dulu: ass_escape = identitas ---
    # (BS = backslash; dipakai eksplisit agar tidak ada kebingungan escaping di sumber tes.)
    import shutil
    os.makedirs("work_noesc", exist_ok=True)
    BS = chr(92)
    new_ret = ('return text.replace("{", "' + BS * 2 + '{").replace("}", "' + BS * 2
               + '}").replace("' + BS + 'n", "' + BS * 2 + 'N")')
    old_ret = ('return text.replace("' + BS * 2 + '", "' + BS * 4
               + '").replace("{", "' + BS * 2 + '{").replace("}", "' + BS * 2
               + '}").replace("' + BS + 'n", "' + BS * 2 + 'N")')
    assert new_ret in open(os.path.join(HERE, "render.py"), encoding="utf-8").read(), \
        "pola ass_escape baru tidak ditemukan di render.py"
    src = open(os.path.join(HERE, "render.py"), encoding="utf-8").read()
    hacked = os.path.join("work_noesc", "render_noesc.py")
    open(hacked, "w", encoding="utf-8").write(src.replace(new_ret, "return text"))
    cfg2 = json.loads(json.dumps(cfg)); cfg2["out"] = "esc_noesc.mp4"; cfg2["work"] = "work_noesc"
    json.dump(cfg2, open("esc_noesc.json", "w"))
    p2 = subprocess.run([sys.executable, hacked, "--config", "esc_noesc.json"], capture_output=True, text=True)
    expect("ASS escape C1 kontrol: render tanpa-escape selesai (agar frame bisa dibandingkan)", p2.returncode, 0)
    ass2 = open(os.path.join("work_noesc", "captions.ass"), encoding="utf-8").read() if os.path.exists(os.path.join("work_noesc", "captions.ass")) else ""
    dlg2 = [m.group(0) for m in re.finditer(r"Dialogue: 0,[^,]+,[^,]+,[^,]+,,0,0,\d+,,(.+)", ass2)]
    body2 = "\n".join(dlg2)
    stripped2 = re.sub(r"\{\\1c&H[0-9A-F]+&\}|\{\\r\}", "", body2)
    expect("ASS escape C1 kontrol: tanpa-escape, '{diskon}' mentah ADA di .ass (tes yang sama GAGAL)",
           "{diskon}" in stripped2, True)
    f2 = _scan_band("esc_noesc.mp4", 45) if p2.returncode == 0 else {"white": -1, "yellow": -1}
    expect("ASS escape C1 kontrol: tanpa-escape, piksel glif BERKURANG (kata ditelan override)",
           (f2["white"] + f2["yellow"]) < (f1["white"] + f1["yellow"]), True)
    print(f"ASS escape C1: piksel glif dengan-escape={f1['white'] + f1['yellow']}, tanpa-escape={f2['white'] + f2['yellow']}")
    sh(["ffmpeg", "-y", "-v", "error", "-i", "esc_noesc.mp4", "-vf", "select=eq(n\\,45)",
        "-frames:v", "1", "ass_escape_frame_noesc.png"])
    # --- kontrol FAIL-dulu (2): kode LAMA (penggandaan backslash) ---
    os.makedirs("work_oldesc", exist_ok=True)
    hacked_old = os.path.join("work_oldesc", "render_oldesc.py")
    open(hacked_old, "w", encoding="utf-8").write(src.replace(new_ret, old_ret))
    cfg3 = json.loads(json.dumps(cfg)); cfg3["out"] = "esc_oldesc.mp4"; cfg3["work"] = "work_oldesc"
    json.dump(cfg3, open("esc_oldesc.json", "w"))
    p3 = subprocess.run([sys.executable, hacked_old, "--config", "esc_oldesc.json"], capture_output=True, text=True)
    expect("ASS escape C1 kontrol: render kode-lama selesai", p3.returncode, 0)
    ass3 = open(os.path.join("work_oldesc", "captions.ass"), encoding="utf-8").read() if os.path.exists(os.path.join("work_oldesc", "captions.ass")) else ""
    dlg3 = [m.group(0) for m in re.finditer(r"Dialogue: 0,[^,]+,[^,]+,[^,]+,,0,0,\d+,,(.+)", ass3)]
    body3 = "\n".join(dlg3)
    expect("ASS escape C1 kontrol: kode-lama, backslash GANDA di .ass (asersi baru GAGAL di kode lama)",
           "\\\\" in body3, True)
    f3 = _scan_band("esc_oldesc.mp4", 45) if p3.returncode == 0 else {"white": -1, "yellow": -1}
    expect("ASS escape C1 kontrol: kode-lama, piksel glif LEBIH BANYAK (satu backslash ekstra tampil)",
           (f3["white"] + f3["yellow"]) > (f1["white"] + f1["yellow"]), True)
    print(f"ASS escape C1: piksel glif perbaikan={f1['white'] + f1['yellow']}, kode-lama={f3['white'] + f3['yellow']}")
    sh(["ffmpeg", "-y", "-v", "error", "-i", "esc_oldesc.mp4", "-vf", "select=eq(n\\,45)",
        "-frames:v", "1", "ass_escape_frame_oldesc.png"])
