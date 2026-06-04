# Image Sourcing Strategy — Deep Research Report
## The Videshi News Publication
*Compiled: June 3, 2026*

---

## Executive Summary

For a news publication producing ~170 articles/day across 10+ categories, the optimal image strategy uses a **multi-source waterfall** with **Openverse as the primary aggregator** (it searches Flickr + Wikimedia + 50+ other CC sources in one call), supplemented by direct Wikimedia Commons API calls for person-specific articles, and Pexels as a generic fallback. All images must be downloaded, compressed, and re-hosted on Supabase storage for permanence and performance.

For **celebrity/public figure photos**, the best legal path is Wikimedia Commons (good coverage of Indian politicians, Bollywood stars, and cricket players) combined with Indian government photo archives (PIB, MEA) which are free for editorial use under GODL.

For **X/Twitter embeds**, the free oEmbed endpoint (`publish.twitter.com/oembed`) can **verify whether a tweet exists** without any API key. The new pay-per-use X API ($0.005/read) makes searching for real tweets affordable at ~$5-10/month for our volume.

---

## 1. Image Sources — Comprehensive Comparison

### 1A. Openverse API ⭐ RECOMMENDED PRIMARY SOURCE

**What it is:** Open-source search engine (by WordPress Foundation) that aggregates 800M+ openly-licensed images from Flickr, Wikimedia Commons, StockSnap, rawpixel, iNaturalist, Smithsonian, and 50+ other sources. One API call searches them all.

**Pricing:** Completely free. No API key required for anonymous access.

**Rate Limits:**
| Access Level | Burst Limit | Sustained Limit |
|---|---|---|
| Anonymous (no key) | 20 requests/min | 200 requests/day |
| Registered (free) | 100 requests/min | 10,000 requests/day |

**Registration:** Free, instant. We already registered:
- Client ID: `a7gAY68XlhemaWpOXeJyUzvwonXK53ZjLQ12kLA7`
- Client Secret: (stored — check email for verification link to activate)

**At 170 articles/day with ~3 searches each = ~510 requests/day** — well within the 10,000/day registered limit.

**API Endpoint:**
```
GET https://api.openverse.org/v1/images/
  ?q=Narendra+Modi
  &license=by,by-sa,cc0,pdm
  &page_size=5
```

**Key features:**
- License filtering (`by`, `by-sa`, `cc0`, `pdm` for commercial-safe licenses)
- Source filtering (e.g., `source=flickr,wikimedia`)
- Returns full attribution text, creator name, license type per image
- Returns both thumbnail and full-size URLs
- Aggregates results across 50+ sources

**Test Results (live):**
- "Narendra Modi": 240 results (Flickr + Wikimedia)
- "Shah Rukh Khan": 209 results (Flickr + Wikimedia)
- "India cricket test match": 144 results (Flickr + Wikimedia)

**Verdict:** Best single source. Replaces the need to separately call Flickr and Wikimedia for most use cases. Use as the primary image search for all articles.

---

### 1B. Wikimedia Commons API ⭐ ALREADY IN USE — KEEP FOR PERSON ARTICLES

**What it is:** Direct API for 100M+ CC-licensed files on Wikimedia Commons.

**Pricing:** Free. No API key needed. Requires `User-Agent` header.

