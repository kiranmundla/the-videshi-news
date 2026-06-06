# Image Sourcing Rules for The Videshi
# All writers MUST follow this. No shortcuts, no generic stock.

## The Rule
**You are a photo editor at a newspaper. Every image must be specifically relevant to the article.**

## Strategy: Multi-Source + Compare
Search ALL available sources, then pick the most relevant image for THIS specific article. Don't stop at the first result — compare candidates and choose the best match.

## Sources (search ALL, then pick best)

### Source 1: Wikipedia Person Image — MANDATORY first check for person articles
If the article is predominantly about a **specific named person** (politician, athlete, celebrity, business leader, etc.), you MUST try Wikipedia first. Do NOT go straight to Pexels for person articles.

**How to detect**: If the headline or article body prominently features a person's name (e.g., "Jofra Archer", "Modi", "Trump", "Sundar Pichai", "Priyanka Chopra"), this step is mandatory.

**API call** — Use the Wikipedia REST API to get the person's actual photo:
```python
import requests, urllib.parse

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer originalimage (higher res), fall back to thumbnail
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    
    # Try alternate name forms (e.g., "Jofra Archer" vs "Jofra_Archer")
    # Also try with disambiguation: "{name} (cricketer)", "{name} (politician)", etc.
    return None
```

**Important notes:**
- Use `User-Agent: TheVideshi/1.0 (thevideshi.com)` — Wikipedia blocks requests without a proper User-Agent
- The API handles redirects, so "Modi" will resolve to "Narendra Modi"
- For common names, try with disambiguation: `fetch_wikipedia_person_image("Jofra Archer")` first, then `fetch_wikipedia_person_image("Jofra Archer (cricketer)")` if no result
- Wikipedia images are CC-licensed or public domain — safe to use for editorial purposes
- Set `image_attribution` to "Wikimedia Commons" when using Wikipedia images

### Source 2: Wikimedia Commons Search — For EVERYTHING (people, events, places, topics)
Wikimedia Commons has 100M+ CC-licensed files. Search it for ANY article topic — not just events/places. It often has current photos that the Wikipedia article page doesn't surface.

**API call** — Search Commons for images:
```python
import requests, urllib.parse

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images. Returns list of {url, title, width, height}."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",  # File namespace only
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                # Skip SVGs and tiny images
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []
```

**Search tips for better results:**
- For people: `"Gulveer Singh" athletics` or `Gulveer Singh runner`
- For events: `India cricket World Cup 2025` or `G20 summit New Delhi`
- For places: `Kedarnath temple` or `Silicon Valley tech campus`
- For policies: `H-1B visa United States` or `Indian passport`
- Try multiple search queries if the first returns nothing — vary the terms

**Date-relevant searches**: For recent events, add the year or specific event name to improve relevance.

### Source 3: Pexels — Topic/scene fallback
- Use SPECIFIC search terms that match the article
- ✅ "Cannes film festival red carpet" — specific and relevant
- ✅ "US visa stamp passport" — specific to the story
- ❌ "Movie" — too generic
- ❌ "Netflix streaming" — generic stock
- ❌ "Man in suit" — useless generic
- **Use curl, not Python urllib** (gets 403 with urllib)
- Pexels env: `source ~/workspace/.env.pexels`

### Source 4: Social Embeds in Article Body (NOT hero image)
For entertainment, sports, tech, and political figures — embed their actual social media posts in the article body. This gives readers real, current content alongside the article.

**How it works**: Drop a bare URL on its own line in the article body markdown. The frontend auto-renders it as an embedded post.

**X/Twitter embeds** (works now):
```markdown
Some article text here.

https://x.com/BCCI/status/1234567890

More article text continues.
```

**Instagram embeds** (works now):
```markdown
https://www.instagram.com/p/SHORTCODE/
```

**Where to find relevant posts**: Check `pipeline/social-embed-registry.json` for verified handles organized by category. Search the person's X/Instagram for a recent post related to the article topic.

**Rules for social embeds:**
- Only embed posts that are DIRECTLY relevant to the article topic
- Prefer posts from the past 7 days for news articles
- Don't embed more than 2 social posts per article
- Social embeds supplement the hero image — they don't replace it
- NEVER download social media images as hero images (copyright violation)

### Source 5: No image — Better than a wrong or generic image
Kiran's rule: **No image > wrong image**

## The Compare Step — CRITICAL
After searching multiple sources, you will often have several candidate images. **Pick the best one** based on:

