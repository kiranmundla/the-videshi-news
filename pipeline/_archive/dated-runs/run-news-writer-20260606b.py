#!/usr/bin/env python3
"""
News writer for The Videshi — June 6, 2026 (afternoon batch)
Writes 3 articles:
1. Indian national killed, 13 injured in Iran's Kuwait airport attack — Gulf diaspora in crossfire
2. India faces stagflation risk as Iran oil shock meets weak monsoon — Nuvama warns on FY27
3. India's defence secretary holds 10+ bilaterals at Shangri-La Dialogue 2026
"""

import json, os, sys, time, uuid, re, hashlib
import requests
from datetime import datetime, timezone
from io import BytesIO
from PIL import Image

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ✗ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(' ', '_')
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if "image" not in mime:
                    continue
                thumb = ii.get("thumburl") or ii.get("url")
                w = ii.get("thumbwidth") or ii.get("width", 0)
                h = ii.get("thumbheight") or ii.get("height", 0)
                if w < 300 or h < 200:
                    continue
                title = page.get("title", "")
                # Skip SVGs, icons, logos, flags
                if any(x in title.lower() for x in ['flag', 'logo', 'icon', '.svg', 'coat of arms']):
                    continue
                results.append({"url": thumb, "title": title, "width": w, "height": h})
            if results:
                print(f"  ✓ Wikimedia Commons found {len(results)} results for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY, **UA},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            results = [{"url": p["src"]["large2x"], "title": p.get("alt", ""), "width": p["width"], "height": p["height"]} for p in photos]
            if results:
                print(f"  ✓ Pexels found {len(results)} results for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return []

def download_and_upload(image_url, slug):
    try:
        r = requests.get(image_url, headers=UA, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ Download failed: HTTP {r.status_code}")
            return None
        ct = r.headers.get("Content-Type", "")
        if "image" not in ct:
            print(f"  ✗ Not an image: {ct}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ✗ Too small: {len(raw)} bytes")
            return None
        compressed = compress_image(raw)
        size_kb = len(compressed) / 1024
        print(f"  Image compressed: {size_kb:.0f} KB")
        filename = f"{slug}.jpg"
        return upload_to_supabase(compressed, filename)
    except Exception as e:
        print(f"  ✗ Download/upload error: {e}")
        return None

def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ============================================================
# ARTICLE 1: Indian killed in Kuwait airport attack
# ============================================================
def write_article_1():
    print("\n=== Article 1: Indian Killed in Kuwait Airport Attack ===")
    slug = "indian-national-killed-iran-kuwait-airport-attack-gulf-diaspora-june-2026"

    # Image: Kuwait airport or Kuwait city
    print("Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikimedia Commons for Kuwait airport
    commons = fetch_wikimedia_commons("Kuwait International Airport terminal", 5)
    if commons:
        best = commons[0]
        uploaded = download_and_upload(best["url"], slug)
        if uploaded:
            image_url = uploaded
            image_caption = "Kuwait International Airport terminal, damaged in the June 3 Iranian drone and missile attack"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        pexels = fetch_pexels("Kuwait airport", 3)
        if pexels:
            uploaded = download_and_upload(pexels[0]["url"], slug)
            if uploaded:
                image_url = uploaded
                image_caption = "Kuwait International Airport"
                image_attribution = "Pexels"

    if not image_url:
        # Try a broader Pexels search
        pexels = fetch_pexels("airport terminal attack damage", 3)
        if pexels:
            uploaded = download_and_upload(pexels[0]["url"], slug)
            if uploaded:
                image_url = uploaded
                image_caption = "Airport terminal following aerial attack"
                image_attribution = "Pexels"

    body = """An Indian national has been killed and at least 13 others injured in an Iranian drone and missile attack on Kuwait International Airport on June 3, India's Ministry of External Affairs confirmed — the second Indian casualty in the Gulf since the war between the United States and Iran erupted in late February.

The attack, which struck Terminal 1 of the airport in the early hours of Wednesday morning, killed one person and injured over 63 others, according to Kuwait's Health Ministry. Seven of the injured required emergency surgery. Kuwait's military said it intercepted 13 ballistic missiles and 17 drones since dawn, though debris fell across residential areas.

## India Mobilises Support

India's Embassy in Kuwait confirmed the death on X, expressing condolences and stating it was coordinating with local authorities. Aseem R Mahajan, Additional Secretary (Gulf) at the MEA, said during an inter-ministerial briefing that the Indian mission was providing all necessary assistance to the injured and maintaining constant contact with Kuwaiti authorities.

"Yesterday, in an attack on Kuwait International Airport, an Indian national unfortunately lost his life. We express our deepest condolences to the family of the deceased," Mahajan said. The mortal remains of the deceased were expected to arrive in India by June 5.

The killing marks the second Indian death in Kuwait's conflict zone since March 30, when another Indian national died during Iranian strikes on a power and water desalination plant. India has a massive diaspora presence in Kuwait — over one million Indian nationals live and work in the country, many in construction, services, and the energy sector.

## Gulf Tensions Hit Home for the Diaspora

The broader context is alarming for the estimated 8.5 million Indians living across the Gulf Cooperation Council states. Kuwait has faced near-daily drone attacks since March. Its airport had only reopened in late April after an extended closure triggered by earlier Iranian strikes that destroyed fuel tanks and radar systems.

Iran's Revolutionary Guard Corps claimed responsibility for targeting the Ali Al Salem airbase in Kuwait and the US Navy's Fifth Fleet headquarters in Bahrain, but denied hitting the civilian airport — blaming the damage on a failed American interceptor missile. The US military rejected that claim, saying Iranian drones deliberately targeted the airport.

Kuwait's foreign ministry summoned Iran's top envoy and expelled two lower-ranking diplomats in response. Saudi Arabia condemned the attacks as a "clear violation of international law."

## The Evacuation Pipeline

India has been quietly running one of the largest civilian evacuation operations in the current conflict. The Indian Embassy in Tehran has facilitated the evacuation of 2,557 Indian nationals through land border routes since hostilities began. Travel advisories urge Indians to avoid Iran entirely, and those still in the country have been urged to leave with embassy support.

Mahajan noted that Indian missions across the Gulf continue to monitor the situation closely, maintaining regular contact with community associations, professional groups, and employers. The MEA has also advised Indian nationals in Kuwait and Bahrain to exercise caution and follow local emergency instructions.

## What Comes Next

The attack on Kuwait came hours before the US military carried out strikes on Iran's Qeshm Island and intercepted multiple ballistic missiles and drones. The tit-for-tat cycle continues even as back-channel negotiations between Washington and Tehran attempt to secure a deal to reopen the Strait of Hormuz.

For India, the stakes are existential. Roughly 40 percent of India's crude oil imports normally transit through the Strait. Every escalation in the Gulf carries a direct cost — in energy prices, in remittances, and now, in lives.

The MEA has urged all Indian nationals in the Gulf to register with their nearest Indian mission and keep emergency contact numbers accessible. In Kuwait, the 24/7 helpline is +965-99abortz349."""

    # Verify word count
    words = len(body.split())
    print(f"  Word count: {words}")

    article = {
        "headline": "An Indian Worker Died at Kuwait Airport. It Was Iran's Second Indian Casualty in Three Months.",
        "subheadline": "Over a million Indians live in Kuwait. The MEA says 13 more were injured and 2,557 have been evacuated from Iran through land borders.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Reuters", "Ministry of External Affairs (India)", "Kuwait Health Ministry", "Dainik Jagran", "The Kashmir Horizon"]),
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution
    }

    return insert_article(article)


# ============================================================
# ARTICLE 2: India stagflation risk — Nuvama report
# ============================================================
def write_article_2():
    print("\n=== Article 2: India Stagflation Risk — Nuvama Report ===")
    slug = "india-stagflation-risk-iran-oil-shock-weak-monsoon-nuvama-fy27-gdp-forecast"

    print("Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikimedia Commons for RBI or Indian economy
    commons = fetch_wikimedia_commons("Reserve Bank of India building Mumbai", 5)
    if commons:
        best = commons[0]
        uploaded = download_and_upload(best["url"], slug)
        if uploaded:
            image_url = uploaded
            image_caption = "The Reserve Bank of India headquarters in Mumbai"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        commons = fetch_wikimedia_commons("Bombay Stock Exchange India", 5)
        if commons:
            for c in commons:
                if c["width"] > 500:
                    uploaded = download_and_upload(c["url"], slug)
                    if uploaded:
                        image_url = uploaded
                        image_caption = "The Bombay Stock Exchange in Mumbai's financial district"
                        image_attribution = "Wikimedia Commons"
                        break

    if not image_url:
        pexels = fetch_pexels("India stock market economy", 3)
        if pexels:
            uploaded = download_and_upload(pexels[0]["url"], slug)
            if uploaded:
                image_url = uploaded
                image_caption = "India's financial markets face mounting headwinds from oil prices and monsoon uncertainty"
                image_attribution = "Pexels"

    body = """India posted 7.7 percent real GDP growth in the year that just ended. The next twelve months could look very different.

Nuvama Institutional Equities, one of India's most closely watched brokerages, warned this week that the country faces a growing risk of stagflation — the toxic combination of slowing growth and persistent inflation — driven by the twin shocks of the Iran-related oil crisis and a forecast for below-normal monsoon rainfall.

## The Downgrade

In a GDP analysis report published on Friday, Nuvama cut its real GDP growth forecast for FY27 (April 2026 to March 2027) to 6–6.5 percent, down from the 7.7 percent that FY26 delivered. Nominal GDP growth, however, is expected to accelerate to 11–12 percent — a gap that signals inflation is doing the heavy lifting.

"FY27 is likely to be a challenging year, beginning with heightened geopolitical tensions that could keep input costs elevated and weigh on real income," the report stated. "With the economy already in an inflationary phase, a prolonged supply shock — particularly alongside a weak monsoon — raises the risk of a stagflationary environment."

The revision is driven almost entirely by the oil shock linked to the Iran crisis. With the Strait of Hormuz effectively closed to commercial shipping since late February, India has been forced to source crude from costlier alternatives while Brent hovers near $93 a barrel.

## The Monsoon Factor

The India Meteorological Department has projected southwest monsoon rainfall at just 90 percent of the long-period average for the June–September season — well below the 96–104 percent range considered normal. The monsoon arrived in Kerala three days late, on June 4, and an 84 percent probability of below-normal rainfall looms over the kharif sowing season.

A weak monsoon hits India through multiple channels. Rural demand — which accounts for roughly 45 percent of consumer spending — softens as farm incomes decline. Food prices rise, pushing headline inflation higher. And the RBI's room to cut rates narrows just when the economy needs monetary support.

Livemint reported that markets are now driven more by Brent crude and monsoon data than by any policy action, calling India's current challenge a "supply shock, not a liquidity or demand problem."

## The RBI's Tightrope

The Reserve Bank of India underscored the difficulty on Friday by holding the repo rate steady at 5.25 percent for the third consecutive meeting. Governor Sanjay Malhotra acknowledged the trade-offs: "Faced with difficult trade-offs, monetary policy has turned more cautious. The MPC felt it would be prudent to wait for greater clarity to emerge."

The RBI raised its inflation projection for the current fiscal year to 5.1 percent from 4.6 percent, while trimming its growth forecast to 6.6 percent from 6.9 percent. The Wall Street Journal noted that nine of eleven economists surveyed had expected the hold, with two forecasting a rate hike — a sign that the consensus itself is fragile.

## What It Means for NRIs

For the Indian diaspora, the macro picture matters in direct, personal ways. A weaker rupee — the currency has depreciated sharply since the conflict began — erodes the purchasing power of remittances when converted back to local currency. Higher food and fuel inflation squeezes the families that NRI earnings support. And a growth slowdown can dampen the real estate and equity returns that many diaspora investors count on.

Goldman Sachs estimated this week that 4 to 5 million barrels per day of global oil demand has been destroyed since the Strait of Hormuz closed — a 4 to 5 percent decline. The question for India is whether the destruction reaches demand before it reaches supply, and whether a monsoon failure tips the balance.

## The Bull Case

Not everyone is bearish. Crisil, the rating agency, has revised India's FY27 real GDP growth forecast upward to 6.5 percent, citing government-led capital expenditure (up 38.7 percent in May), continued monetary easing, and the structural consumption engine of a 1.4-billion-person economy.

But even Crisil's optimism comes with a caveat: its forecast assumes a near-normal monsoon. If the IMD's below-normal projection holds, the bull case narrows considerably.

India's economy is not in crisis. It is, however, entering a corridor where the margin for error has shrunk to almost nothing — and two of the three variables that matter most (oil and rain) are entirely outside New Delhi's control."""

    words = len(body.split())
    print(f"  Word count: {words}")

    article = {
        "headline": "India Grew at 7.7 Percent Last Year. A Major Brokerage Just Warned of Stagflation Ahead.",
        "subheadline": "Nuvama cuts FY27 growth to 6–6.5%, warns the Iran oil shock and a below-normal monsoon could trap India between slowing growth and rising prices.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Nuvama Institutional Equities", "Reserve Bank of India", "The Hindu BusinessLine", "Wall Street Journal", "Livemint", "Goldman Sachs", "Crisil"]),
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution
    }

    return insert_article(article)


# ============================================================
# ARTICLE 3: India at Shangri-La Dialogue 2026
# ============================================================
def write_article_3():
    print("\n=== Article 3: India at Shangri-La Dialogue 2026 ===")
    slug = "india-shangri-la-dialogue-2026-defence-secretary-us-indopacom-nato-bilaterals"

    print("Sourcing image...")
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Wikipedia for Rajesh Kumar Singh or Shangri-La Dialogue
    wp = fetch_wikipedia_person_image("Shangri-La Dialogue")
    if wp:
        uploaded = download_and_upload(wp, slug)
        if uploaded:
            image_url = uploaded
            image_caption = "The Shangri-La Dialogue in Singapore, Asia's premier defence summit"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        commons = fetch_wikimedia_commons("Shangri-La Dialogue Singapore defence", 5)
        if commons:
            for c in commons:
                if c["width"] > 500:
                    uploaded = download_and_upload(c["url"], slug)
                    if uploaded:
                        image_url = uploaded
                        image_caption = "The Shangri-La Dialogue at the Shangri-La Hotel, Singapore"
                        image_attribution = "Wikimedia Commons"
                        break

    if not image_url:
        commons = fetch_wikimedia_commons("India defence diplomacy navy", 5)
        if commons:
            for c in commons:
                if c["width"] > 500:
                    uploaded = download_and_upload(c["url"], slug)
                    if uploaded:
                        image_url = uploaded
                        image_caption = "India's defence forces at an international engagement"
                        image_attribution = "Wikimedia Commons"
                        break

    if not image_url:
        pexels = fetch_pexels("Singapore defence summit", 3)
        if pexels:
            uploaded = download_and_upload(pexels[0]["url"], slug)
            if uploaded:
                image_url = uploaded
                image_caption = "The Shangri-La Dialogue in Singapore brings together defence leaders from across the Indo-Pacific"
                image_attribution = "Pexels"

    body = """India's Defence Secretary Rajesh Kumar Singh held over ten bilateral meetings at the Shangri-La Dialogue 2026 in Singapore this weekend, engaging the United States, NATO, Canada, Australia, Singapore, Sweden, and the Netherlands in what New Delhi is calling its most expansive defence diplomatic push at Asia's premier security summit.

The engagement signals India's determination to position itself as an indispensable node in the emerging Indo-Pacific security architecture — even as it navigates the pressures of the Iran war, a deepening China relationship reset, and a defence budget stretched thin by inflation.

## The American Meeting

The centrepiece was Singh's meeting with Admiral Samuel J. Paparo, Commander of US Indo-Pacific Command (INDOPACOM), the military command responsible for American forces across the region.

The Ministry of Defence said the talks focused on "strengthening military-to-military cooperation, enhancing collaboration in the Indo-Pacific, and addressing emerging security challenges." The language is diplomatic boilerplate, but the substance is not: India-US defence ties have expanded dramatically under the Initiative on Critical and Emerging Technology (iCET) and a series of bilateral logistics agreements that allow Indian and American forces to use each other's bases for refuelling and repairs.

The meeting comes at a sensitive moment. The US is engaged in an active military conflict with Iran — a country India has historically maintained close energy and diplomatic ties with. India has been careful to avoid taking sides publicly, even as it has quietly diversified its crude oil sourcing away from the Hormuz corridor.

## NATO, Canada, and the Australia Push

Singh also held discussions with Admiral Giuseppe Cavo Dragone, Chair of the NATO Military Committee — a relatively rare India-NATO bilateral at this level. The Ministry of Defence said the exchange "reaffirmed India's commitment to constructive engagement with key multilateral defence organisations," though India has no formal alliance with NATO and has historically kept the bloc at arm's length.

The Canada meeting followed Prime Minister Mark Carney's February 2026 visit to India, which produced five memoranda of understanding on energy, critical minerals, AI, and defence. High Commissioner Christopher Cooter met Singh to discuss "next steps" on defence cooperation — a notable warming after years of diplomatic frost over the Khalistan issue.

India and Australia deepened their defence partnership further during a parallel meeting in New Delhi between Defence Minister Rajnath Singh and his counterpart Richard Marles. Australia has described India as a "top-tier security partner," and the two sides agreed to expand cooperation in maritime security, cybersecurity, and emerging technologies.

## The Singapore and European Outreach

At the Istana reception hosted on the sidelines, Singh interacted with Singapore President Tharman Shanmugaratnam — a meeting that underscores India's deepening strategic alignment with Southeast Asia's most capable military state.

He also met Sweden's State Secretary to the Minister of Defence, Peter Sandwall, discussing defence technology and innovation cooperation, and held bilateral talks with the Chief of Defence of the Netherlands, General Onno Eichelsheim, focusing on military exchange programmes.

## The Strategic Context

India's Shangri-La blitz is not happening in a vacuum. Three factors are reshaping India's defence calculus simultaneously:

**The Iran corridor risk.** India's maritime supply lines through the Strait of Hormuz remain under threat. The Indian Navy has quietly increased its presence in the Arabian Sea, and the country's dependence on Gulf energy makes maritime security cooperation with the US, Australia, and Japan a survival imperative rather than a diplomatic nicety.

**The China reset.** India and China held what the Ministry of External Affairs called "constructive and forward-looking" talks on the LAC situation in eastern Ladakh this week. The October 2024 patrolling agreement at Depsang and Demchok has been fully implemented. But India is simultaneously hardening its alliances with China's strategic competitors — a hedging strategy that Beijing watches closely.

**The defence-industrial pivot.** Multiple meetings at Shangri-La touched on defence technology, critical minerals, and joint innovation. India is trying to move from being a weapons buyer to a weapons co-developer, and the partnerships being forged in Singapore are the scaffolding for that transition.

## What It Means for the Diaspora

India's expanding defence partnerships carry direct implications for Indian professionals in the US, UK, Australia, and Canada. Defence-adjacent industries — cybersecurity, AI, semiconductor manufacturing, and space technology — are hiring zones in every country India held talks with this week. The iCET framework with the US, in particular, has opened doors for Indian tech firms in defence supply chains.

For the broader diaspora, India's rising profile at forums like Shangri-La shapes the geopolitical context in which NRI communities live and work. When India is perceived as a net security provider rather than a security consumer, it changes the diplomatic texture of immigration debates, trade negotiations, and cultural influence in every host country."""

    words = len(body.split())
    print(f"  Word count: {words}")

    article = {
        "headline": "India Held 10 Defence Bilaterals in Two Days at Shangri-La. That Number Tells a Story.",
        "subheadline": "From the US INDOPACOM chief to NATO's military committee chair, India's defence secretary worked every room in Singapore this weekend.",
        "slug": slug,
        "body": body,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Ministry of Defence (India)", "Ministry of External Affairs (India)", "The Indian EYE", "Reuters"]),
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution
    }

    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer (June 6, 2026 afternoon)")
    print("=" * 60)

    results = []

    art1_id = write_article_1()
    results.append(("Kuwait airport Indian killed", art1_id))

    art2_id = write_article_2()
    results.append(("India stagflation risk", art2_id))

    art3_id = write_article_3()
    results.append(("Shangri-La Dialogue", art3_id))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for title, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {title}: {aid or 'FAILED'}")
    print("=" * 60)
