#!/usr/bin/env python3
"""env_check.py — audit lingkungan untuk skill clipper-ultimate.
  A = VM tanpa GPU (jalur utama)   B = PC user dengan GPU (opsional, langkahnya dijalankan USER secara manual)
Pakai:  python3 env_check.py --env A|B [--out DIR] [--bench] [--sample audio.wav --model ggml-small.bin] [--venv PATH_VENV]
        --venv: jalankan ulang skrip ini DI DALAM venv (pip sistem ditolak PEP 668; modul seperti cv2 hanya terlihat dari venv). Env var CLIPPER_VENV setara.
Keluaran: env_report.<A|B>.json + ringkasan. Tidak menyimpan hostname/username; path rumah diganti '~'."""
import argparse, glob, importlib, importlib.util, json, os, platform, re, shutil, subprocess, sys, tempfile, time

HOME = os.path.expanduser("~")
def clean(s): return s.replace(HOME, "~") if isinstance(s, str) else s

def run(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return -1, str(e)

def ram_gb():
    try:
        for l in open("/proc/meminfo"):
            if l.startswith("MemTotal"): return round(int(l.split()[1]) / 1048576, 2)
    except Exception: pass
    try:
        import ctypes
        class M(ctypes.Structure):
            _fields_ = [("l", ctypes.c_uint32), ("p", ctypes.c_uint32)] + [(n, ctypes.c_uint64) for n in ("tp", "ap", "tf", "af", "tv", "av", "ae")]
        m = M(); m.l = ctypes.sizeof(M)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); return round(m.tp / 1073741824, 2)
    except Exception: pass
    rc, out = run(["sysctl", "-n", "hw.memsize"])
    try: return round(int(out.strip()) / 1073741824, 2)
    except Exception: return None

