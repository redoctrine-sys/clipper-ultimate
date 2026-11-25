#!/usr/bin/env python3
"""qc_all.py v2 — gate otomatis G-AUTO untuk file FINAL. Menulis qc_report.json; exit 1 bila ada FAIL.
Pakai: python3 qc_all.py --video final.mp4 [--brief brief.json] [--cards cards.json] [--cuts 3.0,4.5]
                         [--exceptions project.json|exceptions.json] [--frames-dir qc_frames] [--out qc_report.json]
Perubahan v2 (dari golden ronde 1): celah kartu min 0,04 dtk — F8.2-c menegakkan lock #9 (dulu: celah 0 SAH,
FAIL hanya bila tumpang-tindih); durasi min dengan toleransi 1 frame;
blackdetect pix_th 0,02 + tahap 2 YMAX (v3: hitam murni FAIL walau dideklarasikan; gelap-berkonten harus dideklarasikan -> WARN); bitrate hanya WARN; pengecualian per-proyek -> WARN (wajib alasan).
Pengecualian: daftar {"check":"digital_silence|frame_hitam","from":s,"to":s,"reason":"..."} (atau kunci `qc_exceptions` di project.json).
Hasil PASS tidak menggantikan G-HUMAN: QC subagent PASS dua kali tetapi user tetap menolak (v1 & v2).
F8.2-b (F7-20): kartu_lint memeriksa LEBAR tiap baris (wrap yang sama dengan render.py, atau lines
eksplisit) dengan metrik font sungguhan (PIL getlength; jatuh-balik 0,62*size*jumlah huruf bila PIL/font
tak ada). Lebar > 1080 -> FAIL; > 1080-2*(boxborderw+20) -> WARN. Cek lebar hanya jalan bila style
diberikan (parameter `style` / CLI --project); tanpa style, perilaku lama (tanpa cek lebar).
F8.2-c (an): celah antar-kartu min 0,04 dtk (lock #9 ditegakkan kartu_lint); celah < 0,04-1e-3 -> FAIL
(toleransi 1e-3: celah 0,04 yang terhitung 0,0399999... dari pembulatan 3 desimal bukan FAIL).
Pengecualian legacy: kartu dengan `legacy_gap0: true` + `legacy_gap0_reason` tak kosong -> WARN
(khusus GR-1 golden); penanda tanpa alasan -> tetap FAIL.
F11 (jalur landscape): check_format menerima UKURAN HARAPAN. Tanpa --project -> 1080x1920 (perilaku lama).
Dengan --project -> `size` project; hanya dua ukuran sah (daftar putih 1080x1920 / 1920x1080 — tanpa daftar
putih, salah ketik `size` lolos karena renderer dan QC membaca angka yang sama). Dengan --brief ->
orientasi ukuran harus sama dengan brief.orientasi (tidak ada = portrait); beda -> FAIL.
Pemanggil langsung (selftest) tanpa atribut exp_size/exp_err -> default 1080x1920 seperti lama."""
import argparse, json, os, re, subprocess, sys

try:
    from render import wrap as _render_wrap
except ImportError:  # qc_all disalin tanpa render.py: salinan wrap yang sama (jangan diubah terpisah)
    def _render_wrap(text, n):
        if len(text) <= n: return [text]
        ws, tot, acc, best, bi = text.split(), len(text), 0, None, 0
        for i, w in enumerate(ws[:-1]):
            acc += len(w) + (1 if i else 0)
            if best is None or abs(acc - tot / 2) < best: best, bi = abs(acc - tot / 2), i
        return [" ".join(ws[:bi + 1]), " ".join(ws[bi + 1:])]

_FONT_CACHE = {}
def line_width(line, size, font):
    """Lebar satu baris teks (px) + metode ukur ('PIL' / 'estimasi-0.62'). F8.2-b."""
    key = (size, str(font))
    if key not in _FONT_CACHE:
        f = None
        try:
            from PIL import ImageFont
            if font and os.path.exists(str(font)):
                f = ImageFont.truetype(str(font), int(size))
        except Exception:
            f = None
        _FONT_CACHE[key] = f
    f = _FONT_CACHE[key]
    if f is not None:
        return f.getlength(line), "PIL"
    return 0.62 * size * len(line), "estimasi-0.62"

FPS = 30.0
def run(cmd): p = subprocess.run(cmd, capture_output=True, text=True); return p.returncode, p.stdout, p.stderr

