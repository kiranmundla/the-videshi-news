#!/usr/bin/env python3
"""One-time backfill: add missing film-info cards to trailer-watch brief articles.

Identifies trailer-watch briefs (published, has <youtube>, no vdc-stat marker)
and reconstructs the film-info card from video titles using the same
_cast_from_title + render_cast_strip_block logic as trailer-watch.py.

Only uses verifiable credits from video titles/descriptions — never invents names.
Run once; trailer-watch.py now generates cards at creation time.
"""
import os
import sys
import json
import re
import html
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

for line in open(os.path.expanduser("~/workspace/.env.supabase")):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v

import importlib.util as _ilu

def _load_trailer_watch():
    spec = _ilu.spec_from_file_location(
        "trailer_watch_mod", os.path.join(HERE, "trailer-watch.py"))
    mod = _ilu.module_from_spec(spec)
    sys.modules["trailer_watch_mod"] = mod
    spec.loader.exec_module(mod)
    return mod

_tw = _load_trailer_watch()
_cast_from_title = _tw._cast_from_title
_extract_credits = _tw.extract_credits
from cast_strip import render_cast_strip_block  # noqa: E402

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def api(path, method="GET", data=None):
    req = urllib.request.Request(
        SB_URL + path, method=method,
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "application/json",
                 "Prefer": "return=representation"})
    body = json.dumps(data).encode() if data else None
    with urllib.request.urlopen(req, data=body, timeout=20) as r:
        return json.load(r)


def extract_vids(body):
    vids = re.findall(r"watch\?v=([A-Za-z0-9_-]{11})", body)
    for m in re.finditer(r"<youtube>\s*([A-Za-z0-9_-]{11})\s*</youtube>", body):
        if m.group(1) not in vids:
            vids.append(m.group(1))
    return vids


def video_title(vid, seen):
    title = seen.get(vid, {}).get("title", "")
    if title or seen.get(vid, {}).get("not_trailer"):
        return title
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r).get("title", "")
    except Exception:
        return ""


def build_card(credits, langs, media_type=None, release=None):
    """Mirror the vdc card structure from trailer-watch.build_brief_article."""
    info_rows = []
    cast_strip_html = ""
    if credits.get("cast"):
        try:
            cast_strip_html = render_cast_strip_block(credits["cast"])
        except Exception:
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
    # Same gate as trailer-watch: require a real credit, type, or release
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
    """Same position as trailer-watch: after the diaspora paragraph,
    before the first language-version header."""
    # Find first language header like <p><b>Hindi</b> or <p>Hindi —
    m = re.search(r"<p>(<b>)?[A-Z][a-z]+(</b>)?\s*\u2014", body)
    if m:
        return m.start()
    # Fallback: before first <youtube> tag
    m = re.search(r"<youtube>", body)
    if m:
        # back up to the preceding <p> header if present
        pm = re.search(r"<p>[^<]*</p>$", body[:m.start()])
        return pm.start() if pm else m.start()
    return len(body)


def main():
    seen = json.load(open(os.path.join(HERE, ".state", "trailer-watch-seen.json")))
    candidates = json.load(open("/tmp/no_card_all.json"))

    # Filter to true trailer briefs
    briefs = [c for c in candidates
              if c["has_makers"]
              or (re.search(r"(?i)(trailer|teaser)\s+out", c["headline"])
                  and c["body_len"] < 3000)]
    # Also include tagged ones
    tagged = json.load(open("/tmp/trailer_tagged_no_card.json"))
    tagged_ids = {t["id"] for t in tagged}
    brief_ids = {b["id"] for b in briefs} | tagged_ids

    patched, skipped = 0, []
    for c in candidates:
        if c["id"] not in brief_ids:
            continue
        rows = api(f"/rest/v1/p2_articles?select=id,body&id=eq.{c['id']}&limit=1")
        if not rows:
            skipped.append((c["headline"], "not found"))
            continue
        body = rows[0]["body"] or ""
        if "vdc-stat" in body:
            skipped.append((c["headline"], "already has card"))
            continue

        vids = extract_vids(body)
        if not vids:
            skipped.append((c["headline"], "no video IDs in body"))
            continue
        credits = {}
        langs = []
        for vid in vids:
            title = video_title(vid, seen)
            if not title:
                continue
            # language from title
            lm = re.search(r"(?i)\b(hindi|tamil|telugu|kannada|malayalam|bengali|marathi)\b", title)
            if lm and lm.group(1).capitalize() not in langs:
                langs.append(lm.group(1).capitalize())
            if "cast" not in credits:
                tc = _cast_from_title(title)
                if tc:
                    credits["cast"] = tc

        card = build_card(credits, sorted(langs))
        if not card:
            skipped.append((c["headline"], "no verifiable credits"))
            continue

        pos = card_insert_position(body)
        new_body = body[:pos] + card + "\n" + body[pos:]
        api(f"/rest/v1/p2_articles?id=eq.{c['id']}", method="PATCH",
            data={"body": new_body})
        patched += 1
        print(f"  PATCHED: {c['headline'][:60]} (cast: {credits.get('cast', '')[:50]})")

    print(f"\nDone: {patched} patched, {len(skipped)} skipped")
    for h, reason in skipped:
        print(f"  SKIP [{reason}]: {h[:60]}")


if __name__ == "__main__":
    main()
