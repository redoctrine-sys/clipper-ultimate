#!/usr/bin/env python3
"""sub_voice_check.py v2 — QC subtitle<->suara (aturan terkunci: teks kartu = yang diucapkan), TIGA LAPIS.
Ronde 1 membuktikan bahwa transkripsi bebas whisper bukan wasit yang adil (stokastik, salah dengar nama/bahasa informal,
timestamp meleset; final asli pun gagal). Karena itu hanya lapis A yang menjadi gerbang (FAIL).

  A. TEKS (deterministik, GERBANG): kata pada kartu dibanding NASKAH/transkrip yang sudah disetujui (--script). FAIL bila kartu
     memuat kata yang tidak ada di naskah (rasio < --min-ratio, default 0,9). Cakupan naskah oleh kartu = informasi (WARN bila <100%).
  B. TIMING (hanya bila ada --align): kata-kata hasil forced alignment naskah yang diketahui (stable-ts align() / whisper.cpp -dtw, F3)
     -> offset awal kartu. WARN bila |offset|>warn; FAIL hanya dengan --strict-timing. [T: jalur alignment belum teruji]
     WARN lapis B bukan perintah geser kartu (F7-12): verifikasi dengan model kedua (small word-level) bila |offset|>0,5 dtk;
     timing kata whisper tidak bisa dipercaya di tepi awal/akhir grup — cross-check dengan pita ucap (300-3000 Hz).
  C. SANITY (opsional, --video+--model atau --transcript): transkripsi bebas deterministik (-nf), pencocokan fuzzy global.
     Status paling tinggi WARN — tidak pernah FAIL.

Pakai: python3 sub_voice_check.py --cards cards.json --script naskah.txt [--align aligned_words.json]
         [--video final.mp4 --model ggml-small.bin [--lang en] [--dialog-lang en] [--prompt "Suli, People Pleaser"] | --transcript hyp.json] [--out svc_report.json]
Kartu kind='title' atau spoken=false dilewati.
Bahasa whisper: --lang diteruskan ke whisper-cli -l (default id). Bila --dialog-lang bukan id dan --lang tidak
diberikan (atau berbeda dari --dialog-lang), lapis C = PENDING beralasan — tidak menjalankan whisper dengan bahasa
yang salah dan tidak mengeluarkan WARN-derau."""
import argparse, difflib, json, os, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pause_anchor import load_words, InputFormatError, fuzzy_align, sim

def norm(w): return re.sub(r"[^\w]", "", w.lower())
def words(text): return [x for x in (norm(w) for w in text.split()) if x]

def spoken_cards(cards): return [c for c in cards if c.get("kind", "caption") == "caption" and c.get("spoken", True)]

def check_text(cards, script_text, min_ratio=0.9):
    """Lapis A. Pencocokan global kartu (berurutan) terhadap naskah."""
    A, owner = [], []
    for ci, c in enumerate(cards):
        for w in words(c["text"]): A.append(w); owner.append(ci)
    S = words(script_text)
    sm = difflib.SequenceMatcher(None, A, S, autojunk=False); amap = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): amap[blk.a + k] = blk.b + k
    rows, bad = [], False
    for ci, c in enumerate(cards):
        idx = [i for i, o in enumerate(owner) if o == ci]; m = sum(i in amap for i in idx)
        ratio = m / len(idx) if idx else 1.0; st = "PASS" if ratio >= min_ratio else "FAIL"; bad |= st == "FAIL"
        miss = [A[i] for i in idx if i not in amap]
        rows.append({"id": c["id"], "teks": c["text"], "cocok_naskah": round(ratio, 2), "kata_tak_ada_di_naskah": miss, "status": st})
    cov = len(set(amap.values())) / len(S) if S else 0.0
    return {"kartu": rows, "cakupan_naskah_oleh_kartu": round(cov, 2), "ada_fail": bad}

def compare_hyp(cards, hyp, warn_off, fail_off, strict):
    """Lapis B/C: cocokkan kata kartu ke kata hipotesis (waktu) -> offset awal kartu."""
    A, owner = [], []
    for ci, c in enumerate(cards):
        for w in words(c["text"]): A.append(w); owner.append(ci)
    H = [(norm(h["w"]), h["start"]) for h in hyp if norm(h["w"])]
    amap = fuzzy_align(A, [h[0] for h in H]); rows = []
    for ci, c in enumerate(cards):
        idx = [i for i, o in enumerate(owner) if o == ci]; m = [amap[i] for i in idx if i in amap]
        ratio = len(m) / len(idx) if idx else 1.0; off = (H[min(m)][1] - c["start"]) if m else None
        st = "PASS"
        if off is None or ratio < 0.8: st = "FAIL"
        elif abs(off) > fail_off: st = "FAIL"
        elif abs(off) > warn_off: st = "WARN"
        if st == "FAIL" and not strict: st = "WARN"
        rows.append({"id": c["id"], "teks": c["text"], "cocok": round(ratio, 2), "offset_dtk": None if off is None else round(off, 3), "status": st})
    return {"kartu": rows, "cakupan_ucapan_oleh_kartu": round(len(amap) / len(H), 2) if H else 0.0}

