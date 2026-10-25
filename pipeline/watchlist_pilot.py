#!/usr/bin/env python3
"""
watchlist_pilot.py — Personality + Org Watchlist Synthesis Pilot (1 week).

Approved by Kiran 2026-10-24. Pilot window: 2026-10-25 → 2026-10-31.

Idea: prominent personalities and organisations increasingly break their
own news on X / Instagram / their official blogs. This pilot watches a
curated list (pipeline/watchlist-pilot.json, ~30 entries, two lanes) and
turns genuinely news-bearing posts into article candidates.

Evidence model (non-negotiable, inherited from the 2026-10-24 IG embed
gate — Kiran: "synthesize correctly"):
  * A watchlist post / blog item is an ATTRIBUTED primary source —
    source #1, never the article's sole truth.
  * An article may only be drafted after INDEPENDENT corroboration
    (the standing ≥2-source gate): matching coverage in p2_signals /
    p2_topics from a source that is not the poster.
  * DEDUP BEFORE DRAFTING: corroborated candidates are checked against
    already-published articles. Outcomes:
      (a) corroborated + not yet published  → draft candidate
      (b) corroborated + already published   → skip, "duplicate-of-ingest"
      (c) no corroboration                   → hold (never drafted)
    The pilot is judged on (a) vs (b): its true value is stories the
    regular ingest had NOT already covered.

Reuse, not reinvention:
  * X reads: TwitterAPI.io via refresh-embed-cache.py's fetch_x_handle
    (X API itself is write-only in this pipeline) + cache/embed_cache.json
  * IG reads: Meta connector via refresh-embed-cache.py's
    fetch_ig_posts_batch (structural 429 detection) + the same cache
  * RSS: official blogs/press feeds from the config, fetched with curl
    (urllib fails through this proxy) and parsed with a small stdlib
    parser (feedparser is not installed on this box)
  * Scoring: GPT-4o-mini, v3-select.py's curl + json_object pattern
  * Insert path: v3-batch-insert.py process_article consumes the sample
    article dict this script emits (it hardcodes status="published", so
    --draft here writes the validated article JSON to
    pipeline/.state/watchlist-sample.json instead of inserting — see
    build_sample_article / cmd_draft).

Usage:
  python3 -u watchlist_pilot.py --dry-run [--no-refresh] [--hours 72]
  python3 -u watchlist_pilot.py --draft   [--no-refresh]
  python3 -u watchlist_pilot.py --dry-run --commit-ledger   # mark seen
  python3 -u watchlist_pilot.py --draft-all [--no-refresh] [--draft-cap 6]
      Daily pilot run (Kiran approved draft mode 2026-10-24): draft EVERY
      outcome-(a) candidate (cap 6, highest score first) as a file in
      .state/watchlist-drafts/, write + print the daily digest
      (.state/watchlist-digest-YYYYMMDD.json, Pacific date), and consume
      the batch in the ledger. Drafts are NEVER inserted — see _draft_one.

Env: ~/workspace/.env.supabase, ~/workspace/.env.openai,
     ~/workspace/.env.twitterapi-io (all loaded if present).
"""

import argparse
import hashlib
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

CONFIG_PATH = os.path.join(_DIR, "watchlist-pilot.json")
CACHE_PATH = os.path.join(_DIR, "cache", "embed_cache.json")
STATE_PATH = os.path.join(_DIR, ".state", "watchlist-pilot.json")
SAMPLE_PATH = os.path.join(_DIR, ".state", "watchlist-sample.json")
REPORT_DIR = os.path.join(_DIR, ".state")
DRAFTS_DIR = os.path.join(_DIR, ".state", "watchlist-drafts")
DRAFT_ALL_CAP = 6

# GPT-4o-mini list prices (same constants v3-select.py uses).
PRICE_IN_PER_M = 0.15
PRICE_OUT_PER_M = 0.60

SCORE_THRESHOLD_DEFAULT = 7
NEWS_TYPES = {
    "announcement", "statement", "result", "milestone", "launch",
    "appointment", "policy", "other-news",
}
MAX_POSTS_SCORED = 60

_CAT_NORMALIZE = {
    "lifestyle": "lifestyle-health", "health": "lifestyle-health",
    "finance": "markets-finance", "markets": "markets-finance",
    "market": "markets-finance", "business": "markets-finance",
    "nri": "nri-world", "world": "nri-world",
    "tech": "technology", "cricket": "sports",
    "bollywood": "entertainment", "movies": "entertainment",
    "visa": "immigration", "h1b": "immigration",
    "politics": "news", "india": "news",
}


def load_env(*paths):
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ─── Pure helpers (unit-tested in test_watchlist_pilot.py) ───────────────────

STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "will", "has",
    "have", "our", "your", "their", "they", "them", "then", "than",
    "into", "about", "after", "before", "over", "under", "been", "were",
    "are", "was", "its", "it", "in", "on", "of", "to", "a", "an", "is",
    "at", "by", "as", "we", "you", "he", "she", "his", "her", "new",
    "now", "today", "india", "indian", "says", "said", "announces",
    "announced", "announce", "official", "watch", "video", "live",
    "http", "https", "www", "com",
}

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'\-]*")


def distinctive_tokens(text):
    """Lowercased content tokens (len>=4, not stopwords) from a text."""
    out = set()
    for tok in _TOKEN_RE.findall((text or "").lower()):
        tok = tok.strip("'-")
        if len(tok) >= 4 and tok not in STOPWORDS:
            out.add(tok)
    return out


def entity_phrases(entities):
    """Normalised multiword entity phrases from a scorer entity list."""
    phrases = set()
    for e in entities or []:
        p = re.sub(r"\s+", " ", (e or "").strip().lower())
        if p and " " in p:
            phrases.add(p)
    return phrases


def candidate_keywords(post_text, entities):
    """(token set, phrase set) used for corroboration matching."""
    toks = distinctive_tokens(post_text)
    for e in entities or []:
        toks |= distinctive_tokens(e)
    return toks, entity_phrases(entities)


def _text_contains_phrase(text_lower, phrase):
    return phrase in text_lower


def match_corroboration(cand_tokens, cand_phrases, items, self_markers,
                        min_shared=3, phrase_min_shared=1, min_ratio=0.0):
    """Find the best independent corroborating item for a candidate.

    items: [{title, source_name, url, extra_text?}] (signals/topics/articles)
    self_markers: lowercase strings identifying the poster (handles, name) —
    an item is excluded when its URL equals the post URL or its source_name
    contains a self marker of length >= 4.

    Default (corroboration) rule: >=min_shared shared distinctive tokens,
    OR a shared multiword entity phrase plus >=phrase_min_shared tokens.

    Strict rule (already-published dedup; min_ratio > 0): additionally the
    shared tokens must cover at least min_ratio of the SMALLER token set.
    A person-name + generic-token overlap ("Arshdeep Singh" in two
    different stories) has a low ratio and must not mark a new story as
    already published — the pilot's (a)/(b) split is judged on this.
    Returns (item, shared_count) or None.
    """
    markers = {m.lower() for m in self_markers if m and len(m) >= 4}
    best, best_shared = None, 0
    for it in items or []:
        url = (it.get("url") or "").lower()
        src = (it.get("source_name") or "").lower()
        if any(m in src for m in markers):
            continue
        if url and any(url.rstrip("/") == m.rstrip("/") for m in markers if m.startswith("http")):
            continue
        text = f"{it.get('title') or ''} {it.get('extra_text') or ''}"
        toks = distinctive_tokens(text)
        shared = len(cand_tokens & toks)
        phrase_hit = any(_text_contains_phrase(text.lower(), p) for p in cand_phrases)
        if min_ratio > 0:
            denom = min(len(cand_tokens), len(toks)) or 1
            ratio = shared / denom
            need = phrase_min_shared if phrase_hit else min_shared
            ok = shared >= need and ratio >= min_ratio
        else:
            ok = shared >= min_shared or (phrase_hit and shared >= phrase_min_shared)
        if ok and shared > best_shared:
            best, best_shared = it, shared
    if best is None:
        return None
    return best, best_shared