1. **Relevance**: Does the image show the actual person/event/topic? (A real photo of Gulveer Singh beats a generic runner)
2. **Recency**: For news, prefer current photos over dated ones
3. **Quality**: Prefer larger, higher-resolution images (min 300px wide)
4. **Specificity**: A photo of the specific cricket match beats a generic cricket photo

Example decision flow:
```
Article: "Gulveer Singh Breaks National 800m Record"

Wikipedia person image: None (too new/niche)
Wikimedia Commons: Found 2 images from athletics events, one shows a runner at an Indian athletics meet
Pexels: Found "track and field runner" — generic stock

→ PICK: Wikimedia Commons athletics photo (most relevant, even if not specifically Gulveer)
→ FALLBACK: No image (better than a generic runner stock photo)
```

## Writer Script Template
Every writer script MUST search multiple sources and compare:

```python
# Image sourcing — Multi-source + compare
person_name = "Gulveer Singh"  # Extract from headline/article
article_topic = "800m national record athletics"  # Key topic terms

candidates = []

# Source 1: Wikipedia (mandatory for person articles)
wiki_img = fetch_wikipedia_person_image(person_name)
if wiki_img:
    candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": "high"})

# Source 2: Wikimedia Commons (search with topic terms)
commons_results = fetch_wikimedia_commons_images(f"{person_name} {article_topic}")
if not commons_results:
    # Try broader search
    commons_results = fetch_wikimedia_commons_images(article_topic)
for r in commons_results[:2]:
    candidates.append({"url": r["url"], "source": "wikimedia_commons", "relevance": "medium"})

# Source 3: Pexels (specific terms only)
pexels_img = fetch_pexels_image("athletics 800m race track", "Indian athletics competition")
if pexels_img:
    candidates.append({"url": pexels_img, "source": "pexels", "relevance": "low"})

# Pick best candidate
if candidates:
    # Prefer wikipedia > wikimedia_commons > pexels
    # But override if a lower-priority source has clearly better relevance
    best = candidates[0]  # Already sorted by priority
    img_url = best["url"]
    
    # Download and re-upload to Supabase for permanence
    filename = f"{article['slug']}.jpg"
    final_url = upload_image_to_supabase(img_url, filename)
    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
    sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": final_url, "image_attribution": attribution})
```

## What NEVER to do
- Generic stock photos (popcorn for a movie article, laptop for a tech article, stethoscope for health)
- Pexels as first choice when the article is about a specific person
- Same image on multiple articles
- Images that don't match the article's actual subject
- Satellite/aerial/map images (filtered by BAD_ALT_RE in the pipeline)
- Random kid bowling when the article is about Jofra Archer
- **NEVER use Facebook/Instagram/Meta CDN URLs** (`fbcdn.net`, `cdninstagram.com`, `scontent-*.fbcdn.net`, `lookaside.fbsbx.com`) — these expire within 24-48 hours and will show broken images. Always download and re-upload to Supabase storage.
- **NEVER use any URL with `_nc_ht=`, `_nc_cat=`, `ccb=` query params** — these are signed Meta CDN URLs that expire
- **NEVER download social media photos as hero images** — use social embeds in the body instead (copyright-safe)

## MANDATORY: Re-upload ALL images to Supabase storage (COMPRESSED)
**Every image MUST be downloaded, resized/compressed, and re-uploaded to Supabase storage.** The `image_url` in the database must ALWAYS be a Supabase storage URL.

**Size rules:**
- Max width: **1200px** (resize down if larger, preserve aspect ratio)
- JPEG quality: **80** (good balance of quality vs file size)
- Target file size: **100-300 KB** (flag anything over 500 KB)
- Minimum: **10 KB** (anything smaller is probably a tiny thumbnail — go back and get a larger version)

**When downloading from Wikimedia Commons**, use the thumbnail API with `iiurlwidth=1200` — this returns a pre-resized URL in the `thumburl` field. Do NOT use the `originalimage` URL for hero images (those can be 5+ MB).

**When downloading from Pexels**, append `?auto=compress&cs=tinysrgb&w=1200` to constrain size.

**When downloading from any source**, always include: `headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}`

**Compression before upload** (Python example):
```python
from PIL import Image
import io

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()
```

Upload to Supabase bucket `article-images` with filename `{slug}.jpg` (or `{article_id}.jpg`).

## Skip list
Check `pipeline/image-skip-list.json` before sourcing. Articles in this list had images manually removed — don't re-source them.

## Upload format
- Hero: `{article_id}.jpg` to Supabase bucket `article-images`
- Gallery: `{article_id}_g1.jpg`, `{article_id}_g2.jpg` etc
- Set `image_attribution` = "Wikimedia Commons" (for Wikipedia/Commons images) or "Pexels" (for Pexels images)
- Set `gallery_images` = JSON array of `[{"url": "...", "caption": "..."}]`

