#!/usr/bin/env python3
"""Entity resolution service — image rebuild Rungs 1–2 (design.md §2).

Identity by construction: a name resolves to a Wikidata item whose
identity is adjudicated, never to a search result whose text merely
matches. Two paths:

  1. REGISTRY (pipeline/entity_registry.json) — the measured entity
     set with hand-verified corrections, confusables and a blocklist
     of known-wrong files seeded from the failure corpus. Same-name
     pairs (the two Mandeep Singhs, the two Shahbaz Ahmeds…) are
     adjudicated by the article's context via per-entry context_hints.

  2. LIVE WIKIDATA — wbsearchentities, then adjudication over ALL
     hits by SITELINK PRIMACY (never label-exact rank: label search
     returns a French wholesaler for Infosys and ORCID stubs for
     Mandeep Singh), with type/context agreement (description + P31
     labels vs the article context) able to override when it
     discriminates and the sitelink gap is not overwhelming.
     Successful live resolutions cache back into the registry —
     but ONLY when the winner bears the queried name (the
     names_agree standard, shared with verified_sourcer's
     identity guard): an unguarded cache-back once wrote a
     vetoed namesake into the registry, where registry-method
     results are exempt from the guard — poisoning by design
     accident (corpus-replay-live.json residual risk #1).

Also: depicts_candidates(qid) — Commons files carrying a depicts
(P180) statement for the item, license read from extmetadata with
NC/ND rejected programmatically; and the corpus blocklist lookup.

Stdlib only; network via curl subprocess (urllib/requests do not pass
this box's proxy — AGENTS.md). This module changes NO live sourcing
behaviour; it is a library for the rebuild's shadow path.

Result dict from resolve():
  {query, name, qid, p18_file, p18_quality, type, method, confidence,
   confusables, blocked_files, ...}
method ∈ registry | registry-context | wikidata-sitelinks |
wikidata-context. qid None = no verified identity anchor exists —
callers must treat that as "no image from identity routes".
"""
import json
import os
import re
import subprocess
import tempfile
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "entity_registry.json")
UA = ("TheVideshiEntityResolver/1.0 "
      "(news image verification; contact editor@thevideshi.com)")
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

_CTX_STOP = {"the", "and", "for", "with", "from", "article", "story",
             "news", "says", "said", "will", "after", "over", "into",
             "that", "this", "than", "more", "has", "have", "been"}


# ── canonical file identity ──────────────────────────────────────
# Identical algorithm to article_picture_pass._wikimedia_file_key /
# image_ledger.file_key_for (the IOB fix, commit 72b6f805d): identity
# comparisons use this key, never raw URL strings.
def file_key(text):
    if not text:
        return None
    t = urllib.parse.unquote(str(text))
    t = t.split("?")[0].split("#")[0].strip()
    if "/" in t:
        t = t.rsplit("/", 1)[-1]
    t = re.sub(r"^\d+px-", "", t)  # thumb rendition prefix
    t = re.sub(r"^file:", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t.replace("_", " ")).strip().lower()
    if "." not in t:
        return None
    return t


# ── registry ─────────────────────────────────────────────────────
_registry_cache = None


def load_registry(path=None):
    global _registry_cache
    if path is None and _registry_cache is not None:
        return _registry_cache
    with open(path or REGISTRY_PATH) as f:
        reg = json.load(f)
    if path is None:
        _registry_cache = reg
    return reg


