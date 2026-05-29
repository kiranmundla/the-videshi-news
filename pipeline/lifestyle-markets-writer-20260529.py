#!/usr/bin/env python3
"""Lifestyle-health + markets-finance writer for The Videshi — 2026-05-29 run."""

import json, os, re, requests, uuid, urllib.parse
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
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

# ── Image helpers ────────────────────────────────────────────────────────────
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
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
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    # Validate
                    vr = requests.head(url, timeout=10)
                    ct = vr.headers.get("Content-Type", "")
                    cl = int(vr.headers.get("Content-Length", "0"))
                    if vr.status_code == 200 and "image" in ct and cl > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check that a URL returns a valid image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD properly
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True)
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", "0"))
        if r2.status_code == 200 and "image" in ct2 and cl2 > 5000:
            return True
    except Exception:
        pass
    return False


def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    return any(b in url for b in banned)


# ── Article publishing ───────────────────────────────────────────────────────
def generate_slug(headline):
    """Generate a clean slug from headline."""
    slug = re.sub(r'[^a-z0-9\s-]', '', headline.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    slug = slug[:80].rstrip('-')
    return slug + "-20260529"


def publish_article(article):
    """Publish an article to Supabase."""
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article["category"],
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article["sources"]),
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        article_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✅ Published: {article['headline'][:60]}... (id={article_id})")
        return True
    else:
        print(f"  ❌ Failed to publish: {r.status_code} {r.text[:200]}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 1: Flesh-eating bacteria in Florida (lifestyle-health)
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ Article 1: Vibrio vulnificus in Florida ═══")

art1_headline = "Five Cases of Flesh-Eating Bacteria Have Already Hit Florida This Year. The Season Is Starting Earlier Than Ever."
art1_subheadline = "Vibrio vulnificus thrives in warm coastal waters and can turn a small cut into a medical emergency within hours. Indian Americans along the Gulf Coast and in South Florida should know the warning signs before summer beach season begins."

art1_body = """The numbers are small but the trajectory is alarming. Five confirmed cases of Vibrio vulnificus — the bacterium behind what is commonly called flesh-eating disease — have been reported across Florida in 2026, already surpassing this time last year. Cases have been confirmed in Miami-Dade, Hillsborough, Lee, Palm Beach, and St. Johns counties, stretching from the Gulf Coast to the Atlantic side of the state.

One case, documented in the *New England Journal of Medicine*, involved a 74-year-old man who had a small cut on his leg and briefly swam in Gulf Coast waters. Within two days, his leg showed severe bruising, discoloration, and swelling. His arm was also affected. By the third day, he was in the emergency room. Surgeons confirmed Vibrio vulnificus and had to perform an above-the-knee amputation to save his life, along with extensive skin grafting on his arm.

## Why It Is Happening Earlier

Vibrio vulnificus thrives in warm, brackish coastal water. Historically, the bacteria was most dangerous between June and October. But warming ocean temperatures are expanding that window. Florida's Department of Health data shows 161 cases over the past three years and 35 deaths — a fatality rate of nearly 22 per cent. Health officials are now warning that the 2026 season has started ahead of schedule.

The bacterium enters the body through open wounds — cuts, scrapes, recent surgical incisions, even insect bites — when exposed to warm seawater. It can also be contracted by eating raw or undercooked shellfish, particularly oysters. Once inside the body, it can cause necrotising fasciitis, a rapidly spreading infection that destroys soft tissue.

## What Indian Americans Should Know

Florida has one of the largest and fastest-growing Indian American populations in the country, concentrated in South Florida, Tampa Bay, and the Orlando corridor. Many families spend weekends at Gulf Coast and Atlantic beaches, especially during the summer months.

The risk factors that make Vibrio vulnificus especially dangerous overlap significantly with conditions that are more prevalent in the South Asian community. People with liver disease, diabetes, chronic kidney disease, or compromised immune systems face substantially higher risk of severe infection and death. South Asians in the United States have nearly double the prevalence of diabetes by age 55 compared to white Americans, according to the MASALA study published in the *Journal of the American Heart Association*.

If you have any open wound — no matter how small — avoid swimming in warm coastal waters. This includes recent piercings, tattoos, and post-surgical sites. If you do swim and notice rapid swelling, redness that spreads quickly, or fever within hours of leaving the water, go to an emergency room immediately. Vibrio vulnificus can progress from mild symptoms to life-threatening infection in 12 to 24 hours.

## The Seafood Angle

For families who enjoy raw oysters or shellfish, the risk extends beyond the water itself. Vibrio vulnificus can be present in shellfish harvested from warm waters. The CDC recommends that anyone with liver conditions, diabetes, or weakened immunity avoid raw or undercooked shellfish entirely during summer months. Cooking shellfish to an internal temperature of 145°F eliminates the bacterium.

## What to Watch For

The early signs of Vibrio vulnificus infection include sudden fever, chills, and the rapid appearance of painful, red, swollen skin that may blister. The speed of progression is what makes it so dangerous — this is not a wait-and-see situation. If you or a family member develops these symptoms after ocean exposure, tell the emergency department specifically that you were in warm coastal water. Early antibiotic treatment dramatically improves outcomes.

Florida's health department is urging residents and visitors to be aware of the risks as summer approaches. With ocean temperatures continuing to rise, the window for Vibrio season is expanding. The bacteria that your grandparents never worried about at the beach is becoming a routine summer concern — and knowing the warning signs is the simplest form of protection."""

art1_slug = generate_slug("vibrio-vulnificus-flesh-eating-bacteria-florida-indian-americans")

# Image for article 1
print("  Sourcing image...")
art1_image = fetch_pexels_image("florida ocean beach waves coast", "warm ocean water coastal")
if art1_image and not is_banned_url(art1_image) and validate_image(art1_image):
    art1_image_attr = "Pexels"
else:
    art1_image = None
    art1_image_attr = ""
    print("  ⚠ No suitable image found for article 1")

article1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "lifestyle-health",
    "sources": [
        {"name": "Florida Department of Health", "url": "https://www.floridahealth.gov/"},
        {"name": "New England Journal of Medicine", "url": "https://www.nejm.org/"},
        {"name": "CDC Vibrio Guidelines", "url": "https://www.cdc.gov/vibrio/"},
        {"name": "MASALA Study — JAHA", "url": "https://www.ahajournals.org/journal/jaha"},
    ],
    "image_url": art1_image,
    "image_attribution": art1_image_attr,
}


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Europe May heatwave — heat safety (lifestyle-health)
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ Article 2: Europe heatwave + heat safety ═══")

