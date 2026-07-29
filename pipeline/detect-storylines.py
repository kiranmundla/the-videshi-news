#!/usr/bin/env python3
"""
Developing Stories — auto-detect storylines from recent articles.

Groups articles covering the same ongoing event/narrative (NEET protests,
diplomatic incidents, cricket series) into storylines. Manages lifecycle:
  emerging (2 articles) → active (3+) → cooling (5d quiet) → resolved (14d quiet)

Usage:
  python3 pipeline/detect-storylines.py               # normal run
  python3 pipeline/detect-storylines.py --backfill     # seed from last 14 days
  python3 pipeline/detect-storylines.py --dry-run      # preview only
"""
import os, sys, json, subprocess, time, re, argparse
from datetime import datetime, timedelta, timezone

# ── Config ────────────────────────────────────────────────────────────────────
SUPABASE_URL  = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY    = os.environ.get("OPENAI_API_KEY", "")

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

LOOKBACK_DAYS       = 14
ACTIVE_THRESHOLD    = 3       # articles needed to go from emerging → active
COOLING_DAYS        = 5       # no new article → cooling
RESOLVED_DAYS       = 14      # no new article → resolved
BATCH_SIZE          = 8       # articles per LLM call for classification
MAX_ARTICLES        = 300     # safety cap on articles to process

# ── Helpers ───────────────────────────────────────────────────────────────────

def sb_get(path, params=""):
    """GET from Supabase REST API via curl."""
    url = f"{SUPABASE_URL}/rest/v1/{path}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{path}"
    cmd = ["curl", "-sS", "--max-time", "30", url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    if r.returncode != 0:
        print(f"  ⚠️  GET {path} failed: rc={r.returncode}")
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"  ⚠️  GET {path} bad JSON: {r.stdout[:200]}")
        return []


