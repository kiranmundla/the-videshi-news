#!/usr/bin/env python3
"""
movie-reviews.py — Friday movie review roundup automation.

Reads now-in-theaters.json for movies opening this week, searches for critic
reviews, synthesizes a review roundup article per movie via GPT-4o-mini, and
publishes directly to Supabase. Runs article-polish.py and enrich-on-publish.py
on each inserted article.

Designed to run Friday mornings. Indian reviews are already out by then due to
the timezone gap, and US Thursday night press screenings have posted.

Run: python3 -u pipeline/movie-reviews.py [--dry-run]
Uses curl for all HTTP calls (no requests/urllib for external APIs).
"""
import json, os, re, sys, subprocess, tempfile, time, hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
THEATERS_JSON = REPO / "public" / "data" / "now-in-theaters.json"

DRY_RUN = "--dry-run" in sys.argv

NOW = datetime.now(timezone.utc)
TODAY = NOW.strftime("%Y-%m-%d")

# ── Env loading ───────────────────────────────────────────────────────────────
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

load_env("~/workspace/.env.supabase", "~/workspace/.env.openai")

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

if not SB_URL or not SB_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

SB_HOST = SB_URL.replace("https://", "")
UA = "TheVideshi/1.0 (https://thevideshi.com; editorial)"


# ── curl helpers ──────────────────────────────────────────────────────────────
def curl_get(url, headers=None, timeout=15):
    """GET via curl. Returns (status_code, body_text)."""
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "--max-time", str(timeout), url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return 0, ""
        lines = r.stdout.rsplit("\n", 1)
        if len(lines) == 2:
            body, code = lines
            return int(code), body
        return 0, r.stdout
    except Exception as e:
        print(f"  ⚠ curl_get error: {e}")
        return 0, ""


def curl_post_json(url, data, headers=None, timeout=60):
    """POST JSON via curl. Returns parsed JSON or None."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(data, tmp, ensure_ascii=False)
        tmp_path = tmp.name

    cmd = [
        "curl", "-sS", "--max-time", str(timeout),
        "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", f"@{tmp_path}",
    ]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        os.unlink(tmp_path)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  ⚠ curl_post error: {e}")
        try:
            os.unlink(tmp_path)
        except:
            pass
        return None


def sb_get(endpoint, params=None):
    """GET from Supabase REST API."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if params:
        qs = "&".join(f"{k}={quote(str(v), safe='.,()')}" for k, v in params.items())
        url = f"{url}?{qs}"
    code, body = curl_get(url, headers={
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
    }, timeout=15)
    if code != 200 or not body:
        return None
    try:
        return json.loads(body)
    except:
        return None


def sb_insert(table, data):
    """INSERT into Supabase. Returns inserted row (with id) or None."""
    url = f"{SB_URL}/rest/v1/{table}"
    result = curl_post_json(url, data, headers={
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Prefer": "return=representation",
    }, timeout=20)
    return result


# ── Web search ────────────────────────────────────────────────────────────────
def web_search(query, timeout=15):
    """Search via DuckDuckGo HTML and extract result snippets."""
    encoded_q = quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
    code, body = curl_get(url, headers={"User-Agent": UA}, timeout=timeout)
    if code != 200 or not body:
        return ""
    # Strip HTML tags, keep text
    text = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:6000]


def search_reviews(movie_title, year, is_indian=False, language=""):
    """Search the web for critic reviews of a movie. Returns combined text."""
    queries = [
        f"{movie_title} {year} movie review",
        f"{movie_title} critic reviews ratings",
        f"{movie_title} {year} Rotten Tomatoes review",
    ]
    if is_indian:
        queries.append(f"{movie_title} review India critics")
        if language and language != "English":
            queries.append(f"{movie_title} {language} movie review {year}")

    all_text = []
    for q in queries:
        print(f"    🔍 {q}")
        result = web_search(q)
        if result:
            all_text.append(f"[Search: {q}]\n{result}")
        time.sleep(0.5)

    return "\n\n".join(all_text)


