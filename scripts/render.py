#!/usr/bin/env python3
"""render.py v5-F6 — render final dari DATA (project.json, skema 2) dengan ffmpeg. Satu-satunya renderer skill ini.
Tahap: video (tanpa audio) -> audio (mix) -> loudnorm 2-pass -> mux AAC.
Pakai: python3 render.py --config project.json [--print] [--stage all|video|audio|mux]    (--print = hanya cetak perintah)

KUNCI v2 (dari golden ronde 1)
- Timeline dihitung dalam FRAME dari batas ABSOLUT: tiap segmen dipaksa tepat N frame (N = round(end*fps) - round(start*fps)),
  sumber dikonversi ke fps proyek (CFR) lebih dulu. Tak ada akumulasi pembulatan 24->30 fps.
- Segmen: clip | freeze (bekukan frame sumber di src_in) | still (gambar + zoom, SELALU cover — mode
  fit/blurpad/crop pada still ditolak preflight rc 2, F7-19/F8.2-a; pre-fit PNG 1080x1920 dulu).
  Mode (clip/freeze): crop (x/y/w/h tetap ATAU {"from","to"} = pan linear),
  cover, fit (skala ke lebar + bar pad_color), blurpad. Transisi antar segmen: "transition_in":{"type":"fade","dur":0.5} (xfade).
  Posisi segmen: start_k = akhir_{k-1} - dur_transisi_k (offset xfade = start_k). `at` opsional = asersi posisi mulai.
- AUDIO TERPISAH DARI VIDEO: daftar `audio.items` (role source|vo|music|sfx, src, src_in, at, dur, gain_db, fade_in, fade_out, loop).
  Audio sumber boleh diambil dari offset berbeda dari videonya. Tiap item di-pad ke durasi total -> musik tak terpotong saat VO habis.
  Ducking: audio.duck {key:[roles], target:[roles], threshold, ratio, attack, release, makeup}. Fade master: audio.master.fade_out {start,dur}.
- Kartu: SATU drawtext per kartu (multi-baris, text_align), kotak (box) + boxborderw, interval setengah terbuka gte(t,a)*lt(t,b)
  (between() DILARANG: inklusif di kedua ujung). Override per kartu: size, y, lines.
- Freeze/hold = frame sumber (freeze) atau PNG (still). `tpad` default (stop_mode=add) menambah frame HITAM — hanya dipakai internal
  dengan stop_mode=clone untuk menutup selisih <1 frame.
v3: HAPUS atrim di akhir rantai audio per item DAN di bus akhir (ronde 2: atrim=duration=T setelah adelay pada input MP4 dengan -ss
menggeser/memotong audio; di sandbox ffmpeg 6.1.1 atrim setelah amix memotong mix jadi 4 dtk). Panjang dijamin apad=whole_dur per item + `-t T` pada keluaran mix.
v4: segmen `type:"color"` ({"color":"black","dur":..}) = warna polos dari lavfi, TANPA berkas (pengganti still black.png yang rapuh);
PREFLIGHT: semua berkas masukan (segmen, audio, font, cards) diperiksa sebelum ffmpeg -> kode keluar 2 + daftar berkas hilang.
v4.1-fix-range: normalisasi range TV (`scale=out_range=tv`) di AKHIR graf video, sesudah gabung segmen
(xfade/concat) dan sebelum drawtext (K2.10 FAIL format yuvj420p: xfade mengeluarkan full-range dari still
PNG pc-range; `-pix_fmt yuv420p` di akhir tidak menyelamatkan karena libx264 menerima yuvj420p langsung).
No-op untuk sumber TV-range (klip K1/golden); dibuktikan regression test work/regression_range/.
v4.2-F6: (a) direktori output dibuat bila belum ada, sesudah preflight dan sebelum semua stage (dulu mux gagal
kode 254 bila dir out tak ada, K2.9; berlaku juga untuk --stage mux saja); (e) kunci `style` hilang tidak lagi
KeyError di cards_filters (default {} bila tanpa kartu; bila ada kartu, error font tetap jelas, bukan KeyError).
Kasus regresi baru di selftest_render.py: still(JPG)->xfade harus yuv420p (celah yang membuat bug range lolos v0.4).
v5-F6 (K3, caption ASS): kartu boleh membawa `keywords` (0-2 kata per kartu, di cards.json); bila ADA kartu
ber-keywords, SEMUA kartu dirender lewat SATU filter ASS (`ass=`, berkas work/captions.ass) menggantikan drawtext,
kata kunci diwarnai aksen (style.accent, default #FFD60A) lewat tag inline {\\1c...}kata{\\r}, kata lain warna
caption biasa; timing SAMA dengan drawtext (interval kartu yang sama, presisi ASS 0,01 dtk). Tanpa keywords di
kartu mana pun -> jalur drawtext LAMA, perintah --print identik v4.2 (dibuktikan diff kosong K1/K2).
Kalibrasi ASS vs drawtext (diukur piksel, VM, DejaVuSans-Bold): fontsize ASS = round(size*1.172) (lebar glif
sama: ASS fs54 = drawtext 46 -> 161 vs 160 px; fs75 = drawtext 64 -> 223 vs 223 px); MarginV =
H - y_atas - round(0.85*ass_fs) - (nbaris-1)*ass_fs (atas glif baris-1 sama dengan y drawtext +/-2 px pada
ukuran 46/64, 1-2 baris). Perbedaan yang TERSISA dan didokumentasikan (celah aj): (1) kotak ASS (BorderStyle=3)
lebih ketat (padding ~7 px vs boxborderw 20) DAN selalu hitam pekat — alfa BackColour diabaikan libass build ini
(uji: alfa 00/80/FF semua memberi interior (0,0,0)); (2) jarak antar-baris ASS ~1.0*ass_fs vs drawtext
size+line_spacing (62 px pada size 46) — baris ke-2 ASS ~8 px lebih rapat; (3) presisi waktu ASS 0,01 dtk
(maks 5 ms dari interval drawtext, < 1 frame). Font ASS: family dibaca dari fontfile lewat fc-scan
(jatuh-balik heuristik nama berkas); fontsdir = direktori fontfile dilewatkan ke filter ass agar font yang
SAMA dengan drawtext yang dipakai, tanpa bergantung pada cache fontconfig. Escape ASS: {, } + baris baru -> \\N;
backslash TIDAK digandakan — build libass VM merender `\\` sebagai dua backslash (probe F9/C1), lihat ass_escape;
koma TIDAK diescape (legal sebagai medan terakhir Dialogue); baris baru -> \\N. Keyword dicocokkan per kata
utuh (case-insensitive, tanda baca tepi diabaikan); keyword yang tak ditemukan di teks hanya diperingatkan
di stderr, kartu tetap dirender satu warna.
Lihat templates/project.example.json."""
import argparse, json, os, re, shlex, subprocess, sys

