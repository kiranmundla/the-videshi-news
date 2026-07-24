#!/usr/bin/env python3
"""
media-library-enqueue.py — the FRESHNESS LOOP (Kiran's directive).

Reads recent articles from Supabase (p2_articles), extracts subjects
(persons / places / things-orgs / events) and keywords, and enqueues any
subject not already well-covered in the media_library into
pipeline/media-library-queue.json. The sourcing cron then fills them.

Extraction approach (lightweight, no LLM round-trip):
  1. tags column            → keyword subjects (subject_type guessed)
  2. registry person match  → social-embed-registry.json + pulse-leaders.json
                              names found in headline/body  → subject_type=person
  3. PLACES gazetteer match → known Indian/diaspora cities/states/countries
                              → subject_type=place
  4. capitalized noun-phrase fallback in headline → subject_type=thing
  5. image_entities / image_search_query columns when present

New articles → new subjects/keywords → queue grows → sourcing fills it.

Run:
    python3 media-library-enqueue.py                # last 24h published
    python3 media-library-enqueue.py --hours 72
    python3 media-library-enqueue.py --limit 40
"""

import os, re, sys, json, argparse
from datetime import datetime, timezone, timedelta
import requests
import media_library_store as store

PIPELINE_DIR = store.PIPELINE_DIR
REGISTRY = os.path.join(PIPELINE_DIR, "social-embed-registry.json")
PULSE = os.path.join(PIPELINE_DIR, "pulse-leaders.json")

SUPABASE_URL = store.SUPABASE_URL
HEADERS = store.sb_headers()

# Small gazetteer of places relevant to Videshi coverage (India + diaspora hubs).
PLACES = {
    "india", "mumbai", "delhi", "new delhi", "bengaluru", "bangalore", "chennai",
    "kolkata", "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow", "kochi",
    "goa", "kerala", "punjab", "gujarat", "maharashtra", "tamil nadu", "karnataka",
    "uttar pradesh", "west bengal", "rajasthan", "telangana", "andhra pradesh",
    "varanasi", "amritsar", "agra", "surat", "nagpur", "indore", "chandigarh",
    "united states", "usa", "new york", "new jersey", "california", "san francisco",
    "silicon valley", "texas", "houston", "dallas", "chicago", "seattle", "boston",
    "canada", "toronto", "vancouver", "brampton", "united kingdom", "uk", "london",
    "australia", "sydney", "melbourne", "dubai", "uae", "abu dhabi", "singapore",
}

# Words that look capitalized but aren't useful subjects
STOP_CAPS = {"the", "a", "an", "after", "why", "how", "this", "that", "india's",
             "america's", "just", "its", "for", "and", "but", "with", "from"}


def load_registry_names():
    names = []
    try:
        data = json.load(open(REGISTRY))
        for cat, entries in data.items():
            if cat.startswith("_") or not isinstance(entries, dict):
                continue
            for grp in ("persons", "organizations"):
                for e in entries.get(grp, []):
                    if e.get("name"):
                        st = "person" if grp == "persons" else "thing"
                        names.append((e["name"], st))
    except Exception as e:
        print(f"  ⚠ registry load: {e}")
    try:
        pulse = json.load(open(PULSE))
        for p in pulse:
            if p.get("name"):
                names.append((p["name"], "person"))
    except Exception:
        pass
    # dedup by lowercase name
    seen, out = set(), []
    for n, st in names:
        k = n.lower()
        if k not in seen:
            seen.add(k)
            out.append((n, st))
    return out


def fetch_articles(hours, limit):
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = (f"{SUPABASE_URL}/rest/v1/p2_articles"
           f"?select=id,headline,subheadline,body,category,tags,image_entities,image_search_query"
           f"&status=eq.published&published_at=gte.{since}"
           f"&order=published_at.desc&limit={limit}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ⚠ article fetch: {e}")
        return []


