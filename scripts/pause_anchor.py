#!/usr/bin/env python3
"""pause_anchor.py v4 — bangun cards.json (kartu caption) yang ditambatkan ke ucapan nyata. TEKS SELALU DARI NASKAH.

TIGA CARA TIMING per grup (kunci "timing"; default "prop"):
  prop    — NARASI VO (K2/K6): durasi kartu = bagian PROPORSIONAL JUMLAH KARAKTER di dalam span ucapan (+hold), lantai min_dur.
            Terbukti GR-1 (maks selisih 0,035). TIDAK cocok untuk dialog dengan tempo bicara bervariasi (GR-2: selisih 0,65).
  island  — DIALOG (K1/K7), tanpa ML: "pulau ucapan" = interval tidak-hening dari energi audio; kartu ditetapkan ke pulau secara berurutan
            (DP: biaya |porsi karakter - porsi waktu|); start kartu = onset pulau pertamanya; end = start kartu berikut - gap; kartu terakhir
            = akhir pulau + hold. Bila pulau < kartu, pulau dibelah proporsional karakter. [T: belum teruji pada dialog di atas musik]
  words   — DIALOG: timestamp KATA dari whisper.cpp (-ml 1 -sow) dipetakan ke kata naskah (Needleman-Wunsch fuzzy); start kartu = kata pertama
            yang cocok. Whisper salah dengar/timestamp meleset -> dipetakan fuzzy, kartu tanpa kata cocok diinterpolasi. [T]
  (mode global --mode word-pause tetap ada: kartu dari kata whisper langsung; teks = whisper, bukan naskah.)

PARAMETER PER GRUP (override global)
  noise  default -50dB (sweep VM ronde 3: -35/-40/-45 melewatkan suku kata pelan di awal VO; -55 salah di ujung; -50 <=0,02 dtk di ketiga VO GR-1)
  hold   default 0 (detik kartu terakhir grup menahan setelah akhir ucapan; GR-1: grup1 0,10, grup2-3 0,00 -> JANGAN pakai default universal)
  gap    default 0,04 (semua timing — prop dulu 0, kini 0,04, F8.2-c/an; lock #9 ditegakkan kartu_lint) — celah antar-kartu
  silence_d 0,1 (durasi hening minimum untuk silencedetect), pause 0,15 (hening min pemisah pulau), min_island 0,12

PAKAI
  python3 pause_anchor.py --script script.json --out cards.json [--compare ref_cards.json]
  python3 pause_anchor.py --list-segments transcript.json       # cetak segmen (idx, start, end, teks)
  python3 pause_anchor.py --whisper-words audio.wav --model ggml-small.bin --out-words words.json   # -l id -ml 1 -sow -nf (deterministik, tapi bisa salah dengar)
  python3 pause_anchor.py --mode word-pause --words words.json [--audio vo.wav] --out cards.json
  python3 pause_anchor.py --list-pauses trailer.mp4 [--src-in 64 --dur 8 --offset 9.74 --depth 6]   # JALUR MANUAL: cetak KANDIDAT jeda (lembah RMS)

JALUR MANUAL = DEFAULT UNTUK DIALOG (golden ronde 3: island dan words GAGAL pada dialog di atas musik). --list-pauses hanya MENCETAK
kandidat jeda (waktu timeline + kedalaman dB) untuk dipilih manusia; TIDAK PERNAH menulis kartu. `island`/`words` = eksperimental, hasil wajib dicek G-HUMAN.
`cuts` (script) / --cuts = batas BEAT, bukan tiap ganti shot (kartu boleh menjangkau potong internal dalam satu beat).
v4: akhir kartu terakhir sebuah grup DIJEPIT ke (start grup berikut - gap) (hold tidak boleh menabrak grup berikutnya).
v4.2-zona (F6-A2, Opus-8: satu kartu = satu panel): `zones` (script) / --zones-file = interval TERLARANG (xfade),
list [start,end]; kartu yang melewati zona DIBELAH di batas zona (teks dibagi di batas kata, proporsional waktu);
kartu yang berakhir/mulai di dalam zona dipotong/digeser ke batas zona; kartu yang seluruhnya di dalam zona
dipertahankan + peringatan keras. Tanpa zones -> perilaku lama, identik.

script.json:
  {"min_dur":1.0, "min_words":2, "max_words":7, "cuts":[], "zones":[[10.09,10.59]],
   "groups":[
     {"span":[0.30,6.04], "hold":0.10, "cards":["Cuan saat market merah:","Bitcoin turun dalam,"], "size":64},
     {"audio":"vo2.wav", "offset":10.0, "cards":[...]},                                   # span = ucapan pertama..terakhir (noise -50dB)
     {"timing":"island", "audio":"trailer.mp4", "src_in":64.0, "dur":8.0, "offset":9.74, "cards":[...], "hold":0.25},
     {"timing":"island", "islands":[[9.80,11.30],[12.0,13.1]], "cards":[...]},          # pulau eksplisit (mis. dari stem vokal)
     {"timing":"words", "words":"words.json", "offset":9.74, "cards":[...]}
   ]}
  - "span" ATAU "audio"(+"src_in","dur","offset": timeline = waktu_di_file - src_in + offset) ATAU "islands" ATAU "words".
  - "cards" (sudah dibelah) ATAU "text" (dibelah otomatis; HASIL harus dilihat manusia). "size"/"y"/"lines" opsional -> disalin ke kartu."""
