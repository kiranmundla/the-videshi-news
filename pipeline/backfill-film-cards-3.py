#!/usr/bin/env python3
"""Backfill film-info cards on the 7 flagged trailer briefs (2026-10-09 run).

Card structure + placement mirrors pipeline/trailer-watch.py build_brief_article:
vdc card inserted before the first trailer-embed label paragraph (the <p>
immediately preceding the first <youtube>), keeping all existing body text.

Usage: python3 backfill-film-cards-3.py [--apply]
"""
import os, sys, re, json, html, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

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

_cs = _load("cast_strip_mod", os.path.join(HERE, "cast_strip.py"))
render_cast_strip_block = _cs.render_cast_strip_block

# Per-article data: all facts verified (see research in task log).
ARTICLES = {
    "epic-anand-deverakonda-trailer-out-anand-deverakonda": {
        "rows": [("Director", "Aditya Haasan"),
                 ("Music", "Hesham Abdul Wahab"),
                 ("Type", "Film"),
                 ("Release", "Sep 11, 2026 · Netflix Oct 9")],
        "cast": "Anand Deverakonda, Vaishnavi Chaitanya",
    },
    "hanuman-ansh-a-powerful-divine-story-trailer-out-a-powerful-divine-sto": {
        "rows": [("Director", "Vishal Chaturvedi"),
                 ("Type", "Film"),
                 ("Release", "Oct 9, 2026 (Telugu)"),
                 ("Languages", "Telugu")],
        "cast": "Shobhinaw Satyaa, Vihaan Shedge, Chandan K Anand, Purnima Tiwari",
    },
    "kappi-squad-15th-october-trailer-out-15th-october": {
        "rows": [("Director", "Belraj Kalarickal"),
                 ("Producer", "Rahul Riji Nair · First Print Studios"),
                 ("Type", "Series · 100 episodes"),
                 ("Release", "Oct 15, 2026 · JioHotstar"),
                 ("Languages", "Malayalam")],
        "cast": "Rinosh George, Anagha Ajith, Diya Deepan, Joel Joseph, Abhirami Dayanandan",
    },
    "ranabaali-trailer-october-8": {
        "rows": [("Director", "Rahul Sankrityan"),
                 ("Music", "Ajay-Atul"),
                 ("Type", "Film"),
                 ("Release", "Oct 16, 2026")],
        "cast": "Vijay Deverakonda, Rashmika Mandanna, Arnold Vosloo",
    },
    "drive-teaser-out-prime-video-india": {
        "rows": [("Director", "Sergej Moya"),
                 ("Type", "Film"),
                 ("Release", "Oct 28, 2026 · Prime Video")],
        "cast": "Lisa-Marie Koroll, Amin Baahmed, Gustav Schmidt, Mišel Matičević",
    },
    "418-trailer-out-the-last-warning": {
        "rows": [("Director", "Kirtan Nadagouda"),
                 ("Producer", "Naveen Yerneni, Ravi Shankar"),
                 ("Music", "Venky GG"),
                 ("Type", "Horror thriller"),
                 ("Release", "Oct 23, 2026"),
                 ("Languages", "Telugu, Kannada, Tamil, Hindi")],
        "cast": "Chaithra Achar, Surya Raj Veerabathini, Charan Lakkaraju, Preethi Pagadala, Shashank Patil",
    },
    "marvel-television-s-visionquest-trailer-out-14th-october": {
        "rows": [("Showrunner", "Terry Matalas"),
                 ("Type", "Miniseries"),
                 ("Release", "Oct 14, 2026 · JioHotstar / Disney+")],
        "cast": "Paul Bettany, James Spader, Ruaridh Mollica, Todd Stashwick",
    },
}


def build_card(rows, cast):
    strip = ""
    if cast:
        try:
            strip = render_cast_strip_block(cast)
        except Exception as e:
            print(f"    cast strip failed: {e}")
    if not (rows or strip):
        return ""
    return ('<div class="vdc"><div class="vdc-glow"></div>'
            '<div class="vdc-title">Film information</div>'
            '<div class="vdc-grid">'
            + "".join(
                f'<div class="vdc-stat"><div class="vdc-stat-val">{html.escape(v)}</div>'
                f'<div class="vdc-stat-lbl">{k}</div></div>'
                for k, v in rows)
            + "</div>"
            + strip
            + "</div>")


def insert_pos(body):
    """Before the label <p> directly preceding the first <youtube>,
    else right before the first <youtube>."""
    i = body.find("<youtube>")
    if i < 0:
        return len(body)
    tail = body[:i]
    m = re.search(r"<p>(?:<b>)?[^<]{1,80}(?:</b>)?(?:\s*—[^<]*)?</p>\s*$", tail)
    if m:
        return m.start()
    return i


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


def main():
    apply = "--apply" in sys.argv
    for slug, cfg in ARTICLES.items():
        rows = sb_get(f"/rest/v1/p2_articles?select=id,headline,body&slug=eq.{slug}&limit=1")
        if not rows:
            print(f"SKIP [not found]: {slug}"); continue
        r = rows[0]
        body = r["body"] or ""
        if "vdc-stat" in body:
            print(f"SKIP [already has card]: {r['headline'][:60]}"); continue
        card = build_card(cfg["rows"], cfg["cast"])
        if not card:
            print(f"SKIP [empty card]: {r['headline'][:60]}"); continue
        pos = insert_pos(body)
        anchor = body[pos:pos+90].replace("\n", " ")
        print(f"\n{'PATCH' if apply else 'WOULD PATCH'}: {r['headline'][:70]}")
        print(f"  insert at {pos}, anchor: {anchor!r}")
        print(f"  card rows: {[k for k, v in cfg['rows']]} | cast: {cfg['cast']}")
        if apply:
            new_body = body[:pos] + card + "\n" + body[pos:]
            sb_patch(f"/rest/v1/p2_articles?id=eq.{r['id']}", {"body": new_body})
            print("  patched OK")


if __name__ == "__main__":
    main()
