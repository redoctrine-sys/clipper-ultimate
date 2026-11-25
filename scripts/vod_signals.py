#!/usr/bin/env python3
"""vod_signals.py — Sinyal non-transkrip -> kandidat.json (K3-panjang.md §15.1, F9.4).

Masukan: info.json yt-dlp (--dump-single-json) + opsional chat replay (live_chat JSON
dari yt-dlp --write-subs --sub-langs live_chat) + opsional komentar (--write-comments).
Keluaran: kandidat.json berisi 6-9 jendela (waktu absolut + sinyal pendukung + skor)
dan catatan_k5 (jendela yang dicurigai gameplay-only, TIDAK diunduh di F9.5).

Tanpa satu pun sinyal -> exit != 0 (bukan kandidat kosong yang diam-diam).
Tidak ada transkripsi di sini (P1): skrip ini tidak pernah memanggil whisper.
"""
import json
import math
import re
import statistics
import sys

BIN_S = 10            # lebar bin chat (dtk)
MEDIAN_WIN = 30       # bin median bergulir = 5 menit
SPIKE_MIN = 10        # pesan minimum per bin agar dihitung lonjakan [A]
SPIKE_RATIO = 2.0     # bin > median * rasio = lonjakan [A]
LAG_S = 15            # geser mundur jendela (tengah rentang lag chat 5-20 dtk) [A]
TOKENS = ("wkwk", "wkwkw", "haha", "anjir", "anjir", "gila", "ngakak", "hihu", "hihuu")
MIN_WIN_S = 30        # jendela kandidat minimum (dtk)
MAX_WIN_S = 90        # jendela kandidat maksimum (dtk)
MAX_KANDIDAT = 9
MIN_KANDIDAT = 6
# Ambang gameplay-only RELATIF (temuan F9, chat Windah nyata): curiga bila densitas token
# jendela < 0.5x densitas baseline seluruh chat; bila baseline < 0.02 heuristik tidak
# dipakai. Ambang absolut 0.10 yang lama DITARIK: baseline chat nyata hanya ~0.03,
# jadi ambang absolut menandai semua lonjakan sebagai gameplay-only.
GAMEPLAY_DENS_RATIO = 0.5
GAMEPLAY_BASE_MIN = 0.02
                                # -> dicurigai gameplay-only [A]


def _hms_to_s(s):
    p = s.split(":")
    try:
        if len(p) == 2:
            return int(p[0]) * 60 + int(p[1])
        if len(p) == 3:
            return int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
    except ValueError:
        return None
    return None


def iter_json_array(path, chunk_size=1 << 20):
    """Yield elemen array JSON satu per satu tanpa memuat seluruh berkas ke RAM.
    Perlu untuk live_chat replay (270 MB, ~255 ribu pesan; json.load butuh >1 GB).
    Berkas kecil tetap jalan (satu chunk sudah cukup). chunk_size hanya untuk tes."""
    dec = json.JSONDecoder()
    with open(path, encoding="utf-8") as fh:
        buf = fh.read(chunk_size)
        i = 0
        while i < len(buf) and buf[i] in " \t\r\n":
            i += 1
        if i < len(buf) and buf[i] == "[":
            i += 1
        buf = buf[i:]
        while True:
            buf = buf.lstrip(" \t\r\n,")
            if not buf:
                chunk = fh.read(chunk_size)
                if not chunk:
                    return
                buf = chunk
                continue
            if buf[0] == "]":
                return
            try:
                obj, end = dec.raw_decode(buf)
            except json.JSONDecodeError:
                chunk = fh.read(chunk_size)
                if not chunk:
                    raise
                buf += chunk
                continue
            yield obj
            buf = buf[end:]


def parse_chat(path):
    """live_chat JSON yt-dlp -> [(t_dtk, teks)]. Tahan terhadap beberapa bentuk."""
    out = []
    for it in iter_json_array(path):
        t = None
        txt = ""
        act = it.get("replayChatItemAction", it)
        if "videoOffsetTimeMsec" in act:
            try:
                t = float(act["videoOffsetTimeMsec"]) / 1000.0
            except (TypeError, ValueError):
                t = None
        for a in act.get("actions", [act]):
            item = a.get("addChatItemAction", a).get("item", {})
            rend = item.get("liveChatTextMessageRenderer") or item.get("liveChatPaidMessageRenderer") or {}
            # timestampUsec adalah epoch dinding, BUKAN offset video — jangan dipakai
            # sebagai t (temuan F9: berkas nyata menyimpannya sebagai string epoch).
            runs = (rend.get("message") or {}).get("runs", [])
            txt = "".join(r.get("text", "") for r in runs if isinstance(r, dict))
            if txt:
                break
        if t is not None and txt:
            out.append((float(t), txt))
    return out