def probe(path):
    rc, out, err = run(["ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate:format=duration,bit_rate", "-of", "json", path])
    if rc: sys.exit("ffprobe gagal: " + err[:300])
    return json.loads(out)

def ratio(s): a, b = s.split("/"); return float(a) / float(b) if float(b) else 0.0
def chk(cid, status, detail, **ev): return {"id": cid, "status": status, "detail": detail, "bukti": ev}

def check_format(pr, a):
    v = next((s for s in pr["streams"] if s["codec_type"] == "video"), {}); au = next((s for s in pr["streams"] if s["codec_type"] == "audio"), {})
    fps = ratio(v.get("r_frame_rate", "0/1")); br = float(pr["format"].get("bit_rate", 0)) / 1e6; bad = []
    exp = tuple(getattr(a, "exp_size", (1080, 1920))); experr = getattr(a, "exp_err", None)  # F11: ukuran harapan (default = perilaku lama)
    if v.get("codec_name") != "h264": bad.append(f"video={v.get('codec_name')}")
    if au.get("codec_name") != "aac": bad.append(f"audio={au.get('codec_name')}")
    if experr: bad.append(experr)
    if (v.get("width"), v.get("height")) != exp: bad.append(f"ukuran={v.get('width')}x{v.get('height')} (harap {exp[0]}x{exp[1]})")
    if abs(fps - 30) > 0.01: bad.append(f"fps={fps:.2f}")
    if v.get("pix_fmt") != "yuv420p": bad.append(f"pix_fmt={v.get('pix_fmt')}")
    r = [chk("format", "FAIL" if bad else "PASS", "; ".join(bad) or f"h264+aac {exp[0]}x{exp[1]} 30fps yuv420p", fps=fps)]
    lo, hi = a.bitrate * (1 - a.tol_bitrate), a.bitrate * (1 + a.tol_bitrate)
    ok = lo <= br <= hi
    r.append(chk("bitrate", "PASS" if ok else "WARN",
                 f"{br:.2f} Mbps (target {a.bitrate}±{a.tol_bitrate*100:.0f}%; diukur dari konten gerak — konten dominan stills wajar lebih rendah; bitrate tidak pernah FAIL)", mbps=round(br, 3)))
    return r, float(pr["format"]["duration"])

def check_duration(d, brief):
    dd = (brief or {}).get("duration", {}); lo, hi = dd.get("min_s"), dd.get("max_s")
    if lo is None and hi is None: return chk("durasi", "WARN", f"{d:.2f}s — brief tidak diberikan/tanpa batas durasi")
    ok = (lo is None or d >= lo) and (hi is None or d <= hi)
    return chk("durasi", "PASS" if ok else "FAIL", f"{d:.2f}s (brief {lo}–{hi}s)", durasi=round(d, 3))

def check_loudness(path, a):
    rc, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "loudnorm=I=-18:TP=-3.5:LRA=11:print_format=json", "-f", "null", "-"])
    js = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
    if not js: return chk("loudness", "FAIL", "tidak bisa mengukur loudness")
    m = json.loads(js[-1]); i, tp = float(m["input_i"]), float(m["input_tp"]); bad = []
    if abs(i - (-18)) > a.tol_lufs: bad.append(f"I={i:.1f} LUFS (target -18±{a.tol_lufs})")
    if tp > a.tp_max: bad.append(f"TP={tp:.1f} dBTP (maks {a.tp_max})")
    return chk("loudness", "FAIL" if bad else "PASS", "; ".join(bad) or f"I={i:.2f} LUFS, TP={tp:.2f} dBTP", I=i, TP=tp, LRA=m.get("input_lra"))

def apply_exceptions(cid, spans, exc, label):
    """spans [(s,e)] -> (uncovered, covered[(s,e,alasan)]). Pengecualian tanpa alasan diabaikan."""
    unc, cov = [], []
    for s, e in spans:
        m = next((x for x in exc if x.get("check") == cid and x.get("reason") and x["from"] - 0.15 <= s and e <= x["to"] + 0.15), None)
        (cov.append((s, e, m["reason"])) if m else unc.append((s, e)))
    if unc: return chk(cid, "FAIL", f"{len(unc)} rentang {label} TANPA pengecualian: " + ", ".join(f"{s:.2f}–{e:.2f}" for s, e in unc), rentang=unc, dikecualikan=cov)
    if cov: return chk(cid, "WARN", f"{len(cov)} rentang {label} DIKECUALIKAN (dideklarasikan): " + "; ".join(f"{s:.2f}–{e:.2f} ({r})" for s, e, r in cov), dikecualikan=cov)
    return chk(cid, "PASS", f"tidak ada {label}")

