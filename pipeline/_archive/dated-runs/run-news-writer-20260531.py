#!/usr/bin/env python3
"""The Videshi — News writer run for 2026-05-31 (batch 2)."""

import json, os, sys, time, uuid, re
import requests, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ─────────────────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Image helpers ─────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Use curl internally (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        import subprocess
        cmd = [
            "curl", "-sS",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
            "-H", f"Authorization: {PEXELS_KEY}",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Check image URL returns 200 with image content > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ Banned source: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD well, try GET with range
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)",
                                   "Range": "bytes=0-10000"})
        if r2.status_code in (200, 206):
            chunk = r2.content
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ✗ Failed to download image: HTTP {r.status_code}")
            return None
        img_data = r.content
        if len(img_data) < 5000:
            print(f"  ✗ Image too small: {len(img_data)} bytes")
            return None

        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=img_data,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {up.status_code} {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def sb_insert(table, row):
    """Insert a row into a Supabase table."""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=row, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) and data else data
    else:
        print(f"  ✗ Insert {table} failed: {r.status_code} {r.text[:300]}")
        return None


def sb_patch(table, filters, patch):
    """Patch rows in a Supabase table."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS, json=patch, timeout=30,
    )
    if r.status_code in (200, 201, 204):
        return True
    else:
        print(f"  ✗ Patch {table} failed: {r.status_code} {r.text[:300]}")
        return False


# ── Articles ──────────────────────────────────────────────────────────────────

articles = [
    {
        "headline": "Air India and IndiGo Are Cutting 250 Domestic Flights a Day Starting June. Fuel Costs Are the Reason.",
        "subheadline": "India's two biggest carriers are slashing routes between Delhi, Mumbai, Bengaluru, and a dozen other cities as jet fuel prices surge and post-summer demand softens. NRIs planning trips home face fewer options and higher fares.",
        "slug": "air-india-indigo-250-domestic-flight-cuts-june-fuel-costs-nri-travel-20260531",
        "category": "news",
        "sources": ["Outlook Traveller", "Outlook Business", "DGCA April 2026 traffic report", "IATA April 2026 data"],
        "image_search_person": None,
        "image_search_pexels": "India airport terminal departure board",
        "image_pexels_fallback": "airplane Indian airline terminal",
        "body": """India's two largest airline groups are pulling back hard on domestic flying starting in June, cutting a combined 250 daily flights as jet fuel prices eat into already thin margins and post-summer demand softens.

Air India is making the deepest reductions, trimming between 15 and 22 percent of its planned domestic schedule — roughly 110 to 120 fewer flights every day. IndiGo, which operates more than 1,950 daily flights, is cutting between 5 and 10 percent of its operations. Air India Express is also scaling back by about 10 percent.

The cuts hit virtually every major route in the country. Delhi–Kolkata, Delhi–Bengaluru, Delhi–Hyderabad, Mumbai–Ahmedabad, Mumbai–Bengaluru, Mumbai–Nagpur, Mumbai–Patna, and even the critical Delhi–Mumbai corridor are all seeing reduced frequencies. Short-haul metro connections under 90 minutes are taking the biggest hit.

## Why Now

The trigger is aviation turbine fuel, which has roughly doubled in recent weeks as geopolitical tensions — particularly around the Strait of Hormuz — have roiled global energy markets. Fuel is the single largest cost for any airline, and Indian carriers, which already operate on some of the thinnest margins in global aviation, have limited room to absorb the spike.

Airlines have responded by adding fuel surcharges of ₹400 to ₹450 per passenger, but that alone is not enough to offset the cost increase. Cutting frequencies is the blunter but more effective lever.

The timing coincides with a broader slowdown in Indian domestic air travel. According to data released by the Directorate General of Civil Aviation, domestic passenger traffic in April fell 4.2 percent month-on-month to 1.38 crore, and was 3.47 percent below April 2025. For the January-to-April period, year-on-year growth was essentially flat at 0.06 percent — a stark contrast to the double-digit post-pandemic recovery seen in 2023 and 2024.

## Market Share Shifts

IndiGo has tightened its grip on the domestic market, rising to a 65 percent share in April from 63.3 percent in March. The Air India Group — including Air India, Vistara, and Air India Express — slipped to 24.7 percent from 26.2 percent. Akasa Air edged up slightly to 5.8 percent, while SpiceJet fell to 3.4 percent.