def parse_comments(path):
    """comments JSON yt-dlp -> [(t_dtk, teks)] dari timestamp HH:MM:SS/MM:SS di teks."""
    data = json.load(open(path, encoding="utf-8"))
    out = []
    for c in data.get("comments", []):
        txt = c.get("text") or ""
        for m in re.finditer(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", txt):
            t = _hms_to_s(m.group(1))
            if t is not None:
                out.append((float(t), txt))
                break
    return out


def parse_chapters(info):
    ch = info.get("chapters") or []
    return [(float(c["start_time"]), c.get("title", "")) for c in ch if c.get("start_time") is not None]


def parse_heatmap(info):
    """heatmap yt-dlp: list {start_time, end_time, value} atau None."""
    hm = info.get("heatmap")
    if not hm:
        return []
    return [(float(h["start_time"]), float(h["end_time"]), float(h.get("value", 0)))
            for h in hm if h.get("start_time") is not None]


def parse_desc_timestamps(info):
    desc = info.get("description") or ""
    out = []
    for m in re.finditer(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", desc):
        t = _hms_to_s(m.group(1))
        if t is not None:
            out.append(float(t))
    return sorted(set(out))


def bin_chat(msgs, duration):
    """[(t, teks)] -> per bin 10 dtk: (jumlah, jumlah_ber_token)."""
    nb = int(math.ceil(duration / BIN_S)) or 1
    cnt = [0] * nb
    tok = [0] * nb
    for t, txt in msgs:
        if t < 0 or t >= duration:
            continue
        i = int(t // BIN_S)
        cnt[i] += 1
        low = txt.lower()
        if any(k in low for k in TOKENS):
            tok[i] += 1
    return cnt, tok


def find_spikes(cnt, tok):
    """Bin lonjakan: cnt > median_bergulir * rasio dan cnt >= minimum."""
    spikes = []
    n = len(cnt)
    for i, c in enumerate(cnt):
        lo = max(0, i - MEDIAN_WIN)
        med = statistics.median(cnt[lo:i]) if i > lo else 0
        if c >= SPIKE_MIN and (med == 0 and c >= SPIKE_MIN or c > med * SPIKE_RATIO):
            spikes.append(i)
    return spikes


def merge_bins(spikes):
    """Gabung bin lonjakan yang berdekatan (celah <= 2 bin = 20 dtk)."""
    if not spikes:
        return []
    groups = [[spikes[0]]]
    for b in spikes[1:]:
        if b - groups[-1][-1] <= 3:
            groups[-1].append(b)
        else:
            groups.append([b])
    return groups


def score_window(start, end, cnt, tok, anchors, heat):
    """Skor sinyal jendela: lonjakan chat + token + jangkar (chapter/komentar) + heatmap."""
    n = len(cnt)
    i0 = min(int(start // BIN_S), max(0, n - 1))
    i1 = min(int(end // BIN_S), max(0, n - 1))
    msgs = sum(cnt[i0:i1 + 1])
    toks = sum(tok[i0:i1 + 1])
    win = cnt[max(0, i0 - MEDIAN_WIN):i0] if i0 > 0 else []
    med = statistics.median(win) if win else 0
    ratio = (msgs / max(1, (i1 - i0 + 1))) / med if med else (msgs / max(1, (i1 - i0 + 1)))
    score = 0.0
    score += min(3.0, ratio)                 # kekuatan lonjakan (maks 3)
    score += min(2.0, toks / 5.0)            # token tawa/kaget (maks 2)
    if any(start - 30 <= a <= end + 30 for a, _ in anchors):
        score += 2.0                          # jangkar chapter/komentar dekat
    if any(hs <= end and he >= start for hs, he, _ in heat):
        score += 1.0                          # puncak heatmap tumpang-tindih
    return round(score, 2), msgs, toks


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--info", required=True, help="info.json yt-dlp")
    ap.add_argument("--chat", help="live_chat JSON (yt-dlp --write-subs live_chat)")
    ap.add_argument("--comments", help="comments JSON (yt-dlp --write-comments)")
    ap.add_argument("--out", required=True, help="kandidat.json keluaran")
    ap.add_argument("--max", type=int, default=MAX_KANDIDAT)
    ap.add_argument("--min", type=int, default=MIN_KANDIDAT)
    a = ap.parse_args(argv)
    info = json.load(open(a.info, encoding="utf-8"))
    duration = float(info.get("duration") or 0)
    if duration <= 0:
        print("info.json tanpa durasi", file=sys.stderr)
        return 2
    chapters = parse_chapters(info)
    heat = parse_heatmap(info)
    desc_ts = parse_desc_timestamps(info)
    anchors = [(t, "chapter") for t, _ in chapters] + [(t, "deskripsi") for t in desc_ts]
    chat = parse_chat(a.chat) if a.chat else []
    comments = parse_comments(a.comments) if a.comments else []
    anchors += [(t, "komentar") for t, _ in comments]
    signals_found = bool(chapters or heat or desc_ts or chat or comments)
    if not signals_found:
        print("TIDAK ADA SINYAL: tanpa chapter/heatmap/deskripsi/chat/komentar", file=sys.stderr)
        return 3
    cnt, tok = bin_chat(chat, duration)
    # Densitas token baseline chat: heuristik gameplay-only harus RELATIF terhadapnya.
    # Temuan F9 (chat Windah nyata): baseline hanya ~3% (5.801/193.036 pesan), jadi
    # ambang absolut 10% menandai SEMUA lonjakan sebagai gameplay-only (k3 = 0).
    # Aturan baru: curiga gameplay-only bila densitas < setengah baseline; bila baseline
    # < 2% (token praktis tidak dipakai), heuristik tidak bisa membedakan -> jangan tandai.
    base_dens = (sum(tok) / sum(cnt)) if sum(cnt) else 0.0
    spikes = find_spikes(cnt, tok)
    groups = merge_bins(spikes)
    windows = []
    dilewati = []
    for g in groups:
        start = g[0] * BIN_S - LAG_S
        end = (g[-1] + 1) * BIN_S - LAG_S
        start = max(0.0, start)
        if start < LAG_S:
            # Jendela di awal VOD tidak bisa diberi pad 15 dtk untuk F9.5 (chunk_start < 0
            # ditolak vod_chunks); biasanya juga hanya hype awal stream, bukan momen.
            dilewati.append({"alasan": "awal VOD (tidak bisa pad 15 dtk)",
                             "abs_start": round(start, 1), "abs_end": round(max(0.0, end), 1)})
            continue
        if end - start < MIN_WIN_S:
            end = min(duration, start + MIN_WIN_S)
        if end - start > MAX_WIN_S:
            end = start + MAX_WIN_S
        score, msgs, toks = score_window(start, end, cnt, tok, anchors, heat)
        sig = []
        if msgs:
            sig.append(f"lonjakan chat: {msgs} pesan/bin puncak")
        if toks:
            sig.append(f"token tawa/kaget: {toks}")
        near = [f"{kind}@{t:.0f}" for t, kind in anchors if start - 30 <= t <= end + 30]
        sig += [f"jangkar {x}" for x in near[:3]]
        if any(hs <= end and he >= start for hs, he, _ in heat):
            sig.append("puncak heatmap")
        density = (toks / msgs) if msgs else 0.0
        windows.append({"abs_start": round(start, 1), "abs_end": round(end, 1),
                        "sinyal": sig, "skor": score, "pesan": msgs, "token": toks,
                        "kemungkinan_gameplay_only": bool(
                            msgs >= SPIKE_MIN and base_dens >= GAMEPLAY_BASE_MIN
                            and density < GAMEPLAY_DENS_RATIO * base_dens)})
    windows.sort(key=lambda w: -w["skor"])
    k5 = [w for w in windows if w["kemungkinan_gameplay_only"]]
    k3 = [w for w in windows if not w["kemungkinan_gameplay_only"]]
    # Jangkar (chapter/deskripsi/komentar) melengkapi k3 bila lonjakan chat tidak cukup:
    # kelompokkan jangkar per jendela 60 dtk, urutkan menurut jumlah jangkar
    # (komentar ber-timestamp ramai = momen menonjol). Sebelumnya fallback ini hanya
    # jalan bila TIDAK ADA lonjakan sama sekali — temuan F9: bila semua lonjakan
    # dicurigai gameplay-only, k3 = 0 padahal jangkar komentar ada.
    if len(k3) < a.min and anchors:
        clusters = {}
        for t, kind in anchors:
            if t > duration:
                continue
            clusters.setdefault(int(t // 60), []).append((t, kind))
        ranked = sorted(clusters.items(), key=lambda kv: -len(kv[1]))
        dipilih = [(w["abs_start"], w["abs_end"]) for w in k3]
        for _key, items in ranked:
            if len(k3) >= a.max:
                break
            t0 = sum(t for t, _ in items) / len(items)
            s, e = max(0.0, t0 - 5), min(duration, t0 + 55)
            if any(s < pe and e > ps for ps, pe in dipilih):
                continue  # tumpang tindih dengan jendela yang sudah dipilih (satu lonjakan;
                          # dua momen sedekat ini muat dalam satu chunk F9.5)
            dipilih.append((s, e))
            sc, _, _ = score_window(s, e, cnt, tok, anchors, heat)
            kinds = sorted({k for _, k in items})
            k3.append({"abs_start": round(s, 1), "abs_end": round(e, 1),
                       "sinyal": [f"jangkar {','.join(kinds)} x{len(items)} (tengah {t0:.0f})"],
                       "skor": sc, "pesan": 0, "token": 0, "kemungkinan_gameplay_only": False})
    k3 = k3[:a.max]
    if len(k3) < a.min:
        print(f"HANYA {len(k3)} kandidat K3 (min {a.min}) — sinyal tidak cukup", file=sys.stderr)
        return 4
    out = {"sumber": info.get("id"), "durasi_dtk": duration,
           "kandidat": k3, "catatan_k5": k5,
           "dilewati": dilewati,
           "sinyal_tersedia": {"chapter": len(chapters), "heatmap": len(heat),
                               "timestamp_deskripsi": len(desc_ts), "pesan_chat": len(chat),
                               "komentar_ber_timestamp": len(comments)},
           "parameter": {"bin_dtk": BIN_S, "lag_geser_dtk": LAG_S, "token": list(TOKENS),
                         "densitas_token_baseline": round(base_dens, 4)}}
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"OK: {len(k3)} kandidat K3 + {len(k5)} catatan_k5 -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