## Image caption — MANDATORY
Every article MUST have an `image_caption` that describes what the image actually shows. This appears below the hero image on the article page, like a newspaper photo caption.

**Format**: Short, factual, present tense. Describe the scene or identify the person. 5-20 words.

**Examples**:
- ✅ "Prime Minister Modi meets Australian Defence Minister Richard Marles at Hyderabad House, New Delhi"
- ✅ "Vicky Kaushal at the premiere of Zara Hatke Zara Bachke in Mumbai"
- ✅ "Traders on the floor of the Bombay Stock Exchange"
- ✅ "A Dassault Rafale fighter jet during a flyover at Republic Day 2025"
- ❌ "Image of a person" — too vague
- ❌ "" — never leave it blank

**When inserting/updating the article**, always include:
```python
{
    "image_url": final_url,
    "image_caption": "Description of what the image shows",
    "image_attribution": "Wikimedia Commons"  # or "Pexels"
}
```


## Source 4: YouTube Trailer Embed — MANDATORY for Movie/Series Articles

If the article is about a **specific movie, film, series, or show** (new release, review, trailer drop, box office, streaming premiere), you MUST search for its official trailer on YouTube and embed it.

**How to detect:** Headlines containing release dates, "trailer", "teaser", "season", "streaming on", "box office", "crore", "OTT release", director/producer names with a film title.

**Search method** — Scrape YouTube search results (no API key needed):
```python
import requests, re
from urllib.parse import quote_plus

def search_youtube_trailer(title, content_type="movie"):
    """Search YouTube for official trailer. Returns URL or None."""
    queries = []
    if content_type == "series":
        # Try season-specific first
        import re as _re
        season_m = _re.search(r"Season\s*(\d+)", title, _re.IGNORECASE)
        if season_m:
            queries.append(f"{title} Season {season_m.group(1)} official trailer")
    queries.append(f"{title} official trailer")
    queries.append(f"{title} trailer")

    for query in queries:
        try:
            url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', r.text)
            seen = set()
            for vid in video_ids:
                if vid not in seen:
                    seen.add(vid)
                    return f"https://youtube.com/watch?v={vid}"
        except Exception:
            continue
    return None
```

**How to embed:** Insert a `<youtube>` tag after the first or second paragraph:
```python
trailer_url = search_youtube_trailer("House of the Dragon", "series")
if trailer_url:
    # Insert after first paragraph
    embed_tag = f"\n\n<youtube>{trailer_url}</youtube>\n"
    # Split body and insert
```

**Rules:**
- Only one YouTube embed per article
- Place it after the intro paragraph (not at the very top or bottom)
- Don't embed for general analysis, roundup, or opinion pieces — only for articles about a specific title
- If no trailer exists (very new announcement), skip — don't embed random videos

## Source 5: Wikipedia Season-Specific Pages — For Series/Show Articles

When the article is about a **specific season** of a TV series, search Wikipedia for the season page, not the show page. The season page usually has the official promotional poster.

```python
def fetch_wikipedia_season_image(show_name, season_number):
    """Fetch the season poster from Wikipedia."""
    slug = f"{show_name.replace(' ', '_')}_season_{season_number}"
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                return img
    except Exception:
        pass
    return None
```

**Example:** "House of the Dragon Season 3" → Wikipedia page `House_of_the_Dragon_season_3` → returns the S3 promotional poster (not the show logo).

## Source 6: Google Custom Search (when available)

When the Google CSE API is enabled, use it for the best image results — especially for entertainment, movies, and shows where Wikipedia/Commons may not have great images.

```python
GOOGLE_CSE_KEY = os.environ.get("GOOGLE_CSE_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")

def search_google_images(query, cc_only=True, num=5):
    if not GOOGLE_CSE_KEY or not GOOGLE_CSE_ID:
        return []
    params = {
        "key": GOOGLE_CSE_KEY, "cx": GOOGLE_CSE_ID,
        "q": query, "searchType": "image", "num": num,
    }
    if cc_only:
        params["rights"] = "cc_publicdomain|cc_attribute|cc_sharealike"
    r = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
    if r.status_code != 200:
        return []
    return [{"url": i["link"], "title": i["title"]} for i in r.json().get("items", [])]
```

**Priority order** for image sourcing (highest first):
1. Google CSE with CC filter (when enabled)
2. Wikipedia season page (for series)
3. Wikipedia person page (for person articles)
4. Wikimedia Commons search
5. Openverse API
6. Pexels (last resort)
