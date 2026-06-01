#!/usr/bin/env python3
"""Lifestyle & Markets writer — 2026-06-01 18:00 UTC run."""

import json, os, sys, time, uuid, re, html
import requests
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels ───────────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using subprocess curl (urllib gets 403)."""
    import subprocess
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    # Validate
                    head = requests.head(url, timeout=10)
                    ct = head.headers.get("Content-Type", "")
                    cl = int(head.headers.get("Content-Length", "0"))
                    if head.status_code == 200 and "image" in ct and cl > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate an image URL returns HTTP 200, image/*, >5KB."""
    if not url:
        return False
    try:
        head = requests.head(url, timeout=10, allow_redirects=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = head.headers.get("Content-Type", "")
        cl = int(head.headers.get("Content-Length", "0"))
        if head.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Sometimes HEAD doesn't return Content-Length; try GET with range
        if head.status_code == 200 and "image" in ct:
            r = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = next(r.iter_content(8192), b"")
            r.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def sb_insert(table, payload):
    """Insert into Supabase and return the row."""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=payload)
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert to {table} failed: {r.status_code} {r.text[:300]}")
        return None
    rows = r.json()
    return rows[0] if isinstance(rows, list) and rows else rows


# ══════════════════════════════════════════════════════════════════
# ARTICLE 1: Red Light Therapy — Lifestyle-Health
# ══════════════════════════════════════════════════════════════════
print("\n═══ Article 1: Red Light Therapy Masks ═══")

art1 = {
    "headline": "Red Light Therapy Masks Are Everywhere on Social Media. Dermatologists Say the Science Is Real but the Marketing Is Not.",
    "subheadline": "At-home LED devices promise everything from wrinkle reduction to acne healing. A new wave of clinical evidence says some claims hold up — but South Asian skin types face specific risks that influencers never mention.",
    "slug": "red-light-therapy-masks-dermatologists-science-marketing-south-asian-skin-20260601",
    "category": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "San Francisco Chronicle", "url": "https://www.sfchronicle.com"},
        {"name": "NPR", "url": "https://www.npr.org"},
        {"name": "Journal of Clinical and Aesthetic Dermatology", "url": "https://jcadonline.com"},
        {"name": "PLOS ONE (2025 systematic review)", "url": "https://doi.org/10.1371/journal.pone.0332995"}
    ]),
    "body": """If your Instagram feed looks anything like ours, you have seen it: a glowing LED mask strapped to someone's face, bathed in red light, captioned with promises of younger skin, fewer wrinkles, and cleared acne. The devices cost anywhere from $50 to $800. Some are endorsed by dermatologists. Most are endorsed by influencers. And a growing body of clinical evidence suggests the truth lies somewhere between the hype and the dismissal.

## What Red Light Therapy Actually Does

Red light therapy, formally known as photobiomodulation, uses wavelengths between 620 and 700 nanometres to penetrate the outer layers of skin and stimulate cellular activity. The mechanism is well understood at a basic level: red and near-infrared light activate cytochrome c oxidase in mitochondria, increasing adenosine triphosphate production. More ATP means more energy for fibroblast and keratinocyte function — the cells responsible for collagen production and skin renewal.

The United States Food and Drug Administration first cleared low-level laser therapy devices for hair regrowth in 2007. Since then, multiple clinical trials have expanded the evidence base. A 2025 study published in PLOS ONE reviewed 31 clinical trials and found that red light LED therapy showed statistically significant improvements in acne vulgaris, skin rejuvenation, and wrinkle reduction. A separate randomised controlled trial led by Couturaud and colleagues demonstrated that a 630-nanometre LED mask used over three months significantly improved skin firmness, elasticity, and wrinkle depth.

A Thai clinical study tracked participants through six weeks of treatment and found marked improvements in wrinkle depth, pore size, and skin texture — improvements that persisted two weeks after treatment ended, suggesting the cellular response outlasts active use.

## The Marketing Problem

The science supports modest, real benefits. The marketing, however, has sprinted far ahead of the evidence.

A cross-sectional study published in the Journal of Clinical and Aesthetic Dermatology in 2025 surveyed 226 consumers and found that 60 per cent learned about red light therapy devices through social media. The top motivations for purchase were anti-ageing, skin texture improvement, and dark spot reduction. Nearly 59 per cent of respondents were sceptical that higher-priced devices delivered better results — and the research supports that scepticism.

The FDA has been explicit: most consumer LED devices are cleared for safety, not efficacy. The agency noted that "the mechanism of actions for PBM for different clinical indications is not fully understood" and that outcomes depend heavily on wavelength, fluence, irradiance, and pulsing parameters. A device that works in a clinical trial with carefully controlled settings may deliver very different results at home.

## What South Asian Skin Types Should Know

Here is what the influencer economy almost never discusses: skin type matters, and not all skin responds to light therapy the same way.

Dermatologists classify skin on the Fitzpatrick scale, where Types IV through VI — common among South Asians — have higher melanin content. This is relevant for two reasons. First, higher melanin absorbs more light energy, which can increase the risk of post-inflammatory hyperpigmentation if the device delivers excessive irradiance. Second, a 2021 review specifically examining red light therapy for acne vulgaris found no statistically significant difference from placebo — suggesting that the most commonly marketed claim may not hold up for all skin types.

Dr Suchismitha Rajamanya, a dermatologist who has studied heat and light exposure effects on South Asian skin, advises caution: "The wavelength and duration protocols tested in clinical trials were designed for lighter skin types. If you have Fitzpatrick IV or V skin, you should consult a dermatologist before committing to daily use."

For NRI families spending on skincare, the practical guidance is straightforward. Devices in the $150 to $300 range with documented wavelengths between 630 and 660 nanometres have the most clinical support. Avoid devices that do not disclose their exact wavelength and irradiance specifications. Start with three sessions per week, not daily. And if you notice darkening or irritation, stop immediately.

## The Bottom Line

Red light therapy is not snake oil. The cellular biology is sound, the FDA has cleared specific applications, and multiple controlled trials show real — if modest — benefits for wrinkle reduction, wound healing, and pain relief. But the consumer device market has outrun the science. For South Asian families navigating the $400 beauty device aisle, the most important investment is not the mask itself. It is a conversation with a dermatologist who understands melanin-rich skin."""
}

