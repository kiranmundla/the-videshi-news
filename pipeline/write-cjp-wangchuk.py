#!/usr/bin/env python3
"""Writer script: Cockroach Janta Party / Sonam Wangchuk hunger strike article."""

import os, sys, json, requests, io, subprocess, urllib.parse, time

# ─── Env ───
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"

# ─── Image functions ───
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []

def download_image(url):
    """Download image bytes. Try requests first, fall back to curl on 429."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
        elif r.status_code == 429:
            print(f"  ⚠ 429 from requests, trying curl...")
        else:
            print(f"  ⚠ Download failed: HTTP {r.status_code}, size={len(r.content) if r.status_code==200 else 'N/A'}")
    except Exception as e:
        print(f"  ⚠ requests download error: {e}")
    
    # curl fallback
    tmp = "/tmp/hero_download.jpg"
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", tmp, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip() == "200" and os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
            with open(tmp, "rb") as f:
                return f.read()
    except Exception as e:
        print(f"  ⚠ curl download error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes, timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"  ⚠ Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"

def sb_insert(table, data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json=data, timeout=30
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed {r.status_code}: {r.text[:300]}")
        return None
    result = r.json()
    return result[0] if isinstance(result, list) else result

# ─── Article content ───

SLUG = "cockroach-janta-party-sonam-wangchuk-hunger-strike-neet-exam-youth-movement-20260630"
HEADLINE = "He Called India's Jobless Youth 'Cockroaches.' They Built a Party Around It."
SUBHEADLINE = "The Cockroach Janta Party has 22 million followers, a Boston University graduate at the helm, and an icon of Ladakh on hunger strike at its side. India's education minister may not survive the week."

BODY = """India's newest and most improbable political movement was born from an insult.

When Chief Justice of India Surya Kant used the word "cockroaches" in remarks widely interpreted as dismissing the country's unemployed youth, the backlash was immediate — but it was the form it took that nobody expected. Within days, a satirical political party named the Cockroach Janta Party had appeared online, amassed 22 million Instagram followers, and begun mounting the kind of street pressure that India's ruling establishment has rarely faced from a generation it assumed was too busy scrolling to organise.

On June 28, the movement gained its most powerful ally yet. Sonam Wangchuk, the Ladakh-based climate activist and education reformer who inspired the film *3 Idiots*, began an indefinite hunger strike at Jantar Mantar in central Delhi, demanding the resignation of Union Education Minister Dharmendra Pradhan over the NEET-UG 2026 paper leak scandal.

"Six weeks of hunger strike or death," Wangchuk told Reuters, lying on a mattress at the protest site. "But hopefully, we don't have to go that far. A sensitive government in a democracy listens to the pains of the people."

## A Scandal That Won't Die

The crisis traces back to May 3, when the National Eligibility-cum-Entrance Test for undergraduate medical admissions — taken by nearly 23 lakh students — was compromised. A CBI investigation found that question papers had been obtained days before the exam and sold through a network of coaching institutes spanning Maharashtra, Rajasthan, and Bihar for as much as ₹15 lakh per set.

The government cancelled the entire examination and scheduled a re-sit for June 21, but the damage went deeper than a single test. Investigators discovered that the same network had also compromised the NEET UG 2025 paper the previous year — meaning two consecutive classes of aspiring doctors had competed on a rigged playing field. Pradhan himself admitted a "breach in the command chain."

For millions of students who spent years preparing, the revelation shattered whatever trust remained in India's examination apparatus.

## Memes to the Streets

The Cockroach Janta Party — a deliberate riff on Prime Minister Narendra Modi's ruling Bharatiya Janata Party — is the creation of Abhijeet Dipke, a 30-year-old Boston University graduate who flew back to India earlier this month to lead the agitation in person.

"We are here for the long haul, no matter how many days it takes," Dipke told CNN from the protest site. "We are going to be here until Dharmendra Pradhan resigns."

The party started as a single sarcastic tweet and turned into a phenomenon so rapid that the government's Ministry of Electronics and Information Technology ordered its X account blocked within a week of formation, citing "national security concerns." Dipke challenged the block in Delhi High Court and launched a new account within minutes. The party's Instagram page — its primary battlefield — remains untouched, its 22 million followers dwarfing the official accounts of most Indian political parties.

The sit-in at Jantar Mantar, which began on June 20, has drawn daily crowds of hundreds. Protesters bring symbolic props — cockroach masks, satirical signs, exam papers — and the mood is part carnival, part fury. Student leaders from the All India Students Association, JNU, Delhi University, and Ambedkar University have joined. Over 650 farmer organisations have announced plans for a large *khap panchayat* in Delhi to support the movement.

Pradhan has dismissed the CJP as the "B-team of terror groups." Dipke called the charge "ridiculous."

## Why the Diaspora Should Care

The NEET scandal strikes at something deeply personal for the Indian diaspora. Families who have spent years — and lakhs of rupees — preparing children for competitive exams now face a system where the question papers can be bought in advance. For NRIs with children in India's education pipeline, or those who counsel relatives through the gruelling entrance exam cycle, the breach is not abstract.

