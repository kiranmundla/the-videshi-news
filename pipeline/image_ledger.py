#!/usr/bin/env python3
"""image_ledger.py — Rung 0 of the image-sourcing rebuild (2026-10-30):
the intent + provenance ledger. Design:
~/workspace/research_notes/image-rebuild-2026-10-30/design.md §2.

RECORDS ONLY. Nothing in this module changes a sourcing decision, a
gate outcome, or any published value. Every public function is
best-effort: a ledger failure must never break a producer, so callers
wrap calls in try/except AND this module swallows its own errors
(returning None / {} / False).

Two stores:

1. Intent — the DB columns that already exist on p2_articles:
   image_entities (text[]), image_must_show (text),
   image_search_query (text). The archive audit found them populated
   on 0 of 378 articles: the pipeline never stated what an image must
   show, so nothing could verify that it did. intent_columns()
   derives them at insert (writer-supplied values always win) from
   headline subjects + named co-subjects, reusing the picture pass's
   subject extraction (article_picture_pass.extract_article_entities
   + headline_subject_names).

2. Provenance — every image placement or removal, recorded as:
     {article_id, slug, surface, action, producer, source_route,
      image_url, source_page_url, original_file_url, file_key,
      rights_status, license, attribution, capture_year, entity,
      reason, placed_at, history}
   p2_articles has NO image_provenance column, and this environment
   has no Supabase Management API token to add one (verified
   2026-10-30: no SUPABASE_ACCESS_TOKEN / sbp_ token exists in any
   env file on this box — the value referenced by older scripts is
   not provisioned). So the ledger of record is the append-only
   JSONL at pipeline/.state/image-provenance.jsonl (override with
   $IMAGE_LEDGER_PATH). The DDL is staged in
   image_provenance_migration.sql and backfill_image_provenance.py
   replays this JSONL into the column once it exists. As a bridge,
   record_provenance() ALSO best-effort syncs the current placement
   (with its history array) into the image_provenance column when
   that column exists — it probes once per process and stays silent
   while the column is missing, so DB sync starts the day the
   migration lands with no code change.

Reviewer strips are applied by the reviewer agent directly via
Supabase PATCH (there is no strip code path), so removals from that
flow are recorded through this module's CLI:

  python3 image_ledger.py record-removal --article-id <uuid> \
      --surface hero --removed-url <url> --reason "wrong venue"
  python3 image_ledger.py record-removal --article-id <uuid> \
      --surface inline --removed-url <url> --reason "namesake"

Routes (source_route): wikimedia, wikidata_p18, person_profile,
official, source_og, pexels, youtube_thumb, manual, other.
Rights (rights_status): verified-license, official, public-domain,
embed, unknown. Derivation is conservative: anything not positively
established by a license string or a known-license route stays
"unknown" — per the Oct 30 editorial standard, unknown rights are
not publishable; this module only RECORDS that fact, later rungs
enforce it.
"""

import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROUTES = {"wikimedia", "wikidata_p18", "person_profile", "official",
          "source_og", "pexels", "youtube_thumb", "manual", "other"}
RIGHTS = {"verified-license", "official", "public-domain", "embed",
          "unknown"}

_MODULE_DIR = Path(__file__).resolve().parent
_DB_COLUMN_STATE = {"probed": False, "exists": False}


def ledger_path():
    env = os.environ.get("IMAGE_LEDGER_PATH")
    if env:
        return Path(env)
    return _MODULE_DIR / ".state" / "image-provenance.jsonl"


def _now():
    return datetime.now(timezone.utc).isoformat()


# ── canonical file identity ────────────────────────────────────────
# Mirrors article_picture_pass._wikimedia_file_key (the IOB fix,
# commit 72b6f805d): duplicate/identity comparisons must use this
# key, never raw URL strings. Kept as a local copy so this module
# stays importable without the picture pass's dependency chain;
# test_image_ledger.py asserts parity on Wikimedia forms.
def file_key_for(text):
    """Canonical identity of an image from any of its surface
    forms. Wikimedia files resolve to the normalized 'name.ext'
    key; other URLs resolve to their normalized path tail; bare
    'File:' titles work too. None when nothing resolves."""
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


def commons_file_page_url(url):
    """The Commons file page for an upload.wikimedia.org URL, or
    None. Reconstructed from the canonical file key."""
    if not url or "wikimedia.org" not in str(url):
        return None
    key = file_key_for(url)
    if not key:
        return None
    return ("https://commons.wikimedia.org/wiki/File:"
            + key.replace(" ", "_"))


# ── route + rights derivation ──────────────────────────────────────
_SOURCER_ROUTES = {
    "og:image": "source_og",
    "rss_thumbnail": "source_og",
    "person_cache": "person_profile",
    "person_profile": "person_profile",
    "youtube_thumbnail": "youtube_thumb",
    "official_source": "official",
    "brand_official": "official",
    "prnewswire": "official",
    "wikipedia": "wikimedia",
    "wikipedia_headline_guard": "wikimedia",
    "commons_search": "wikimedia",
    "pexels": "pexels",
}