import argparse, difflib, json, os, re, subprocess, sys, tempfile

class InputFormatError(ValueError):
    pass

END = re.compile(r"[.!?…]+[\"')\]]*$")
SOFT = re.compile(r"[,;:–—]+$")
SPECIAL = re.compile(r"\s*(\[.*\]|<\|.*\|>)\s*")

# ---------------------------------------------------------------- input word-level
def load_words(path):
    """JSON whisper.cpp (-oj, word-level) ATAU list [{"w","start","end"}]. MENOLAK segmen kalimat (bukan kata)."""
    d = json.load(open(path, encoding="utf-8"))
    out, multi, total = [], 0, 0
    if isinstance(d, dict) and "transcription" in d:
        for seg in d["transcription"]:
            t, o = seg.get("text", ""), seg.get("offsets", {})
            if "from" not in o or not t.strip() or SPECIAL.fullmatch(t):
                continue
            total += 1; multi += len(t.split()) > 1
            s, e = o["from"] / 1000.0, o["to"] / 1000.0
            if out and not t.startswith(" "):  # potongan sub-kata -> gabung ke kata sebelumnya
                out[-1]["w"] += t.strip(); out[-1]["end"] = e
            else:
                out.append({"w": t.strip(), "start": s, "end": e})
    else:
        for x in (d["words"] if isinstance(d, dict) else d):
            w = str(x.get("w", x.get("word", x.get("text", "")))).strip()
            if not w: continue
            total += 1; multi += len(w.split()) > 1
            out.append({"w": w, "start": float(x["start"]), "end": float(x["end"])})
    longw = [w for w in out if w["end"] - w["start"] > 2.5]
    if total and (multi / total > 0.3 or longw):
        raise InputFormatError(
            f"input bukan word-level: {multi}/{total} token berisi >1 kata, {len(longw)} 'kata' >2,5 dtk "
            f"(ini segmen KALIMAT). Ulangi whisper dengan -ml 1 -sow, atau pakai mode span-prop (--script) "
            f"dengan span dari `--list-segments`.")
    return out

def list_segments(path):
    d = json.load(open(path, encoding="utf-8")); rows = []
    if isinstance(d, dict) and "transcription" in d:
        for i, s in enumerate(d["transcription"]):
            o = s.get("offsets", {}); t = s.get("text", "").strip()
            if "from" in o and t and not SPECIAL.fullmatch(s.get("text", "")):
                rows.append((i, o["from"] / 1000.0, o["to"] / 1000.0, t))
    else:
        for i, s in enumerate(d["segments"] if isinstance(d, dict) and "segments" in d else d):
            rows.append((i, float(s["start"]), float(s["end"]), str(s.get("text", "")).strip()))
    return rows

# ---------------------------------------------------------------- audio
def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def detect_silences(audio, noise="-50dB", dur=0.1):
    r = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", audio, "-af", f"silencedetect=noise={noise}:d={dur}", "-f", "null", "-"])
    s, res = None, []
    for l in r.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", l)
        if m: s = max(float(m.group(1)), 0.0); continue
        m = re.search(r"silence_end: ([\d.]+)", l)
        if m and s is not None: res.append((s, float(m.group(1)))); s = None
    return res, s  # s != None => hening terbuka sampai akhir file

def file_duration(audio):
    return float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]).stdout.strip())

def speech_span(audio, noise="-50dB", sil_d=0.1):
    """(start,end) ucapan di dalam file: setelah hening awal .. sebelum hening akhir."""
    dur = file_duration(audio); sil, open_start = detect_silences(audio, noise, sil_d)
    st, en = 0.0, dur
    if sil and sil[0][0] <= 0.05: st = sil[0][1]
    if open_start is not None: en = open_start
    elif sil and sil[-1][1] >= dur - 0.05: en = sil[-1][0]
    return st, en

def prep_audio(g, tmp):
    """Siapkan audio grup -> (path_wav, geser) dengan timeline = waktu_di_file + geser. Mendukung src_in/dur (ekstrak dari MP4)."""
    sin, dur, off = float(g.get("src_in", 0)), g.get("dur"), float(g.get("offset", 0))
    if not sin and dur is None: return g["audio"], off
    out = os.path.join(tmp, f"grp_{abs(hash(json.dumps(g, sort_keys=True))) % 10**8}.wav")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + (["-ss", f"{sin:.3f}"] if sin else []) + (["-t", f"{dur:.3f}"] if dur is not None else []) + \
          ["-i", g["audio"], "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", out]
    p = _run(cmd)
    if p.returncode: raise InputFormatError(f"ekstraksi audio gagal: {p.stderr[-200:]}")
    return out, off  # file ekstrak mulai di src_in -> timeline = t + offset

