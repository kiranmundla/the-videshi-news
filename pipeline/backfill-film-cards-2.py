#!/usr/bin/env python3
"""Backfill missing film-info cards on trailer briefs flagged by videshi-health.

Reuses trailer-watch.py's _cast_from_title + cast_strip.render_cast_strip_block
logic and the same card structure. Only verifiable credits from video titles.
Writes via curl (urllib fails through the proxy for Supabase PATCH).

Usage: python3 backfill-film-cards-2.py [--apply]
Default is dry-run: prints what would change, no writes.
"""
import os, sys, re, json, html, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

for line in open(os.path.expanduser("~/workspace/.env.supabase")):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

import importlib.util as _ilu
def _load(name, path):
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_tw = _load("trailer_watch_mod", os.path.join(HERE, "trailer-watch.py"))
_cast_from_title = _tw._cast_from_title
_cs = _load("cast_strip_mod", os.path.join(HERE, "cast_strip.py"))
render_cast_strip_block = _cs.render_cast_strip_block

SLUGS = [
    "epic-anand-deverakonda-trailer-out-anand-deverakonda",
    "hanuman-ansh-a-powerful-divine-story-trailer-out-a-powerful-divine-sto",
    "kappi-squad-15th-october-trailer-out-15th-october",
    "ranabaali-trailer-october-8",
    "drive-teaser-out-prime-video-india",
    "official-trailer-birangana-2-sandipta-sen-nirjhar-mitra-15-oct-hoichoi",
    "418-trailer-out-the-last-warning",
    "marvel-television-s-visionquest-trailer-out-14th-october",
]

def sb_get(path):
    out = subprocess.run(
        ["curl", "-s", "--fail", "-H", f"apikey: {SB_KEY}",
         "-H", f"Authorization: Bearer {SB_KEY}", SB_URL + path],
        capture_output=True, text=True, timeout=30)
    out.check_returncode()
    return json.loads(out.stdout)

def sb_patch(path, data):
    out = subprocess.run(
        ["curl", "-s", "--fail", "-X", "PATCH", "-H", f"apikey: {SB_KEY}",
         "-H", f"Authorization: Bearer {SB_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "--data", json.dumps(data), SB_URL + path],
        capture_output=True, text=True, timeout=30)
    out.check_returncode()

def extract_vids(body):
    vids = re.findall(r"watch\?v=([A-Za-z0-9_-]{11})", body)
    for m in re.finditer(r"<youtube>\s*([A-Za-z0-9_-]{11})\s*</youtube>", body):
        if m.group(1) not in vids:
            vids.append(m.group(1))
    return vids

def video_title(vid):
    try:
        out = subprocess.run(
            ["curl", "-s", "--fail",
             f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json",
             "-H", "User-Agent: Mozilla/5.0", "--max-time", "15"],
            capture_output=True, text=True, timeout=30)
        out.check_returncode()
        return json.loads(out.stdout).get("title", "")
    except Exception:
        return ""

def build_card(credits, langs, media_type=None, release=None):
    info_rows = []
    cast_strip_html = ""
    if credits.get("cast"):
        try:
            cast_strip_html = render_cast_strip_block(credits["cast"])
        except Exception as e:
            print(f"    cast strip failed: {e}")
            cast_strip_html = ""
    for key, label in (("director", "Director"), ("host", "Host"),
                       ("producer", "Producer"), ("music", "Music")):
        if credits.get(key):
            info_rows.append((label, credits[key]))
    if media_type:
        info_rows.append(("Type", media_type))
    if release:
        info_rows.append(("Release", release))
    if langs:
        info_rows.append(("Languages", ", ".join(langs)))
    if not ((info_rows or cast_strip_html)
            and (any(credits.get(k) for k in
                     ("cast", "director", "host", "producer", "music"))
                 or media_type or release)):
        return ""
    return ('<div class="vdc"><div class="vdc-glow"></div>'
            '<div class="vdc-title">Film information</div>'
            '<div class="vdc-grid">'
            + "".join(
                f'<div class="vdc-stat"><div class="vdc-stat-val">{html.escape(v)}</div>'
                f'<div class="vdc-stat-lbl">{k}</div></div>'
                for k, v in info_rows)
            + "</div>"
            + cast_strip_html
            + "</div>")

def card_insert_position(body):
    m = re.search(r"<p>(<b>)?[A-Z][a-z]+(</b>)?\s*\u2014", body)
    if m:
        return m.start()
    m = re.search(r"<youtube>", body)
    if m:
        pm = re.search(r"<p>[^<]*</p>$", body[:m.start()])
        return pm.start() if pm else m.start()
    return len(body)

def main():
    apply = "--apply" in sys.argv
    patched, skipped = 0, []
    for slug in SLUGS:
        rows = sb_get(f"/rest/v1/p2_articles?select=id,headline,body&slug=eq.{slug}&limit=1")
        if not rows:
            skipped.append((slug, "not found")); continue
        r = rows[0]
        body = r["body"] or ""
        if "vdc-stat" in body:
            skipped.append((r["headline"], "already has card")); continue
        vids = extract_vids(body)
        if not vids:
            skipped.append((r["headline"], "no video IDs")); continue
        credits, langs = {}, []
        titles = []
        for vid in vids:
            title = video_title(vid)
            if not title:
                continue
            titles.append(title)
            lm = re.search(r"(?i)\b(hindi|tamil|telugu|kannada|malayalam|bengali|marathi)\b", title)
            if lm and lm.group(1).capitalize() not in langs:
                langs.append(lm.group(1).capitalize())
            if "cast" not in credits:
                tc = _cast_from_title(title)
                if tc:
                    credits["cast"] = tc
        card = build_card(credits, sorted(langs))
        if not card:
            skipped.append((r["headline"], "no verifiable credits")); continue
        print(f"\n{'PATCH' if apply else 'WOULD PATCH'}: {r['headline'][:70]}")
        print(f"  titles: {titles}")
        print(f"  credits: {credits} | langs: {langs}")
        if apply:
            pos = card_insert_position(body)
            sb_patch(f"/rest/v1/p2_articles?id=eq.{r['id']}",
                     {"body": body[:pos] + card + "\n" + body[pos:]})
            patched += 1
        else:
            patched += 1  # would-patch count
    print(f"\n{'Patched' if apply else 'Would patch'}: {patched}, skipped: {len(skipped)}")
    for h, reason in skipped:
        print(f"  SKIP [{reason}]: {h[:65]}")

if __name__ == "__main__":
    main()
