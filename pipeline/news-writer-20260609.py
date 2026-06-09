#!/usr/bin/env python3
"""
News Writer — June 9, 2026 batch
Writes 3 news articles with proper image sourcing and Supabase insertion.
"""

import requests
import json
import os
import sys
import uuid
import re
from datetime import datetime, timezone
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    os.system("pip install Pillow -q")
    from PIL import Image

# Load environment
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    # strip quotes and export prefix
                    key = key.replace('export ', '').strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ---- Image sourcing functions ----

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10
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
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
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
            headers={"User-Agent": UA},
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


def fetch_pexels_image(query):
    """Fetch an image from Pexels using curl-like approach."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        import subprocess
        result = subprocess.run([
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape'
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for photo in photos:
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    result = buf.getvalue()
    print(f"  ✓ Compressed image: {len(result)//1024}KB ({img.width}x{img.height})")
    return result


def download_image(url):
    """Download an image and return bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or len(r.content) > 10000:
                print(f"  ✓ Downloaded {len(r.content)//1024}KB from {url[:60]}...")
                return r.content
        else:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'."""
    bucket = "article-images"
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_and_upload_image(slug, person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source image search → download → compress → upload. Returns (url, attribution, caption_hint)."""
    candidates = []

    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url:
            candidates.append({"url": wiki_url, "source": "wikipedia", "priority": 1})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for tq in topic_queries:
            commons = fetch_wikimedia_commons_images(tq, limit=3)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2, "title": c.get("title", "")})
            if commons:
                break

    # Source 3: Pexels (fallback for scenes/topics, NOT for people)
    if pexels_query and not person_name:
        pex_url = fetch_pexels_image(pexels_query)
        if pex_url:
            candidates.append({"url": pex_url, "source": "pexels", "priority": 3})

    # Pick best
    if not candidates:
        print(f"  ⚠ No image found for {slug}")
        return None, None, None

    candidates.sort(key=lambda x: x["priority"])
    best = candidates[0]

    # Download, compress, upload
    raw = download_image(best["url"])
    if not raw:
        # Try next candidate
        for c in candidates[1:]:
            raw = download_image(c["url"])
            if raw:
                best = c
                break
    if not raw:
        print(f"  ⚠ Could not download any image for {slug}")
        return None, None, None

    compressed = compress_image(raw)
    if len(compressed) < 5000:
        print(f"  ⚠ Compressed image too small ({len(compressed)} bytes), skipping")
        return None, None, None

    filename = f"{slug}.jpg"
    final_url = upload_to_supabase(compressed, filename)
    if not final_url:
        return None, None, None

    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
    return final_url, attribution, best.get("title", "")


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else data.get("id", "?")
        print(f"  ✓ Article inserted: {art_id} — {article['headline'][:60]}...")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# =====================================================================
# ARTICLE 1: NEET Re-Exam — IAF Security
# =====================================================================
def write_article_1():
    print("\n" + "="*70)
    print("ARTICLE 1: NEET Re-Exam — IAF to Transport Question Papers")
    print("="*70)

    slug = "neet-2026-re-exam-iaf-air-force-question-papers-lockdown-security-june-21"

    headline = "The Indian Air Force Will Fly NEET Papers to 18 Military Hubs. The Paper Setters Are Already in Lockdown."

    subheadline = "After the May exam was cancelled over a leaked paper that matched 120 questions, India is treating the June 21 re-exam like a military operation. For 22.79 lakh students, a second chance hinges on a chain of custody that now runs through the armed forces."

    body = """India's National Testing Agency has done something it has never attempted in any previous entrance examination: it has handed the physical security of NEET question papers to the Indian Air Force.

Specialised IAF aircraft will airlift sealed exam packets from a single classified printing facility to 18 strategically chosen military base hubs across the country. From those hubs, the materials will travel under armed escort to 551 cities and thousands of exam centres for the June 21 re-exam. The move, confirmed by NTA Director General Abhishek Singh, marks the first time India's armed forces have been formally embedded in the logistics of a civilian entrance test.

"For the first time, the Indian Air Force is being engaged to transport question papers, reflecting the importance being accorded to maintaining the integrity and security of the examination process," a government release stated after Singh briefed Telangana's chief secretary on preparations.

## Why the Air Force Got Involved

The original NEET-UG 2026 exam, held on May 3 for more than 22.79 lakh medical aspirants, was cancelled barely nine days later. A handwritten "guess paper" had surfaced on Telegram and WhatsApp before the test — and it matched between 120 and 140 of the actual questions. The Central Bureau of Investigation is now running a criminal probe into the leak. Multiple arrests have followed. In Parliament, the opposition demanded the education minister's resignation.

It was the second consecutive year that NEET's integrity had been compromised. In 2025, NTA faced similar allegations, though it managed to avoid a full cancellation. This time, the government had no choice. It scrapped the exam and ordered a re-test within 30 days, a timeline officials privately called a "massive logistical challenge."

## Paper Setters Under Total Lockdown

The security overhaul extends far beyond transport. According to a Times of India report, every person involved in the question paper chain — setters, moderators, translators, proofreaders — has been moved to an undisclosed location and placed under lockdown until June 21.

Mobile phones, laptops, smartwatches, and all communication devices have been confiscated. Internet access is cut off entirely. Entry and exit from the facility are being monitored around the clock. The NTA has adopted what officials described as a "zero trust" policy: no single individual has access to the complete chain of operations, from creation through printing to packaging.

"The integrity of the examination process is fully intact, and every safeguard is in place to ensure a fair and secure examination for all candidates," the NTA said in a statement, while simultaneously warning Telegram channels hawking fake papers that strict legal action would follow.

## A New Kind of Exam Logistics

The June 21 re-exam will be conducted in pen-and-paper format from 2 PM to 5:15 PM across India and in 14 cities abroad. City intimation slips were released on June 8, and admit cards are expected by June 14. Around 73,000 students will sit the exam across 208 centres in Telangana alone.

The operational framework involves the NTA coordinating with the Ministry of Defence, state police departments, and district administrations simultaneously. Telangana's Director General of Police Mahesh Bhagwat emphasised "close coordination between the police department and district administration" to ensure smooth exam-day operations, including infrastructure, power supply, transportation, and drinking water at every centre.

## The Diaspora Angle

For NRI families, the NEET saga has reinforced long-standing anxieties about India's competitive examination system. NEET is the sole gateway to undergraduate medical seats in India — including the handful reserved for NRI and OCI quota candidates. The May cancellation forced students who had travelled from the Gulf, the US, and the UK to sit for the exam to rebook flights and extend stays.

The 14 overseas exam centres remain part of the re-exam plan, but the NTA has not clarified whether IAF-grade security protocols extend to those locations. For the roughly 8,000 students who were reportedly defrauded by Telegram groups selling fake papers at prices as high as ₹10 lakh each, the re-exam is a second chance that feels more fragile than it should.

The question now is whether military-grade logistics can restore trust in an exam that determines the fate of India's future doctors. The answer arrives on June 21."""

    # Image sourcing - search for NEET exam / Indian Air Force related
    print("\n  Sourcing image...")
    img_url, img_attr, _ = source_and_upload_image(
        slug,
        topic_queries=["Indian Air Force C-17 transport", "Indian Air Force aircraft", "NEET examination India"],
        pexels_query="indian air force military aircraft"
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url or "",
        "image_caption": "An Indian Air Force transport aircraft — IAF planes will deliver NEET question papers to 18 military hubs nationwide",
        "image_attribution": img_attr or "Wikimedia Commons",
        "sources": json.dumps([
            {"name": "Careers360", "url": "https://news.careers360.com"},
            {"name": "Jagran Josh", "url": "https://www.jagranjosh.com"},
            {"name": "Shiksha", "url": "https://www.shiksha.com"},
            {"name": "Medical Dialogues", "url": "https://medicaldialogues.in"},
            {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# =====================================================================
# ARTICLE 2: INDIA Bloc Opposition Meeting
# =====================================================================
def write_article_2():
    print("\n" + "="*70)
    print("ARTICLE 2: INDIA Bloc Opposition Meeting")
    print("="*70)

    slug = "india-bloc-opposition-meeting-kharge-modi-misgovernance-unity-june-2026"

    headline = "India's Opposition Just Met in Delhi. Kharge Told Them the Economy Is Broken and Modi's Government Is the Reason."

    subheadline = "The INDIA bloc's latest show of unity comes as inflation crosses the RBI's target, fuel prices climb for the fourth time in three weeks, and the opposition tries to build on a rare Lok Sabha victory."

    body = """Congress president Mallikarjun Kharge convened a meeting of the Opposition INDIA bloc in New Delhi on June 8, urging the coalition's leaders to fortify their unity and confront what he called the Modi government's "misgovernance" across political, economic, social, and foreign policy fronts.

The meeting, attended by leaders from multiple opposition parties, was the most significant gathering of the INDIA alliance since its dramatic Lok Sabha victory in April, when the bloc defeated the government's delimitation bills.

## Kharge's Indictment

Kharge used the meeting to lay out a sweeping case against the ruling BJP. He argued that the "economic environment is extremely negative" and that new investments are not arriving at the pace needed to generate employment. He pointed to what he described as the "complete mismanagement" of the country's examination system — a reference to the NEET paper leak scandal and CBSE marking errors — saying the hopes of lakhs of students were being betrayed.

"The assault on the Constitution continues, and probe agencies are persistently being used as tools to harass, intimidate, and bully political opponents," Kharge said in his opening address.

He also targeted the government's Special Intensive Revision of electoral rolls, claiming that the voting rights of millions of people were being "stripped away" through the process — a charge the BJP has repeatedly denied.

## The April Precedent

Kharge reminded the room of the April 17 vote in the Lok Sabha, where the INDIA bloc united to defeat the Modi government's delimitation bills — a rare legislative setback for the ruling coalition. He framed that moment as proof that coordinated opposition action could work.

"On April 17, 2026, we demonstrated our unity and solidarity in the Lok Sabha in a very decisive manner, when we all came together firmly to defeat the Modi government's malicious bills on delimitation," Kharge said. "Now we must strengthen that same spirit even further."

The delimitation defeat was widely seen as a turning point. It showed that cracks in the BJP's parliamentary dominance could be exploited when the opposition presented a unified front. Since then, however, the coalition has struggled to maintain momentum on the ground, with state-level rivalries and competing leadership ambitions threatening cohesion.

## The Economic Backdrop

The meeting unfolded against a deteriorating economic backdrop that lends weight to the opposition's critique. India's consumer price inflation is expected to hit the RBI's 4% target in May — after staying below it for 15 consecutive months — driven by soaring vegetable prices and fuel cost pass-throughs from the Iran-related oil crisis.

State-owned fuel retailers have raised petrol and diesel prices four times since mid-May. Petrol is now 7.8% more expensive; diesel, 8.6% higher. Oil Minister Hardeep Singh Puri acknowledged on June 8 that prices "cannot remain at their current height for a very long time" but warned the situation could become "worrying" if the Gulf crisis expands.

Indian markets fell to two-month lows on Monday, with the Nifty 50 shedding 1.04% and the Sensex dropping 0.97%. The rupee has been under sustained pressure, and the RBI last week unveiled a $50 billion dollar-defence package — including FCNR deposit incentives for NRI investors — to stem the bleeding.

## What the NRI Diaspora Watches

For the Indian diaspora, the INDIA bloc's positioning matters less as ideology than as signal. NRIs sending remittances home — India received $43 billion in Q4 FY26, enough to tip the current account into a rare surplus — watch domestic economic stability closely. Rising fuel prices flow directly into food costs. Inflation erodes the purchasing power of the rupees their families receive.

The FCNR scheme, which the RBI expanded specifically to attract NRI deposits, is a direct acknowledgement that the government needs diaspora capital to stabilise the currency. If the opposition succeeds in making the economic pain a central electoral narrative, the calculus for NRI investors shifts.

## What Comes Next

The INDIA bloc meeting did not produce specific policy proposals or a unified economic counter-platform. That absence is the coalition's persistent weakness: it has proved more effective at blocking the government's agenda than at articulating its own.

But with monsoon session approaching, fuel prices still climbing, and the NEET scandal unresolved, the opposition has a growing list of grievances to weaponise. Whether Kharge can hold the coalition together long enough to turn those grievances into sustained political pressure will determine if the April victory was a beginning or a peak."""

    # Image sourcing - Mallikarjun Kharge
    print("\n  Sourcing image...")
    img_url, img_attr, _ = source_and_upload_image(
        slug,
        person_name="Mallikarjun Kharge",
        topic_queries=["Mallikarjun Kharge Congress president", "INDIA bloc opposition meeting"]
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url or "",
        "image_caption": "Congress president Mallikarjun Kharge addresses party leaders at the INDIA bloc meeting in New Delhi",
        "image_attribution": img_attr or "Wikimedia Commons",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# =====================================================================
# ARTICLE 3: Monsoon Late Arrival + Economic Impact
# =====================================================================
def write_article_3():
    print("\n" + "="*70)
    print("ARTICLE 3: Monsoon Arrival — Late Onset, Economic Implications")
    print("="*70)

    slug = "india-southwest-monsoon-2026-late-arrival-kerala-economic-impact-agriculture"

    headline = "The Monsoon Arrived Three Days Late. For an Economy Already Burning Through Oil Reserves, That Delay Matters."

    subheadline = "The southwest monsoon hit Kerala on June 4, later than the June 1 normal. As it crawls toward Mumbai and Delhi, India's farmers, power grid managers, and inflation watchers are all counting the same thing: days."

    body = """The southwest monsoon made landfall over Kerala on June 4, three days after its normal onset date of June 1. By June 8, the India Meteorological Department declared it had advanced into Karnataka, parts of Maharashtra and Andhra Pradesh, and most of the northeastern states. Mumbai could see its first monsoon rains between June 10 and 15. Delhi will wait until the last week of June.

In an ordinary year, a three-day delay would merit a paragraph in the weather section. This is not an ordinary year.

## An Economy Running Hot

India is absorbing the worst energy supply shock since the 2022 Russia-Ukraine crisis. The Strait of Hormuz, which carried a fifth of the world's oil before the US-Israel war on Iran, remains largely blocked. Brent crude touched $98 on Monday before settling around $94. India, which sourced more than 40% of its crude imports and 90% of its LPG through that corridor, has been forced to diversify at higher cost.

Fuel prices have risen four times since mid-May. Inflation hit the RBI's 4% target in May after staying below it for 15 straight months. The Reserve Bank held rates last week but deployed a $50 billion dollar-defence package to protect the rupee. The economy is growing, but it is growing expensive.

Into this, the monsoon arrives — late and watched more closely than usual.

## Why Three Days Matters

The southwest monsoon delivers roughly 70% of India's annual rainfall. It determines the fate of the kharif crop — rice, pulses, cotton, soybean — which accounts for about half of India's total food grain output. Agriculture contributes 17-20% of GDP and supports the livelihoods of nearly 60% of the population.

A delayed onset pushes back the sowing window. Farmers in rain-dependent regions cannot plant until the soil has absorbed enough moisture. Every day of delay compresses the growing season and increases the risk of crop stress later.

The delay also affects hydroelectric power generation. India's reservoirs need monsoon inflows to sustain generation through the summer peak demand period. With thermal power plants already consuming more coal to compensate for higher energy demand — partly driven by a severe heatwave across northern and central India — every additional day without monsoon rain adds pressure to the grid.

## The Advance So Far

The IMD's monsoon tracker shows the Northern Limit of Monsoon passing through Kannur, Chennai, and parts of the west-central Bay of Bengal as of June 8. It has fully covered Nagaland, Manipur, and Mizoram, and entered Tripura, Assam, and Arunachal Pradesh.

The immediate forecast is encouraging: the IMD expects heavy to very heavy rainfall across Kerala, Karnataka, and Tamil Nadu over the coming week. Karnataka may see isolated spells of extremely heavy rainfall between June 8 and 10. Conditions are favourable for further advance into Maharashtra, Telangana, and Odisha.

But the heatwave has not retreated. The IMD has warned that parts of northwest, central, and peninsular India will continue to experience heat-wave conditions even as the monsoon pushes north. The juxtaposition — extreme heat in the interior, heavy rain on the coasts — creates its own risks, including flash flooding in rain-receiving areas and drought stress in heatwave zones.

## The Kharif Calculus

In 2025, the monsoon arrived in Delhi on June 29, two days later than the long-term average. Despite the delay, kharif output was broadly on target because subsequent rainfall distribution was adequate. The lesson: onset timing matters, but total monsoon performance matters more.

This year, the IMD has forecast a normal monsoon overall, with cumulative rainfall expected to be within the 96-104% range of the long-period average. If that forecast holds, the late start will be a footnote.

If it does not — if the monsoon stalls, or if distribution turns erratic as El Niño patterns have historically caused — the consequences will compound with the oil crisis already underway. Food inflation, which has been the single largest contributor to CPI pressure in recent months, would accelerate. The RBI, which chose to hold rates despite crossing its 4% target, would face calls to tighten.

## What the Diaspora Sends Home

India received $43 billion in NRI remittances in the last quarter of FY26 — enough to produce a surprise current account surplus. Those remittances flow disproportionately into rural and semi-urban India, where they supplement agricultural income and fund household consumption.

When monsoon fails, remittance families feel it first: food prices rise, water scarcity forces additional spending, and the purchasing power of the rupees they receive shrinks. When monsoon succeeds, it acts as a stabiliser, keeping food affordable and rural demand healthy.

For now, the forecast says normal. The monsoon is advancing. The first real test arrives when it reaches the Indo-Gangetic plain — the rice bowl and the wheat belt — sometime in the last week of June. Until then, India watches the sky and counts the days."""

    # Image sourcing - monsoon India
    print("\n  Sourcing image...")
    img_url, img_attr, _ = source_and_upload_image(
        slug,
        topic_queries=["India monsoon rainfall Kerala", "southwest monsoon India"],
        pexels_query="monsoon rain India"
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url or "",
        "image_caption": "Monsoon clouds over the Indian coast — the southwest monsoon arrived in Kerala on June 4, three days late",
        "image_attribution": img_attr or "Pexels",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Skymet Weather", "url": "https://www.skymetweather.com"},
            {"name": "IMD", "url": "https://mausam.imd.gov.in"},
            {"name": "India Meteorological Department", "url": "https://www.imd.gov.in"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    print("="*70)
    print("The Videshi — News Writer Batch")
    print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("="*70)

    results = []
    
    # Write Article 1
    art1 = write_article_1()
    results.append(("NEET IAF Security", art1))

    # Write Article 2
    art2 = write_article_2()
    results.append(("INDIA Bloc Meeting", art2))

    # Write Article 3
    art3 = write_article_3()
    results.append(("Monsoon Late Arrival", art3))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    success = 0
    for name, art_id in results:
        status = "✓" if art_id else "✗"
        print(f"  {status} {name}: {art_id or 'FAILED'}")
        if art_id:
            success += 1
    print(f"\n  {success}/{len(results)} articles published successfully")
    print("="*70)