def sb_post(path, data):
    """POST to Supabase REST API via curl. Returns response data."""
    import tempfile
    payload = json.dumps(data)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        cmd = ["curl", "-sS", "--max-time", "30",
               "-X", "POST", f"{SUPABASE_URL}/rest/v1/{path}",
               "-H", f"apikey: {SUPABASE_KEY}",
               "-H", f"Authorization: Bearer {SUPABASE_KEY}",
               "-H", "Content-Type: application/json",
               "-H", "Prefer: return=representation",
               "-d", f"@{tmp_path}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        os.unlink(tmp_path)
        if r.returncode != 0:
            print(f"  ⚠️  POST {path} failed: rc={r.returncode}")
            return None
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            print(f"  ⚠️  POST {path} bad JSON: {r.stdout[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠️  POST {path} error: {e}")
        return None


def sb_delete(path, params=""):
    """DELETE from Supabase REST API via curl."""
    url = f"{SUPABASE_URL}/rest/v1/{path}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{path}"
    cmd = ["curl", "-sS", "--max-time", "30",
           "-X", "DELETE", url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    return r.returncode == 0


def sb_patch(path, data, params=""):
    """PATCH Supabase REST API via curl."""
    import tempfile
    payload = json.dumps(data)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        url = f"{SUPABASE_URL}/rest/v1/{path}?{params}" if params else f"{SUPABASE_URL}/rest/v1/{path}"
        cmd = ["curl", "-sS", "--max-time", "30",
               "-X", "PATCH", url,
               "-H", f"apikey: {SUPABASE_KEY}",
               "-H", f"Authorization: Bearer {SUPABASE_KEY}",
               "-H", "Content-Type: application/json",
               "-H", "Prefer: return=minimal",
               "-d", f"@{tmp_path}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        os.unlink(tmp_path)
        return r.returncode == 0
    except Exception as e:
        print(f"  ⚠️  PATCH {path} error: {e}")
        return False


def slugify(text):
    """Convert text to a URL-safe slug."""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s[:80]


def llm_call(messages, label="LLM", timeout=60):
    """Call OpenAI GPT-4o-mini via curl. Returns (parsed_json, error_string)."""
    if not OPENAI_KEY:
        return None, "No OPENAI_API_KEY"

    import tempfile
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": 2000,
    })
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name

    try:
        cmd = [
            "curl", "-sS", "--max-time", str(timeout),
            "-X", "POST", "https://api.openai.com/v1/chat/completions",
            "-H", f"Authorization: Bearer {OPENAI_KEY}",
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        os.unlink(tmp_path)
        if r.returncode != 0:
            return None, f"curl error (rc={r.returncode})"

        data = json.loads(r.stdout)
        if "error" in data:
            return None, data["error"].get("message", str(data["error"]))

        content_str = data["choices"][0]["message"]["content"]
        content = json.loads(content_str)
        usage = data.get("usage", {})
        tokens = usage.get("total_tokens", 0)
        if tokens:
            cost = tokens * 0.00000015  # gpt-4o-mini input ~$0.15/M, output ~$0.60/M, avg ~$0.15/M
            print(f"    💰 {label}: {tokens} tokens (~${cost:.4f})")
        return content, None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"
    except Exception as e:
        return None, f"Error: {e}"


# ── Core Logic ────────────────────────────────────────────────────────────────

def fetch_recent_articles(days=LOOKBACK_DAYS, limit=MAX_ARTICLES):
    """Fetch published articles from the last N days."""
    from urllib.parse import quote
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    cutoff_encoded = quote(cutoff, safe='')
    params = (
        f"select=id,headline,slug,category,published_at,image_url"
        f"&status=eq.published"
        f"&published_at=gte.{cutoff_encoded}"
        f"&order=published_at.desc"
        f"&limit={limit}"
    )
    articles = sb_get("p2_articles", params)
    if isinstance(articles, dict) and "message" in articles:
        print(f"  ⚠️  Error fetching articles: {articles}")
        return []
    return articles or []


def fetch_storylines(statuses=("emerging", "active", "cooling")):
    """Fetch storylines with given statuses."""
    status_filter = ",".join(statuses)
    params = f"select=*&status=in.({status_filter})&order=last_article_at.desc"
    result = sb_get("storylines", params)
    if isinstance(result, dict) and "message" in result:
        print(f"  ⚠️  Error fetching storylines: {result}")
        return []
    return result or []


def fetch_storyline_article_ids():
    """Fetch all article IDs that are already linked to any storyline."""
    params = "select=article_id"
    result = sb_get("storyline_articles", params)
    if isinstance(result, list):
        return {r["article_id"] for r in result}
    return set()


def fetch_storyline_headlines(storyline_id, limit=5):
    """Fetch recent article headlines for a given storyline."""
    params = (
        f"select=article_id,p2_articles(headline,published_at)"
        f"&storyline_id=eq.{storyline_id}"
        f"&order=added_at.desc"
        f"&limit={limit}"
    )
    result = sb_get("storyline_articles", params)
    if isinstance(result, list):
        return [r.get("p2_articles", {}).get("headline", "") for r in result if r.get("p2_articles")]
    return []


def classify_articles(articles, storylines, storyline_headlines_map):
    """Classify a batch of articles: match to existing storyline, new storyline, or none."""

    # Build storyline context for the LLM
    storyline_ctx = []
    for s in storylines:
        headlines = storyline_headlines_map.get(s["id"], [])
        storyline_ctx.append({
            "id": s["id"],
            "title": s["title"],
            "category": s["category"],
            "article_count": s["article_count"],
            "recent_headlines": headlines[:5],
        })

    article_ctx = []
    for a in articles:
        article_ctx.append({
            "id": a["id"],
            "headline": a["headline"],
            "category": a.get("category", ""),
            "published_at": a.get("published_at", ""),
        })

    system_prompt = """You are a news editor identifying developing stories — specific ongoing events or narratives that span multiple articles over days or weeks.

A STORYLINE is a specific ongoing event with a narrative arc:
✅ "NEET paper leak protests" — specific event with escalation, investigation, rulings
✅ "India-Pakistan diplomatic standoff over Kashmir" — specific incident evolving
✅ "IPL 2026 season" — bounded event with multiple developments
✅ "H-1B visa fee increase implementation" — specific policy change playing out
✅ "Trump tariffs on Indian goods" — specific trade action with reactions and consequences

A storyline is NOT:
❌ A broad recurring topic ("tech layoffs", "Bollywood box office", "stock market")
❌ A one-time event that's done ("single earthquake report", "one product launch")
❌ A general theme ("AI advances", "immigration news")

For each article, decide:
1. "match" — it clearly belongs to an existing storyline (same specific event/narrative)
2. "new" — it's part of a new developing story not yet tracked. Provide a concise title and 1-sentence summary.
3. "none" — it's a standalone article or a broad topic, not a developing story

Return JSON:
{
  "classifications": [
    {"article_id": "...", "action": "match", "storyline_id": "..."},
    {"article_id": "...", "action": "new", "title": "...", "summary": "...", "category": "..."},
    {"article_id": "...", "action": "none"}
  ]
}

Be conservative. Only "match" when the article clearly covers the SAME specific event. Only "new" for events that are likely to have multiple developments over days."""

    user_msg = json.dumps({
        "existing_storylines": storyline_ctx,
        "articles_to_classify": article_ctx,
    })

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ]

    result, err = llm_call(messages, label=f"classify {len(articles)} articles")
    if err:
        print(f"    ⚠️  LLM error: {err}")
        return []
    return result.get("classifications", [])


def verify_new_storyline(title, candidate_articles):
    """Verify a proposed new storyline has enough related articles. Returns list of matching article IDs."""
    if len(candidate_articles) < ACTIVE_THRESHOLD:
        return []

    article_list = [{"id": a["id"], "headline": a["headline"]} for a in candidate_articles[:20]]

    messages = [
        {"role": "system", "content": f"""Given the proposed storyline title "{title}", identify which of these articles are clearly about this SAME specific event/narrative. Be strict — only include articles that are genuinely about this story, not tangentially related.

Return JSON: {{"matching_article_ids": ["id1", "id2", ...]}}"""},
        {"role": "user", "content": json.dumps(article_list)},
    ]

    result, err = llm_call(messages, label=f"verify '{title}'")
    if err:
        print(f"    ⚠️  Verify error: {err}")
        return []
    return result.get("matching_article_ids", [])


def create_storyline(title, summary, category, article_ids, articles_by_id, dry_run=False):
    """Create a new storyline and link articles to it."""
    slug = slugify(title)

    # Get dates from linked articles
    dates = []
    for aid in article_ids:
        a = articles_by_id.get(aid, {})
        if a.get("published_at"):
            dates.append(a["published_at"])

    first_at = min(dates) if dates else datetime.now(timezone.utc).isoformat()
    last_at = max(dates) if dates else datetime.now(timezone.utc).isoformat()
    count = len(article_ids)
    status = "active" if count >= ACTIVE_THRESHOLD else "emerging"

    if dry_run:
        print(f"    🏷️  [DRY RUN] Would create storyline: '{title}' ({status}, {count} articles)")
        return None

    # Check if slug already exists
    existing = sb_get("storylines", f"slug=eq.{slug}&select=id")
    if existing and isinstance(existing, list) and len(existing) > 0:
        # Slug collision — append a counter
        slug = f"{slug}-{int(time.time()) % 10000}"

    storyline_data = {
        "title": title,
        "slug": slug,
        "summary": summary,
        "category": category,
        "status": status,
        "article_count": count,
        "first_article_at": first_at,
        "last_article_at": last_at,
    }

    result = sb_post("storylines", storyline_data)
    if not result or not isinstance(result, list) or len(result) == 0:
        print(f"    ⚠️  Failed to create storyline '{title}'")
        return None

    storyline_id = result[0]["id"]
    print(f"    ✅ Created storyline: '{title}' ({status}, {count} articles, id={storyline_id[:8]})")

    # Link articles
    for aid in article_ids:
        sb_post("storyline_articles", {
            "storyline_id": storyline_id,
            "article_id": aid,
        })

    return storyline_id


def link_article_to_storyline(storyline_id, article_id, article, dry_run=False):
    """Link an article to an existing storyline and update counts."""
    if dry_run:
        print(f"    🔗 [DRY RUN] Would link '{article.get('headline', '')[:60]}' to storyline {storyline_id[:8]}")
        return

    sb_post("storyline_articles", {
        "storyline_id": storyline_id,
        "article_id": article_id,
    })

    # Update storyline metadata
    pub_at = article.get("published_at", datetime.now(timezone.utc).isoformat())
    sb_patch("storylines", {
        "article_count": None,  # will be set below
        "last_article_at": pub_at,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",  # any new article reactivates
    }, f"id=eq.{storyline_id}")

    # Recount articles
    linked = sb_get("storyline_articles", f"storyline_id=eq.{storyline_id}&select=id")
    if isinstance(linked, list):
        sb_patch("storylines", {"article_count": len(linked)}, f"id=eq.{storyline_id}")


def merge_similar_storylines(dry_run=False):
    """Find and merge storylines that cover the same event."""
    storylines = fetch_storylines(("emerging", "active"))
    if len(storylines) < 2:
        print("    ℹ️  Fewer than 2 storylines, nothing to merge")
        return 0

    # Build context for LLM
    sl_ctx = []
    for s in storylines:
        sl_ctx.append({
            "id": s["id"],
            "title": s["title"],
            "status": s["status"],
            "article_count": s.get("article_count", 0),
            "category": s.get("category", ""),
        })

    messages = [
        {"role": "system", "content": """You are a news editor reviewing storylines for duplicates.
Two storylines should be MERGED when they cover the SAME specific event or narrative, just described differently.
For example:
- "India Overhauls OCI Rules" + "India Launches Digital e-OCI Card" = SAME event, merge
- "H-1B Visa Freeze Bill" + "House Republicans Propose H-1B Visa Pause" = SAME legislative push, merge
- "Canada Express Entry Draws" + "Canada PGWP Refusal Rate" = DIFFERENT topics, do NOT merge

Only merge when they are clearly the same event. When in doubt, keep them separate.

Return JSON:
{"merge_pairs": [{"keep_id": "id-of-larger-or-better-titled", "remove_id": "id-of-smaller-or-redundant"}]}
Return empty array if no merges needed."""},
        {"role": "user", "content": json.dumps({"storylines": sl_ctx})},
    ]

    result, err = llm_call(messages, label="merge check")
    if err:
        print(f"    ⚠️  Merge LLM error: {err}")
        return 0

    pairs = result.get("merge_pairs", [])
    if not pairs:
        print("    ℹ️  No duplicate storylines found")
        return 0

    merged = 0
    sl_by_id = {s["id"]: s for s in storylines}

    for pair in pairs:
        keep_id = pair.get("keep_id")
        remove_id = pair.get("remove_id")
        if not keep_id or not remove_id:
            continue
        if keep_id not in sl_by_id or remove_id not in sl_by_id:
            continue

        keep = sl_by_id[keep_id]
        remove = sl_by_id[remove_id]

        if dry_run:
            print(f"    🔀 [DRY RUN] Would merge '{remove['title']}' → '{keep['title']}'")
            merged += 1
            continue

        # Reassign articles from remove → keep
        ok = sb_patch(
            "storyline_articles",
            {"storyline_id": keep_id},
            f"storyline_id=eq.{remove_id}"
        )
        if not ok:
            print(f"    ⚠️  Failed to reassign articles from '{remove['title']}'")
            continue

        # Recalculate counts and dates for the kept storyline
        linked = sb_get("storyline_articles",
                        f"storyline_id=eq.{keep_id}&select=article_id,p2_articles(published_at)")
        new_count = len(linked) if isinstance(linked, list) else keep.get("article_count", 0)
        dates = []
        if isinstance(linked, list):
            for r in linked:
                pa = (r.get("p2_articles") or {}).get("published_at")
                if pa:
                    dates.append(pa)

        update_data = {
            "article_count": new_count,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if new_count >= ACTIVE_THRESHOLD:
            update_data["status"] = "active"
        if dates:
            update_data["first_article_at"] = min(dates)
            update_data["last_article_at"] = max(dates)

        # Merge metadata (keep medal_tracker etc from either side)
        keep_meta = keep.get("metadata") or {}
        remove_meta = remove.get("metadata") or {}
        if remove_meta:
            for k, v in remove_meta.items():
                if k not in keep_meta:
                    keep_meta[k] = v
            update_data["metadata"] = keep_meta

        sb_patch("storylines", update_data, f"id=eq.{keep_id}")

        # Delete the empty storyline
        sb_delete("storylines", f"id=eq.{remove_id}")

        print(f"    🔀 Merged '{remove['title']}' → '{keep['title']}' ({new_count} articles)")
        merged += 1

        # Remove from map so we don't double-merge
        del sl_by_id[remove_id]

    return merged


def update_lifecycle(dry_run=False):
    """Update storyline statuses based on last_article_at."""
    now = datetime.now(timezone.utc)
    cooling_cutoff = (now - timedelta(days=COOLING_DAYS)).isoformat()
    resolved_cutoff = (now - timedelta(days=RESOLVED_DAYS)).isoformat()

    # Active/emerging → cooling (no new article for 5 days)
    active = sb_get("storylines", "status=in.(active,emerging)&select=id,title,last_article_at")
    if isinstance(active, list):
        for s in active:
            last = s.get("last_article_at", "")
            if last and last < cooling_cutoff:
                if dry_run:
                    print(f"    ❄️  [DRY RUN] Would cool: '{s['title']}'")
                else:
                    sb_patch("storylines", {"status": "cooling", "updated_at": now.isoformat()}, f"id=eq.{s['id']}")
                    print(f"    ❄️  Cooling: '{s['title']}'")

    # Cooling → resolved (no new article for 14 days)
    cooling = sb_get("storylines", "status=eq.cooling&select=id,title,last_article_at")
    if isinstance(cooling, list):
        for s in cooling:
            last = s.get("last_article_at", "")
            if last and last < resolved_cutoff:
                if dry_run:
                    print(f"    📦 [DRY RUN] Would resolve: '{s['title']}'")
                else:
                    sb_patch("storylines", {"status": "resolved", "updated_at": now.isoformat()}, f"id=eq.{s['id']}")
                    print(f"    📦 Resolved: '{s['title']}'")


def update_summaries(dry_run=False):
    """Re-generate summaries for active storylines that have new articles."""
    active = sb_get("storylines", "status=in.(active,emerging)&select=id,title,summary,article_count")
    if not isinstance(active, list) or not active:
        return

    for s in active:
        headlines = fetch_storyline_headlines(s["id"], limit=8)
        if len(headlines) < 2:
            continue

        messages = [
            {"role": "system", "content": "Write a 1-2 sentence summary of this developing story based on its recent headlines. Be concise and factual. Return JSON: {\"summary\": \"...\"}"},
            {"role": "user", "content": json.dumps({"title": s["title"], "recent_headlines": headlines})},
        ]

        result, err = llm_call(messages, label=f"summary '{s['title'][:30]}'")
        if err or not result:
            continue

        new_summary = result.get("summary", "")
        if new_summary and new_summary != s.get("summary", ""):
            if dry_run:
                print(f"    📝 [DRY RUN] Would update summary for '{s['title']}': {new_summary[:80]}")
            else:
                sb_patch("storylines", {"summary": new_summary, "updated_at": datetime.now(timezone.utc).isoformat()}, f"id=eq.{s['id']}")
                print(f"    📝 Updated summary: '{s['title']}' → {new_summary[:80]}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Detect storylines from recent articles")
    parser.add_argument("--backfill", action="store_true", help="Seed from all articles in the last 14 days")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no DB writes")
    parser.add_argument("--limit", type=int, default=MAX_ARTICLES, help="Max articles to process")
    args = parser.parse_args()

    print("📰 Developing Stories — storyline detection")
    print(f"  Mode: {'backfill' if args.backfill else 'incremental'} {'(dry run)' if args.dry_run else ''}")

    # 1. Fetch recent articles
    articles = fetch_recent_articles(days=LOOKBACK_DAYS, limit=args.limit)
    print(f"  📄 {len(articles)} published articles in last {LOOKBACK_DAYS} days")
    if not articles:
        print("  No articles to process.")
        return

    articles_by_id = {a["id"]: a for a in articles}

    # 2. Fetch existing storylines
    storylines = fetch_storylines()
    print(f"  📌 {len(storylines)} active/emerging/cooling storylines")

    # 3. Get already-linked article IDs
    linked_ids = fetch_storyline_article_ids()
    print(f"  🔗 {len(linked_ids)} articles already linked")

    # 4. Filter to unlinked articles
    unlinked = [a for a in articles if a["id"] not in linked_ids]
    print(f"  🆕 {len(unlinked)} unlinked articles to classify")

    if not unlinked:
        print("  All articles already classified.")
        # Still update lifecycle
        update_lifecycle(dry_run=args.dry_run)
        return

    # 5. Build storyline headlines map for context
    storyline_headlines = {}
    for s in storylines:
        storyline_headlines[s["id"]] = fetch_storyline_headlines(s["id"], limit=5)

    # 6. Classify articles in batches
    new_proposals = {}  # title → [article_ids]
    matches = 0
    nones = 0

    for i in range(0, len(unlinked), BATCH_SIZE):
        batch = unlinked[i:i + BATCH_SIZE]
        print(f"\n  Batch {i // BATCH_SIZE + 1}/{(len(unlinked) + BATCH_SIZE - 1) // BATCH_SIZE} ({len(batch)} articles)...")

        classifications = classify_articles(batch, storylines, storyline_headlines)

        for c in classifications:
            aid = c.get("article_id", "")
            action = c.get("action", "none")
            article = articles_by_id.get(aid)
            if not article:
                continue

            if action == "match":
                sid = c.get("storyline_id", "")
                # Validate storyline exists
                if any(s["id"] == sid for s in storylines):
                    link_article_to_storyline(sid, aid, article, dry_run=args.dry_run)
                    matches += 1
                    print(f"    🔗 Matched: '{article['headline'][:60]}' → storyline {sid[:8]}")
                else:
                    print(f"    ⚠️  Invalid storyline_id {sid} for article '{article['headline'][:50]}'")

            elif action == "new":
                title = c.get("title", "").strip()
                summary = c.get("summary", "").strip()
                category = c.get("category", article.get("category", ""))
                if title:
                    if title not in new_proposals:
                        new_proposals[title] = {"summary": summary, "category": category, "article_ids": []}
                    new_proposals[title]["article_ids"].append(aid)
            else:
                nones += 1

        # Rate limit between batches
        if i + BATCH_SIZE < len(unlinked):
            time.sleep(0.5)

    print(f"\n  📊 Classification: {matches} matched, {len(new_proposals)} new proposals, {nones} standalone")

    # 7. Process new storyline proposals
    created = 0
    for title, info in new_proposals.items():
        proposal_ids = info["article_ids"]

        # For new proposals, find ALL recent articles that might match
        # (the batch might have split articles across batches)
        all_candidates = [a for a in articles if a.get("category") == info["category"] or not info["category"]]

        # Verify with LLM which articles truly belong
        verified_ids = verify_new_storyline(title, all_candidates)

        # Merge: proposal IDs + verified IDs
        all_ids = list(set(proposal_ids + [vid for vid in verified_ids if vid in articles_by_id]))

        if len(all_ids) >= ACTIVE_THRESHOLD:
            sid = create_storyline(
                title, info["summary"], info["category"],
                all_ids, articles_by_id, dry_run=args.dry_run
            )
            if sid:
                created += 1
        elif len(all_ids) >= 2:
            # Create as emerging (below threshold but tracking)
            sid = create_storyline(
                title, info["summary"], info["category"],
                all_ids, articles_by_id, dry_run=args.dry_run
            )
            if sid:
                created += 1
        else:
            print(f"    ⏭️  Skipped '{title}' — only {len(all_ids)} article(s)")

    print(f"\n  🏷️  Created {created} new storylines")

    # 8. Merge duplicate storylines
    print("\n  🔀 Merging duplicate storylines...")
    merge_count = merge_similar_storylines(dry_run=args.dry_run)
    if merge_count:
        print(f"  🔀 Merged {merge_count} duplicate storyline(s)")

    # 9. Update lifecycle
    print("\n  🔄 Updating lifecycle...")
    update_lifecycle(dry_run=args.dry_run)

    # 10. Update summaries for active storylines
    print("\n  📝 Updating summaries...")
    update_summaries(dry_run=args.dry_run)

    # Final summary
    all_storylines = fetch_storylines(("emerging", "active", "cooling"))
    active_count = sum(1 for s in all_storylines if s["status"] == "active")
    emerging_count = sum(1 for s in all_storylines if s["status"] == "emerging")
    cooling_count = sum(1 for s in all_storylines if s["status"] == "cooling")
    print(f"\n  ✅ Done. Storylines: {active_count} active, {emerging_count} emerging, {cooling_count} cooling")


if __name__ == "__main__":
    main()