def islands_from_audio(audio, noise="-50dB", pause=0.15, min_island=0.12):
    """Pulau ucapan = komplemen silencedetect (d=pause). Return [(s,e)] dalam waktu file."""
    dur = file_duration(audio); sil, open_start = detect_silences(audio, noise, pause)
    if open_start is not None: sil = sil + [(open_start, dur)]
    out, t = [], 0.0
    for s0, e0 in sil:
        if s0 - t >= min_island: out.append((t, s0))
        t = max(t, e0)
    if dur - t >= min_island: out.append((t, dur))
    return out

# ---------------------------------------------------------------- span-prop
def auto_split(text, max_words=7, min_words=2):
    """Fallback: belah di tanda baca/klausa. HASIL HARUS DILIHAT MANUSIA."""
    parts = [p.strip() for p in re.findall(r"[^,;:.!?…]+[,;:.!?…]*", text) if p.strip()]
    out = []
    for p in parts:
        ws = p.split()
        while len(ws) > max_words:  # bagi rata
            k = (len(ws) + 1) // 2; out.append(" ".join(ws[:k])); ws = ws[k:]
        if ws: out.append(" ".join(ws))
    merged = []
    for c in out:  # gabung kartu 1 kata dengan tetangga
        if merged and len(c.split()) < min_words and len(merged[-1].split()) + len(c.split()) <= max_words:
            merged[-1] += " " + c
        else: merged.append(c)
    if len(merged) > 1 and len(merged[0].split()) < min_words and len(merged[0].split()) + len(merged[1].split()) <= max_words:
        merged[1] = merged[0] + " " + merged[1]; merged.pop(0)
    return merged

def allocate(total, weights, min_dur):
    """Bagi `total` detik proporsional `weights`, dengan lantai min_dur (iteratif). Return (durasi, peringatan)."""
    n = len(weights); warn = None
    if n * min_dur > total + 1e-9:
        return [total / n] * n, f"{n} kartu x {min_dur}s > span {total:.2f}s: dibagi rata (kartu lebih sedikit atau span lebih panjang?)"
    fixed = set()
    while True:
        rem = total - min_dur * len(fixed); ws = sum(weights[i] for i in range(n) if i not in fixed) or 1.0
        d = [min_dur if i in fixed else rem * weights[i] / ws for i in range(n)]
        new = [i for i in range(n) if i not in fixed and d[i] < min_dur - 1e-9]
        if not new: return d, warn
        fixed.update(new)

# ---------------------------------------------------------------- fuzzy (dipakai mode words & sub_voice_check)
def norm(w): return re.sub(r"[^\w]", "", w.lower())

def sim(a, b):
    return 1.0 if a == b else difflib.SequenceMatcher(None, a, b).ratio()

def fuzzy_align(A, H, thr=0.7, gap=-0.5):
    """Needleman–Wunsch kata (kemiripan >= thr dianggap cocok). Return dict indeks A -> indeks H."""
    n, m = len(A), len(H); sc = [[0.0] * (m + 1) for _ in range(n + 1)]; bt = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): sc[i][0] = i * gap; bt[i][0] = 1
    for j in range(1, m + 1): sc[0][j] = j * gap; bt[0][j] = 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s_ = sim(A[i - 1], H[j - 1]); d = sc[i - 1][j - 1] + (s_ if s_ >= thr else -1.0)
            u, l = sc[i - 1][j] + gap, sc[i][j - 1] + gap; best = max(d, u, l); sc[i][j] = best
            bt[i][j] = 0 if best == d else (1 if best == u else 2)
    amap, i, j = {}, n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and bt[i][j] == 0:
            if sim(A[i - 1], H[j - 1]) >= thr: amap[i - 1] = j - 1
            i -= 1; j -= 1
        elif i > 0 and (j == 0 or bt[i][j] == 1): i -= 1
        else: j -= 1
    return amap

def run_whisper_words(audio, model, out_base, lang="id", prompt=None):
    """whisper.cpp word-level, deterministik (-nf) namun bisa salah dengar. Return path JSON."""
    wav = out_base + ".16k.wav"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav])
    cmd = ["whisper-cli", "-m", model, "-f", wav, "-l", lang, "-ml", "1", "-sow", "-nf", "-oj", "-of", out_base]
    if prompt: cmd += ["--prompt", prompt]
    p = _run(cmd)
    if p.returncode: raise InputFormatError(f"whisper-cli gagal: {p.stderr[-200:]}")
    return out_base + ".json"