def q(p): return "'" + str(p).replace("\\", "/").replace(":", "\\:") + "'"
def f3(x): return f"{x:.3f}"


def preflight(cfg):
    """Daftar berkas masukan yang HILANG (segmen non-color, audio.items, font kartu, cards.json). [] bila lengkap.
    F8.2-a (F7-19): segmen still yang membawa mode selain cover juga DITOLAK di sini (bukan diam-diam
    diabaikan): vchain() still tidak pernah membaca mode, jadi mode fit/blurpad/crop pada still
    hanya akan menghasilkan cover tanpa peringatan. Pesan persis, rc 2 via main()."""
    miss = []
    def need(path, what):
        if path and not os.path.exists(str(path)): miss.append(f"{what}: {path}")
    for k, s in enumerate(cfg["segments"]):
        if s.get("type") == "still" and s.get("mode") not in (None, "cover"):
            miss.append("still hanya mendukung cover; pre-buat PNG 1080×1920 untuk fit/blurpad")
        if s.get("type") != "color": need(s.get("src"), f"segmen {k} src")
        elif not s.get("color"): miss.append(f"segmen {k}: type=color butuh kunci 'color'")
    for n, it in enumerate((cfg.get("audio") or {}).get("items") or []): need(it.get("src"), f"audio item {n} src")
    c = cfg.get("cards")
    if isinstance(c, str): need(c, "cards")
    try: cards = load_cards(cfg) if (not isinstance(c, str) or os.path.exists(c)) else []
    except Exception as e: miss.append(f"cards tidak terbaca: {e}"); cards = []
    if cards:
        font = (cfg.get("style") or {}).get("font") or os.environ.get("CAPTION_FONT")
        if not font: miss.append("font kartu belum diset (style.font atau env CAPTION_FONT)")
        else: need(font, "font")
    return miss

# ------------------------------------------------------------------ timeline
def normalize(cfg):
    for s in cfg["segments"]:
        if "end" in s and "dur" not in s: s["dur"] = s["end"] - s["start"]          # skema v1
        if "start" in s and "src_in" not in s: s["src_in"] = s["start"]
    return cfg

