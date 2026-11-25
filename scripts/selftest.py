#!/usr/bin/env python3
"""selftest.py v4 — suite uji skill (positif + NEGATIF) dengan data sintetis. Jalankan di VM sebelum golden reference:
    python3 selftest.py [--keep] [--render]
Kasus NEGATIF (cacat sengaja) HARUS tetap FAIL; kasus positif/pengecualian harus PASS/WARN. Exit 1 bila ada hasil tak sesuai.
Ambang tidak boleh dilonggarkan supaya final tertentu lolos: pelonggaran harus lewat alasan teknis + kasus negatif yang tetap FAIL."""
import argparse, json, os, shutil, subprocess, sys, tempfile, types
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import qc_all, pause_anchor, brief_audit, sub_voice_check

def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode: raise RuntimeError("gagal: " + " ".join(cmd)[:200] + "\n" + p.stderr[-600:])
    return p.stderr

def lufs(path):
    import re
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "loudnorm=I=-18:TP=-3.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)[-1])["input_i"])

def make_wav(path, dur, gain_db=0.0, zero=(), calib=None):
    """Sinus stereo. calib = offset dB agar ±-18 LUFS. zero = [(s,e)] diisi nol (digital silence)."""
    vol = f"{gain_db + (calib or 0):.2f}dB"
    af = f"aformat=channel_layouts=stereo,volume={vol}" + "".join(f",volume=0:enable='between(t,{s},{e})'" for s, e in zero)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=f=440:r=48000:d={dur}", "-af", af, "-c:a", "pcm_s16le", path])

def make_video(path, wav, parts, size="1080x1920"):
    """parts = [(sumber_lavfi, durasi)] -> video h264 + aac."""
    ins, pre, labs = [], "", ""
    for i, pt in enumerate(parts):
        src, d = pt[0], pt[1]; vf = pt[2] if len(pt) > 2 else None
        ins += ["-f", "lavfi", "-i", f"{src}{':' if '=' in src else '='}s={size}:r=30:d={d}"]
        if vf: pre += f"[{i}:v]{vf}[p{i}];"; labs += f"[p{i}]"
        else: labs += f"[{i}:v]"
    fc = pre + labs + f"concat=n={len(parts)}:v=1:a=0[v]"
    sh(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-i", wav, "-filter_complex", fc, "-map", "[v]", "-map", f"{len(parts)}:a", "-c:v", "libx264", "-preset", "ultrafast",
        "-b:v", "3200k", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "128k", "-shortest", path])

class A(types.SimpleNamespace): pass
ARGS = A(bitrate=3.4, tol_bitrate=0.10, tol_lufs=1.0, tp_max=-3.0)