# ---------------------------------------------------------------- kandidat jeda (jalur manual)
def rms_envelope(wav, hop=0.01, win=0.03):
    """Envelope RMS (dB) WAV mono/stereo 16-bit; pustaka standar saja. Return (list dB, hop_detik)."""
    import wave, array, math
    w = wave.open(wav, "rb"); n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate(); raw = array.array("h"); raw.frombytes(w.readframes(n)); w.close()
    x = raw[::ch] if ch > 1 else raw; H, Wn = max(int(sr * hop), 1), max(int(sr * win), 1); env = []
    for i in range(0, max(len(x) - Wn, 1), H):
        seg = x[i:i + Wn]; e = math.sqrt(sum(v * v for v in seg) / max(len(seg), 1)) / 32768.0
        env.append(20 * math.log10(e) if e > 1e-6 else -120.0)
    return env, H / sr

def list_pauses(wav, offset=0.0, depth=6.0, ctx=0.4, near=0.15):
    """Kandidat jeda = lembah RMS: titik minimum lokal (+-near) yang >= `depth` dB di bawah puncak terendah dari kiri/kanan dalam `ctx` detik.
    Return [(waktu_timeline, kedalaman_dB, level_dB)] terurut waktu. Hanya KANDIDAT untuk dipilih manusia (musik/noise bisa membuat lembah palsu/hilang)."""
    env, hs = rms_envelope(wav); k, c = max(int(near / hs), 1), max(int(ctx / hs), 2); out = []
    for i in range(len(env)):
        lo, hi = max(0, i - k), min(len(env), i + k + 1)
        if env[i] > min(env[lo:hi]) or (i > lo and env[i] == env[i - 1]): continue
        left, right = env[max(0, i - c):i], env[i + 1:i + 1 + c]
        if not left or not right: continue
        d = min(max(left), max(right)) - env[i]
        if d >= depth: out.append((round(i * hs + 0.015 + offset, 3), round(d, 1), round(env[i], 1)))
    return out

# ---------------------------------------------------------------- partisi pulau <-> kartu (DP)
def _partition(costf, n_items, n_groups):
    """Bagi n_items berurutan menjadi n_groups kelompok tak kosong, minimalkan jumlah costf(g, i, j) (kelompok g = item i..j-1)."""
    INF = float("inf"); dp = [[INF] * (n_items + 1) for _ in range(n_groups + 1)]; bk = [[0] * (n_items + 1) for _ in range(n_groups + 1)]
    dp[0][0] = 0.0
    for g in range(1, n_groups + 1):
        for j in range(g, n_items - (n_groups - g) + 1):
            for i in range(g - 1, j):
                c = dp[g - 1][i] + costf(g - 1, i, j)
                if c < dp[g][j]: dp[g][j] = c; bk[g][j] = i
    cuts, j = [], n_items
    for g in range(n_groups, 0, -1): i = bk[g][j]; cuts.append((i, j)); j = i
    return cuts[::-1]

def assign_cards_to_islands(texts, islands):
    """Return daftar start kartu (dtk, waktu pulau) dan list (indeks pulau awal) per kartu; pulau yang dibelah memakai proporsional karakter."""
    k, m = len(texts), len(islands); ch = [max(len(t), 1) for t in texts]; tc = float(sum(ch))
    dur = [e - s for s, e in islands]; td = float(sum(dur)) or 1.0
    starts = []
    if m >= k:  # kelompokkan pulau -> tiap kartu mendapat >=1 pulau
        parts = _partition(lambda g, i, j: abs(ch[g] / tc - sum(dur[i:j]) / td), m, k)
        starts = [islands[i][0] for i, j in parts]
    else:       # kelompokkan kartu -> tiap pulau mendapat >=1 kartu, lalu bagi proporsional karakter di dalam pulau
        parts = _partition(lambda g, i, j: abs(sum(ch[i:j]) / tc - dur[g] / td), k, m)
        for g, (i, j) in enumerate(parts):
            s0, e0 = islands[g]; cs = sum(ch[i:j]); acc = 0
            for x in range(i, j):
                starts.append(s0 + (e0 - s0) * acc / cs); acc += ch[x]
    return starts

def finish_cards(texts, starts, last_end, gap, min_dur, warn, gi):
    """starts -> (start,end) per kartu: end = start berikut - gap; kartu terakhir berakhir di last_end (diperpanjang ke min_dur)."""
    out = []
    for i, t in enumerate(texts):
        st = starts[i]
        en = starts[i + 1] - gap if i + 1 < len(texts) else last_end
        if i + 1 == len(texts) and en - st < min_dur: warn.append(f"group {gi}: kartu terakhir diperpanjang ke {min_dur}s (ucapan berakhir {last_end:.2f})"); en = st + min_dur
        out.append((st, en))
    return out