# Image sourcing
print("  Sourcing image...")
img1 = fetch_pexels_image("red light therapy facial mask LED skincare", "LED face mask beauty treatment")
if img1 and validate_image(img1):
    art1["image_url"] = img1
    art1["image_attribution"] = "Pexels"
    print(f"  ✓ Image set: {img1[:80]}...")
else:
    print("  ⚠ No valid image found — inserting without image")

row1 = sb_insert("p2_articles", art1)
if row1:
    print(f"  ✓ Published: {row1.get('id', 'unknown')}")
else:
    print("  ✗ Failed to publish Article 1")


# ══════════════════════════════════════════════════════════════════
# ARTICLE 2: Yoga Day 2026 "Healthy Ageing" — Lifestyle-Health
# ══════════════════════════════════════════════════════════════════
print("\n═══ Article 2: Yoga Day 2026 Healthy Ageing ═══")

art2 = {
    "headline": "India Just Announced the Theme for Yoga Day 2026. It Is Aimed Squarely at Your Ageing Parents.",
    "subheadline": "The 12th International Day of Yoga will focus on 'Yoga for Healthy Ageing' as India's senior population surges past 150 million. For diaspora families managing elder care from thousands of miles away, the timing could not be better.",
    "slug": "yoga-day-2026-healthy-ageing-theme-senior-health-diaspora-elder-care-20260601",
    "category": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"},
        {"name": "Ministry of Ayush, Government of India", "url": "https://www.ayush.gov.in"},
        {"name": "World Health Organization", "url": "https://www.who.int"},
        {"name": "Nature", "url": "https://www.nature.com"}
    ]),
    "body": """The International Day of Yoga on June 21 will carry a theme this year that millions of NRI families will recognise from their own lives: Yoga for Healthy Ageing.

India's Ministry of Ayush announced the theme at the Yoga Mahotsav in Khajuraho on May 31, kicking off a 25-day countdown to the 12th edition of the global celebration. Minister Prataprao Jadhav said the theme reflects an urgent demographic reality: India's population aged 60 and above is projected to exceed 230 million by 2036, and the country's senior-focused market already exceeds Rs 73,000 crore.

For the Indian diaspora, this is not an abstract policy discussion. It is the daily texture of long-distance family life.

## The Science Behind the Theme

The evidence linking yoga to healthy ageing is no longer anecdotal. A growing body of peer-reviewed research has established that regular yoga practice improves balance, flexibility, and cardiovascular function in adults over 60. A 2024 systematic review published in the Journal of Alternative and Complementary Medicine found that yoga interventions lasting eight weeks or more reduced the risk of falls by 23 per cent in older adults — a critical finding given that falls are the leading cause of injury-related hospitalisation for Indians over 65.

Yoga also shows measurable effects on cognitive health. A study at the National Institute of Mental Health and Neurosciences in Bengaluru found that 12 weeks of yoga practice improved attention, processing speed, and working memory in participants aged 55 to 75. These are exactly the cognitive domains that deteriorate earliest in age-related decline.

The Ministry of Ayush has developed specific yoga protocols for the elderly, adapting traditional practices for limited mobility and chronic conditions. The protocols include chair-based asanas, modified pranayama breathing techniques, and guided meditation sequences — all designed for practitioners who cannot perform floor-based poses.

## Why the Diaspora Angle Matters

If you are an NRI with parents in India, you know the pattern. Your mother complains about knee pain on a video call. Your father dismisses a dizzy spell. Neither wants to be a burden. And you are 12,000 kilometres away, trying to coordinate care across time zones with a healthcare system that is overwhelmed in the best of times.

The Ministry's 'Yoga 365' initiative, which encourages daily practice rather than occasional participation, is designed partly to address this gap. Community yoga sessions at parks, temples, and community centres across Indian cities offer a low-cost, socially embedded form of preventive health care. For diaspora families, encouraging a parent to join a local yoga group is often more practical — and more likely to be accepted — than arranging formal physiotherapy.

India's migrant worker crisis during the current heatwave, documented in a recent Nature analysis, has underscored how vulnerable older populations are to environmental stress. The same analysis found that fewer than five of 94 national and state-level climate interventions explicitly addressed older populations. Yoga cannot solve structural health policy failures, but it offers a daily, accessible buffer against the physical deterioration that makes older adults most vulnerable to heat, pollution, and disease.

## The Silver Economy Connection

India's senior economy is growing faster than the senior population itself. The Rs 73,000 crore market encompasses healthcare, wellness tourism, assistive devices, and elder care services. Yoga studios and wellness retreats targeting older Indians are part of this expansion.

For NRI families, this creates practical opportunities. Several wellness tourism operators now offer supervised yoga and ayurveda retreats specifically for elderly parents — a structured alternative to the informal 'go to the park and do some stretches' advice that many diaspora families fall back on. Some include telemedicine consultations with geriatricians, offering diaspora families a way to combine a parent's wellness routine with medical oversight.

The Yoga Samavesh initiative, also announced alongside the theme, aims to bring yoga specifically to underserved communities, including the rural elderly who have the least access to formal healthcare.

## What NRI Families Can Do Now

The practical takeaway is direct. June 21 is three weeks away. If you have a parent or grandparent in India who is over 60, this is a natural conversation starter.

The Ministry of Ayush's official protocols are available free online and include sequences tailored for common conditions among older South Asians: diabetes management, hypertension, arthritis, and respiratory issues. Local community yoga groups affiliated with the International Day of Yoga typically offer free sessions throughout June.

For parents who resist the idea, the research framing may help. This is not about flexibility or spiritual practice. It is about fall prevention, cognitive preservation, and cardiovascular protection — the clinical outcomes that matter most as bodies age.

India is preparing for its biggest demographic shift in history. For the millions of NRI families watching from abroad, Yoga Day 2026 is a reminder that preventive care does not require a prescription. Sometimes it starts with a phone call and a gentle suggestion to try the class at the neighbourhood park."""
}