def parse_score_results(content, batch_len):
    """Parse a scorer LLM response (v3-select pattern): defensive, skips
    malformed items, clamps scores, normalises categories. Returns
    {batch_index: result_dict}."""
    out = {}
    if not isinstance(content, dict):
        return out
    for item in content.get("results", []):
        if not isinstance(item, dict):
            continue
        try:
            idx = int(item.get("id", 0)) - 1
        except (TypeError, ValueError):
            continue
        if not (0 <= idx < batch_len):
            continue
        try:
            score = float(item.get("score", 0))
        except (TypeError, ValueError):
            score = 0.0
        score = max(0.0, min(10.0, score))
        cat = _CAT_NORMALIZE.get(str(item.get("category", "news")).lower(),
                                 str(item.get("category", "news")).lower())
        ents = item.get("entities") or []
        if not isinstance(ents, list):
            ents = []
        out[idx] = {
            "score": score,
            "type": str(item.get("type", "other-news")).lower(),
            "summary": str(item.get("summary", ""))[:300],
            "entities": [str(e) for e in ents][:8],
            "category": cat,
        }
    return out


def passes_score_gate(result, threshold=SCORE_THRESHOLD_DEFAULT):
    """Strict news gate: high score AND a news-bearing type. A 9/10 promo
    still fails — type is checked independently of score."""
    if not result:
        return False
    return result.get("score", 0) >= threshold and result.get("type") in NEWS_TYPES