def timeline(cfg):
    """-> list {start,end,S,E,N,Tf,trans}; S/E frame absolut. Error bila `at` tak cocok."""
    fps = cfg.get("fps", 30); out, prev_end = [], 0.0
    for k, s in enumerate(cfg["segments"]):
        tr = s.get("transition_in") if k else None; td = tr["dur"] if tr else 0.0
        st = prev_end - td if k else 0.0; en = st + s["dur"]
        if "at" in s and abs(s["at"] - st) > 1.0 / fps + 1e-6: sys.exit(f"segmen {k}: at={s['at']} != posisi terhitung {st:.3f} (dur+transisi sebelumnya)")
        S, E = round(st * fps), round(en * fps)
        if E - S < 1: sys.exit(f"segmen {k}: durasi < 1 frame")
        Tf = (out[-1]["E"] - S) if k else 0
        if k and tr and Tf < 1: sys.exit(f"segmen {k}: transisi < 1 frame")
        if k and not tr and Tf != 0: Tf = 0; S = out[-1]["E"]; E = S + (E - round(st * fps))
        out.append({"start": st, "end": en, "S": S, "E": E, "N": E - S, "Tf": Tf, "trans": tr}); prev_end = en
    return out

# ------------------------------------------------------------------ video
def ex(v, D):
    """angka tetap atau {"from","to"} -> ekspresi crop (t = detik dari awal segmen)."""
    if isinstance(v, dict): a, b = v["from"], v["to"]; return f"{a}+({b}-{a})*min(t/{D:.4f},1)"
    return str(v)

def mode_chain(s, W, H, D):
    mode = s.get("mode", "crop")
    if mode == "crop":
        c = s["crop"]; return f"crop=w={ex(c['w'], D)}:h={ex(c['h'], D)}:x='{ex(c['x'], D)}':y='{ex(c.get('y', 0), D)}':exact=0,scale={W}:{H}:flags=lanczos,setsar=1"
    if mode == "cover": return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
    if mode == "fit":
        h = s.get("fit_h", -2); return f"scale={W}:{h}:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={s.get('pad_color','black')},setsar=1"
    if mode == "blurpad":
        return (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:5[g];"
                f"[b]scale={W}:-2[f];[g][f]overlay=(W-w)/2:(H-h)/2,setsar=1")
    sys.exit(f"mode segmen tidak dikenal: {mode}")

def vchain(i, s, tl, W, H, fps):
    N, D = tl["N"], tl["N"] / fps; end = f"format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={N},setpts=PTS-STARTPTS,settb=1/{fps}"
    t = s["type"]
    if t == "color": return f"[{i}:v]fps={fps},setsar=1,{end}[v{i}]"
    if t == "still":
        z0, z1 = s.get("zoom", [1, 1]); fx, fy = s.get("focus", [0.5, 0.5])
        if z0 == z1 == 1: body = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}"
        else:
            body = (f"scale={2*W}:{2*H}:force_original_aspect_ratio=increase,crop={2*W}:{2*H},"
                    f"zoompan=z='{z0}+({z1}-{z0})*on/{max(N-1,1)}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d=1:s={W}x{H}:fps={fps},setsar=1")
        return f"[{i}:v]{body},{end}[v{i}]"
    if t == "freeze":
        mc = mode_chain(s, W, H, D)
        if s.get("mode") == "blurpad": mc = mc.replace("[a]", f"[a{i}]").replace("[b]", f"[b{i}]").replace("[g]", f"[g{i}]").replace("[f]", f"[f{i}]").replace("split[a", f"split[a")
        return f"[{i}:v]fps={fps},trim=end_frame=1,setpts=PTS-STARTPTS,{mc},loop=loop={N}:size=1:start=0,{end}[v{i}]"
    mc = mode_chain(s, W, H, D)
    if s.get("mode") == "blurpad":
        return (f"[{i}:v]fps={fps},setpts=PTS-STARTPTS,split[a{i}][b{i}];[a{i}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:5[g{i}];"
                f"[b{i}]scale={W}:-2[f{i}];[g{i}][f{i}]overlay=(W-w)/2:(H-h)/2,setsar=1,{end}[v{i}]")
    return f"[{i}:v]fps={fps},setpts=PTS-STARTPTS,{mc},{end}[v{i}]"

def load_cards(cfg):
    c = cfg.get("cards")
    if isinstance(c, str): c = json.load(open(c, encoding="utf-8"))
    return (c["cards"] if isinstance(c, dict) else c) or []

def wrap(text, n):
    if len(text) <= n: return [text]
    ws, tot, acc, best, bi = text.split(), len(text), 0, None, 0
    for i, w in enumerate(ws[:-1]):
        acc += len(w) + (1 if i else 0)
        if best is None or abs(acc - tot / 2) < best: best, bi = abs(acc - tot / 2), i
    return [" ".join(ws[:bi + 1]), " ".join(ws[bi + 1:])]