art2_headline = "Europe Just Recorded Its Deadliest May Heatwave. Seven People Died in France Alone. As US Summer Approaches, Here Is What Heat Actually Does to Your Body."
art2_subheadline = "Temperatures 15°C above normal are breaking records across Western Europe. For Indian American families heading into summer — or planning trips to India — the science of heat illness is worth understanding before June arrives."

art2_body = """A heatwave that climate scientists are calling unprecedented for May has swept across Western Europe this week, killing at least seven people in France, shattering temperature records in the UK, Spain, and Germany, and triggering emergency health advisories across the continent. France recorded its hottest May day ever. The UK Met Office said what was once a 1-in-100-year May heatwave is now a 1-in-33-year event. Temperatures across Western Europe ran 10 to 15 degrees Celsius above normal.

The deaths in France included five drownings linked to people seeking relief in water, plus two deaths during outdoor sporting events — a 53-year-old man during a running event in Paris and a woman at a fitness competition in Lyon. France's sports minister called the deaths "a stark reminder that practicing sports in extreme heat requires absolute vigilance."

## The Body's 30-Minute Timeline

What makes heat dangerous is how quickly it overwhelms the body's cooling system. Within 30 minutes of heat exposure without adequate hydration, the body begins losing its ability to regulate temperature. The sequence is predictable and worth knowing.

**Minutes to hours: Heat exhaustion.** Symptoms include heavy sweating, weakness, cold and clammy skin, nausea, and dizziness. At this stage, moving to a cool place, lying down, and drinking water can reverse the condition within 30 minutes. If symptoms persist beyond that window, the situation is escalating.

**Beyond 30 minutes: Heatstroke.** When the body's cooling mechanism fails entirely, core temperature rises rapidly. The skin becomes hot and dry — sweating stops. Confusion, disorientation, poor balance, rapid heartbeat, and in severe cases seizures follow. Heatstroke is a medical emergency. Without treatment, it can cause organ damage and death.

**The dehydration multiplier.** Dehydration accelerates every stage of heat illness. The body needs to sweat to cool itself, and sweating requires adequate fluid. Alcohol and caffeine accelerate fluid loss. For people taking blood pressure medication — common in the South Asian community — the risk is compounded because many antihypertensives affect the body's ability to regulate temperature and hydration.

## Why This Matters for Indian American Families

The timing of Europe's heatwave is a preview of what much of the United States will face in the coming weeks. But the more immediate concern for many Indian American families is summer travel to India, where temperatures have already exceeded 50°C in parts of Rajasthan and have remained above 45°C across much of northern India through May.

India recorded over 40,000 suspected heatstroke cases and more than 100 heat-related deaths in 2025, according to government data. The 2026 season is tracking similarly. For diaspora families visiting during summer — particularly those who have acclimatised to air-conditioned American environments — the transition to Indian heat can be physiologically jarring. The body needs seven to fourteen days to acclimatise to sustained high temperatures, and most visit durations do not allow for that adjustment.

Older family members, children under five, pregnant women, and anyone with diabetes, heart disease, or kidney disease are at highest risk. The combination of high humidity — common in coastal Indian cities — and high temperature is especially dangerous because humidity prevents sweat from evaporating, eliminating the body's primary cooling mechanism.

## Practical Measures That Work

Hydration needs to be proactive, not reactive. By the time you feel thirsty, you are already mildly dehydrated. During heat exposure, drink water every 15 to 20 minutes even if you are not thirsty. Oral rehydration solutions — the same ones Indian pharmacies sell for diarrhoea — are highly effective because they replace electrolytes lost through sweating.

Avoid outdoor activity between 11 AM and 4 PM during extreme heat. Wear lightweight, loose, light-coloured clothing. If you are exercising outdoors, cut intensity by at least 50 per cent during the first week of heat exposure and build gradually.

Watch for confusion in elderly family members — it is the single most reliable warning sign that heat exhaustion is progressing to heatstroke. A person who becomes disoriented, stops making sense, or stops sweating in hot conditions needs emergency medical attention immediately.

The European heatwave is a reminder that extreme heat is no longer a problem confined to predictable seasons or geographies. The body's response to heat follows the same physiological rules whether you are in Lyon, Los Angeles, or Lucknow. Knowing those rules is the difference between a close call and a medical emergency."""

