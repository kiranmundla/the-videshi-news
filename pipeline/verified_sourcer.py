#!/usr/bin/env python3
"""verified_sourcer.py — SHADOW hero path for the image rebuild
(design.md §2 Rungs 1–3, §3 evaluation protocol).

SHADOW ONLY. decide() computes what the new path WOULD serve for an
article's hero and appends the decision to
pipeline/.state/shadow-sourcing.jsonl. Nothing here is wired into
any producer; no live article, feed, or gate is affected.

Decision logic, in order (verified or nothing):

  1. Subjects — the article's headline subjects: the Rung 0 intent
     (image_entities, else the "Must show: …" line of
     image_must_show), else the picture pass's own extractor
     (extract_article_entities + headline_subject_names). Body-only
     mentions are never hero subjects. Extractor-derived subjects
     must additionally be ELIGIBLE (_subject_eligible): the
     extractor's sourceable contract, with a curated-registry
     exception — live replay showed headline common nouns
     ('Ordering', 'Profit', 'SEBI') otherwise manufacture
     identities for words. And a LIVE resolution counts only
     when the item it picked actually bears the queried name
     (identity_agrees) — sitelink primacy alone resolved the
     guitarist Adrian Abraham to a rugby player of a different
     name. inline_decide() applies the same guards to the
     subjects + named co-subjects it sources for inlines.
  2. Per subject, identity by construction only:
       resolver (entity_resolve.resolve) → Wikidata QID, then
       a. the item's P18, if it passes the quality screen;
       b. depicts_candidates(QID) — Commons files whose depicts
          (P180) statement IS this entity — best by width.
     Story-specific official/gov sourcing (design Rung 3) is NOT
     consulted in this shadow build: image_sourcer's official step
     validates og:image candidates with a topical metadata gate —
     the class of check this rebuild abolishes — and carries
     import-time env/network seams that don't belong in a shadow
     path. Rungs 1–2 are the measured backbone (design §1.4);
     Rung 3 integration is a separate, deliberate step.
  3. NOTHING comes from open metadata search. There is no search
     call in this module.
  3b. VENUE IDENTITY (acceptance gap, baps-acceptance.md case 1):
     identity routes verify the unit they resolve — and for an
     organization with local instances (a temple network, a chain)
     that unit is the ORG, while the story may be about one
     specific VENUE (the Dallas mandir's Diwali). An org-level
     depicts/P18 then presents an unidentified instance as the
     story's venue. So when _venue_context() classifies the story
     as venue-specific — primary subject is an org (registry type
     "org", or any type flagged has_local_instances) AND a city
     signal exists (a place/building co-subject among the
     subjects or headline names, or the headline's "<City> <Org>"
     / "<Org> <City>" / "in <City>" venue pattern) — candidates
     face a venue test on TOP of the quality screen:
       - a candidate serves UNLABELED only when its own evidence
         ties it to that venue: the file's Commons description or
         categories name the story's city, or the file depicts a
         co-subject venue/place item's QID (file_evidence);
       - otherwise the best org-level candidate may still serve,
         but ONLY as a labeled file photo: the decision carries
         label="file_photo", a label_text naming the org
         generically ("File photo: a BAPS mandir") and a caption
         that does not claim the story's venue. Downstream
         surfaces are REQUIRED to render the label;
       - with no candidate at all, decide "none" with reason
         "venue-unverified" — never fall through to another
         subject (a skyline of the city would be the same
         venue-blindness in another form).
     Non-venue-specific org stories are untouched: org depicts /
     P18 serve unlabeled, exactly as before.
  4. Fail closed (decision "none") when:
       - a candidate's canonical file key is on the entity's
         corpus blocklist (entity_resolve blocked_files);
       - the subject's resolution is ambiguous between confusables
         and context did not discriminate (abstention, per design —
         a guess between namesakes is how the corpus happened);
       - the subject resolves to a non-visual entity (a language —
         registry type "language"; the Hindi corpus cases);
       - the subject has no Wikidata identity anchor (QID null):
         identity routes cannot run, and nothing else may speak
         for a named subject;
       - every candidate fails the quality screen.

Quality screen (P18 and depicts alike):
  - not a logo/graphic: .svg files and files named as logos are
    not photos. An org whose P18 is a logo gets photo:none and
    falls through to depicts (design Rung 1; corpus generic-logo
    class — a logo captioned as a headquarters is a failure, not
    a fallback);
  - not on the entity's blocklist (canonical file key);
  - width: 1200 preferred. 800–1199 is accepted as a DOCUMENTED
    EXCEPTION (the reason string says so). Below 800 is rejected.
    Width unknown is rejected too (fail closed) unless a live
    imageinfo lookup (registry entries carry width in
    p18_quality; live resolutions fetch it) establishes it —
    and that lookup also verifies the license (CC0/PD/BY/BY-SA
    only, via entity_resolve's filter).

Resolver note: the default resolver is entity_resolve.resolve,
which adjudicates same-name pairs by context and caches successful
live resolutions back into the registry (that cache-back is the
resolver's own designed behaviour, Rungs 1–2). registry_only_
resolve() is provided for offline callers (corpus replay, tests)
and never touches the network or the registry file.

Returns from decide():
  {decision: "image"|"none", url, file_key, route, entity, reason,
   attempts: [...], label, label_text, caption}
route ∈ wikidata_p18 | wikidata_depicts | None. label is None for
an ordinary serve; label == "file_photo" (with label_text and
caption populated) for a labeled organization file photo under
the venue rule above.
"""