def _split_texts(g, script, hi, lo, warn, gi):
    texts = g.get("cards") or auto_split(g.get("text", ""), hi, lo)
    if not texts: raise InputFormatError(f"group {gi}: tidak ada 'cards'/'text'")
    if "cards" not in g: warn.append(f"group {gi}: teks dibelah OTOMATIS -> periksa batas frasa secara manual")
    return texts

# ---------------------------------------------------------------- zona panel/xfade (F6-A2, Opus-8: satu kartu = satu panel)
def _norm_zones(raw):
    """Validasi + urutkan zones (list [start,end] dari script["zones"] / --zones-file). Zona = interval TERLARANG (xfade)."""
    zs = []
    for z in raw or []:
        z0, z1 = float(z[0]), float(z[1])
        if not z1 > z0: raise InputFormatError(f"zona tidak valid: [{z0}, {z1}] (akhir harus > awal)")
        zs.append((z0, z1))
    return sorted(zs)

def _split_card_at_zone(c, z0, z1, min_dur, min_words, warn):
    """Belah satu kartu di zona [z0,z1]. Return list kartu (1 atau 2). Toleransi 1e-3, sama seperti hard cut di kartu_lint.
    - tidak menyentuh zona -> apa adanya.
    - menjangkau penuh (start < z0, end > z1) -> dua kartu: teks dibagi di batas kata, proporsional waktu
      (belahan sebelum zona mengambil kata-kata awal sesuai fraksi waktu); belahan <2 kata / <min_dur -> peringatan.
    - berakhir di dalam zona -> ujung dipotong ke z0, teks utuh + peringatan (kata akhir tampil lebih awal).
    - mulai di dalam zona -> awal digeser ke z1, teks utuh + peringatan (durasi pendek -> peringatan).
    - seluruhnya di dalam zona -> dipertahankan apa adanya + peringatan KERAS (tidak bisa diperbaiki otomatis)."""
    s, e = c["start"], c["end"]
    if e - 1e-3 <= z0 or s + 1e-3 >= z1: return [c]
    if s >= z0 - 1e-3 and e <= z1 + 1e-3:
        warn.append(f"kartu {c['id']}: SELURUHNYA di dalam zona panel/xfade {z0:.2f}–{z1:.2f}s — dipertahankan apa adanya (tidak bisa diperbaiki otomatis)")
        return [c]
    words = c["text"].split()
    if s < z0 and e > z1:
        k = min(max(round((z0 - s) / (e - s) * len(words)), 1), len(words) - 1)
        pre = dict(c); pre["text"] = " ".join(words[:k]); pre["end"] = round(z0, 3)
        post = dict(c); post["text"] = " ".join(words[k:]); post["start"] = round(z1, 3)
        for part, label in ((pre, "sebelum"), (post, "sesudah")):
            if len(part["text"].split()) < min_words:
                warn.append(f"kartu {c['id']}: belahan {label} zona hanya {len(part['text'].split())} kata (<{min_words})")
            if part["end"] - part["start"] < min_dur - 0.034:
                warn.append(f"kartu {c['id']}: belahan {label} zona {part['end']-part['start']:.2f}s < {min_dur}s")
        return [pre, post]
    if s < z0:  # berakhir di dalam zona
        nc = dict(c); nc["end"] = round(z0, 3)
        warn.append(f"kartu {c['id']}: dipotong di awal zona {z0:.2f}s (berakhir {e:.2f}s di dalam zona); teks utuh, kata-kata akhir tampil lebih awal")
        return [nc]
    nc = dict(c); nc["start"] = round(z1, 3)  # mulai di dalam zona
    warn.append(f"kartu {c['id']}: digeser ke akhir zona {z1:.2f}s (mulai {s:.2f}s di dalam zona)")
    if nc["end"] - nc["start"] < min_dur - 0.034:
        warn.append(f"kartu {c['id']}: {nc['end']-nc['start']:.2f}s < {min_dur}s setelah digeser keluar zona")
    return [nc]