def silence_spans(path, d):
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "silencedetect=n=-90dB:d=0.3", "-vn", "-f", "null", "-"])[2]
    res, s = [], None
    for l in err.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", l)
        if m: s = max(float(m.group(1)), 0.0); continue
        m = re.search(r"silence_end: ([\d.]+)", l)
        if m and s is not None: res.append((s, float(m.group(1)))); s = None
    if s is not None: res.append((s, d))  # hening sampai akhir file
    return res

def black_spans(path, pix_th, d_min=0.04):
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vf", f"blackdetect=d={d_min}:pic_th=0.98:pix_th={pix_th}", "-an", "-f", "null", "-"])[2]
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]

def check_silence(path, d, exc): return apply_exceptions("digital_silence", silence_spans(path, d), exc, "hening digital ≥0,3s (−90 dB)")

def ymax_samples(path, s, e):
    """YMAX (luma maks) frame-frame pada rentang [s,e] — tahap 2 deteksi hitam. Rentang pendek: semua frame; panjang: 5 fps."""
    vf = ("" if e - s <= 1.5 else "fps=5,") + "signalstats,metadata=print:key=lavfi.signalstats.YMAX:file=-"
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "error", "-ss", f"{max(s,0):.3f}", "-t", f"{max(e-s,0.04):.3f}", "-i", path,
                        "-vf", vf, "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [float(x) for x in re.findall(r"lavfi\.signalstats\.YMAX=([\d.]+)", p.stdout)]

def check_black(path, exc, pix_th=0.02, ymax_th=64.0, d_min=0.04):
    """Dua tahap. (1) blackdetect -> rentang kandidat. (2) YMAX per rentang membedakan:
         hitam_murni    : tidak ada piksel terang (mis. freeze tpad hitam)          -> FAIL, deklarasi TIDAK menyelamatkan
         gelap_berkonten: ≥50% sampel punya YMAX ≥ ymax_th (poster gelap + teks/logo) -> FAIL bila tak dideklarasikan, WARN bila dideklarasikan
       Deklarasi = qc_exceptions {"check":"frame_hitam","from","to","reason"} (alasan wajib; rentang ±0,15). Ambang YMAX 64 [T: kalibrasi di VM]."""
    rows, bad, warn = [], [], []
    for s, e in black_spans(path, pix_th, d_min):
        ys = ymax_samples(path, s, e); frac = sum(y >= ymax_th for y in ys) / len(ys) if ys else 0.0
        kelas = "gelap_berkonten" if ys and frac >= 0.5 else "hitam_murni"
        m = next((x for x in exc if x.get("check") == "frame_hitam" and x.get("reason") and x["from"] - 0.15 <= s and e <= x["to"] + 0.15), None)
        rows.append({"dari": round(s, 3), "sampai": round(e, 3), "kelas": kelas, "sampel": len(ys), "ymax_maks": max(ys) if ys else None, "frac_konten": round(frac, 2), "deklarasi": m["reason"] if m else None})
        if kelas == "hitam_murni": bad.append(f"{s:.2f}–{e:.2f} HITAM MURNI (YMAX maks {max(ys) if ys else '?'} < {ymax_th}; deklarasi tidak berlaku)")
        elif not m: bad.append(f"{s:.2f}–{e:.2f} gelap-berkonten TANPA deklarasi")
        else: warn.append(f"{s:.2f}–{e:.2f} gelap-berkonten dideklarasikan ({m['reason']})")
    if bad: return chk("frame_hitam", "FAIL", "; ".join(bad), rentang=rows)
    if warn: return chk("frame_hitam", "WARN", "; ".join(warn) + " — periksa frame di G-HUMAN", rentang=rows)
    return chk("frame_hitam", "PASS", "tidak ada frame hitam")

GAP_MIN = 0.04   # F8.2-c (an): celah antar-kartu minimum, lock #9 — ditegakkan kartu_lint
GAP_TOL = 1e-3   # toleransi float: celah 0,04 yang terhitung 0,0399999... dari pembulatan 3 desimal bukan FAIL

