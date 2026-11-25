#!/usr/bin/env python3
"""vod_chunks.py — Manifest kandidat -> perintah yt-dlp + tabel pemetaan waktu (K3 §15.2-15.3).

Masukan: manifest JSON {video_id/url, durasi_dtk, format, potongan: [{id, abs_start,
abs_end, pad_dtk}]} + info.json (opsional, untuk estimasi ukuran).
Keluaran: perintah yt-dlp per potongan + tabel pemetaan (abs_start, chunk_start,
berkas, sha bila sudah ada) + ringkasan anggaran P3.

Aturan yang ditegakkan (exit != 0 bila dilanggar):
- potongan (abs_end - abs_start + 2*pad) >= 600 dtk -> TOLAK (P3)
- abs_start < 0 atau abs_end > durasi -> TOLAK
- resume (P5): berkas potongan sudah ada + sha256 cocok dengan tabel lama -> "skip",
  bukan perintah unduh ulang.
"""
import hashlib
import json
import os
import sys

MAX_CHUNK_S = 600        # P3: tidak ada unduhan media >= 600 dtk per berkas
MAX_TOTAL_BYTES = 1_000_000_000  # P3: total media <= 1,0 GB [A]
PAD_DEFAULT = 15         # padding potongan kandidat (dtk) [A]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fmt_hms(t):
    t = int(round(t))
    return f"{t // 3600:02d}:{(t % 3600) // 60:02d}:{t % 60:02d}"


def plan(manifest, info=None, outdir=".", old_map=None):
    """-> (perintah, tabel, errors). Murni kecuali baca sha berkas yang sudah ada."""
    url = manifest.get("url") or f"https://www.youtube.com/watch?v={manifest.get('video_id')}"
    dur = manifest.get("durasi_dtk") or (info or {}).get("duration")
    fmt = manifest.get("format", "bv*[height<=480]+ba/b[height<=480]")
    errors = []
    cmds, table = [], []
    total_est = 0
    # estimasi byte/dtk dari format video+audio info.json (bila ada)
    rate = None
    if info:
        for f in info.get("formats", []):
            if f.get("height") == 480 and f.get("vcodec") != "none" and f.get("acodec") == "none":
                fs = f.get("filesize_approx")
                if fs and dur:
                    rate = fs / dur
                    break
    for p in manifest.get("potongan", []):
        pid = p["id"]
        pad = float(p.get("pad_dtk", PAD_DEFAULT))
        a0 = float(p["abs_start"]) - pad
        a1 = float(p["abs_end"]) + pad
        if a1 - a0 >= MAX_CHUNK_S:
            errors.append(f"{pid}: durasi potongan {a1 - a0:.0f} dtk >= {MAX_CHUNK_S} (P3)")
            continue
        if a0 < 0:
            errors.append(f"{pid}: abs_start-pad < 0")
            continue
        if dur and a1 > dur:
            errors.append(f"{pid}: abs_end+pad {a1:.0f} > durasi {dur:.0f}")
            continue
        fname = f"{pid}.mp4"
        fpath = os.path.join(outdir, fname)
        est = int(rate * (a1 - a0)) if rate else None
        if est:
            total_est += est
        old = (old_map or {}).get(pid)
        if old and old.get("sha256") and os.path.exists(fpath):
            if sha256_file(fpath) == old["sha256"]:
                cmds.append(f"# SKIP {pid} (resume P5: sudah ada, sha cocok)")
                table.append({"id": pid, "abs_start": round(a0, 1), "abs_end": round(a1, 1),
                              "chunk_start_abs": round(a0, 1), "berkas": fname,
                              "sha256": old["sha256"], "status": "sudah_ada"})
                continue
        sec = f"*{fmt_hms(a0)}-{fmt_hms(a1)}"
        cmds.append(f"yt-dlp --download-sections \"{sec}\" -f \"{fmt}\" -o \"{fpath}\" \"{url}\"")
        table.append({"id": pid, "abs_start": round(a0, 1), "abs_end": round(a1, 1),
                      "chunk_start_abs": round(a0, 1), "berkas": fname,
                      "sha256": None, "estimasi_byte": est, "status": "unduh"})
    if total_est and total_est > MAX_TOTAL_BYTES:
        errors.append(f"total estimasi {total_est} byte > 1,0 GB (P3)")
    return cmds, table, errors, total_est


def abs_to_chunk(abs_t, row):
    """Waktu absolut VOD -> detik di dalam berkas potongan."""
    return round(float(abs_t) - float(row["chunk_start_abs"]), 3)


def chunk_to_abs(t_chunk, row):
    """Detik di dalam berkas potongan -> waktu absolut VOD."""
    return round(float(row["chunk_start_abs"]) + float(t_chunk), 3)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--info", help="info.json yt-dlp (estimasi ukuran)")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--old-map", help="tabel pemetaan lama (JSON) untuk resume P5")
    ap.add_argument("--out", help="tulis perintah + tabel ke JSON")
    a = ap.parse_args(argv)
    manifest = json.load(open(a.manifest, encoding="utf-8"))
    info = json.load(open(a.info, encoding="utf-8")) if a.info else None
    old_map = None
    if a.old_map:
        old_map = {r["id"]: r for r in json.load(open(a.old_map, encoding="utf-8")).get("tabel", [])}
    cmds, table, errors, total_est = plan(manifest, info, a.outdir, old_map)
    if errors:
        for e in errors:
            print("TOLAK:", e, file=sys.stderr)
        return 2
    result = {"perintah": cmds, "tabel": table, "total_estimasi_byte": total_est,
              "video": manifest.get("video_id"), "format": manifest.get("format")}
    if a.out:
        json.dump(result, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\n".join(cmds))
    print(f"# total estimasi: {total_est} byte" if total_est else "# estimasi ukuran: tidak ada info format")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