def build_span_prop(script, noise=None):
    """Bangun kartu dari script (semua grup). Nama dipertahankan dari v2; kini mendukung timing prop|island|words, hold & noise per grup."""
    min_dur = script.get("min_dur", 1.0); lo, hi = script.get("min_words", 2), script.get("max_words", 7); cuts = sorted(script.get("cuts", []))
    zones = _norm_zones(script.get("zones", []))  # v4.2-zona: interval TERLARANG (xfade); tanpa zones -> perilaku lama
    gnoise = noise or script.get("noise") or "-50dB"
    cards, warn, gaps = [], [], {}
    tmp = tempfile.mkdtemp(prefix="pa_")
    for gi, g in enumerate(script["groups"]):
        timing = g.get("timing", "prop"); nz = g.get("noise", gnoise); hold = float(g.get("hold", script.get("hold", 0.0)))
        gap = float(g.get("gap", script.get("gap", 0.04))); sil_d = g.get("silence_d", 0.1)
        texts = _split_texts(g, script, hi, lo, warn, gi)
        if timing == "prop":
            if "span" in g: s, e = g["span"]
            elif "audio" in g:
                wav, off = prep_audio(g, tmp); a_, b_ = speech_span(wav, nz, sil_d); s, e = a_ + off, b_ + off
            else: raise InputFormatError(f"group {gi}: timing=prop butuh 'span' atau 'audio'")
            dur, w = allocate((e + hold - s) - gap * (len(texts) - 1), [len(t) for t in texts], min_dur)
            if w: warn.append(f"group {gi}: {w}")
            t = s; spans = []
            for k in range(len(texts)): spans.append((t, t + dur[k])); t += dur[k] + gap
        elif timing == "island":
            if "islands" in g: isl = [tuple(x) for x in g["islands"]]
            elif "audio" in g:
                wav, off = prep_audio(g, tmp); isl = [(a_ + off, b_ + off) for a_, b_ in islands_from_audio(wav, nz, g.get("pause", 0.15), g.get("min_island", 0.12))]
            else: raise InputFormatError(f"group {gi}: timing=island butuh 'audio' atau 'islands'")
            if "span" in g: isl = [(max(a_, g["span"][0]), min(b_, g["span"][1])) for a_, b_ in isl if b_ > g["span"][0] and a_ < g["span"][1]]
            if not isl: raise InputFormatError(f"group {gi}: tidak ada pulau ucapan (noise {nz} terlalu rendah/tinggi?)")
            if len(isl) != len(texts): warn.append(f"group {gi}: {len(isl)} pulau ucapan vs {len(texts)} kartu (pulau dibelah/digabung otomatis) -> periksa")
            spans = finish_cards(texts, assign_cards_to_islands(texts, isl), isl[-1][1] + hold, gap, min_dur, warn, gi)
        elif timing == "words":
            wp = g.get("words")
            if not wp: raise InputFormatError(f"group {gi}: timing=words butuh 'words' (JSON whisper -ml 1 -sow)")
            hyp = load_words(wp); off = float(g.get("offset", 0.0)); A, owner = [], []
            for ci, tx in enumerate(texts):
                for w_ in tx.split():
                    if norm(w_): A.append(norm(w_)); owner.append(ci)
            H = [(norm(h["w"]), h["start"] + off, h["end"] + off) for h in hyp if norm(h["w"])]
            amap = fuzzy_align(A, [h[0] for h in H]); st = [None] * len(texts); last_end = None
            for ci in range(len(texts)):
                idx = [i for i, o in enumerate(owner) if o == ci]; m_ = [amap[i] for i in idx if i in amap]
                if idx and len(m_) / len(idx) < 0.8: warn.append(f"group {gi} kartu {ci+1}: hanya {len(m_)}/{len(idx)} kata cocok dengan transkrip -> timing diperkirakan")
                if m_:
                    st[ci] = H[min(m_)][1]
                    if ci == len(texts) - 1: last_end = H[max(m_)][2]
            known = [i for i, v in enumerate(st) if v is not None]
            if not known: raise InputFormatError(f"group {gi}: tidak ada kata naskah yang cocok dengan transkrip")
            for ci in range(len(st)):  # interpolasi linear untuk kartu tanpa kata cocok
                if st[ci] is None:
                    lo_i = max([i for i in known if i < ci], default=None); hi_i = min([i for i in known if i > ci], default=None)
                    if lo_i is None: st[ci] = st[hi_i] - 0.3 * (hi_i - ci)
                    elif hi_i is None: st[ci] = st[lo_i] + 1.2 * (ci - lo_i)
                    else: st[ci] = st[lo_i] + (st[hi_i] - st[lo_i]) * (ci - lo_i) / (hi_i - lo_i)
            for ci in range(1, len(st)):
                if st[ci] <= st[ci - 1]: warn.append(f"group {gi} kartu {ci+1}: start tidak menaik (transkrip kacau) -> dipaksa +0,05"); st[ci] = st[ci - 1] + 0.05
            if last_end is None: last_end = max(h[2] for h in H)
            spans = finish_cards(texts, st, last_end + hold, gap, min_dur, warn, gi)
        else: raise InputFormatError(f"group {gi}: timing tidak dikenal: {timing} (prop|island|words)")
        for k, txt in enumerate(texts):
            c = {"id": len(cards) + 1, "kind": "caption", "text": txt, "start": round(spans[k][0], 3), "end": round(spans[k][1], 3), "group": gi, "timing": timing}
            for key in ("size", "y", "lines"):
                if key in g: c[key] = g[key]
            n = len(txt.split())
            if not lo <= n <= hi: warn.append(f"kartu {c['id']}: {n} kata (di luar {lo}-{hi})")
            if c["end"] - c["start"] < min_dur - 0.034: warn.append(f"kartu {c['id']}: {c['end']-c['start']:.2f}s < {min_dur}s")
            for x in cuts:
                if c["start"] < x < c["end"]: warn.append(f"kartu {c['id']}: melewati hard cut {x}s")
            cards.append(c); gaps[gi] = gap
    if zones:  # v4.2-zona: belah kartu yang melewati zona (ketiga mode timing); id dinomori ulang sesudahnya
        out = []
        for c in cards:
            pieces = [c]
            for z0, z1 in zones:
                nxt = []
                for p in pieces: nxt.extend(_split_card_at_zone(p, z0, z1, min_dur, lo, warn))
                pieces = nxt
            out.extend(pieces)
        cards = out
        for i, c in enumerate(cards, 1): c["id"] = i
    for i in range(1, len(cards)):  # jepit lintas-grup: end kartu sebelumnya <= start kartu ini - gap grup ini
        prv, cur = cards[i - 1], cards[i]
        if prv["group"] != cur["group"]:
            lim = round(cur["start"] - gaps[cur["group"]], 3)
            if prv["end"] > lim + 1e-6:
                warn.append(f"kartu {prv['id']}: end {prv['end']:.2f} dijepit ke {lim:.2f} (hold/span grup {prv['group']} menabrak grup {cur['group']})"); prv["end"] = lim
                if prv["end"] - prv["start"] < script.get("min_dur", 1.0) - 0.034: warn.append(f"kartu {prv['id']}: {prv['end']-prv['start']:.2f}s < {script.get('min_dur', 1.0)}s setelah dijepit")
        if cur["start"] < prv["end"] - 1e-3: warn.append(f"kartu {cur['id']}: TUMPANG-TINDIH dengan #{prv['id']} (urutan/start grup tidak menaik)")
    return cards, warn

