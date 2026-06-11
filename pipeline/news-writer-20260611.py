#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-06-11 batch)
3 articles: NEET IAF security, VivaTech AI Partner, Modi Slovakia historic visit
"""

import json, os, sys, time, uuid, re
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# ── Image sourcing ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC images."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1200",
                "format": "json"
            },
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    results.append(url)
            if results:
                print(f"  ✓ Commons found {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def fetch_pexels(query):
    """Search Pexels for stock photos. Use curl to avoid 403."""
    if not PEXELS_KEY:
        return None
    try:
        import subprocess
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Sometimes HEAD doesn't return Content-Length, try GET
        if r.status_code == 200 and 'image' in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False


def is_banned_url(url):
    """Check if URL is from a banned source."""
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    return any(b in url for b in banned)


# ── Articles ──

articles = []

# ════════════════════════════════════════════════════════════════════
# ARTICLE 1: NEET UG 2026 — IAF Airlifts Papers, Military Lockdown
# ════════════════════════════════════════════════════════════════════

print("\n═══ ARTICLE 1: NEET UG 2026 IAF Security ═══")

# Image sourcing: Search for Indian Air Force, NTA exam, medical entrance
img1 = None
img1_caption = ""
img1_attribution = ""

# Try Wikimedia Commons for IAF or Indian exam
commons_results = fetch_wikimedia_commons("Indian Air Force C-17 transport aircraft")
if commons_results:
    for url in commons_results:
        if not is_banned_url(url) and validate_image(url):
            img1 = url
            img1_caption = "An Indian Air Force transport aircraft — IAF will deploy aircraft and Mi-17 helicopters to airlift NEET papers"
            img1_attribution = "Wikimedia Commons"
            break

if not img1:
    commons_results = fetch_wikimedia_commons("Indian Air Force Mi-17 helicopter")
    if commons_results:
        for url in commons_results:
            if not is_banned_url(url) and validate_image(url):
                img1 = url
                img1_caption = "An Indian Air Force Mi-17 helicopter used in logistics operations"
                img1_attribution = "Wikimedia Commons"
                break

if not img1:
    commons_results = fetch_wikimedia_commons("NEET examination India students")
    if commons_results:
        for url in commons_results:
            if not is_banned_url(url) and validate_image(url):
                img1 = url
                img1_caption = "Students at an examination centre in India"
                img1_attribution = "Wikimedia Commons"
                break

if not img1:
    img1 = fetch_pexels("Indian students examination hall")
    if img1 and not is_banned_url(img1) and validate_image(img1):
        img1_caption = "Students preparing for a competitive examination"
        img1_attribution = "Pexels"
    else:
        img1 = None

art1_body = """India is deploying an unprecedented military logistics operation to secure the NEET UG 2026 re-examination on June 21 — after the original May 3 test was cancelled over a devastating paper leak scandal that shook the faith of 22.8 lakh medical aspirants and their families.

For the first time in the history of Indian entrance examinations, the **Indian Air Force will airlift confidential question papers** to 18 strategic locations across the country. IAF transport aircraft and Mi-17 helicopters will carry sealed paper packets from designated distribution points to examination hubs, with military and security personnel on standby throughout the operation.

The scale of the security apparatus is staggering. Paper setters, moderators, and translators involved in preparing the question paper have been moved to an undisclosed, heavily guarded facility and placed under complete lockdown until after the examination. Mobile phones, laptops, smartwatches, and all electronic devices are banned. Internet access is cut. Entry and exit are monitored around the clock.

## The Paper Leak That Broke the System

The original NEET UG 2026 examination, conducted on May 3, was cancelled just nine days later on May 12 after allegations of a widespread paper leak surfaced. The Central Bureau of Investigation launched a probe, and multiple central agencies have since been involved in designing a new security framework from scratch.

The scandal affected over 22.8 lakh registered candidates — many of whom had spent years preparing for India's most competitive medical entrance exam. For NRI families with children aspiring to study medicine in India, the cancellation threw carefully planned timelines into chaos.

Union Education Minister Dharmendra Pradhan has publicly staked his reputation on a clean re-examination, directing officials to plug every security loophole identified during the May debacle.

## A Compartmentalised Fortress

The security framework goes far beyond airlifting papers. The entire examination chain — from question paper creation, translation, and moderation to printing, packaging, storage, and transportation — has been divided into separate compartments. No single individual or group has access to the full chain of operations, a design intended to make a repeat leak structurally impossible.

In Bihar alone, 331 examination centres have been set up across 34 districts and 35 cities, with over 1.56 lakh candidates expected to appear. The state government has placed itself on high alert, with Chief Secretary Pratyaya Amrit and DGP Vinay Kumar personally reviewing arrangements.

The Indian Postal Service has been roped in alongside the IAF, with a joint transport plan designed to deliver question papers to every examination hub within two to three hours of dispatch.

