#!/usr/bin/env python3
"""Cast headshot strip for film-information (vdc) cards.

Converts a flat cast name list ("A, B, C") into a mobile-friendly horizontal
strip of circular headshots with names underneath.

Photo sourcing is verified-only — a wrong photo is worse than no photo:
  1. person_images table (exact name match) — already identity-verified
  2. Wikipedia page-summary API — page title must match the name;
     disambiguation pages rejected; an exact-title page is ALSO rejected
     when its own data proves it is a different person (see
     _summary_identity_conflict: the title match alone is not identity
     proof — "Beatrice Campbell" the Northern Irish stage actress,
     1922–1979, is not the newcomer child actress in a 2027 film, and
     her page thumbnail is literally her husband Nigel Patrick)
  3. Wikimedia Commons file search — filename must contain a name token;
     for AMBIGUOUS names (single-token, or Wikipedia says the name is a
     disambiguation page, or the exact-title Wikipedia page is a
     different person) the filename must match the name EXACTLY —
     "Atul_Kumar_MD" and "Mathew_Brady_1875" are different people and
     must fall back to initials, not headshots
Otherwise the member renders as an initials circle. Never a guessed photo.

All HTTP goes through curl (urllib/requests fail through this host's proxy).
"""

import html
import json
import os
import re
import subprocess
import unicodedata
import urllib.parse
from datetime import datetime, timezone

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


_wiki_summary_cache = {}


def _wiki_summary(name):
    """Cached Wikipedia page-summary dict for a person name (or None)."""
    key = name.lower()
    if key not in _wiki_summary_cache:
        title = name.replace(" ", "_")
        url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
               + urllib.parse.quote(title))
        _wiki_summary_cache[key] = _curl_json(url)
    return _wiki_summary_cache[key]


def _fold(tok):
    """Lowercase + strip diacritics so 'Mišel' and 'Misel' compare equal."""
    return "".join(c for c in unicodedata.normalize("NFKD", tok.lower())
                   if not unicodedata.combining(c))


_YEAR_RE = r"(1[6-9]\d{2}|20\d{2})"
# Words that commonly appear in image filenames without naming a person.
# Used only to decide whether a filename positively names SOMEONE ELSE —
# never as evidence FOR an identity.
_FILENAME_STOPWORDS = {
    "the", "and", "at", "in", "on", "of", "for", "with", "from", "by",
    "film", "films", "movie", "festival", "cannes", "tiff", "sxsw",
    "sundance", "berlinale", "venice", "premiere", "press", "conference",
    "panel", "event", "events", "awards", "award", "red", "carpet",
    "cropped", "crop", "portrait", "photo", "photograph", "image",
    "img", "dsc", "pic", "still", "stills", "trailer", "official",
    "actor", "actress",
}


def _image_names_other_person(url, name):
    """True when an image filename positively names a DIFFERENT person.

    Fires only when (a) NONE of the target's name tokens appear in the
    filename, and (b) after stripping digits/years and generic words the
    filename still holds >=2 name-like tokens — i.e. it reads as another
    person's name ("Nigel_Patrick.jpg" on the Beatrice Campbell page).
    Generic filenames ("DSC_4471.jpg", festival/press shots) carry no
    such evidence and return False.
    """
    if not url:
        return False
    base = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    base = base.split("?")[0].split("#")[0]  # drop utm/query junk
    base = re.sub(r"^\d+px-", "", base)  # thumbnail size prefix
    base = re.sub(r"\.(jpe?g|png|webp|gif|tiff?)$", "", base, flags=re.I)
    base = re.sub(r"\.(jpe?g|png|webp)$", "", base, flags=re.I)  # thumb ext
    # Letter runs in any script (š, č, Hangul, ...) — a narrow Latin-1
    # class would shred accented names into meaningless fragments.
    toks = [_fold(t) for t in re.findall(r"[^\W\d_]+", base) if len(t) >= 3]
    name_toks = {_fold(t) for t in name.lower().split() if len(t) > 2}
    # Overlap = any exact token match, or a filename token that CONTAINS
    # a name token (merged-name files: "PaulBettany-byPhilipRomano.jpg"
    # is one token, but it plainly names Paul Bettany).
    for tok in toks:
        for ntok in name_toks:
            if tok == ntok or (len(ntok) >= 4 and ntok in tok):
                return False
    cand = [t for t in toks if t not in _FILENAME_STOPWORDS]
    return len(cand) >= 2