def check_cards(cards, cuts, d, fps=FPS, zones=None, style=None, W=1080):
    """Aturan terkunci v2: 2–7 kata; min 1,0s (judul 1,5s) dengan toleransi 1 frame; FAIL bila tumpang-tindih;
    F8.2-c: celah antar-kartu < GAP_MIN - GAP_TOL -> FAIL (pengecualian legacy_gap0 + alasan -> WARN).
    F8.2-b: bila `style` diberikan, lebar tiap baris (lines eksplisit, atau wrap yang sama dengan render.py)
    diukur dengan metrik font sungguhan; lebar > W -> FAIL, > W - 2*(boxborderw+20) -> WARN.
    Tanpa `style` -> cek lebar dilewati (perilaku lama).
    v4.2-zona (F6-A2, Opus-8): satu kartu = satu panel — kartu yang melewati zona panel/xfade
    (parameter `zones`, list [start,end]; toleransi 1e-3 sama seperti hard cut) = FAIL. Tanpa zones -> perilaku lama."""
    tol, bad, warns = 1.0 / fps + 1e-6, [], []
    cs = sorted(cards, key=lambda c: c["start"])
    for i, c in enumerate(cs):
        n, du = len(c["text"].split()), c["end"] - c["start"]
        if c.get("kind", "caption") == "caption":
            if not 2 <= n <= 7: bad.append(f"#{c['id']}: {n} kata (harus 2–7)")
            if du < 1.0 - tol: bad.append(f"#{c['id']}: {du:.3f}s < 1,0s (toleransi 1 frame)")
        elif du < 1.5 - tol: bad.append(f"#{c['id']}: judul {du:.3f}s < 1,5s (harus sempat terbaca)")
        if c["end"] > d + tol: bad.append(f"#{c['id']}: melewati akhir video")
        if i:
            gap = c["start"] - cs[i - 1]["end"]
            if gap < -1e-3: bad.append(f"#{c['id']}: TUMPANG-TINDIH dengan #{cs[i-1]['id']} ({cs[i-1]['end']-c['start']:.3f}s)")
            elif gap < GAP_MIN - GAP_TOL:
                if c.get("legacy_gap0") is True and str(c.get("legacy_gap0_reason") or "").strip():
                    warns.append(f"#{c['id']}: celah {gap:.3f}s < 0,04 DIKECUALIKAN legacy_gap0 ({c['legacy_gap0_reason']})")
                elif c.get("legacy_gap0") is True:
                    bad.append(f"#{c['id']}: celah {gap:.3f}s < 0,04; legacy_gap0 TANPA alasan (alasan wajib)")
                else:
                    bad.append(f"#{c['id']}: celah {gap:.3f}s < 0,04 (min lock #9)")
        for t in cuts:
            if c["start"] + 1e-3 < t < c["end"] - 1e-3: bad.append(f"#{c['id']}: melewati hard cut {t}s")
        for z0, z1 in (zones or []):
            if c["start"] + 1e-3 < z1 and c["end"] - 1e-3 > z0: bad.append(f"#{c['id']}: melewati zona panel/xfade {z0}–{z1}s")
        if style is not None:  # F8.2-b: lebar baris (hanya bila style diberikan)
            size = c.get("size") or ((style.get("title_size", 54) if c.get("kind") == "title" else style.get("size", 46)))
            lines = c.get("lines") or _render_wrap(c["text"], style.get("wrap", 28))
            font = style.get("font") or os.environ.get("CAPTION_FONT")
            bbw = c.get("boxborderw", style.get("boxborderw", 20))
            for ln in lines:
                wpx, meth = line_width(ln, size, font)
                if wpx > W: bad.append(f"#{c['id']}: baris {ln!r} {wpx:.0f}px > {W}px (lebar frame; ukur {meth})")
                elif wpx > W - 2 * (bbw + 20): warns.append(f"#{c['id']}: baris {ln!r} {wpx:.0f}px > {W - 2*(bbw+20):.0f}px (kotak mepet tepi; ukur {meth})")
    if bad: return chk("kartu_lint", "FAIL", "; ".join(bad), gagal=bad, peringatan=warns)
    if warns: return chk("kartu_lint", "WARN", "; ".join(warns) + f" — {len(cs)} kartu", peringatan=warns)
    return chk("kartu_lint", "PASS", f"{len(cs)} kartu sesuai aturan terkunci")