art2_slug = generate_slug("europe-may-heatwave-deaths-heat-safety-indian-americans-summer")

# Image for article 2
print("  Sourcing image...")
art2_image = fetch_pexels_image("summer heat sun thermometer", "hot weather heatwave sun")
if art2_image and not is_banned_url(art2_image) and validate_image(art2_image):
    art2_image_attr = "Pexels"
else:
    art2_image = None
    art2_image_attr = ""
    print("  ⚠ No suitable image found for article 2")

article2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "lifestyle-health",
    "sources": [
        {"name": "CNN — Europe heatwave coverage", "url": "https://www.cnn.com/"},
        {"name": "Met Office UK", "url": "https://www.metoffice.gov.uk/"},
        {"name": "Météo France", "url": "https://meteofrance.com/"},
        {"name": "Cleveland Clinic — Heat Illness Guide", "url": "https://my.clevelandclinic.org/"},
    ],
    "image_url": art2_image,
    "image_attribution": art2_image_attr,
}


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 3: RBI forex reserves + rupee defense (markets-finance)
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ Article 3: RBI forex reserves / rupee ═══")

art3_headline = "India's Forex Reserves Just Fell to a One-Year Low of $681 Billion. The RBI Is Burning Through Dollars to Defend the Rupee. Here Is What NRI Investors Should Watch."
art3_subheadline = "The Reserve Bank of India's war chest shrank by $7.5 billion in a single week. Ceasefire hopes briefly pushed the rupee past 95. But the rate hike question looming over June 5 will determine what comes next for your deposits, remittances, and home loans."