def transcribe(video, model, tmp, prompt=None, lang="id"):
    if shutil.which("whisper-cli") is None:
        sys.exit("whisper-cli tidak ditemukan di PATH; pasang whisper.cpp (biner build/bin/whisper-cli) "
                 "atau tambah direktorinya ke PATH, lalu ulangi. Lapis C tidak dapat dijalankan.")
    wav, base = os.path.join(tmp, "svc.wav"), os.path.join(tmp, "svc")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav], check=True)
    cmd = ["whisper-cli", "-m", model, "-f", wav, "-l", lang, "-ml", "1", "-sow", "-nf", "-oj", "-of", base]
    if prompt: cmd += ["--prompt", prompt]  # glosarium nama [T: opsi --prompt]
    subprocess.run(cmd, check=True, capture_output=True)
    return base + ".json"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cards", required=True); ap.add_argument("--script"); ap.add_argument("--align"); ap.add_argument("--video"); ap.add_argument("--model")
    ap.add_argument("--prompt"); ap.add_argument("--transcript"); ap.add_argument("--out", default="svc_report.json")
    ap.add_argument("--lang", default=None, help="bahasa untuk whisper-cli -l (default: id, atau --dialog-lang bila diberikan)")
    ap.add_argument("--dialog-lang", default=None, help="bahasa dialog yang sebenarnya (mis. en); bila bukan id dan --lang tidak diberikan/dicocokkan, lapis C = PENDING")
    ap.add_argument("--min-ratio", type=float, default=0.9); ap.add_argument("--warn-offset", type=float, default=0.35)
    ap.add_argument("--fail-offset", type=float, default=0.6); ap.add_argument("--strict-timing", action="store_true")
    a = ap.parse_args(); cj = json.load(open(a.cards, encoding="utf-8")); cards = spoken_cards(cj["cards"] if isinstance(cj, dict) else cj)
    rep, fail = {}, False
    if a.script:
        rep["A_teks_vs_naskah"] = A = check_text(cards, open(a.script, encoding="utf-8").read(), a.min_ratio); fail |= A["ada_fail"]
        for k in A["kartu"]: print(f"A {k['status']:<5} #{k['id']:<3} cocok_naskah={k['cocok_naskah']:.2f}  {k['teks'][:45]}" + (f"   tak ada di naskah: {k['kata_tak_ada_di_naskah']}" if k['kata_tak_ada_di_naskah'] else ""))
        print(f"A cakupan naskah oleh kartu: {A['cakupan_naskah_oleh_kartu']:.0%}" + ("" if A["cakupan_naskah_oleh_kartu"] >= 0.99 else "  (WARN: ada ucapan yang tidak punya kartu)"))
    else:
        print("A PENDING: --script (naskah/transkrip yang disetujui) tidak diberikan -> lapis A tidak dinilai"); rep["A_teks_vs_naskah"] = {"status": "PENDING"}
    if a.align:
        try: aw = load_words(a.align)
        except InputFormatError as e: sys.exit(f"INPUT --align DITOLAK: {e}")
        rep["B_timing_alignment"] = B = compare_hyp(cards, aw, a.warn_offset, a.fail_offset, a.strict_timing); fail |= any(k["status"] == "FAIL" for k in B["kartu"])
        B["catatan"] = ("WARN lapis B bukan perintah geser kartu (F7-12): verifikasi dengan model kedua (small word-level) "
                        "bila |offset|>0,5 dtk; timing kata whisper tidak bisa dipercaya di tepi awal/akhir grup — cross-check dengan pita ucap.")
        for k in B["kartu"]: print(f"B {k['status']:<5} #{k['id']:<3} offset={k['offset_dtk']}")
        print("B CATATAN: WARN lapis B bukan perintah geser kartu — verifikasi dengan model kedua bila |offset|>0,5 dtk (F7-12)")
    if a.transcript or (a.video and a.model):
        # Bahasa whisper vs bahasa dialog: jangan pernah menjalankan whisper dengan bahasa yang salah
        # (dulu -l selalu id -> dialog Inggris menghasilkan WARN-derau). Ketidakcocokan = PENDING.
        pending_alasan = None
        if a.lang is not None and a.dialog_lang is not None and a.lang != a.dialog_lang:
            pending_alasan = f"--lang {a.lang} != --dialog-lang {a.dialog_lang}; samakan keduanya lalu ulangi"
        elif a.lang is None and a.dialog_lang is not None and a.dialog_lang != "id":
            pending_alasan = f"bahasa dialog {a.dialog_lang}, jalankan dengan --lang {a.dialog_lang}"
        if pending_alasan and not a.transcript:
            print(f"C PENDING: {pending_alasan} (whisper tidak dijalankan; lapis C tidak dinilai)")
            rep["C_sanity_whisper"] = {"status": "PENDING", "alasan": pending_alasan}
        else:
            try:
                if a.transcript: hyp = load_words(a.transcript)
                else:
                    lang = a.lang or a.dialog_lang or "id"
                    with tempfile.TemporaryDirectory() as t: hyp = load_words(transcribe(a.video, a.model, t, a.prompt, lang))
            except InputFormatError as e: sys.exit(f"INPUT TRANSKRIP DITOLAK: {e}")
            rep["C_sanity_whisper"] = C = compare_hyp(cards, hyp, a.warn_offset, a.fail_offset, False)
            for k in C["kartu"]: print(f"C {k['status']:<5} #{k['id']:<3} cocok={k['cocok']:.2f} offset={k['offset_dtk']}  (sanity: maks WARN)")
    rep["ada_fail"] = fail; json.dump(rep, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(1 if fail else 0)
