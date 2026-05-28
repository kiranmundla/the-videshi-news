#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-27 evening batch)
Publishes 3 articles to Supabase with proper images.
"""

import json, os, sys, uuid, subprocess, urllib.parse, time
from datetime import datetime, timezone

# ── ENV ──
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def sb_post(table, data):
    """Insert a row into Supabase."""
    import json as _json
    cmd = [
        "curl", "-sS", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/{table}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", _json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"  ✗ Insert error: {result.stderr}")
        return None
    try:
        resp = _json.loads(result.stdout)
        if isinstance(resp, list) and len(resp) > 0:
            print(f"  ✓ Inserted: {resp[0].get('id', 'unknown')}")
            return resp[0]
        elif isinstance(resp, dict) and resp.get("message"):
            print(f"  ✗ API error: {resp['message']}")
            return None
        return resp
    except Exception as e:
        print(f"  ✗ Parse error: {e} — raw: {result.stdout[:200]}")
        return None

def sb_patch(table, filters, data):
    """Patch a row in Supabase."""
    import json as _json
    filter_str = "&".join(f"{k}={v}" for k, v in filters.items())
    cmd = [
        "curl", "-sS", "-X", "PATCH",
        f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", _json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    cmd = [
        "curl", "-sS",
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
        "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Use curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        encoded_q = urllib.parse.quote(q)
        cmd = [
            "curl", "-sS",
            f"https://api.pexels.com/v1/search?query={encoded_q}&per_page=5&orientation=landscape",
            "-H", f"Authorization: {PEXELS_KEY}"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate an image URL returns HTTP 200 and >5KB."""
    if not url:
        return False
    cmd = ["curl", "-sS", "-I", "-L", url, "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        headers = result.stdout.lower()
        if "200 ok" not in headers and "200" not in headers.split("\n")[0]:
            print(f"  ⚠ Image validation failed (not 200): {url[:60]}")
            return False
        if "content-type: image" not in headers:
            # Some servers don't send this consistently, proceed anyway
            pass
        # Check content-length
        for line in headers.split("\n"):
            if "content-length:" in line:
                size = int(line.split(":")[1].strip())
                if size < 5000:
                    print(f"  ⚠ Image too small ({size} bytes): {url[:60]}")
                    return False
        return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

# ── ARTICLES ──
now_iso = datetime.now(timezone.utc).isoformat()

articles = [
    {
        "headline": "Petrol Crosses ₹100 in Most Indian Cities After Fourth Fuel Price Hike in Two Weeks",
        "subheadline": "State-owned retailers raise prices by ₹2.61 per litre for petrol and ₹2.71 for diesel as Iran war keeps crude above $90. The cumulative hike since May 15 is now nearly ₹7.50 per litre.",
        "slug": "india-petrol-crosses-100-fourth-fuel-price-hike-iran-war-crude-20260527",
        "category": "news",
        "sources": json.dumps(["Reuters", "Press Trust of India", "The Hindu BusinessLine"]),
        "image_search_person": None,
        "vertical": "economy",
        "image_search_pexels": "fuel pump petrol station India",
        "image_search_pexels_fallback": "gas station fuel pump",
        "body": """India's state-owned fuel retailers raised petrol and diesel prices for the fourth time in less than two weeks on May 25, pushing petrol past the ₹100 mark in most major cities and diesel close to that threshold. The cumulative increase since May 15 now stands at nearly ₹7.50 per litre — the steepest run of hikes since 2022.

## The Numbers

In Delhi, petrol rose to ₹102.12 per litre and diesel to ₹95.20. In Bengaluru, petrol hit ₹110.89. Mumbai and Chennai saw similar spikes. The latest round — ₹2.61 per litre for petrol and ₹2.71 for diesel — came after state elections concluded in several key states, removing the political pressure that had kept prices frozen for 76 days even as global crude soared.

Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum collectively control roughly 90 percent of the country's retail fuel market. The three companies reported combined daily losses exceeding ₹1,000 crore during the freeze, according to filings cited by Reuters.

## Why Now

The trigger is the Iran war. Since the U.S. and Israel launched strikes against Iran on February 28, the Strait of Hormuz — through which roughly a fifth of the world's oil supply flows — has been effectively closed to commercial shipping. Brent crude surged more than 30 percent from prewar levels and has remained stubbornly above $90 a barrel. On May 27, fresh U.S. strikes on an Iranian drone station in Bandar Abbas sent prices climbing again, with Brent briefly touching $100.

India, the world's third-largest oil importer, has scrambled to diversify. Refiners have turned to Latin American and African crude to replace disrupted Middle Eastern supplies, but the logistical premium adds to costs. The rupee, meanwhile, has slipped to 95.68 against the dollar, compounding the import bill.

## The Modi Austerity Push

The price hikes come weeks after Prime Minister Narendra Modi made a direct public appeal for fuel conservation — a rare move that underscored the severity of the energy squeeze. Modi urged citizens to limit foreign travel, use public transport, and avoid purchasing gold, all aimed at preserving India's dwindling foreign exchange reserves.

Corporate India has started falling in line. Maruti Suzuki, the country's largest carmaker, announced a raft of measures this week: expanded work-from-home arrangements, curbs on domestic and international travel, and encouragement of carpooling. The company framed the moves as a response to Modi's austerity call, but analysts say the operational savings are also meaningful for a company whose supply chains depend on imported components.

## What It Means for the Diaspora

For the estimated 18 million NRIs who send remittances home, the fuel hikes are a double hit. Rising prices erode the purchasing power of rupee-denominated transfers at a time when the weak rupee should, in theory, make remittances go further. Families in tier-two and tier-three cities — where public transport options are limited — feel the pinch most directly through higher auto-rickshaw fares, school bus charges, and the cost of last-mile delivery.

The Reserve Bank of India faces an increasingly uncomfortable position. Inflation expectations are climbing, with traders pricing in up to 100 basis points of rate hikes. But tightening monetary policy risks slowing an economy that is already headed for its first annual stock market decline since 2015.

## What Comes Next

The trajectory depends almost entirely on the Strait of Hormuz. Secretary of State Marco Rubio said on May 27 that a peace deal with Iran could "take a few days," but hours later the U.S. military shot down four Iranian attack drones and struck a ground control station — hardly the conditions for a swift resolution. If Brent stays above $95, analysts say a fifth fuel price hike is likely within the next two weeks.

For now, every Indian filling up at a fuel pump is absorbing the cost of a war being fought thousands of kilometres away.""",
    },
    {
        "headline": "India's Monsoon Forecast Is Below Normal for the First Time in Eight Years. El Niño Is Building.",
        "subheadline": "IMD projects just 92 percent of the long-period average rainfall for June through September. Agriculture, rural livelihoods, and food prices across the subcontinent are bracing for impact.",
        "slug": "india-monsoon-2026-below-normal-el-nino-imd-forecast-agriculture-20260527",
        "category": "news",
        "sources": json.dumps(["India Meteorological Department", "Skymet Weather", "National Geographic", "NOAA"]),
        "image_search_person": None,
        "vertical": "news",
        "image_search_pexels": "monsoon rain India farm agriculture",
        "image_search_pexels_fallback": "monsoon rain India",
        "body": """The India Meteorological Department has confirmed what climate watchers have been warning about for months: the 2026 southwest monsoon will be below normal, the first such forecast in eight years. IMD projects total seasonal rainfall at 92 percent of the long-period average of 87 centimeters — a shortfall that, if realized, would reverberate through an agricultural economy that still employs nearly half the country's workforce.

## The El Niño Factor

The culprit is a strengthening El Niño in the Pacific Ocean. NOAA puts the probability of an El Niño forming during the 2026 monsoon season at 98 percent, with an 80 percent chance it will be moderate to strong. El Niño years have historically correlated with weaker Indian monsoons — the 2015 El Niño coincided with a 14 percent rainfall deficit, triggering drought declarations across multiple states.

Private forecaster Skymet is even more pessimistic than IMD, projecting rainfall at just 94 percent of the long-period average (using the 1971–2020 LPA benchmark of 868.6 mm). Skymet expects June to hold steady, but July through September — the critical months for kharif sowing — to see progressively weaker rainfall, with central and northwest India facing the deepest deficits.

The monsoon onset itself may be delayed. IMD has noted that atmospheric conditions over Kerala have not yet met the criteria for an official onset declaration, though a minor delay of a few days is not uncommon.

## Why It Matters

India's southwest monsoon delivers roughly 70 percent of the country's annual rainfall. It irrigates 60 percent of farmland that lacks access to canal or borewell systems. When the monsoon underperforms, the consequences cascade: reservoir levels drop, groundwater tables fall, crop yields shrink, and food prices spike.

The most vulnerable kharif crops — rice, pulses, oilseeds, cotton, and sugarcane — depend on timely and adequate monsoon rainfall for planting between June and July. A shortfall during this window can reduce yields by 15 to 25 percent in dryland farming regions, according to estimates from the Indian Council of Agricultural Research.

States like Odisha are already mobilizing. The state government has unveiled a Kharif 2026 preparedness plan emphasizing climate-resilient crop varieties, seed supply chain management, fertilizer stockpiling, and expanded crop insurance coverage. Rajasthan, Madhya Pradesh, and Maharashtra — all states with large dryland farming footprints — are expected to announce similar measures.

## The Food Price Risk

India's food inflation has already been elevated, driven by fuel price hikes and supply chain disruptions linked to the Iran war. A below-normal monsoon would compound the pressure. In past El Niño years, vegetable prices have spiked 20 to 40 percent between August and October, and pulses — a dietary staple for hundreds of millions — have seen similar surges.

The government is likely to lean on its buffer stocks to manage prices. The Food Corporation of India holds substantial rice and wheat reserves, and the Centre has the option of restricting or banning exports of key commodities, as it did during previous monsoon disruptions. But buffer stocks address symptoms, not causes.

## What NRIs Should Watch

For diaspora families with relatives in rural India, the monsoon forecast is a quiet alarm. Remittances often increase during poor agricultural seasons as farming households face income shocks. The combination of a below-normal monsoon, high fuel prices, and a weakening rupee creates a triple squeeze on rural purchasing power.

The broader economic implications matter too. Agriculture contributes roughly 15 percent of GDP but accounts for more than 40 percent of employment. A bad monsoon typically shaves 0.3 to 0.5 percentage points off GDP growth, adds 50 to 100 basis points to food inflation, and forces the RBI into a tighter-than-desired monetary policy stance.

## What Comes Next

The decisive months will be July and August. If El Niño weakens or a positive Indian Ocean Dipole develops — as some models tentatively suggest — the actual rainfall could outperform the seasonal forecast. But the base case is clear: India is heading into its most challenging monsoon season since 2018, and the preparations need to match the risk.""",
    },
    {
        "headline": "Rajnath Singh Signs a Cyber Defense Pact With South Korea. India's Military Partnerships Are Going Digital.",
        "subheadline": "A new MoU in Seoul covers joint cyber threat intelligence, protection of critical military infrastructure, and digital defense cooperation across the Indo-Pacific.",
        "slug": "rajnath-singh-south-korea-cyber-defense-mou-indo-pacific-20260527",
        "category": "news",
        "sources": json.dumps(["The Indian Eye", "India Sentinels", "Press Information Bureau"]),
        "vertical": "geopolitics",
        "image_search_person": "Rajnath Singh",
        "image_search_pexels": "India military defense cooperation",
        "image_search_pexels_fallback": "cyber security defense",
        "body": """Defence Minister Rajnath Singh signed a memorandum of understanding on cyber defense cooperation with his South Korean counterpart Ahn Gyu-back during a visit to Seoul, marking the first formal bilateral agreement between the two countries focused specifically on digital military threats.

## What the Deal Covers

The MoU establishes a framework for sharing cyber threat intelligence, protecting critical military infrastructure from digital attacks, and building institutional mechanisms for real-time information exchange between the two militaries. Officials from both sides said the agreement would improve situational awareness and coordination in the Indo-Pacific — a region where cyber operations have become as consequential as conventional military posturing.

The agreement also opens the door to joint cyber exercises, collaborative research on digital defense technologies, and exchanges of military cybersecurity personnel. India and South Korea already participate in bilateral naval exercises and joint Army drills, but the cyber domain has been notably absent from their defense cooperation agenda until now.

## Why South Korea

India's choice of partner is deliberate. South Korea is one of the most cyber-targeted nations in the world, facing persistent attacks from North Korea's military hackers. The Korean military's Cyber Operations Command has developed sophisticated defensive capabilities and rapid-response protocols born of necessity — experience that India, facing its own escalating cyber threats from state actors, wants to learn from.

For South Korea, the logic runs the other way. India's Tier-1 tech talent pool and growing defense technology sector — defense production hit a record ₹1.54 lakh crore ($16.09 billion) in the year ending March 2025 — make it an attractive partner for co-developing next-generation cyber defense tools.

## The Bigger Picture

Singh's Seoul visit included wide-ranging talks on expanding military-to-military ties beyond cybersecurity: joint exercises, defense industry projects, and technology transfer were all on the agenda. The two ministers discussed deepening cooperation in AI-enabled defense systems, an area where both countries are investing heavily but neither has achieved the scale of the U.S. or China.

The timing is not accidental. The Shangri-La Dialogue — the region's premier defense forum — opens in Singapore on May 29, with U.S. Defense Secretary Pete Hegseth expected to deliver a closely watched speech against the backdrop of the Iran war. India has historically been inconsistent in its engagement with the Shangri-La Dialogue, but the Seoul cyber pact signals a broader shift toward proactive defense diplomacy in the Indo-Pacific.

India's defense partnerships have been expanding rapidly. The $500 billion package announced during Secretary of State Rubio's visit to New Delhi last week included nuclear energy cooperation and defense technology transfers. The AMCA stealth fighter program has solicited proposals from Tata, L&T, and Bharat Forge. And Modi's push for domestic defense manufacturing — aligned with the broader Make in India agenda — has created new opportunities for bilateral defense industry joint ventures.

## The Diaspora Connection

The India-South Korea defense relationship has an underappreciated diaspora dimension. An estimated 12,000 to 15,000 Indians live and work in South Korea, many in the technology sector. Samsung, Hyundai, and LG all operate major R&D centers in India. The cultural corridor — K-pop's massive Indian fanbase, the growing popularity of Korean cuisine in Indian cities — provides a soft-power foundation for deeper strategic ties.

For Indian Americans working in cybersecurity — one of the fastest-growing career fields in the U.S. — the agreement also opens potential trilateral opportunities. Indo-Pacific cyber defense cooperation is increasingly multilateral, and professionals with cross-cultural fluency are in high demand.

## What Comes Next

The cyber MoU will need to be operationalized through a detailed implementation roadmap, which officials said would be finalized within six months. The first joint cyber exercise is expected before the end of 2026. If it follows the pattern of India's cyber cooperation agreements with Japan and Australia, the partnership will deepen incrementally — starting with information sharing, progressing to joint exercises, and eventually moving toward collaborative capability development.

India's defense posture is evolving. The traditional focus on hardware — fighter jets, submarines, missile systems — is being augmented by investments in the digital domain. The Seoul MoU is a concrete step in that direction.""",
    },
]

# ── PUBLISH ──
for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:70]}...")
    print(f"{'='*60}")

    # Image sourcing
    img_url = None

    # Step 1: Wikipedia for person articles
    if art.get("image_search_person"):
        img_url = fetch_wikipedia_person_image(art["image_search_person"])
        if img_url and validate_image(img_url):
            print(f"  ✓ Using Wikipedia image")
        else:
            img_url = None

    # Step 2: Pexels fallback
    if not img_url and art.get("image_search_pexels"):
        img_url = fetch_pexels_image(art["image_search_pexels"], art.get("image_search_pexels_fallback"))
        if img_url and validate_image(img_url):
            print(f"  ✓ Using Pexels image")
        else:
            img_url = None

    if not img_url:
        print(f"  ⚠ No valid image found — publishing without image")

    # Build record
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "body": art["body"],
        "sources": art["sources"],
        "status": "published",
        "published_at": now_iso,
        "image_url": img_url or "",
        "vertical": art.get("vertical", "news"),
        "image_attribution": "Wikimedia Commons" if (img_url and "wikimedia" in (img_url or "").lower()) or (img_url and "wikipedia" in (img_url or "").lower()) else ("Pexels" if img_url else ""),
    }

    result = sb_post("p2_articles", record)
    if result:
        print(f"  ✓ Published: {art['slug']}")
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

    time.sleep(1)

print("\n✅ News writer batch complete.")
