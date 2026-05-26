# Image Sourcing Rules for The Videshi
# All writers MUST follow this. No shortcuts, no generic stock.

## The Rule
**You are a photo editor at a newspaper. Every image must be specifically relevant to the article.**

## Hierarchy (in order)

### 1. Wikipedia Person Image — MANDATORY for articles about people
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

### 2. Wikimedia Commons Search — For events, places, institutions
For articles NOT about a specific person but about a known event, building, institution, or place:
```
https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={topic}&gsrlimit=10&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1200&format=json
```

### 3. Social embeds (entertainment/sports/tech only)
If the person is in `pipeline/celebrity-handles.json`, embed their recent relevant Instagram/X post in the article body (copyright-safe).

### 4. Pexels — ONLY as fallback
- ONLY when Wikipedia/Wikimedia returns nothing
- Use SPECIFIC search terms that match the article. 
- ✅ "Cannes film festival red carpet" — specific and relevant
- ✅ "US visa stamp passport" — specific to the story
- ❌ "Movie" — too generic
- ❌ "Netflix streaming" — generic stock
- ❌ "Man in suit" — useless generic
- Pexels API: 
  ```python
  def fetch_pexels_image(query, fallback_query=None):
      ...  # existing implementation
  ```

### 5. No image — Better than a wrong or generic image
Kiran's rule: **No image > wrong image**

## Writer Script Template
Every writer script MUST include the `fetch_wikipedia_person_image()` function above. The image sourcing section should look like:

```python
# Image sourcing — Wikipedia first for person articles
person_name = "Jofra Archer"  # Extract from headline/article
img_url = fetch_wikipedia_person_image(person_name)

if not img_url:
    # Fall back to Pexels with SPECIFIC terms only
    img_url = fetch_pexels_image("IPL cricket match", "cricket stadium India")

if img_url:
    filename = f"{article['slug']}.jpg"
    final_url = upload_image_to_supabase(img_url, filename)
    sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": final_url})
```

## What NEVER to do
- Generic stock photos (popcorn for a movie article, laptop for a tech article, stethoscope for health)
- Pexels as first choice when the article is about a specific person
- Same image on multiple articles
- Images that don't match the article's actual subject
- Satellite/aerial/map images (filtered by BAD_ALT_RE in the pipeline)
- Random kid bowling when the article is about Jofra Archer

## Skip list
Check `pipeline/image-skip-list.json` before sourcing. Articles in this list had images manually removed — don't re-source them.

## Upload format
- Hero: `{article_id}.jpg` to Supabase bucket `article-images`
- Gallery: `{article_id}_g1.jpg`, `{article_id}_g2.jpg` etc
- Set `image_attribution` = "Wikimedia Commons" (for Wikipedia images) or "The Videshi" (for Pexels)
- Set `gallery_images` = JSON array of `[{"url": "...", "caption": "..."}]`