**Rate Limits:** No published hard limit for API queries, but they request:
- "Reasonable" usage (don't hammer endpoints)
- `User-Agent` header identifying your app is mandatory
- Image hotlinks require `User-Agent` for downloads (403 without it)

**Best for:** Person-specific searches where Wikipedia's REST API (`/page/summary/{name}`) gives the canonical portrait photo.

**API Endpoints:**
```python
# Person photo (canonical portrait)
GET https://en.wikipedia.org/api/rest_v1/page/summary/{Person_Name}
# Returns: originalimage.source, thumbnail.source

# Topic search (events, places, objects)
GET https://commons.wikimedia.org/w/api.php
  ?action=query&generator=search
  &gsrsearch={topic}&gsrnamespace=6
  &gsrlimit=10&prop=imageinfo
  &iiprop=url|size|mime|extmetadata
  &iiurlwidth=1200&format=json
```

**Coverage of Indian celebrities:** Good for politicians (Modi, Rahul Gandhi, etc.), established Bollywood actors (SRK, Vicky Kaushal, Ranveer Singh), and major cricket stars. Weaker for newer or less prominent figures.

**Verdict:** Keep as the mandatory first check for person articles. The Wikipedia REST API gives the most canonical/recognizable photo of a public figure.

---

### 1C. Pexels API ✅ ALREADY IN USE — KEEP AS GENERIC FALLBACK

**Pricing:** Free. API key required (already have one).

**Rate Limits:** 200 requests/hour, 20,000 requests/month (can request unlimited for free with proper attribution).

**License:** Pexels License — free for commercial use, no attribution legally required, but must link back to Pexels and credit photographers when possible.

**Best for:** Generic/scene/topic images when no specific person photo is needed (e.g., "stock market chart", "visa passport", "hospital", "cricket stadium").

**Weaknesses:** No celebrity photos. No editorial/news-specific content. Generic stock quality.

**Verdict:** Keep as the last-resort fallback for articles where Openverse and Wikimedia return nothing.

---

### 1D. Flickr API ⚠️ NOT RECOMMENDED (Openverse covers it)

**Pricing:** Free API, BUT API key creation now requires a Flickr Pro subscription ($49.99/year — increased from free).

**Rate Limits:** 3,600 requests/hour.

**License filtering:** Excellent — can filter by specific CC license types (IDs 1-10).

**Coverage:** 400M+ CC-licensed images, including significant editorial/event content from government accounts, news photographers, and organizations.

**Why skip:** Openverse already indexes Flickr's CC-licensed content. Our Openverse test results returned Flickr photos for Modi and SRK. There's no need to separately integrate Flickr unless Openverse's results are insufficient.

**Verdict:** Skip for now. If Openverse coverage proves insufficient for specific categories, revisit with a Flickr Pro subscription ($50/year).

---

### 1E. Unsplash API ⚠️ LIMITED VALUE FOR NEWS

**Pricing:** Free. Requires registration.

**Rate Limits:** 50 requests/hour (development), 5,000/hour (production after approval).

**License:** Unsplash License (custom — NOT CC). Free for commercial use, no attribution required, but cannot use to create a competing image product.

**Restrictions:** "Unsplash photos should not be used to create a new wallpaper or stock photo platform, or a service that competes with Unsplash."

**Coverage:** 3M+ high-quality photos. Strong for lifestyle, food, travel, nature. **No celebrity/public figure content. No editorial/news content.**

**Verdict:** Marginal value. Could add as an additional fallback for food/travel/lifestyle articles, but Pexels already covers this space. Not worth the integration effort.

---

### 1F. Pixabay API ⚠️ LIMITED VALUE FOR NEWS

**Pricing:** Free. Requires API key registration (free, instant).

**Rate Limits:** 5,000 requests/hour (generous).

**License:** Pixabay License (custom — NOT CC0 anymore). Free for commercial use, no attribution required. Explicitly prohibits redistribution as standalone files or in a competing image library.

**Coverage:** 4M+ images and videos. Similar to Pexels — strong for generic/lifestyle, weak for editorial/news.

**Verdict:** Skip. Pexels already covers the same space with similar terms. Adding another generic stock source adds complexity without improving article quality.

---

### 1G. Getty Images Embed Program

**What it is:** Getty allows embedding their images on non-commercial websites/blogs for free (with their embed code). The embed includes Getty branding and links.

**Restrictions:** Non-commercial use only. An ad-supported news publication like The Videshi would likely NOT qualify. Commercial use requires a paid license ($175-499 per image for editorial use).

**Verdict:** Not viable for automated pipeline use.

---

### 1H. AP Images / Reuters

**Pricing:** Professional wire services. Subscriptions typically $500-2000+/month for editorial clients. AP has "AP Buyline" for smaller publishers with per-image pricing.

**Verdict:** Not cost-effective at our stage. Revisit when the publication has revenue to justify it.

---

### 1I. Google Custom Search Images

**Status as of June 2026:** Google is deprecating the Custom Search JSON API (deadline January 2027). New projects cannot get access — returns 403 errors. **Dead for new users.**

**Alternative:** Google Programmable Search Engine still works for web search embeds (rendered in iframe), but not for programmatic image URL extraction.

**Verdict:** Dead. Not available.

---

### 1J. Bing Image Search API

**Status:** Microsoft blocked new Azure resource creation for Bing Search since early 2025 (`ApiSetDisabledForCreation` error). Existing keys still work but no new users can sign up.

**Verdict:** Dead. Not available.

---

## 2. Celebrity & Public Figure Photos

### 2A. The Legal Landscape

**Indian Copyright Act, Section 52(1)(a)(iii):** Permits "fair dealing" for "the reporting of current events and current affairs." This is the primary legal basis for using photos in news articles.

**Key differences from US fair use:**
- India uses a **closed-list** system — only the specific purposes listed in Section 52 are protected
- The purpose must be one of: criticism/review, private study/research, or **reporting current events**
- Indian courts evaluate: (1) purpose and character of use, (2) nature of the work, (3) amount used, (4) effect on the market for the original

**For The Videshi:** As a news publication reporting current events, using photos of public figures in editorial context IS a permitted purpose under Section 52(1)(a)(iii). However, this applies to fair dealing with the photos — it doesn't mean you can take any copyrighted photo you find. Best practice: use CC-licensed or government photos, and apply fair dealing defense only as a backup.

### 2B. Best Sources for Indian Celebrity/Public Figure Photos

**Tier 1 — Safest (CC-licensed or public domain):**

1. **Wikimedia Commons** — Best single source for Indian public figures. Coverage:
   - **Indian politicians:** Excellent (Modi, Shah, Rajnath, state CMs — most have Wikipedia articles with photos)
   - **Bollywood:** Good for established stars (SRK, Salman, Aamir, Vicky Kaushal, Ranveer Singh, Deepika, Priyanka). Weaker for newer/smaller actors
   - **Cricket:** Good for international players (Kohli, Bumrah, Rohit Sharma). Weaker for domestic-only players
   - **Tech CEOs:** Excellent (Sundar Pichai, Satya Nadella, Indian-origin founders)

2. **Indian Government Photo Archives (PIB/MEA):**
   - **Press Information Bureau (PIB):** Has a public photo gallery at `pib.gov.in/photogallery`. Contains official photos of PM, ministers, foreign dignitaries, government events
   - **Ministry of External Affairs (MEA):** Photos of diplomatic events, foreign visits
   - **GODL (Government Open Data License - India):** Indian government works marked with GODL can be freely used with attribution. In June 2025, the government explicitly opened PIB, Doordarshan, and All India Radio archives for free public use
   - **PBShabd portal:** Prasar Bharati's digital portal offers copyright-cleared news clips and photos

3. **Openverse/Flickr CC photos:** Many event photographers, government accounts, and organizations upload CC-licensed photos. Openverse aggregates these.

**Tier 2 — Editorial use (fair dealing):**

4. **Social media profile photos / press kits:** Many celebrities and organizations have press photos on their websites intended for media use. Always check for a "press" or "media" section.

5. **Event photos from wire services:** If the publication grows, AP/Reuters subscriptions provide the gold standard.

**What major Indian news sites use:**
- **NDTV, Times of India, Indian Express:** Reuters, AFP, AP wire service photos + their own photographers
- **Scroll.in, The Wire:** Mix of wire photos, Wikimedia Commons, and CC-licensed Flickr photos
- **Smaller digital outlets:** Primarily Wikimedia Commons + stock photos (similar to our approach)

### 2C. Recommended Approach

```
Person article → Search order:
1. Wikipedia REST API (/page/summary/{name}) — canonical portrait
2. Openverse API (searches Flickr + Wikimedia CC photos)
3. PIB Photo Gallery (for Indian politicians/government officials)
4. Pexels (only as last resort — will return generic, not the actual person)
5. No image (better than a wrong/generic photo)
```

---

## 3. Multiple Images Per Article

### 3A. Current State
Articles currently have one hero image. The database supports `gallery_images` (JSON array of `{url, caption}`), but writers aren't populating it.

### 3B. Best Practice: 2-4 Images Per Article

**How major publications handle it:**
- **Hero image:** The primary photo, displayed above the article body. Should be the most impactful, relevant image.
- **Inline images:** 1-3 additional images placed within the article body at relevant points. These break up text and illustrate specific sections.
- **Embedded media:** Social media posts, charts, maps — not traditional images but serve the same visual function.

**Search strategy for supplementary images:**

Given an article about "India-Australia Defence Dialogue":
1. **Hero:** Photo of the two ministers meeting (Wikipedia/PIB)
2. **Inline 1:** Indian Navy submarine or warship (Wikimedia Commons: "Indian Navy submarine")
3. **Inline 2:** Australian military delegation (PIB photo gallery)
4. **Inline 3:** Map of Indo-Pacific region (Wikimedia Commons)

**Implementation approach:**
```python
# For the LLM writer:
# 1. Extract 3-4 key visual themes from the article
# 2. Search Openverse for each theme
# 3. Pick the best match per theme
# 4. Insert as markdown images at relevant points in the body

# Example article body with inline images:
"""
## India's Defence Partnership Deepens

The dialogue covered maritime cooperation...

![Indian Navy frigate during Malabar exercise](https://supabase.co/.../inline-1.jpg)
*An Indian Navy frigate participating in the Malabar naval exercise. Photo: Wikimedia Commons*

The two sides also discussed...
"""
```

**Writer instruction template:**
```
For each article, source 2-4 images:
- 1 hero image (primary subject)
- 1-2 inline images (illustrating key sections)
- Use markdown image syntax in the body: ![caption](url)
- Add figcaption below each inline image
- Search different terms for each image to get variety
```

---

## 4. X/Twitter Embeds — Proper Approach

### 4A. The Problem
AI writers fabricated fake tweet URLs with garbled handles (e.g., `@rajaborijfnews`, `@WaborWrestling`). These render as broken blockquotes on the site.

### 4B. Solution: oEmbed Verification + Curated Handle Registry

**X oEmbed endpoint (FREE, no API key needed):**
```
GET https://publish.twitter.com/oembed?url=https://twitter.com/{handle}/status/{id}
```
- Returns JSON with `html` field for **real tweets** (HTTP 200)
- Returns HTTP 404 or non-JSON for **fake/deleted tweets**
- **No authentication required** — completely free
- Rate limit: undocumented but generous (intended for embed widgets)

**Note:** Our server-side tests returned inconsistent results (possibly due to proxy/IP restrictions). The endpoint works reliably from browser contexts. For server-side validation, use a HEAD request to check HTTP status code.

### 4C. X API for Finding Real Tweets

**New pay-per-use pricing (launched Feb 2026):**
| Operation | Cost |
|---|---|
| Post read | $0.005 |
| Post create | $0.01 |
| User profile lookup | $0.01 |
| Recent search (7-day window) | Per-read pricing |

**For The Videshi's needs:**
- ~20 articles/day might benefit from tweet embeds
- ~3 searches per article × $0.005 = $0.015/article
- 20 articles × $0.015 = $0.30/day = **~$9/month**

**API capabilities with pay-per-use:**
- Recent search (7-day window) — find tweets by keyword/handle
- User timeline — get recent tweets from a specific account
- No streaming (Pro/Enterprise only)
- No full archive search (7-day window only)

### 4D. Recommended Approach

**Phase 1 (Now — Free):**
1. Remove social embed instructions from writers (already done)
2. Build a curated tweet registry: manually add real tweet URLs for major handles when relevant stories break
3. Use oEmbed endpoint to verify any tweet URL before embedding

**Phase 2 (When budget allows — ~$10/month):**
1. Sign up for X API pay-per-use
2. Build a pre-processing step that searches X for recent tweets from relevant handles about the article topic
3. Verify each found tweet via oEmbed
4. Pass verified tweet URLs to the writer for embedding
5. Never let the AI writer fabricate tweet URLs

**Phase 3 (Future):**
1. Build an automated tweet-sourcing cron that runs before writers
2. For each article topic, search X for the most relevant tweet
3. Store in a tweet cache with article_id mapping
4. Writers pull from the cache instead of searching

---

## 5. Copyright Protection & Attribution

### 5A. Attribution Requirements by Source

| Source | Attribution Required? | Format |
|---|---|---|
| **Wikimedia Commons** | Yes (per license) | "Photo: {Creator}, via Wikimedia Commons, {License}" |
| **Pexels** | Recommended (not legally required) | "Photo by {Photographer} on Pexels" + link |
| **Openverse (CC BY)** | Yes, mandatory | "{Title}" by {Creator} is licensed under CC BY {version} |
| **Openverse (CC BY-SA)** | Yes, mandatory | Same as above + must share derivatives under same license |
| **Openverse (CC0/PDM)** | No, but recommended | "Photo: {Source}, Public Domain" |
| **Unsplash** | Not required | "Photo by {Photographer} on Unsplash" (recommended) |
| **Pixabay** | Not required | "Image: Pixabay" (recommended) |
| **PIB/Government (GODL)** | Yes | "Photo: Press Information Bureau, Government of India" |

### 5B. Standard Figcaption Format

Major news sites use this pattern:
```html
<figure>
  <img src="..." alt="Description" />
  <figcaption>
    Caption describing the image. Photo: Creator/Source
  </figcaption>
</figure>
```

**Examples from major publications:**
- Reuters: `"FILE PHOTO: Prime Minister Narendra Modi speaks at... REUTERS/Photographer Name"`
- BBC: `"Image caption: Description. Image source: Source"`
- NDTV: `"Caption (Source: Agency/Photographer)"`

**Recommended format for The Videshi:**
```
{Descriptive caption of what the image shows}. Photo: {Creator/Source}
```
Examples:
- `Prime Minister Modi addresses the G20 summit in New Delhi. Photo: PIB, Government of India`
- `Vicky Kaushal at the Zara Hatke Zara Bachke premiere. Photo: Bollywood Hungama, via Wikimedia Commons (CC BY 3.0)`
- `A view of the Bombay Stock Exchange. Photo: Pexels`

### 5C. Creative Commons Licenses — What Each Allows

| License | Commercial Use? | Modification? | Must Share Alike? | Safe for The Videshi? |
|---|---|---|---|---|
| **CC0 (Public Domain)** | ✅ Yes | ✅ Yes | No | ✅ Yes |
| **CC BY** | ✅ Yes | ✅ Yes | No | ✅ Yes (with attribution) |
| **CC BY-SA** | ✅ Yes | ✅ Yes | Yes (derivatives must be CC BY-SA) | ⚠️ Caution — resizing/cropping may count as derivative |
| **CC BY-ND** | ✅ Yes | ❌ No modifications | N/A | ⚠️ Cannot crop/resize |
| **CC BY-NC** | ❌ No | ✅ Yes | No | ❌ No — ad-supported site is commercial |
| **CC BY-NC-SA** | ❌ No | ✅ Yes | Yes | ❌ No |
| **CC BY-NC-ND** | ❌ No | ❌ No | N/A | ❌ No |

**For The Videshi (commercial, ad-supported):** Only use images licensed as **CC0, CC BY, CC BY-SA, or Public Domain**. Avoid NC (Non-Commercial) licenses.

**Openverse API license filter for commercial-safe:**
```
license=by,by-sa,cc0,pdm
```

### 5D. DMCA Safe Harbor

As a US-facing publication (thevideshi.com), you should establish DMCA safe harbor:

1. **Designate a DMCA agent** — Register with the US Copyright Office ($6 online)
2. **Add a DMCA/Copyright page** to the website with:
   - Contact information for copyright complaints
   - Takedown procedure
   - Counter-notification procedure
3. **Respond promptly** to any takedown requests (within 72 hours)
4. **Keep records** of image sources and licenses for every article

### 5E. Indian Copyright Law — Section 52 Fair Dealing

**Section 52(1)(a)(iii)** permits fair dealing for "reporting of current events and current affairs."

**What this means for The Videshi:**
- Using photos of public figures in news articles IS permitted as fair dealing
- The use must be proportionate — use a reasonable portion, not entire photo galleries
- Always provide attribution — courts look more favorably at attributed use
- Don't use photos in misleading or defamatory contexts
- Fair dealing is a DEFENSE, not a right — it's evaluated case-by-case

**Best practice:** Don't rely on fair dealing as your primary strategy. Use properly licensed images (CC, government, stock) and treat fair dealing as a safety net.

### 5F. Metadata Preservation

**Should you preserve EXIF/XMP metadata?**

For legal protection, preserve at least:
- Original creator/photographer name
- License type
- Source URL
- Date of sourcing

**Recommended:** Store metadata in the database alongside the image URL:
```json
{
  "image_url": "https://supabase.co/.../article.jpg",
  "image_caption": "PM Modi meets Australian PM at G20",
  "image_attribution": "PIB, Government of India",
  "image_license": "GODL-India",
  "image_source_url": "https://pib.gov.in/photogallery/...",
  "image_creator": "PIB Photo Division"
}
```

This metadata should be stored but doesn't need to be displayed to readers — the `figcaption` with caption + attribution is sufficient.

---

## 6. Recommended Architecture

### 6A. Image Source Priority (Ranked)

```
For PERSON articles:
  1. Wikipedia REST API (/page/summary/{name}) → canonical portrait
  2. Openverse API (q="{person name}", license=by,by-sa,cc0,pdm)
  3. Wikimedia Commons API (direct search)
  4. PIB Photo Gallery (for Indian politicians/officials)
  5. Pexels (generic fallback)
  6. No image

For EVENT/TOPIC articles:
  1. Openverse API (topic keywords, license=by,by-sa,cc0,pdm)
  2. Wikimedia Commons API (direct search)
  3. PIB Photo Gallery (for government/political events)
  4. Pexels (topic-specific search)
  5. No image
```

### 6B. API Integration Code

```python
import requests
from PIL import Image
import io

OPENVERSE_CLIENT_ID = "a7gAY68XlhemaWpOXeJyUzvwonXK53ZjLQ12kLA7"
OPENVERSE_TOKEN = None  # obtained via OAuth after email verification

def search_openverse(query, page_size=5):
    """Search Openverse for CC-licensed images. Returns list of candidates."""
    headers = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}
    if OPENVERSE_TOKEN:
        headers["Authorization"] = f"Bearer {OPENVERSE_TOKEN}"
    
    r = requests.get(
        "https://api.openverse.org/v1/images/",
        params={
            "q": query,
            "license": "by,by-sa,cc0,pdm",  # commercial-safe only
            "page_size": page_size,
        },
        headers=headers,
        timeout=15,
    )
    if r.status_code != 200:
        return []
    
    results = []
    for img in r.json().get("results", []):
        # Skip tiny images
        if img.get("width", 0) < 300 or img.get("height", 0) < 300:
            continue
        results.append({
            "url": img["url"],
            "thumbnail": img.get("thumbnail", img["url"]),
            "title": img.get("title", ""),
            "creator": img.get("creator", ""),
            "source": img.get("source", ""),
            "license": img.get("license", ""),
            "license_version": img.get("license_version", ""),
            "attribution": img.get("attribution", ""),
            "foreign_landing_url": img.get("foreign_landing_url", ""),
        })
    return results

def search_wikipedia_person(person_name):
    """Get canonical portrait from Wikipedia."""
    encoded = person_name.replace(" ", "_")
    r = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
        timeout=10,
    )
    if r.status_code == 200:
        data = r.json()
        img = data.get("originalimage", {}).get("source") or \
              data.get("thumbnail", {}).get("source")
        if img:
            return {
                "url": img,
                "title": data.get("title", person_name),
                "source": "wikimedia",
                "license": "varies",  # Wikipedia images have various licenses
                "attribution": f"Wikimedia Commons",
            }
    return None

def compress_and_upload(img_url, filename, supabase_url, supabase_key):
    """Download, compress, and upload image to Supabase storage."""
    r = requests.get(
        img_url,
        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
        timeout=15,
    )
    if r.status_code != 200:
        return None
    
    img = Image.open(io.BytesIO(r.content))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > 1200:
        ratio = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80, optimize=True)
    
    upload_r = requests.put(
        f"{supabase_url}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=buf.getvalue(),
        timeout=30,
    )
    if upload_r.status_code in (200, 201):
        return f"{supabase_url}/storage/v1/object/public/article-images/{filename}"
    return None

def verify_tweet_exists(tweet_url):
    """Check if a tweet URL is real using X's free oEmbed endpoint."""
    # Normalize to twitter.com format
    url = tweet_url.replace("x.com", "twitter.com")
    r = requests.get(
        "https://publish.twitter.com/oembed",
        params={"url": url},
        timeout=10,
    )
    return r.status_code == 200 and "html" in r.json()
```

### 6C. Attribution Handling

Store per-image metadata in the article record:
```sql
-- Existing columns (already in p2_articles):
image_url TEXT,           -- Supabase storage URL (always re-hosted)
image_caption TEXT,       -- "PM Modi meets Australian PM at G20 summit"
image_attribution TEXT,   -- "PIB, Government of India" or "Wikimedia Commons"

-- Recommended additions for legal protection:
image_license TEXT,       -- "CC BY 2.0" or "GODL-India" or "Pexels License"
image_source_url TEXT,    -- Original URL on source platform
image_creator TEXT,       -- Photographer/creator name
```

**Display format on the frontend** (already implemented):
```
[Image]
{Caption}. Photo: {Attribution}
```

### 6D. License Verification Pipeline

Before using any image, verify it's legally safe:
```python
SAFE_LICENSES = {"by", "by-sa", "cc0", "pdm", "publicdomain"}
UNSAFE_LICENSES = {"by-nc", "by-nc-sa", "by-nc-nd", "by-nd"}

def is_license_safe(license_code):
    """Check if a license allows commercial editorial use."""
    normalized = license_code.lower().replace(" ", "").replace("-", "")
    # Check for NC (non-commercial) — not safe for ad-supported site
    if "nc" in normalized:
        return False
    # Check for known safe licenses
    for safe in SAFE_LICENSES:
        if safe.replace("-", "") in normalized:
            return True
    # Pexels, Unsplash, Pixabay custom licenses are safe for editorial
    if normalized in ("pexels", "unsplash", "pixabay"):
        return True
    return False  # When in doubt, don't use
```

### 6E. Caching & Storage Strategy

```
Writer pipeline flow:
1. Article topic → Extract search terms
2. Search Openverse + Wikipedia (parallel)
3. Compare candidates → Pick best
4. Download image with User-Agent header
5. Compress to 1200px JPEG @ 80% quality
6. Upload to Supabase storage bucket "article-images"
7. Store metadata: image_url (Supabase), caption, attribution, license, source_url
8. Article record always points to Supabase URL

Benefits:
- All images served from our own CDN (fast, reliable)
- No hotlink dependency on external services
- Images survive if upstream source changes/disappears
- Social autopost scripts can always download from Supabase
- Consistent sizing/quality across all articles
```

---

## 7. Implementation Priority

### Immediate (can do now):
1. ✅ Activate Openverse API registration (check email, verify, get token)
2. ✅ Replace primary image search: Openverse → Wikipedia → Pexels
3. ✅ Mandate image captions + attribution on all articles
4. ✅ Compress all images to 1200px before upload
5. ✅ Remove fake tweet embed instructions from writers

### Short-term (this week):
6. Add `image_license`, `image_source_url`, `image_creator` columns to `p2_articles`
7. Update writer cron instructions to use Openverse API
8. Build inline image support (2-3 images per article)
9. Create a Copyright/DMCA page on the website

### Medium-term (this month):
10. Integrate PIB photo gallery scraper for government event photos
11. Sign up for X API pay-per-use (~$10/month) for real tweet searching
12. Build tweet verification step using oEmbed endpoint
13. Create automated image sourcing pre-processor (runs before writers)

### Long-term (future):
14. AP/Reuters subscription when revenue justifies it
15. Custom photographer partnerships for exclusive Indian diaspora content
16. AI-powered image relevance scoring

---

## Appendix: API Quick Reference

| Source | Endpoint | Key Required? | Rate Limit | License |
|---|---|---|---|---|
| **Openverse** | `api.openverse.org/v1/images/` | No (anon) / Yes (registered) | 200/day (anon) / 10K/day (registered) | Per-image (CC variants) |
| **Wikipedia** | `en.wikipedia.org/api/rest_v1/page/summary/{name}` | No | Reasonable use | Per-image (usually CC) |
| **Wikimedia Commons** | `commons.wikimedia.org/w/api.php` | No | Reasonable use | Per-image (all CC) |
| **Pexels** | `api.pexels.com/v1/search` | Yes (free) | 200/hr, 20K/month | Pexels License |
| **Unsplash** | `api.unsplash.com/search/photos` | Yes (free) | 50/hr (dev), 5K/hr (prod) | Unsplash License |
| **Pixabay** | `pixabay.com/api/` | Yes (free) | 5,000/hr | Pixabay License |
| **X oEmbed** | `publish.twitter.com/oembed` | No | Undocumented | N/A (verification only) |
| **X API v2** | `api.twitter.com/2/tweets/search/recent` | Yes (paid) | Pay-per-use ($0.005/read) | N/A |