def card(i, s, e, text="dua kata", kind="caption"): return {"id": i, "kind": kind, "text": text, "start": s, "end": e}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--keep", action="store_true"); ap.add_argument("--render", action="store_true"); a = ap.parse_args()
    w = tempfile.mkdtemp(prefix="clipper_selftest_"); res = []
    def expect(name, got, want):
        ok = got == want; res.append(ok); print(("OK    " if ok else "SALAH ") + f"{name}: hasil={got} diharapkan={want}")
    try:
        cal = -18 - lufs((lambda p: (make_wav(p, 4, 0), p)[1])(os.path.join(w, "cal.wav")))
        TS = "testsrc2"
        def vid(name, parts, zero=(), gain=0.0, dur=None, size="1080x1920"):
            d = dur or sum(p[1] for p in parts); wav = os.path.join(w, name + ".wav"); make_wav(wav, d, gain, zero, cal)
            out = os.path.join(w, name + ".mp4"); make_video(out, wav, parts, size); return out, d
        # --- video / audio
        good, d = vid("good", [(TS, 6)])
        st = lambda cid, rr: next(x["status"] for x in rr if x["id"] == cid)
        r, _ = qc_all.check_format(qc_all.probe(good), ARGS)
        expect("format final baik", st("format", r), "PASS")
        expect("loudness final baik (≈-18)", qc_all.check_loudness(good, ARGS)["status"], "PASS")
        expect("tanpa hening/hitam: hening", qc_all.check_silence(good, d, [])["status"], "PASS")
        expect("tanpa hening/hitam: hitam", qc_all.check_black(good, [])["status"], "PASS")
        bf, d = vid("blackfreeze", [(TS, 4), ("color=c=black", 2)])
        expect("NEGATIF freeze hitam 2s (tpad default)", qc_all.check_black(bf, [])["status"], "FAIL")
        dp, d = vid("darkposter", [(TS, 4), ("color=c=0x090909", 2)])
        expect("poster gelap (Y≈24) BUKAN hitam", qc_all.check_black(dp, [])["status"], "PASS")
        bf_exc = [{"check": "frame_hitam", "from": 3.9, "to": 6.0, "reason": "end card hitam disengaja"}]
        expect("NEGATIF hitam MURNI + deklarasi beralasan TETAP FAIL (v3)", qc_all.check_black(bf, bf_exc)["status"], "FAIL")
        dn, d = vid("blacknoise", [(TS, 3), ("color=c=black", 2, "noise=alls=3:allf=t")])
        expect("NEGATIF hitam + dither ±3 tetap FAIL (hitam murni)", qc_all.check_black(dn, [])["status"], "FAIL")
        PV = "drawbox=x=400:y=900:w=200:h=155:color=white:t=fill"   # ≈1,5% area terang
        pst, d = vid("poster_content", [(TS, 3), ("color=c=0x030303", 2, PV)])
        expect("poster gelap + teks (YMAX tinggi) TANPA deklarasi = FAIL", qc_all.check_black(pst, [])["status"], "FAIL")
        pst_exc = [{"check": "frame_hitam", "from": 2.9, "to": 5.1, "reason": "poster CTA gelap disengaja"}]
        expect("poster gelap + teks DENGAN deklarasi beralasan = WARN", qc_all.check_black(pst, pst_exc)["status"], "WARN")
        expect("NEGATIF poster gelap + deklarasi TANPA alasan = FAIL", qc_all.check_black(pst, [{"check": "frame_hitam", "from": 2.9, "to": 5.1}])["status"], "FAIL")
        expect("NEGATIF pengecualian TANPA alasan", qc_all.check_black(bf, [{"check": "frame_hitam", "from": 3.9, "to": 6.0}])["status"], "FAIL")
        gap, d = vid("gap", [(TS, 6)], zero=[(2.0, 3.0)])
        expect("NEGATIF hening digital 1s di tengah", qc_all.check_silence(gap, d, [])["status"], "FAIL")
        expect("NEGATIF pengecualian di tempat lain", qc_all.check_silence(gap, d, [{"check": "digital_silence", "from": 5.0, "to": 6.0, "reason": "x"}])["status"], "FAIL")
        tail, d = vid("tail", [(TS, 6)], zero=[(5.2, 6.0)])
        expect("NEGATIF ekor sunyi tanpa pengecualian", qc_all.check_silence(tail, d, [])["status"], "FAIL")
        expect("ekor sunyi dideklarasikan -> WARN", qc_all.check_silence(tail, d, [{"check": "digital_silence", "from": 5.2, "to": 6.0, "reason": "ekor sunyi disengaja"}])["status"], "WARN")
        loud, d = vid("loud", [(TS, 6)], gain=9.0)
        expect("NEGATIF terlalu keras", qc_all.check_loudness(loud, ARGS)["status"], "FAIL")
        small, d = vid("small", [(TS, 3)], size="720x1280")
        r, _ = qc_all.check_format(qc_all.probe(small), ARGS)
        expect("NEGATIF ukuran 720x1280", st("format", r), "FAIL")
        # --- bitrate tidak pernah FAIL
        low = os.path.join(w, "low.mp4"); sh(["ffmpeg", "-y", "-loglevel", "error", "-i", good, "-c:v", "libx264", "-b:v", "300k", "-c:a", "copy", low])
        r, _ = qc_all.check_format(qc_all.probe(low), ARGS)
        expect("bitrate rendah = WARN (bukan FAIL)", st("bitrate", r), "WARN")
        # --- lint kartu
        L = lambda cs, cuts=(), d=10.0, zones=None: qc_all.check_cards(cs, list(cuts), d, zones=zones)["status"]
        def crosses(cs, zones):
            return [(c["id"], z0, z1) for c in cs for z0, z1 in zones if c["start"] + 1e-3 < z1 and c["end"] - 1e-3 > z0]
        expect("NEGATIF kartu celah 0 (dulu 'Suli sah' — kini FAIL lock #9, F8.2-c)", L([card(1, 0.3, 1.69), card(2, 1.69, 2.9)]), "FAIL")
        expect("kartu celah 0,04 (PP) sah", L([card(1, 0.0, 1.6), card(2, 1.64, 2.7)]), "PASS")
        expect("kartu 0,97s lolos (toleransi 1 frame)", L([card(1, 0.0, 0.97)]), "PASS")
        expect("NEGATIF kartu 0,8s", L([card(1, 0.0, 0.8)]), "FAIL")
        expect("NEGATIF tumpang-tindih", L([card(1, 0.0, 1.5), card(2, 1.4, 2.6)]), "FAIL")
        expect("NEGATIF kartu 1 kata", L([card(1, 0.0, 1.5, "satu")]), "FAIL")
        expect("NEGATIF 8 kata", L([card(1, 0.0, 1.5, "a b c d e f g h")]), "FAIL")
        expect("NEGATIF melewati hard cut", L([card(1, 0.0, 2.0)], cuts=[1.0]), "FAIL")
        expect("NEGATIF judul 1,2s", L([card(1, 0.0, 1.2, "Judul Film", "title")]), "FAIL")
        expect("NEGATIF melewati akhir video", L([card(1, 9.0, 11.5)], d=10.0), "FAIL")
        # --- lint kartu: lebar baris (F8.2-b, F7-20) + celah min 0,04 (F8.2-c, an)
        STYLE_V1 = {"font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "size": 46, "title_size": 54, "wrap": 28, "boxborderw": 20, "y": "h-280"}
        LB = lambda cs, style=None, d=40.8: qc_all.check_cards(cs, [], d, style=style)["status"]
        LD = lambda cs, style=None, d=40.8: qc_all.check_cards(cs, [], d, style=style)["detail"]
        title_v1 = {"id": 25, "kind": "title", "text": "SUDAH TAYANG AWAL MULA HAMKA 19 November 2026 di Bioskop", "start": 39.3, "end": 40.8}
        title_v1b = dict(title_v1, lines=["SUDAH TAYANG", "AWAL MULA HAMKA", "19 November 2026 di Bioskop"])
        expect("NEGATIF F8.2-b kartu title K2 v1 TANPA lines (wrap 28, size 54) -> FAIL (baris 1095px > 1080)", LB([title_v1], STYLE_V1), "FAIL")
        expect("F8.2-b pesan FAIL menyebut lebar 1095px dan 1080px", ("1095px" in LD([title_v1], STYLE_V1) and "1080px" in LD([title_v1], STYLE_V1)), True)
        expect("F8.2-b kartu 25 v1b (lines 3 baris eksplisit, maks 909px) -> PASS", LB([title_v1b], STYLE_V1), "PASS")
        expect("F8.2-b tanpa style, cek lebar dilewati (perilaku lama): title v1 -> PASS", LB([title_v1]), "PASS")
        expect("F8.2-b baris 1011px (>1000 ambang WARN, <=1080) -> WARN", LB([dict(title_v1, text="SUDAH TAYANG AWAL MULA HAM")], STYLE_V1), "WARN")
        expect("F8.2-b lebar diukur PIL getlength (bukan estimasi)", qc_all.line_width("SUDAH TAYANG AWAL MULA HAMKA", 54, STYLE_V1["font"]), (1095.109375, "PIL"))
        expect("NEGATIF F8.2-c kartu celah 0,02 tanpa penanda -> FAIL", L([card(1, 0.0, 1.5), card(2, 1.52, 2.6)]), "FAIL")
        expect("NEGATIF F8.2-c kartu celah 0,03 (kasus GR-2) tanpa penanda -> FAIL", L([card(1, 0.0, 1.5), card(2, 1.53, 2.6)]), "FAIL")
        expect("F8.2-c celah 0,04 tepat (batas, bukan di bawah) -> PASS", L([card(1, 0.0, 1.5), card(2, 1.54, 2.6)]), "PASS")
        expect("F8.2-c celah 0,0 + legacy_gap0 beralasan -> WARN (bukan PASS diam-diam)", L([card(1, 0.0, 1.5), dict(card(2, 1.5, 2.6), legacy_gap0=True, legacy_gap0_reason="GR-1 golden pra-lock-#9")]), "WARN")
        expect("F8.2-c pesan WARN menyebut legacy_gap0", "legacy_gap0" in qc_all.check_cards([card(1, 0.0, 1.5), dict(card(2, 1.5, 2.6), legacy_gap0=True, legacy_gap0_reason="GR-1 golden pra-lock-#9")], [], 10.0)["detail"], True)
        expect("NEGATIF F8.2-c legacy_gap0 TANPA alasan -> tetap FAIL", L([card(1, 0.0, 1.5), dict(card(2, 1.5, 2.6), legacy_gap0=True)]), "FAIL")
        expect("NEGATIF kartu melewati zona panel/xfade", L([card(1, 0.0, 2.0)], zones=[[1.0, 1.5]]), "FAIL")
        expect("kartu berakhir tepat di awal zona -> PASS", L([card(1, 0.0, 1.0)], zones=[[1.0, 1.5]]), "PASS")
        expect("kartu mulai tepat di akhir zona -> PASS", L([card(1, 1.5, 2.5)], zones=[[1.0, 1.5]]), "PASS")
        expect("tanpa zones, kartu yang sama -> PASS (perilaku lama)", L([card(1, 0.0, 2.0)]), "PASS")
        expect("NEGATIF kartu melewati zona kedua dari dua zona", L([card(1, 0.0, 3.0)], zones=[[0.5, 1.0], [2.0, 2.5]]), "FAIL")
        expect("pesan FAIL menyebut zona panel/xfade", "zona panel/xfade" in qc_all.check_cards([card(1, 0.0, 2.0)], [], 10.0, zones=[[1.0, 1.5]])["detail"], True)
        # CLI qc_all --zones (end-to-end pada video `good` 6 dtk; semua cek lain PASS di sana)
        _zc = os.path.join(w, "cards_zona.json"); json.dump([card(1, 0.0, 2.0)], open(_zc, "w"))
        _zz = os.path.join(w, "zones.json"); json.dump([[1.0, 1.5]], open(_zz, "w"))
        _cli = subprocess.run([sys.executable, os.path.join(HERE, "qc_all.py"), "--video", good, "--cards", _zc, "--zones", _zz, "--out", os.path.join(w, "qc_zona.json")], capture_output=True, text=True)
        expect("CLI qc_all --zones: kartu melewati zona -> exit 1", _cli.returncode, 1)
        json.dump([card(1, 0.0, 1.0), card(2, 1.5, 2.5)], open(_zc, "w"))
        _cli = subprocess.run([sys.executable, os.path.join(HERE, "qc_all.py"), "--video", good, "--cards", _zc, "--zones", _zz, "--out", os.path.join(w, "qc_zona.json")], capture_output=True, text=True)
        expect("CLI qc_all --zones: kartu menempel batas zona -> exit 0", _cli.returncode, 0)
        # --- pause_anchor
        script = {"groups": [{"span": [0.30, 6.14], "cards": ["Cuan saat market merah:", "Bitcoin turun dalam,", "Suli malah cuan", "hampir Rp 1 miliar", "dari short Bitcoin."]}]}
        cards, warn = pause_anchor.build_span_prop(script, "-35dB")
        ref = [(0.30, 1.645), (1.685, 2.856), (2.896, 3.896), (3.936, 4.989), (5.029, 6.14)]
        expect("span-prop reproduksi 5 kartu GR-1 (±0,05) — F8.2-c: celah antar-kartu kini 0,04, bukan 0", len(cards) == 5 and max(max(abs(c["start"] - r[0]), abs(c["end"] - r[1])) for c, r in zip(cards, ref)) <= 0.05, True)
        expect("span-prop: semua kartu ≥1,0s & berurutan dengan celah 0,04 (F8.2-c)", all(c["end"] - c["start"] >= 0.999 for c in cards) and all(abs(cards[i + 1]["start"] - cards[i]["end"] - 0.04) < 1e-3 for i in range(4)), True)
        seg = os.path.join(w, "seg.json"); json.dump({"transcription": [{"text": " Kenapa pas gue senang, orang lain nggak ikut senang?", "offsets": {"from": 80, "to": 2700}}]}, open(seg, "w"))
        try: pause_anchor.load_words(seg); got = "diterima"
        except pause_anchor.InputFormatError: got = "ditolak"
        expect("NEGATIF input segmen kalimat ditolak", got, "ditolak")
        # --- pause_anchor v3: hold per grup, noise -50, island, words
        base5 = ["Cuan saat market merah:", "Bitcoin turun dalam,", "Suli malah cuan", "hampir Rp 1 miliar", "dari short Bitcoin."]
        c_h, _ = pause_anchor.build_span_prop({"groups": [{"span": [0.30, 6.04], "hold": 0.10, "cards": base5}]})
        expect("hold 0,10 per grup: 5 kartu GR-1 (±0,05) dan kartu terakhir berakhir 6,14", len(c_h) == 5 and max(max(abs(c["start"] - r[0]), abs(c["end"] - r[1])) for c, r in zip(c_h, ref)) <= 0.05 and abs(c_h[-1]["end"] - 6.14) < 0.005, True)
        c_0, _ = pause_anchor.build_span_prop({"groups": [{"span": [0.30, 6.04], "cards": base5}]})
        expect("hold default 0: kartu terakhir berakhir tepat di ujung span (6,04)", abs(c_0[-1]["end"] - 6.04) < 0.005, True)
        c_g, _ = pause_anchor.build_span_prop({"hold": 0.0, "groups": [{"span": [0.30, 6.04], "hold": 0.10, "cards": base5}, {"span": [10.0, 14.11], "cards": ["Satu dua tiga", "empat lima enam"]}]})
        expect("hold per grup: grup2 tidak ikut hold grup1 (berakhir 14,11)", abs(c_g[-1]["end"] - 14.11) < 0.005, True)
        def gated(name, dur, tones):
            """tones = [(s,e,amp)] sinus; di luar = digital silence. Gating per-SAMPEL (aevalsrc) agar tepi akurat."""
            expr = "+".join(f"{a}*between(t,{s0},{e0})" for s0, e0, a in tones)
            p = os.path.join(w, name + ".wav")
            sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"aevalsrc='({expr})*sin(2*PI*300*t)':s=16000:d={dur}", "-ac", "1", "-c:a", "pcm_s16le", p]); return p
        vo = gated("vo_soft", 5.0, [(0.0, 0.19, 0.008), (0.19, 4.1, 0.5)])   # 0-0,19 suku kata pelan (≈-42 dB), lalu ucapan keras, lalu hening
        st35, _ = pause_anchor.speech_span(vo, "-35dB"); st50, en50 = pause_anchor.speech_span(vo, "-50dB")
        expect("noise -35dB melewatkan suku kata pelan (start≈0,19) [perilaku v0.2]", abs(st35 - 0.19) < 0.03, True)
        expect("noise -50dB (default v3) menangkapnya: start≈0,00 dan end≈4,10", abs(st50) < 0.03 and abs(en50 - 4.10) < 0.03, True)
        c_a, _ = pause_anchor.build_span_prop({"groups": [{"audio": vo, "offset": 10.0, "cards": ["satu dua tiga", "empat lima enam"]}]})
        expect("audio+offset memakai default -50dB: kartu1 start=10,00", abs(c_a[0]["start"] - 10.0) < 0.03, True)
        isl = gated("islands", 7.0, [(0.0, 1.5, 0.5), (2.5, 4.0, 0.5), (4.6, 6.5, 0.5)])
        c_i, wi = pause_anchor.build_span_prop({"groups": [{"timing": "island", "audio": isl, "offset": 10.0, "cards": ["Orang orang people pleaser", "orang yang gak tau diri", "begitu saja kok"]}]})
        exp_st = [10.0, 12.5, 14.6]; exp_en = [12.46, 14.56, 16.5]
        expect("island (audio): start kartu = onset pulau (±0,03)", max(abs(c["start"] - e) for c, e in zip(c_i, exp_st)) < 0.03, True)
        expect("island (audio): end = start berikut - 0,04; terakhir = akhir pulau (±0,03)", max(abs(c["end"] - e) for c, e in zip(c_i, exp_en)) < 0.03, True)
        c_i2, _ = pause_anchor.build_span_prop({"groups": [{"timing": "island", "islands": [[0, 2], [3, 6]], "cards": ["aaa bbb", "ccc ddd", "eee fff", "ggg hhh"]}]})
        expect("island: pulau<kartu -> pulau dibelah proporsional karakter (start 0;1;3;4,5)", [round(c["start"], 2) for c in c_i2] == [0.0, 1.0, 3.0, 4.5], True)
        c_i3, _ = pause_anchor.build_span_prop({"groups": [{"timing": "island", "islands": [[0, 1], [1.5, 2.5], [4, 5], [6, 7.5]], "cards": ["aaa bbb", "ccc ddd"]}]})
        expect("island: pulau>kartu -> pulau dikelompokkan (start 0;4,0; akhir 7,5)", [round(c["start"], 2) for c in c_i3] == [0.0, 4.0] and abs(c_i3[-1]["end"] - 7.5) < 0.005, True)
        c_i4, _ = pause_anchor.build_span_prop({"groups": [{"timing": "island", "islands": [[0, 2], [3, 6]], "hold": 0.25, "cards": ["aaa bbb", "ccc ddd"]}]})
        expect("island + hold: kartu terakhir berakhir akhir pulau + hold (6,25)", abs(c_i4[-1]["end"] - 6.25) < 0.005, True)
        wj = os.path.join(w, "words_syn.json")
        json.dump([{"w": x, "start": s0, "end": s0 + 0.3} for x, s0 in [("Kenapa", 1.0), ("pas", 1.4), ("gue", 1.7), ("sulit", 2.0), ("orang", 3.6), ("lain", 3.9), ("nggak", 4.2), ("ikut", 4.5), ("senang", 4.8)]], open(wj, "w"))
        c_w, ww = pause_anchor.build_span_prop({"groups": [{"timing": "words", "words": wj, "offset": 5.0, "cards": ["Kenapa pas gue Suli", "orang lain nggak ikut senang"]}]})
        expect("words: start kartu = kata pertama + offset; 'Suli'~'sulit' dipetakan fuzzy", [round(c["start"], 2) for c in c_w] == [6.0, 8.6] and abs(c_w[0]["end"] - (8.6 - 0.04)) < 0.005, True)
        expect("words: kartu terakhir berakhir di kata terakhir (+offset)", abs(c_w[-1]["end"] - 10.1) < 0.005, True)
        try: pause_anchor.build_span_prop({"groups": [{"timing": "island", "cards": ["a b"]}]}); got = "diterima"
        except pause_anchor.InputFormatError: got = "ditolak"
        expect("NEGATIF island tanpa audio/islands ditolak", got, "ditolak")
        try: pause_anchor.build_span_prop({"groups": [{"timing": "ngawur", "span": [0, 3], "cards": ["a b"]}]}); got = "diterima"
        except pause_anchor.InputFormatError: got = "ditolak"
        expect("NEGATIF timing tak dikenal ditolak", got, "ditolak")
        # --- v4: jepit antar-grup, kandidat jeda (jalur manual), --cuts = batas beat
        c_c, w_c = pause_anchor.build_span_prop({"groups": [{"span": [0.3, 3.0], "hold": 0.5, "cards": ["aaa bbb", "ccc ddd"]}, {"timing": "island", "islands": [[3.2, 5.0]], "cards": ["eee fff"]}]})
        expect("jepit antar-grup: hold grup1 (akhir 3,50) dijepit ke start grup2 - 0,04 = 3,16; tidak tumpang-tindih", abs(c_c[1]["end"] - 3.16) < 0.005 and c_c[1]["end"] <= c_c[2]["start"], True)
        expect("jepit antar-grup: ada peringatan 'dijepit'", any("dijepit" in x for x in w_c), True)
        dip = os.path.join(w, "dip.wav")
        sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "aevalsrc='(0.5*between(t,0,2)+0.1*between(t,2,2.15)+0.5*between(t,2.15,5))*sin(2*PI*300*t)+0.04*sin(2*PI*110*t)':s=16000:d=5", "-ac", "1", "-c:a", "pcm_s16le", dip])
        lp = pause_anchor.list_pauses(dip, 10.0)
        expect("list_pauses: 1 lembah di atas bed musik, waktu timeline 12,075 (±0,06)", len(lp) == 1 and abs(lp[0][0] - 12.075) < 0.06, True)
        flat = os.path.join(w, "flat.wav")
        sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*300*t)+0.04*sin(2*PI*110*t)':s=16000:d=5", "-ac", "1", "-c:a", "pcm_s16le", flat])
        expect("NEGATIF list_pauses: audio tanpa lembah -> tidak ada kandidat", pause_anchor.list_pauses(flat, 0.0), [])
        mp4d = os.path.join(w, "dip.mp4"); sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=gray:s=320x240:r=30:d=10", "-i", dip, "-filter_complex", "[1:a]apad=whole_dur=10[a]", "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", mp4d])
        cli = subprocess.run([sys.executable, os.path.join(HERE, "pause_anchor.py"), "--list-pauses", mp4d, "--src-in", "1.0", "--dur", "4.0", "--offset", "20.0"], capture_output=True, text=True)
        tt = [float(l.split()[0]) for l in cli.stdout.splitlines() if l and not l.startswith("#")]
        expect("CLI --list-pauses dari MP4 (src_in 1, offset 20): lembah di 21,075 (±0,08) dan TIDAK menulis kartu", cli.returncode == 0 and len(tt) == 1 and abs(tt[0] - 21.075) < 0.08, True)
        beat_ok = qc_all.check_cards([card(1, 1.0, 3.5, "kartu menjangkau potong shot")], [4.0, 9.0], 12.0)["status"]
        expect("--cuts = batas BEAT: kartu menjangkau potong shot internal (2,0) tapi tidak batas beat -> PASS", beat_ok, "PASS")
        expect("NEGATIF: tiap ganti shot diberikan sebagai cuts (2,0 di dalam kartu) -> FAIL (alasan dokumen: cuts hanya batas beat)", qc_all.check_cards([card(1, 1.0, 3.5, "kartu menjangkau potong shot")], [2.0, 4.0, 9.0], 12.0)["status"], "FAIL")
        # --- v4.2-zona (F6-A2): pause_anchor mengenali zona panel/xfade
        # bobot karakter 35 vs 42 -> kartu1 [0, 2,709] menjangkau penuh zona [1,0, 1,5]; fraksi 0,369 -> 3 kata pertama
        c_z, w_z = pause_anchor.build_span_prop({"zones": [[1.0, 1.5]], "groups": [{"span": [0.0, 6.0], "cards": ["satu dua tiga empat lima enam tujuh", "delapan sembilan sepuluh sebelas dua belas"]}]})
        expect("zona: kartu menjangkau zona dibelah di batas zona (teks 3+4 kata, proporsional waktu)",
               [c["text"] for c in c_z] == ["satu dua tiga", "empat lima enam tujuh", "delapan sembilan sepuluh sebelas dua belas"]
               and [round(c["start"], 3) for c in c_z] == [0.0, 1.5, 2.749] and [round(c["end"], 3) for c in c_z] == [1.0, 2.709, 6.0], True)
        expect("zona: tidak ada kartu melewati zona sesudah dibelah", crosses(c_z, [[1.0, 1.5]]), [])
        expect("zona: belahan bersih (>=2 kata, >=1,0s) tanpa peringatan", w_z, [])
        c_e, w_e = pause_anchor.build_span_prop({"zones": [[2.0, 2.5]], "groups": [{"span": [0.0, 2.2], "cards": ["satu dua tiga"]}]})
        expect("zona: kartu berakhir di dalam zona -> ujung dipotong ke awal zona, teks utuh",
               [(c["start"], c["end"], c["text"]) for c in c_e] == [(0.0, 2.0, "satu dua tiga")] and bool(w_e), True)
        c_s, w_s = pause_anchor.build_span_prop({"zones": [[2.0, 2.5]], "groups": [{"span": [2.2, 4.0], "cards": ["satu dua tiga"]}]})
        expect("zona: kartu mulai di dalam zona -> awal digeser ke akhir zona, teks utuh",
               [(c["start"], c["end"], c["text"]) for c in c_s] == [(2.5, 4.0, "satu dua tiga")] and bool(w_s), True)
        c_i, w_i = pause_anchor.build_span_prop({"zones": [[1.0, 2.5]], "groups": [{"span": [1.1, 2.4], "cards": ["satu dua tiga"]}]})
        expect("zona: kartu seluruhnya di dalam zona -> dipertahankan + peringatan keras",
               [(c["start"], c["end"], c["text"]) for c in c_i] == [(1.1, 2.4, "satu dua tiga")] and any("SELURUHNYA" in x for x in w_i), True)
        c_n, _ = pause_anchor.build_span_prop(dict({"groups": [{"span": [0.30, 6.14], "cards": ["Cuan saat market merah:", "Bitcoin turun dalam,", "Suli malah cuan", "hampir Rp 1 miliar", "dari short Bitcoin."]}]}, zones=[[100.0, 100.5]]))
        expect("zona: kartu tak melewati zona tidak berubah (identik tanpa zones)",
               [(c["start"], c["end"], c["text"]) for c in c_n] == [(c["start"], c["end"], c["text"]) for c in cards], True)
        try: pause_anchor.build_span_prop({"zones": [[2.5, 2.0]], "groups": [{"span": [0.0, 3.0], "cards": ["a b"]}]}); got = "diterima"
        except pause_anchor.InputFormatError: got = "ditolak"
        expect("NEGATIF zona akhir <= awal ditolak", got, "ditolak")
        # CLI --zones-file (end-to-end): script + zones digabung, hasil tanpa pelintas zona
        _zs = os.path.join(w, "script_zona.json"); json.dump({"zones": [[1.0, 1.5]], "groups": [{"span": [0.0, 6.0], "cards": ["satu dua tiga empat lima enam tujuh", "delapan sembilan sepuluh sebelas dua belas"]}]}, open(_zs, "w"))
        _zo = os.path.join(w, "cards_zona_out.json")
        _cli = subprocess.run([sys.executable, os.path.join(HERE, "pause_anchor.py"), "--script", _zs, "--out", _zo], capture_output=True, text=True)
        _cz = json.load(open(_zo))["cards"] if _cli.returncode == 0 else []
        expect("CLI --script zones: 3 kartu, tidak ada yang melewati zona", _cli.returncode == 0 and len(_cz) == 3 and crosses(_cz, [[1.0, 1.5]]) == [], True)
        _zf = os.path.join(w, "zones_cli.json"); json.dump([[1.0, 1.5]], open(_zf, "w"))
        _zs2 = os.path.join(w, "script_nozona.json"); json.dump({"groups": [{"span": [0.0, 6.0], "cards": ["satu dua tiga empat lima enam tujuh", "delapan sembilan sepuluh sebelas dua belas"]}]}, open(_zs2, "w"))
        _cli = subprocess.run([sys.executable, os.path.join(HERE, "pause_anchor.py"), "--script", _zs2, "--zones-file", _zf, "--out", _zo], capture_output=True, text=True)
        _cz = json.load(open(_zo))["cards"] if _cli.returncode == 0 else []
        expect("CLI --zones-file: zones dari file digabung, hasil sama (3 kartu, tanpa pelintas)", _cli.returncode == 0 and len(_cz) == 3 and crosses(_cz, [[1.0, 1.5]]) == [], True)
        # --- F8.4: brief.schema menerima deviasi_sumber (cek struktural, tanpa dependensi jsonschema)
        _schema = json.load(open(os.path.join(HERE, "..", "templates", "brief.schema.json")))
        _dev = _schema["properties"].get("deviasi_sumber", {})
        expect("F8.4 schema: deviasi_sumber ada, array, wajib sumber_brief/sumber_dipakai/alasan",
               _dev.get("type") == "array" and _dev.get("items", {}).get("required") == ["sumber_brief", "sumber_dipakai", "alasan"], True)
        _b_ok = {"campaign": {"name": "x"}, "duration": {}, "tiktok": {}, "deviasi_sumber": [{"sumber_brief": "Trailer Utama", "sumber_dipakai": "teaser resmi 29 dtk", "alasan": "trailer utama bot-blocked (F7-1)"}]}
        _b_bad = {"campaign": {"name": "x"}, "duration": {}, "tiktok": {}, "deviasi_sumber": [{"sumber_brief": "Trailer Utama", "sumber_dipakai": "teaser"}]}
        _req = set(_dev.get("items", {}).get("required", []))
        expect("F8.4 schema: brief contoh dengan deviasi_sumber lengkap -> sah", all(_req <= set(x) for x in _b_ok["deviasi_sumber"]), True)
        expect("F8.4 schema: deviasi_sumber tanpa alasan -> TIDAK sah", all(_req <= set(x) for x in _b_bad["deviasi_sumber"]), False)
        expect("F8.4 schema: auto enum memuat sfx/vo_suara/t_dengar (F8.3-d, F8.5-b/d)",
               all(k in _schema["properties"]["manual_items"]["items"]["properties"]["auto"]["enum"] for k in ("sfx", "vo_suara", "t_dengar")), True)
        # --- F8.5-d: C21 (sfx) di brief_audit.auto_checks + F8.5-b vo_suara + F8.3-d t_dengar
        _B0 = {"manual_items": []}
        _Q0 = {"cek": [{"id": c, "status": "PASS", "detail": "ok"} for c in ("durasi", "format", "loudness", "digital_silence", "frame_hitam", "kartu_lint")], "durasi": 35.0}
        _A = lambda P, rt=None: brief_audit.auto_checks(_B0, _Q0, None, P, None, rt)
        expect("F8.5-d C21: tanpa blok sfx -> N/A", _A({})["sfx"][0], "N/A")
        expect("F8.5-d C21: sfx jumlah 0 + catatan -> N/A", _A({"sfx": {"jumlah": 0, "catatan": "TIDAK ADA SFX"}})["sfx"][0], "N/A")
        expect("F8.5-d C21: SFX lengkap (sumber+lisensi+sha256) -> PASS",
               _A({"sfx": {"items": [{"nama": "whoosh", "sumber": "Pixabay SFX", "lisensi": "Pixabay Content License", "sha256": "aa"}]}})["sfx"][0], "PASS")
        expect("F8.5-d C21: SFX tanpa lisensi/sha256 -> FAIL",
               _A({"sfx": {"items": [{"nama": "whoosh", "sumber": "Pixabay SFX"}]}})["sfx"][0], "FAIL")
        expect("F8.5-d C21: sfx jumlah>0 tanpa daftar aset -> FAIL", _A({"sfx": {"jumlah": 2}})["sfx"][0], "FAIL")
        expect("F8.5-b vo_suara: Helio eksplisit -> tidak ada baris (default benar)", "vo_suara" in _A({"vo": {"suara": "Helio (avocado_v2:MAI_03)"}}), False)
        expect("F8.5-b vo_suara: tanpa VO -> tidak ada baris", "vo_suara" in _A({}), False)
        expect("F8.5-b vo_suara: suara lain tanpa override -> FAIL",
               _A({"vo": {"suara": "Charon (Gemini)"}})["vo_suara"][0], "FAIL")
        expect("F8.5-b vo_suara: override lengkap (alasan+tanggal+pace ukur) -> PASS",
               _A({"vo": {"suara": "Charon (Gemini)", "alasan_override": "uji", "tanggal_override": "2026-11-23", "pace_terukur_kata_dtk": 2.1}})["vo_suara"][0], "PASS")
        expect("F8.5-b vo_suara: override kurang pace terukur -> FAIL",
               _A({"vo": {"suara": "Charon (Gemini)", "alasan_override": "uji", "tanggal_override": "2026-11-23"}})["vo_suara"][0], "FAIL")
        _rs_terbuka = "## Pertanyaan dengar (kata-kata [T])\n\n| # | Detik | Kartu | ASR | Pertanyaan |\n|---|---|---|---|---|\n| 1 | ~7,9 | \"puncaknya\" | small: pinjaknya | puncaknya / pinjaknya? |\n"
        _rs_tutup = "## 2a. Pertanyaan dengar [T]\n\n| # | Detik | Kata | Pertanyaan | Putusan telinga user | Status |\n|---|---|---|---|---|---|\n| 1 | 7,9 | puncaknya | puncaknya / pinjaknya? | puncaknya | TERTUTUP — puncaknya |\n| 2 | 3,8 | Track-nya | Track-nya / Traiknya? | Track-nya | DIJAWAB |\n"
        expect("F8.3-d t_dengar: format lama (tanpa kolom Status) -> PENDING", _A({}, _rs_terbuka)["t_dengar"][0], "PENDING")
        expect("F8.3-d t_dengar: semua tertutup -> PASS", _A({}, _rs_tutup)["t_dengar"][0], "PASS")
        expect("F8.3-d t_dengar: tanpa bagian [T] -> PENDING", _A({}, "# Review sheet\n\n## 5. Keputusan\n")["t_dengar"][0], "PENDING")
        expect("F8.3-d t_dengar: bagian ada, 0 pertanyaan -> PASS", _A({}, "## Pertanyaan dengar [T]\n\nTidak ada — kedua ASR sepakat.\n")["t_dengar"][0], "PASS")
        expect("F8.3-d t_dengar: tanpa --review-sheet -> tidak ada baris", "t_dengar" in _A({}), False)
        # --- CLI brief_audit end-to-end (F8.5-d + F8.3-d)
        _bf = os.path.join(w, "brief_cli.json"); json.dump({"campaign": {"name": "x"}, "duration": {}, "tiktok": {}, "manual_items": []}, open(_bf, "w"))
        _qf = os.path.join(w, "qc_cli.json"); json.dump(_Q0, open(_qf, "w"))
        _sf = os.path.join(w, "svc_cli.json"); json.dump({"A_teks_vs_naskah": {"ada_fail": False, "kartu": []}}, open(_sf, "w"))
        _pf_ok = os.path.join(w, "prod_ok.json"); json.dump({"hook_time_s": 2.0, "sfx": {"jumlah": 0, "catatan": "TIDAK ADA SFX"}, "vo": {"suara": "Helio (avocado_v2:MAI_03)"}}, open(_pf_ok, "w"))
        _pf_bad = os.path.join(w, "prod_bad.json"); json.dump({"hook_time_s": 2.0, "sfx": {"items": [{"nama": "whoosh", "sumber": "Pixabay SFX"}]}}, open(_pf_bad, "w"))
        _mf = os.path.join(w, "manual_cli.json"); json.dump({}, open(_mf, "w"))
        _rsf = os.path.join(w, "review_cli.md"); open(_rsf, "w").write(_rs_tutup)
        def _bacli(prod, extra=()):
            return subprocess.run([sys.executable, os.path.join(HERE, "brief_audit.py"), "--brief", _bf, "--qc", _qf, "--svc", _sf,
                                   "--production", prod, "--manual", _mf, "--out", os.path.join(w, "audit_cli")] + list(extra), capture_output=True, text=True)
        _c1 = _bacli(_pf_ok, ("--review-sheet", _rsf))
        _j1 = json.load(open(os.path.join(w, "audit_cli.json")))
        expect("CLI brief_audit: bersih (C21 N/A + t_dengar PASS) -> rc 0, 10 baris", _c1.returncode == 0 and len(_j1["item"]) == 10 and _j1["ringkasan"]["FAIL"] == 0 and _j1["ringkasan"]["PENDING"] == 0, True)
        expect("CLI brief_audit: baris AUTO-sfx = N/A", [r["hasil"] for r in _j1["item"] if r["id"] == "AUTO-sfx"], ["N/A"])
        _c2 = _bacli(_pf_bad)
        _j2 = json.load(open(os.path.join(w, "audit_cli.json")))
        expect("CLI brief_audit: SFX tanpa lisensi -> rc 1, AUTO-sfx FAIL", _c2.returncode == 1 and [r["hasil"] for r in _j2["item"] if r["id"] == "AUTO-sfx"] == ["FAIL"], True)
        # --- F8-1: brief_audit mencatat sha256 tiap masukan (beku manual_audit, G-FINAL harus bisa direproduksi)
        import hashlib as _hl
        _mf_sha = _hl.sha256(open(_mf, "rb").read()).hexdigest()
        expect("F8-1 brief_audit: output JSON memuat sha256 manual_audit yang dipakai", _j1.get("masukan", {}).get("manual_audit_sha256"), _mf_sha)
        expect("F8-1 brief_audit: output JSON memuat sha256 brief + production", _j1.get("masukan", {}).get("brief_sha256") == _hl.sha256(open(_bf, "rb").read()).hexdigest() and _j1.get("masukan", {}).get("production_sha256") == _hl.sha256(open(_pf_ok, "rb").read()).hexdigest(), True)
        # --- F7-12: WARN lapis B (align tiny) bukan perintah geser kartu
        expect("F7-12 svc: docstring/--help memuat peringatan WARN lapis B bukan perintah geser", "bukan perintah geser" in sub_voice_check.__doc__, True)
        _svc_cards = os.path.join(w, "svc_cards.json"); json.dump({"cards": [{"id": 1, "text": "lima belas penghargaan", "start": 0.5, "end": 2.0}]}, open(_svc_cards, "w"))
        _svc_align = os.path.join(w, "svc_align.json"); json.dump([{"w": "lima", "start": 0.5, "end": 0.8}, {"w": "belas", "start": 0.8, "end": 1.1}, {"w": "penghargaan", "start": 1.1, "end": 1.9}], open(_svc_align, "w"))
        _svc_out = os.path.join(w, "svc_out.json")
        _sc = subprocess.run([sys.executable, os.path.join(HERE, "sub_voice_check.py"), "--cards", _svc_cards, "--align", _svc_align, "--out", _svc_out], capture_output=True, text=True)
        _sj = json.load(open(_svc_out)) if os.path.exists(_svc_out) else {}
        expect("F7-12 svc: laporan lapis B memuat catatan 'WARN bukan perintah geser'", "bukan perintah geser" in str(_sj.get("B_timing_alignment", {}).get("catatan", "")), True)
        # --- F11: jalur landscape — 16 kasus dari test_qc_landscape.py (F11.2), dilipat ke selftest atas S2 Opus FINAL F11
        _wls = os.path.join(w, "f11ls"); os.makedirs(_wls, exist_ok=True)
        _FONT_LS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        _SCHEMA_LS = os.path.join(HERE, "..", "templates", "brief.schema.json")
        _F7_LS = os.path.join(HERE, "..", "..", "f2-run", "f7_k2_hamka")
        def _mkvid_ls(path, size, dur=3):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                            "-f", "lavfi", "-i", f"testsrc2=s={size}:r=30:d={dur}",
                            "-f", "lavfi", "-i", f"sine=f=440:r=48000:d={dur}",
                            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "30",
                            "-c:a", "aac", "-b:a", "128k", "-shortest", path], check=True)
        def _runqc_ls(video, extra, out):
            subprocess.run([sys.executable, os.path.join(HERE, "qc_all.py"), "--video", video, "--out", out] + extra,
                           capture_output=True, text=True)
            return {c["id"]: c for c in json.load(open(out))["cek"]}
        _v_ls = os.path.join(_wls, "ls.mp4"); _mkvid_ls(_v_ls, "1920x1080")
        _v_pt = os.path.join(_wls, "pt.mp4"); _mkvid_ls(_v_pt, "1080x1920")
        _v_720 = os.path.join(_wls, "p720.mp4"); _mkvid_ls(_v_720, "1280x720")
        _style_ls = {"font": _FONT_LS, "size": 46, "title_size": 54, "wrap": 28, "boxborderw": 20, "y": "h-280"}
        _pj_ls = os.path.join(_wls, "pj_ls.json"); json.dump({"size": [1920, 1080], "style": _style_ls}, open(_pj_ls, "w"))
        _pj_bad = os.path.join(_wls, "pj_bad.json"); json.dump({"size": [1280, 720], "style": _style_ls}, open(_pj_bad, "w"))
        _br_ls = os.path.join(_wls, "br_ls.json"); json.dump({"orientasi": "landscape", "duration": {"min_s": 1, "max_s": 120}}, open(_br_ls, "w"))
        _br_no = os.path.join(_wls, "br_no.json"); json.dump({"duration": {"min_s": 1, "max_s": 120}}, open(_br_no, "w"))
        _c = _runqc_ls(_v_ls, ["--project", _pj_ls, "--brief", _br_ls], os.path.join(_wls, "q1.json"))
        expect("F11-LS T1 format landscape benar", _c["format"]["status"], "PASS")
        expect("F11-LS T1 detail menyebut 1920x1080", "1920x1080" in _c["format"]["detail"], True)
        _c = _runqc_ls(_v_ls, [], os.path.join(_wls, "q2.json"))
        expect("F11-LS T2 format landscape tanpa project", _c["format"]["status"], "FAIL")
        _c = _runqc_ls(_v_pt, ["--project", _pj_ls, "--brief", _br_ls], os.path.join(_wls, "q3.json"))
        expect("F11-LS T3 format vertikal vs project landscape", _c["format"]["status"], "FAIL")
        _c = _runqc_ls(_v_720, ["--project", _pj_bad], os.path.join(_wls, "q4.json"))
        expect("F11-LS T4 format size luar daftar putih", _c["format"]["status"], "FAIL")
        expect("F11-LS T4 detail menyebut daftar putih", "daftar putih" in _c["format"]["detail"], True)
        _c = _runqc_ls(_v_ls, ["--project", _pj_ls, "--brief", _br_no], os.path.join(_wls, "q5.json"))
        expect("F11-LS T5 format brief tanpa orientasi vs landscape", _c["format"]["status"], "FAIL")
        expect("F11-LS T5 detail menyebut orientasi", "orientasi" in _c["format"]["detail"], True)
        _c = _runqc_ls(os.path.join(_F7_LS, "v6", "final.mp4"),
                       ["--project", os.path.join(_F7_LS, "project-v6.json"), "--brief", os.path.join(_F7_LS, "brief.json")],
                       os.path.join(_wls, "q6.json"))
        expect("F11-LS T6 regresi format v6 vertikal", _c["format"]["status"], "PASS")
        _w1095, _meth = qc_all.line_width("SUDAH TAYANG AWAL MULA HAMKA", 54, _FONT_LS)
        expect("F11-LS T7 precondition baris uji = 1095 px (PIL)", (round(_w1095), _meth), (1095, "PIL"))
        _cf = os.path.join(_wls, "cards_ok.json"); json.dump({"cards": [{"id": 19, "kind": "title", "text": "SUDAH TAYANG AWAL MULA HAMKA",
                            "start": 0.5, "end": 2.0, "lines": ["SUDAH TAYANG AWAL MULA HAMKA"]}]}, open(_cf, "w"))
        _c = _runqc_ls(_v_ls, ["--project", _pj_ls, "--cards", _cf], os.path.join(_wls, "q7a.json"))
        expect("F11-LS T7a kartu_lint baris 1095px di W=1920", _c["kartu_lint"]["status"], "PASS")
        _long_line = "X" * 60 + " kata"
        _wl_ls, _ = qc_all.line_width(_long_line, 64, _FONT_LS)
        expect("F11-LS T7 precondition baris panjang > 1920 px", _wl_ls > 1920, True)
        _cf2 = os.path.join(_wls, "cards_bad.json"); json.dump({"cards": [{"id": 1, "kind": "caption", "text": _long_line, "size": 64,
                            "start": 0.5, "end": 2.0, "lines": [_long_line]}]}, open(_cf2, "w"))
        _c = _runqc_ls(_v_ls, ["--project", _pj_ls, "--cards", _cf2], os.path.join(_wls, "q7b.json"))
        expect("F11-LS T7b kartu_lint baris >1920px", _c["kartu_lint"]["status"], "FAIL")
        import jsonschema as _js_ls
        _schema_ls = json.load(open(_SCHEMA_LS))
        _old_brief_ls = json.load(open(os.path.join(_F7_LS, "brief.json")))
        _old_brief_ls["footage"] = dict(_old_brief_ls["footage"])
        _old_brief_ls["footage"]["allowed_sources"] = [_old_brief_ls["footage"]["allowed_sources"]]  # perbaikan pra-ada tak terkait orientasi (tercatat F11)
        def _valid_ls(doc):
            try:
                _js_ls.validate(doc, _schema_ls); return True
            except Exception:
                return False
        expect("F11-LS S1 brief lama (tanpa orientasi) tetap valid", _valid_ls(_old_brief_ls), True)
        _ls_brief = dict(_old_brief_ls); _ls_brief["orientasi"] = "landscape"
        expect("F11-LS S2 brief orientasi=landscape valid", _valid_ls(_ls_brief), True)
        _bad_brief = dict(_old_brief_ls); _bad_brief["orientasi"] = "diagonal"
        expect("F11-LS S3 brief orientasi=diagonal TIDAK valid", _valid_ls(_bad_brief), False)
        # --- (opsional) render
        if a.render:
            import selftest_render; selftest_render.run(w, cal, expect); selftest_render.run_audio_regression(w, expect); selftest_render.run_color_preflight(w, expect); selftest_render.run_still_xfade_range(w, expect); selftest_render.run_still_mode_preflight(w, expect); selftest_render.run_ass_keywords(w, expect); selftest_render.run_ass_escape(w, expect)
    finally:
        if a.keep: print("berkas uji:", w)
        else: shutil.rmtree(w, ignore_errors=True)
    bad = res.count(False); print(f"\n{len(res)-bad}/{len(res)} sesuai" + ("" if not bad else f" — {bad} TIDAK SESUAI")); sys.exit(1 if bad else 0)

if __name__ == "__main__": main()
