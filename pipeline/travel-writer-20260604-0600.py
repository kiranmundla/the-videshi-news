#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-04 06:00 UTC run."""

import json, os, uuid, re, subprocess, sys, io, time
from datetime import datetime, timezone
from pathlib import Path

# -------------------------------------------------------------------
# Env setup
# -------------------------------------------------------------------
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.supabase"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

try:
    import requests
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "Pillow", "-q"])
    import requests
    from PIL import Image

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# -------------------------------------------------------------------
# Image helpers
# -------------------------------------------------------------------
def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_bytes, filename):
    """Upload image bytes to Supabase article-images bucket. Returns public URL."""
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    h = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(upload_url, headers=h, data=img_bytes, timeout=30)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"


def fetch_wikipedia_image(topic):
    encoded = topic.replace(" ", "_")
    encoded = requests.utils.quote(encoded, safe="")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{topic}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{topic}': {e}")
    return None


def fetch_wikimedia_commons(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15,
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
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []


def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def download_and_upload(url, slug):
    """Download image, compress, upload to Supabase. Returns final URL or None."""
    try:
        r = requests.get(url, headers=UA, timeout=20, stream=True)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        if "image" not in ct:
            print(f"  ⚠ Not an image: {ct}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ⚠ Image too small: {len(raw)} bytes")
            return None
        compressed = compress_image(raw)
        filename = f"{slug}.jpg"
        final_url = upload_to_supabase(compressed, filename)
        print(f"  ✓ Uploaded to Supabase: {filename} ({len(compressed)} bytes)")
        return final_url
    except Exception as e:
        print(f"  ⚠ Download/upload error: {e}")
        return None


def source_image(slug, wiki_topics, commons_queries, pexels_queries):
    """Multi-source image sourcing. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Wikipedia
    for topic in wiki_topics:
        img = fetch_wikipedia_image(topic)
        if img:
            candidates.append({"url": img, "source": "wikipedia", "priority": 1})
            break

    # Wikimedia Commons
    for q in commons_queries:
        results = fetch_wikimedia_commons(q)
        for r in results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
        if results:
            break

    # Pexels
    for q in pexels_queries:
        img = fetch_pexels(q)
        if img:
            candidates.append({"url": img, "source": "pexels", "priority": 3})
            break

    # Pick best and upload
    candidates.sort(key=lambda c: c["priority"])
    for c in candidates:
        final = download_and_upload(c["url"], slug)
        if final:
            attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
            return final, attr

    return None, None


# -------------------------------------------------------------------
# Articles
# -------------------------------------------------------------------
articles = []

# ===== ARTICLE 1: Delhi Hotel Fire - NRI Safety Guide =====
print("\n=== Article 1: Delhi Hotel Fire ===")

slug1 = make_slug("delhi-malviya-nagar-hotel-fire-nri-safety-guide")
img1, attr1 = source_image(
    slug1,
    wiki_topics=["Malviya Nagar, Delhi", "Delhi"],
    commons_queries=["Malviya Nagar Delhi", "Delhi fire safety", "Delhi hotel building"],
    pexels_queries=["Delhi building fire smoke", "India hotel safety fire escape"],
)

body1 = """Twenty-one people are dead — seventeen of them foreign nationals from Bangladesh, Nigeria, Mozambique, Liberia, and Turkmenistan — after a fire ripped through Flourish Stay, a bed-and-breakfast in Delhi's Malviya Nagar neighbourhood, on the morning of June 3. It is the capital's deadliest blaze since 2022, and for the tens of thousands of NRIs who fly relatives, friends, and themselves into Delhi every year, it carries an uncomfortable message: the budget accommodation many of them book without a second thought can be lethally unsafe.

## What Happened

The fire broke out at approximately 8:48 AM in a four-storey building that housed a restaurant on the ground floor and hotel rooms above. Delhi Fire Services deployed eight trucks. More than 40 people were rescued, many suffering smoke inhalation and fractures from jumping out of upper-floor windows. Eight patients remain on ventilator support.

The building had a single entry-and-exit point. Police say the B&B was licensed to operate six rooms under Delhi's bed-and-breakfast scheme but was running 25, with rooms carved out of the basement and upper floors. A neighbouring guesthouse, Green Residency Hotel, was found to be operating 28 rooms on a six-room licence. A criminal case has been lodged; the building's owner has been arrested, and a lookout circular has been issued for co-owner Lovkesh Bajaj, who remains at large.

Prime Minister Narendra Modi announced ex gratia payments of ₹2 lakh to the families of each victim and ₹50,000 for the injured. Delhi's chief minister ordered a city-wide crackdown on guesthouses and establishments violating fire safety norms.

## Why NRIs Should Care

Many of the dead were medical tourists — patients undergoing treatment at a nearby private hospital and their accompanying relatives, staying in cheap accommodation within walking distance. This is a pattern NRIs know well. When an ageing parent needs a procedure at AIIMS or Max Healthcare, the family books the cheapest room nearby and focuses on the medical logistics. Fire safety rarely enters the equation.

Delhi alone has an estimated 5,000-plus unregistered guesthouses and B&Bs operating in residential buildings, many with improvised electrical wiring, blocked stairwells, and no fire exits. The city's B&B licensing scheme, meant to regularise small operators, has become a loophole: owners register for six rooms and build twenty-five.

## What to Check Before You Book

For NRIs arranging accommodation in Indian cities — whether for visiting family, medical stays, or pilgrimage trips — a few checks can make the difference:

**Multiple exits.** Any hotel with only one staircase and one entry point is a potential trap. Ask before booking, or check on arrival. If there is no second exit, leave.

**Fire safety certificate.** Licensed hotels in India must display a Fire NOC (No Objection Certificate). Its absence is a red flag. The Delhi Fire Service and most state fire departments maintain online databases where you can verify a property's compliance status.

**Structural legitimacy.** Basement rooms, rooms built on rooftops, and rooms in buildings with commercial kitchens on the ground floor all carry elevated risk. A quick look at the building from outside tells you more than TripAdvisor.

**Branded chains vs. budget B&Bs.** This is not about luxury — it is about accountability. Hotels affiliated with recognised brands (even budget ones like OYO Townhouse, Lemon Tree Express, or Ginger) are audited for fire safety. An unlicensed B&B operating 25 rooms on a six-room permit is not.

**Travel insurance.** Most NRIs carry medical insurance when visiting India but not travel insurance that covers emergency evacuation. After incidents like this one, it is worth the modest premium.

## The Larger Pattern

India's hotel fire safety record is grim. The 2019 Karol Bagh fire killed 17 in a hotel that had no fire clearance. The 2022 Mundka warehouse blaze in Delhi killed 27. In each case, the post-tragedy crackdown lasted weeks before enforcement relapsed. The National Building Code mandates fire-resistant construction, sprinkler systems, and marked evacuation routes for commercial establishments — but enforcement rests with municipal bodies that are chronically understaffed and, critics allege, susceptible to corruption.

Foreign Minister S. Jaishankar confirmed the MEA is coordinating with embassies of the affected nationalities. For NRIs, the takeaway is simpler: when you book accommodation in India, especially in Delhi, treat fire safety as non-negotiable — not an afterthought.

*The death toll may rise; several of the injured remain in critical condition.*"""

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "21 Dead in Delhi Hotel Fire — What NRIs Booking Budget Stays Need to Know",
    "subheadline": "Flourish Stay in Malviya Nagar was licensed for six rooms but ran twenty-five. Seventeen of the dead were foreign nationals, many of them medical tourists. Here is a practical safety checklist for anyone arranging accommodation in Indian cities.",
    "slug": slug1,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs frequently book budget B&Bs near hospitals for visiting relatives undergoing medical procedures in Delhi, often without checking fire safety compliance. This tragedy underscores the need for a safety-first checklist.",
    "tags": ["travel", "delhi", "fire-safety", "hotels", "medical-tourism", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/delhi-crack-down-fire-safety-violations-after-blaze-that-killed-21-2026-06-04/"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/malviya-nagar-fire-pm-modi-announces-rs-2-lakh-ex-gratia-for-kin-of-deceased-after-delhi-hotel-blaze-kills-21-11748957345762.html"},
        {"name": "People", "url": "https://people.com/at-least-21-dead-after-fire-in-new-delhi-india-11738968"},
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "image_url": img1 or "",
    "image_caption": "The Malviya Nagar neighbourhood in South Delhi, site of the deadly hotel fire on June 3",
    "image_attribution": attr1 or "",
    "is_editorial": False,
    "body": body1,
})


# ===== ARTICLE 2: Monsoon Season Travel Guide for NRIs =====
print("\n=== Article 2: India Monsoon Travel Guide ===")

slug2 = make_slug("india-monsoon-travel-guide-nri-where-to-go-summer")
img2, attr2 = source_image(
    slug2,
    wiki_topics=["Kerala backwaters", "Munnar"],
    commons_queries=["Kerala backwaters monsoon", "Munnar tea plantation rain", "Western Ghats monsoon India"],
    pexels_queries=["Kerala houseboat rain monsoon", "India monsoon green mountains"],
)

body2 = """The southwest monsoon hit Kerala on June 1, right on schedule — and for the first time in eleven years, meteorologists are forecasting a below-normal season driven by a developing Super El Niño. For NRI families planning their annual summer trip to India, this is counterintuitively good news. A weaker monsoon means fewer washout days, lower humidity in hill stations, and a rare window to enjoy destinations that are normally too soggy to visit between June and September.

## The Case for Monsoon Travel

India during the monsoon is a different country. Hotel rates drop 30-50 percent from peak-season highs. Crowds at heritage sites thin out. The Western Ghats, Rajasthan's palaces, and Kerala's backwaters transform into lush, cinematic landscapes that look nothing like the dusty versions NRI families remember from their winter visits. Ayurvedic practitioners consider the monsoon the ideal season for rejuvenation therapy — the humidity opens the pores, making treatments more effective.

And now there is a financial tailwind: since April 1, 2026, the TCS (Tax Collected at Source) on overseas tour packages booked from India has been slashed from the old 5-20 percent slabs to a flat 2 percent. If your parents in India are booking a domestic travel package that includes flights, it is now significantly cheaper on the upfront cash outflow.

## Where to Go

**Kerala.** The undisputed monsoon champion. Munnar's tea plantations vanish into mist, Alleppey's houseboats glide through rain-speckled backwaters, and Wayanad's waterfalls — Soochipara, Meenmutty — are at full thundering power. June is also peak season for traditional Ayurveda retreats in Kottakkal and Thrissur, where three-week Panchakarma packages run ₹50,000-₹1,50,000 (roughly $600-$1,800) — a fraction of what similar programmes cost in Rishikesh or Bali. Book houseboats with covered indoor seating for the rain.

**Rajasthan.** The desert state undergoes a dramatic transformation in July and August. Udaipur's lakes fill up after months of being half-empty, and the City Palace and Lake Pichola look their most spectacular against overcast skies. Jodhpur's Mehrangarh Fort is striking in the rain, and Pushkar is blissfully uncrowded. Temperatures drop from the brutal 45°C of May to a manageable 32-35°C.

**Western Ghats — Coorg, Goa's Hinterland, Konkan Coast.** The Western Ghats come alive with waterfalls that exist only during the monsoon. Coorg's coffee plantations, Goa's spice farms in the interior (skip the beaches — they are rough and dangerous in monsoon), and the Konkan coast's deserted stretches between Ratnagiri and Gokarna are all at their best. Drive, do not fly — the road from Mumbai through the Sahyadris is one of India's great monsoon journeys.

**Valley of Flowers, Uttarakhand.** This UNESCO World Heritage Site in the western Himalayas is open only from June through October. The valley transforms into an alpine carpet of rare wildflowers — brahmakamal, blue poppy, cobra lily — accessible via a moderate 17-kilometre trek from Govindghat. The monsoon is not a hazard here; it is the entire reason the valley exists. Pair it with a visit to Hemkund Sahib.

## Where to Avoid

**Srinagar.** Kashmir's airport will shut down for two days a week starting in July for runway resurfacing, making logistics unpredictable. The Katra-Srinagar Vande Bharat train is running but with limited capacity. Save Kashmir for September-October, when the chinar trees turn gold and the airport is fully operational.

**Coastal Goa and Mumbai beaches.** Rough seas, rip currents, and closed beach shacks. Goa's monsoon charm is inland — the waterfalls at Dudhsagar, the spice plantations, and the Portuguese heritage quarters in Fontainhas, Panaji. Beach season resumes in October.

**Flood-prone zones.** Assam, Bihar, and parts of eastern UP experience annual flooding between July and September. Avoid unless you are visiting family and have local knowledge of conditions.

## Practical Tips for NRI Families

Pack light, synthetic fabrics that dry fast — cotton stays wet for hours in Indian humidity. Carry waterproof bags for electronics. Book refundable hotels through recognised platforms (MakeMyTrip, Booking.com, Taj/ITC direct sites) rather than unverified B&Bs — especially in the wake of the Delhi hotel fire that killed 21 on June 3. Domestic flights during monsoon face frequent delays and diversions; build buffer days into the itinerary. And if you are driving, avoid night travel on highways through the Ghats, where visibility drops to near-zero in heavy rain.

The monsoon is India's secret season — the one most NRIs skip because the weather looks bad on paper. In practice, it is when the country is at its most beautiful, most affordable, and most uncrowded. A weaker monsoon year makes it even more accessible."""

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "India's Monsoon Just Arrived — and This Year, NRIs Should Actually Visit",
    "subheadline": "A weak El Niño monsoon, half-price hotels, and slashed travel taxes make the June-September window the best-kept secret for diaspora families planning their India trip.",
    "slug": slug2,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Most NRIs schedule India trips during the winter holidays, missing the monsoon entirely. A below-normal season in 2026 creates an ideal window for budget-friendly travel to Kerala, Rajasthan, and the Western Ghats — with Ayurveda retreats at a fraction of peak-season prices.",
    "tags": ["travel", "monsoon", "india", "kerala", "rajasthan", "nri", "budget-travel"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TravelMedia.in", "url": "https://thetravelandtourismtimes.com/listicle-travelmedia-in-curates-monsoon-escapes-across-india/"},
        {"name": "VisaHQ", "url": "https://www.visahq.com/india/news/budget-2026-halves-tcs-on-overseas-tours-doubles-nri-equity-limit-to-10-percent"},
        {"name": "EaseIndiaTrip", "url": "https://www.easeindiatrip.com/blog/kerala-in-june/"},
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": img2 or "",
    "image_caption": "Kerala's backwaters during the monsoon season, when houseboats glide through rain-soaked lagoons and lush green banks",
    "image_attribution": attr2 or "",
    "is_editorial": False,
    "body": body2,
})


# -------------------------------------------------------------------
# Insert articles
# -------------------------------------------------------------------
print("\n=== Inserting articles ===")
success = 0
for art in articles:
    # Remove empty image fields
    if not art["image_url"]:
        art.pop("image_url", None)
        art.pop("image_caption", None)
        art.pop("image_attribution", None)
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        success += 1
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n=== Done: {success}/{len(articles)} articles published ===")
