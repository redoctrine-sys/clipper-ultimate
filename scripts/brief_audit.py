#!/usr/bin/env python3
"""brief_audit.py v2 — audit file FINAL terhadap brief.json, item per item, dengan bukti. Menulis <out>.md/.json.
Exit 0 = semua PASS/N-A-sah; 1 = ada FAIL (termasuk KONFLIK otomatis↔manual); 2 = ada item PENDING.

Pemetaan 1:1: tiap butir brief.manual_items {id, requirement, auto?} punya SATU baris. `auto` = id cek otomatis yang setara:
  durasi · format · loudness · digital_silence · frame_hitam · kartu_lint · teks_kartu (svc lapis A) · hashtag · tag · cta · larangan_ai · hook
Hasil efektif: manual (bila ada bukti) selaras dengan otomatis; bila BEDA -> KONFLIK (FAIL) kecuali manual memuat `overrides_auto` (alasan).
Butir tanpa `auto` hanya dinilai manual (PENDING bila belum). Cek otomatis yang tak dipetakan ke butir tampil sebagai baris tambahan.

Pakai: python3 brief_audit.py --brief brief.json --qc qc_report.json [--svc svc_report.json] [--caption caption_tiktok.txt]
                              [--production production.json] [--manual manual_audit.json] --out brief_audit
production.json: {"tools":[{"name":"whisper.cpp","category":"analytic-ml"},{"name":"ffmpeg","category":"none"},{"name":"<tts>","category":"generative"}],
                  "ai_waiver":{"granted":true,"by":"user","date":"2026-11-21T20:40","scope":"tools AI","note":"..."}, "hook_time_s":2.7}
   category: generative (VO/musik/visual/edit generatif) | analytic-ml (transkrip, deteksi wajah, dll) | none.
   Blok "sfx" (C21, lock #43, F8.5-d): {"jumlah":0,"catatan":"..."} -> N/A beralasan; {"items":[{"nama":..,"sumber":..,"lisensi":..,"sha256":..}]} -> PASS bila tiap aset
   punya sumber+lisensi+sha256, FAIL bila ada yang kurang; {"jumlah":N>0} tanpa daftar -> FAIL.
   Blok "vo" (lock #45, F8.5-b): {"suara":"Helio (avocado_v2:MAI_03)"} = kanonik (tidak dibuatkan baris — default yang benar tidak butuh baris,
   pola yang sama dengan hashtag/tag tanpa item). Suara lain WAJIB {"alasan_override":..,"tanggal_override":..,"pace_terukur_kata_dtk":..}
   -> lengkap = PASS (status [T] sampai disetujui G-HUMAN), kurang = FAIL. Bila "suara" tidak ada, disimpulkan dari catatan "tts"/tools
   (produksi lama); bila tidak bisa disimpulkan dan ada VO -> PENDING; bila tidak ada VO sama sekali -> tidak ada baris.
   --review-sheet review-sheet.md (F8.3-d, lock #11): membaca bagian "Pertanyaan dengar [T]" (§2a template); pertanyaan terbuka = PENDING
   (persetujuan tidak sah), semua tertutup = PASS, bagian tidak ada = PENDING, 0 pertanyaan = PASS.
manual_audit.json: {"M1":{"result":"PASS|FAIL|N/A","evidence":"...","reason":"...","waiver_by":"user","overrides_auto":"alasan"}}"""
import argparse, json, sys

def L(path): return json.load(open(path, encoding="utf-8")) if path else None

