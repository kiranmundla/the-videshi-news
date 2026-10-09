#!/usr/bin/env python3
"""Backfill film-info card on the 'Doctor X: Mafia in White' trailer brief
flagged by videshi-health (2026-10-09 ~04:00 PDT run).

Card structure + placement mirrors pipeline/trailer-watch.py build_brief_article:
vdc card inserted before the first trailer-embed label paragraph (the <p>
immediately preceding the first <youtube>), keeping all existing body text.

Facts verified 2026-10-09:
- SBS Friday-Saturday medical noir (12 episodes), premiered Oct 9, 2026
- Directed by Lee Jung-rim, written by Pyeon Sung-geun
- Streams on Netflix from Oct 9 (Netflix India / Netflix PH teasers)
- Based on Japanese drama "Doctor X: Surgeon Michiko Daimon"
- Cast: Kim Ji-won, Kim Woo-seok, Lee Jung-eun, Son Hyun-joo, Jang Seung-jo
  (special appearance)
Sources: sbsstar.net (SBS Star official), filmfare.com, Netflix teaser page.

Usage: python3 backfill-film-cards-4.py [--apply]
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

ARTICLES = {
    "doctor-x-mafia-in-white-trailer-out": {
        "rows": [("Director", "Lee Jung-rim"),
                 ("Writer", "Pyeon Sung-geun"),
                 ("Type", "Series · 12 episodes"),
                 ("Release", "Oct 9, 2026 · SBS + Netflix"),
                 ("Languages", "Korean"),
                 ("Based on", "Doctor X: Surgeon Michiko Daimon (Japan)")],
        "cast": "Kim Ji-won, Kim Woo-seok, Lee Jung-eun, Son Hyun-joo",
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