# ---------------------------------------------------------------- word-pause
def split_by_cuts(words, cuts):
    groups, ci = [[]], 0
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        while ci < len(cuts) and mid >= cuts[ci]:
            if groups[-1]: groups.append([])
            ci += 1
        groups[-1].append(w)
    return [g for g in groups if g]

def chunk(g, a):
    cards, cur = [], []
    for i, w in enumerate(g):
        cur.append(w); n = g[i + 1] if i + 1 < len(g) else None
        if n is None: brk = True
        else:
            pause = (n["start"] - w["end"]) >= a.pause or any(s < n["start"] and e > w["end"] for s, e in a.sil)
            brk = len(cur) >= a.max_words or (len(cur) >= a.min_words and (END.search(w["w"]) or pause or (len(cur) >= 5 and SOFT.search(w["w"]))))
        if brk: cards.append(cur); cur = []
    if len(cards) > 1 and len(cards[-1]) < a.min_words:
        last, prev = cards[-1], cards[-2]
        if len(prev) + len(last) <= a.max_words: prev.extend(cards.pop())
        else:
            while len(last) < a.min_words and len(prev) > a.min_words: last.insert(0, prev.pop())
    return cards

def build_word_pause(words, a):
    cuts, warn, cards = sorted(a.cuts), [], []
    for g in split_by_cuts(words, cuts): cards += chunk(g, a)
    out = [{"id": i + 1, "kind": "caption", "text": " ".join(w["w"] for w in c), "start": c[0]["start"],
            "end": c[-1]["end"] + a.hold, "_last": c[-1]["end"], "n": len(c)} for i, c in enumerate(cards)]
    for i, c in enumerate(out):
        nxt = out[i + 1]["start"] if i + 1 < len(out) else float("inf")
        cut = min([x for x in cuts if x > c["start"] + 1e-6], default=float("inf"))
        lim = min(nxt - a.gap, cut - a.gap); c["end"] = min(c["end"], lim)
        if c["end"] - c["start"] < a.min_dur: c["end"] = min(c["start"] + a.min_dur, lim)
        if c["end"] - c["start"] < a.min_dur - 0.034: warn.append(f"kartu {c['id']}: {c['end']-c['start']:.2f}s < {a.min_dur}s (terhalang kartu berikut/hard cut)")
        if c["end"] < c["_last"] - 0.05: warn.append(f"kartu {c['id']}: kehilangan {c['_last']-c['end']:.2f}s sebelum kata terakhir selesai")
        if not a.min_words <= c["n"] <= a.max_words: warn.append(f"kartu {c['id']}: {c['n']} kata (di luar {a.min_words}-{a.max_words})")
        c["start"], c["end"] = round(c["start"], 3), round(c["end"], 3); del c["_last"], c["n"]
    return out, warn