def check_sfx(P):
    """C21 (lock #43, F8.5-d): tiap SFX punya sumber + lisensi tercatat (sha256 ikut dicek)."""
    sfx = (P or {}).get("sfx")
    if sfx is None:
        return ("N/A", "tidak ada blok sfx di production.json — klip menyatakan tidak memakai SFX")
    if isinstance(sfx, dict):
        items = sfx.get("items") or sfx.get("daftar") or sfx.get("aset")
        if isinstance(items, list):
            if not items:
                return ("N/A", "blok sfx ada, daftar kosong — " + (str(sfx.get("catatan") or "tidak ada SFX").strip()))
            bad = [str(x.get("nama") or x.get("sumber") or "?") for x in items if not (isinstance(x, dict) and x.get("sumber") and x.get("lisensi") and x.get("sha256"))]
            if bad: return ("FAIL", f"SFX tanpa sumber/lisensi/sha256: {bad}")
            return ("PASS", f"{len(items)} SFX tercatat lengkap (sumber+lisensi+sha256)")
        n = sfx.get("jumlah")
        if n == 0:
            return ("N/A", "blok sfx: jumlah 0 — " + (str(sfx.get("catatan") or "tidak ada SFX").strip()))
        if isinstance(n, int) and n > 0:
            return ("FAIL", f"blok sfx jumlah {n} tanpa daftar aset (sumber/lisensi/sha256 tidak tercatat)")
        return ("PENDING", "blok sfx tanpa jumlah/daftar — tidak bisa dinilai")
    if isinstance(sfx, list):
        if not sfx: return ("N/A", "daftar sfx kosong — tidak ada SFX")
        bad = [str(x.get("nama") or x.get("sumber") or "?") for x in sfx if not (isinstance(x, dict) and x.get("sumber") and x.get("lisensi") and x.get("sha256"))]
        if bad: return ("FAIL", f"SFX tanpa sumber/lisensi/sha256: {bad}")
        return ("PASS", f"{len(sfx)} SFX tercatat lengkap (sumber+lisensi+sha256)")
    return ("PENDING", "format blok sfx tidak dikenal")

def check_vo_suara(P):
    """Lock #45 (F8.5-b): suara kanonik Helio; suara lain hanya lewat override lengkap. Mengembalikan None bila tidak ada baris
    (Helio terverifikasi, atau tidak ada VO sama sekali) — default yang benar tidak butuh baris."""
    P = P or {}
    vo = P.get("vo") if isinstance(P.get("vo"), dict) else {}
    suara = str(vo.get("suara") or "").strip()
    if not suara:
        hay = " ".join([str(P.get("tts") or "")] + [str(t.get("dipakai_untuk") or "") + " " + str(t.get("name") or "") for t in (P.get("tools") or []) if isinstance(t, dict)])
        if "avocado_v2:MAI_03" in hay or "Helio" in hay:
            return None  # produksi lama tanpa field vo.suara; catatan tts/tools menyebut Helio
        import re as _re
        if _re.search(r"\b(tts|voice|suara|narasi|gemini|charon)\b", hay, _re.I):
            # ada jejak VO/TTS tapi suaranya tidak bisa dipastikan — produser wajib mencatat vo.suara
            return ("PENDING", "suara VO tidak tercatat sebagai vo.suara dan tidak bisa disimpulkan dari catatan tts/tools — catat vo.suara di production.json")
        return None  # tidak ada VO narasi tercatat (mis. K1 dialog trailer)
    if "avocado_v2:MAI_03" in suara or suara.strip().lower().startswith("helio"):
        return None
    kurang = [k for k in ("alasan_override",) if not str(vo.get(k) or "").strip()]
    if not str(vo.get("tanggal_override") or vo.get("tanggal") or "").strip(): kurang.append("tanggal_override")
    pace = vo.get("pace_terukur_kata_dtk")
    if pace is None: kurang.append("pace_terukur_kata_dtk")
    if kurang:
        return ("FAIL", f"vo.suara '{suara}' bukan Helio tanpa override lengkap (kurang: {', '.join(kurang)}) — lihat lock #45")
    return ("PASS", f"override suara '{suara}': alasan + tanggal + pace terukur {pace} kata/dtk tercatat; status [T] sampai disetujui G-HUMAN")