def gpu():
    g = {"nvidia_smi": None, "torch": None, "catatan": "nvidia-smi kosong BUKAN bukti tidak ada GPU (AMD/Intel tidak terdeteksi)."}
    if shutil.which("nvidia-smi"):
        rc, out = run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
        g["nvidia_smi"] = out.strip().splitlines() if rc == 0 else "gagal: " + out.strip()[:120]
    if importlib.util.find_spec("torch"):
        try:
            import torch
            g["torch"] = {"versi": torch.__version__, "cuda": torch.cuda.is_available(),
                          "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
        except Exception as e: g["torch"] = f"error import: {e}"
    else: g["torch"] = "tidak terpasang"
    return g

FILTERS = ["drawtext", "loudnorm", "sidechaincompress", "silencedetect", "blackdetect", "minterpolate",
           "subtitles", "ass", "zoompan", "tpad", "amix", "concat", "ebur128"]
def ffmpeg_info():
    if not shutil.which("ffmpeg"): return {"ada": False}
    r = {"ada": True, "ffprobe": bool(shutil.which("ffprobe"))}
    r["versi"] = run(["ffmpeg", "-hide_banner", "-version"])[1].splitlines()[0]
    fl = run(["ffmpeg", "-hide_banner", "-filters"])[1]
    r["filter"] = {f: bool(re.search(r"\s%s\s" % f, fl)) for f in FILTERS}
    en = run(["ffmpeg", "-hide_banner", "-encoders"])[1]
    r["encoder"] = {e: bool(re.search(r"\s%s\s" % e, en)) for e in ("libx264", "aac")}
    bc = run(["ffmpeg", "-hide_banner", "-buildconf"])[1]
    r["libass"] = "--enable-libass" in bc; r["libfreetype"] = "--enable-libfreetype" in bc
    r["drawtext_text_align"] = "text_align" in run(["ffmpeg", "-hide_banner", "-h", "filter=drawtext"])[1]  # render.py v2: kartu multi-baris (style.text_align)
    return r

def tools():
    t = {b: bool(shutil.which(b)) for b in ["whisper-cli", "yt-dlp", "demucs", "deepFilter", "deep-filter", "gdown", "node", "deno"]}
    mods = {}
    for m in ["cv2", "av", "numpy", "norfair", "supervision", "pysubs2", "torch", "stable_whisper",
              "pyannote.audio", "faster_whisper", "whisper", "demucs", "df"]:
        try: mods[m] = importlib.util.find_spec(m) is not None
        except Exception: mods[m] = False
    ver = {}
    for pkg in ["demucs", "stable-ts", "stable-ts-whisperless", "av", "opencv-python", "opencv-python-headless", "norfair", "pysubs2", "deepfilternet", "supervision"]:
        try:
            from importlib.metadata import version; ver[pkg] = version(pkg)
        except Exception: pass
    cv = {}
    if mods["cv2"]:
        try:
            import cv2
            haar_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
            cv = {"versi": cv2.__version__, "FaceDetectorYN": hasattr(cv2, "FaceDetectorYN"),
                  "FaceDetectorYN_create": hasattr(getattr(cv2, "FaceDetectorYN", None), "create"),
                  "haar_frontalface": os.path.exists(haar_path)}
            # Uji Haar SUNGGUHAN: cv2 5.x menghapus CascadeClassifier; sekadar ada file / ada modul tidak cukup.
            try:
                clf = cv2.CascadeClassifier(haar_path)
                cv["haar_tersedia"] = not clf.empty()
                if not cv["haar_tersedia"]: cv["haar_alasan"] = "CascadeClassifier kosong (file tidak termuat)"
            except AttributeError as e:
                cv["haar_tersedia"] = False
                cv["haar_alasan"] = f"cv2.CascadeClassifier tidak ada di cv2 {cv2.__version__}: {e}"
            except Exception as e:
                cv["haar_tersedia"] = False; cv["haar_alasan"] = f"gagal memuat CascadeClassifier: {str(e)[:120]}"
            ym = [f for d in [os.environ.get("YUNET_MODEL_DIR"), ".", "./models"] if d for f in glob.glob(os.path.join(os.path.expanduser(d), "face_detection_yunet*.onnx"))]
            if ym and cv["FaceDetectorYN_create"]:  # uji API nyata (cv2 5.x belum diverifikasi [T])
                try: cv2.FaceDetectorYN.create(ym[0], "", (320, 320)); cv["yunet_create_ok"] = True
                except Exception as e: cv["yunet_create_ok"] = f"gagal: {str(e)[:120]}"
        except Exception as e: cv = {"error": str(e)}
    return {"bin": t, "modul": mods, "versi_paket": ver, "opencv": cv,
            "av_butuh_python_3_12_plus": {"python": platform.python_version(), "ok": sys.version_info >= (3, 12)}}

def models():
    dirs = [os.environ.get("WHISPER_CPP_DIR"), "~/workspace/whisper.cpp", "."]
    ggml, yunet = [], []
    for d in dirs:
        if not d: continue
        d = os.path.expanduser(d)
        for f in glob.glob(os.path.join(d, "models", "ggml-*.bin")) + glob.glob(os.path.join(d, "ggml-*.bin")):
            ggml.append({"file": clean(f), "MB": round(os.path.getsize(f) / 1e6, 1)})
    for d in [os.environ.get("YUNET_MODEL_DIR"), ".", "./models"]:
        if d: yunet += [clean(f) for f in glob.glob(os.path.join(os.path.expanduser(d), "face_detection_yunet*.onnx"))]
    font = os.environ.get("CAPTION_FONT")
    return {"ggml": ggml, "yunet_onnx": yunet, "caption_font": {"env": bool(font), "ada": bool(font and os.path.exists(font))},
            "catatan": "ggml di-set via WHISPER_CPP_DIR; YuNet diunduh dari opencv_zoo (BUKAN dari repo opencv); font via CAPTION_FONT."}

def bench(sample=None, model=None):
    res = {}
    if shutil.which("ffmpeg"):
        with tempfile.TemporaryDirectory() as d:
            o = os.path.join(d, "b.mp4"); t0 = time.time()
            rc, _ = run(["ffmpeg", "-y", "-hide_banner", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30:d=10", "-f", "lavfi",
                         "-i", "sine=f=440:d=10", "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3200k", "-c:a", "aac", "-shortest", o], 900)
            el = time.time() - t0
        res["render_10s_1080x1920_detik"] = round(el, 2); res["render_x_realtime"] = round(10 / el, 2) if rc == 0 else None
    if sample and model and shutil.which("whisper-cli"):
        rc, o = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", sample])
        dur = float(o.strip()) if rc == 0 else None
        t0 = time.time(); rc, _ = run(["whisper-cli", "-m", model, "-f", sample, "-l", "id", "-nt", "-np"], 7200)
        el = time.time() - t0
        res["whisper"] = {"audio_detik": dur, "proses_detik": round(el, 1), "ok": rc == 0, "model": os.path.basename(model),
                          "x_realtime": round(dur / el, 2) if dur and rc == 0 else None}
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True, choices=["A", "B"]); ap.add_argument("--out", default=".")
    ap.add_argument("--bench", action="store_true"); ap.add_argument("--sample"); ap.add_argument("--model")
    ap.add_argument("--venv", default=os.environ.get("CLIPPER_VENV"))
    a = ap.parse_args()
    if a.venv:
        vpy = os.path.join(os.path.expanduser(a.venv), "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python")
        if not os.path.exists(vpy): sys.exit(f"python venv tidak ditemukan: {vpy}")
        if os.path.realpath(sys.prefix) != os.path.realpath(os.path.expanduser(a.venv)):
            argv = [x for x in sys.argv[1:]]
            if "--venv" in argv: i = argv.index("--venv"); del argv[i:i + 2]
            os.environ.pop("CLIPPER_VENV", None); sys.exit(subprocess.call([vpy, os.path.abspath(__file__)] + argv))
    ff, tl, md, g = ffmpeg_info(), tools(), models(), gpu()
    rep = {"env": a.env, "venv_aktif": sys.prefix != getattr(sys, "base_prefix", sys.prefix), "waktu_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "os": f"{platform.system()} {platform.release()}", "python": platform.python_version(),
           "cpu_logis": os.cpu_count(), "ram_gb": ram_gb(), "gpu": g, "ffmpeg": ff, "tools": tl, "model_file": md}
    if a.bench: rep["bench"] = bench(a.sample, a.model)
    fl = ff.get("filter", {})
    core = {"ffmpeg+libx264+aac": bool(ff.get("ada") and ff["encoder"]["libx264"] and ff["encoder"]["aac"]),
            "filter drawtext/loudnorm/sidechaincompress/silencedetect/blackdetect": all(fl.get(x) for x in ["drawtext", "loudnorm", "sidechaincompress", "silencedetect", "blackdetect"]),
            "whisper-cli": tl["bin"]["whisper-cli"], "model ggml": bool(md["ggml"]), "OpenCV (cv2)": tl["modul"]["cv2"], "font kartu": md["caption_font"]["ada"],
            "Haar (CascadeClassifier)": bool(tl["opencv"].get("haar_tersedia"))}
    rep["core_siap"] = core; rep["core_siap_semua"] = all(core.values())
    gpu_found = bool(g["nvidia_smi"] and isinstance(g["nvidia_smi"], list)) or bool(isinstance(g["torch"], dict) and g["torch"].get("cuda"))
    rep["keputusan_tool_gpu_boleh"] = bool(a.env == "B" and gpu_found)  # [T] baru valid bila user menyetujui hasil env_report.B
    path = os.path.join(a.out, f"env_report.{a.env}.json")
    json.dump(rep, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[env {a.env}] CPU={rep['cpu_logis']} RAM={rep['ram_gb']}GB GPU={g['nvidia_smi'] or 'tidak terdeteksi'} ffmpeg={'ya' if ff.get('ada') else 'TIDAK'}")
    for k, v in core.items(): print(("  OK   " if v else "  GAGAL ") + k)
    if "haar_tersedia" in tl["opencv"]:
        print("  Haar CascadeClassifier:", "tersedia" if tl["opencv"]["haar_tersedia"] else "TIDAK tersedia" + (f" ({tl['opencv']['haar_alasan']})" if tl["opencv"].get("haar_alasan") else ""))
    else:
        print("  Haar CascadeClassifier: tidak diperiksa (cv2 tidak terpasang)")
    print("  drawtext text_align:", ff.get("drawtext_text_align"), "(False -> set style.text_align:'none')")
    print("  libass di ffmpeg:", ff.get("libass"), "| Python>=3.12 (syarat PyAV):", tl["av_butuh_python_3_12_plus"]["ok"])
    print("laporan ->", path)
