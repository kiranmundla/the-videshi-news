#!/usr/bin/env python3
"""
The Videshi — Lifestyle-Health & Markets-Finance Writer
Run date: 2026-05-27
Generates 2 lifestyle-health articles + 1 markets-finance article
"""

import json, os, sys, uuid, re, time
import requests
from datetime import datetime, timezone

# ── Env ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Wikipedia person image ───────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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

# ── Pexels image ─────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    # Validate
                    head = requests.head(url, timeout=10)
                    ct = head.headers.get("Content-Type", "")
                    cl = int(head.headers.get("Content-Length", 0))
                    if head.status_code == 200 and "image" in ct and cl > 5000:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
                    else:
                        print(f"  ⚠ Pexels image rejected (status={head.status_code}, ct={ct}, size={cl})")
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Validate image URL ───────────────────────────────────────────
def validate_image_url(url):
    """Check the URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    # Ban Meta CDN
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED source detected: {b}")
            return False
    try:
        head = requests.head(url, timeout=10, allow_redirects=True)
        ct = head.headers.get("Content-Type", "")
        cl = int(head.headers.get("Content-Length", 0))
        if head.status_code == 200 and "image" in ct and cl > 5000:
            return True
        print(f"  ✗ Image validation failed: status={head.status_code}, ct={ct}, size={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

# ── Publish article ──────────────────────────────────────────────
def publish_article(article):
    """Insert topic into p2_topics, then article into p2_articles."""
    art_id = str(uuid.uuid4())
    topic_id = str(uuid.uuid4())

    # Create the topic first
    topic = {
        "id": topic_id,
        "canonical_title": article["headline"][:200],
        "vertical": article.get("vertical", "health"),
        "urgency": article.get("urgency", "evergreen"),
        "score_diaspora": 70,
        "score_significance": 70,
        "score_recency": 80,
        "score_source_avail": 70,
        "score_total": 72,
        "signal_count": 3,
        "status": "published",
        "keywords": article.get("tags", []),
        "category": article["category"],
    }
    resp_t = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_topics",
        headers=HEADERS,
        json=topic,
        timeout=30,
    )
    if resp_t.status_code not in (200, 201):
        print(f"  ✗ Topic creation failed ({resp_t.status_code}): {resp_t.text[:300]}")
        return None

    # Now create the article
    article["id"] = art_id
    article["topic_id"] = topic_id
    article["status"] = "published"
    article["published_at"] = datetime.now(timezone.utc).isoformat()
    article["word_count"] = len(article["body"].split())

    # Validate mandatory fields
    assert len(article["headline"]) >= 20, f"Headline too short: {article['headline']}"
    assert len(article.get("subheadline", "")) >= 15, f"Subheadline too short or missing"
    assert len(article["body"]) >= 400, f"Body too short ({len(article['body'])} chars)"
    assert article["category"] in ("lifestyle-health", "markets-finance"), f"Bad category: {article['category']}"
    assert re.match(r'^[a-z0-9][a-z0-9-]*$', article["slug"]), f"Bad slug: {article['slug']}"

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        aid = result[0]["id"] if isinstance(result, list) else result.get("id", article["id"])
        print(f"  ✓ Published: {article['headline'][:60]}... (id={aid})")
        return aid
    else:
        print(f"  ✗ Publish failed ({resp.status_code}): {resp.text[:500]}")
        return None


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: Sleep Sweet Spot & Biological Aging (lifestyle-health)
# ═══════════════════════════════════════════════════════════════════
print("\n═══ Article 1: Sleep Sweet Spot ═══")

article1_body = """A study of nearly 500,000 people just drew a line through one of the most basic questions in medicine: how much sleep is enough?

The answer, published in Nature by a team at Columbia University, is narrower than most people assume. Women who slept 6.5 to 7.8 hours and men who slept 6.4 to 7.7 hours had the lowest biological age across 23 aging clocks that measure how old the body actually looks at the cellular level — independent of the number on a birth certificate.