def _bio_date_parentheticals(d, name):
    """Parentheticals that carry the PAGE PERSON's life dates — and only
    those. Two places qualify:

      * the trailing parenthetical of the Wikidata short description
        ("British actress (1922–1979)", "American actress (born 1949)")
      * the lead parenthetical of the extract, immediately after the
        person's name ("John Smith (3 May 1930 – 2 June 2020) was ...")

    Other parentheticals in the extract are filmography/show dates
    ("... Sex Education (2019–2023) ...") and must NEVER be read as
    life dates — that misread is the exact false positive this guards.
    """
    out = []
    desc = (d.get("description") or "").rstrip()
    if desc.endswith(")"):
        m = re.search(r"\(([^()]*)\)$", desc)
        if m:
            out.append(m.group(1))
    extract = d.get("extract") or ""
    title = (d.get("title") or "").replace("_", " ")
    for who in (title, name):
        if not who:
            continue
        m = re.match(re.escape(who) + r"\s*\(([^()]*)\)", extract)
        if m:
            out.append(m.group(1))
            break
    return out


def _summary_identity_conflict(d, name, now_year=None):
    """Positive evidence that a Wikipedia summary page is a DIFFERENT
    person than the (living, working) cast member being looked up.

    An exact page-title match is not identity proof: the page titled
    "Beatrice Campbell" is a Northern Irish actress who died in 1979,
    not the newcomer in an upcoming film. Reject ONLY on positive
    evidence — a living actor with an old photo, or a page whose data
    carries no dates at all, is left alone:

      * the bio date parentheticals give a birth–death year range
        ("British actress (1922–1979)") or a death note — the page's
        person is deceased, so cannot be in a current production
      * a recorded birth year makes the person implausibly old for a
        new production (>105 years)
      * the page's own thumbnail filename names a different person —
        applied only when the page carries NO "(born ...)" living
        marker: with one, a non-matching filename may be a character
        still of the same actor, which is not identity evidence

    Returns True on conflict, False otherwise (fall back to initials
    when in doubt is handled by the caller treating True as no-photo).
    """
    if not d or not isinstance(d, dict):
        return False
    if d.get("type") == "disambiguation":
        return False  # handled by the disambiguation path, not this one
    if now_year is None:
        now_year = datetime.now(timezone.utc).year
    has_born_marker = False
    for inner in _bio_date_parentheticals(d, name):
        years = re.findall(_YEAR_RE, inner)
        if len(years) >= 2 and re.search(r"[–—-]", inner):
            return True  # birth–death range: page person is deceased
        if re.search(r"\b(died|death|deceased)\b", inner, re.I):
            return True
        if years and re.search(r"\bborn\b", inner, re.I):
            has_born_marker = True
            if now_year - int(years[0]) > 105:
                return True  # implausibly old for a current production
    if has_born_marker:
        # The page is anchored to a specific LIVING person whose name
        # matches. A thumbnail filename that names no one matching may
        # be a character still OF that actor (Lewis Tan's page photo is
        # "Cole Young as depicted in Mortal Kombat II") — not evidence
        # of a different person, so the filename check does not apply.
        return False
    thumb = (d.get("thumbnail") or {}).get("source")
    orig = (d.get("originalimage") or {}).get("source")
    if _image_names_other_person(thumb or orig, name):
        return True
    return False


def _is_ambiguous(name):
    """True when the name could belong to several people.

    Single-token names (e.g. 'Mathew') and names whose Wikipedia page is
    a disambiguation page (e.g. 'Atul Kumar') both qualify — as do names
    whose exact-title Wikipedia page is provably a different person
    (_summary_identity_conflict): other people with that name exist, so
    Commons must not be trusted on a loose filename match either.
    """
    if len(name.split()) < 2:
        return True
    d = _wiki_summary(name)
    if not d or not isinstance(d, dict):
        return False
    if d.get("type") == "disambiguation":
        return True
    return _summary_identity_conflict(d, name)


def _wikipedia_lookup(name):
    d = _wiki_summary(name)
    if not d or not isinstance(d, dict):
        return None
    if d.get("type") == "disambiguation":
        return None
    # Exact-title match is NOT identity proof: reject when the page's own
    # data (death dates, implausible birth year, a thumbnail that names
    # someone else) shows it is a different person.
    if _summary_identity_conflict(d, name):
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


def _commons_lookup(name, ambiguous=False):
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
        if ambiguous:
            # Ambiguous name: filename must BE the name, nothing else.
            # "Atul_Kumar_MD" (ophthalmologist) and "Mathew_Brady_1875"
            # (19th-century photographer) are different people — the
            # extra tokens prove a wrong identity, so reject outright.
            if base != want:
                continue
        elif not base.startswith(want):
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
            or _commons_lookup(name, ambiguous=_is_ambiguous(name)))


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