def cards_filters(cfg, work, total_s, write):
    st = cfg.get("style") or {}  # v4.2-F6 (e): default {} bila kunci style hilang (dulu KeyError di sini)
    cards = load_cards(cfg)
    font = st.get("font") or os.environ.get("CAPTION_FONT")
    if cards and not font: sys.exit("font kartu belum diset (style.font atau env CAPTION_FONT)")
    out = []
    for c in cards:
        if c["start"] >= total_s: continue
        end = min(c["end"], total_s)
        size = c.get("size") or (st.get("title_size", 54) if c.get("kind") == "title" else st.get("size", 46))
        y = c.get("y") or st.get("y", "h-280"); lines = c.get("lines") or wrap(c["text"], st.get("wrap", 28))
        fp = os.path.join(work, f"card_{int(c['id']):03d}.txt")
        if write: open(fp, "w", encoding="utf-8").write("\n".join(lines))
        o = [f"fontfile={q(font)}", f"textfile={q(fp)}", "expansion=none", f"fontsize={size}", f"fontcolor={st.get('color','white')}",
             f"borderw={st.get('border',3)}", f"bordercolor={st.get('bordercolor','black')}", "x='(w-text_w)/2'", f"y='{y}'", f"line_spacing={st.get('line_spacing',8)}"]
        if st.get("box", True): o += ["box=1", f"boxcolor={st.get('boxcolor','black@0.45')}", f"boxborderw={c.get('boxborderw', st.get('boxborderw',20))}"]
        if st.get("text_align", "center") != "none": o.append(f"text_align={st.get('text_align','center')}")
        o.append(f"enable='gte(t,{f3(c['start'])})*lt(t,{f3(end)})'")  # setengah terbuka: ujung akhir eksklusif
        out.append("drawtext=" + ":".join(o))
    return out

# ------------------------------------------------------------------ caption ASS (v5-F6, K3)
ASS_FS_FACTOR = 1.172   # terkalibrasi: lebar glif ASS(fs) == drawtext(size) bila fs = round(size*1.172)
ASS_TOP_FACTOR = 0.85   # jarak atas-glif ke bawah blok satu baris, sebagai fraksi ass_fs
ASS_ACCENT_DEFAULT = "#FFD60A"  # kuning sorot; kontras vs putih di atas kotak hitam, satu warna per proyek (K3 §8)
ASS_LINE_FACTOR = 1.0   # jarak antar-baris ASS, sebagai fraksi ass_fs (terukur 54 px pada fs54)

_NAMED_COLORS = {"white": (255, 255, 255), "black": (0, 0, 0), "yellow": (255, 255, 0),
                 "red": (255, 0, 0), "green": (0, 128, 0), "blue": (0, 0, 255), "cyan": (0, 255, 255),
                 "magenta": (255, 0, 255), "orange": (255, 165, 0), "gray": (128, 128, 128),
                 "grey": (128, 128, 128), "purple": (128, 0, 128), "pink": (255, 192, 203),
                 "brown": (165, 42, 42), "lime": (0, 255, 0), "navy": (0, 0, 128), "teal": (0, 128, 128)}

def parse_color(s):
    """Warna gaya (nama / #RRGGBB / 0xRRGGBB / RRGGBB, opsional '@alfa') -> (r,g,b,alfa 0..1) atau None."""
    if not isinstance(s, str): return None
    s = s.strip()
    alpha = 1.0
    if "@" in s:
        s, a = s.rsplit("@", 1)
        try: alpha = float(a)
        except ValueError: return None
    if s.lower() in _NAMED_COLORS: return (*_NAMED_COLORS[s.lower()], alpha)
    h = s[1:] if s.startswith("#") else (s[2:] if s.lower().startswith("0x") else s)
    if len(h) == 6 and all(c in "0123456789abcdefABCDEF" for c in h):
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    return None

def ass_color(rgb):
    """(r,g,b,alfa) -> warna ASS &HAABBGGRR& (AA=00 pekat, FF transparan)."""
    r, g, b, a = rgb
    aa = round((1.0 - max(0.0, min(1.0, a))) * 255)
    return f"&H{aa:02X}{b:02X}{g:02X}{r:02X}&"

def ass_escape(text):
    """Escape teks Dialogue ASS: {, }; baris baru -> \\N. Koma TIDAK diescape (legal di medan terakhir).
    Backslash TIDAK digandakan: build libass di VM ini merender `\\\\` sebagai DUA backslash
    (diuji probe F9/C1: `A\\\\B` -> dua goresan, `A\\B` -> satu; `\\{` -> `{`, `\\N` -> baris baru).
    Menggandakan justru merusak teks kartu (celah ao: 1 backslash tampil 2). Sisa tepi yang
    diterima: `\\` sebelum N/n/{/} kehilangan backslash; praktis tidak pernah muncul di
    ucapan (ditangkap QC frame bila muncul)."""
    return text.replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")