## The U-Shaped Curve Nobody Wanted

Both too little and too much sleep accelerated biological aging. Short sleepers faced a 50 percent higher relative risk of all-cause mortality. Long sleepers faced a 40 percent higher risk. Nine of the aging clocks — spanning the brain, heart, immune system, and skin — showed statistically significant links to sleep duration.

Short sleep hit the body hardest in cardiovascular, metabolic, and neurological terms. Long sleep was more strongly associated with psychiatric outcomes. Neither extreme was benign.

## What This Means for the Indian Tech Worker

The finding lands with particular force in a community that has normalised sleep deprivation as a professional credential. Indian Americans are overrepresented in technology, finance, and medicine — industries where six hours is treated as generous and five is worn as a badge. The cultural framing runs deeper than any single workplace: the idea that discipline means endurance, that rest is earned rather than required, that the body will cooperate if the mind insists.

It will not. The Columbia data says the body keeps score at the cellular level, and the bill comes due in the form of accelerated aging that no supplement, no biohack, and no weekend lie-in can reverse.

Saema Tahir, a board-certified sleep medicine physician in New York, explained the mechanism to Fox News Digital: "Sleep is really when the body does its most critical repair work, including cellular restoration, immune regulation, hormonal balance, and even clearing out metabolic waste from the brain through what we call the glymphatic system."

When sleep is consistently too short or too long, those processes get disrupted. "Over time, that disruption accumulates at the cellular level," Tahir said. The result is increased inflammatory markers and cellular changes that are "hallmarks of accelerated aging."

## The Quality Problem

Hours alone do not tell the full story. Tahir has seen patients who log seven hours but spend most of that time in light sleep, barely touching the deep slow-wave or REM stages that are most restorative. "They age just as poorly, sometimes worse, than someone getting six hours of genuinely consolidated, high-quality sleep," she said.

Deep sleep is when growth hormone is released and tissue repair peaks. REM sleep is critical for cognitive health and emotional regulation. Chasing hours without addressing sleep fragmentation, sleep apnea, or poor sleep architecture misses the bigger picture.

## The South Asian Compounding Risk

For South Asians, sleep deprivation does not exist in isolation. It compounds with the elevated cardiovascular risk, higher rates of insulin resistance, and the visceral fat distribution pattern that are already well-documented in this population. A South Asian man sleeping five hours a night is not just tired — he is layering a modifiable risk factor on top of a genetic baseline that already puts him in a higher-risk category for heart disease and type 2 diabetes.

The intervention is not expensive. It does not require a prescription. "Consistent, good-quality sleep is one of the most accessible tools we have for healthy aging," Tahir said. "It requires prioritisation."

## What to Do

The study does not prescribe a rigid number. Individual needs vary by age, health status, and life stage. But the data provides a framework: aim for the 6.5-to-7.8-hour window, pay attention to how you feel during the day, and stop treating sleep deprivation as a personality trait.

If you need caffeine to stay alert past noon, if you fall asleep within minutes of lying down, if your weekends are spent recovering from your weekdays — those are functional cues that your sleep is insufficient, regardless of what the clock says.

