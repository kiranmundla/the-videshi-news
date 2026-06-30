#!/usr/bin/env python3
"""Writer script: India-Canada diplomatic reset under PM Carney."""

import os, sys, json, requests, io, subprocess, urllib.parse

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
        print(f"  ⚠ Wikipedia error: {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200",
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
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

import re
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

def _keywords(text):
    toks = re.findall(r"[A-Za-z][A-Za-z'-]+", text or "")
    return [t.lower() for t in toks if len(t) >= 4 and t.lower() not in _COMMONS_STOP]

def commons_relevance_ok(commons_title, headline, topic=""):
    title_l = (commons_title or "").lower()
    if not title_l:
        return False
    kws = set(_keywords(headline)) | set(_keywords(topic))
    if not kws:
        return True
    return any(kw in title_l for kw in kws)

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
        elif r.status_code == 429:
            print(f"  ⚠ 429, trying curl...")
    except Exception as e:
        print(f"  ⚠ requests error: {e}")
    tmp = "/tmp/hero_download2.jpg"
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", tmp, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip() == "200" and os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
            with open(tmp, "rb") as f:
                return f.read()
    except Exception as e:
        print(f"  ⚠ curl error: {e}")
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
        print(f"  ⚠ Upload failed {r.status_code}: {r.text[:200]}")
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

# ─── Article ───

SLUG = "india-canada-reset-modi-carney-cepa-trade-uranium-defence-diaspora-20260630"
HEADLINE = "Modi and Carney Have Met Four Times in Under a Year. Here's What India and Canada Just Agreed To."
SUBHEADLINE = "A C$2.6 billion uranium deal, a defence pact, a free trade agreement by December, and 300 research scholarships — the India-Canada relationship has turned around so fast that neither side seems sure what to do with the momentum."

BODY = """Two years ago, India and Canada couldn't stay in the same room. Diplomats were expelled. Consulates were shuttered. Visa services were suspended. The Trudeau government's allegations of Indian involvement in the killing of Khalistani separatist Hardeep Singh Nijjar in British Columbia — allegations India dismissed as "absurd" — had cratered a relationship that generations of Indian-Canadians had spent decades building.

Today, the two countries are negotiating a free trade agreement, a military intelligence-sharing pact, a uranium supply deal, and 300 fully funded research internships for Indian students. Prime Minister Modi has a standing invitation to visit Ottawa. And the man who made it all possible — Canadian Prime Minister Mark Carney — has met Modi four times in less than a year.

"It was a delight to meet Prime Minister Carney on the sidelines of the Evian G7 Summit," Modi posted on X after their most recent meeting on June 17. "In less than a year, it is our fourth meeting, indicating our commitment to strong India-Canada ties."

## What Changed

The short answer is: the prime minister.

Carney, a former Bank of Canada and Bank of England governor who replaced Justin Trudeau in October 2025, inherited a relationship in ruins. But he also inherited a strategic imperative. Canada was scrambling to diversify beyond the United States, its dominant trading partner, after years of trade friction under Trump. India, with its 1.4 billion consumers and its position as a counterweight to China, was the obvious pivot.

The reset began at the G7 Summit in Kananaskis, Alberta in June 2025, where Carney invited Modi as a guest — a gesture Trudeau had never extended. By March 2026, Carney was in New Delhi for his first official visit, signing deals on uranium, energy, critical minerals, and artificial intelligence. By May, Commerce Minister Piyush Goyal was leading India's largest-ever business delegation to Ottawa and Toronto.

At every step, the diplomatic language shifted from forensic to forward-looking. The Nijjar investigation quietly continued through law enforcement channels, but the political conversation moved elsewhere.

## The Deals on the Table

The centrepiece is the Comprehensive Economic Partnership Agreement (CEPA), a full free trade pact that both sides have committed to concluding by the end of 2026. The target: $50 billion in bilateral trade by 2030, up from roughly $8.7 billion today. If completed, it would be one of India's most significant trade agreements since the India-UK FTA that takes effect on July 15.

But the deal sheet extends well beyond tariffs:

- **Uranium**: A C$2.6 billion long-term supply agreement between Canada's Cameco and India's Department of Atomic Energy for uranium ore concentrates — critical for India's nuclear energy expansion.
- **Defence**: The two countries have launched negotiations on a General Security of Information Agreement (GSOIA), a prerequisite for sharing classified military intelligence. An India-Canada defence dialogue has been formally established.
- **Energy**: Commercial arrangements covering LNG, LPG, crude oil, and refined petroleum, with Canada positioning itself as a long-term LNG supplier to the Indo-Pacific.
- **Critical minerals**: A new MOU to strengthen clean energy and advanced manufacturing supply chains — Canada sits on some of the world's largest deposits of lithium, cobalt, and nickel.
- **Education**: A pact between India's AICTE and Canada's Mitacs will fund up to 300 research internships annually for Indian students starting in 2027. Twenty-four institutional partnerships spanning AI, healthcare, and agriculture were also announced.
- **Technology**: A trilateral MOU among India, Canada, and Australia on emerging tech cooperation, including AI and digital infrastructure.
- **Dialogue platforms**: The creation of "Raisina Americas," a new forum modelled on India's flagship Raisina Dialogue, to deepen India-Canada strategic conversation.

## Why the Diaspora Should Pay Attention

For the 1.8 million people of Indian origin in Canada — the largest diaspora population outside the United States — the reset is more than diplomatic ceremony.

The Trudeau-era rupture hit them hardest. Students saw visa processing freeze. Families postponed visits. Business owners in Punjab watched NRI traffic dry up. Community organisations navigated an atmosphere where being Indian and being Canadian felt, for the first time, like a contradiction.

The Carney government has worked to undo that damage, but the underlying tensions haven't disappeared. Khalistan-related extremism remains a live issue — temple vandalism, extortion threats against Hindu-Canadians, and the activities of Gurpatwant Singh Pannun's "Sikhs for Justice" continue to strain community relations. The GSOIA and defence dialogue signal that both governments now treat these as shared security problems rather than diplomatic irritants.

For NRIs considering business or education in Canada, the CEPA timeline matters. A completed agreement would reduce tariffs on Indian goods, ease services trade, and create clearer rules for investment — potentially making Canada a more attractive destination for Indian capital at a time when the country is actively courting non-US partners.

"A forward-looking CEPA can provide predictability for investors, facilitate mobility of talent, and deepen collaboration in critical minerals," said Agneshwar Sen, trade policy leader at EY India. "The presence of a significant Indian diaspora in Canada will be an added factor in positioning both economies for resilient, long-term growth."

The question now is whether the momentum holds. Modi has accepted Carney's invitation to visit Canada later this year — a trip that would be the first by an Indian prime minister since the relationship collapsed. If it happens, it will close one of the most dramatic diplomatic arcs in recent Indo-Pacific history."""

SOURCES = json.dumps([
    {"name": "Livemint", "url": "https://www.livemint.com"},
    {"name": "The Indian Eye", "url": "https://theindianeye.com"},
    {"name": "Reuters", "url": "https://www.reuters.com"},
    {"name": "Ministry of External Affairs, India", "url": "https://www.mea.gov.in"},
    {"name": "Wikipedia - Canada-India relations", "url": "https://en.wikipedia.org/wiki/Canada%E2%80%93India_relations"}
])

# ─── Image sourcing ───
print("\n=== IMAGE SOURCING ===")
candidates = []

# Try Mark Carney
wiki_img = fetch_wikipedia_person_image("Mark Carney")
if wiki_img:
    candidates.append({"url": wiki_img, "caption": "Canadian Prime Minister Mark Carney, who has met PM Modi four times in under a year", "attribution": "Wikimedia Commons"})

# Try Modi Carney on Commons
commons = fetch_wikimedia_commons_images("Modi Carney India Canada", limit=5)
for r in commons[:3]:
    if commons_relevance_ok(r.get("title",""), HEADLINE, "Modi Carney"):
        candidates.append({"url": r["url"], "caption": "PM Modi with Canadian PM Mark Carney", "attribution": "Wikimedia Commons"})

# Also try India Canada trade
commons2 = fetch_wikimedia_commons_images("India Canada trade summit", limit=5)
for r in commons2[:2]:
    if commons_relevance_ok(r.get("title",""), HEADLINE, "India Canada"):
        candidates.append({"url": r["url"], "caption": "India-Canada diplomatic engagement", "attribution": "Wikimedia Commons"})

print(f"  Found {len(candidates)} candidates")

hero_url = None
hero_caption = ""
hero_attribution = ""

for c in candidates:
    raw = download_image(c["url"])
    if raw:
        compressed = compress_image(raw)
        print(f"  Compressed: {len(compressed)/1024:.0f} KB")
        hero_url = upload_image_to_supabase(compressed, f"{SLUG}.jpg")
        if hero_url:
            hero_caption = c["caption"]
            hero_attribution = c["attribution"]
            print(f"  ✓ Uploaded: {hero_url[:60]}...")
            break
        else:
            print("  ✗ Upload failed, trying next...")

if not hero_url:
    print("  ⚠ No hero image available")

# ─── Insert ───
print("\n=== INSERTING ARTICLE ===")

article_data = {
    "headline": HEADLINE,
    "subheadline": SUBHEADLINE,
    "slug": SLUG,
    "body": BODY,
    "category": "nri-world",
    "vertical": "diplomacy",
    "status": "review",
    "is_editorial": False,
    "sources": SOURCES,
    "diaspora_angle": "Canada is home to 1.8 million Indian-origin people — the diplomatic reset directly affects visa processing, education pathways, business opportunities, and community safety for the largest Indian diaspora outside the US.",
    "image_url": hero_url or "",
    "image_caption": hero_caption,
    "image_attribution": hero_attribution,
    "published_at": "2026-06-30T15:00:00+00:00",
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