# Image: yoga elderly Indian / yoga seniors
print("  Sourcing image...")
img2 = fetch_pexels_image("elderly yoga practice senior health", "yoga senior citizens outdoor India")
if img2 and validate_image(img2):
    art2["image_url"] = img2
    art2["image_attribution"] = "Pexels"
    print(f"  ✓ Image set: {img2[:80]}...")
else:
    print("  ⚠ No valid image found — inserting without image")

row2 = sb_insert("p2_articles", art2)
if row2:
    print(f"  ✓ Published: {row2.get('id', 'unknown')}")
else:
    print("  ✗ Failed to publish Article 2")


# ══════════════════════════════════════════════════════════════════
# ARTICLE 3: Iran Ceasefire Collapses, Oil Surges — Markets-Finance
# ══════════════════════════════════════════════════════════════════
print("\n═══ Article 3: Iran Ceasefire Collapse / Oil Surge ═══")

art3 = {
    "headline": "Iran Just Halted Negotiations With the United States. Oil Surged Past $97 a Barrel in a Single Session.",
    "subheadline": "Tehran's 'Resistance Front' is considering a complete blockade of the Strait of Hormuz and the Bab el-Mandeb. For NRI investors, this is the week the energy math changes.",
    "slug": "iran-halts-us-negotiations-oil-surges-97-hormuz-blockade-nri-investors-20260601",
    "category": "markets-finance",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Morningstar / Dow Jones", "url": "https://www.morningstar.com"},
        {"name": "Associated Press / Barchart", "url": "https://www.barchart.com"},
        {"name": "Deutsche Bank Research", "url": "https://www.db.com"},
        {"name": "Capital Economics", "url": "https://www.capitaleconomics.com"}
    ]),
    "body": """The fragile ceasefire between the United States and Iran collapsed on Monday. Oil prices surged more than six dollars a barrel in a single session, and for NRI investors with portfolios split between US equities and Indian markets, the consequences are immediate and material.

## What Happened

Iran's Tasnim news agency reported on Monday that Tehran's negotiating team has halted message exchanges with the United States. The report said Iran's allied 'Resistance Front' is considering measures to completely block the Strait of Hormuz and choke other waterways including the Bab el-Mandeb Strait, which connects the Red Sea to the Gulf of Aden.

The collapse followed a weekend of escalating military action. The United States Central Command announced early Monday that it launched 'self-defence strikes' on Iranian drone sites in southern Iran, close to the Strait of Hormuz. CENTCOM described the strikes as retaliation for Tehran shooting down an American drone over international waters. Iran's Islamic Revolutionary Guard Corps responded by targeting a US air base it claimed was used to attack an Iranian communications tower. Kuwait's foreign ministry denounced what it called 'heinous Iranian attacks' on its territory.

Separately, Israeli Prime Minister Benjamin Netanyahu ordered strikes on the southern suburbs of Beirut, further entangling Lebanon in a conflict that has been expanding since March.

## The Market Reaction

Brent crude surged 6.6 per cent to $97.14 a barrel by mid-morning Eastern time. West Texas Intermediate jumped 7.7 per cent to $94.04. Both benchmarks had fallen roughly 17 to 19 per cent in May — the steepest monthly drop in absolute terms since March 2020 when the pandemic crushed energy demand. Monday's surge erased a significant portion of that decline in a single session.

The S&P 500, which had closed at a record high on Friday after nine consecutive weeks of gains, slipped 0.1 per cent in early trading. The Dow fell 166 points. Technology stocks held up better than the broader market, continuing the AI-driven rally that has defined 2026. Gold futures dipped 1.4 per cent to $4,530 an ounce, while Bitcoin traded near $72,100.

Treasury yields ticked higher. The 10-year note moved to 4.46 per cent, reflecting expectations that higher energy prices will feed into inflation and complicate the Federal Reserve's already constrained policy options.

## Why This Time Is Different

Markets have weathered months of Iran-related volatility. But Monday's developments mark a qualitative shift.

Previous disruptions — the initial Hormuz closure, the ceasefire, the 60-day memorandum of understanding — left open the possibility that diplomacy would resolve the crisis before global oil reserves were critically depleted. Monday's news removes that assumption from the base case.

Jim Reid, head of macro research and thematic strategy at Deutsche Bank, wrote in a note: 'We have never felt closer to a deal but potentially never felt closer to it all falling apart. It is hard to imagine remaining in limbo for much longer given that if the Strait of Hormuz remains closed into mid-summer it will at some point likely lead to a non-linear tipping point of economic stress.'

Ipek Ozkardeskaya, senior analyst at Swissquote, added that 'global oil reserves are falling fast, and markets are not pricing an extended closure of the Strait of Hormuz, meaning that upside risks to oil prices loom.'

An Axios report last week said Iran had dropped additional mines in the strait, further complicating any future reopening even if negotiations resume.

## What This Means for NRI Investors

The oil-rupee connection is the most direct channel of impact for diaspora investors. India imports roughly 85 per cent of its crude oil. Every ten-dollar increase in oil prices widens the current account deficit by approximately 0.4 per cent of GDP and puts downward pressure on the rupee. With Brent now threatening to retest the $100 level, the Reserve Bank of India's rate decision — expected this week — becomes significantly more complicated.

Indian equities are already under pressure. The Sensex lost 1,092 points in a single session last week on MSCI rebalancing and the weak rupee. A sustained move in oil above $95 would hit India's oil marketing companies, airlines, and paint manufacturers hardest. Reliance Industries, which operates India's largest refining complex, could see mixed effects: higher refining margins but weaker petrochemical demand.

For NRI portfolios with US exposure, energy stocks are the obvious beneficiary. Chevron rose 2.3 per cent on Monday. But the broader risk is that persistent oil inflation above $90 forces the Federal Reserve to maintain or raise rates at a time when the market is pricing in cuts. The S&P 500's nine-week winning streak has been built on the assumption that AI earnings growth can outrun macro headwinds. A sustained energy shock would test that thesis directly.

## What to Watch This Week

Three events will determine whether Monday's surge is a one-day spike or the start of a new regime. First, any resumption of US-Iran messaging through backchannel or intermediary contacts. Second, the Reserve Bank of India's monetary policy decision, which will signal how seriously New Delhi is taking the oil threat. Third, Friday's US nonfarm payrolls report, which will shape expectations for the Federal Reserve's next move.

Jonas Goltermann, chief markets economist at Capital Economics, struck a cautiously optimistic note: 'In spite of another round of tit-for-tat attacks, market participants continue to operate on the assumption that, sooner rather than later, the Strait of Hormuz will re-open.'

That assumption is now carrying more weight than at any point since the war began. For NRI investors, the practical question is not whether oil prices will be volatile — they will. It is whether your portfolio can absorb a scenario where they stay above $95 for the rest of the summer."""
}

# Image: oil markets / energy
print("  Sourcing image...")
img3 = fetch_pexels_image("crude oil barrel energy market trading", "oil refinery industry energy")
if img3 and validate_image(img3):
    art3["image_url"] = img3
    art3["image_attribution"] = "Pexels"
    print(f"  ✓ Image set: {img3[:80]}...")
else:
    print("  ⚠ No valid image found — inserting without image")

row3 = sb_insert("p2_articles", art3)
if row3:
    print(f"  ✓ Published: {row3.get('id', 'unknown')}")
else:
    print("  ✗ Failed to publish Article 3")


print("\n══════════════════════════════════════════")
print("✅ Lifestyle/Markets writer run complete")
print("══════════════════════════════════════════")
