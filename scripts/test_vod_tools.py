#!/usr/bin/env python3
"""test_vod_tools.py — Tes fail-first untuk vod_signals.py + vod_chunks.py (F9.3).

Cara pakai: python3 test_vod_tools.py [--keep]
- Dijalankan dulu saat skrip BELUM ada -> FAIL (ImportError) = bukti tes tidak vakum.
- Dijalankan sesudah implementasi -> semua PASS, exit 0.
Fixture sintetis: chat dengan lonjakan di waktu yang diketahui, komentar bertimestamp,
info.json minimal. Tanpa jaringan, tanpa media nyata.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def expect(nama, got, want):
    ok = got == want
    print(("PASS " if ok else "FAIL ") + nama + ("" if ok else f" (dapat {got!r}, mau {want!r})"))
    if not ok:
        FAILS.append(nama)


def run_cli(mod, args, cwd):
    return subprocess.run([sys.executable, os.path.join(HERE, mod)] + args,
                          capture_output=True, text=True, cwd=cwd)


def main():
    import vod_signals as vs
    import vod_chunks as vc

    # --- vod_signals: parsing ---
    chat = []
    for i in range(600):  # 10 menit, 1 pesan/10 dtk latar
        chat.append({"replayChatItemAction": {"videoOffsetTimeMsec": i * 10000,
                     "actions": [{"addChatItemAction": {"item": {"liveChatTextMessageRenderer": {
                         "timestampUsec": i * 10000000,
                         "message": {"runs": [{"text": "seru banget"}]}}}}}]}})
    for i in range(40):  # lonjakan di 300-320 dtk: 40 pesan + token tawa
        chat.append({"replayChatItemAction": {"videoOffsetTimeMsec": 300000 + i * 500,
                     "actions": [{"addChatItemAction": {"item": {"liveChatTextMessageRenderer": {
                         "timestampUsec": (300 + i * 0.5) * 1000000,
                         "message": {"runs": [{"text": "wkwkwk ngakak"}]}}}}}]}})
    with tempfile.TemporaryDirectory() as d:
        cp = os.path.join(d, "chat.json")
        json.dump(chat, open(cp, "w"))
        # regresi F9: iter_json_array streaming (chunk kecil = elemen terpotong)
        # harus menghasilkan jumlah elemen yang sama dengan json.load
        n_stream = len(list(vs.iter_json_array(cp, chunk_size=64)))
        n_load = len(json.load(open(cp)))
        expect("signals: iter_json_array streaming == json.load", n_stream, n_load)
        expect("signals: parse_chat streaming membaca lonjakan", len(vs.parse_chat(cp)), len(chat))
        # regresi F9: videoOffsetTimeMsec + timestampUsec berupa STRING (berkas nyata);
        # t harus dari offset video, BUKAN epoch timestampUsec
        chat_str = [{"replayChatItemAction": {"videoOffsetTimeMsec": "300500",
                    "actions": [{"addChatItemAction": {"item": {"liveChatTextMessageRenderer": {
                        "timestampUsec": "1795419210644474",
                        "message": {"runs": [{"text": "wkwk"}]}}}}}]}}]
        cps = os.path.join(d, "chat_str.json")
        json.dump(chat_str, open(cps, "w"))
        got_str = vs.parse_chat(cps)
        expect("signals: offset string -> 300.5 dtk (bukan epoch)", got_str, [(300.5, "wkwk")])
        info = {"id": "TEST", "duration": 600, "chapters": [],
                "description": "buka 05:00 momennya"}
        ip = os.path.join(d, "info.json")
        json.dump(info, open(ip, "w"))
        out = os.path.join(d, "kandidat.json")
        r = run_cli("vod_signals.py", ["--info", ip, "--chat", cp, "--out", out, "--min", "1"], d)
        expect("signals: lonjakan diketahui -> rc 0", r.returncode, 0)
        if r.returncode == 0:
            k = json.load(open(out))
            w = k["kandidat"][0]
            expect("signals: jendela memuat lonjakan 300 dtk (digeser mundur)",
                   w["abs_start"] <= 300 <= w["abs_end"], True)
            expect("signals: token tawa tercatat", w["token"] > 0, True)
            expect("signals: skor > 0", w["skor"] > 0, True)
            expect("signals: timestamp deskripsi terhitung",
                   k["sinyal_tersedia"]["timestamp_deskripsi"], 1)
        # tanpa sinyal apa pun -> rc != 0
        info2 = {"id": "TEST2", "duration": 600, "chapters": [], "description": ""}
        ip2 = os.path.join(d, "info2.json")
        json.dump(info2, open(ip2, "w"))
        r2 = run_cli("vod_signals.py", ["--info", ip2, "--out", os.path.join(d, "k2.json"), "--min", "1"], d)
        expect("signals: tanpa sinyal -> rc != 0", r2.returncode != 0, True)
        # komentar bertimestamp
        com = {"comments": [{"text": "12:34 wkwk parah"}, {"text": "keren"}]}
        comp = os.path.join(d, "com.json")
        json.dump(com, open(comp, "w"))
        got = vs.parse_comments(comp)
        expect("signals: komentar '12:34' -> 754 dtk", [t for t, _ in got], [754.0])
        expect("signals: _hms_to_s 1:02:03", vs._hms_to_s("1:02:03"), 3723)
        # regresi F9: jangkar di luar durasi tidak boleh crash (komentar > durasi ada)
        cnt, tok = vs.bin_chat([], 600)
        sc_out, _, _ = vs.score_window(20000, 20090, cnt, tok, [(20000.0, "komentar")], [])
        expect("signals: skor jendela di luar durasi tidak crash", isinstance(sc_out, float), True)
        # regresi F9: lonjakan tanpa token + baseline tinggi -> catatan_k5, dan
        # jangkar komentar tetap mengisi k3 (fallback lama hanya jalan bila 0 lonjakan)
        chat2 = []
        for i in range(600):
            txt = "wkwk seru" if i % 10 == 0 else "seru banget"
            chat2.append({"replayChatItemAction": {"videoOffsetTimeMsec": i * 10000,
                         "actions": [{"addChatItemAction": {"item": {"liveChatTextMessageRenderer": {
                             "timestampUsec": i * 10000000,
                             "message": {"runs": [{"text": txt}]}}}}}]}})
        for i in range(40):  # lonjakan 300-320 dtk TANPA token tawa/kaget
            chat2.append({"replayChatItemAction": {"videoOffsetTimeMsec": 300000 + i * 500,
                         "actions": [{"addChatItemAction": {"item": {"liveChatTextMessageRenderer": {
                             "timestampUsec": (300 + i * 0.5) * 1000000,
                             "message": {"runs": [{"text": "seru banget"}]}}}}}]}})
        cp2 = os.path.join(d, "chat2.json")
        json.dump(chat2, open(cp2, "w"))
        com3 = {"comments": [{"text": "05:00 gokil"}]}
        comp3 = os.path.join(d, "com3.json")
        json.dump(com3, open(comp3, "w"))
        out3 = os.path.join(d, "kandidat3.json")
        r4 = run_cli("vod_signals.py", ["--info", ip, "--chat", cp2, "--comments", comp3,
                                        "--out", out3, "--min", "1", "--max", "9"], d)
        expect("signals: lonjakan tanpa token + jangkar -> rc 0", r4.returncode, 0)
        if r4.returncode == 0:
            k3 = json.load(open(out3))
            expect("signals: lonjakan tanpa token -> catatan_k5", len(k3["catatan_k5"]) >= 1, True)
            expect("signals: jangkar komentar mengisi k3", len(k3["kandidat"]) >= 1, True)
        # regresi F9: dua klaster jangkar bersebelahan (satu lonjakan) -> satu jendela
        com2 = {"comments": [{"text": "05:50 gokil"}, {"text": "06:10 wkwk"}, {"text": "01:40 seru"}]}
        comp2 = os.path.join(d, "com2.json")
        json.dump(com2, open(comp2, "w"))
        info3 = {"id": "TEST3", "duration": 600, "chapters": [], "description": ""}
        ip3 = os.path.join(d, "info3.json")
        json.dump(info3, open(ip3, "w"))
        out2 = os.path.join(d, "kandidat2.json")
        r3 = run_cli("vod_signals.py", ["--info", ip3, "--comments", comp2, "--out", out2,
                                        "--min", "1", "--max", "9"], d)
        expect("signals: jangkar bersebelahan -> rc 0", r3.returncode, 0)
        if r3.returncode == 0:
            k2 = json.load(open(out2))
            expect("signals: klaster tumpang tindih digabung (2 jendela, bukan 3)",
                   len(k2["kandidat"]), 2)

    # --- vod_chunks: pemetaan + penolakan + resume ---
    man = {"video_id": "TEST", "durasi_dtk": 14631, "format": "bv*[height<=480]+ba/b[height<=480]",
           "potongan": [{"id": "k1", "abs_start": 300, "abs_end": 360, "pad_dtk": 15}]}
    cmds, table, errs, _ = vc.plan(man)
    expect("chunks: tanpa error", errs, [])
    row = table[0]
    expect("chunks: chunk_start_abs = 285", row["chunk_start_abs"], 285.0)
    expect("chunks: abs->chunk 300 -> 15", vc.abs_to_chunk(300, row), 15.0)
    expect("chunks: chunk->abs 15 -> 300", vc.chunk_to_abs(15, row), 300.0)
    expect("chunks: perintah berisi --download-sections",
           any("--download-sections" in c for c in cmds), True)
    expect("chunks: rentang pada perintah", any("00:04:45-00:06:15" in c for c in cmds), True)
    man_bad = {"video_id": "TEST", "durasi_dtk": 14631,
               "potongan": [{"id": "kX", "abs_start": 0, "abs_end": 590, "pad_dtk": 15}]}
    _, _, errs2, _ = vc.plan(man_bad)
    expect("chunks: potongan 620 dtk DITOLAK (P3)", len(errs2) == 1 and "620" in errs2[0], True)
    man_neg = {"video_id": "TEST", "durasi_dtk": 14631,
               "potongan": [{"id": "kY", "abs_start": 5, "abs_end": 60, "pad_dtk": 15}]}
    _, _, errs3, _ = vc.plan(man_neg)
    expect("chunks: abs_start-pad < 0 DITOLAK", len(errs3) == 1, True)
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, "k1.mp4")
        open(fp, "wb").write(b"palsu")
        sha = hashlib.sha256(b"palsu").hexdigest()
        old = {"k1": {"sha256": sha}}
        cmds2, table2, errs4, _ = vc.plan(man, outdir=d, old_map=old)
        expect("chunks: resume P5 -> SKIP, bukan unduh", cmds2[0].startswith("# SKIP"), True)
        expect("chunks: resume P5 -> status sudah_ada", table2[0]["status"], "sudah_ada")
        old_bad = {"k1": {"sha256": "0" * 64}}
        cmds3, _, _, _ = vc.plan(man, outdir=d, old_map=old_bad)
        expect("chunks: sha beda -> unduh ulang", cmds3[0].startswith("yt-dlp"), True)

    print(f"\n{len(FAILS)} FAIL" if FAILS else "\nSEMUA PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