def extract_subjects(article, registry_names):
    """Return list of (subject, subject_type, source_tag)."""
    found = {}  # lower -> (subject, subject_type)
    head = article.get("headline", "") or ""
    sub = article.get("subheadline", "") or ""
    body = (article.get("body", "") or "")[:4000]
    text = f"{head} {sub} {body}"
    text_l = text.lower()

    def add(subj, st):
        k = subj.lower().strip()
        if len(k) < 3:
            return
        if k not in found:
            found[k] = (subj.strip(), st)

    # 1) registry persons/orgs mentioned
    for name, st in registry_names:
        if name.lower() in text_l:
            add(name, st)

    # 2) places gazetteer
    for place in PLACES:
        if re.search(r"\b" + re.escape(place) + r"\b", text_l):
            # canonicalize a few
            canon = {"usa": "United States", "uk": "United Kingdom", "uae": "United Arab Emirates",
                     "bangalore": "Bengaluru"}.get(place, place.title())
            add(canon, "place")

    # 3) tags column → things/concepts
    for t in (article.get("tags") or []):
        t = str(t).replace("-", " ").strip()
        if t and t.lower() not in PLACES:
            add(t, "thing")

    # 4) image_entities / image_search_query when present
    ie = article.get("image_entities")
    if isinstance(ie, list):
        for e in ie:
            if isinstance(e, str) and e.strip():
                add(e.strip(), "thing")
    isq = article.get("image_search_query")
    if isinstance(isq, str) and isq.strip():
        add(isq.strip(), "concept")

    # 5) capitalized multi-word noun phrases — DISABLED.
    # Videshi headlines are title-cased, so this heuristic grabs sentence
    # fragments ("Alpha Has Arrived", "Win It") rather than real subjects.
    # Registry-name + places + tags + image_entities are the reliable signals.

    return [(subj, st, "article") for subj, st in found.values()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--min-coverage", type=int, default=1,
                    help="skip subjects already having >= this many image assets")
    args = ap.parse_args()

    registry_names = load_registry_names()
    print(f"Loaded {len(registry_names)} registry/pulse names.")
    articles = fetch_articles(args.hours, args.limit)
    print(f"Scanning {len(articles)} recent articles (last {args.hours}h).")

    # existing queue
    if os.path.exists(store.QUEUE_PATH):
        q = json.load(open(store.QUEUE_PATH))
    else:
        q = {"_description": "Article-driven subject queue for media-library-source.py. "
                             "Grown by media-library-enqueue.py as new articles publish.",
             "queue": []}
    existing = {it["subject"].lower(): it for it in q.get("queue", [])}

    added, skipped_covered = 0, 0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for a in articles:
        subs = extract_subjects(a, registry_names)
        for subj, st, srctag in subs:
            key = subj.lower()
            # already covered in library?
            if store.coverage_count(subj, "image") >= args.min_coverage:
                skipped_covered += 1
                continue
            if key in existing:
                # bump priority / refresh article ref
                existing[key]["priority"] = existing[key].get("priority", 1) + 1
                continue
            # priority: persons + places rank above generic things/concepts
            prio = {"person": 5, "place": 4, "event": 4, "thing": 2, "concept": 1}.get(st, 2)
            existing[key] = {
                "subject": subj, "subject_type": st,
                "tags": [subj.lower()],
                "first_seen": now, "article_id": a.get("id"),
                "priority": prio,
            }
            added += 1

    q["queue"] = list(existing.values())
    q["_updated"] = now
    tmp = store.QUEUE_PATH + ".tmp"
    json.dump(q, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, store.QUEUE_PATH)

    print(f"\n── Enqueue done. Added {added} new subjects, "
          f"{skipped_covered} already covered. Queue now {len(q['queue'])} subjects.")
    # show top of queue
    top = sorted(q["queue"], key=lambda x: -x.get("priority", 0))[:12]
    for it in top:
        print(f"   [{it.get('priority')}] {it['subject']} ({it['subject_type']})")


if __name__ == "__main__":
    main()