## Misinformation and Scam Warnings

Even before the re-exam, the National Testing Agency has had to fight a parallel battle against misinformation. The Press Information Bureau recently debunked a viral fake circular claiming changes to the NEET re-exam pattern, issuing a public warning that the document was not issued by NTA or any government body.

The NTA has separately dismissed claims circulating on social media about an alleged leak or sale of the June 21 question paper, calling them "false and fraudulent" and warning of strict legal action against those spreading such content.

## What It Means for Diaspora Families

For NRI families with children taking NEET — many of whom juggle preparation across time zones and fly to India specifically for the exam — the June 21 re-test is a moment of reckoning. The military-grade security is reassuring, but the emotional and financial toll of the cancellation and the three-month uncertainty has been significant.

Results from the re-exam are expected to follow swiftly, given the compressed admissions timeline. Medical college counselling, already delayed, will need to move rapidly once scores are out.

The NEET UG 2026 re-examination will be held on June 21 from 2:00 PM to 5:15 PM IST across 551 cities in India and 14 cities abroad — the largest single-day test operation India has ever mounted under military guard.

Sources: Press Trust of India, Ministry of Education, NTA, The Hindu, Jagran Josh, CurrentIndia"""

articles.append({
    "headline": "India Deploys the Air Force to Guard Its Medical Entrance Exam. That Is How Bad the Leak Was.",
    "subheadline": "IAF aircraft and Mi-17 helicopters will airlift NEET papers to 18 locations. Paper setters are in military lockdown. 22.8 lakh students are watching.",
    "slug": "india-air-force-neet-ug-2026-reexam-military-security-paper-leak-june-21-20260611",
    "body": art1_body.strip(),
    "category": "news",
    "image_url": img1,
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "sources": json.dumps(["Press Trust of India", "Ministry of Education", "NTA", "The Hindu", "Jagran Josh", "CurrentIndia"]),
    "vertical": "news"
})

# ════════════════════════════════════════════════════════════════════
# ARTICLE 2: India Named Official AI Partner Country at VivaTech 2026
# ════════════════════════════════════════════════════════════════════

print("\n═══ ARTICLE 2: India AI Partner VivaTech ═══")

img2 = None
img2_caption = ""
img2_attribution = ""

# Try Wikimedia Commons for VivaTech or IIT Madras
commons_results = fetch_wikimedia_commons("VivaTech Paris technology conference")
if commons_results:
    for url in commons_results:
        if not is_banned_url(url) and validate_image(url):
            img2 = url
            img2_caption = "VivaTech, Europe's largest technology conference, held at Paris Expo Porte de Versailles"
            img2_attribution = "Wikimedia Commons"
            break

if not img2:
    commons_results = fetch_wikimedia_commons("IIT Madras campus research technology")
    if commons_results:
        for url in commons_results:
            if not is_banned_url(url) and validate_image(url):
                img2 = url
                img2_caption = "IIT Madras, which will showcase 15 deep-tech startups at Bharat Innovates 2026 in France"
                img2_attribution = "Wikimedia Commons"
                break

if not img2:
    img2 = fetch_pexels("technology conference startup innovation exhibition")
    if img2 and not is_banned_url(img2) and validate_image(img2):
        img2_caption = "A major technology innovation showcase — India will be VivaTech 2026's Official AI Partner Country"
        img2_attribution = "Pexels"
    else:
        img2 = None

art2_body = """India will arrive in Paris next week not as a guest but as VivaTech 2026's **Official AI Partner Country** — the headline designation at Europe's largest technology and startup event, running June 17 to 20.

The announcement, first reported by the Economic Times, positions India at the centre of a global conversation about where AI work will actually get built: in domestic markets, through regional partners, or on foreign-controlled infrastructure. For the 4.5 million Indian-origin professionals working in technology across the United States, Europe, and the Gulf, the message is unmistakable — India wants to be a platform, not just a pipeline.

## Bharat Innovates: India's Deep-Tech Showcase

Before VivaTech, India's tech offensive begins with **Bharat Innovates 2026** — an international technology showcase running June 14 to 16 in Nice, organised by the Ministry of Education during the India-France Year of Innovation.

Prime Minister Narendra Modi and French President Emmanuel Macron will jointly inaugurate the event, which brings together startups, venture capital funds, and research institutions from India, France, and beyond.

**IIT Madras** will lead two of the 13 thematic areas — Blue Economy and Next-Generation Communications — and showcase 15 incubated startups alongside five flagship research projects:

- **TuTr Hyperloop** — developing practical hyperloop applications for metro rail and port cargo
- **Lab-grown diamond marking technology** — laser-based invisible QR codes and logos embedded within diamond seeds
- **5G and 6G end-to-end indigenous capabilities** — spanning hardware, software, standards, and testbeds
- **Port automation systems** — advanced logistics technology for maritime infrastructure
- **A low-compute indigenous AI ecosystem** — domain-specific, built under the National Mission on Interdisciplinary Cyber-Physical Systems