def _norm(name):
    t = re.sub(r"[^\w\s]", " ", str(name or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def _candidates(name, reg=None):
    reg = reg or load_registry()
    q = _norm(name)
    out = []
    for ent in reg.get("entities", []):
        names = [ent.get("name")] + list(ent.get("aliases") or [])
        if any(_norm(n) == q for n in names if n):
            out.append(ent)
    return out


def _hint_score(entry, context_text):
    ctx = " " + re.sub(r"\s+", " ", (context_text or "").lower()) + " "
    score = 0
    for hint in entry.get("context_hints") or []:
        if " " + hint.lower() + " " in ctx or hint.lower() in ctx:
            score += 1
    return score


def _from_entry(entry, method, confidence):
    return {
        "query": None,
        "name": entry.get("name"),
        "aliases": list(entry.get("aliases") or []),
        "qid": entry.get("wikidata_qid"),
        "p18_file": entry.get("p18_file"),
        "p18_quality": entry.get("p18_quality"),
        "type": entry.get("type"),
        "has_local_instances": bool(entry.get("has_local_instances")),
        "method": method,
        "confidence": confidence,
        "confusables": [c.get("name") for c in entry.get("confusables") or []],
        "blocked_files": list(entry.get("blocked_files") or []),
        "no_wikidata_identity": bool(entry.get("no_wikidata_identity")),
        "notes": entry.get("notes") or "",
    }


# ── blocklist ────────────────────────────────────────────────────
def entry_blocks(entry, file_ref):
    """True when file_ref (any surface form: File: title, original
    URL, thumb URL) is on this entry's corpus blocklist."""
    key = file_key(file_ref)
    if not key:
        return False
    return key in {file_key(b) for b in entry.get("blocked_files") or []}


def blocked_file(entity_name, file_ref):
    """Blocklist lookup by entity name/alias across registry entries."""
    return any(entry_blocks(e, file_ref) for e in _candidates(entity_name))


# ── network (single seams, monkeypatchable in tests) ─────────────
def _curl_json(url):
    try:
        out = subprocess.run(
            ["curl", "-s", "-m", "30", "-A", UA, url],
            capture_output=True, text=True, timeout=40)
        return json.loads(out.stdout)
    except Exception:
        return None


def _wikidata_api(params):
    qs = urllib.parse.urlencode(params)
    return _curl_json(f"{WIKIDATA_API}?{qs}")


def _commons_api(params):
    qs = urllib.parse.urlencode(params)
    return _curl_json(f"{COMMONS_API}?{qs}")


# ── live Wikidata adjudication ───────────────────────────────────
def _context_tokens(context_text, query_name):
    """Discriminating context tokens: content words in the context
    that are NOT part of the query name itself (the name's own words
    match every candidate's label and discriminate nothing)."""
    name_tokens = set(re.findall(r"[a-z0-9]+", (query_name or "").lower()))
    toks = set()
    for t in re.findall(r"[a-z0-9]+", (context_text or "").lower()):
        if len(t) >= 4 and t not in _CTX_STOP and t not in name_tokens:
            toks.add(t)
    return toks


def _hit_context_score(hit, ctx_tokens):
    hay = " ".join([
        hit.get("label") or "",
        hit.get("description") or "",
        " ".join(hit.get("aliases") or []),
        " ".join(hit.get("p31_labels") or []),
    ]).lower()
    return sum(1 for t in ctx_tokens if t in hay)


def _adjudicate(hits, context_text, query_name):
    """Pick the intended item from wbsearchentities hits enriched
    with sitelink counts. Returns (winner, method, confidence).

    Sitelink primacy is the default — label rank is meaningless
    (ORCID stubs and namesakes outrank real subjects). Context
    agreement overrides only when it uniquely discriminates AND the
    winner's sitelinks are not negligible vs the field (≥10% of the
    top count, ≥2 absolute): that is the Supreme-Court-of-India case
    (47 sitelinks + 'India' context vs a generic concept with more).
    """
    live = [h for h in hits if not h.get("is_disambiguation")]
    if not live:
        return None, None, None
    ctx_tokens = _context_tokens(context_text, query_name)
    for h in live:
        h["context_score"] = _hit_context_score(h, ctx_tokens)
    top_sl = max(h.get("sitelinks", 0) for h in live)
    by_sl = sorted(live, key=lambda h: -h.get("sitelinks", 0))
    ctx_best = max(h["context_score"] for h in live)
    ctx_winners = [h for h in live if h["context_score"] == ctx_best]
    if (ctx_best >= 1 and len(ctx_winners) == 1
            and ctx_winners[0].get("sitelinks", 0) >= max(2, 0.1 * top_sl)
            and ctx_winners[0] is not by_sl[0]):
        winner, method = ctx_winners[0], "wikidata-context"
    else:
        winner, method = by_sl[0], "wikidata-sitelinks"
    runner = by_sl[1].get("sitelinks", 0) if len(by_sl) > 1 else 0
    wsl = winner.get("sitelinks", 0)
    if method == "wikidata-context" and winner["context_score"] >= 2:
        confidence = "high"
    elif wsl >= 25 and (runner == 0 or wsl >= 3 * runner):
        confidence = "high"
    elif wsl >= 5:
        confidence = "medium"
    else:
        confidence = "low"
    return winner, method, confidence


# ── name agreement (the identity standard) ───────────────────────
# ONE standard, two enforcement points: verified_sourcer's
# identity guard applies it at decision time, and _cache_back
# applies it before a live resolution may become registry truth.
# (The logic lived in verified_sourcer first; it moved here so
# the resolver — the module that writes the registry — can
# enforce it without a circular import. verified_sourcer now
# delegates.)
_TYPE_TOKENS = {"party", "city", "state", "district", "county",
                "university", "bank", "group", "company", "inc",
                "ltd", "river", "island", "airport", "national",
                "of", "the", "and"}
_TITLE_TOKENS = {"justice", "judge", "dr", "mr", "mrs", "ms",
                 "shri", "sri", "prof", "professor"}


def _name_tokens(name):
    toks = set()
    for t in re.findall(r"[a-z0-9]+", (name or "").lower()):
        if t.isdigit():
            continue
        if len(t) > 3 and t.endswith("s"):
            t = t[:-1]
        toks.add(t)
    return toks


def _numerals(name):
    return set(re.findall(r"\d+", str(name or "")))


def names_agree(query, resolved_name, aliases=None):
    """Does the resolved item actually BEAR the queried name?
    Sitelink primacy picks the most-linked item a name search
    returns; nothing in that guarantees the item IS the name —
    live replay resolved 'Adrian Abraham' (a 9-year-old
    guitarist) to Adrian Jacobs (a rugby player) and 'SEBI' to
    Serbia. Agreement = token-set equality (plural-insensitive,
    numerals ignored) against the item's label OR any of its
    aliases (an item bearing the queried name as an alias bears
    the name — SEBI is the alias of 'Securities and Exchange
    Board of India'), or the label adds only generic type words
    ('Republican' → 'Republican Party'), or the query adds only
    an honorific ('Justice Vikram Nath' → 'Vikram Nath').

    NUMERAL MISMATCH VETO (2026-10-31, the reel-sourcer fix's
    live dry-run): numerals are ignored for token equality,
    but when BOTH names carry numerals and they DIFFER, the
    names cannot agree — 'Jailer 2' (Nelson Dilipkumar's film)
    resolved by sitelink primacy to 'Jailer 3' (a different
    film, by Atlee) and the digit-stripping token comparison
    waved it through into the registry. A sequel number is
    part of the name."""
    q = _name_tokens(query)
    if not q:
        return False
    q_nums = _numerals(query)
    for nm in [resolved_name] + list(aliases or []):
        if q_nums and _numerals(nm) and _numerals(nm) != q_nums:
            continue
        n = _name_tokens(nm)
        if not n:
            continue
        if q == n:
            return True
        if q < n and (n - q) <= _TYPE_TOKENS:
            return True
        if n < q and (q - n) <= _TITLE_TOKENS:
            return True
    return False


_P31_TYPE = {
    "Q5": "person",            # human
    "Q43229": "org",           # organization
    "Q4830453": "company",     # business
    "Q783794": "company",      # company
    "Q6881511": "company",     # enterprise
    "Q515": "place",           # city
    "Q486972": "place",        # human settlement
    "Q41176": "building",      # building
    "Q16560": "event",         # recurring event (approx via subclasses not fetched)
}


def _infer_type(p31_qids):
    for q in p31_qids or []:
        if q in _P31_TYPE:
            return _P31_TYPE[q]
    return "other"


def _resolve_live(name, context_text=""):
    """Live Wikidata resolution with adjudication. Does NOT touch
    the registry (resolve() handles cache-back)."""
    data = _wikidata_api({
        "action": "wbsearchentities", "search": name, "language": "en",
        "format": "json", "limit": 10,
    })
    raw_hits = (data or {}).get("search") or []
    if not raw_hits:
        return None
    ids = [h["id"] for h in raw_hits]
    detail = _wikidata_api({
        "action": "wbgetentities", "ids": "|".join(ids),
        "props": "sitelinks|claims|descriptions|aliases|labels",
        "format": "json", "languages": "en",
    }) or {}
    entities = detail.get("entities") or {}
    # P31 labels for the type/context agreement signal
    p31_ids = set()
    for e in entities.values():
        for c in (e.get("claims") or {}).get("P31", [])[:2]:
            try:
                p31_ids.add(c["mainsnak"]["datavalue"]["value"]["id"])
            except Exception:
                pass
    p31_labels = {}
    if p31_ids:
        lab = _wikidata_api({
            "action": "wbgetentities", "ids": "|".join(sorted(p31_ids)),
            "props": "labels", "format": "json", "languages": "en",
        }) or {}
        for qid, e in (lab.get("entities") or {}).items():
            p31_labels[qid] = (e.get("labels", {}).get("en") or {}).get("value", "")
    hits = []
    for h in raw_hits:
        e = entities.get(h["id"]) or {}
        claims = e.get("claims") or {}
        p31 = []
        for c in claims.get("P31", []):
            try:
                p31.append(c["mainsnak"]["datavalue"]["value"]["id"])
            except Exception:
                pass
        p18 = None
        try:
            p18 = claims["P18"][0]["mainsnak"]["datavalue"]["value"]
        except Exception:
            pass
        hits.append({
            "qid": h["id"],
            "label": h.get("label") or (e.get("labels", {}).get("en") or {}).get("value"),
            "description": (e.get("descriptions", {}).get("en") or {}).get("value", ""),
            "aliases": [a.get("value") for a in (e.get("aliases", {}).get("en") or [])],
            "sitelinks": len(e.get("sitelinks") or {}),
            "p31": p31,
            "p31_labels": [p31_labels.get(q, "") for q in p31],
            "p18_file": p18,
            "is_disambiguation": "Q4167410" in p31,
        })
    winner, method, confidence = _adjudicate(hits, context_text, name)
    if not winner:
        return None
    p18_width = None
    if winner.get("p18_file"):
        info = _commons_api({
            "action": "query", "prop": "imageinfo", "iiprop": "size",
            "format": "json", "titles": "File:" + winner["p18_file"],
        }) or {}
        for p in (info.get("query", {}).get("pages") or {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            p18_width = ii.get("width")
    return {
        "query": name,
        "name": winner.get("label") or name,
        "aliases": list(winner.get("aliases") or []),
        "qid": winner["qid"],
        "p18_file": winner.get("p18_file"),
        "p18_quality": p18_width,
        "type": _infer_type(winner.get("p31")),
        "has_local_instances": False,
        "method": method,
        "confidence": confidence,
        "confusables": [],
        "blocked_files": [],
        "notes": "",
        "description": winner.get("description", ""),
        "sitelinks": winner.get("sitelinks", 0),
        "candidates": [{"qid": h["qid"], "sitelinks": h.get("sitelinks", 0),
                        "context_score": h.get("context_score", 0)}
                       for h in hits],
    }


def _cache_back(query_name, result, context_text=""):
    """Persist a successful live resolution into the registry file.

    POISONING GUARD (corpus-replay-live.json residual risk #1):
    the winner is cached ONLY when it bears the queried name —
    names_agree() against its label or aliases, the same
    standard verified_sourcer.identity_agrees applies at
    decision time. Before this guard, resolve() cached the
    sitelink winner unconditionally: the replay's fixed run
    vetoed 'Adrian Abraham' → Adrian Jacobs at decision time
    while _cache_back was already writing Q2825029 into the
    registry under that alias — and registry-method results are
    EXEMPT from the decision-time guard (exact by construction),
    so a retained entry would have promoted a namesake error to
    curated-grade truth. The veto has to happen here, before
    the write, or it does not happen at all.

    Provenance: every write records the resolution method, the
    confidence, and the context the adjudication ran against
    (resolved_method / resolved_confidence / resolved_context,
    the context also quoted in the human-readable notes).
    Never overwrites an existing entry. Returns True when an
    entry was written. Failure is silent (caching must not
    break resolution)."""
    try:
        if not result or not result.get("qid"):
            return False
        if not names_agree(query_name, result.get("name"),
                           result.get("aliases")):
            return False
        reg = load_registry()
        if _candidates(query_name, reg):
            return False
        aliases = [query_name]
        if result.get("name") and result["name"] != query_name:
            aliases.append(result["name"])
        for a in result.get("aliases") or []:
            if a and a not in aliases:
                aliases.append(a)
        reg.setdefault("entities", []).append({
            "name": result.get("name") or query_name,
            "aliases": aliases,
            "type": result.get("type") or "other",
            "wikidata_qid": result.get("qid"),
            "p18_file": result.get("p18_file"),
            "p18_quality": result.get("p18_quality"),
            "has_local_instances": False,
            "official_domain": None,
            "confusables": [],
            "blocked_files": [],
            "resolved_method": result.get("method"),
            "resolved_confidence": result.get("confidence"),
            "resolved_context": (context_text or "")[:400],
            "notes": f"auto-resolved via {result.get('method')} "
                     f"(confidence {result.get('confidence')}); "
                     f"context: {(context_text or '')[:200]!r}; "
                     f"description: {result.get('description', '')}",
        })
        # Temp file in the REGISTRY's directory, not HERE: an
        # atomic os.replace cannot cross filesystems (a registry
        # path outside the pipeline tree — as in tests — would
        # silently fail the write on a cross-device link).
        fd, tmp = tempfile.mkstemp(
            dir=os.path.dirname(os.path.abspath(REGISTRY_PATH)),
            suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(reg, f, indent=1, ensure_ascii=False)
        os.replace(tmp, REGISTRY_PATH)
        global _registry_cache
        _registry_cache = reg
        return True
    except Exception:
        return False


# ── public resolution ────────────────────────────────────────────
def resolve(name, context_text=""):
    """Resolve an entity name to a verified Wikidata identity.

    Registry first (hand-verified data wins); same-name registry
    pairs are adjudicated by context_hints; otherwise live Wikidata
    with sitelink-primacy adjudication, cached back on success.
    Returns a result dict, or None when nothing resolves anywhere.
    """
    cands = _candidates(name)
    if len(cands) == 1:
        r = _from_entry(cands[0], "registry",
                        "high" if cands[0].get("wikidata_qid") else "low")
        r["query"] = name
        return r
    if len(cands) > 1:
        scored = sorted(cands, key=lambda e: -_hint_score(e, context_text))
        top = _hint_score(scored[0], context_text)
        second = _hint_score(scored[1], context_text) if len(scored) > 1 else 0
        if top > second:
            r = _from_entry(scored[0], "registry-context",
                            "high" if top >= 2 else "medium")
            r["query"] = name
            return r
        # Context does not discriminate: fall through to live
        # adjudication rather than guessing between namesakes.
    live = _resolve_live(name, context_text)
    if live:
        _cache_back(name, live, context_text)
        return live
    if cands:
        r = _from_entry(cands[0], "registry", "low")
        r["query"] = name
        r["notes"] = (r.get("notes") + " [ambiguous registry name; context "
                      "did not discriminate and live resolution failed]").strip()
        return r
    return None


# ── depicts (P180) candidates ────────────────────────────────────
def _license_ok(license_id, license_short):
    """CC0 / public domain / CC BY / CC BY-SA only. NC and ND are
    rejected programmatically (design.md Rung 1). Unknown = reject
    (fail closed)."""
    text = f"{license_id or ''} {license_short or ''}".lower()
    tokens = set(re.split(r"[^a-z0-9]+", text))
    if "nc" in tokens or "nd" in tokens:
        return False
    if "cc0" in tokens or "public" in tokens and "domain" in tokens:
        return True
    if text.strip().startswith("cc by") or "cc-by" in text:
        return True
    return False


def depicts_candidates(qid, limit=10):
    """Commons files with a depicts (P180) statement equal to qid,
    via the Commons API haswbstatement search. Each candidate carries
    its license from extmetadata; NC/ND (and unknown) licenses are
    filtered out. Returns [{title, file_key, url, width, height,
    license}]."""
    if not qid:
        return []
    data = _commons_api({
        "action": "query", "format": "json",
        "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"haswbstatement:P180={qid}",
        "gsrlimit": max(limit * 3, 20),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata",
    }) or {}
    out = []
    for p in (data.get("query", {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii:
            continue
        em = ii.get("extmetadata") or {}
        lic = (em.get("License") or {}).get("value", "")
        lic_short = (em.get("LicenseShortName") or {}).get("value", "")
        if not _license_ok(lic, lic_short):
            continue
        out.append({
            "title": p.get("title"),
            "file_key": file_key(p.get("title")),
            "url": ii.get("url"),
            "width": ii.get("width"),
            "height": ii.get("height"),
            "license": lic_short or lic,
        })
        if len(out) >= limit:
            break
    return out
