#!/usr/bin/env python3
import json, os, uuid, re, io, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ---- Load env ----
for cand in [Path.home()/".env.supabase", Path.home()/"workspace"/".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ---- Image helpers ----
def fetch_commons(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers=UA, timeout=20)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            out = []
            for _, p in pages.items():
                ii = p.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 600:
                    continue
                out.append({"url": ii.get("thumburl") or ii.get("url"),
                            "title": p.get("title", ""), "width": ii.get("width", 0)})
            return out
    except Exception as e:
        print(f"  Commons error: {e}")
    return []

def download(url):
    try:
        r = requests.get(url, headers=UA, timeout=60)
        if r.status_code == 200 and r.content and len(r.content) > 5000:
            return r.content
        # curl fallback for 429
        import subprocess, tempfile
        tf = tempfile.NamedTemporaryFile(suffix=".img", delete=False)
        subprocess.run(["curl", "-sS", "-A", UA["User-Agent"], "-o", tf.name, url], timeout=90)
        data = Path(tf.name).read_bytes()
        os.unlink(tf.name)
        if len(data) > 5000:
            return data
    except Exception as e:
        print(f"  download error: {e}")
    return None

def compress(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "image/jpeg", "x-upsert": "true"},
        data=jpeg_bytes, timeout=90)
    if r.status_code not in (200, 201):
        print(f"  upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def source_hero(search_queries, slug):
    """Try a list of Commons search queries, return (public_url) or None."""
    for q in search_queries:
        results = fetch_commons(q)
        for r in results:
            data = download(r["url"])
            if not data:
                continue
            try:
                jpeg = compress(data)
            except Exception as e:
                print(f"  compress error: {e}")
                continue
            if len(jpeg) < 10000:
                continue
            url = upload_supabase(jpeg, f"{slug}.jpg")
            if url:
                print(f"  ✓ hero from Commons '{q}': {r['title']}")
                return url, r["title"]
    return None, None

# ---- Articles ----
ai_body = """Air India has launched a service it is calling **Easy Connect**, and the name undersells what it actually does. For the first time, a flyer in Varanasi can check a bag, clear immigration formalities at their home airport, and have that single booking carry them through Delhi onto a long-haul flight to New York, London or Toronto — without re-checking luggage or queuing at a foreign transit desk. The pilot route, Varanasi–Delhi, went live on June 25, with Air India designated the lead carrier for the government's hub-and-spoke aviation model.

For the Indian diaspora, this is less about a single city and more about the architecture of how families fly home.

## What "Easy Connect" actually changes

The premise is simple and long overdue. Today, a large share of Indians flying internationally from smaller cities first hop to Delhi, Mumbai or Bengaluru, collect their bags, re-check them, and start the security-and-immigration cycle over again. Many bypass India's own hubs entirely and connect through Dubai, Doha or Singapore instead.

Easy Connect folds the domestic and international legs into one coordinated itinerary. Passengers book both sectors together — through Air India's website, app, call centre or an agent — complete baggage check-in and immigration at the originating airport, and transit Delhi on a schedule built to minimise layovers. The bag is tagged to the final destination; the traveller clears formalities once.

After Varanasi, Air India plans to extend the model to 11 more cities: Ahmedabad, Amritsar, Chennai, Goa, Guwahati, Hyderabad, Kochi, Mumbai, Patna, Vadodara and Visakhapatnam, feeding the international hubs at Delhi, Mumbai and Bengaluru.

## Why this matters to NRIs

Most diaspora families do not live in metros. They come from Amritsar, Vadodara, Patna, Vizag — the Tier-II and Tier-III cities Easy Connect is built around. For a Gujarati family in New Jersey flying parents over from Ahmedabad, or a Punjabi household in Toronto routing relatives through Amritsar, the friction has never been the long-haul leg. It has been the messy domestic connection at the other end: the bag that didn't make it, the re-check line, the missed onward flight when a feeder runs late.

Campbell Wilson, Air India's chief executive, framed the initiative as making foreign travel "more accessible to Bharat" — to passengers beyond the big metros who have long depended on overseas transit hubs. Nipun Aggarwal, the airline's chief commercial officer, has pitched the wider network expansion as a bet on long-haul growth through 2026.

There is a strategic subtext for the diaspora too. Every passenger Easy Connect keeps inside India's own network is one not spending three extra hours in a Gulf terminal. For elderly parents travelling alone — the people NRIs worry about most — a single through-checked itinerary with formalities handled at the home airport removes exactly the part of the journey that goes wrong.

## The catch, and what to watch

This is a phased rollout, and the gap between announcement and reliable execution is where Indian aviation has stumbled before. Through-check immigration at a Tier-II airport depends on staffing and systems that have to actually work on a Tuesday morning in monsoon season, not just in a press release. The Varanasi pilot is the proof of concept; the 11-city expansion is the real test.

NRIs booking for the festive season should treat Easy Connect as a feature to ask for by name, not assume. When it covers your home city, it is a genuinely better way to move a family from a small Indian town to a US or Canadian gateway — fewer bags lost, fewer connections blown, one set of formalities instead of two.

For now, watch the city list. The moment Easy Connect reaches Amritsar, Ahmedabad or Kochi, the calculus of booking a parent's ticket home changes for a very large slice of the diaspora."""

uae_body = """If you are an Indian national in the UAE who needs a passport renewal, a visa stamp or a document attested, the next few days are a dead zone. The Indian Embassy in Abu Dhabi has paused all routine passport, visa and attestation services across the Emirates from **June 26 to June 30**, as it switches the company that runs its consular front desk. New applications, appointments and standard services will not be processed during the five-day window.

The pause marks the end of an era: BLS International and SGIVS Global, which stopped accepting new applications after June 25, are being replaced. From July 1, **Al Hind Tours and Travels LLC** takes over.

## What is closed, and what is not

The freeze covers the three services Indians in the Gulf use most — passport work, visa processing and document attestation. Routine bookings resume after June 30, once the new system is live.

Emergency consular services stay open throughout. The Embassy of India in Abu Dhabi and the Consulate General of India in Dubai will handle urgent cases directly. The mission has published help channels for the transition:

- Toll-free: 800 46342
- WhatsApp: +971 54 309 0571
- Email: pbsk.dubai@mea.gov.in

Crucially, anything filed before the cut-off still moves: applications lodged through BLS or SGIVS before the transition will continue to be processed through the existing centres.

## Why a UAE story matters to the wider diaspora

The Gulf holds the single largest concentration of overseas Indians anywhere — and the UAE is its beating heart, with millions of Indian passport holders. BLS had run this outsourcing since 2011; handing it to a new operator is one of the biggest resets in the diaspora's consular landscape in over a decade.

For NRIs in the US, UK and Canada, the relevance is twofold. First, families are rarely contained by one country: a Houston engineer's brother may be in Dubai, parents shuttling between Kochi and Sharjah. A five-day consular blackout in the Emirates ripples through extended families that plan travel, OCI cards and attestations across borders together. Second, this is a template. India routinely re-tenders these outsourced contracts, and the same churn — a new provider, a transition freeze, fresh portals and centres — surfaces periodically in North American and European consular jurisdictions too. The UAE switch is a preview of how the disruption plays out: a short, sharp pause, then a new vendor.

## What changes on July 1

Al Hind won the contract as the lowest bidder, quoting a unified, all-inclusive fee of Dh19 per transaction — notably cheaper than the outgoing arrangement, with document handling and photography bundled in. It plans to roll out **16 Indian Consular Application Centres** across the UAE, with a dedicated online portal for appointments.

The full service menu is broad: passport renewals, visa applications, Overseas Citizen of India cards, Police Clearance Certificates, surrender certificates, Global Entry Programme verification and attestation. The embassy says core procedures will stay largely unchanged; details on centre locations, hours, fees and appointment steps are being released ahead of the switch.

## Practical advice

If your paperwork can wait, it should — try to file before June 25 through the existing centres, or hold until the new system stabilises in early July rather than racing the transition. If you have a genuine emergency — an expired passport before a flight, a death or medical crisis at home — use the embassy's direct emergency channels above; those do not stop.

And whatever you read on WhatsApp forwards in the coming days, verify it against the embassy's official handles. Provider changes are exactly the moment when fake "expedite" agents and lookalike booking sites multiply. The Dh19 official fee is the number to remember; anything dramatically higher is someone making a margin on your anxiety."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's New 'Easy Connect' Lets You Clear Immigration in Your Hometown — and It's Built for the Diaspora's Tier-2 Roots",
        "subheadline": "A single booking from Varanasi to New York, with bags and formalities handled at the home airport. The model is coming to 11 more Indian cities most NRIs actually fly from.",
        "slug": make_slug("air-india-easy-connect-hub-spoke-tier2-cities-diaspora-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Most NRI families fly home through Tier-2 cities like Amritsar, Ahmedabad and Vizag, not metros — Easy Connect's through-checked baggage and single-point immigration removes the messy domestic connection that most often strands elderly parents and loses luggage.",
        "tags": ["travel", "airlines", "air india", "aviation", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-launches-easy-connect-service/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-make-foreign-travel-more-accessible-to-bharat-ai-ceo/article69730000.ece"},
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "An Air India aircraft on the apron; the carrier's Easy Connect model links Tier-2 cities to its Delhi hub.",
        "image_attribution": "Wikimedia Commons",
        "body": ai_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Consular Services in the UAE Go Dark for Five Days — Here's the June 26–30 Survival Guide Before Al Hind Takes Over",
        "subheadline": "BLS and SGIVS are out after a decade; a new provider starts July 1 at Dh19 a transaction. Passport, visa and attestation work pauses — but emergencies don't.",
        "slug": make_slug("uae-indian-consular-services-suspended-june-al-hind-bls-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "The UAE holds the world's largest concentration of Indian passport holders and is woven into NRI families everywhere; a five-day consular freeze ripples across borders, and the provider switch previews the same churn that periodically hits North American and European missions.",
        "tags": ["travel", "visa", "passport", "uae", "consular", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/uae-indian-consular-services-to-be-suspended-for-five-days-from-june-26"},
            {"name": "Gulf Business", "url": "https://gulfbusiness.com/uae-alhind-replaces-bls-in-indian-consular-services-shift/"},
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/global/destinations/india-appoints-new-visa-and-passport-service-provider-in-the-uae/"},
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_caption": "An Indian passport; consular services in the UAE pause June 26–30 during a provider transition.",
        "image_attribution": "Wikimedia Commons",
        "body": uae_body,
    },
]

# ---- Source heroes ----
img_queries = {
    articles[0]["slug"]: ["Air India Boeing 787", "Air India aircraft", "Air India airplane Indira Gandhi airport"],
    articles[1]["slug"]: ["Indian passport", "Republic of India passport", "Indian passport biometric"],
}

for art in articles:
    url, title = source_hero(img_queries[art["slug"]], art["slug"])
    if url:
        art["image_url"] = url
    else:
        print(f"  ⚠ no hero for {art['slug']} — inserting without image")

# ---- Insert ----
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  (img={'yes' if art.get('image_url') else 'NO'})")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