"The India-France Year of Innovation 2026 and Bharat Innovates are expected to create new opportunities for collaboration between IIT Madras and French universities, research labs, startups, and industries," said IIT Madras Director Prof. V. Kamakoti.

## VivaTech: Where India Meets European Enterprise AI

VivaTech itself has evolved into a bellwether for enterprise AI adoption. This year's edition, as TechCrunch noted, will focus heavily on the "hard part" — governance, compliance, infrastructure, and security questions that companies barely considered during the first wave of AI experimentation.

India's pitch as Official AI Partner Country comes at a moment when enterprises across Asia-Pacific are weighing where AI work gets built. The country's combination of a massive engineering talent pool, competitive costs, and growing sovereign AI ambitions gives it a distinctive position in a market increasingly wary of concentrated dependence on American cloud platforms and Chinese hardware.

Modi will attend VivaTech on June 18, his final stop on the European tour after the G7 Summit in Evian, adding prime ministerial heft to India's tech positioning.

## The Diaspora Connection

For Indian-origin tech professionals in Silicon Valley, London, and Berlin, India's AI Partner Country status signals a maturing ecosystem that may finally offer credible alternatives to building exclusively in Western markets.

The IIT showcase is particularly significant — it demonstrates that India's deep-tech capabilities now extend well beyond services and outsourcing into hardware, communications infrastructure, and frontier research.

The 13 thematic areas at Bharat Innovates span the full breadth of India's technology ambitions, from quantum computing to sustainable agriculture. That a single IIT campus is leading two of them, with 15 production-ready startups, suggests the institutional pipeline is beginning to deliver at scale.

France, for its part, sees India as a strategic technology partner — a counterweight to American and Chinese dominance in AI. The "Special Global Strategic Partnership" between the two countries, elevated earlier this year, has technology and innovation at its core.

Sources: Economic Times, TechRepublic, The Hindu Business Line, Ministry of External Affairs, IANS, TechCrunch"""

articles.append({
    "headline": "India Just Became Europe's Official AI Partner. The Pitch Starts in Nice.",
    "subheadline": "VivaTech 2026 has named India its Official AI Partner Country. IIT Madras is bringing hyperloop tech and indigenous 6G to France. Modi will seal it.",
    "slug": "india-official-ai-partner-vivatech-2026-bharat-innovates-iit-madras-deep-tech-20260611",
    "body": art2_body.strip(),
    "category": "news",
    "image_url": img2,
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "sources": json.dumps(["Economic Times", "TechRepublic", "The Hindu Business Line", "Ministry of External Affairs", "IANS", "TechCrunch"]),
    "vertical": "technology"
})


# ════════════════════════════════════════════════════════════════════
# ARTICLE 3: Modi Makes History — First Indian PM to Visit Slovakia
# ════════════════════════════════════════════════════════════════════

print("\n═══ ARTICLE 3: Modi Historic Slovakia Visit ═══")

img3 = None
img3_caption = ""
img3_attribution = ""

# Try Wikipedia for Narendra Modi
img3 = fetch_wikipedia_person_image("Narendra Modi")
if img3 and not is_banned_url(img3) and validate_image(img3):
    img3_caption = "Prime Minister Narendra Modi, who will make history as the first Indian PM to visit Slovakia"
    img3_attribution = "Wikimedia Commons"
else:
    img3 = None

if not img3:
    commons_results = fetch_wikimedia_commons("Bratislava castle Slovakia")
    if commons_results:
        for url in commons_results:
            if not is_banned_url(url) and validate_image(url):
                img3 = url
                img3_caption = "Bratislava, Slovakia — the destination for the first-ever visit by an Indian Prime Minister"
                img3_attribution = "Wikimedia Commons"
                break

if not img3:
    img3 = fetch_pexels("Bratislava Slovakia cityscape")
    if img3 and not is_banned_url(img3) and validate_image(img3):
        img3_caption = "The city of Bratislava, Slovakia"
        img3_attribution = "Pexels"
    else:
        img3 = None

art3_body = """When Narendra Modi lands in Slovakia on June 14, he will become the first Indian Prime Minister to visit the country since it gained independence in 1993 — a 33-year gap that says as much about India's evolving diplomatic ambitions as it does about Central Europe's rising strategic importance.

The state visit, at the invitation of Slovak Prime Minister Robert Fico, is the second leg of a week-long European tour that begins in Nice, France, and culminates with the G7 Summit in Evian. But the Slovakia stop is the one that breaks new ground.

## Why Slovakia, and Why Now

