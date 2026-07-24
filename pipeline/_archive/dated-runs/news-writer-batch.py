#!/usr/bin/env python3
"""News writer batch — 3 articles for The Videshi, 2026-05-30 evening run."""

import json, os, re, sys, time, uuid, urllib.parse
import requests
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

# ── Pexels config ──────────────────────────────────────────────────────────
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

# ── Image helpers ────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    # Block banned domains
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ Banned domain in URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in content_type and content_length == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = int(r2.headers.get("Content-Length", 0))
            if size > 5000:
                print(f"  ✓ Image validated (GET): {size} bytes")
                return True
            # Read a chunk to check
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated (chunk): {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert a row into Supabase and return the response."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return None


def sb_patch(table, filters, data):
    """Patch rows in Supabase matching filters."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")
    return False


# ── Articles ─────────────────────────────────────────────────────────────────

articles = [
    {
        "headline": "India's Monsoon Forecast Just Got Worse. It Will Be the Weakest in Eleven Years.",
        "subheadline": "The IMD revised its rainfall projection downward to 90 percent of normal, citing an emerging El Niño. Farmers, food prices, and the rural economy are all on notice.",
        "slug": "imd-monsoon-forecast-revised-90-percent-weakest-eleven-years-el-nino-20260530",
        "category": "news",
        "sources_list": "Reuters, Livemint, India Meteorological Department, Rural Voice India, The Indian Witness",
        "image_search": "monsoon rain India agriculture",
        "image_fallback": "monsoon clouds India farming",
        "person_image": None,
        "body": """India's weather agency has delivered an unwelcome forecast update that could reshape the country's economic outlook for the rest of the year. The India Meteorological Department on Friday revised its projection for the 2026 southwest monsoon downward to 90 percent of the long-period average — firmly in the "below normal" category and the weakest monsoon forecast since 2015.

The revision, issued in the IMD's second-stage long-range outlook, marks a further deterioration from the 92 percent rainfall estimate announced in April. The culprit, according to M. Ravichandran, secretary of the Ministry of Earth Sciences, is an emerging El Niño pattern in the equatorial Pacific that is expected to strengthen through the latter half of the monsoon season.

**Why This Matters for 600 Million People**

The southwest monsoon, which typically runs from June through September, delivers roughly 70 percent of India's annual rainfall. It replenishes reservoirs, recharges groundwater, and sustains the sowing of kharif crops — rice, pulses, oilseeds, cotton, and sugarcane — that feed hundreds of millions and anchor rural livelihoods. Nearly half of India's farmland lacks irrigation, making the monsoon the single most consequential variable for agricultural output.

At 90 percent of the long-period average of 87 centimeters, the forecast places rainfall well below the 96-to-104-percent band that the IMD classifies as normal. If the prediction holds, this will be the first below-average monsoon in three years, breaking a stretch of favorable seasons that helped keep food inflation in check and rural demand buoyant.

The IMD expects rainfall distribution to vary sharply across regions. Northwest India may receive near-normal precipitation, but Central India, the southern peninsula, and the northeastern states — including the monsoon core zone, where the bulk of rain-fed agriculture is concentrated — are all projected to fall below normal.

**A Perfect Storm of Economic Risks**

The timing could not be worse. India's finance ministry released its monthly economic review on Saturday, flagging the monsoon as a key risk alongside rising fuel prices and the ongoing disruption to the Strait of Hormuz caused by the US-Iran conflict. Retail inflation stood at 3.48 percent in April, still below the Reserve Bank of India's 4 percent target, but the ministry warned that a confluence of elevated energy prices, a weakening rupee, and deficient rainfall could push food inflation sharply higher in the coming months.

"A deficient monsoon, particularly in the crucial July-August months, can add to the pressure and push up inflation closer to an average of 5.5 percent if food inflation spikes," said Gaura Sengupta, chief economist at IDFC First Bank. That would significantly complicate the RBI's policy calculus at a moment when the central bank is already under pressure to raise interest rates to defend the rupee.

El Niño conditions, which warm the central Pacific and tend to suppress Indian monsoon rainfall, are expected to develop soon and intensify to moderate-to-strong levels during the second half of the season. This is a marked shift from the weak La Niña conditions that prevailed earlier this year and had initially offered some hope for normal rainfall.

**What It Means for the Diaspora**

For NRIs with family in rural India, particularly in states like Maharashtra, Madhya Pradesh, Karnataka, and Telangana that fall within the monsoon core zone, the implications are direct. A weak monsoon typically translates into lower farm incomes, reduced rural spending, and higher food prices — all of which affect household budgets back home.

For those invested in Indian equities, the monsoon is a macro signal that markets watch closely. Agricultural output accounts for roughly 15 percent of GDP but supports nearly 45 percent of the workforce, and any sustained disruption feeds through to consumption demand, FMCG earnings, and overall growth expectations.

India is already grappling with heatwave conditions across several northern states, with temperatures exceeding 45 degrees Celsius (113°F) — conditions that normally ease only with the arrival of monsoon rains. The IMD has indicated that June rainfall is also expected to fall below 92 percent of the average, suggesting the season will start slow.

The last time India recorded a monsoon this weak was in 2015, when rainfall came in at 86 percent of the long-period average. That year, food inflation surged, the government was forced to import pulses, and rural distress became a dominant political issue. Whether 2026 follows a similar trajectory will depend on how quickly El Niño develops and whether the government's buffer stocks and price stabilization mechanisms can absorb the shock.""",
    },
    {
        "headline": "India Just Told Its Oil Companies to Build a 30-Day LPG Reserve. The Iran War Is the Reason.",
        "subheadline": "The petroleum ministry has directed IOC, BPCL, and HPCL to plan LPG storage that can cover a full month of demand. India is also expanding crude oil reserves.",
        "slug": "india-lpg-30-day-strategic-reserve-ioc-bpcl-hpcl-iran-war-energy-security-20260530",
        "category": "news",
        "sources_list": "Reuters, PTI via AngelOne, Hellenic Shipping News, S&P Global Commodity Insights, Discovery Alert",
        "image_search": "oil refinery India industrial",
        "image_fallback": "petroleum storage tanks industrial",
        "person_image": None,
        "body": """India has ordered its three largest state-run fuel retailers to draw up plans for expanding liquefied petroleum gas storage capacity to cover at least 30 days of national demand — a significant strategic shift driven by the energy insecurity exposed by the US-Iran war.

Sujata Sharma, a joint secretary in the Ministry of Petroleum and Natural Gas, confirmed the directive during a media interaction on Friday. Indian Oil Corporation, Bharat Petroleum Corporation, and Hindustan Petroleum Corporation — which together control the vast majority of India's LPG marketing and distribution — have been asked to assess the infrastructure and investment required for the expansion.

The proposed reserves would supplement, not replace, the commercial inventories that the three companies maintain for day-to-day distribution. India is also working separately on increasing its crude oil strategic reserves, Sharma said, though she did not provide a timeline for either initiative.

**Why LPG Matters More Than You Think**

India is the world's second-largest consumer of LPG after China, with over 320 million households relying on it as their primary cooking fuel. The Pradhan Mantri Ujjwala Yojana scheme, which distributed free LPG connections to below-poverty-line families, dramatically expanded the user base over the past decade. But the supply chain that feeds those connections was engineered for cost efficiency, not resilience.

India imports roughly 60 percent of its LPG requirements, with the bulk arriving from the Middle East through shipping lanes that run through or near the Strait of Hormuz. The three-month disruption to the strait — caused by Iranian mine-laying and the subsequent US naval blockade — has laid bare the vulnerability of a system that was optimized for a world where Gulf shipping routes stayed open and competitively priced.

State-run fuel retailers are currently losing nearly six billion rupees daily on LPG and other fuel sales despite two price hikes this month, according to industry reports. The losses compound the financial pressure of building new strategic storage, but the government appears to have concluded that the cost of inaction is higher.

**Underground Caverns and the Road Ahead**

India has been quietly building LPG storage infrastructure for years, but the pace has been modest. The country's total underground cavern LPG storage capacity currently stands at around 60,000 metric tons, operated by South Asia LPG Co. in Visakhapatnam. Hindustan Petroleum is constructing an 80,000-metric-ton underground rock cavern in Mangalore, which would more than double total cavern capacity when completed.

"India is making significant strides in strengthening its LPG infrastructure to meet rising domestic demand and ensure long-term energy security," said Anmol Bhushan, lead research analyst for Asia and the Middle East at S&P Global Commodity Insights. "These developments align with India's goals to reduce dependence on spot market imports, stabilize domestic prices, and ease financial losses faced by oil marketing companies due to government-controlled pricing."

On the crude oil side, India's strategic petroleum reserves — underground caverns at Visakhapatnam, Mangalore, and Padur — currently hold approximately 40 million barrels, covering about 10 days of net imports. The government has been discussing a second phase that would add another 50 million barrels, and the Iran war has given that plan new urgency.

**The Diaspora Angle**

For NRIs who send money home to families that depend on subsidized LPG, the story is immediate and personal. LPG cylinder prices have already risen twice in May, and further increases are likely if the Hormuz disruption persists. A 30-day strategic reserve, once built, would provide a buffer against the kind of supply shocks that force emergency price hikes.

The directive also signals a broader shift in India's energy security posture. For decades, the country relied on the assumption that global energy markets would remain broadly functional and that diplomatic relationships with Gulf producers would ensure supply. The Iran war has shattered that assumption for a generation of policymakers.

A crude oil tanker, the Nissos Keros, carrying roughly 270,000 metric tons of cargo for India, passed safely through the Strait of Hormuz this week and is expected to reach Visakhapatnam by early June. Indian refineries are currently running at full capacity with adequate crude stockpiles. But the government is no longer willing to bet that the next tanker will arrive as smoothly — hence the push for reserves that can absorb a month-long disruption without rationing.

The Ministry of Petroleum has also instructed state governments to monitor district-level diesel and petrol consumption patterns and intensify inspections along major transportation routes to prevent unauthorized fuel procurement and hoarding. The message is clear: India is preparing for a prolonged energy disruption, even as diplomatic efforts to reopen the Hormuz corridor inch forward.""",
    },
    {
        "headline": "The RBI Will Almost Certainly Hold Rates on June 5. But Most Economists Now Expect a Hike Before December.",
        "subheadline": "A Reuters poll shows 80 percent of economists see no change next week. But the rupee's slide, rising oil prices, and a weakening monsoon are shifting the consensus toward tightening by year-end.",
        "slug": "rbi-rate-hold-june-5-majority-expect-hike-year-end-rupee-oil-monsoon-20260530",
        "category": "news",
        "sources_list": "Reuters, Mizuho Securities, Capital Economics, STCI Primary Dealer, Ainvest, Standard Chartered",
        "image_search": "Reserve Bank India Mumbai building",
        "image_fallback": "central bank India finance",
        "person_image": None,
        "body": """The Reserve Bank of India will almost certainly keep its benchmark interest rate unchanged at 5.25 percent when the Monetary Policy Committee meets on June 5, according to a Reuters poll of 56 economists. But the more consequential finding is what comes after: a growing majority now expects the central bank to raise rates at least once before the year is out.

The shift in sentiment has been rapid. In an April poll, only one economist predicted a rate hike in June. In the latest survey, conducted between May 22 and 29, eleven respondents forecast a 25-basis-point increase on June 5 and one expected a larger 50-basis-point move. The remaining 44 — roughly 80 percent — still expect a hold, but many of them see the RBI's hand being forced by year-end as inflation risks pile up.

**Why the RBI Can Afford to Wait — For Now**

India's retail inflation stood at 3.48 percent in April, comfortably below the RBI's 4 percent medium-term target and below the upper band of its 2-to-6-percent tolerance range. That gives the central bank room to be patient, even as wholesale inflation has started accelerating and upstream price pressures are building.

"With growth facing downside risks while inflation faces strong upside pressures, we expect the RBI to hold rates steady in June, as supply shocks perceived as temporary might not warrant an interest rate action immediately," said Aditya Vyas, chief economist at STCI Primary Dealer. "Interest rates are not a good tool to counter large supply shocks."

The argument against an immediate hike rests on a distinction between demand-pull and cost-push inflation. The current inflationary pressure is overwhelmingly supply-driven — higher oil prices from the Iran war, rising freight costs from the Hormuz disruption, and fuel price hikes that are feeding through to transportation and energy costs. Raising interest rates does little to address these supply-side forces and risks choking off economic growth at a time when India can least afford it.

**But the Pressure Is Building**

The case for patience is getting harder to sustain. The Indian rupee has fallen more than 5 percent this year, briefly touching 97 per dollar on May 22 before apparent RBI intervention pulled it back. It closed Friday at 95 per dollar after its best single-day gain in nearly two months, aided by reports of a potential 60-day US-Iran truce extension and a corresponding drop in crude oil prices.

But currency traders remain nervous. Foreign investors have pulled over $24 billion from Indian debt and equities on a net basis between March and May, driven by the economic hit from elevated oil prices and a lack of AI-related trade that has kept India out of favor compared with tech-heavy Asian markets.

The rupee's weakness creates its own inflationary loop: a cheaper currency makes imports — especially oil — more expensive in rupee terms, which pushes up domestic fuel and transportation costs, which feeds into the prices of everything from food to manufactured goods. The interest rate differential between India and the United States has narrowed to a decade-low level, reducing the attractiveness of rupee-denominated assets and encouraging further capital outflows.

Vishnu Varathan of Mizuho Securities has argued publicly that the RBI should hike rates sooner rather than later to "mitigate unnecessary pain" from rupee pressures. Standard Chartered has projected a cumulative 50-basis-point increase this fiscal year, with the first move likely in June. Shilan Shah, deputy chief emerging-market economist at Capital Economics, sees the repo rate reaching 6.00 percent before December — but only if the Iran crisis ends soon and energy prices retreat.

**What NRIs Should Watch**

For Indians in the United States, the United Kingdom, and Canada, the RBI's rate decision matters in two immediate ways.

First, remittances. The rupee's weakness means that every dollar, pound, or Canadian dollar sent home currently buys more rupees than it did at the start of the year. A rate hike would typically strengthen the currency, reducing that advantage. But if the hike stabilizes the rupee at a weaker-than-historical level, the remittance math may still favor NRIs compared with pre-war exchange rates.

Second, mortgages. Those with home loans in India — whether for personal use or investment property — will see their EMIs rise if the RBI tightens. A move from 5.25 percent to 6.00 percent on the repo rate typically translates into a 50-to-75-basis-point increase in lending rates, which for a Rs 50 lakh loan can add Rs 2,000-3,000 per month to repayments.

The RBI's decision on June 5 will be announced at 10:00 AM IST (12:30 AM Eastern, 9:30 PM Pacific on June 4). The monetary policy statement will be closely watched not just for the rate decision itself but for the tone of the commentary — any signal that the RBI is preparing markets for a hike later in the year could move the rupee and bond yields even before any actual policy change.""",
    },
]