# ── Step 1: Find opening movies ──────────────────────────────────────────────
def find_opening_movies():
    """Read now-in-theaters.json and find movies opening today/this week."""
    if not THEATERS_JSON.exists():
        print("  ❌ now-in-theaters.json not found")
        return []

    data = json.loads(THEATERS_JSON.read_text())
    movies = data.get("movies", [])
    if not movies:
        print("  No movies in theater data")
        return []

    today_dt = NOW.date()
    yesterday_dt = (NOW - timedelta(days=1)).date()
    # Also include tomorrow for Thursday night releases when running Friday
    tomorrow_dt = (NOW + timedelta(days=1)).date()

    opening = []
    for m in movies:
        release_str = m.get("release_date", "")
        status = m.get("status", "")

        # Match by status or by date
        is_opening = status == "opening"

        if release_str:
            try:
                release_dt = datetime.strptime(release_str, "%Y-%m-%d").date()
                if release_dt in (today_dt, yesterday_dt, tomorrow_dt):
                    is_opening = True
            except ValueError:
                pass

        if is_opening:
            opening.append(m)

    return opening


# ── Step 2: Dedup check ──────────────────────────────────────────────────────
def already_reviewed(movie_title):
    """Check if we already published a review roundup for this movie."""
    # Build a slug-style search from the movie title
    title_slug = re.sub(r'[^a-z0-9\s-]', '', movie_title.lower())
    title_slug = re.sub(r'\s+', '-', title_slug.strip())
    # Search by slug containing the movie's slug AND "review"
    results = sb_get("p2_articles", {
        "select": "id,headline,slug",
        "status": "eq.published",
        "slug": f"like.*review*",
        "limit": "50",
    })

    if not results or not isinstance(results, list):
        return False

    # Check if any result's slug contains the movie name
    # Use first 2-3 significant words from movie title for matching
    title_words = [w for w in movie_title.lower().split() if len(w) > 2 and w not in ('the', 'and', 'for')]
    for r in results:
        slug = (r.get("slug") or "").lower()
        headline = (r.get("headline") or "").lower()
        # Match if at least 2 distinctive title words appear in slug or headline
        word_matches = sum(1 for w in title_words if w in slug or w in headline)
        if word_matches >= min(2, len(title_words)):
            print(f"    ⏭ Already reviewed: {r.get('headline')}")
            return True

    return False