India's interest in Slovakia is not sentimental — it is industrial. Slovakia is a major European automotive manufacturing hub, home to production facilities for Volkswagen, Kia, Stellantis, and Jaguar Land Rover. For India, which is aggressively pushing to become a global automobile manufacturing base itself, Slovakia offers partnerships in automotive technology, supply chain expertise, and a potential gateway to European markets.

Railway manufacturing is another point of convergence. India's ambitious rail modernisation programme, including the Vande Bharat expansion and freight corridor development, aligns with Slovakia's engineering capabilities in rail systems.

The Ministry of External Affairs said the visit will "reaffirm India's commitment towards strengthening its bilateral relationship with Slovakia in various sectors, including trade, investment, and automobile and railway manufacturing."

Modi will hold talks with Prime Minister Fico and call on Slovak President Peter Pellegrini. The visit follows President Droupadi Murmu's trip to Slovakia in April 2025, which laid the diplomatic groundwork for this escalation to a full state visit.

## A Broader Central European Strategy

The Slovakia visit is part of a quiet but deliberate Indian push into Central Europe — a region that has historically received far less diplomatic attention from New Delhi than Western Europe.

For the roughly 15,000 Indian students and professionals in Slovakia and the wider Visegrád Group countries (Poland, Czech Republic, Hungary, Slovakia), the visit carries practical significance. Bilateral agreements on student exchanges, professional mobility, and mutual recognition of qualifications are expected to feature in the discussions.

Slovakia's membership in the European Union and the Eurozone also makes it a useful partner for India's broader EU engagement strategy. As India negotiates a long-delayed free trade agreement with the EU, closer ties with individual member states build leverage and goodwill.

## The Full European Tour

Modi's European itinerary unfolds across three legs. In Nice on June 14, he meets French President Emmanuel Macron for bilateral talks and jointly inaugurates 'Bharat Innovates', a showcase of Indian deep-tech startups. The India-France relationship was elevated to a Special Global Strategic Partnership earlier this year.

From June 14 to 16, the historic Slovakia stop. Then, from June 16 to 17, the G7 Summit in Evian, where a bilateral meeting with US President Donald Trump is expected to cover trade, H-1B visas, and energy cooperation.

The tour wraps in Paris on June 18, where Modi will attend VivaTech, Europe's largest technology and startup event, where India has been named the Official AI Partner Country.

## The NRI Angle

For the Indian diaspora in Europe, Modi's tour is the most significant European engagement in years. The combination of France's tech corridor, Slovakia's manufacturing partnerships, the G7's geopolitical stage, and India's AI Partner Country status at VivaTech amounts to a diplomatic offensive aimed squarely at repositioning India as a European partner of first resort.

The Slovakia visit, specifically, opens a new corridor. Indian automobile and engineering companies looking to establish European operations now have a bilateral framework to build on — something that did not exist 33 years after Slovakia's independence.

Sources: Ministry of External Affairs, Reuters, IANS, Outlook Business, Devdiscourse, Livemint"""

articles.append({
    "headline": "No Indian PM Has Visited Slovakia in 33 Years. Modi Is About to Change That.",
    "subheadline": "India's first-ever prime ministerial visit to Slovakia targets automotive and railway manufacturing partnerships — and a deeper foothold in Central Europe.",
    "slug": "modi-first-indian-pm-visit-slovakia-europe-tour-automotive-railway-20260611",
    "body": art3_body.strip(),
    "category": "news",
    "image_url": img3,
    "image_caption": img3_caption,
    "image_attribution": img3_attribution,
    "sources": json.dumps(["Ministry of External Affairs", "Reuters", "IANS", "Outlook Business", "Devdiscourse", "Livemint"]),
    "vertical": "politics"
})

# ── Insert into Supabase ──

print("\n═══ INSERTING ARTICLES ═══")
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

success_count = 0
for art in articles:
    if not art["image_url"]:
        print(f"  ⚠ SKIPPING '{art['headline'][:50]}...' — no valid image found")
        continue

    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "vertical": art["vertical"],
        "image_url": art["image_url"],
        "image_caption": art["image_caption"],
        "image_attribution": art["image_attribution"],
        "sources": art["sources"],
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "created_at": now
    }

    print(f"\n  → Inserting: {art['headline'][:60]}...")
    print(f"    Image: {art['image_url'][:80]}...")

    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=15
        )
        if r.status_code in (200, 201):
            resp = r.json()
            aid = resp[0]['id'] if isinstance(resp, list) else resp.get('id', 'unknown')
            print(f"    ✓ Inserted (id={aid}, status=review)")
            success_count += 1
        else:
            print(f"    ✗ Failed: {r.status_code} — {r.text[:200]}")
    except Exception as e:
        print(f"    ✗ Error: {e}")

print(f"\n═══ DONE: {success_count}/{len(articles)} articles inserted ═══")