def ass_time(t):
    """Detik -> H:MM:SS.cc (presisi ASS sentidetik; pembulatan maks 5 ms)."""
    cs = int(round(float(t) * 100))
    h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cc = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cc:02d}"

def eval_y(y, W, H):
    """Nilai y kartu ('h-280', 'h-170', angka) -> atas teks dalam piksel. Hanya aritmetika + h/w yang diizinkan."""
    if isinstance(y, (int, float)): return float(y)
    if not isinstance(y, str): sys.exit(f"nilai y kartu tidak dikenal: {y!r}")
    expr = y.strip().replace("h", str(H)).replace("w", str(W))
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expr): sys.exit(f"ekspresi y kartu tidak dikenal: {y!r}")
    return float(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307 — ekspresi sudah divalidasi charset di atas

def font_family(font):
    """(family, bold, italic) fontfile: fc-scan bila ada, jatuh-balik heuristik nama berkas."""
    fam, bold, italic = None, False, False
    try:
        p = subprocess.run(["fc-scan", "--format", "%{family[0]}|%{style}", font], capture_output=True, text=True, timeout=10)
        if p.returncode == 0 and "|" in p.stdout:
            fam, style = p.stdout.strip().split("|", 1)
            bold = "Bold" in style; italic = ("Italic" in style or "Oblique" in style)
    except Exception:
        pass
    if not fam:
        base = os.path.splitext(os.path.basename(font))[0]
        bold = bold or "Bold" in base; italic = italic or ("Italic" in base or "Oblique" in base)
        for suf in ("Bold", "Italic", "Oblique", "Regular", "Book", "Medium", "Light"):
            base = base.replace("-" + suf, "").replace(suf, "")
        fam = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", base).strip() or base
    return fam, bold, italic

def _kw_norm(k):
    return re.sub(r"^\W+|\W+$", "", str(k).strip().lower())

def colorize_line(line, keywords, accent_ass):
    """Satu baris teks -> teks ASS dengan kata kunci berwarna aksen (cocok kata utuh, case-insensitive).
    Mengembalikan (teks_ass, ditemukan). Tanda baca tepi token tidak ikut diwarnai."""
    kwset = {_kw_norm(k) for k in keywords if _kw_norm(k)}
    if not kwset: return ass_escape(line), False
    found, out = False, []
    for tok in re.split(r"(\s+)", line):
        if not tok or tok.isspace() or not kwset:
            out.append(ass_escape(tok)); continue
        lead = re.match(r"^\W*", tok).group(0)
        trail = re.search(r"\W*$", tok).group(0)
        core = tok[len(lead):len(tok) - len(trail) if trail else len(tok)]
        if core and core.lower() in kwset:
            out.append(ass_escape(lead) + "{\\1c" + accent_ass + "}" + ass_escape(core) + "{\\r}" + ass_escape(trail)); found = True
        else:
            out.append(ass_escape(tok))
    return "".join(out), found

def cards_have_keywords(cfg):
    """True bila ADA kartu dengan `keywords` tak kosong (str dihitung satu kata kunci)."""
    for c in load_cards(cfg):
        kw = c.get("keywords")
        if isinstance(kw, str): kw = [kw]
        if isinstance(kw, list) and [k for k in kw if str(k).strip()]: return True
    return False

def build_ass_text(cfg, W, H, total_s):
    """Isi berkas .ass + daftar peringatan. Murni (tanpa tulis berkas) agar bisa diuji unit."""
    st = cfg.get("style") or {}
    cards = load_cards(cfg)
    font = st.get("font") or os.environ.get("CAPTION_FONT")
    if cards and not font: sys.exit("font kartu belum diset (style.font atau env CAPTION_FONT)")
    base = parse_color(st.get("color", "white")) or (255, 255, 255, 1.0)
    accent_raw = st.get("accent", ASS_ACCENT_DEFAULT)
    accent = parse_color(accent_raw)
    warns = []
    if accent is None:
        warns.append(f"style.accent {accent_raw!r} tidak dikenal -> default {ASS_ACCENT_DEFAULT}")
        accent = parse_color(ASS_ACCENT_DEFAULT)
    border = st.get("border", 3)
    border_c = parse_color(st.get("bordercolor", "black")) or (0, 0, 0, 1.0)
    box = st.get("box", True)
    box_c = parse_color(st.get("boxcolor", "black@0.45")) or (0, 0, 0, 0.45)
    fam, bold, italic = font_family(font) if font else ("DejaVu Sans", True, False)
    align = {"center": 2, "left": 1, "right": 3}.get(str(st.get("text_align", "center")).lower(), 2)
    size_def = st.get("size", 46); title_size = st.get("title_size", 54)
    wrap_n = st.get("wrap", 28); y_def = st.get("y", "h-280")
    styles, events = {}, []
    for c in cards:
        if c["start"] >= total_s: continue
        end = min(c["end"], total_s)
        size = c.get("size") or (title_size if c.get("kind") == "title" else size_def)
        afs = max(1, round(size * ASS_FS_FACTOR))
        sname = f"S{afs}"
        if sname not in styles:
            styles[sname] = (f"Style: {sname},{fam},{afs},{ass_color(base)},{ass_color(base)},"
                             f"{ass_color(border_c)},{ass_color(box_c)},{-1 if bold else 0},{-1 if italic else 0},0,0,"
                             f"100,100,0,0,{3 if box else 1},{border},0,{align},20,20,0,1")
        lines = c.get("lines") or wrap(c["text"], wrap_n)
        kw = c.get("keywords") or []
        if isinstance(kw, str): kw = [kw]
        kw = [k for k in kw if isinstance(k, str) and k.strip()]
        parts, found_any = [], False
        for ln in lines:
            t, f = colorize_line(ln, kw, ass_color(accent)); parts.append(t); found_any |= f
        if kw and not found_any:
            warns.append(f"kartu #{c.get('id')}: keyword {kw} tidak ditemukan di teks — dirender satu warna")
        y_top = eval_y(c.get("y") or y_def, W, H)
        mv = round(H - y_top - ASS_TOP_FACTOR * afs - (len(lines) - 1) * ASS_LINE_FACTOR * afs)
        if mv < 0:
            warns.append(f"kartu #{c.get('id')}: MarginV {mv} < 0 dijepit ke 0 (y={c.get('y') or y_def} terlalu rendah)")
            mv = 0
        events.append(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(end)},{sname},,0,0,{mv},,{'\\N'.join(parts)}")
    head = ("[Script Info]\nTitle: clipper-ultimate captions\nScriptType: v4.00+\n"
            f"PlayResX: {W}\nPlayResY: {H}\nScaledBorderAndShadow: yes\nWrapStyle: 2\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
            "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
            "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n" + "\n".join(styles.values()) +
            "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            + "\n".join(events) + "\n")
    return head, warns

def ass_filter(cfg, work, total_s, write):
    """Filter `ass=` untuk video_cmd ('' bila tanpa kartu). Menulis work/captions.ass bila write=True."""
    st = cfg.get("style") or {}
    cards = load_cards(cfg)
    if not cards: return ""
    W, H = cfg.get("size", [1080, 1920])
    text, warns = build_ass_text(cfg, W, H, total_s)
    for wmsg in warns: print("PERINGATAN ASS:", wmsg, file=sys.stderr)
    path = os.path.join(work, "captions.ass")
    if write: open(path, "w", encoding="utf-8").write(text)
    font = st.get("font") or os.environ.get("CAPTION_FONT") or ""
    fdir = os.path.dirname(font)
    f = f"ass={q(path)}"
    if fdir: f += f":fontsdir={q(fdir)}"
    return f + ":alpha=1"

def video_cmd(cfg, work, outv, write):
    W, H = cfg.get("size", [1080, 1920]); fps = cfg.get("fps", 30); segs = cfg["segments"]; tls = timeline(cfg); ins, fc = [], []
    for i, (s, tl) in enumerate(zip(segs, tls)):
        need = tl["N"] / fps + 1.0
        if s["type"] == "color": ins += ["-f", "lavfi", "-t", f3(need), "-i", f"color=c={s['color']}:s={W}x{H}:r={fps}"]
        elif s["type"] == "still": ins += ["-loop", "1", "-framerate", str(fps), "-t", f3(need), "-i", s["src"]]
        elif s["type"] == "freeze": ins += ["-ss", f3(s["src_in"]), "-t", "0.5", "-i", s["src"]]
        else: ins += ["-ss", f3(s["src_in"]), "-t", f3(need), "-i", s["src"]]
        fc.append(vchain(i, s, tl, W, H, fps))
    acc = "v0"
    for k in range(1, len(segs)):
        tl, nxt = tls[k], f"x{k}"
        if tl["trans"]:
            fc.append(f"[{acc}][v{k}]xfade=transition={tl['trans'].get('type','fade')}:duration={tl['Tf']/fps:.4f}:offset={tl['S']/fps:.4f},settb=1/{fps},fps={fps}[{nxt}]")
        else: fc.append(f"[{acc}][v{k}]concat=n=2:v=1:a=0,settb=1/{fps}[{nxt}]")
        acc = nxt
    # v4.1-fix-range: normalisasi range TV di AKHIR graf video, sesudah gabung segmen dan
    # sebelum drawtext. xfade menaikkan format ke yuv444p dan MEMPERTAHANKAN properti
    # color_range pc dari still PNG (format=yuv420p di rantai per-segmen tidak meresetnya),
    # sehingga keluarannya yuvj444p -> encode jadi yuvj420p (K2.10 FAIL format).
    # `-pix_fmt yuv420p` di akhir TIDAK menyelamatkan: libx264 menerima yuvj420p langsung
    # sehingga tidak ada konversi yang disisipkan. scale=out_range=tv (in_range auto)
    # memaksa range TV; untuk sumber TV-range (klip K1/golden) ini no-op. Satu filter ini
    # berlaku untuk semua jenis segmen (clip/still/freeze/color, xfade maupun concat).
    fc.append(f"[{acc}]scale=out_range=tv[vrng]")
    acc = "vrng"
    total_f = tls[-1]["E"]; total_s = total_f / fps
    last = acc
    if cards_have_keywords(cfg):  # v5-F6: ADA keywords -> SATU filter ASS menggantikan drawtext (sesudah scale tv)
        af = ass_filter(cfg, work, total_s, write)
        if af: fc.append(f"[{acc}]" + af + "[vout]"); last = "vout"
    else:  # tanpa keywords -> jalur drawtext LAMA, tidak berubah (perintah --print identik v4.2)
        dt = cards_filters(cfg, work, total_s, write)
        if dt: fc.append(f"[{acc}]" + ",".join(dt) + "[vout]"); last = "vout"
    e = cfg.get("encode", {})
    return (["ffmpeg", "-y", "-hide_banner"] + ins + ["-filter_complex", ";".join(fc), "-map", f"[{last}]", "-an", "-frames:v", str(total_f),
            "-c:v", "libx264", "-preset", e.get("preset", "veryfast"), "-b:v", e.get("vbitrate", "3200k"),
            "-maxrate", e.get("maxrate", "3800k"), "-bufsize", e.get("bufsize", "7600k"), "-pix_fmt", "yuv420p", "-r", str(fps), outv]), total_s

# ------------------------------------------------------------------ audio
def audio_cmd(cfg, mix, T):
    a = cfg.get("audio", {}); items = a.get("items")
    if items is None: sys.exit("audio.items wajib (skema 2): daftar {role,src,src_in,at,dur,gain_db,...}")
    ins, fc, byrole, Ts = [], [], {}, f3(T)
    for n, it in enumerate(items):
        role = it.get("role", "source"); at = float(it.get("at", 0)); sin = float(it.get("src_in", 0)); dur = it.get("dur")
        if it.get("loop"): ins += ["-stream_loop", "-1"]
        if sin: ins += ["-ss", f3(sin)]
        if dur is not None: ins += ["-t", f3(dur)]
        ins += ["-i", it["src"]]
        ch = f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo"
        if dur is not None: ch += f",atrim=duration={f3(dur)}"
        ch += ",asetpts=PTS-STARTPTS"
        if it.get("gain_db"): ch += f",volume={it['gain_db']}dB"
        if it.get("fade_in"): ch += f",afade=t=in:st=0:d={it['fade_in']}"
        if it.get("fade_out"):
            if dur is None: sys.exit(f"audio item {n}: fade_out butuh dur")
            ch += f",afade=t=out:st={f3(dur - it['fade_out'])}:d={it['fade_out']}"
        ms = int(round(at * 1000))
        if ms: ch += f",adelay={ms}|{ms}"
        ch += f",apad=whole_dur={Ts}[ai{n}]"; fc.append(ch); byrole.setdefault(role, []).append(f"[ai{n}]")
    bus = {}
    for role, labs in byrole.items():
        bus[role] = f"[b_{role}]"
        fc.append(("".join(labs) + f"amix=inputs={len(labs)}:duration=longest:normalize=0" if len(labs) > 1 else labs[0] + "anull") + f"[b_{role}]")
    final = []; d = a.get("duck")
    if d:
        keys = [r for r in d.get("key", ["vo"]) if r in bus]; tg = [r for r in d.get("target", ["music"]) if r in bus]
        if keys and tg:
            ks = [f"[k_{r}]" for r in keys]; fc.append(f"{bus[keys[0]]}asplit=2[m_{keys[0]}]{ks[0]}")
            keybus = ks[0]
            if len(keys) > 1:
                for r in keys[1:]: fc.append(f"{bus[r]}asplit=2[m_{r}]{ks[keys.index(r)]}")
                fc.append("".join(ks) + f"amix=inputs={len(ks)}:duration=longest:normalize=0[keymix]"); keybus = "[keymix]"
            fc_keys = [f"[m_{r}]" for r in keys]
            for j, r in enumerate(tg):
                kk = keybus
                if len(tg) > 1:
                    fc.append(f"{keybus}asplit={len(tg)}" + "".join(f"[kk{x}]" for x in range(len(tg)))); kk = f"[kk{j}]"
                fc.append(f"{bus[r]}{kk}sidechaincompress=threshold={d.get('threshold',0.05)}:ratio={d.get('ratio',8)}:attack={d.get('attack',20)}"
                          f":release={d.get('release',300)}:makeup={d.get('makeup',1)}[duck_{r}]"); final.append(f"[duck_{r}]")
            final += fc_keys + [bus[r] for r in bus if r not in keys and r not in tg]
        else: final = list(bus.values())
    else: final = list(bus.values())
    chain = "".join(final) + (f"amix=inputs={len(final)}:duration=longest:normalize=0" if len(final) > 1 else "anull") 
    mf = (a.get("master") or {}).get("fade_out")
    if mf: chain += f",afade=t=out:st={mf['start']}:d={mf['dur']}"
    fc.append(chain + "[mix]")
    return ["ffmpeg", "-y", "-hide_banner"] + ins + ["-filter_complex", ";".join(fc), "-map", "[mix]", "-t", Ts, "-ar", "48000", "-c:a", "pcm_s16le", mix]

def ln_args(cfg, first=False):
    L = cfg.get("loudness", {}); tp = L.get("TP_pass1", L.get("TP", -3.5)) if first else L.get("TP", -3.5)
    return f"I={L.get('I',-18)}:TP={tp}:LRA={L.get('LRA',11)}"

def sh(cmd, dry, cap=False):
    print("$", shlex.join(cmd))
    if dry: return ""
    p = subprocess.run(cmd, capture_output=cap, text=True)
    if p.returncode: sys.exit(f"gagal (kode {p.returncode}):\n{(p.stderr or '')[-1800:]}")
    return p.stderr if cap else ""

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); ap.add_argument("--print", action="store_true")
    ap.add_argument("--stage", default="all", choices=["all", "video", "audio", "mux"]); a = ap.parse_args()
    cfg = normalize(json.load(open(a.config, encoding="utf-8"))); work = cfg.get("work", "work"); dry = a.print
    miss = preflight(cfg)
    if miss:
        print("PREFLIGHT GAGAL (berkas hilang):\n  " + "\n  ".join(miss), file=sys.stderr); sys.exit(2)
    if not dry: os.makedirs(work, exist_ok=True)
    v, mix, aud = (os.path.join(work, x) for x in ("video.mp4", "mix.wav", "aud.wav")); out = cfg["out"]
    if not dry:  # v4.2-F6 (a): buat direktori output bila belum ada (sesudah preflight, sebelum semua stage;
        outdir = os.path.dirname(out)  # berlaku juga untuk --stage mux saja). dirname "" (out tanpa dir) -> lewati.
        if outdir: os.makedirs(outdir, exist_ok=True)
    cmd, total = video_cmd(cfg, work, v, not dry)
    if a.stage in ("all", "video"): sh(cmd, dry)
    if a.stage in ("all", "audio"):
        sh(audio_cmd(cfg, mix, total), dry)
        m = {"input_i": "-99", "input_lra": "0", "input_tp": "0", "input_thresh": "-70", "target_offset": "0"}
        err = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", mix, "-af", f"loudnorm={ln_args(cfg, True)}:print_format=json", "-f", "null", "-"], dry, True)
        if not dry:
            js = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
            if not js: sys.exit("loudnorm pass-1: JSON tidak ditemukan")
            m = json.loads(js[-1])
        sh(["ffmpeg", "-y", "-hide_banner", "-i", mix, "-af",
            f"loudnorm={ln_args(cfg)}:measured_I={m['input_i']}:measured_LRA={m['input_lra']}:measured_TP={m['input_tp']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000",
            "-c:a", "pcm_s16le", aud], dry)
    if a.stage in ("all", "mux"):
        ab = cfg.get("encode", {}).get("abitrate", "128k")
        sh(["ffmpeg", "-y", "-hide_banner", "-i", v, "-i", aud, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", ab,
            "-ar", "48000", "-shortest", "-movflags", "+faststart", out], dry)
        print("selesai ->", out, f"(durasi rencana {total:.3f}s = {round(total*cfg.get('fps',30))} frame)")