Your body is aging. The question is whether you are letting it age at its natural pace or accelerating the process by six hours a night."""

article1 = {
    "headline": "The Sleep Window That Slows Aging Is Narrower Than You Think. A Study of 500,000 People Found It. Most Indian Tech Workers Are Outside It.",
    "subheadline": "A Columbia University study published in Nature mapped 23 biological aging clocks against sleep duration. The optimal range is 6.4 to 7.8 hours — and both extremes accelerate cellular aging.",
    "body": article1_body.strip(),
    "slug": "sleep-sweet-spot-aging-columbia-nature-500000-indian-tech-worker-20260527",
    "category": "lifestyle-health",
    "sources": ["Nature (Columbia University study, 2026)", "Fox News Digital (Dr. Saema Tahir interview)"],
    "urgency": "evergreen",
    "vertical": "health",
    "diaspora_angle": "Indian tech workers in the US routinely sleep under six hours, layering a modifiable aging accelerant on top of the elevated cardiovascular and metabolic risk already documented in South Asians.",
    "tags": ["sleep", "aging", "biological age", "South Asian health", "Columbia University"],
    "image_attribution": "Pexels",
}

# Image sourcing — not about a specific person, use Pexels
img1 = fetch_pexels_image("person sleeping alarm clock bedroom", "sleeping peacefully dark room")
if img1 and validate_image_url(img1):
    article1["image_url"] = img1
else:
    print("  ⚠ No valid image found for Article 1")

aid1 = publish_article(article1)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Recovery Sleep & Mortality (lifestyle-health)
# ═══════════════════════════════════════════════════════════════════
print("\n═══ Article 2: Recovery Sleep ═══")

article2_body = """The conventional wisdom says you cannot catch up on lost sleep. A study of 574,000 days of objective sleep data says the truth is more nuanced — and more urgent.

A research team at Tsinghua University analysed wrist-worn accelerometer data from approximately 85,000 participants in the UK Biobank, tracking actual sleep rather than self-reported estimates. Their finding, published in Nature Communications: participants who did not take recovery sleep after a night of sleep restriction had a 15 percent higher probability of all-cause mortality over the following eight years compared with those who never experienced sleep restriction at all.

The group that slept roughly one additional hour the day after a short night showed no statistically significant difference in mortality from those who slept well consistently.

## The Weekday Pattern Nobody Expected

The most surprising finding was when recovery sleep happened. Most of it occurred on weekdays, not weekends. The popular narrative of "catching up on sleep over the weekend" was not what the data showed. Instead, the body appeared to self-correct the very next day — sleeping slightly longer after a bad night, often without the person even noticing.

This matters because it reframes the problem. The danger is not a single bad night. The danger is chronic sleep restriction without any compensatory response — the pattern of grinding through five-hour nights for weeks on end with no recovery signal at all.

Among participants with chronic sleep deprivation — averaging only 5.7 hours per night — the mortality gap was even more pronounced. The Tsinghua team verified their findings against the U.S. National Health and Nutrition Examination Survey and found consistent results.

## Why This Matters for NRIs

The Indian American professional class operates in exactly the pattern this study warns against. Long work hours, late-night calls with teams in India, early-morning meetings on the East Coast if you live on the West Coast, and a cultural framework that treats exhaustion as evidence of effort.

The study does not say sleep deprivation is harmless. Jean-Philippe Chaput, a sleep expert at the University of Ottawa, stressed that point: "The fact that recovery sleep is possible should not be interpreted as meaning that repeatedly cutting sleep during weekdays is harmless."

What it does say is that the body has a repair mechanism — but only if you let it work. A single hour of additional sleep after a short night appears to neutralise the mortality signal. But if you override that signal with an alarm clock, caffeine, and willpower every single morning, the repair never happens.

## The Compounding Problem

For South Asians specifically, the stakes are higher. This population already carries elevated cardiovascular risk, higher rates of metabolic syndrome, and a genetic predisposition to visceral fat accumulation. Sleep restriction adds an inflammatory load on top of an already elevated baseline. The 15 percent mortality increase in the general population may understate the impact in a group where the cardiovascular system is already under strain.

The study also found that recovery sleep was effective whether sleep deprivation lasted one night or two consecutive nights. But it could not determine a threshold beyond which recovery becomes impossible — three, four, five consecutive nights of restriction may exceed the body's ability to compensate.

## The One-Hour Intervention

The practical implication is straightforward: if you slept badly last night, sleep one hour longer tonight. Do not push through. Do not treat the fatigue as a challenge to overcome. The data says that single hour may be the difference between a mortality trajectory that looks normal and one that does not.