def parse_post_time(value, platform):
    """Parse the three timestamp shapes the caches/feeds produce → aware
    datetime in UTC, or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).strip()
        dt = None
        if "T" in s:  # ISO-8601 (Atom feeds, e.g. Apple's fractional-second Z)
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            except ValueError:
                dt = None
        if dt is None:
            for fmt in ("%a %b %d %H:%M:%S %z %Y",          # X cache/live
                        "%Y-%m-%d %H:%M:%S",                 # IG cache
                        "%Y-%m-%dT%H:%M:%S%z",
                        "%Y-%m-%dT%H:%M:%S"):
                try:
                    dt = datetime.strptime(s.replace("Z", "+0000") if fmt.endswith("%z") else s, fmt)
                    break
                except (ValueError, TypeError):
                    continue
        if dt is None:
            try:
                dt = parsedate_to_datetime(s)           # RSS RFC-822
            except Exception:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def is_new_post(post, watermark, seen_ids):
    """A post is new when it is after the ledger watermark and its id has
    not been seen or drafted before. Ledger keys are platform-prefixed
    ("x:<id>", "ig:<shortcode>", "rss:<hash>") — the same form the ledger
    writers store."""
    pid = post.get("id")
    if pid and f"{post.get('platform', '')}:{pid}" in (seen_ids or set()):
        return False
    created = post.get("created_at_dt")
    if created is None or watermark is None:
        return True
    return created > watermark


def slugify(text, maxlen=80):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:maxlen].strip("-") or "watchlist-story"


def dedupe_candidates(posts):
    """Merge cross-posts of the same item by the same watchlist entry
    (e.g. the identical announcement on X and Instagram). Keeps the
    richest version (media first, then longest text) and records what
    was merged. Different entries are never merged."""
    kept = []
    for post in posts:
        toks = distinctive_tokens(post.get("text", ""))
        merged = False
        for k in kept:
            if k["entry_name"] != post["entry_name"]:
                continue
            ktoks = distinctive_tokens(k.get("text", ""))
            union = toks | ktoks
            jaccard = (len(toks & ktoks) / len(union)) if union else 0.0
            if jaccard >= 0.6:
                richer = (bool(post.get("photos")), len(post.get("text", "")))
                kricher = (bool(k.get("photos")), len(k.get("text", "")))
                if richer > kricher:
                    post["merged_from"] = k.get("merged_from", []) + [
                        f"{k['platform']}:{k['id']}"]
                    kept[kept.index(k)] = post
                else:
                    k["merged_from"] = k.get("merged_from", []) + [
                        f"{post['platform']}:{post['id']}"]
                merged = True
                break
        if not merged:
            kept.append(post)
    return kept


# ─── Minimal RSS/Atom parser (stdlib only; feedparser absent on this box) ───

def _local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(el, name):
    for child in el:
        if _local(child.tag) == name:
            return "".join(child.itertext()).strip()
    return ""


def _atom_link(el):
    for child in el:
        if _local(child.tag) == "link":
            rel = child.get("rel", "alternate")
            if rel in ("alternate", ""):
                return child.get("href", "")
    return ""


def parse_feed(xml_text, feed_name, feed_url):
    """Parse RSS 2.0 / Atom XML (already fetched) → [{id, title, text,
    url, created_at_dt}]. Unparseable input returns []."""
    items = []
    if not xml_text:
        return items
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    def _mk(id_src, title, summary, url, date_s):
        dt = parse_post_time(date_s, "rss")
        text = f"{title}. {summary}" if summary else title
        return {
            "id": hashlib.sha256((id_src or url or title).encode()).hexdigest()[:24],
            "title": title,
            "text": re.sub(r"<[^>]+>", " ", html.unescape(text))[:900],
            "url": url,
            "created_at_dt": dt,
        }

    for el in root.iter():
        lname = _local(el.tag)
        if lname == "item":  # RSS 2.0
            title = _child_text(el, "title")
            link = _child_text(el, "link")
            desc = _child_text(el, "description")
            date = _child_text(el, "pubdate") or _child_text(el, "date")
            guid = _child_text(el, "guid")
            if title and link:
                items.append(_mk(guid or link, title, desc, link, date))
        elif lname == "entry":  # Atom
            title = _child_text(el, "title")
            link = _atom_link(el)
            summary = _child_text(el, "summary") or _child_text(el, "content")
            date = _child_text(el, "published") or _child_text(el, "updated")
            eid = _child_text(el, "id")
            if title and link:
                items.append(_mk(eid or link, title, summary, link, date))
    return items


# ─── Network layer (curl only — urllib/requests fail through the proxy) ─────

def llm_call(payload_dict, timeout=60):
    """OpenAI chat completion via curl (v3-select.py pattern).
    Returns (parsed_content, usage, error)."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return None, None, "OPENAI_API_KEY not set"
    import tempfile
    payload = json.dumps(payload_dict)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        cmd = ["curl", "-sS", "--max-time", str(timeout),
               "-X", "POST", "https://api.openai.com/v1/chat/completions",
               "-H", f"Authorization: Bearer {key}",
               "-H", "Content-Type: application/json",
               "-d", f"@{tmp_path}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        if r.returncode != 0:
            return None, None, f"curl error (rc={r.returncode})"
        data = json.loads(r.stdout)
        if "error" in data:
            return None, None, data["error"].get("message", str(data["error"]))
        content = json.loads(data["choices"][0]["message"]["content"])
        return content, data.get("usage", {}), None
    except Exception as e:
        return None, None, str(e)
    finally:
        os.unlink(tmp_path)


def usage_cost(usage):
    if not usage:
        return 0.0
    return (usage.get("prompt_tokens", 0) * PRICE_IN_PER_M / 1_000_000
            + usage.get("completion_tokens", 0) * PRICE_OUT_PER_M / 1_000_000)


def sb_get(endpoint):
    """Supabase REST GET via curl. Returns parsed JSON or None."""
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return None
    cmd = ["curl", "-sS", "--max-time", "25", f"{sb_url}/rest/v1/{endpoint}",
           "-H", f"apikey: {sb_key}",
           "-H", f"Authorization: Bearer {sb_key}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def _ilike(column, keyword):
    return f"{column}=ilike.%25{urllib.parse.quote(keyword, safe='')}%25"


# ─── Detection ────────────────────────────────────────────────────────────────

def load_json_file(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return default


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def _load_refresh_mod():
    """Import refresh-embed-cache.py (hyphenated) for its fetch functions —
    the exact read paths the embed cache refresh uses."""
    spec = importlib.util.spec_from_file_location(
        "refresh_embed_cache", os.path.join(_DIR, "refresh-embed-cache.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _norm_x_post(raw, entry, origin):
    created = parse_post_time(raw.get("created_at"), "x")
    if created is None:
        return None
    handle = (raw.get("handle") or entry.get("x") or "").lower()
    return {
        "platform": "x",
        "entry_name": entry["name"],
        "lane": entry.get("lane", ""),
        "beat": entry.get("beat", ""),
        "handle": handle,
        "id": str(raw.get("id", "")),
        "text": raw.get("text", ""),
        "url": raw.get("url") or f"https://x.com/{handle}/status/{raw.get('id', '')}",
        "created_at_dt": created,
        "photos": raw.get("photos") or [],
        "has_video": bool(raw.get("has_video")),
        "origin": origin,
    }


def _norm_ig_post(raw, entry, origin):
    created = parse_post_time(raw.get("timestamp"), "ig")
    if created is None:
        return None
    sc = raw.get("shortCode", "")
    return {
        "platform": "ig",
        "entry_name": entry["name"],
        "lane": entry.get("lane", ""),
        "beat": entry.get("beat", ""),
        "handle": (raw.get("ownerUsername") or entry.get("ig") or "").lower(),
        "id": sc,
        "text": raw.get("caption", ""),
        "url": raw.get("url") or f"https://www.instagram.com/p/{sc}/",
        "created_at_dt": created,
        "photos": [raw["displayUrl"]] if raw.get("displayUrl") else [],
        "has_video": (raw.get("type") or "").lower() in ("video", "reel"),
        "origin": origin,
    }


def fetch_feed_items(feed):
    """Fetch one official RSS/Atom feed via curl and parse it."""
    cmd = ["curl", "-sS", "-L", "--max-time", "20",
           "-A", "TheVideshi/1.0 (thevideshi.com)", feed["url"]]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if r.returncode != 0 or not r.stdout:
        print(f"  ⚠ RSS fetch failed: {feed['url']} (rc={r.returncode})")
        return []
    return parse_feed(r.stdout, feed.get("name", ""), feed["url"])


def detect_posts(cfg, cache, refresh=True, window_hours=72):
    """Collect unified posts for all watchlist entries from the caches,
    optionally topped up live (watchlist handles only), plus Lane A RSS.

    Returns (posts, per_entry_counts). Posts carry created_at_dt and are
    NOT yet watermark-filtered."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=window_hours)
    posts = []
    counts = {}
    mod = None
    if refresh:
        try:
            mod = _load_refresh_mod()
        except Exception as e:
            print(f"  ⚠ could not load refresh module ({e}); cache-only detection")
            mod = None

    x_cache = cache.get("x", {}) if isinstance(cache, dict) else {}
    ig_cache = cache.get("ig", {}) if isinstance(cache, dict) else {}

    for entry in cfg.get("entries", []):
        name = entry["name"]
        got = 0
        # ── X ──
        xh = (entry.get("x") or "").lower()
        if xh:
            by_id = {}
            for raw in (x_cache.get(xh, {}) or {}).get("posts", []):
                p = _norm_x_post(raw, entry, "cache")
                if p and p["id"]:
                    by_id[p["id"]] = p
            if mod is not None:
                try:
                    for raw in mod.fetch_x_handle(xh, hours=window_hours, max_results=20):
                        p = _norm_x_post(raw, entry, "live")
                        if p and p["id"]:
                            by_id[p["id"]] = p
                except Exception as e:
                    print(f"  ⚠ X live fetch failed for @{xh}: {e}")
            for p in by_id.values():
                if p["created_at_dt"] >= cutoff and len(p["text"].strip()) >= 30:
                    posts.append(p)
                    got += 1
        # ── Instagram ──
        igh = (entry.get("ig") or "").lower()
        if igh:
            by_id = {}
            for raw in (ig_cache.get(igh, {}) or {}).get("posts", []):
                p = _norm_ig_post(raw, entry, "cache")
                if p and p["id"]:
                    by_id[p["id"]] = p
            if mod is not None:
                try:
                    live = mod.fetch_ig_posts_batch([igh], results_limit=12)
                    for raw in live.get(igh, []):
                        p = _norm_ig_post(raw, entry, "live")
                        if p and p["id"]:
                            by_id[p["id"]] = p
                except Exception as e:
                    print(f"  ⚠ IG live fetch failed for @{igh}: {e}")
            for p in by_id.values():
                if p["created_at_dt"] >= cutoff and len(p["text"].strip()) >= 30:
                    posts.append(p)
                    got += 1
        # ── RSS (Lane A blogs / press feeds) ──
        for feed in entry.get("rss", []) or []:
            try:
                items = fetch_feed_items(feed)
            except Exception as e:
                print(f"  ⚠ RSS failed for {feed.get('url')}: {e}")
                items = []
            for it in items:
                if it["created_at_dt"] is None or it["created_at_dt"] < cutoff:
                    continue
                posts.append({
                    "platform": "rss",
                    "entry_name": name,
                    "lane": entry.get("lane", ""),
                    "beat": entry.get("beat", ""),
                    "handle": "",
                    "feed_name": feed.get("name", ""),
                    "id": it["id"],
                    "text": it["text"],
                    "url": it["url"],
                    "created_at_dt": it["created_at_dt"],
                    "photos": [],
                    "has_video": False,
                    "origin": "rss",
                })
                got += 1
        counts[name] = got

    posts.sort(key=lambda p: p["created_at_dt"], reverse=True)
    return posts, counts


# ─── Scoring (GPT-4o-mini, v3-select pattern) ─────────────────────────────────

SCORER_PROMPT = """You score social-media posts and official blog/press items as NEWS candidates for The Videshi, a news site for the Indian diaspora.

Score STRICTLY. A post is news only when the post itself is the event: an announcement, an official statement or position, a result, a record/milestone, a launch, an appointment/resignation, a policy decision, or a first-person disclosure of a newsworthy fact — made by the account holder about their own domain.

Score these LOW (0-4) and type them accordingly:
- "promo": marketing, product hype without news facts, ticket/merch sales, discounts, partnership fluff
- "greeting": festival/birthday/anniversary wishes, congratulations to others, condolences with no new fact
- "personal": lifestyle, behind-the-scenes, family, fitness, throwbacks, teasers with no concrete news
- "repost": sharing/amplifying someone else's content with no new statement
- "commentary": opinions about third-party news the poster did not make

Scoring guide (news value for a diaspora audience): 9-10 = major announcement/statement with broad impact; 7-8 = solid news in the poster's domain; 5-6 = minor or niche; below 5 = not news.

Categories (use exactly one): news (India is the subject/actor/direct object), nri-world (everything outside India, diaspora or general world), immigration, technology, entertainment, sports, markets-finance, lifestyle-health, travel, food. Apply the subject rule, not the topic: a story is "news" only when India, the Indian government, Indian institutions, or Indian teams/companies are the actor or direct object.

For each item return: id (the number given), score (0-10), type (announcement|statement|result|milestone|launch|appointment|policy|other-news|promo|greeting|personal|repost|commentary), summary (one factual line: what news fact the post states), entities (proper nouns: people, orgs, places, events named), category.

Return ONLY JSON: {"results": [{"id": 1, "score": 8, "type": "announcement", "summary": "...", "entities": ["..."], "category": "technology"}]}
"""


def score_posts(posts, batch_size=12):
    """Score posts in batches. Returns ({post_key: result}, total_cost).
    post_key = f"{platform}:{id}". Unscored posts are simply absent."""
    results = {}
    total_cost = 0.0
    for start in range(0, len(posts), batch_size):
        batch = posts[start:start + batch_size]
        lines = []
        for i, p in enumerate(batch):
            who = (f"@{p['handle']}" if p["handle"]
                   else p.get("feed_name", "official feed"))
            lines.append(
                f"{i + 1}. [{p['entry_name']} via {who} on {p['platform'].upper()}, "
                f"{p['created_at_dt'].strftime('%Y-%m-%d')}] {p['text'][:500]}")
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user",
                          "content": SCORER_PROMPT + "\n\nITEMS:\n" + "\n".join(lines)}],
            "response_format": {"type": "json_object"},
            "max_tokens": max(len(batch) * 170, 1200),
            "temperature": 0,
        }
        content, usage, err = llm_call(payload, timeout=60)
        total_cost += usage_cost(usage)
        if err:
            time.sleep(2)
            content, usage, err = llm_call(payload, timeout=75)
            total_cost += usage_cost(usage)
        if err:
            print(f"  ⚠ scoring batch at {start} failed: {err}")
            continue
        parsed = parse_score_results(content, len(batch))
        for idx, res in parsed.items():
            p = batch[idx]
            results[f"{p['platform']}:{p['id']}"] = res
    return results, total_cost


# ─── Corroboration + already-published dedup ──────────────────────────────────

def _query_by_keywords(table, select, extra_filters, keywords, limit=15):
    """Targeted ilike queries per keyword (server-side) — fetching whole
    tables is not viable (p2_signals ingests ~10k rows/day)."""
    col = {"p2_signals": "title", "p2_topics": "canonical_title",
           "p2_articles": "headline"}[table]
    rows, seen = [], set()
    for kw in keywords:
        if len(kw) < 4:
            continue
        ep = f"{table}?select={select}&{_ilike(col, kw)}&{extra_filters}&limit={limit}"
        got = sb_get(ep)
        if not isinstance(got, list):
            if got is not None:
                print(f"  ⚠ {table} query for '{kw}' returned non-list: "
                      f"{str(got)[:140]}")
            continue
        for row in got:
            if not isinstance(row, dict):
                continue
            key = row.get("id") or row.get("original_url") or row.get("headline")
            if key and key not in seen:
                seen.add(key)
                rows.append(row)
    return rows


def _source_display_name(row):
    """Some ingest rows (notably RSS-type signals) carry a null
    source_name. Fall back to something factual: 'Google News' for
    google_news rows, else the URL's domain."""
    name = (row.get("source_name") or "").strip()
    if name:
        return name
    if row.get("source_type") == "google_news":
        return "Google News"
    host = urllib.parse.urlparse(row.get("original_url") or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _signal_items(keywords):
    since = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
    rows = _query_by_keywords(
        "p2_signals",
        "id,title,source_name,source_type,original_url,description,published_at,topic_id",
        f"published_at=gte.{urllib.parse.quote(since)}&order=published_at.desc",
        keywords)
    return [{"title": r.get("title", ""), "source_name": _source_display_name(r),
             "url": r.get("original_url", ""), "extra_text": r.get("description") or "",
             "topic_id": r.get("topic_id")} for r in rows]


def _topic_items(keywords):
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    rows = _query_by_keywords(
        "p2_topics", "id,canonical_title,created_at",
        f"created_at=gte.{urllib.parse.quote(since)}&order=created_at.desc",
        keywords)
    return [{"title": r.get("canonical_title", ""), "source_name": "",
             "url": "", "extra_text": "", "topic_id": r.get("id")} for r in rows]


def _article_items(keywords):
    since = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    rows = _query_by_keywords(
        "p2_articles", "id,headline,subheadline,slug,published_at",
        f"status=eq.published&published_at=gte.{urllib.parse.quote(since)}&order=published_at.desc",
        keywords)
    # articles use `headline`, not `title`
    out = []
    for r in rows:
        out.append({"title": r.get("headline", ""),
                    "source_name": "The Videshi (published)",
                    "url": f"https://www.thevideshi.com/articles/{r.get('slug', '')}",
                    "extra_text": r.get("subheadline") or "",
                    "slug": r.get("slug", "")})
    return out


def _topic_signal_url(topic_id):
    """A matched topic carries no URL; fetch one of its signals so the
    corroboration can serve as a real source #2."""
    if not topic_id:
        return None
    rows = sb_get(f"p2_signals?select=title,source_name,source_type,original_url,description"
                  f"&topic_id=eq.{topic_id}&order=published_at.desc&limit=5")
    for r in rows if isinstance(rows, list) else []:
        if isinstance(r, dict) and r.get("original_url"):
            return {"title": r.get("title", ""), "source_name": _source_display_name(r),
                    "url": r.get("original_url", ""), "extra_text": r.get("description") or ""}
    return None


def corroborate(post, scored):
    """Full gate for one scored candidate. Returns a dict:
      outcome: 'draft' (a) | 'duplicate' (b) | 'held' (c)
      corroboration: matched source item or None
      published_match: matched published article or None
    """
    entities = scored.get("entities", [])
    toks, phrases = candidate_keywords(post["text"], entities)
    # Query with the most distinctive entity tokens first.
    query_kws = []
    for e in entities:
        query_kws.extend(sorted(distinctive_tokens(e), key=len, reverse=True))
    query_kws = list(dict.fromkeys(query_kws))[:4]
    if not query_kws:
        query_kws = sorted(toks, key=len, reverse=True)[:3]

    self_markers = {post.get("handle", ""), post["entry_name"], post.get("url", "")}
    out = {"outcome": "held", "corroboration": None, "published_match": None,
           "keywords": sorted(toks)[:20]}

    articles = _article_items(query_kws)
    # STRICT dedup: a shared person name across two different stories must
    # not suppress a true add (see match_corroboration's strict rule).
    pub = match_corroboration(toks, phrases, articles,
                              self_markers - {post.get("url", "")},
                              min_shared=4, phrase_min_shared=2, min_ratio=0.30)
    if pub:
        out["published_match"] = pub[0]
        out["outcome"] = "duplicate"
        return out

    signals = _signal_items(query_kws)
    hit = match_corroboration(toks, phrases, signals, self_markers)
    if hit:
        out["corroboration"] = hit[0]
        out["outcome"] = "draft"
        return out

    topics = _topic_items(query_kws)
    hit = match_corroboration(toks, phrases, topics, self_markers)
    if hit:
        sig = _topic_signal_url(hit[0].get("topic_id"))
        if sig:
            out["corroboration"] = sig
            out["outcome"] = "draft"
            return out
        # Topic exists but no sourceable signal — corroboration too weak
        # to satisfy the ≥2-source gate. Held, honestly.
        out["topic_only_match"] = hit[0].get("title", "")
    return out


# ─── Synthesis ────────────────────────────────────────────────────────────────

WRITER_PROMPT = """You write a short news article for The Videshi (Indian diaspora news) from a primary-source post plus independent corroboration. Reuters tone: factual, plain, no hype, no filler phrases ("in a significant development", "it is worth noting").

RULES:
- Use ONLY facts present in the POST and CORROBORATION material given. Do not add background facts from memory.
- The first paragraph must attribute: "In a post on X, <name> ..." (or Instagram / on the <feed name> blog).
- Quote the post directly at most once, briefly.
- 4-6 short paragraphs. No subheadings.
- Return ONLY JSON: {"headline": "...", "subheadline": "1-2 sentences", "takeaways": ["3-4 bullets, last one reader-impact where the material supports it"], "paragraphs": ["...", "..."], "tags": ["3-5 tags"], "diaspora_angle": "one sentence, or empty if none is natural"}
"""


def synthesize(post, scored, corr, name_for_attr):
    """One GPT-4o-mini writing call. Returns (writer_dict, cost, error)."""
    platform_word = {"x": "X", "ig": "Instagram"}.get(post["platform"], post["platform"])
    if post["platform"] == "rss":
        platform_word = f"the {post.get('feed_name', 'official blog')}"
    material = (
        f"POST by {post['entry_name']} ({name_for_attr}) on {platform_word}, "
        f"{post['created_at_dt'].strftime('%Y-%m-%d')}:\n{post['text'][:1200]}\n\n"
        f"CORROBORATION ({corr.get('source_name', '')}): {corr.get('title', '')}. "
        f"{(corr.get('extra_text') or '')[:2400]}\n\n"
        f"Scorer summary: {scored.get('summary', '')}\nCategory: {scored.get('category', 'news')}")
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": WRITER_PROMPT + "\n\n" + material}],
        "response_format": {"type": "json_object"},
        "max_tokens": 1400,
        "temperature": 0.2,
    }
    content, usage, err = llm_call(payload, timeout=75)
    return content, usage_cost(usage), err


def build_sample_article(post, scored, corr, writer):
    """Assemble the article dict in v3-batch-insert.process_article's
    shape. THE EVIDENCE GATE lives here: with no independent corroboration
    this returns None — an uncorroborated post is never drafted."""
    if not corr or not corr.get("url"):
        return None
    if not writer or not writer.get("headline") or not writer.get("paragraphs"):
        return None
    try:
        import source_gate
        sources = [
            {"name": _source1_name(post), "url": post["url"]},
            {"name": corr.get("source_name") or "Corroborating coverage",
             "url": corr["url"]},
        ]
        if source_gate.gate_failure(sources) is not None:
            return None
    except Exception:
        return None

    platform_word = {"x": "X", "ig": "Instagram"}.get(post["platform"], "")
    paras = [f"<p>{html.escape(p)}</p>" for p in writer["paragraphs"] if p.strip()]
    if not paras:
        return None
    takeaways = "".join(f"<li>{html.escape(t)}</li>"
                        for t in (writer.get("takeaways") or [])[:4])
    body_parts = []
    if takeaways:
        body_parts.append(f'<div class="key-takeaways"><ul>{takeaways}</ul></div>')
    body_parts.append(paras[0])
    if platform_word:  # embed the primary-source post, enrich-on-publish style
        body_parts.append(post["url"])
    body_parts.extend(paras[1:])
    body = "\n\n".join(body_parts)

    headline = writer["headline"].strip()
    article = {
        "headline": headline,
        "subheadline": (writer.get("subheadline") or "").strip(),
        "body": body,
        "slug": slugify(headline),
        "category": scored.get("category", "news"),
        "vertical": scored.get("category", "news"),
        "tags": writer.get("tags") or [],
        "sources": sources,
        "diaspora_angle": writer.get("diaspora_angle", ""),
        "topic_id": None,
        "kids_relevant": False,
        "article_type": "breaking",
        "_watchlist_pilot": {
            "entry": post["entry_name"], "lane": post.get("lane", ""),
            "platform": post["platform"], "post_url": post["url"],
            "score": scored.get("score"), "type": scored.get("type"),
        },
    }
    # Hero hints (process_article order: verified person portrait overrides
    # a writer preset; org posts carry only their own media, never stock).
    if post.get("photos"):
        article["image_url"] = post["photos"][0]
        article["image_attribution"] = (
            f"Image: {post['entry_name']} via {platform_word or 'official post'}")
    if post.get("lane") == "B" and post["platform"] != "rss":
        article["image_search_persons"] = [post["entry_name"]]
    return article


def _source1_name(post):
    if post["platform"] == "x":
        return f"{post['entry_name']} on X (@{post['handle']})"
    if post["platform"] == "ig":
        return f"{post['entry_name']} on Instagram (@{post['handle']})"
    return post.get("feed_name") or f"{post['entry_name']} (official blog)"


# ─── Ledger / reports ─────────────────────────────────────────────────────────

def load_ledger(window_hours):
    led = load_json_file(STATE_PATH, {})
    if not led.get("watermark"):
        led["watermark"] = (datetime.now(timezone.utc)
                            - timedelta(hours=window_hours)).isoformat()
        led["seen_ids"] = []
        led["drafted_ids"] = []
    return led


def save_ledger(led):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(led, f, indent=2)


def pacific_date_str(now=None):
    """Pilot digests are dated by the Pacific day (Kiran reads in PT)."""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("America/Los_Angeles")
    except Exception:
        tz = timezone(timedelta(hours=-7))  # PDT fallback
    return (now or datetime.now(timezone.utc)).astimezone(tz).strftime("%Y-%m-%d")


def write_reports(report):
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    jpath = os.path.join(REPORT_DIR, f"watchlist-report-{stamp}.json")
    mpath = os.path.join(REPORT_DIR, f"watchlist-report-{stamp}.md")
    with open(jpath, "w") as f:
        json.dump(report, f, indent=2, default=str)
    lines = [
        f"# Watchlist pilot — {report.get('mode', 'dry-run')} report {report['run_at']}",
        "",
        f"- Posts detected (new, in window): **{report['scanned']}**; scored: "
        f"**{report.get('scored', report['scanned'])}** "
        f"(X {report['by_platform'].get('x', 0)}, IG {report['by_platform'].get('ig', 0)}, "
        f"RSS {report['by_platform'].get('rss', 0)} of the scored set)",
        f"- Passed strict scoring (≥{report['threshold']}, news type): **{report['passed_scoring']}**",
        f"- Outcome (a) corroborated, NOT yet published → draftable: **{len(report['outcome_a'])}**",
        f"- Outcome (b) corroborated but ALREADY published (duplicate-of-ingest): **{len(report['outcome_b'])}**",
        f"- Outcome (c) passed scoring, NO corroboration → held: **{len(report['outcome_c'])}**",
        f"- Estimated GPT-4o-mini spend this run: **${report['cost_usd']:.4f}**",
        "",
        "## Top candidates",
    ]
    for c in report["top_candidates"]:
        lines.append(f"- [{c['outcome']}] {c['entry']} ({c['platform']}, score {c['score']}, "
                     f"{c['type']}) — {c['summary']}")
        if c.get("corroboration"):
            lines.append(f"  - corroborated by: {c['corroboration']}")
        if c.get("published_match"):
            lines.append(f"  - already published as: {c['published_match']}")
    lines += ["", "## Per-entry scan counts"]
    for name, n in sorted(report["per_entry_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"- {name}: {n}")
    lines += ["", "## Honesty notes", *[f"- {n}" for n in report["notes"]]]
    with open(mpath, "w") as f:
        f.write("\n".join(lines) + "\n")
    return jpath, mpath


# ─── Pipeline driver ──────────────────────────────────────────────────────────

def run_pipeline(args):
    load_env("~/workspace/.env.supabase", "~/workspace/.env.openai",
             "~/workspace/.env.twitterapi-io")
    cfg = load_config()
    threshold = int(cfg.get("pilot", {}).get("score_threshold", SCORE_THRESHOLD_DEFAULT))
    window = args.hours or int(cfg.get("pilot", {}).get("window_hours", 72))
    cache = load_json_file(CACHE_PATH, {"x": {}, "ig": {}})
    led = load_ledger(window)
    watermark = parse_post_time(led["watermark"], "x")
    seen = set(led.get("seen_ids", [])) | set(led.get("drafted_ids", []))

    mode_label = ("DRAFT-ALL" if args.draft_all
                  else "DRAFT" if args.draft else "DRY RUN")
    print(f"═══ Watchlist pilot — {mode_label} ═══")
    print(f"Window {window}h · watermark {led['watermark']} · threshold {threshold}")
    posts, counts = detect_posts(cfg, cache, refresh=not args.no_refresh,
                                 window_hours=window)
    print(f"Detected {len(posts)} posts in window across "
          f"{sum(1 for v in counts.values() if v)} entries")
    posts = [p for p in posts if is_new_post(p, watermark, seen)]
    posts = dedupe_candidates(posts)
    scanned_total = len(posts)
    print(f"New after watermark/dedup: {scanned_total}")
    cap = args.max_scored or MAX_POSTS_SCORED
    if len(posts) > cap:
        print(f"  ⚠ capping scoring at {cap} newest (cost discipline); "
              f"{len(posts) - cap} unscored")
        posts = posts[:cap]

    scores, cost = score_posts(posts)
    print(f"Scored {len(scores)} posts · GPT cost so far ${cost:.4f}")
    passed = []
    for p in posts:
        res = scores.get(f"{p['platform']}:{p['id']}")
        if passes_score_gate(res, threshold):
            passed.append((p, res))
    passed.sort(key=lambda pr: (pr[1]["score"], pr[0]["created_at_dt"]), reverse=True)
    print(f"Passed strict gate: {len(passed)}")

    outcome_a, outcome_b, outcome_c = [], [], []
    for p, res in passed:
        c = corroborate(p, res)
        rec = {"post": p, "scored": res, "corr": c}
        if c["outcome"] == "draft":
            outcome_a.append(rec)
        elif c["outcome"] == "duplicate":
            outcome_b.append(rec)
        else:
            outcome_c.append(rec)
        print(f"  [{c['outcome']:>9}] {p['entry_name']} ({p['platform']}) "
              f"{res['score']:.0f} {res['type']} — {res['summary'][:80]}")

    report = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "mode": ("draft-all" if args.draft_all
                 else "draft" if args.draft else "dry-run"),
        "scanned": scanned_total,
        "scored": len(posts),
        "by_platform": {pf: sum(1 for p in posts if p["platform"] == pf)
                        for pf in ("x", "ig", "rss")},
        "by_lane": {ln: sum(1 for p in posts if p.get("lane") == ln)
                    for ln in ("A", "B")},
        "passed_scoring": len(passed),
        "threshold": threshold,
        "cost_usd": cost,
        "per_entry_counts": counts,
        "outcome_a": [_cand_rec(r) for r in outcome_a],
        "outcome_b": [_cand_rec(r) for r in outcome_b],
        "outcome_c": [_cand_rec(r) for r in outcome_c],
        "top_candidates": [_cand_rec(r) for r in (outcome_a + outcome_b + outcome_c)[:12]],
        "notes": [
            "Corroboration is keyword/entity matching over p2_signals + p2_topics + "
            "published headlines, fetched by targeted ilike queries on the scorer's "
            "top entities. A corroborating story that names none of those entities "
            "will be missed (held, not drafted) — the failure direction is safe.",
            "p2_signals rows are ingest titles (often Google News cluster titles); "
            "the matched signal's original_url becomes source #2.",
            "Two watchlist entries posting about the same event are NOT treated as "
            "corroboration for each other unless one independently matches coverage "
            "in signals/topics (self-source exclusion is per-entry).",
            "Already-published dedup uses a STRICTER match than corroboration "
            "(>=4 shared tokens AND >=30% coverage of the smaller token set): a "
            "shared person name across different stories must not suppress a true "
            "add. Corroboration stays looser because a human reviews every draft "
            "and both sources are printed in it.",
            "X cache on disk dates from 2026-10-05; detection therefore live-"
            "refreshes watchlist handles only (TwitterAPI.io + Meta connector). "
            "Use --no-refresh for a cache-only run.",
        ],
    }

    sample_info = None
    if args.draft:
        sample_info, cost = _do_draft(outcome_a, outcome_b, led, cost)
        report["cost_usd"] = cost
        report["sample"] = sample_info

    digest = None
    if args.draft_all:
        counts = {"scanned": scanned_total, "scored": len(posts),
                  "passed": len(passed)}
        digest, cost, deferred_recs = _do_draft_all(
            outcome_a, outcome_b, outcome_c, led, cost, counts,
            cap=args.draft_cap or DRAFT_ALL_CAP)
        report["cost_usd"] = cost
        report["digest"] = digest
        report["draft_all"] = {
            "drafts_written": len(digest["drafts"]),
            "deferred": [_cand_rec(r) for r in deferred_recs],
        }
        # Draft files are already on disk and drafted_ids already saved —
        # only NOW consume the rest of the batch, so a crash mid-drafting
        # loses nothing (undrafted posts stay new and are retried).
        args.commit_ledger = True

    if args.commit_ledger:
        led["seen_ids"] = sorted(seen | {f"{p['platform']}:{p['id']}" for p in posts})
        save_ledger(led)
        print("Ledger updated (detected posts marked seen).")

    jpath, mpath = write_reports(report)
    print(f"\nReports: {jpath}\n         {mpath}")
    print(f"Outcomes: (a) draftable {len(outcome_a)} · (b) duplicates "
          f"{len(outcome_b)} · (c) held {len(outcome_c)} · total cost ${report['cost_usd']:.4f}")
    if digest is not None:
        print(f"\nDaily digest (also in pipeline/.state/"
              f"watchlist-digest-{digest['date'].replace('-', '')}.json):")
        print(json.dumps(digest, indent=2))
    return report


def _cand_rec(rec):
    p, res, c = rec["post"], rec["scored"], rec["corr"]
    return {
        "entry": p["entry_name"], "lane": p.get("lane", ""),
        "platform": p["platform"], "handle": p.get("handle", ""),
        "url": p["url"], "created_at": p["created_at_dt"].isoformat(),
        "score": res["score"], "type": res["type"], "summary": res["summary"],
        "category": res.get("category", ""),
        "outcome": c["outcome"],
        "corroboration": (f"{c['corroboration'].get('source_name', '')}: "
                          f"{c['corroboration'].get('title', '')[:90]}"
                          if c.get("corroboration") else None),
        "published_match": (c["published_match"].get("title", "")[:90]
                            if c.get("published_match") else None),
    }


def fetch_url_text(url, max_chars=2600):
    """Fetch a corroborating article's readable text via curl (the V3
    writer standard is to write from sources actually read, not just
    headlines). Returns '' on any failure — synthesis then falls back to
    the signal's own description."""
    if not url or "news.google.com" in url:
        return ""
    cmd = ["curl", "-sS", "-L", "--max-time", "20",
           "-A", "Mozilla/5.0 (X11; Linux x86_64) TheVideshi/1.0", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    except Exception:
        return ""
    if r.returncode != 0 or not r.stdout:
        return ""
    text = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", r.stdout)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    # Crude readability trim: start at the first long sentence-ish chunk.
    return text[:max_chars] if len(text) > 200 else ""


def _do_draft(outcome_a, outcome_b, led, cost):
    """Draft ONE sample article. Preference order: (a) a true-add
    candidate; else (b) a duplicate — file-only and loudly labelled,
    purely so the synthesis quality can be judged; in production (b) is
    skipped. Nothing is inserted: process_article hardcodes
    status='published', so the validated article JSON is written to
    SAMPLE_PATH for Kiran's review."""
    pool, label = outcome_a, "true-add (corroborated, not yet published)"
    if not pool:
        pool, label = outcome_b, ("SAMPLE-ONLY from a duplicate-of-ingest candidate — "
                                  "in production this is skipped, never drafted")
    if not pool:
        print("No draftable candidate this run (all held at the evidence gate).")
        return {"status": "none",
                "reason": "no candidate passed scoring + corroboration"}, cost
    rec = pool[0]
    p, res, c = rec["post"], rec["scored"], rec["corr"]
    corr_item = c.get("corroboration")
    if c["outcome"] == "duplicate":
        # For the quality sample, re-run corroboration ignoring the
        # published match so a real source #2 is attached.
        corr_item = None
        toks, phrases = candidate_keywords(p["text"], res.get("entities", []))
        kws = sorted(toks, key=len, reverse=True)[:4]
        hit = match_corroboration(toks, phrases, _signal_items(kws),
                                  {p.get("handle", ""), p["entry_name"], p["url"]})
        if hit:
            corr_item = hit[0]
    if not corr_item:
        print("Top candidate has no sourceable corroboration — no draft (evidence gate).")
        return {"status": "none",
                "reason": "top candidate lacked a sourceable corroboration"}, cost

    # Read the corroborating article itself where reachable — the sample
    # should be written from material actually read, per the writer
    # standard, not from a headline alone.
    fetched = fetch_url_text(corr_item.get("url", ""))
    if fetched and len(fetched) > len(corr_item.get("extra_text") or ""):
        corr_item = dict(corr_item, extra_text=fetched)
        print(f"  Corroboration text fetched ({len(fetched)} chars) from "
              f"{corr_item.get('source_name', '')}")

    name_attr = f"@{p['handle']}" if p.get("handle") else p.get("feed_name", "")
    writer, wcost, err = synthesize(p, res, corr_item, name_attr)
    cost += wcost
    if writer and len(writer.get("paragraphs") or []) < 3 and not err:
        writer2, wcost2, err2 = synthesize(p, res, corr_item, name_attr)
        cost += wcost2
        if writer2 and len(writer2.get("paragraphs") or []) > len(writer.get("paragraphs") or []):
            writer = writer2
    if err or not writer:
        print(f"  ⚠ synthesis failed: {err}")
        return {"status": "error", "reason": str(err)}, cost
    article = build_sample_article(p, res, corr_item, writer)
    if article is None:
        print("  ⚠ assembled article failed the ≥2-source gate — not written.")
        return {"status": "error", "reason": "source gate rejected assembly"}, cost

    # Slug collision check against the live corpus.
    existing = sb_get(f"p2_articles?select=id&slug=eq.{article['slug']}&limit=1")
    if existing:
        article["slug"] = article["slug"] + "-watchlist"

    payload = {
        "status": "DRAFT — not inserted",
        "why_not_inserted": (
            "v3-batch-insert.process_article hardcodes status='published'. "
            "This validated article dict is ready to pass to process_article "
            "once the pilot is approved; for the pilot it is held in this "
            "file per the no-live-publishing rule."),
        "basis": label,
        "candidate": _cand_rec(rec),
        "article": article,
    }
    os.makedirs(os.path.dirname(SAMPLE_PATH), exist_ok=True)
    with open(SAMPLE_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    led["drafted_ids"] = sorted(set(led.get("drafted_ids", []))
                                | {f"{p['platform']}:{p['id']}"})
    save_ledger(led)
    print(f"Sample draft written: {SAMPLE_PATH}")
    print(f"  Headline: {article['headline']}")
    print(f"  Slug: {article['slug']} · category {article['category']} · "
          f"sources: {[s['name'] for s in article['sources']]}")
    return {"status": "written", "path": SAMPLE_PATH, "basis": label,
            "headline": article["headline"], "slug": article["slug"],
            "category": article["category"],
            "sources": article["sources"]}, cost


# ─── Draft-all (daily pilot mode) ─────────────────────────────────────────────
# Kiran approved the 1-week pilot in DRAFT mode (2026-10-24): every
# outcome-(a) candidate becomes a draft FILE in .state/watchlist-drafts/.
# Nothing is ever inserted — v3-batch-insert.process_article hardcodes
# status='published', so pilot drafts stay files exactly like the sample.
#
# Crash-safety order (deliberate): draft files are written FIRST, then
# drafted post IDs are persisted to the ledger, then (in run_pipeline)
# the rest of the batch is marked seen. A crash can therefore at worst
# re-draft a post on the next run (slug suffixing keeps files distinct);
# it can never consume a post whose draft was never written.

def select_draft_batch(outcome_a, cap=DRAFT_ALL_CAP):
    """(batch, deferred): outcome-(a) records ordered highest score
    first (ties: newest post first), split at the daily cap. Deferred
    candidates are NOT carried over — they are consumed with the batch
    and age out."""
    ordered = sorted(outcome_a,
                     key=lambda r: (r["scored"].get("score", 0),
                                    r["post"]["created_at_dt"]),
                     reverse=True)
    return ordered[:cap], ordered[cap:]


def build_digest(date_str, scanned, scored, passed, drafts, duplicates,
                 held, deferred_count, est_cost_usd):
    """The daily digest relayed to Kiran by the cron worker. Field names
    are a stable contract — do not rename."""
    return {
        "date": date_str,
        "scanned": scanned,
        "scored": scored,
        "passed": passed,
        "drafts": drafts,
        "duplicates": duplicates,
        "held": held,
        "deferred_count": deferred_count,
        "est_cost_usd": round(est_cost_usd, 4),
    }


def _draft_one(rec, used_slugs, drafts_dir):
    """Synthesize + validate + write ONE draft file for an outcome-(a)
    record, using the same checks as the single --draft path
    (corroboration actually read, build_sample_article's ≥2-source
    evidence gate, corpus slug-collision check). Returns
    (article, added_cost, error_reason)."""
    p, res, c = rec["post"], rec["scored"], rec["corr"]
    corr_item = c.get("corroboration")
    if not corr_item or not corr_item.get("url"):
        return None, 0.0, "no sourceable corroboration (evidence gate)"

    fetched = fetch_url_text(corr_item.get("url", ""))
    if fetched and len(fetched) > len(corr_item.get("extra_text") or ""):
        corr_item = dict(corr_item, extra_text=fetched)

    name_attr = f"@{p['handle']}" if p.get("handle") else p.get("feed_name", "")
    writer, cost, err = synthesize(p, res, corr_item, name_attr)
    if writer and len(writer.get("paragraphs") or []) < 3 and not err:
        writer2, cost2, err2 = synthesize(p, res, corr_item, name_attr)
        cost += cost2
        if writer2 and len(writer2.get("paragraphs") or []) > len(writer.get("paragraphs") or []):
            writer = writer2
    if err or not writer:
        return None, cost, f"synthesis failed: {err}"
    article = build_sample_article(p, res, corr_item, writer)
    if article is None:
        return None, cost, "assembled article failed the ≥2-source gate"

    slug = article["slug"]
    existing = sb_get(f"p2_articles?select=id&slug=eq.{slug}&limit=1")
    if existing:
        slug = slug + "-watchlist"
    base, n = slug, 2
    while slug in used_slugs or os.path.exists(os.path.join(drafts_dir, slug + ".json")):
        slug = f"{base}-{n}"
        n += 1
    article["slug"] = slug
    used_slugs.add(slug)

    payload = {
        "status": "DRAFT — not inserted",
        "why_not_inserted": (
            "v3-batch-insert.process_article hardcodes status='published'. "
            "Watchlist pilot drafts stay files for Kiran's review during "
            "the pilot week (2026-10-25 → 2026-10-31)."),
        "basis": "true-add (corroborated, not yet published) — pilot draft-all",
        "candidate": _cand_rec(rec),
        "article": article,
    }
    os.makedirs(drafts_dir, exist_ok=True)
    with open(os.path.join(drafts_dir, slug + ".json"), "w") as f:
        json.dump(payload, f, indent=2)
    return article, cost, None


def run_draft_all(outcome_a, outcome_b, outcome_c, led, counts,
                  cap=DRAFT_ALL_CAP, drafts_dir=DRAFTS_DIR,
                  digest_dir=REPORT_DIR, persist=None, date_str=None,
                  base_cost=0.0):
    """Draft every outcome-(a) candidate up to the daily cap and build
    the daily digest. Only (a) records are drafted — duplicates (b) and
    held (c) are reported, never written (the evidence gate). Returns
    (digest, total_cost, deferred_records)."""
    batch, deferred = select_draft_batch(outcome_a, cap)
    used_slugs, drafted_keys, drafts_meta = set(), [], []
    added_cost = 0.0
    for rec in batch:
        article, dcost, err = _draft_one(rec, used_slugs, drafts_dir)
        added_cost += dcost
        p, res = rec["post"], rec["scored"]
        if article is None:
            print(f"  ⚠ draft-all: skipped {p['entry_name']} "
                  f"({p['platform']}) — {err}")
            continue
        corr = rec["corr"].get("corroboration") or {}
        drafts_meta.append({
            "headline": article["headline"],
            "slug": article["slug"],
            "score": res["score"],
            "handle": p.get("handle", ""),
            "platform": p["platform"],
            "corroboration_source_name": corr.get("source_name", ""),
            "why": res.get("summary", ""),
        })
        drafted_keys.append(f"{p['platform']}:{p['id']}")
        print(f"  ✎ drafted: {article['headline']} "
              f"(.state/watchlist-drafts/{article['slug']}.json)")

    # Files are on disk BEFORE the ledger moves — see the ordering note
    # at the top of this section.
    if persist is not None and drafted_keys:
        led["drafted_ids"] = sorted(set(led.get("drafted_ids", []))
                                    | set(drafted_keys))
        persist(led)

    duplicates = [{
        "headline_or_post": r["scored"].get("summary", ""),
        "matched_article": (r["corr"].get("published_match") or {}).get("title", ""),
    } for r in outcome_b]
    held = []
    for r in outcome_c:
        p = r["post"]
        reason = ("coverage exists only as a topic match with no "
                  "sourceable article"
                  if r["corr"].get("topic_only_match")
                  else "no independent corroboration found")
        held.append({"handle": p.get("handle") or p["entry_name"],
                     "reason": reason})

    digest = build_digest(date_str or pacific_date_str(),
                          counts.get("scanned", 0), counts.get("scored", 0),
                          counts.get("passed", 0), drafts_meta, duplicates,
                          held, len(deferred), base_cost + added_cost)
    if digest_dir:
        os.makedirs(digest_dir, exist_ok=True)
        dpath = os.path.join(
            digest_dir,
            f"watchlist-digest-{digest['date'].replace('-', '')}.json")
        with open(dpath, "w") as f:
            json.dump(digest, f, indent=2)
    return digest, base_cost + added_cost, deferred


def _do_draft_all(outcome_a, outcome_b, outcome_c, led, cost, counts, cap):
    digest, total_cost, deferred = run_draft_all(
        outcome_a, outcome_b, outcome_c, led, counts, cap=cap,
        persist=save_ledger, base_cost=cost)
    print(f"Draft-all: {len(digest['drafts'])} draft(s) written to "
          f"pipeline/.state/watchlist-drafts/ · "
          f"{digest['deferred_count']} deferred past the cap of {cap}")
    return digest, total_cost, deferred


def main():
    ap = argparse.ArgumentParser(description="Watchlist synthesis pilot")
    ap.add_argument("--dry-run", action="store_true", help="detect + score + corroborate, report only")
    ap.add_argument("--draft", action="store_true", help="also synthesize ONE sample draft (file only)")
    ap.add_argument("--draft-all", action="store_true",
                    help="daily pilot mode: draft EVERY outcome-(a) candidate "
                         "(cap --draft-cap) to .state/watchlist-drafts/, write + "
                         "print the daily digest, consume the batch in the ledger")
    ap.add_argument("--draft-cap", type=int, default=0,
                    help="max drafts per --draft-all run (default 6)")
    ap.add_argument("--no-refresh", action="store_true", help="cache-only detection (no live top-up)")
    ap.add_argument("--hours", type=int, default=0, help="detection window override")
    ap.add_argument("--max-scored", type=int, default=0,
                    help="cap on posts sent to the scorer (default 60)")
    ap.add_argument("--commit-ledger", action="store_true", help="mark detected posts seen in the ledger")
    args = ap.parse_args()
    if not (args.dry_run or args.draft or args.draft_all):
        ap.error("one of --dry-run / --draft / --draft-all is required")
    run_pipeline(args)


if __name__ == "__main__":
    main()