art3_body = """India's foreign exchange reserves fell to $681.4 billion in the week ended May 22, their lowest level in more than a year, as the Reserve Bank of India continued spending billions to slow the rupee's decline. The $7.5 billion weekly drop included a $4.5 billion fall in gold holdings and a nearly $3 billion decline in foreign currency assets, according to data the RBI released on Friday.

The numbers tell a story of sustained intervention. The RBI has been aggressively selling dollars in the open market to put a floor under the rupee, which has fallen more than 5 per cent in 2026 and briefly touched a record low of 96.96 per dollar last week. The central bank's foreign currency assets — the most liquid component of reserves — now stand at $543 billion, down from nearly $600 billion at the start of the year.

## Friday's Sharp Rally

On Friday, the rupee staged its best single-day gain in nearly two months, ending the session at 95 per dollar — up 0.7 per cent. The rally was driven by two converging forces. First, likely dollar-selling intervention by the RBI ahead of the local market open. Five traders told Reuters that state-run banks sold dollars on behalf of the central bank before the spot market opened, pushing the rupee from around 95.78 to 95.55 in minutes.

Second, oil prices dropped sharply on reports that Washington and Tehran had agreed to extend their ceasefire for another 60 days and allow traffic through the Strait of Hormuz — the chokepoint through which roughly 20 per cent of the world's oil flows. Brent crude fell toward $91 per barrel, on track for its steepest weekly decline since early April. For India, the world's third-largest oil importer, lower oil prices directly ease the current account pressure that has been hammering the rupee.

## The June 5 Decision

All eyes now turn to the RBI's monetary policy meeting on June 5. A Reuters poll of economists found that most expect the central bank to hold its key repo rate unchanged at 5.25 per cent. But the consensus is shifting. A majority of economists now expect at least one 25-basis-point rate hike by year-end, compared with expectations just two months ago for no increase through 2027.

Capital Economics forecasts the repo rate will reach 6.00 per cent before the end of 2026, contingent on the Middle East crisis winding down and energy prices retreating. Mizuho's head of macro research called a rate hike "a matter of when not if" and argued that moving "sooner rather than later at the August meeting makes sense."

The pressure is coming from multiple directions. Inflation — particularly food and fuel inflation — remains elevated. Foreign investors have pulled over $24 billion from Indian debt and equities on a net basis between March and May. Other Asian central banks have already begun tightening: Indonesia delivered a surprise 50-basis-point hike last week, and the Philippines raised rates 25 basis points in April. India is increasingly the outlier in holding steady.

## What It Means for NRIs

**Remittances:** The rupee at 95 means your dollar buys fewer rupees than it did at 88 in January but more than the 96.96 record low last week. If you are remitting regularly, the currency is in a volatile band. Locking in rates through forward contracts may be worth discussing with your bank.

**NRI deposits:** If the RBI does raise rates, NRI fixed deposit rates — both FCNR and NRE — are likely to follow. Banks have already quietly raised some NRI deposit rates in anticipation. A rate hike cycle would make parking dollars in Indian bank deposits more attractive than it has been in years.

**Home loans in India:** Anyone with a floating-rate home loan in India should prepare for higher EMIs. A 25-basis-point repo rate increase translates roughly to a 25-basis-point increase in your home loan rate, which on a ₹50 lakh loan at current rates would add approximately ₹800 to ₹1,000 to your monthly EMI.

**Equity exposure:** The Nifty has been under pressure all year as foreign institutional investors exit. But if ceasefire hopes hold and oil stabilises below $90, the combination of attractive valuations and eventual rate stability could make Indian equities interesting again on a 12-month view. The risk is that the ceasefire collapses and oil spikes back above $100.

## The RBI's Digital Rupee Push

Separately, the RBI's annual report released Friday revealed plans to expand the digital rupee to welfare payments and cross-border transactions. The central bank has piloted digital rupee disbursement of food subsidies in Gujarat, Puducherry, and Chandigarh, and signed a digital assets pact with Singapore's monetary authority for cross-border pilot projects. For NRIs, the long-term implication is that remittances to India could eventually bypass traditional banking channels entirely — though that remains years away from practical implementation.

## The Bottom Line

India's forex reserves provide a large buffer, but they are being drawn down at a pace that cannot continue indefinitely. The RBI is effectively buying time — intervening in markets while waiting for either the Middle East situation to resolve, oil prices to fall, or both. The June 5 meeting will signal whether the central bank is willing to use its interest rate tool alongside intervention. For NRIs, the next two weeks will set the tone for the rest of the year on deposits, remittances, and portfolio allocations."""