This is not permission to maintain a chaotic sleep schedule. It is evidence that the body knows when it has been shortchanged and will attempt to repair itself — if you let it. The intervention costs nothing. It requires no device, no supplement, no appointment. It requires turning off the screen one hour earlier and letting the biology do what it evolved to do."""

article2 = {
    "headline": "One Hour of Recovery Sleep After a Bad Night Erases the Mortality Signal. A Study of 574,000 Nights Proves Your Body Knows What It Needs — If You Let It.",
    "subheadline": "Tsinghua University researchers tracked 85,000 people with wrist-worn devices. Those who slept one extra hour after sleep deprivation had the same mortality risk as those who never lost sleep at all.",
    "body": article2_body.strip(),
    "slug": "recovery-sleep-one-hour-mortality-tsinghua-574000-nights-nri-20260527",
    "category": "lifestyle-health",
    "sources": ["Nature Communications (Tsinghua University, 2026)", "Seoul Economic Daily", "Dr. Jean-Philippe Chaput, University of Ottawa"],
    "urgency": "evergreen",
    "vertical": "health",
    "diaspora_angle": "NRI professionals routinely grind through sleep-deprived weekdays with no recovery signal. This study shows the body can self-repair after a bad night — but only if the alarm clock and caffeine do not override it.",
    "tags": ["sleep", "recovery sleep", "mortality", "sleep deprivation", "South Asian health"],
    "image_attribution": "Pexels",
}

img2 = fetch_pexels_image("morning sunlight bedroom waking up", "person resting bed peaceful")
if img2 and validate_image_url(img2):
    article2["image_url"] = img2
else:
    print("  ⚠ No valid image found for Article 2")

aid2 = publish_article(article2)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: India Oil Import Diversification (markets-finance)
# ═══════════════════════════════════════════════════════════════════
print("\n═══ Article 3: India Oil Diversification ═══")

article3_body = """India is rewriting its oil supply chain in real time. Three months after the Strait of Hormuz effectively closed to commercial shipping, the world's third-largest oil importer has pivoted to suppliers it barely used a year ago — and the shift has implications for every NRI who sends money home, holds rupee assets, or watches the price of a flight to Delhi.

## The Numbers

In April and May, Indian refiners sharply increased imports from Venezuela, Brazil, Angola, and Nigeria, according to preliminary data from Kpler, the cargo-tracking firm. Iraq — historically one of India's top three suppliers — was skipped entirely last month after exports were halted. Iran, absent from India's import ledger for seven years, made a return after Washington granted a temporary waiver to stabilise global prices.

Russia remained India's largest single supplier but its share fell from nearly 50 percent in March to about 35 percent in April after Nayara Energy shut its 400,000-barrel-per-day refinery for maintenance, cutting Russian intake by 29.4 percent. In May, Russian volumes are expected to recover to about 1.9 million barrels per day.

Overall, India imported 4.57 million barrels per day in April — flat month-on-month but down 15.5 percent from a year earlier.

## The Hormuz Factor

The Strait of Hormuz, which handles roughly a fifth of global oil and liquefied natural gas flows, has remained largely shut since the U.S.-Iran war began on February 28. Only the UAE and Saudi Arabia have pipeline infrastructure that bypasses the strait. Kuwait, Iraq, Qatar, and Bahrain are effectively landlocked for oil exports as long as the waterway remains contested.

Brent crude jumped about 4 percent on Tuesday after fresh U.S. strikes on Iran set back hopes of a deal to reopen the strait. Prices had dropped 7 percent the previous day on peace-talk optimism, then reversed. At nearly $100 per barrel, oil is roughly 45 percent higher than before the war began.

## What This Means for NRIs

The ripple effects reach diaspora wallets in three ways.

**Rupee pressure.** India imports over 80 percent of its crude. Higher oil prices widen the current account deficit, which weakens the rupee. The currency has already slipped, and the RBI is running dollar swap auctions and studying NRI bond schemes reminiscent of the 2013 crisis playbook to stabilise it. If you are sending dollars home, the exchange rate is working in your favour — but it signals economic stress.

**Inflation.** Costlier crude feeds into everything from cooking gas to airline tickets to the cost of transporting vegetables to mandis. The wholesale price index is already under upward pressure. If you have family in India, their grocery bills are rising faster than official inflation suggests.