import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import entity_resolve as er
import image_ledger

WIDTH_PREFERRED = 1200
WIDTH_FLOOR = 800
PRODUCER = "verified_sourcer.shadow"


def shadow_path():
    env = os.environ.get("SHADOW_SOURCING_PATH")
    if env:
        return Path(env)
    return Path(HERE) / ".state" / "shadow-sourcing.jsonl"


# ── article subjects + context ───────────────────────────────────
def _strip_html(text):
    t = re.sub(r"<[^>]+>", " ", str(text or ""))
    return re.sub(r"\s+", " ", t).strip()


def article_context(article):
    """Context the resolver adjudicates namesakes against:
    headline + standfirst/summary + the top of the body."""
    parts = [article.get("headline") or "",
             article.get("summary") or article.get("standfirst") or "",
             _strip_html(article.get("body") or "")[:3000]]
    return " ".join(p for p in parts if p)


def headline_subjects(article):
    """Headline subjects in priority order: Rung 0 intent first
    (image_entities, then the image_must_show line the ledger
    writes), then the picture pass's extractor. [] when nothing
    can be stated — intent is never invented here."""
    if not isinstance(article, dict):
        return []
    ents = [str(e).strip() for e in (article.get("image_entities")
                                     or []) if str(e).strip()]
    if ents:
        return ents
    must = (article.get("image_must_show") or "").strip()
    if must.lower().startswith("must show:"):
        inner = must[len("must show:"):].split("(")[0]
        names = [s.strip() for s in inner.split(";") if s.strip()]
        if names:
            return names
    try:
        import article_picture_pass as APP
        entities = APP.extract_article_entities(article)
        subs = APP.headline_subject_names(article, entities)
        ordered = [e["name"] for e in entities
                   if e["name"].lower() in subs
                   and _subject_eligible(e)]
        if ordered:
            return ordered
    except Exception:
        pass
    return []


def _subject_eligible(entity):
    """May this extracted entity be SOURCED as a subject at all?
    The extractor's own contract: single tokens and fragments are
    recorded but never sourced — a lone capitalized token is not
    identity proof ('Mann', 'Host'). Live replay of the corpus
    (2026-10-31) showed why this matters here: fed to the
    resolver as subjects, headline common nouns manufactured
    confident identities for words, not stories — 'Ordering' →
    partial order (mathematics), 'Profit' → income tax, 'SEBI'
    → Serbia, 'Yulu' → fish sauce, 'President' → the US
    presidency on an Indian president's story. The one exception
    is a name the curated registry itself carries (exact
    name/alias match): curation IS an identity adjudication, so
    a registry single token ('Nifty') is a verified subject,
    while an unregistered one is a common noun the headline
    happens to capitalize."""
    if entity.get("sourceable"):
        return True
    try:
        return bool(er._candidates(entity["name"]))
    except Exception:
        return False


def identity_agrees(query, res):
    """Does a LIVE resolution actually bear the queried name?
    Sitelink primacy picks the most-linked item a name search
    returns; nothing in that guarantees the item IS the name —
    live replay resolved 'Adrian Abraham' (a 9-year-old
    guitarist) to Adrian Jacobs (a rugby player) and 'SEBI' to
    Serbia. The agreement standard itself is
    entity_resolve.names_agree (token-set equality against the
    label or an alias, plural-insensitive; generic type-word
    suffixes and honorific prefixes allowed) — ONE standard,
    shared with the resolver's cache-back guard, so a name this
    guard vetoes here can never become registry truth there.
    Registry resolutions are exempt: the registry matched the
    name/alias exactly, by construction."""
    if (res.get("method") or "").startswith("registry"):
        return True
    return er.names_agree(query, res.get("name"), res.get("aliases"))


# ── registry-only resolution (offline; mirrors er.resolve's
#    registry branch, including its ambiguity marker) ────────────
def registry_only_resolve(name, context_text=""):
    cands = er._candidates(name)
    if not cands:
        return None
    if len(cands) == 1:
        r = er._from_entry(cands[0], "registry",
                           "high" if cands[0].get("wikidata_qid")
                           else "low")
        r["query"] = name
        return r
    scored = sorted(cands,
                    key=lambda e: -er._hint_score(e, context_text))
    top = er._hint_score(scored[0], context_text)
    second = er._hint_score(scored[1], context_text)
    if top > second:
        r = er._from_entry(scored[0], "registry-context",
                           "high" if top >= 2 else "medium")
        r["query"] = name
        return r
    r = er._from_entry(scored[0], "registry", "low")
    r["query"] = name
    r["notes"] = ((r.get("notes") or "")
                  + " [ambiguous registry name; context did not "
                    "discriminate]").strip()
    return r