# ---------------------------------------------------------------- bandingkan
def compare(new, ref, tol=0.05):
    ref = ref["cards"] if isinstance(ref, dict) else ref
    print(f"jumlah kartu: baru={len(new)} rujukan={len(ref)}" + ("" if len(new) == len(ref) else "  <-- BEDA"))
    ds = []
    for n, r in zip(new, ref):
        ds += [abs(n["start"] - r["start"]), abs(n["end"] - r["end"])]
        print(f"#{n['id']:>2} start {n['start']-r['start']:+.3f}  end {n['end']-r['end']:+.3f}  | {n['text'][:40]}")
    ok = len(new) == len(ref) and ds and max(ds) <= tol + 1e-9
    if ds: print(f"selisih maks = {max(ds):.3f} dtk (golden: <= {tol}) -> {'LULUS' if ok else 'GAGAL'}")
    return ok

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mode", choices=["span-prop", "word-pause"], default="span-prop")
    p.add_argument("--script"); p.add_argument("--words"); p.add_argument("--audio"); p.add_argument("--silences")
    p.add_argument("--list-segments"); p.add_argument("--list-pauses"); p.add_argument("--src-in", type=float, default=0.0); p.add_argument("--dur", type=float); p.add_argument("--offset", type=float, default=0.0); p.add_argument("--depth", type=float, default=6.0)
    p.add_argument("--out"); p.add_argument("--compare")
    p.add_argument("--whisper-words"); p.add_argument("--model"); p.add_argument("--out-words"); p.add_argument("--lang", default="id"); p.add_argument("--prompt")
    p.add_argument("--cuts", default="", help="batas BEAT (bukan tiap ganti shot), detik, dipisah koma"); p.add_argument("--cuts-file")
    p.add_argument("--zones-file", help="file JSON list [start,end] zona panel/xfade; digabung ke script['zones']")
    p.add_argument("--min-words", type=int, default=2); p.add_argument("--max-words", type=int, default=7)
    p.add_argument("--min-dur", type=float, default=1.0); p.add_argument("--gap", type=float, default=0.0)
    p.add_argument("--hold", type=float, default=0.25); p.add_argument("--pause", type=float, default=0.25)
    p.add_argument("--noise", default=None, help="default -50dB (atau kunci noise di script)")
    a = p.parse_args()
    try:
        if a.list_segments:
            for i, s, e, t in list_segments(a.list_segments): print(f"{i:>3}  {s:8.3f} {e:8.3f}  {t}")
            sys.exit(0)
        if a.list_pauses:
            import tempfile as _t
            g = {"audio": a.list_pauses, "src_in": a.src_in, "dur": a.dur, "offset": a.offset}; wav, off = prep_audio(g, _t.mkdtemp(prefix="lp_"))
            if wav == a.list_pauses:  # tanpa src_in/dur: konversi ke WAV 16k mono agar terbaca modul wave
                wav = os.path.join(_t.mkdtemp(prefix="lp_"), "x.wav"); _run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.list_pauses, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav])
            print("# KANDIDAT jeda (lembah RMS) — waktu timeline | kedalaman dB | level dB. Pilih manusia; tidak menulis kartu.")
            for t, d, lv in list_pauses(wav, off, a.depth): print(f"{t:9.3f}  {d:5.1f}  {lv:6.1f}")
            sys.exit(0)
        if a.whisper_words:
            if not (a.model and a.out_words): sys.exit("--whisper-words butuh --model dan --out-words (basis nama, tanpa .json)")
            print("->", run_whisper_words(a.whisper_words, a.model, a.out_words, a.lang, a.prompt)); sys.exit(0)
        if not a.out: sys.exit("--out wajib")
        if a.mode == "span-prop":
            if not a.script: sys.exit("mode span-prop butuh --script (lihat docstring)")
            script = json.load(open(a.script, encoding="utf-8"))
            script.setdefault("min_dur", a.min_dur); script.setdefault("min_words", a.min_words); script.setdefault("max_words", a.max_words)
            if a.gap: script["gap"] = a.gap
            if a.cuts: script["cuts"] = script.get("cuts", []) + [float(x) for x in a.cuts.split(",") if x]
            if a.zones_file: script["zones"] = script.get("zones", []) + json.load(open(a.zones_file, encoding="utf-8"))
            cards, warn = build_span_prop(script, a.noise); params = {"mode": "span-prop", "script": a.script}
        else:
            if not a.words: sys.exit("mode word-pause butuh --words")
            a.cuts = [float(x) for x in a.cuts.split(",") if x] + (json.load(open(a.cuts_file)) if a.cuts_file else [])
            a.sil = [tuple(x) for x in json.load(open(a.silences))] if a.silences else (detect_silences(a.audio, a.noise or "-35dB")[0] if a.audio else [])
            cards, warn = build_word_pause(load_words(a.words), a)
            params = {k: v for k, v in vars(a).items() if k not in ("sil",)}; params["mode"] = "word-pause"
    except InputFormatError as e:
        sys.exit(f"INPUT DITOLAK: {e}")
    json.dump({"params": params, "cards": cards, "warnings": warn}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(cards)} kartu -> {a.out}; {len(warn)} peringatan"); [print(" !", w) for w in warn]
    if a.compare: sys.exit(0 if compare(cards, json.load(open(a.compare))) else 1)