# ── Publish ──────────────────────────────────────────────────────────────────

def publish_article(art):
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline']}")
    print(f"Slug: {art['slug']}")
    print(f"Category: {art['category']}")

    # Image sourcing
    img_url = None
    img_attribution = None

    # Try Wikipedia if person article
    if art.get("person_image"):
        img_url = fetch_wikipedia_person_image(art["person_image"])
        if img_url:
            img_attribution = "Wikimedia Commons"

    # Try Pexels
    if not img_url:
        img_url = fetch_pexels_image(art["image_search"], art.get("image_fallback"))
        if img_url:
            img_attribution = "Pexels"

    # Validate
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image failed validation, dropping")
        img_url = None
        img_attribution = None

    if img_url:
        print(f"  ✓ Using image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No valid image found — publishing without image")

    # Build article record
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "body": art["body"].strip(),
        "sources": art["sources_list"],
        "status": "published",
        "published_at": now,
        "created_at": now,
    }
    if img_url:
        record["image_url"] = img_url
    if img_attribution:
        record["image_attribution"] = img_attribution

    # Insert
    result = sb_insert("p2_articles", record)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published! ID: {art_id}")
        return art_id
    else:
        print(f"  ✗ FAILED to publish")
        return None


def main():
    published = []
    failed = []
    for art in articles:
        art_id = publish_article(art)
        if art_id:
            published.append(art["slug"])
        else:
            failed.append(art["slug"])

    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(published)} published, {len(failed)} failed")
    for s in published:
        print(f"  ✓ {s}")
    for s in failed:
        print(f"  ✗ {s}")


if __name__ == "__main__":
    main()