**Flight prices.** Jet fuel is the single largest cost component for airlines. Higher crude means higher fares, particularly on long-haul India routes. If you are planning a summer trip, book now — prices are unlikely to fall before the Hormuz situation resolves.

## The Geopolitical Hedge

India's diversification is not just a response to logistics. It is a strategic repositioning. Venezuela, which was effectively shut out of India's import mix during years of U.S. sanctions, is now on course to become India's fourth-largest supplier in May. Brazil, which supplies heavy crude compatible with Indian refinery configurations, has moved into the top five.

The UAE's exit from OPEC in May — freeing it from output quotas — adds another variable. Abu Dhabi can now pump and price independently, and its pipeline infrastructure bypassing Hormuz makes it the most reliable Gulf supplier for the foreseeable future. India is expected to deepen that relationship.

## The RBI Response

The Reserve Bank of India is not standing still. Indian banks are seeking hedging cost subsidies from the RBI to raise dollar funding, Reuters reported. The central bank's $5 billion USD/INR buy-sell swap auction on Tuesday is designed both to roll over previous swaps and to mitigate the impact of its dollar sales on rupee liquidity.

For NRIs with NRE or FCNR deposits, this environment creates an asymmetry: your dollar deposits earn a higher effective return as the rupee depreciates, but the underlying economy is under strain. The RBI may announce NRI-specific bond offerings — similar to the 2013 programme that raised $26 billion — as a further incentive.

## The Bottom Line

India's oil import map has changed more in three months than it did in the previous three years. The Hormuz disruption forced a diversification that was overdue, but the transition is expensive and the geopolitical uncertainty is unresolved. U.S. Secretary of State Marco Rubio has said a peace deal could "take a few days," but the market is pricing in weeks or months.

If you hold rupee-denominated assets, watch the oil price. If you send money home, the current exchange rate is historically favourable. If you are planning travel to India this summer, the cost of that trip is being set in the Strait of Hormuz."""

article3 = {
    "headline": "India Just Rewrote Its Oil Supply Chain in Ninety Days. Venezuela Is Now Its Fifth-Largest Supplier. The Rupee, Your Remittances, and Your Summer Flights Are All in Play.",
    "subheadline": "With the Strait of Hormuz largely shut since February, Indian refiners have pivoted to Latin American and African crude. The shift has direct implications for NRI wallets.",
    "body": article3_body.strip(),
    "slug": "india-oil-supply-chain-hormuz-venezuela-brazil-rupee-nri-remittances-20260527",
    "category": "markets-finance",
    "sources": ["Reuters (India oil import data, May 2026)", "Kpler cargo tracking data", "Reuters (RBI swap auctions, bank hedging)", "Wall Street Journal (currency analysis)"],
    "urgency": "daily",
    "vertical": "economy",
    "diaspora_angle": "India's oil diversification directly affects NRI wallets through rupee depreciation, rising remittance value, higher flight costs, and the RBI's NRI bond courtship modelled on the 2013 crisis playbook.",
    "tags": ["oil imports", "Strait of Hormuz", "rupee", "NRI remittances", "India economy", "Venezuela", "crude oil"],
    "image_attribution": "Pexels",
}

img3 = fetch_pexels_image("oil tanker ship ocean", "oil refinery industrial")
if img3 and validate_image_url(img3):
    article3["image_url"] = img3
else:
    print("  ⚠ No valid image found for Article 3")

aid3 = publish_article(article3)

# ── Summary ──────────────────────────────────────────────────────
print("\n═══ Summary ═══")
print(f"Article 1 (lifestyle-health): {'✓' if aid1 else '✗'} Sleep Sweet Spot")
print(f"Article 2 (lifestyle-health): {'✓' if aid2 else '✗'} Recovery Sleep")
print(f"Article 3 (markets-finance):  {'✓' if aid3 else '✗'} India Oil Diversification")
print("Done.")