def route_from_sourcer_name(source_name):
    """image_sourcer.source_hero_image's source_name → ledger route."""
    if not source_name:
        return "other"
    return _SOURCER_ROUTES.get(str(source_name).strip(), "other")


def route_from_picture_pass(route):
    """article_picture_pass candidate route label → ledger route."""
    r = str(route or "")
    if r.startswith(("A —", "C —")):
        return "wikimedia"
    if r.startswith("B —"):
        return "official"
    if r == "person_images cache":
        return "person_profile"
    return "other"


def route_for_url(url):
    """Best route derivable from a bare URL (insert paths that only
    carry the writer's final URL)."""
    if not url:
        return "other"
    u = str(url).lower()
    if "wikimedia.org" in u or "wikipedia.org" in u:
        return "wikimedia"
    if "img.youtube.com" in u or "i.ytimg.com" in u:
        return "youtube_thumb"
    if "images.pexels.com" in u or "pexels.com" in u:
        return "pexels"
    return "other"


def rights_status(route, license_text=None, attribution=None):
    """Conservative rights derivation. A license string that
    positively names CC0 / public domain / a CC license wins;
    Pexels carries its own license; profile/official routes are
    'official'. Everything else is 'unknown' — recorded, not
    judged, at this rung."""
    text = f"{license_text or ''} {attribution or ''}".lower()
    if "cc0" in text or "public domain" in text:
        return "public-domain"
    if re.search(r"cc[ -]?by", text) or "creative commons" in text:
        return "verified-license"
    if route == "pexels":
        return "verified-license"
    if route in ("person_profile", "official"):
        return "official"
    return "unknown"


# ── intent ─────────────────────────────────────────────────────────
def _subject_names(article):
    """Headline subjects + named co-subjects for one article dict,
    via the picture pass's extraction (the same code that decides
    hero eligibility). Returns [] when extraction is unavailable —
    intent derivation must never break an insert."""
    try:
        sys.path.insert(0, str(_MODULE_DIR))
        import article_picture_pass as APP
        entities = APP.extract_article_entities(article)
        subjects = APP.headline_subject_names(article, entities)
        by_lower = {e["name"].lower(): e["name"] for e in entities}
        ordered = []
        for e in entities:  # extraction order = ranked order
            if e["name"].lower() in subjects:
                ordered.append(e["name"])
        for s in subjects:  # any subject not in ranked order
            if s in by_lower and by_lower[s] not in ordered:
                ordered.append(by_lower[s])
        return ordered
    except Exception:
        return []


def intent_columns(article):
    """The image_entities / image_must_show / image_search_query
    values to write at insert. Writer-supplied values always win;
    derivation only fills what the writer left empty. Returns {}
    when nothing can be stated (never invents intent)."""
    if not isinstance(article, dict):
        return {}
    out = {}
    writer_entities = [str(e).strip() for e in
                       (article.get("image_entities") or [])
                       if str(e).strip()]
    subjects = _subject_names(article)
    entities = list(writer_entities)
    for s in subjects:
        if s.lower() not in {e.lower() for e in entities}:
            entities.append(s)
    if entities:
        out["image_entities"] = entities
    must_show = (article.get("image_must_show") or "").strip()
    if not must_show and subjects:
        must_show = ("Must show: " + "; ".join(subjects[:4])
                     + " (headline subject"
                     + ("s" if len(subjects) > 1 else "") + ")")
    if must_show:
        out["image_must_show"] = must_show
    query = (article.get("image_search_query") or "").strip()
    if not query and subjects:
        query = subjects[0]
    if query:
        out["image_search_query"] = query
    return out