On-time performance tells its own story: IndiGo led at 88.5 percent, followed by Air India Group at 82.4 percent, Akasa Air at 81.4 percent, Alliance Air at 71.2 percent, and SpiceJet at a dismal 31.2 percent.

## What NRIs Need to Know

For diaspora travelers planning trips to India this summer, the practical impact is straightforward: fewer flight options on domestic connections, especially during off-peak hours, and higher fares on the routes that remain. Booking flexibility is going to matter more than usual.

The international network is also under pressure. Air India has separately been rationalizing some international frequencies, though the Delhi–New York, Delhi–San Francisco, and Mumbai–Newark routes — the most critical for the NRI corridor — appear largely intact for now.

Airlines have framed the cuts as temporary. "These adjustments are driven by the sustained impact of high fuel prices on overall operations," Air India said in a statement. "Air India will continue to monitor demand and operating conditions closely." But temporary in aviation often means "until the next oil shock ends," and with Hormuz tensions unresolved, that timeline is anything but certain.

The broader picture is sobering. Global air passenger demand fell 3.4 percent year-on-year in April, according to the International Air Transport Association — the first meaningful decline since the post-pandemic recovery. Middle Eastern carriers saw traffic collapse by 46 percent. India's domestic market, while not facing anything that extreme, is clearly feeling the downstream effects of a world where fuel costs, conflict, and demand are all moving in the wrong direction at once.""",
    },
    {
        "headline": "A Single Day of Extreme Heat Kills 3,400 People Across India. A New Study Just Put a Number on It.",
        "subheadline": "UC Berkeley researchers estimate that a five-day heatwave causes nearly 30,000 excess deaths nationally. With temperatures crossing 46°C across northern India and the monsoon arriving late, the numbers are about to get worse.",
        "slug": "india-heatwave-3400-deaths-per-day-uc-berkeley-study-monsoon-delay-20260531",
        "category": "news",
        "sources": ["Frontiers in Environmental Health (journal)", "UC Berkeley India Energy and Climate Center", "India Meteorological Department", "phys.org"],
        "image_search_person": None,
        "image_search_pexels": "extreme heat scorching sun India road",
        "image_pexels_fallback": "heatwave cracked dry earth India",
        "body": """A single day of extreme heat kills approximately 3,400 people across India. A five-day heatwave — the kind that has become routine across the northern plains every May and June — causes nearly 30,000 excess deaths.

Those are the findings of a new study by researchers Piyush Narang and Ashok Gadgil at the University of California, Berkeley's India Energy and Climate Center, published in the journal Frontiers in Environmental Health. The numbers are not projections for some distant climate future. They describe the country as it exists right now.

## How the Study Works

India does not publish comprehensive, real-time heat-mortality data. The official death tolls reported by state governments — 37 so far this season — are widely understood to be severe undercounts. Heat deaths are frequently attributed to other causes: cardiac arrest, kidney failure, dehydration. Many occur among the elderly, outdoor laborers, and the rural poor, whose deaths may not be medically investigated at all.

To get around this data gap, Narang and Gadgil adapted findings from a multi-city analysis of heat-related mortality across 10 Indian cities, then scaled those results to all 640 districts using Civil Registration System mortality rates and 2024 population projections. The approach is not perfect, but it produces the most granular picture of heat mortality risk in India to date.

The geographic distribution is as unequal as you would expect. Uttar Pradesh alone accounts for roughly 8,100 excess deaths during a five-day heatwave. Individual districts — Ahmedabad, Jaipur, Surat — each see more than 250 deaths in a single event. The burden falls overwhelmingly on states with large populations, limited cooling infrastructure, and high proportions of outdoor workers.

## What Is Happening Right Now

India is in the grip of one of its worst pre-monsoon heat spells in a decade. Daily maximum temperatures have topped 46°C across Rajasthan, Madhya Pradesh, parts of Uttar Pradesh, and Haryana. Some stations have been running 5 to 8 degrees Celsius above seasonal norms since mid-April.

The India Meteorological Department has forecast that the 2026 monsoon will be the driest in 11 years, driven by a strengthening El Niño pattern. That means the usual relief — the arrival of monsoon rains that break the heat across the Indo-Gangetic plain — will come later and weaker than normal. June temperatures across southern, western, central, and northern India are projected to remain above seasonal averages.

Record electricity demand tells part of the story: India's power grid hit 270 gigawatts of peak demand recently, as air conditioning load surged. Coal India is scrambling to keep generation matched to demand, and blackouts have been reported in several states.

## The Diaspora Dimension

For the millions of NRIs with elderly parents and grandparents in northern and central India, the heatwave is a source of daily anxiety. Many households in Tier-2 and Tier-3 cities still rely on ceiling fans and water coolers, not air conditioning. Power outages during peak afternoon hours — precisely when cooling is most critical — remain common.

Modi addressed the heatwave in Sunday's Mann Ki Baat, urging citizens to follow official advisories, stay hydrated, and be careful in the sun. He highlighted India's traditional summer drinks — aam panna, lassi, buttermilk, sattu sharbat, kokum sharbat, panakam — as markers of cultural resilience against the heat.

But traditional drinks only go so far when the wet-bulb temperature crosses the threshold at which the human body can no longer cool itself through sweating. That threshold is being approached more frequently across South Asia. A rapid study by the World Weather Attribution group found that climate change made the April 2026 heat in India, Bangladesh, Thailand, and Laos at least 30 times more likely.

## What the Numbers Mean

The Berkeley study's most important contribution is not the death toll itself — those numbers are estimates, not body counts. It is the framework: district-by-district risk mapping that could, in theory, let state governments pre-position medical resources, open cooling shelters, and target advisories at the most vulnerable populations before the next heat event hits.

Whether any of that happens is a different question. India's disaster response infrastructure is optimized for cyclones, floods, and earthquakes — events that are sudden, visible, and dramatic. Heatwaves kill slowly and invisibly, and the victims tend to be people the system already overlooks.""",
    },
    {
        "headline": "300 Tourists Were Stranded 500 Feet in the Air Over Gulmarg. The Gondola Is Reopening Tuesday.",
        "subheadline": "Asia's highest cable car malfunctioned last Sunday, trapping 320 people in 65 cabins for seven hours during heavy rain. The army, NDRF, and police pulled everyone out safely. An investigation is underway.",
        "slug": "gulmarg-gondola-malfunction-300-stranded-rescue-reopening-kashmir-tourism-20260531",
        "category": "news",
        "sources": ["PTI", "The Hindu Business Line", "Madhyamam Online", "IANS"],
        "image_search_person": None,
        "image_search_pexels": "Gulmarg Kashmir cable car gondola mountain",
        "image_pexels_fallback": "Kashmir mountain valley scenic",
        "body": """The Gulmarg Gondola — Asia's highest cable car and one of Kashmir's most popular tourist attractions — is set to resume operations on Tuesday, June 2, after a major technical malfunction last Sunday left 320 tourists stranded mid-air in 65 cabins for seven hours.

Officials said that an expert trial run will be conducted on Monday to assess operational safety and technical performance before public services resume. All tickets for visit dates between May 25 and June 1 have been refunded in full.

## What Happened

On the afternoon of Sunday, May 25, the cable car system developed a technical snag around noon, halting operations on both Phase 1 (Gulmarg to Kongdoori) and Phase 2 (Kongdoori to Apharwat Peak). Some 320 passengers found themselves suspended in cabins across the mountainous terrain, with certain cabins hanging as high as 500 feet above the ground.

Heavy rain compounded the crisis, reducing visibility and making manual evacuation more dangerous. A multi-agency rescue operation was launched involving the Indian Army's Chinar Corps, the National Disaster Response Force, the State Disaster Response Force, and Jammu & Kashmir Police. Teams reached affected cabins using snowmobiles and ATVs, then used ropes and ladders to bring passengers down one cabin at a time.

The operation took seven hours to complete. All 320 passengers were evacuated safely, with no major injuries reported.

"The rescue operation has concluded and all the stranded persons have been evacuated safely," Director General of Police Nalin Prabhat said at the scene.

## The Response

Union Home Minister Amit Shah praised the disaster response forces on X, saying the nation "salutes the forces for their valour and skill." Chief Minister Omar Abdullah, whose office said the incident would be "thoroughly examined," ordered an official investigation into the malfunction. Deputy Chief Minister Surinder Kumar Choudhary traveled to Gulmarg with local MLA Farooq Ahmed Shah and senior officials to oversee coordination on the ground.

Lieutenant Governor Manoj Sinha directed the DGP to proceed to Gulmarg personally to monitor the rescue.

## Why It Matters for Travelers

The Gulmarg Gondola is not some peripheral tourist sideshow. It is the centerpiece of Kashmir's tourism infrastructure — a two-phase cable car that climbs from the resort town at 8,530 feet to Apharwat Peak at 13,780 feet, offering views of the Himalayas and access to some of the best skiing terrain in South Asia. During peak season, it carries thousands of visitors daily, including a significant number of NRI families who make Kashmir a priority stop during India trips.

The malfunction raises uncomfortable questions about maintenance and safety standards for the aging system. The Gondola, originally built by French company Pomagalski (now part of Leitner Group), has been in operation since 1998 for Phase 1 and 2005 for Phase 2. Cable car systems of this vintage require rigorous, continuous maintenance — particularly in an environment as harsh as Gulmarg's, where snow, ice, wind, and moisture impose extreme stresses on cables, pulleys, and drive mechanisms.

The investigation will need to determine whether the malfunction was a one-off technical failure or indicative of deeper maintenance issues. For tourists, the question is simpler: is it safe to ride?

## The Broader Kashmir Tourism Context

Kashmir has been enjoying a sustained tourism boom since the mid-2020s, with visitor numbers climbing steadily as the security situation has stabilized and infrastructure has improved. Gulmarg, Pahalgam, and Dal Lake have become staples of Indian domestic tourism, and an increasing number of diaspora families are adding Kashmir to their India itineraries.

That boom has placed enormous pressure on infrastructure that was never designed for current volumes. The Gondola, the roads, the hotels — all are operating at or beyond capacity during peak months. Incidents like last Sunday's are a reminder that tourist infrastructure needs to keep pace with tourist numbers, and right now it is not clear that it is.

For NRI families planning summer trips to Kashmir, the practical advice is to check conditions before booking Gondola rides, consider travel insurance that covers evacuation costs, and remember that mountain infrastructure anywhere in the world carries inherent risks that flat-ground attractions do not.

The Gondola will almost certainly be safe to ride on Tuesday. Whether the investigation produces meaningful safety reforms, or just a press release and a shrug, will tell us more about the long-term trajectory of Kashmir tourism than any visitor number ever could.""",
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now(timezone.utc).isoformat()
    published = 0

    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {art['headline'][:70]}...")
        print(f"{'='*60}")

        # Image sourcing
        img_url = None
        if art.get("image_search_person"):
            img_url = fetch_wikipedia_person_image(art["image_search_person"])

        if not img_url and art.get("image_search_pexels"):
            img_url = fetch_pexels_image(art["image_search_pexels"], art.get("image_pexels_fallback"))

        # Validate
        if img_url and not validate_image_url(img_url):
            print(f"  ✗ Image failed validation, trying fallback...")
            img_url = fetch_pexels_image(art.get("image_pexels_fallback"))
            if img_url and not validate_image_url(img_url):
                img_url = None

        # Upload to Supabase if non-permanent source
        final_img_url = None
        img_attribution = "The Videshi"
        if img_url:
            if "upload.wikimedia.org" in img_url:
                final_img_url = img_url
                img_attribution = "Wikimedia Commons"
            elif "images.pexels.com" in img_url:
                final_img_url = img_url
                img_attribution = "Pexels"
            else:
                filename = f"{art['slug']}.jpg"
                final_img_url = upload_to_supabase_storage(img_url, filename)

        # Build the row
        art_id = str(uuid.uuid4())
        sources_list = [{"name": s} for s in art["sources"]]

        row = {
            "id": art_id,
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "category": art["category"],
            "body": art["body"].strip(),
            "sources": sources_list,
            "status": "published",
            "published_at": now,
            "created_at": now,
            "updated_at": now,
        }

        row["vertical"] = "news"

        if final_img_url:
            row["image_url"] = final_img_url
            row["image_attribution"] = img_attribution

        result = sb_insert("p2_articles", row)
        if result:
            print(f"  ✓ Published: {art['slug']}")
            published += 1
        else:
            print(f"  ✗ FAILED to publish: {art['slug']}")

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(articles)} articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