def frames(path, cuts, d, outdir):
    os.makedirs(outdir, exist_ok=True); ts = [0.0] + [x for t in cuts for x in (t - 0.06, t + 0.06)] + [max(d - 0.1, 0)]; made = []
    for t in ts:
        f = os.path.join(outdir, f"t{t:07.3f}.jpg")
        if run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(t,0):.3f}", "-i", path, "-frames:v", "1", "-q:v", "3", f])[0] == 0: made.append(f)
    return chk("frame_junction", "MANUAL", f"{len(made)} frame untuk diperiksa mata (awal, tiap junction ±0,06s, akhir): kartu tidak menutupi objek kunci, scene akhir utuh, tidak ada tempelan", frames=made)

def load_exceptions(path):
    if not path: return []
    j = json.load(open(path, encoding="utf-8")); return j.get("qc_exceptions", []) if isinstance(j, dict) else j

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--brief"); ap.add_argument("--cards")
    ap.add_argument("--cuts", default=""); ap.add_argument("--frames-dir"); ap.add_argument("--out", default="qc_report.json"); ap.add_argument("--exceptions")
    ap.add_argument("--zones", help="file JSON list [start,end] zona panel/xfade (satu kartu = satu panel; kartu yang melewatinya = FAIL)")
    ap.add_argument("--project", help="project.json: style (font/wrap/size/boxborderw) + size dipakai kartu_lint untuk cek lebar baris (F8.2-b); tanpa ini cek lebar dilewati")
    ap.add_argument("--bitrate", type=float, default=3.4); ap.add_argument("--tol-bitrate", type=float, default=0.10)
    ap.add_argument("--tol-lufs", type=float, default=1.0); ap.add_argument("--tp-max", type=float, default=-3.0)
    ap.add_argument("--black-pix-th", type=float, default=0.02); ap.add_argument("--black-ymax", type=float, default=64.0)
    a = ap.parse_args(); brief = json.load(open(a.brief)) if a.brief else None
    cuts = [float(x) for x in a.cuts.split(",") if x]; exc = load_exceptions(a.exceptions)
    zones = [tuple(map(float, z)) for z in json.load(open(a.zones, encoding="utf-8"))] if a.zones else None
    pj = json.load(open(a.project, encoding="utf-8")) if a.project else None  # F11: project dimuat sekali, dipakai format + kartu_lint
    # F11: ukuran harapan check_format. Tanpa --project -> 1080x1920. Dengan --project -> `size` (daftar putih
    # dua ukuran). Dengan --brief -> orientasi ukuran harus sama dengan brief.orientasi (kosong = portrait).
    exp, experr = (1080, 1920), None
    if pj is not None:
        sz = pj.get("size") or [1080, 1920]; exp = (int(sz[0]), int(sz[1]))
        if exp not in ((1080, 1920), (1920, 1080)):
            experr = f"size project {exp[0]}x{exp[1]} di luar daftar putih (hanya 1080x1920 / 1920x1080)"
    if brief is not None:
        ori = brief.get("orientasi") or "portrait"; ori_size = "landscape" if exp[0] > exp[1] else "portrait"
        if ori != ori_size:
            msg = f"orientasi brief '{ori}' tidak cocok dengan ukuran {exp[0]}x{exp[1]} (orientasi '{ori_size}')"
            experr = f"{experr}; {msg}" if experr else msg
    a.exp_size, a.exp_err = exp, experr
    r, d = check_format(probe(a.video), a)
    r += [check_duration(d, brief), check_loudness(a.video, a), check_silence(a.video, d, exc), check_black(a.video, exc, a.black_pix_th, a.black_ymax)]
    if a.cards:
        c = json.load(open(a.cards)); style, Wd = None, 1080
        if pj is not None:
            style = pj.get("style") or {}
            Wd = (pj.get("size") or [1080, 1920])[0]
        r.append(check_cards(c["cards"] if isinstance(c, dict) else c, cuts, d, zones=zones, style=style, W=Wd))
    if a.frames_dir: r.append(frames(a.video, cuts, d, a.frames_dir))
    r.append(chk("G-HUMAN", "MANUAL", "wajib: review manusia (review-sheet.md). Hasil otomatis tidak menggantikan keputusan user."))
    json.dump({"video": os.path.basename(a.video), "durasi": round(d, 3), "pengecualian": exc, "cek": r}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for x in r: print(f"{x['status']:<6} {x['id']:<16} {x['detail']}")
    sys.exit(1 if any(x["status"] == "FAIL" for x in r) else 0)