# ── Step 3: GPT-4o-mini review synthesis ─────────────────────────────────────
def synthesize_reviews(movies_with_reviews):
    """
    Single GPT-4o-mini call to synthesize review roundup articles for all movies.
    Returns list of article dicts.
    """
    if not OPENAI_KEY:
        print("  ❌ No OPENAI_API_KEY")
        return []

    # Build the prompt with all movies' review data
    movies_section = []
    for i, (movie, review_text) in enumerate(movies_with_reviews, 1):
        title = movie.get("title", "Unknown")
        director = movie.get("director", "")
        genre = movie.get("genre", "")
        language = movie.get("language", "English")
        is_indian = movie.get("is_indian", False)
        cast = movie.get("cast", [])
        cast_str = ", ".join(cast[:5]) if cast else "unknown cast"

        movies_section.append(f"""
--- MOVIE {i}: {title} ---
Director: {director}
Genre: {genre}
Language: {language}
Cast: {cast_str}
Indian film: {is_indian}

CRITIC REVIEWS FOUND:
{review_text[:8000]}
""")

    movies_block = "\n".join(movies_section)

    prompt = f"""You are writing movie review roundup articles for The Videshi, a news site for the Indian diaspora in the US, UK, Canada, and Australia.

Today is {NOW.strftime('%B %d, %Y')}. These movies are opening in theaters this week.

For EACH movie below, write a review roundup article that synthesizes what critics are saying. This is NOT your own review — it's a digest of real critic opinions.

ARTICLE FORMAT:
Each article should be HTML with this structure:
1. Opening paragraph: one clear sentence stating the critical consensus (positive/mixed/negative), then 2-3 sentences on what the film is about and who made it.
2. "<h2>What Critics Are Saying</h2>" section: 4-5 real critic quotes, each as a blockquote with the reviewer name and outlet. Format: <blockquote>"Actual quote from the review."<cite>— Reviewer Name, Outlet Name</cite></blockquote>
3. "<h2>What Works</h2>" section: 2-3 specific things critics praised (acting, direction, visuals, music, etc.)
4. "<h2>What Doesn't</h2>" section: 1-2 specific criticisms (even for well-reviewed films, be honest)
5. "<h2>The Verdict</h2>" section: 2-3 sentence final summary — should the diaspora audience go see it this weekend?

For Indian films, add a note on the diaspora angle — is it available dubbed/subtitled, does it require cultural context, how does it compare to the director's/star's previous work.

CRITICAL RULES:
- ONLY quote real reviews from the search results below. NEVER fabricate a quote.
- Attribute EVERY quote to the specific outlet and reviewer if named.
- If you can't find enough real quotes, use indirect summaries: "Critics at Variety praised..." rather than fake direct quotes.
- Include the Rotten Tomatoes or Metacritic score ONLY if found in search results. NEVER invent a score.
- Tone: film-literate, opinionated but fair. Like a friend who reads a lot of reviews summarizing them for you.
- Do NOT use generic AI phrases like "In conclusion", "Overall, this film", "It remains to be seen", "Whether you're a fan of..."
- Word count: 500-700 words per article.
- Tags should include movie title, director, lead actors, genre, and language if not English.

Return JSON:
{{
  "articles": [
    {{
      "title": "Movie Title",
      "headline": "Engaging headline (e.g. 'Mirzapur: The Movie — Critics Say Ali Fazal's Swan Song Packs a Punch')",
      "subheadline": "One sentence summary of critical consensus",
      "slug": "movie-title-review-roundup-critics",
      "body_html": "Full article HTML as described above",
      "key_takeaways": ["3-5 bullet points summarizing the key critical consensus points"],
      "sources": [{{"name": "Outlet Name", "url": "https://actual-url-from-search-results"}}],
      "rating_consensus": "Brief score summary if available (e.g. '85% on Rotten Tomatoes, 72 on Metacritic') or null if no scores found",
      "tags": ["tag1", "tag2", "tag3"],
      "is_indian": true/false,
      "cast": ["Actor 1", "Actor 2"],
      "director": "Director Name",
      "diaspora_angle": "Why diaspora audiences should care — 1-2 sentences"
    }}
  ]
}}

If search results contain too little review data for a movie (no actual reviews found), return it with "skip": true and "skip_reason": "explanation".

MOVIES AND THEIR REVIEW DATA:
{movies_block}
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "max_tokens": 6000,
        "temperature": 0.3,
    }

    print("  🤖 Calling GPT-4o-mini for review synthesis...")
    result = curl_post_json(
        "https://api.openai.com/v1/chat/completions",
        payload,
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        timeout=90,
    )

    if not result:
        print("  ❌ GPT call failed")
        return []

    if "error" in result:
        print(f"  ❌ GPT error: {result['error'].get('message', str(result['error']))}")
        return []

    usage = result.get("usage", {})
    cost = usage.get("prompt_tokens", 0) * 0.15 / 1_000_000 + usage.get("completion_tokens", 0) * 0.6 / 1_000_000
    print(f"  💰 GPT cost: ${cost:.4f} ({usage.get('prompt_tokens', 0)} in, {usage.get('completion_tokens', 0)} out)")

    try:
        content = json.loads(result["choices"][0]["message"]["content"])
        articles = content.get("articles", [])
        print(f"  ✅ Got {len(articles)} review articles from GPT")
        return articles
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"  ❌ Failed to parse GPT response: {e}")
        return []


# ── Step 4: Publish to Supabase ──────────────────────────────────────────────
def make_slug_unique(base_slug):
    """Ensure slug is unique by checking Supabase."""
    existing = sb_get("p2_articles", {
        "select": "id",
        "slug": f"eq.{base_slug}",
        "limit": "1",
    })
    if existing and isinstance(existing, list) and len(existing) > 0:
        # Append date to make unique
        return f"{base_slug}-{NOW.strftime('%Y%m%d')}"
    return base_slug


def _pg_text_array(items):
    """Convert a Python list to Postgres text[] literal: {"item1","item2"}.
    PostgREST needs this format for array columns — json.dumps produces
    JSON arrays which Postgres rejects with 'malformed array literal'."""
    if not items:
        return "{}"
    escaped = []
    for item in items:
        s = str(item).replace('\\', '\\\\').replace('"', '\\"')
        escaped.append(f'"{s}"')
    return "{" + ",".join(escaped) + "}"


def publish_article(article_data, movie_data):
    """Insert a review article into Supabase. Returns article ID or None."""
    if article_data.get("skip"):
        print(f"    ⏭ Skipping: {article_data.get('skip_reason', 'insufficient reviews')}")
        return None

    slug = make_slug_unique(article_data.get("slug", "review"))
    headline = article_data.get("headline", "")
    body_html = article_data.get("body_html", "")
    subheadline = article_data.get("subheadline", "")
    key_takeaways = article_data.get("key_takeaways", [])
    tags = article_data.get("tags", [])
    diaspora_angle = article_data.get("diaspora_angle", "")

    # Format sources as URL strings (matching existing article format)
    sources_raw = article_data.get("sources", [])
    sources = []
    for s in sources_raw:
        if isinstance(s, dict):
            url = s.get("url", "")
            if url:
                sources.append(url)
        elif isinstance(s, str):
            sources.append(s)

    # Get poster from theater data for image_url
    poster_url = movie_data.get("poster_url", "")
    image_caption = None
    if poster_url:
        director = article_data.get("director", movie_data.get("director", ""))
        title = article_data.get("title", movie_data.get("title", ""))
        if director:
            image_caption = f"'{title}' directed by {director}, now in theaters."
        else:
            image_caption = f"'{title}', now in theaters."

    # Build the article body with key-takeaways div prepended
    kt_html = ""
    if key_takeaways:
        items = "".join(f"<li>{kt}</li>" for kt in key_takeaways)
        kt_html = f'<div class="key-takeaways"><ul>{items}</ul></div>\n\n'

    full_body = kt_html + body_html

    row = {
        "headline": headline,
        "slug": slug,
        "body": full_body,
        "subheadline": subheadline,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "sources": sources,
        "diaspora_angle": diaspora_angle,
        "score_total": 0,
        "is_editorial": True,
        "key_takeaways": key_takeaways,
        "tags": tags,
        "image_url": poster_url if poster_url else None,
        "image_caption": image_caption,
        "published_at": NOW.isoformat(),
        "created_at": NOW.isoformat(),
    }

    # Remove None values
    row = {k: v for k, v in row.items() if v is not None}

    if DRY_RUN:
        print(f"    📋 [DRY RUN] Would insert: {headline}")
        print(f"       Slug: {slug}")
        print(f"       Sources: {len(sources)}")
        print(f"       Tags: {tags}")
        return "dry-run-id"

    result = sb_insert("p2_articles", row)
    if result and isinstance(result, list) and len(result) > 0:
        article_id = result[0].get("id")
        print(f"    ✅ Published: {headline}")
        print(f"       ID: {article_id}")
        print(f"       Slug: {slug}")
        return article_id
    else:
        print(f"    ❌ Failed to insert: {headline}")
        if result:
            print(f"       Response: {json.dumps(result)[:200]}")
        return None


# ── Step 5: Post-processing ──────────────────────────────────────────────────
def run_polish(article_id):
    """Run article-polish.py on an article."""
    if DRY_RUN:
        print(f"    📋 [DRY RUN] Would polish: {article_id}")
        return

    print(f"    🔧 Running article-polish.py...")
    cmd = [
        "python3", "-u",
        str(REPO / "pipeline" / "article-polish.py"),
        "--article-id", article_id,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                          cwd=str(REPO / "pipeline"))
        if r.returncode == 0:
            print(f"    ✅ Polish complete")
        else:
            print(f"    ⚠ Polish exited {r.returncode}: {r.stderr[:200]}")
    except Exception as e:
        print(f"    ⚠ Polish error: {e}")


def run_enrich(article_id):
    """Run enrich-on-publish.py on an article."""
    if DRY_RUN:
        print(f"    📋 [DRY RUN] Would enrich: {article_id}")
        return

    print(f"    🔧 Running enrich-on-publish.py...")
    cmd = [
        "python3", "-u",
        str(REPO / "pipeline" / "enrich-on-publish.py"),
        "--article-ids", article_id,
        "--apply",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                          cwd=str(REPO / "pipeline"))
        if r.returncode == 0:
            print(f"    ✅ Enrich complete")
        else:
            print(f"    ⚠ Enrich exited {r.returncode}: {r.stderr[:200]}")
    except Exception as e:
        print(f"    ⚠ Enrich error: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    t0 = time.time()

    print(f"\n{'='*60}")
    print(f"Movie Review Roundup — {NOW.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Dry run: {DRY_RUN}")
    print(f"{'='*60}")

    # Step 1: Find opening movies
    print(f"\n── Step 1: Finding opening movies ──")
    opening = find_opening_movies()
    if not opening:
        print("  No movies opening today/this week. Nothing to do.")
        return

    for m in opening:
        indian_flag = " 🇮🇳" if m.get("is_indian") else ""
        print(f"  🎬 {m['title']} ({m.get('release_date', '?')}){indian_flag} — {m.get('genre', '')}")

    # Step 2: Dedup check
    print(f"\n── Step 2: Checking for existing reviews ──")
    movies_to_review = []
    for m in opening:
        if already_reviewed(m["title"]):
            continue
        movies_to_review.append(m)

    if not movies_to_review:
        print("  All opening movies already reviewed. Nothing to do.")
        return

    print(f"  Movies to review: {len(movies_to_review)}")

    # Step 3: Search for reviews
    print(f"\n── Step 3: Searching for critic reviews ──")
    movies_with_reviews = []
    for m in movies_to_review:
        title = m["title"]
        year = m.get("year", NOW.year)
        is_indian = m.get("is_indian", False)
        language = m.get("language", "")
        print(f"\n  📰 Searching reviews for: {title}")
        review_text = search_reviews(title, year, is_indian, language)
        if review_text:
            print(f"    Found {len(review_text)} chars of review data")
            movies_with_reviews.append((m, review_text))
        else:
            print(f"    ⚠ No review data found for {title}")

    if not movies_with_reviews:
        print("\n  No review data found for any movie. Nothing to publish.")
        return

    # Step 4: GPT synthesis
    print(f"\n── Step 4: Synthesizing review articles ──")
    articles = synthesize_reviews(movies_with_reviews)

    if not articles:
        print("  No articles generated.")
        return

    # Step 5: Publish
    print(f"\n── Step 5: Publishing articles ──")
    published_ids = []
    for article, (movie, _) in zip(articles, movies_with_reviews):
        print(f"\n  Publishing: {article.get('headline', article.get('title', '?'))}")
        article_id = publish_article(article, movie)
        if article_id and article_id != "dry-run-id":
            published_ids.append(article_id)

    # Step 6: Post-processing
    if published_ids:
        print(f"\n── Step 6: Post-processing ({len(published_ids)} articles) ──")
        for aid in published_ids:
            run_polish(aid)
            run_enrich(aid)

    # Summary
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"✅ Movie Review Roundup Complete")
    print(f"   Opening movies found: {len(opening)}")
    print(f"   Reviews searched: {len(movies_with_reviews)}")
    print(f"   Articles published: {len(published_ids)}")
    print(f"   Elapsed: {elapsed:.1f}s")
    if DRY_RUN:
        print(f"   ⚠ DRY RUN — nothing was actually published")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