art3_slug = generate_slug("india-forex-reserves-one-year-low-rbi-rupee-defense-nri-investors")

# Image for article 3
print("  Sourcing image...")
art3_image = fetch_wikipedia_person_image("Reserve Bank of India")
if art3_image and not is_banned_url(art3_image) and validate_image(art3_image):
    art3_image_attr = "Wikimedia Commons"
else:
    # Try Pexels
    art3_image = fetch_pexels_image("indian rupee currency notes", "india finance banking")
    if art3_image and not is_banned_url(art3_image) and validate_image(art3_image):
        art3_image_attr = "Pexels"
    else:
        art3_image = None
        art3_image_attr = ""
        print("  ⚠ No suitable image found for article 3")

article3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "markets-finance",
    "sources": [
        {"name": "Reuters — India forex reserves", "url": "https://www.reuters.com/"},
        {"name": "Reuters — RBI rate expectations", "url": "https://www.reuters.com/"},
        {"name": "Reuters — Rupee rally", "url": "https://www.reuters.com/"},
        {"name": "RBI Annual Report 2025-26", "url": "https://www.rbi.org.in/"},
    ],
    "image_url": art3_image,
    "image_attribution": art3_image_attr,
}


# ── Publish all articles ─────────────────────────────────────────────────────
print("\n═══ Publishing ═══")
results = []
for i, article in enumerate([article1, article2, article3], 1):
    print(f"\n  [{i}/3] {article['category']}: {article['headline'][:50]}...")
    # Word count check
    wc = len(article["body"].split())
    if wc < 400:
        print(f"  ❌ REJECTED: body only {wc} words (min 400)")
        continue
    # Headline length check
    if len(article["headline"]) < 20 or len(article["headline"]) > 200:
        print(f"  ❌ REJECTED: headline length {len(article['headline'])} out of range")
        continue
    # Subheadline check
    if len(article["subheadline"]) < 15:
        print(f"  ❌ REJECTED: subheadline too short")
        continue
    # Image ban check
    if article.get("image_url") and is_banned_url(article["image_url"]):
        print(f"  ⚠ Banned image URL detected, clearing")
        article["image_url"] = None

    ok = publish_article(article)
    results.append({"headline": article["headline"][:60], "category": article["category"], "ok": ok})

print("\n═══ Summary ═══")
for r in results:
    status = "✅" if r["ok"] else "❌"
    print(f"  {status} [{r['category']}] {r['headline']}...")

print("\nDone.")