# ── provenance: JSONL ledger ───────────────────────────────────────
def _append_jsonl(record):
    path = ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False)
    try:
        import fcntl
        with open(path, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(line + "\n")
            fcntl.flock(f, fcntl.LOCK_UN)
    except ImportError:  # non-POSIX fallback; appends are line-sized
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    return True


def read_ledger(article_id=None, slug=None, path=None):
    """All ledger records, optionally filtered to one article.
    Used by the backfill and by tests."""
    p = Path(path) if path else ledger_path()
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if article_id and rec.get("article_id") != article_id:
            continue
        if slug and rec.get("slug") != slug:
            continue
        out.append(rec)
    return out


def current_with_history(records):
    """Fold one article's ledger records into the image_provenance
    JSONB shape: the latest event as the current placement, every
    earlier event preserved in `history` (oldest first). Removals
    are events too — a removal becomes the current state, with the
    placement it removed kept in history. Nothing is erased."""
    if not records:
        return None
    current = dict(records[-1])
    current["history"] = [dict(r) for r in records[:-1]]
    return current


# ── provenance: best-effort DB sync (activates when the column
#    exists; silent until then) ────────────────────────────────────
def _sb_env():
    url = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    return (url, key) if url and key else (None, None)


def _curl_json(method, url, key, data=None):
    cmd = ["curl", "-sS", "-X", method, url,
           "-H", f"apikey: {key}",
           "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json"]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    out = (r.stdout or "").strip()
    return json.loads(out) if out else None


def _db_column_exists(url, key):
    if _DB_COLUMN_STATE["probed"]:
        return _DB_COLUMN_STATE["exists"]
    _DB_COLUMN_STATE["probed"] = True
    try:
        res = _curl_json(
            "GET",
            f"{url}/rest/v1/p2_articles?select=image_provenance&limit=1",
            key)
        _DB_COLUMN_STATE["exists"] = isinstance(res, list)
    except Exception:
        _DB_COLUMN_STATE["exists"] = False
    return _DB_COLUMN_STATE["exists"]


def _sync_db(record):
    """Best-effort: fold this article's full JSONL history into
    p2_articles.image_provenance. No-op (and silent) while the
    column doesn't exist or creds are absent."""
    article_id = record.get("article_id")
    if not article_id:
        return False
    url, key = _sb_env()
    if not url:
        return False
    try:
        if not _db_column_exists(url, key):
            return False
        records = read_ledger(article_id=article_id)
        prov = current_with_history(records)
        if prov is None:
            return False
        _curl_json("PATCH",
                   f"{url}/rest/v1/p2_articles?id=eq.{article_id}",
                   key, {"image_provenance": prov})
        return True
    except Exception:
        return False


# ── provenance: the write API producers call ───────────────────────
def record_provenance(article_id=None, slug=None, surface="hero",
                      action="placed", producer=None,
                      source_route=None, image_url=None,
                      source_page_url=None, original_file_url=None,
                      rights=None, license_text=None, attribution=None,
                      capture_year=None, entity=None, reason=None,
                      extra=None):
    """Append one placement/removal event to the ledger (and
    best-effort sync the DB column). Returns the record, or None
    on failure — a ledger failure never propagates."""
    try:
        route = source_route if source_route in ROUTES else "other"
        if not source_page_url and route == "wikimedia":
            source_page_url = commons_file_page_url(
                image_url or original_file_url)
        record = {
            "article_id": article_id,
            "slug": slug,
            "surface": surface,
            "action": action,
            "producer": producer,
            "source_route": route,
            "image_url": image_url,
            "source_page_url": source_page_url,
            "original_file_url": original_file_url or image_url,
            "file_key": file_key_for(original_file_url or image_url
                                     or source_page_url),
            "rights_status": rights if rights in RIGHTS else
                rights_status(route, license_text, attribution),
            "license": license_text,
            "attribution": attribution,
            "capture_year": capture_year,
            "entity": entity,
            "reason": reason,
            "placed_at": _now(),
        }
        if extra:
            record["extra"] = extra
        _append_jsonl(record)
        _sync_db(record)
        return record
    except Exception:
        return None


def record_removal(article_id=None, slug=None, surface="hero",
                   removed_url=None, producer=None, reason=None,
                   source_route=None):
    """A strip/removal event: the placement history stays in the
    ledger; the removal becomes the article's current state."""
    if source_route is None and removed_url:
        source_route = route_for_url(removed_url)
    return record_provenance(
        article_id=article_id, slug=slug, surface=surface,
        action="removed", producer=producer,
        source_route=source_route, image_url=removed_url,
        reason=reason)


# ── CLI (reviewer strip path + manual fixes) ──────────────────────
def _main(argv):
    import argparse
    ap = argparse.ArgumentParser(
        description="Image intent + provenance ledger (Rung 0).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    rm = sub.add_parser("record-removal",
                        help="record a reviewer strip / removal")
    rm.add_argument("--article-id", required=True)
    rm.add_argument("--surface", default="hero",
                    choices=["hero", "inline", "gallery"])
    rm.add_argument("--removed-url", default=None)
    rm.add_argument("--slug", default=None)
    rm.add_argument("--reason", default=None)
    rm.add_argument("--producer", default="reviewer")
    pl = sub.add_parser("record-placement",
                        help="record a manual placement")
    pl.add_argument("--article-id", required=True)
    pl.add_argument("--surface", default="hero",
                    choices=["hero", "inline", "gallery"])
    pl.add_argument("--image-url", required=True)
    pl.add_argument("--slug", default=None)
    pl.add_argument("--source-route", default="manual")
    pl.add_argument("--source-page-url", default=None)
    pl.add_argument("--reason", default=None)
    pl.add_argument("--producer", default="manual")
    args = ap.parse_args(argv)
    if args.cmd == "record-removal":
        rec = record_removal(article_id=args.article_id,
                             slug=args.slug, surface=args.surface,
                             removed_url=args.removed_url,
                             producer=args.producer,
                             reason=args.reason)
    else:
        rec = record_provenance(
            article_id=args.article_id, slug=args.slug,
            surface=args.surface, producer=args.producer,
            source_route=args.source_route, image_url=args.image_url,
            source_page_url=args.source_page_url, reason=args.reason)
    print(json.dumps(rec, ensure_ascii=False) if rec
          else "LEDGER WRITE FAILED")
    return 0 if rec else 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
