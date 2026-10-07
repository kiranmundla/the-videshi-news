#!/usr/bin/env python3
"""Cast headshot strip for film-information (vdc) cards.

Converts a flat cast name list ("A, B, C") into a mobile-friendly horizontal
strip of circular headshots with names underneath.

Photo sourcing is verified-only — a wrong photo is worse than no photo:
  1. person_images table (exact name match) — already identity-verified
  2. Wikipedia page-summary API — page title must match the name;
     disambiguation pages rejected
  3. Wikimedia Commons file search — filename must contain a name token
Otherwise the member renders as an initials circle. Never a guessed photo.

All HTTP goes through curl (urllib/requests fail through this host's proxy).
"""

import html
import json
import os
import re
import subprocess
import urllib.parse

UA = "TheVideshi/1.0 (cast-strip; contact: pipeline@thevideshi.com)"


def _curl_json(url, timeout=25):
    try:
        r = subprocess.run(
            ["curl", "-sS", "--fail", "--max-time", str(timeout),
             "-A", UA, url],
            capture_output=True, text=True, timeout=timeout + 5)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def _sb_env():
    env = {}
    for fn in ("~/workspace/.env.supabase",):
        p = os.path.expanduser(fn)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v.strip().strip('"').strip("'")
    return env.get("SUPABASE_URL"), env.get("SUPABASE_SERVICE_ROLE_KEY")


def split_cast(cast_str):
    """'Anirban Chakrabarti, Suhotra Mukhopadhyay' -> ['Anirban Chakrabarti', ...]."""
    if not cast_str:
        return []
    parts = re.split(r"[;,]|\s+and\s+", cast_str)
    names = []
    for p in parts:
        p = re.sub(r"\s+", " ", p.strip().strip(",;")).strip()
        # drop role hints some descriptions embed: "X as Y"
        p = re.split(r"\s+as\s+", p, flags=re.I)[0].strip()
        if len(p) >= 3 and re.search(r"[A-Za-z]", p):
            names.append(p)
    # de-dupe preserving order
    seen, out = set(), []
    for n in names:
        k = n.lower()
        if k not in seen:
            seen.add(k)
            out.append(n)
    return out


def _lookup_name(display):
    """Name used for photo lookup: strip honorifics like 'Late'."""
    n = re.sub(r"^(late|shri|smt|dr|mr|ms|mrs)\.?\s+", "", display, flags=re.I)
    n = re.sub(r"\s*\(.*?\)\s*", "", n).strip()
    return n or display


def _person_images_lookup(name):
    SB, K = _sb_env()
    if not SB or not K:
        return None
    q = urllib.parse.quote(name.lower())
    url = (f"{SB}/rest/v1/person_images?select=image_url"
           f"&person_name_lower=eq.{q}&limit=1")
    try:
        r = subprocess.run(
            ["curl", "-sS", "--fail", "--max-time", "15", url,
             "-H", f"apikey: {K}", "-H", f"Authorization: Bearer {K}"],
            capture_output=True, text=True, timeout=20)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    try:
        rows = json.loads(r.stdout)
    except Exception:
        return None
    if rows and rows[0].get("image_url"):
        return rows[0]["image_url"]
    return None


def _wikipedia_lookup(name):
    title = name.replace(" ", "_")
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + urllib.parse.quote(title))
    d = _curl_json(url)
    if not d or not isinstance(d, dict):
        return None
    if d.get("type") == "disambiguation":
        return None
    page_title = re.sub(r"\s*\(.*?\)\s*", "", d.get("title", "")).strip()
    # Title must match the person name (allows middle names/initials either way)
    nt = set(page_title.lower().split())
    nn = set(name.lower().split())
    if not nt or not nn or len(nt & nn) < min(2, len(nn)):
        return None
    thumb = (d.get("thumbnail") or {}).get("source")
    orig = (d.get("originalimage") or {}).get("source")
    return thumb or orig


def _commons_lookup(name):
    q = urllib.parse.quote(name)
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
           f"&list=search&srsearch={q}&srnamespace=6&srlimit=5")
    d = _curl_json(url)
    if not d:
        return None
    tokens = [t for t in name.lower().split() if len(t) > 2]
    # Strict: the target name must LEAD the filename ("Anirban_Chakrabarti.jpg",
    # "Raima Sen at event (cropped).jpg"). A mere token match accepts group
    # photos where the person is one of several people ("Manish Tewari ...
    # presenting ... to Kamaleshwar Mukherjee.jpg") — wrong as a headshot.
    want = re.sub(r"[\s_\-]+", " ", name.lower()).strip()
    for r in (d.get("query") or {}).get("search", []):
        ft = (r.get("title") or "").lower()
        if not ft.startswith("file:"):
            continue
        base = re.sub(r"\.\w+$", "", ft[5:])  # strip File: + extension
        base = re.sub(r"\s*\(cropped\)\s*", " ", base)
        base = re.sub(r"[\s_\-]+", " ", base).strip()
        if not base.startswith(want):
            continue
        if any(t in ft for t in tokens):
            # resolve to a direct file URL
            iu = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
                  "&prop=imageinfo&iiprop=url&iiurlwidth=300&titles="
                  + urllib.parse.quote(r["title"]))
            idata = _curl_json(iu)
            if not idata:
                continue
            pages = (idata.get("query") or {}).get("pages", {})
            for p in pages.values():
                ii = (p.get("imageinfo") or [{}])[0]
                if ii.get("thumburl") or ii.get("url"):
                    return ii.get("thumburl") or ii.get("url")
    return None


def resolve_headshot(display_name):
    """Verified headshot URL for a cast member, or None (initials fallback)."""
    name = _lookup_name(display_name)
    return (_person_images_lookup(name)
            or _wikipedia_lookup(name)
            or _commons_lookup(name))


def _initials(display_name):
    words = [w for w in re.split(r"\s+", _lookup_name(display_name)) if w]
    return "".join(w[0] for w in words[:2]).upper() or "?"


def render_cast_strip_block(cast_str, resolve=resolve_headshot):
    """Full vdc-cast HTML block for a cast string. Empty string if no names."""
    names = split_cast(cast_str)
    if not names:
        return ""
    members = []
    for n in names:
        photo = None
        try:
            photo = resolve(n)
        except Exception:
            photo = None
        if photo:
            members.append(
                '<div class="cast-member">'
                f'<img src="{html.escape(photo)}" alt="{html.escape(n)}" '
                'loading="lazy" referrerpolicy="no-referrer">'
                f"<span>{html.escape(n)}</span></div>")
        else:
            members.append(
                '<div class="cast-member">'
                f'<div class="cast-initials">{html.escape(_initials(n))}</div>'
                f"<span>{html.escape(n)}</span></div>")
    return ('<div class="vdc-cast"><div class="vdc-cast-lbl">Cast</div>'
            '<div class="cast-strip">'
            + "".join(members) +
            "</div></div>")


if __name__ == "__main__":
    import sys
    demo = sys.argv[1] if len(sys.argv) > 1 else (
        "Anirban Chakrabarti, Suhotra Mukhopadhyay, Raima Sen")
    for n in split_cast(demo):
        print(f"{n} -> {resolve_headshot(n) or 'initials'}")