def check_t_dengar(review_text):
    """F8.3-d / lock #11: persetujuan tidak sah selama pertanyaan dengar [T] terbuka. review_text None -> None (tanpa --review-sheet)."""
    if review_text is None: return None
    lines = review_text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("#") and "pertanyaan dengar" in l.lower()), None)
    if start is None:
        return ("PENDING", "review-sheet tanpa bagian 'Pertanyaan dengar [T]' — tambah §2a sebelum meminta persetujuan")
    rows = []
    for l in lines[start + 1:]:
        if l.startswith("#"): break
        s = l.strip()
        if s.startswith("|") and "---" not in s and not s.startswith("| #"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if any(cells): rows.append(cells)
    if not rows:
        return ("PASS", "bagian [T] dengar ada, 0 pertanyaan")
    tutup = ("tertutup", "dijawab", "diputus", "selesai", "✓", "√")
    terbuka = []
    for cells in rows:
        status = cells[-1] if len(cells) >= 6 else ""  # template §2a: kolom terakhir = Status; format lama (5 kolom) = tanpa status
        if not any(m in status.lower() for m in tutup):
            terbuka.append(cells[0] if cells else "?")
    if terbuka:
        return ("PENDING", f"pertanyaan dengar [T] masih terbuka: {terbuka} — tanyakan dulu, baru minta 'setuju?' (lock #11)")
    return ("PASS", f"{len(rows)} pertanyaan dengar [T] tertutup oleh telinga user")

def auto_checks(B, Q, S, P, cap, review_text=None):
    qc = {c["id"]: c for c in (Q or {"cek": []})["cek"]}; A = {}
    for cid in ("durasi", "format", "loudness", "digital_silence", "frame_hitam", "kartu_lint"):
        c = qc.get(cid)
        if not c: A[cid] = ("PENDING", "qc_report tidak berisi cek ini"); continue
        st = c["status"]
        if st == "WARN" and cid in ("digital_silence", "frame_hitam"): st = "PASS"; ev = c["detail"] + " (pengecualian dideklarasikan)"
        elif st == "WARN": st, ev = "PENDING", c["detail"]
        else: ev = c["detail"]
        A[cid] = (st, ev)
    if S and isinstance(S.get("A_teks_vs_naskah"), dict) and "ada_fail" in S["A_teks_vs_naskah"]:
        bad = [k["id"] for k in S["A_teks_vs_naskah"]["kartu"] if k["status"] == "FAIL"]
        A["teks_kartu"] = ("FAIL" if bad else "PASS", f"kartu tak cocok naskah: {bad}" if bad else "semua kartu cocok naskah (svc lapis A)")
    else: A["teks_kartu"] = ("PENDING", "svc_report lapis A tidak ada")
    t = B.get("tiktok", {})
    for key, items, label in (("hashtag", t.get("hashtags_required", []), "hashtag"), ("tag", t.get("tag_accounts", []), "tag akun")):
        if not items: continue
        if cap is None: A[key] = ("PENDING", "caption_tiktok.txt tidak diberikan")
        else:
            miss = [x for x in items if x.lower() not in cap]; A[key] = ("FAIL" if miss else "PASS", f"{label} hilang: {miss}" if miss else f"semua {label} ada: {items}")
    cta = B.get("cta", {})
    if cta.get("text") and cta.get("where", "caption") in ("caption", "keduanya"):
        A["cta"] = ("PENDING", "caption tidak diberikan") if cap is None else (("PASS", "CTA ada di caption") if cta["text"].lower() in cap else ("FAIL", "CTA tidak ada di caption"))
    if B.get("prohibitions", {}).get("ai_content"):
        tools = (P or {}).get("tools"); wv = (P or {}).get("ai_waiver") or B.get("ai_waiver") or {}
        valid = bool(wv.get("granted") and wv.get("by") == "user" and wv.get("date") and wv.get("scope"))
        if tools is None: A["larangan_ai"] = ("PENDING", "production.json tidak memuat daftar tools (kategori generative|analytic-ml|none)")
        else:
            cats = {x.get("category") for x in tools}
            if cats - {"generative", "analytic-ml", "none"}: A["larangan_ai"] = ("PENDING", "ada tool tanpa kategori valid")
            elif cats <= {"none"}: A["larangan_ai"] = ("PASS", "tidak ada tool AI")
            elif valid: A["larangan_ai"] = ("N/A", f"waiver user {wv.get('date')} lingkup '{wv.get('scope')}': {wv.get('note','')}; tool: " + ", ".join(f"{x['name']}[{x['category']}]" for x in tools if x['category'] != 'none'))
            elif "generative" in cats: A["larangan_ai"] = ("FAIL", "tool generatif dipakai tanpa waiver user (granted+by=user+date+scope)")
            else: A["larangan_ai"] = ("PASS", "hanya ML analitik (bukan generatif); dicatat; konfirmasi di G-HUMAN: " + ", ".join(x["name"] for x in tools if x["category"] == "analytic-ml"))
    mf = B.get("hook", {}).get("max_fraction", 0.2); d = (Q or {}).get("durasi")
    if P and "hook_time_s" in P and d: A["hook"] = ("PASS" if P["hook_time_s"] <= mf * d else "FAIL", f"hook di {P['hook_time_s']}s dari {d}s (batas {mf:.0%})")
    A["sfx"] = check_sfx(P)
    v = check_vo_suara(P)
    if v is not None: A["vo_suara"] = v
    t = check_t_dengar(review_text)
    if t is not None: A["t_dengar"] = t
    return A

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("brief", "qc", "svc", "caption", "production", "manual"): ap.add_argument("--" + k)
    ap.add_argument("--review-sheet")
    ap.add_argument("--out", default="brief_audit"); a = ap.parse_args()
    B, Q, S, P, M = L(a.brief), L(a.qc), L(a.svc), L(a.production), (L(a.manual) or {})
    cap = open(a.caption, encoding="utf-8").read().lower() if a.caption else None
    review_text = open(a.review_sheet, encoding="utf-8").read() if a.review_sheet else None
    A = auto_checks(B, Q, S, P, cap, review_text); used, rows = set(), []
    for it in B.get("manual_items", []):
        au = A.get(it.get("auto")) if it.get("auto") else None
        if it.get("auto"): used.add(it["auto"])
        m = M.get(it["id"]); man = None
        if m:
            if m.get("result") == "N/A" and not (m.get("reason") and m.get("waiver_by")): man = ("FAIL", "N/A tanpa reason+waiver_by")
            elif m.get("result") in ("PASS", "FAIL", "N/A") and m.get("evidence"): man = (m["result"], m["evidence"])
            else: man = ("FAIL", "bukti (evidence) kosong atau hasil tak valid")
        eff, ev, same = None, [], None
        if man and au and au[0] not in ("PENDING",):
            same = man[0] == au[0]
            if same: eff = man[0]
            elif m.get("overrides_auto"): eff = man[0]; ev.append(f"manual menimpa otomatis: {m['overrides_auto']}")
            else: eff = "FAIL"; ev.append(f"KONFLIK otomatis={au[0]} vs manual={man[0]}")
        elif man: eff = man[0]
        elif au and au[0] != "PENDING": eff = au[0]
        else: eff = "PENDING"
        rows.append({"id": it["id"], "syarat": it["requirement"], "otomatis": au[0] if au else "-", "manual": man[0] if man else "-", "selaras": same, "hasil": eff,
                     "bukti": " | ".join(ev + ([f"otomatis: {au[1]}"] if au else []) + ([f"manual: {man[1]}"] if man else []))})
    for k, (st, e) in A.items():
        if k not in used: rows.append({"id": "AUTO-" + k, "syarat": "cek otomatis (tak dipetakan ke butir)", "otomatis": st, "manual": "-", "selaras": None, "hasil": st if st != "N/A" else "N/A", "bukti": e})
    cnt = {k: sum(r["hasil"] == k for r in rows) for k in ("PASS", "FAIL", "N/A", "PENDING")}
    cnt["selaras_otomatis_manual"] = f"{sum(r['selaras'] is True for r in rows)}/{sum(r['selaras'] is not None for r in rows)}"
    # F8-1 (port dari draft-v4 v0.5.2-F8): catat sha256 tiap masukan — G-FINAL harus bisa direproduksi dari berkas beku.
    # (Pelajaran F7 K2 v6: rerun memberi 18 PASS/2 PENDING karena manual_audit.json di disk
    # sudah bukan yang dipakai saat G-FINAL; arsip brief_audit.json saat itu tidak memuat sha masukan.)
    import hashlib
    def _sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest() if p else None
    masukan = {}
    for _kunci, _path in (("brief", a.brief), ("qc", a.qc), ("svc", a.svc), ("caption", a.caption),
                          ("production", a.production), ("manual_audit", a.manual), ("review_sheet", a.review_sheet)):
        if _path: masukan[_kunci + "_sha256"] = _sha(_path)
    json.dump({"ringkasan": cnt, "masukan": masukan, "item": rows}, open(a.out + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(a.out + ".md", "w", encoding="utf-8") as f:
        f.write(f"# Audit brief\n\nRingkasan: PASS={cnt['PASS']} FAIL={cnt['FAIL']} N/A={cnt['N/A']} PENDING={cnt['PENDING']} · selaras otomatis↔manual: {cnt['selaras_otomatis_manual']}\n\n")
        if masukan: f.write("Masukan (sha256, F8-1 — bekukan berkas-berkas ini bersama audit ini): " + "; ".join(f"{k}={v}" for k, v in masukan.items()) + "\n\n")
        f.write("| ID | Syarat | Otomatis | Manual | Hasil | Bukti |\n|---|---|---|---|---|---|\n")
        for r in rows: f.write(f"| {r['id']} | {r['syarat']} | {r['otomatis']} | {r['manual']} | **{r['hasil']}** | {r['bukti']} |\n")
    print(cnt); sys.exit(1 if cnt["FAIL"] else 2 if cnt["PENDING"] else 0)

if __name__ == "__main__": main()