The movement's timing also collides with a widely expected cabinet reshuffle. Indian media report that Pradhan could be moved from the education portfolio as Modi weighs changes before the monsoon session of Parliament, expected in the third week of July. Whether the reshuffle is a response to the protests or pre-dates them is a matter of debate in Delhi's corridors — but the CJP has made it clear that anything short of Pradhan's full removal will be treated as insufficient.

"We are waiting to see what the government decides because there are reports of a cabinet reshuffle," Dipke said. "Once that announcement comes, we will decide the next course of action."

For a generation that India's political class assumed would stay online, the cockroaches have very much arrived at the door."""

SOURCES = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com"},
    {"name": "CNN", "url": "https://www.cnn.com"},
    {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com"},
    {"name": "Wikipedia - 2026 NEET Controversy", "url": "https://en.wikipedia.org/wiki/2026_NEET_controversy"},
    {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"}
])

# ─── Image sourcing ───
print("\n=== IMAGE SOURCING ===")

# Source 1: Wikipedia image for Sonam Wangchuk
candidates = []
wiki_img = fetch_wikipedia_person_image("Sonam Wangchuk (engineer)")
if wiki_img:
    candidates.append({"url": wiki_img, "source": "wikipedia", "caption": "Climate activist Sonam Wangchuk, who began an indefinite hunger strike at Jantar Mantar on June 28", "attribution": "Wikimedia Commons"})

# Also try without disambiguation
if not wiki_img:
    wiki_img = fetch_wikipedia_person_image("Sonam Wangchuk")
    if wiki_img:
        candidates.append({"url": wiki_img, "source": "wikipedia", "caption": "Climate activist Sonam Wangchuk at a public event", "attribution": "Wikimedia Commons"})

# Source 2: Wikimedia Commons
commons = fetch_wikimedia_commons_images("Sonam Wangchuk Ladakh activist", limit=5)
for r in commons[:2]:
    title = r.get("title", "").lower()
    # relevance check
    if "wangchuk" in title or "sonam" in title or "ladakh" in title:
        candidates.append({"url": r["url"], "source": "wikimedia_commons", "caption": "Sonam Wangchuk, Ladakh activist and education reformer", "attribution": "Wikimedia Commons"})

# Also try Jantar Mantar protest
commons2 = fetch_wikimedia_commons_images("Jantar Mantar protest Delhi", limit=5)
for r in commons2[:2]:
    title = r.get("title", "").lower()
    if "jantar" in title or "protest" in title:
        candidates.append({"url": r["url"], "source": "wikimedia_commons", "caption": "Protesters at Jantar Mantar, New Delhi", "attribution": "Wikimedia Commons"})

print(f"\n  Found {len(candidates)} candidate images")

# Pick best candidate
hero_url = None
hero_caption = ""
hero_attribution = ""

if candidates:
    best = candidates[0]  # Wikipedia person image is highest priority
    print(f"  Selected: {best['source']} — {best['url'][:80]}...")
    
    # Download & compress
    raw = download_image(best["url"])
    if raw:
        compressed = compress_image(raw)
        size_kb = len(compressed) / 1024
        print(f"  Compressed: {size_kb:.0f} KB")
        
        # Upload to Supabase
        filename = f"{SLUG}.jpg"
        hero_url = upload_image_to_supabase(compressed, filename)
        if hero_url:
            print(f"  ✓ Uploaded: {hero_url[:60]}...")
            hero_caption = best["caption"]
            hero_attribution = best["attribution"]
        else:
            print("  ✗ Upload failed")
    else:
        print("  ✗ Download failed, trying next candidate...")
        for alt in candidates[1:]:
            raw = download_image(alt["url"])
            if raw:
                compressed = compress_image(raw)
                filename = f"{SLUG}.jpg"
                hero_url = upload_image_to_supabase(compressed, filename)
                if hero_url:
                    hero_caption = alt["caption"]
                    hero_attribution = alt["attribution"]
                    print(f"  ✓ Uploaded alt: {hero_url[:60]}...")
                    break

if not hero_url:
    print("  ⚠ No hero image available — proceeding without image")

# ─── Insert article ───
print("\n=== INSERTING ARTICLE ===")

article_data = {
    "headline": HEADLINE,
    "subheadline": SUBHEADLINE,
    "slug": SLUG,
    "body": BODY,
    "category": "news",
    "vertical": "politics",
    "status": "review",
    "is_editorial": False,
    "sources": SOURCES,
    "diaspora_angle": "The NEET exam scandal directly affects NRI families with children in India's education pipeline, and the movement is led by a Boston University graduate who flew back from the US to organise protests.",
    "image_url": hero_url or "",
    "image_caption": hero_caption,
    "image_attribution": hero_attribution,
    "published_at": "2026-06-30T14:30:00+00:00",
}

result = sb_insert("p2_articles", article_data)
if result:
    art_id = result.get("id", "unknown")
    print(f"  ✓ Article inserted: id={art_id}")
    print(f"  ✓ Slug: {SLUG}")
    print(f"  ✓ Status: review")
else:
    print("  ✗ Article insertion failed!")
    sys.exit(1)

print("\n=== DONE ===")
