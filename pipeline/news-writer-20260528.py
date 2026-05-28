#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-28 batch)
Writes 3 news articles, sources images, publishes to Supabase.
"""

import json, os, re, sys, uuid, time
from datetime import datetime, timezone
import requests, urllib.parse

# ── env ──
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──

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
    """Search Pexels for a relevant image. Use curl-style request (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Check that image URL returns valid image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # If HEAD doesn't give content-length, try GET
        if "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def sb_insert(table, row):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=row,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get("id")
        return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return None


def publish_article(article):
    """Insert article into p2_articles."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    row = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "news",
        "vertical": article.get("vertical", "news"),
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "sources": json.dumps(article["sources"]),
        "tags": article.get("tags", []),
        "diaspora_angle": article.get("diaspora_angle", ""),
        "urgency": article.get("urgency", "medium"),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
    }

    result = sb_insert("p2_articles", row)
    if result:
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id[:8]})")
    return result


# ── ARTICLE 1: Kuwait under attack — Indian diaspora on alert ──

def write_article_1():
    print("\n📰 Article 1: Kuwait under missile attack — Indian diaspora")

    headline = "Kuwait Is Under Missile Attack. Nearly a Million Indians Live There."
    subheadline = "Iran struck a U.S. base after American jets shot down four drones near the Strait of Hormuz. Kuwait's air defenses intercepted the incoming fire. India's embassy has not issued an advisory — yet."
    slug = "kuwait-missile-drone-attack-indian-diaspora-safety-iran-war-20260528"

    body = """The fragile ceasefire in the Iran war cracked open again on Thursday when Kuwait reported intercepting hostile missiles and drones — the first time the Gulf state has come under direct fire since the conflict began in February.

The Kuwaiti military said its air defense systems engaged incoming threats early Thursday morning, urging residents to seek cover. The attacks came hours after American fighter jets shot down four Iranian attack drones near the Strait of Hormuz and struck a ground control station in the port city of Bandar Abbas that was preparing to launch a fifth.

Iran's Islamic Revolutionary Guard Corps said it had "targeted" a U.S. base in retaliation. Kuwait — which hosts a major American military installation — did not identify where the attacks originated, but the timing left little ambiguity.

## Nearly a Million Indians in the Line of Fire

The escalation is not abstract for India. Kuwait is home to approximately 900,000 Indian nationals — the largest expatriate community in the country and one of the largest Indian populations anywhere in the Gulf. Indian workers dominate Kuwait's construction, oil services, healthcare, retail, and domestic labor sectors.

During the early weeks of the Iran war in March, India's Ministry of External Affairs issued advisories for Indian nationals in the Gulf to "exercise caution and remain in contact with the Indian Embassy." But as the ceasefire held through April and May, that advisory was quietly shelved. No fresh advisory had been issued as of Thursday afternoon.

India's embassy in Kuwait posted a general safety notice on its website but stopped short of recommending evacuation or restricting travel.

## The Ceasefire That Keeps Breaking

The U.S.-Iran ceasefire, which took effect in early April, was always fragile. Both sides have engaged in sporadic skirmishes — drone intercepts, naval provocations near the Strait of Hormuz, and cyberattacks — while maintaining the fiction that the ceasefire was holding.

Thursday's exchange was the most serious breach yet. The U.S. characterized its strikes as "measured, purely defensive and intended to maintain the ceasefire." Iran called them an unprovoked attack.

Oil prices, which had fallen more than 5% on Wednesday amid hopes of a Hormuz deal, surged back. U.S. crude futures gained more than 3%.

## What NRIs Should Know

For the Indian diaspora in Kuwait — and in the wider Gulf — the immediate concern is physical safety. Kuwait's air defense systems intercepted the incoming fire, and there were no reported casualties. But the incident shattered the assumption that the ceasefire had moved Gulf states out of the conflict's direct path.

Indian nationals in Kuwait should register with the Indian Embassy if they haven't already. The embassy's 24-hour helpline is +965-25306300. For emergencies, the consular helpline is +965-65062263.

Travel insurers have been quietly tightening exclusion clauses for Gulf destinations since March. NRIs planning travel to Kuwait, Bahrain, or Qatar should verify their coverage.

## The Bigger Picture

India's exposure to the Iran war extends well beyond its diaspora. The conflict has pushed Indian petrol prices past ₹100 in most cities, triggered India's first below-normal monsoon forecast in eight years via El Niño amplification, and contributed to a $23 billion foreign investor exodus from Indian equity markets this year.

Every escalation in the Gulf ripples through Indian households within days — at the pump, in grocery bills, and in the remittance flows that connect Gulf-based workers to families back home. Kuwait alone sent an estimated $4.8 billion in remittances to India in 2025.

Thursday's attack was intercepted. The next one might not be. For India's Gulf diaspora, the ceasefire has become a warning, not a guarantee."""

    sources = [
        {"name": "Reuters", "url": "https://www.reuters.com/world/middle-east/kuwaiti-army-says-air-defences-intercepting-hostile-missile-drone-attacks-2026-05-28/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/world/middle-east/u-s-military-conducts-new-strikes-on-iran-416f76cf"},
        {"name": "New York Post", "url": "https://nypost.com/2026/05/28/iran-targeted-us-airbase-retaliation-strikes/"}
    ]

    # Image: try Pexels for Kuwait skyline or Gulf military
    img_url = fetch_pexels_image("Kuwait city skyline", "Middle East military defense")
    if img_url and not validate_image(img_url):
        img_url = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "sources": sources,
        "vertical": "geopolitics",
        "tags": ["kuwait", "iran-war", "indian-diaspora", "gulf", "missiles", "ceasefire", "strait-of-hormuz"],
        "diaspora_angle": "Kuwait is home to nearly 900,000 Indian nationals — one of the largest Indian communities in the Gulf. Thursday's missile and drone attacks on Kuwait put this diaspora directly in harm's way. No fresh MEA advisory has been issued. NRIs in Kuwait should register with the Indian Embassy and verify travel insurance coverage.",
        "urgency": "high",
        "image_url": img_url,
        "image_caption": "Kuwait City skyline — nearly a million Indian nationals live and work in the Gulf state",
        "image_attribution": "Pexels" if img_url else None,
    }


# ── ARTICLE 2: SEBI tightens IPO fund oversight ──

def write_article_2():
    print("\n📰 Article 2: SEBI tightens IPO fund oversight")

    headline = "SEBI Wants to Know Where Your IPO Money Goes. Here Is How the Rules Are Changing."
    subheadline = "India's markets regulator is proposing mandatory monitoring of equity fund usage, penalties for non-cooperating companies, and a pilot for tokenized corporate bonds. NRI investors should pay attention."
    slug = "sebi-ipo-fund-oversight-tokenized-bonds-nri-investors-20260528"

    body = """India's securities regulator is moving to close one of the widest gaps in the country's capital markets: the near-total absence of accountability for how companies spend the money they raise through IPOs.

The Securities and Exchange Board of India, or SEBI, has drafted proposals that would require credit rating agencies to report directly to stock exchanges on how listed companies deploy equity capital raised from public markets. Companies that refuse to cooperate would face penalties of ₹50,000 per violation. The monitoring threshold — the minimum fundraise that triggers mandatory oversight — would drop from ₹100 crore to ₹50 crore, casting a much wider net.

The draft proposals, reviewed by Reuters, have not been publicly released. A SEBI panel will send them to the regulator for formal market consultation.

## The Problem SEBI Is Trying to Fix

Under current rules, credit rating firms are supposed to monitor how IPO proceeds are used. In practice, the system barely functions. Companies routinely withhold information. Rating agencies have no enforcement power. And the monitoring reports, such as they are, don't have to be made public.

The result: investors pour billions into Indian IPOs on the strength of prospectus promises — "we will build a factory in Gujarat," "we will acquire three logistics companies" — and have almost no way to verify whether the money went where it was supposed to go.

"Monitoring agency reports are intended to enhance transparency, accountability and safeguarding investor interests," the draft proposals state. "Timely and adequate submission of report to exchanges is paramount to ensuring investor protection."

SEBI's framework mirrors the UK model, where an investment bank or advisory firm is mandated to oversee IPO proceeds.

## Why This Matters for NRI Investors

NRIs have been some of the most active participants in India's IPO market. Under India's liberalized NRI investment rules, non-resident Indians can invest in Indian IPOs through their NRE or NRO accounts, and the 2023-2024 IPO boom saw significant NRI participation across fintech, EV, and consumer-tech listings.

But the same IPO boom exposed the accountability problem. Several high-profile listings — including companies in the EV and edtech sectors — saw stock prices collapse within months of listing as investors discovered that fundraise proceeds were being diverted to unrelated expenses, promoter compensation, or simply sitting idle in bank accounts.

Better monitoring won't prevent all misuse, but it gives investors — including NRIs investing remotely — a paper trail they can follow.

## Tokenized Bonds: The Other Big Move

SEBI chairman Tuhin Kanta Pandey also announced that the regulator is preparing a pilot program for tokenized corporate bonds, with rollout expected in six to nine months.

Tokenization means converting securities like bonds into digital tokens on a shared ledger, enabling faster, cheaper, and more transparent trading. India's corporate bond market remains underdeveloped compared to its equity markets — and SEBI sees blockchain-based infrastructure as a way to leapfrog the liquidity and settlement bottlenecks that have held it back.

For NRI investors, tokenized bonds could eventually simplify cross-border fixed-income investing in India — a segment that has historically been paperwork-heavy and opaque.

## The Market Backdrop

The timing is deliberate. India's IPO pipeline is at an all-time high — 190 companies with approved offerings worth a combined ₹2.5 lakh crore are waiting to go to market. But only 15 companies have actually listed since January, as the Iran war-driven market selloff has frozen fundraising activity.

When the pipeline eventually thaws, SEBI wants tighter guardrails in place. Foreign investors have pulled $23 billion out of India this year. The Nifty is headed for its first annual decline since 2015. Regaining investor confidence — domestic and international — will require more than a market rebound. It will require proof that the money raised in Indian markets is being used as promised."""

    sources = [
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/india-regulator-seeks-tighter-oversight-use-equity-funds-raised-document-shows-2026-05-27/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/finance/indias-markets-regulator-eyes-equity-style-norms-debt-pilot-tokenised-bond-market-2026-05-27/"},
        {"name": "Gulf Business", "url": "https://gulfbusiness.com/india-sebi-equity-fund-oversight/"}
    ]

    # Image: SEBI chairman or Bombay Stock Exchange
    img_url = fetch_wikipedia_person_image("Bombay Stock Exchange")
    if not img_url or not validate_image(img_url):
        img_url = fetch_pexels_image("Indian stock market trading", "Bombay stock exchange building")
        if img_url and not validate_image(img_url):
            img_url = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "sources": sources,
        "vertical": "economy",
        "tags": ["sebi", "ipo", "markets", "regulation", "tokenized-bonds", "nri-investors", "bombay-stock-exchange"],
        "diaspora_angle": "NRIs have been active participants in India's IPO market through NRE/NRO accounts. SEBI's tighter fund-use monitoring gives remote investors a paper trail to follow. Tokenized corporate bonds could simplify cross-border fixed-income investing for the diaspora.",
        "urgency": "medium",
        "image_url": img_url,
        "image_caption": "India's markets regulator SEBI is proposing sweeping changes to how IPO fund usage is monitored",
        "image_attribution": "Wikimedia Commons" if img_url and "wikimedia" in (img_url or "").lower() else "Pexels",
    }


# ── ARTICLE 3: UN climate report — global temps near-record, El Niño building ──

def write_article_3():
    print("\n📰 Article 3: UN climate report — global temps, India impact")

    headline = "The UN Says Global Temperatures Will Hit Near-Record Highs by 2030. India Is Already Baking at 48°C."
    subheadline = "A joint report by the WMO and UK Met Office predicts the 1.5°C Paris threshold will be temporarily breached. A strong El Niño is building. India's below-normal monsoon forecast just got more ominous."
    slug = "un-climate-report-global-temperature-record-el-nino-india-heatwave-20260528"

    body = """The world is about to get hotter — and India, already enduring its deadliest May in years, will feel it first.

A report published Thursday by the World Meteorological Organization and the UK's Met Office forecasts that average global temperatures will reach near-record levels over the next five years, ranging between 1.3°C and 1.9°C above pre-industrial baselines. At least one year between 2026 and 2030 is "very likely" to exceed 2024 — currently the warmest year on record — when global temperatures crossed the 1.5°C threshold for the first time.

"There's very clear evidence that the climate is warming and that the global average temperature is continuing to rise," said Melissa Seabrook, a research scientist at the UK Met Office. "The science is very clear that the window to keeping the global average temperature to 1.5 degrees is closing rapidly."

## El Niño Is Building Again

The report identifies a strong El Niño developing this winter that could persist into 2027, supercharging the warming trend. El Niño — the periodic heating of Pacific Ocean surface waters — typically amplifies heatwaves, disrupts monsoon patterns, and pushes global temperatures toward record territory.

For India, the El Niño signal compounds an already dire situation. The India Meteorological Department issued its first below-normal monsoon forecast in eight years earlier this month, warning that the southwest monsoon — which delivers roughly 70% of India's annual rainfall — is likely to underperform this year.

A weak monsoon directly hits India's 150 million farming households. It means lower reservoir levels, reduced hydropower output, and higher food prices — all layered on top of an economy already strained by the Iran war's impact on energy costs.

## India's Heatwave Has Already Killed at Least 18 People

The UN report arrives as India endures one of its worst May heatwaves on record. Temperatures in Rajasthan have touched 48.2°C. At least 18 people have died from heat-related causes across northern and central India. Power cuts are spreading as air-conditioning demand overwhelms grids.

Several Indian cities — including Delhi, Lucknow, Varanasi, and Nagpur — have recorded temperatures above 45°C for multiple consecutive days. The Indian government has issued advisories urging citizens to stay indoors between 11 a.m. and 4 p.m. and to avoid strenuous outdoor work.

The heatwave is not just a weather event. It is an economic one. Agricultural productivity drops sharply above 40°C. Construction — India's second-largest employer — effectively shuts down during extreme heat. Daily wage workers, who have no air-conditioned fallback, bear the heaviest burden.

## The Arctic Is Warming 3.5 Times Faster

The WMO report also highlights that Arctic winter temperatures are projected to warm at more than three and a half times the global average, reaching around 2.8°C above the 1991-2020 baseline. Arctic sea ice is expected to melt in March in the Barents Sea, Bering Sea, and Sea of Okhotsk.

The Arctic warming is not just a polar concern. Disrupted jet stream patterns — driven by the shrinking temperature differential between the Arctic and the equator — are increasingly linked to the persistent heatwaves and erratic monsoon behavior that India has experienced in recent years.

## What the Diaspora Needs to Watch

For NRIs with family in India, the convergence of El Niño, a weak monsoon, and record-proximate global temperatures means this summer and the kharif growing season (June-October) will be particularly stressful.

Food inflation — already running above 8% year-on-year — could spike further if the monsoon disappoints. Rural distress typically triggers migration surges into already-strained cities. And power infrastructure in states like Uttar Pradesh, Bihar, and Rajasthan is nowhere near adequate for sustained 45°C-plus heat.

The 1.5°C threshold is a number negotiated in Paris. The 48°C thermometer reading in Rajasthan is the number that matters."""

    sources = [
        {"name": "Reuters", "url": "https://www.reuters.com/sustainability/cop/global-temperatures-reach-near-record-highs-next-five-years-report-finds-2026-05-28/"},
        {"name": "UN India", "url": "https://india.un.org/en/stories/un-weather-agency-warns-record-climate-imbalance"},
        {"name": "CurrentIndia.com", "url": "https://currentindia.com/india-heat-un-warns-climate-extremes/"}
    ]

    # Image: heatwave India or climate change
    img_url = fetch_pexels_image("India heatwave scorching heat", "extreme heat summer drought")
    if img_url and not validate_image(img_url):
        img_url = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "sources": sources,
        "vertical": "climate",
        "tags": ["climate-change", "el-nino", "heatwave", "india", "wmo", "paris-agreement", "monsoon", "arctic"],
        "diaspora_angle": "For NRIs with family in India, the convergence of El Niño, a weak monsoon, and near-record global temperatures means this summer and kharif season will be especially stressful. Food inflation could spike further. Rural distress hits families that depend on remittances.",
        "urgency": "high",
        "image_url": img_url,
        "image_caption": "India is enduring one of its deadliest May heatwaves on record as global temperatures approach new highs",
        "image_attribution": "Pexels" if img_url else None,
    }


# ── MAIN ──

if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer (2026-05-28)")
    print("=" * 60)

    articles_funcs = [write_article_1, write_article_2, write_article_3]
    published = 0

    for fn in articles_funcs:
        try:
            article = fn()
            result = publish_article(article)
            if result:
                published += 1
            else:
                print(f"  ✗ Failed to publish: {article['headline'][:50]}")
        except Exception as e:
            print(f"  ✗ Error in {fn.__name__}: {e}")

    print(f"\n{'=' * 60}")
    print(f"Done. Published {published}/{len(articles_funcs)} articles.")
    print(f"{'=' * 60}")