# ── quality screen ───────────────────────────────────────────────
def is_logo_or_graphic(file_name):
    """A logo, mark, map or other graphic is not a photo. .svg is
    a vector graphic by construction; 'logo' in the file name is
    the uploader's own label."""
    if not file_name:
        return True
    n = str(file_name).lower()
    if n.rsplit(".", 1)[-1] == "svg":
        return True
    return "logo" in re.split(r"[^a-z0-9]+", n)


def p18_info(file_name):
    """Live Commons imageinfo for a P18 file: width + license.
    One API call; None on any failure (callers fail closed)."""
    if not file_name:
        return None
    data = er._commons_api({
        "action": "query", "prop": "imageinfo",
        "iiprop": "size|extmetadata", "format": "json",
        "titles": "File:" + file_name,
    }) or {}
    for p in (data.get("query", {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii:
            continue
        em = ii.get("extmetadata") or {}
        return {
            "width": ii.get("width"),
            "license": (em.get("License") or {}).get("value", ""),
            "license_short": (em.get("LicenseShortName") or {})
                             .get("value", ""),
        }
    return None


def _width_verdict(width):
    """(ok, exception_note). 1200 preferred; 800 hard floor."""
    if width is None:
        return False, "width unverified"
    if width < WIDTH_FLOOR:
        return False, f"width {width} below {WIDTH_FLOOR} hard floor"
    if width < WIDTH_PREFERRED:
        return True, (f"width {width} below preferred "
                      f"{WIDTH_PREFERRED} — accepted under the "
                      f"documented >={WIDTH_FLOOR} exception")
    return True, f"width {width}"


def screen_candidate(file_ref, width, blocked_keys, license_pair=None):
    """The shared quality screen. Returns (ok, note). Fail closed
    on every uncertainty."""
    key = er.file_key(file_ref)
    if not key:
        return False, "no canonical file identity"
    if key in blocked_keys:
        return False, "on the entity's corpus blocklist"
    if is_logo_or_graphic(file_ref):
        return False, "logo/graphic, not a photo (photo: none)"
    if license_pair is not None:
        if not er._license_ok(license_pair[0], license_pair[1]):
            return False, "license not CC0/PD/BY/BY-SA (or unknown)"
    ok, note = _width_verdict(width)
    return ok, note


def file_url_for(file_name, width=1920):
    """Stable Commons URL for a file (Special:FilePath redirects
    to the canonical upload.wikimedia.org rendition)."""
    return ("https://commons.wikimedia.org/wiki/Special:FilePath/"
            + urllib.parse.quote(str(file_name).replace(" ", "_"))
            + f"?width={width}")


# ── candidate production for one resolved entity ─────────────────
def candidates_for(res, depicts_fn=None, info_fn=None):
    """(candidate, attempts) for one resolved entity. candidate is
    a decide()-shaped partial {url, file_key, route, reason} or
    None. Order: screened P18, then depicts best-by-width."""
    attempts = []
    name = res.get("name")
    blocked_keys = {er.file_key(b) for b in res.get("blocked_files")
                    or [] if er.file_key(b)}
    p18 = res.get("p18_file")
    if p18:
        width = res.get("p18_quality")
        width = width if isinstance(width, int) else None
        lic = None
        if width is None and info_fn is not None:
            info = info_fn(p18)
            if info:
                width = info.get("width")
                lic = (info.get("license"),
                       info.get("license_short"))
        ok, note = screen_candidate(p18, width, blocked_keys, lic)
        attempts.append({"entity": name, "route": "wikidata_p18",
                         "file": p18, "ok": ok, "note": note})
        if ok:
            return ({"url": file_url_for(p18),
                     "file_key": er.file_key(p18),
                     "route": "wikidata_p18",
                     "reason": f"P18 of {name} ({res.get('qid')}) "
                               f"via {res.get('method')}; {note}"},
                    attempts)
    else:
        attempts.append({"entity": name, "route": "wikidata_p18",
                         "file": None, "ok": False,
                         "note": "entity has no P18"})
    if depicts_fn is not None and res.get("qid"):
        try:
            cands = depicts_fn(res["qid"]) or []
        except Exception:
            cands = []
        screened = []
        for c in cands:
            ok, note = screen_candidate(
                c.get("title") or c.get("url"), c.get("width"),
                blocked_keys)
            if ok:
                screened.append((c, note))
        attempts.append({"entity": name, "route": "wikidata_depicts",
                         "count": len(cands),
                         "passed": len(screened),
                         "note": "depicts(P180) candidates screened"})
        if screened:
            screened.sort(key=lambda cn: (
                1 if (cn[0].get("width") or 0) >= WIDTH_PREFERRED
                else 0, cn[0].get("width") or 0), reverse=True)
            best, note = screened[0]
            return ({"url": best.get("url"),
                     "file_key": best.get("file_key")
                     or er.file_key(best.get("title")),
                     "route": "wikidata_depicts",
                     "reason": f"depicts(P180={res.get('qid')}) file "
                               f"for {name}; {note}; license "
                               f"{best.get('license')}"},
                    attempts)
    return None, attempts


# ── venue identity (org-level identity vs venue-specific story) ─
# Local-instance nouns: the physical unit an org-with-instances
# story is usually about. Presence in the headline (with a city
# signal) is what turns an org story into a venue story.
VENUE_WORDS = {
    "mandir", "temple", "church", "mosque", "masjid", "gurdwara",
    "gurudwara", "synagogue", "cathedral", "chapel", "monastery",
    "ashram", "campus", "branch", "store", "outlet", "showroom",
    "dealership", "restaurant", "clinic", "hospital", "school",
    "library", "center", "centre",
}
_HEADLINE_RUN_STOP = {
    "the", "a", "an", "for", "in", "on", "at", "of", "to", "and",
    "vs", "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november",
    "december", "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
}


def file_evidence(file_ref):
    """What a Commons file ITSELF says it is: its description
    text, its category names, and its own depicts (P180) target
    QIDs — the venue test's evidence. One or two Commons API
    calls; {} on any failure (callers treat no evidence as
    not-venue-tied: fail closed)."""
    if not file_ref:
        return {}
    title = str(file_ref)
    if title.lower().startswith(("http://", "https://")):
        title = title.rsplit("/", 1)[-1]
    if not title.lower().startswith("file:"):
        title = "File:" + title.replace("_", " ")
    data = er._commons_api({
        "action": "query", "format": "json",
        "prop": "imageinfo|categories", "iiprop": "extmetadata",
        "cllimit": "500", "titles": title,
    }) or {}
    for pid, p in (data.get("query", {}).get("pages") or {}).items():
        ii = (p.get("imageinfo") or [{}])[0]
        em = (ii or {}).get("extmetadata") or {}
        desc = _strip_html((em.get("ImageDescription") or {})
                           .get("value", ""))
        cats = []
        for c in p.get("categories") or []:
            t = (c.get("title") or "").split(":", 1)[-1].strip()
            if t:
                cats.append(t)
        qids = []
        if str(pid).isdigit():
            mi = er._commons_api({
                "action": "wbgetentities", "format": "json",
                "ids": f"M{pid}", "props": "claims",
            }) or {}
            ent = (mi.get("entities") or {}).get(f"M{pid}") or {}
            for c in ((ent.get("claims") or {}).get("P180") or []):
                try:
                    qids.append(
                        c["mainsnak"]["datavalue"]["value"]["id"])
                except Exception:
                    pass
        return {"description": desc, "categories": cats,
                "depicts_qids": qids}
    return {}


def _venue_word_in(text):
    for tok in re.findall(r"[a-z]+", (text or "").lower()):
        if tok in VENUE_WORDS:
            return tok
    return None


def _headline_venue_pattern(headline, primary_name, res):
    """The headline's own venue naming: "<City> <Org> <venue…>"
    ("Dallas BAPS Mandir …"), "<Org> <City> <venue…>", or "… in
    <City>" — returns (city, venue_word), city None when the
    headline carries no such pattern. A venue word must be
    present: a bare leading capitalized token ("Diwali BAPS …")
    is not a city-named venue."""
    venue_word = _venue_word_in(headline)
    if not headline or not venue_word:
        return None, venue_word
    org_names = [primary_name, res.get("name")] + list(
        res.get("aliases") or [])
    variants = []
    for nm in org_names:
        if nm:
            variants.append(re.findall(r"[a-z0-9]+", nm.lower()))
    org_toks = {t for v in variants for t in v}
    words = [w.strip(" ,;:\"'()") for w in headline.split()]
    words = [w for w in words if w]
    lower = [w.lower() for w in words]
    start = end = None
    for i in range(len(lower)):
        for v in variants:
            if v and lower[i:i + len(v)] == v:
                start, end = i, i + len(v)
                break
        if start is not None:
            break
    if start is None:
        return None, venue_word

    def cap_run(idxs):
        run = []
        for j in idxs:
            w = words[j]
            if not w[0].isupper() or w.lower() in org_toks \
                    or w.lower() in _HEADLINE_RUN_STOP:
                break
            run.append(w)
        return run

    pre = cap_run(range(start - 1, -1, -1))
    if pre:
        return " ".join(reversed(pre)), venue_word
    post = cap_run(range(end, len(words)))
    if post:
        nxt = end + len(post)
        if nxt < len(words) and lower[nxt] == venue_word:
            return " ".join(post), venue_word
    m = re.search(r"\bin ([A-Z][A-Za-z'.-]*(?: [A-Z][A-Za-z'.-]*)?)\b",
                  headline)
    if m and m.group(1).lower() not in org_toks:
        return m.group(1), venue_word
    return None, venue_word


def _classify(name, context, resolver):
    """Resolve a headline name ONLY to learn its type — never to
    source from it, and NEVER through the caching resolver: the
    default resolver (entity_resolve.resolve) writes live winners
    back into the registry, and a classification lookup must not
    mint subject-grade registry truth. (Live BAPS run, 2026-10-31:
    classification resolved 'Dallas' to Dallas, North Carolina —
    a namesake town — and 'Mandir' to the Hindu-temple concept,
    and resolve() cached both, which then made a NC town an
    ELIGIBLE headline subject. The poisoning guard in
    entity_resolve cannot catch this: the cached items DO bear
    the queried names; they are simply the wrong namesakes, and
    classification never adjudicated them as subjects.)
    Default resolver → registry-only first, then the resolver's
    own non-caching live path. Any other resolver (test stubs,
    registry_only_resolve) is used as passed."""
    if resolver is er.resolve:
        r = registry_only_resolve(name, context)
        if r is not None:
            return r
        try:
            return er._resolve_live(name, context)
        except Exception:
            return None
    return resolver(name, context)


def _venue_context(article, subjects, primary_name, primary_res,
                   resolver, context):
    """Classify the story as venue-specific. Returns
    {cities, city, qids, venue_word} or None.

    Venue-capable primary: registry type "org" (temple networks,
    charities, church bodies — organizations whose stories are
    usually about one local instance) or any resolution flagged
    has_local_instances (the registry schema's explicit signal,
    e.g. a retail chain's curated entry). City signal, any of:
      - another subject, or another extractor headline name,
        classifies (via _classify — no registry writes) as a
        place or building and bears its name;
      - the headline names the venue by city (pattern above).
    The venue word (mandir/temple/…) comes from the headline."""
    if not (primary_res.get("type") == "org"
            or primary_res.get("has_local_instances")):
        return None
    headline = article.get("headline") or ""
    cities, qids = [], set()
    names = [s for s in subjects if s != primary_name]
    try:
        import article_picture_pass as APP
        entities = APP.extract_article_entities(article)
        subs = APP.headline_subject_names(article, entities)
        for e in entities:
            nm = e["name"]
            if (nm.lower() in subs and nm != primary_name
                    and nm not in names):
                names.append(nm)
    except Exception:
        pass
    for nm in names:
        try:
            r2 = _classify(nm, context, resolver)
        except Exception:
            continue
        if not r2 or r2.get("type") not in ("place", "building"):
            continue
        if not identity_agrees(nm, r2):
            continue
        disp = r2.get("name") or nm
        if disp not in cities:
            cities.append(disp)
        if r2.get("qid"):
            qids.add(r2["qid"])
    pat_city, venue_word = _headline_venue_pattern(
        headline, primary_name, primary_res)
    if pat_city and pat_city not in cities:
        cities.insert(0, pat_city)
    if not cities:
        return None
    return {"cities": cities, "city": cities[0], "qids": qids,
            "venue_word": venue_word or _venue_word_in(headline)}


def _all_candidates(res, depicts_fn=None, info_fn=None):
    """(candidates, attempts): EVERY candidate that passes the
    quality screen for one entity, best first — the screened P18,
    then depicts in candidates_for's preference order (preferred
    width first, then widest). candidates_for() picks [0] of an
    equivalent list for the ordinary path; the venue path needs
    the whole list because a later candidate may be the
    venue-tied one. Each candidate additionally carries "file"
    (source file name / Commons title) for evidence lookups."""
    attempts = []
    name = res.get("name")
    blocked_keys = {er.file_key(b) for b in res.get("blocked_files")
                    or [] if er.file_key(b)}
    out = []
    p18 = res.get("p18_file")
    if p18:
        width = res.get("p18_quality")
        width = width if isinstance(width, int) else None
        lic = None
        if width is None and info_fn is not None:
            info = info_fn(p18)
            if info:
                width = info.get("width")
                lic = (info.get("license"),
                       info.get("license_short"))
        ok, note = screen_candidate(p18, width, blocked_keys, lic)
        attempts.append({"entity": name, "route": "wikidata_p18",
                         "file": p18, "ok": ok, "note": note})
        if ok:
            out.append({"url": file_url_for(p18),
                        "file_key": er.file_key(p18),
                        "route": "wikidata_p18", "file": p18,
                        "reason": f"P18 of {name} ({res.get('qid')}) "
                                  f"via {res.get('method')}; {note}"})
    else:
        attempts.append({"entity": name, "route": "wikidata_p18",
                         "file": None, "ok": False,
                         "note": "entity has no P18"})
    if depicts_fn is not None and res.get("qid"):
        try:
            cands = depicts_fn(res["qid"]) or []
        except Exception:
            cands = []
        screened = []
        for c in cands:
            ok, note = screen_candidate(
                c.get("title") or c.get("url"), c.get("width"),
                blocked_keys)
            if ok:
                screened.append((c, note))
        attempts.append({"entity": name, "route": "wikidata_depicts",
                         "count": len(cands),
                         "passed": len(screened),
                         "note": "depicts(P180) candidates screened"})
        screened.sort(key=lambda cn: (
            1 if (cn[0].get("width") or 0) >= WIDTH_PREFERRED
            else 0, cn[0].get("width") or 0), reverse=True)
        for c, note in screened:
            out.append({"url": c.get("url"),
                        "file_key": c.get("file_key")
                        or er.file_key(c.get("title")),
                        "route": "wikidata_depicts",
                        "file": c.get("title"),
                        "reason": f"depicts(P180={res.get('qid')}) "
                                  f"file for {name}; {note}; "
                                  f"license {c.get('license')}"})
    return out, attempts


def _venue_tied(ev, venue):
    """Does the file's own evidence tie it to the story's venue?
    Either it depicts a co-subject venue/place item (its QID is
    in the venue context), or its Commons description/categories
    name the story's city. The candidate pool is already bound
    to the org (P18 / depicts of the org QID), so a city name in
    the file's own record is the venue signal. Anything less —
    no evidence, another city's name — is NOT tied."""
    if not ev:
        return False
    if set(ev.get("depicts_qids") or []) & (venue.get("qids")
                                            or set()):
        return True
    hay = " ".join([ev.get("description") or ""]
                   + list(ev.get("categories") or []))
    for city in venue.get("cities") or []:
        if city and re.search(r"(?<![A-Za-z])" + re.escape(city)
                              + r"(?![A-Za-z])", hay, re.IGNORECASE):
            return True
    return False


def _file_photo_label(ent_name, venue):
    """(label_text, caption) for a labeled org file photo: names
    the organization generically ("File photo: a BAPS mandir")
    and explicitly does NOT claim the story's venue."""
    vw = venue.get("venue_word")
    label_text = (f"File photo: a {ent_name} {vw}" if vw
                  else f"File photo: {ent_name}")
    caption = (f"{label_text} — not the {venue['city']} venue "
               f"in this story.")
    return label_text, caption


def _apply_venue_decision(result, res, ent_name, venue, depicts_fn,
                          info_fn, evidence_fn):
    """Finalize result for a venue-specific story about an org.
    Venue-tied candidate → unlabeled serve. Otherwise the best
    org-level candidate serves ONLY as a labeled file photo.
    No candidate at all → none, reason "venue-unverified".
    Mutates result; always final (decide returns it as-is)."""
    result["entity"] = ent_name
    cands, atts = _all_candidates(res, depicts_fn, info_fn)
    result["attempts"].extend(atts)
    city = venue["city"]
    if not cands:
        result["decision"] = "none"
        result["reason"] = (
            f"venue-unverified: venue-specific story ({ent_name} "
            f"in {city}) — no candidate image exists at all, so "
            f"neither a venue-tied photo nor a labeled org file "
            f"photo can be served")
        return
    for cand in cands:
        ev = {}
        if evidence_fn is not None:
            try:
                ev = evidence_fn(cand.get("file")
                                 or cand.get("file_key")) or {}
            except Exception:
                ev = {}
        tied = _venue_tied(ev, venue)
        result["attempts"].append({
            "entity": ent_name, "route": cand["route"],
            "file": cand["file_key"], "venue_tied": tied,
            "note": "venue evidence: the file's own Commons "
                    "description/categories/depicts"})
        if tied:
            result.update({
                "decision": "image", "url": cand["url"],
                "file_key": cand["file_key"], "route": cand["route"],
                "reason": cand["reason"] + f"; venue-tied: the "
                          f"file's own evidence names {city}, the "
                          f"story's venue city"})
            return
    cand = cands[0]
    label_text, caption = _file_photo_label(ent_name, venue)
    result.update({
        "decision": "image", "url": cand["url"],
        "file_key": cand["file_key"], "route": cand["route"],
        "label": "file_photo", "label_text": label_text,
        "caption": caption,
        "reason": cand["reason"] + f"; venue-specific story "
                  f"({city}) and no candidate is tied to that "
                  f"venue — org-level image served ONLY as a "
                  f"labeled file photo"})


# ── shadow ledger ────────────────────────────────────────────────
def _write_shadow(result, slug, path=None, surface="hero"):
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "producer": PRODUCER,
        "slug": slug,
        "surface": surface,
        "decision": result["decision"],
        "route": result["route"],
        "entity": result["entity"],
        "file_key": result["file_key"],
        "url": result["url"],
        "reason": result["reason"],
        "label": result.get("label"),
        "label_text": result.get("label_text"),
        "caption": result.get("caption"),
    }
    p = Path(path) if path else shadow_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(rec, ensure_ascii=False)
        try:
            import fcntl
            with open(p, "a", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(line + "\n")
                fcntl.flock(f, fcntl.LOCK_UN)
        except ImportError:
            with open(p, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception:
        pass  # a shadow-log failure must never break a caller
    return rec


# ── the decision ─────────────────────────────────────────────────
_UNSET = object()


def decide(article, resolver=None, depicts_fn=None, info_fn=_UNSET,
           evidence_fn=_UNSET, write_log=True, log_path=None):
    """What the new path would serve as this article's hero.
    Shadow only — see module docstring. info_fn=None explicitly
    means NO live width/license lookup (offline callers: unknown
    widths fail the screen closed). evidence_fn=None explicitly
    means NO live venue-evidence lookup (venue-specific stories
    then fail toward the labeled file photo, never toward an
    unlabeled serve)."""
    resolver = resolver or er.resolve
    if depicts_fn is None:
        depicts_fn = er.depicts_candidates
    if info_fn is _UNSET:
        info_fn = p18_info
    if evidence_fn is _UNSET:
        evidence_fn = file_evidence
    slug = article.get("slug") if isinstance(article, dict) else None
    result = {"decision": "none", "url": None, "file_key": None,
              "route": None, "entity": None, "reason": "",
              "attempts": [], "label": None, "label_text": None,
              "caption": None}

    def finish(reason):
        result["reason"] = reason
        if write_log:
            _write_shadow(result, slug, log_path)
        return result

    subjects = headline_subjects(article)
    if not subjects:
        return finish("no headline subject identified (no "
                      "image_entities intent; extractor found no "
                      "headline subject) — fail closed")
    context = article_context(article)
    notes = []
    for idx, name in enumerate(subjects):
        try:
            res = resolver(name, context)
        except Exception as e:
            result["attempts"].append(
                {"entity": name, "outcome": f"resolver error: {e}"})
            continue
        if not res:
            notes.append(f"{name}: unresolved (no registry entry, "
                         f"no Wikidata identity)")
            result["attempts"].append(
                {"entity": name, "outcome": "unresolved"})
            continue
        if not identity_agrees(name, res):
            notes.append(f"{name}: live resolution named "
                         f"'{res.get('name')}' — the item does "
                         f"not bear the queried name; not an "
                         f"identity")
            result["attempts"].append(
                {"entity": name, "outcome": "name-mismatch",
                 "resolved_name": res.get("name"),
                 "qid": res.get("qid")})
            continue
        ent_name = res.get("name") or name
        if (res.get("confidence") == "low"
                and "ambiguous" in (res.get("notes") or "")):
            notes.append(f"{ent_name}: ambiguous between "
                         f"confusables; context did not "
                         f"discriminate — abstaining")
            result["attempts"].append(
                {"entity": ent_name, "outcome": "ambiguous"})
            if idx == 0:
                result["entity"] = ent_name
                return finish(
                    f"primary subject '{name}' is ambiguous "
                    f"between confusables "
                    f"({', '.join(res.get('confusables') or [])}) "
                    f"with no discriminating context — abstain "
                    f"(fail closed)")
            continue
        if res.get("type") == "language":
            notes.append(f"{ent_name}: non-visual entity "
                         f"(language) — never pictured")
            result["attempts"].append(
                {"entity": ent_name, "outcome": "non-visual"})
            continue
        if not res.get("qid"):
            notes.append(f"{ent_name}: no Wikidata identity "
                         f"anchor (QID null) — identity routes "
                         f"unavailable for a named subject")
            result["attempts"].append(
                {"entity": ent_name, "outcome": "no-qid"})
            continue
        if idx == 0:
            venue = _venue_context(article, subjects, name, res,
                                   resolver, context)
            if venue is not None:
                _apply_venue_decision(result, res, ent_name, venue,
                                      depicts_fn, info_fn,
                                      evidence_fn)
                if write_log:
                    _write_shadow(result, slug, log_path)
                return result
        cand, atts = candidates_for(res, depicts_fn, info_fn)
        result["attempts"].extend(atts)
        if cand:
            result.update({"decision": "image", "url": cand["url"],
                           "file_key": cand["file_key"],
                           "route": cand["route"],
                           "entity": ent_name,
                           "reason": cand["reason"]})
            if write_log:
                _write_shadow(result, slug, log_path)
            return result
        notes.append(f"{ent_name}: no candidate passed the "
                     f"screen (see attempts)")
    result["entity"] = subjects[0]
    return finish("no verified candidate — " + "; ".join(notes))


# ── the inline decision (shadow) ─────────────────────────────────
MAX_INLINES = 3


def _inline_roles(article):
    """Ordered [(name, role)] for inline sourcing: headline
    subjects first (headline_subjects — the hero set, same
    eligibility rules), then named co-subjects (the picture
    pass's subject_and_cosubject_names: lede-named, sourceable,
    not quoted sources). Mentioned-only entities are absent by
    construction — the open-search inline route that produced
    73 of the 123 corpus failures is not replaced by a wider
    net; it is replaced by this list."""
    roles = []
    seen = set()
    try:
        import article_picture_pass as APP
        entities = APP.extract_article_entities(article)
        _, co = APP.subject_and_cosubject_names(article, entities)
    except Exception:
        entities, co = [], set()
    for name in headline_subjects(article):
        if name.lower() not in seen:
            seen.add(name.lower())
            roles.append((name, "subject"))
    for e in entities:
        nm = e["name"].lower()
        if nm in co and nm not in seen:
            seen.add(nm)
            roles.append((e["name"], "co-subject"))
    return roles


def inline_decide(article, resolver=None, depicts_fn=None,
                  info_fn=_UNSET, evidence_fn=_UNSET,
                  write_log=True, log_path=None,
                  hero=None):
    """What the new path would place as this article's INLINES.
    Shadow only — see module docstring.

    Subjects + named co-subjects only; each entity sourced
    per-entity via P18/depicts through the resolver (the same
    identity routes and quality screen as the hero), at most
    MAX_INLINES, deduped against the hero decision and against
    each other by canonical file key — the same file can never
    be placed twice on one article. Per-entity failures skip
    that entity (no abstention cascade: one unresolvable
    co-subject must not starve the others). Logs one shadow
    record per placed inline (surface="inline"), plus a single
    decision="none" record when nothing is placed, so shadow
    analysis can count zero-inline articles.

    hero: an optional decide() result for the same article; when
    absent it is computed here (without its own shadow record —
    inline_decide logs only inline records)."""
    resolver = resolver or er.resolve
    if depicts_fn is None:
        depicts_fn = er.depicts_candidates
    if info_fn is _UNSET:
        info_fn = p18_info
    if evidence_fn is _UNSET:
        evidence_fn = file_evidence
    slug = article.get("slug") if isinstance(article, dict) else None
    if hero is None:
        hero = decide(article, resolver=resolver,
                      depicts_fn=depicts_fn, info_fn=info_fn,
                      evidence_fn=evidence_fn,
                      write_log=False)
    used_keys = set()
    if hero.get("file_key"):
        used_keys.add(hero["file_key"])
    context = article_context(article)
    placed, attempts = [], []
    for name, role in _inline_roles(article):
        if len(placed) >= MAX_INLINES:
            attempts.append({"entity": name, "role": role,
                             "outcome": "skipped: inline cap"})
            continue
        try:
            res = resolver(name, context)
        except Exception as e:
            attempts.append({"entity": name, "role": role,
                             "outcome": f"resolver error: {e}"})
            continue
        if not res:
            attempts.append({"entity": name, "role": role,
                             "outcome": "unresolved"})
            continue
        if not identity_agrees(name, res):
            attempts.append({"entity": name, "role": role,
                             "outcome": "name-mismatch",
                             "resolved_name": res.get("name"),
                             "qid": res.get("qid")})
            continue
        ent_name = res.get("name") or name
        if (res.get("confidence") == "low"
                and "ambiguous" in (res.get("notes") or "")):
            attempts.append({"entity": ent_name, "role": role,
                             "outcome": "ambiguous"})
            continue
        if res.get("type") == "language":
            attempts.append({"entity": ent_name, "role": role,
                             "outcome": "non-visual"})
            continue
        if not res.get("qid"):
            attempts.append({"entity": ent_name, "role": role,
                             "outcome": "no-qid"})
            continue
        cand, atts = candidates_for(res, depicts_fn, info_fn)
        attempts.extend(atts)
        if not cand:
            attempts.append({"entity": ent_name, "role": role,
                             "outcome": "no candidate passed screen"})
            continue
        if cand["file_key"] in used_keys:
            attempts.append({"entity": ent_name, "role": role,
                             "outcome": "duplicate of hero/earlier "
                                        "inline (canonical file key)",
                             "file": cand["file_key"]})
            continue
        used_keys.add(cand["file_key"])
        placed.append({"entity": ent_name, "role": role,
                       "url": cand["url"],
                       "file_key": cand["file_key"],
                       "route": cand["route"],
                       "reason": cand["reason"]})
    result = {"decision": "image" if placed else "none",
              "inlines": placed,
              "hero_file_key": hero.get("file_key"),
              "hero_entity": hero.get("entity"),
              "attempts": attempts}
    if write_log:
        if placed:
            for p in placed:
                _write_shadow(
                    {"decision": "image", "route": p["route"],
                     "entity": p["entity"], "file_key": p["file_key"],
                     "url": p["url"],
                     "reason": f"inline ({p['role']}): {p['reason']}"},
                    slug, log_path, surface="inline")
        else:
            _write_shadow(
                {"decision": "none", "route": None, "entity": None,
                 "file_key": None, "url": None,
                 "reason": "no subject/co-subject produced a "
                           "verified inline candidate"},
                slug, log_path, surface="inline")
    return result


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser(
        description="Shadow hero decision for one article JSON "
                    "(image rebuild, Rungs 1-3). No live effect.")
    ap.add_argument("--article-json", required=True,
                    help="path to a JSON file holding one article "
                         "dict (headline, slug, body, "
                         "image_entities, …)")
    ap.add_argument("--offline", action="store_true",
                    help="registry-only resolution, no network")
    args = ap.parse_args(argv)
    with open(args.article_json) as f:
        article = json.load(f)
    kw = {}
    if args.offline:
        kw = {"resolver": registry_only_resolve,
              "depicts_fn": lambda qid: [], "info_fn": None}
    print(json.dumps(decide(article, **kw), indent=1,
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
