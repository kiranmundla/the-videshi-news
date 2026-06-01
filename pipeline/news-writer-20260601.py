#!/usr/bin/env python3
"""
News writer for The Videshi — 2026-06-01 afternoon batch
3 articles: Iran halts talks, India monsoon crisis, Anthropic IPO filing
"""

import json, os, sys, re, time, uuid, urllib.parse
from datetime import datetime, timezone

import requests

# ── env ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}…")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}…")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    try:
        img_resp = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"})
        if img_resp.status_code != 200:
            print(f"  ⚠ Image download failed ({img_resp.status_code})")
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None

        content_type = img_resp.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            content_type = "image/jpeg"

        if len(img_resp.content) < 5000:
            print(f"  ⚠ Image too small ({len(img_resp.content)} bytes)")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=img_resp.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}…")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload exception: {e}")
        if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
            return image_url
        return None


def validate_image_url(url):
    if not url:
        return False
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        return False
    if any(p in url for p in ["_nc_ht=", "_nc_cat=", "ccb="]):
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        r2 = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "TheVideshi/1.0"})
        ct2 = r2.headers.get("Content-Type", "")
        chunk = r2.raw.read(6000)
        r2.close()
        if "image" in ct2 and len(chunk) >= 5000:
            return True
    except:
        pass
    return False


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=15)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── articles ─────────────────────────────────────────────────────────────

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ── ARTICLE 1: Iran halts US talks, threatens full Hormuz blockade ──────

body1 = """Iran's negotiating team has stopped all indirect message exchanges with the United States through mediators, the semi-official Tasnim News Agency reported on Monday, in the most serious setback to the three-month-old peace process since the April ceasefire.

The decision came hours after Israeli Prime Minister Benjamin Netanyahu ordered strikes on Hezbollah-controlled suburbs of Beirut, a move that Iran's Foreign Minister Abbas Araqchi called a "violation on all fronts." In a post on X, Araqchi warned that "the U.S. and Israel are responsible for the consequences of any violation."

## A Two-Strait Threat

What makes Monday's development alarming is not just the diplomatic freeze — it is the military escalation Iran is signalling behind it. Tasnim reported that Iran and the Resistance Front, its network of Shiite allies across Yemen, Lebanon, and Iraq, have drawn up an agenda to completely block the Strait of Hormuz and activate the Bab el-Mandeb Strait off the coast of Yemen.

The Strait of Hormuz has been effectively constricted since Iran entered the war in late February, pushing global oil prices up by more than 40 percent and triggering a fertiliser shortage that is already threatening the northern hemisphere's growing season. A full blockade — combined with Houthi operations at the Bab el-Mandeb, which controls traffic toward the Suez Canal — would choke two of the three main arteries of global maritime trade simultaneously.

"There will be no talks until Iran and the resistance's views on this matter are met," Tasnim said, referring specifically to demands that Israel halt all operations in Lebanon and withdraw from occupied areas.

## The Weekend That Broke the Ceasefire

The diplomatic collapse followed a weekend of escalating tit-for-tat strikes. The U.S. military said it struck Iranian air defences, a ground control station, and two drones that were threatening ships after what it described as "aggressive Iranian actions," including the downing of an American drone over international waters.

Iran's Islamic Revolutionary Guard Corps responded by targeting a U.S. air base — believed to be in Kuwait, which activated its air defences and condemned the Iranian attacks. The U.S. military confirmed it intercepted two Iranian ballistic missiles aimed at American forces in Kuwait late on Sunday. No American personnel were harmed.

The fighting followed what had been billed as a pivotal week for diplomacy. On Friday, Israel and Lebanon held Washington-overseen negotiations, and President Trump said he would "soon decide" on a proposed extension of the ceasefire. By Monday morning, that optimism had evaporated.

Trump posted on Truth Social early Monday that "Iran really wants to make a deal, and it will be a good one for the U.S.A." But he also acknowledged the difficulty of the situation, writing that "it is MUCH tougher for me to properly do my job and negotiate, when political hacks keep negatively 'chirping.'"

## What This Means for India

India is the most exposed major economy outside the Gulf. The Hormuz blockade has already forced New Delhi to pivot its oil imports to Venezuela, Brazil, and Angola — a shift that has increased shipping costs and delivery times. India's forex reserves have fallen $47 billion in three months as the Reserve Bank of India spends billions defending the rupee against oil-driven inflation.

A full Hormuz shutdown, combined with Bab el-Mandeb disruption, would hit India on three fronts: energy costs, fertiliser supply at the start of a monsoon season already forecast to be the driest since 2015, and the safety of the estimated 8.5 million Indian workers in Gulf states.

Average U.S. gas prices stood at $4.32 a gallon as of Monday, according to AAA. Oil prices rose more than 2 percent in early trading, and Gulf stock markets retreated across the board. The Strait of Hormuz carries roughly one-fifth of the world's oil and natural gas — and about 30 percent of traded fertiliser.

The war launched by the U.S. and Israel on February 28 has killed thousands of people, mainly in Iran and Lebanon. Israel says 24 of its soldiers and four civilians have been killed over the same period. Thirteen American service members have died in the conflict. And the economic pain is spreading — not just in the Middle East, but in every economy that depends on energy and fertiliser flowing through the world's most contested waterways."""

articles.append({
    "headline": "Iran Just Froze Peace Talks With the US. It Is Now Threatening to Shut Down Two of the World's Most Important Shipping Lanes.",
    "subheadline": "Tehran says it will not resume negotiations until Israel stops attacking Lebanon. The Resistance Front has drawn up plans to blockade both the Strait of Hormuz and the Bab el-Mandeb.",
    "slug": "iran-halts-us-talks-threatens-full-hormuz-bab-el-mandeb-blockade-india-oil-20260601",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "sources": [
        {"name": "Reuters — Iran halting indirect talks with US over Israel's Lebanon incursion", "url": "https://www.reuters.com"},
        {"name": "Tasnim News Agency — Iran suspends negotiations", "url": "https://www.tasnimnews.com"},
        {"name": "USA Today — Iran suspends US talks over Israel's attacks in Lebanon", "url": "https://www.usatoday.com"},
        {"name": "Reuters — Trump says Iran really wants to make a deal", "url": "https://www.reuters.com"}
    ],
    "body": body1,
    "word_count": len(body1.split()),
    "tags": ["Iran", "US-Iran war", "Strait of Hormuz", "Bab el-Mandeb", "oil prices", "India", "Hezbollah", "Lebanon"],
    "vertical": "geopolitics",
    "urgency": "breaking",
    "diaspora_angle": "India is the most exposed major economy — the Hormuz blockade has already forced an oil import pivot, drained $47 billion in forex reserves, and threatens the 8.5 million Indian workers in Gulf states. A second strait closure would compound the damage at the worst possible time.",
    "image_attribution": None,
    "image_url": None,
})

# ── ARTICLE 2: India monsoon downgraded — driest since 2015 ─────────────

body2 = """The India Meteorological Department has downgraded its monsoon forecast for the second time, warning that the June-to-September season is now expected to deliver just 90 percent of normal rainfall — making 2026 potentially the driest year since 2015, when India received only 86 percent.

The updated forecast, released on Friday, is worse than the 92 percent projected in April and carries an 84 percent probability that rainfall will be below normal. The probability of a full-blown deficient monsoon — below 90 percent of the long-period average — stands at 60 percent.

## The El Niño Factor

The culprit is El Niño, the Pacific Ocean warming pattern that has historically suppressed Indian monsoon rainfall. IMD confirmed that neutral conditions in the equatorial Pacific are transitioning toward El Niño, which climate models expect to develop during the monsoon season itself — the worst possible timing.

"This being an El Niño year, we have to experience this kind of below normal rainfall, including spatial and temporal distribution," said IMD Director Neetha K. Gopal. "Sometimes states can receive good rainfall in some period of the week or month. Then there would be drier periods also."

The last consecutive drought years were 2014 and 2015, when back-to-back El Niño events devastated harvests and pushed food inflation into double digits. India has not had a truly deficient monsoon in 11 years, and policymakers have had little recent practice managing one.

## Where the Damage Will Be Worst

Northwest India — the country's wheat and rice belt, spanning Punjab, Haryana, Rajasthan, and Uttar Pradesh — is expected to be the driest region, with rainfall below 92 percent of the long-period average. Central India, South Peninsular India, and the Monsoon Core Zone, which covers most of India's rain-fed farmland, are all forecast for below-normal rainfall.

Only Northeast India is expected to receive normal precipitation, between 94 and 106 percent.

June is critical because it is when kharif sowing begins. The first month's rainfall is also projected at just 92 percent of normal, which means farmers will be planting into dry soil at a time when input costs — particularly fertiliser, disrupted by the Hormuz blockade — are already elevated.

## The Economic Cascade

The monsoon delivers roughly 75 percent of India's annual rainfall. It replenishes reservoirs, recharges groundwater, and underpins irrigation, drinking water, and hydropower generation. A deficit monsoon in an El Niño year typically triggers a chain reaction: lower crop yields push up food prices, food inflation forces the Reserve Bank of India to keep rates high, and rural demand — which drives nearly half of India's consumer economy — contracts.

IMD has also warned that June will be hotter than normal across most of the country, with above-normal heatwave days expected in Himachal Pradesh, Uttar Pradesh, Bihar, and Odisha. Extended heat combined with deficit rain could push water stress to dangerous levels in northern and central India.

Reservoir levels, already below the 10-year average after a tepid winter season, will be slow to recover. Hydropower generation — which accounts for roughly 12 percent of India's electricity — could fall, increasing dependence on coal and imported LNG at a time when global energy markets are already strained by the Iran conflict.

## What It Means for the Diaspora

For NRIs with family in rural India, a drought monsoon is personal. It means higher food bills for parents and siblings, water rationing in smaller cities, and the spectre of crop failure for farming families. Remittances from the diaspora tend to rise during drought years — in 2015, India received a record $68.9 billion in inward remittances — but the money often chases rising costs rather than improving living standards.

Food export restrictions are also likely. India banned rice exports during the 2023 drought scare, and a repeat in 2026 would affect diaspora communities that depend on Indian rice, spices, and pulses.

The monsoon onset over Kerala, typically around June 1, has already been delayed. IMD expects some rainfall around June 10, but said it will be followed by extended dry spells. For a country already managing war-driven energy inflation and a weakening rupee, the monsoon is the one variable that could tip the balance from managed stress to genuine economic pain."""

articles.append({
    "headline": "India's 2026 Monsoon Is Now Forecast to Be the Driest in a Decade. El Niño Is the Reason.",
    "subheadline": "IMD has downgraded its rainfall outlook to 90 percent of normal with a 60 percent probability of a deficient monsoon. Northwest India, the food bowl, will be hit hardest.",
    "slug": "india-monsoon-2026-driest-decade-el-nino-imd-forecast-food-prices-nri-20260601",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "sources": [
        {"name": "India Meteorological Department — Long Range Forecast for 2026 Monsoon Season", "url": "https://mausam.imd.gov.in"},
        {"name": "Livemint — Is 2026 heading for its driest monsoon since 2015?", "url": "https://www.livemint.com"},
        {"name": "IANS — IMD forecasts below normal monsoon across India", "url": "https://ianslive.in"},
        {"name": "Dogra Herald — Heatwaves, weak monsoon, El Nino rising", "url": "https://dograherald.com"}
    ],
    "body": body2,
    "word_count": len(body2.split()),
    "tags": ["monsoon", "El Niño", "IMD", "India weather", "agriculture", "food prices", "drought", "kharif"],
    "vertical": "economy",
    "urgency": "daily",
    "diaspora_angle": "NRIs with family in rural India face higher food bills and water rationing. Remittances tend to rise during drought years, and food export bans on rice and pulses could directly affect diaspora kitchens abroad.",
    "image_attribution": None,
    "image_url": None,
})

# ── ARTICLE 3: Anthropic files confidential S-1 for IPO ─────────────────

body3 = """Anthropic, the artificial intelligence company behind the Claude chatbot and Claude Code, said on Monday that it has confidentially submitted a draft S-1 registration statement to the Securities and Exchange Commission for a proposed initial public offering of its common stock.

The company did not disclose the number of shares to be offered or a price range. But the filing fires a starting gun on what is shaping up to be the most consequential IPO year in American financial history — and one with deep implications for the hundreds of thousands of Indian-origin engineers and investors in Silicon Valley's AI ecosystem.

## The Three-Way Race

Anthropic's filing lands in the middle of a three-company stampede toward public markets. Elon Musk's SpaceX is set to begin trading on the Nasdaq under the ticker SPCX on June 12, targeting a valuation of up to $2 trillion in what would be the largest IPO on record. And the Wall Street Journal reported last month that OpenAI, Anthropic's chief rival, is working with bankers to file its own confidential prospectus imminently.

Investment banks have told both Anthropic and OpenAI that whoever reaches the public market first will "get to define the new industry and have first dibs on the large pools of cash eager to back new AI companies," according to the Journal.

Anthropic may have an edge. In late May, the company raised $65 billion in fresh funding from Greenoaks, Dragoneer, Altimeter Capital, and Sequoia Capital at a post-money valuation of $965 billion — surpassing OpenAI's most recent private valuation. Its revenue run-rate has reached $47 billion, up from $9 billion at the end of 2025, driven largely by the viral adoption of Claude Code among developers.

## From Underdog to Front-Runner

Anthropic was founded in 2021 by Dario and Daniela Amodei, both former executives at OpenAI, along with a small group of researchers who left over disagreements about AI safety practices. For years, it was seen as a principled but commercially uncertain challenger to ChatGPT.

That narrative shifted with the launch of Claude Code, an AI coding assistant that became the most talked-about developer tool in Silicon Valley in early 2026. Enterprises adopted Claude for its precision, safety features, and ability to handle complex reasoning — positioning Anthropic as a serious competitor in the enterprise AI market that OpenAI has dominated.

The Journal noted that Anthropic, while still unprofitable, is "on track to become profitable more quickly than OpenAI." Its confidential filing was widely expected — the company had engaged Wilson Sonsini Goodrich & Rosati to help with IPO preparation, according to the Financial Times.

## What the IPO Means for the Diaspora

The Anthropic IPO matters to the Indian diaspora for three reasons.

First, compensation. Anthropic employs a significant number of Indian-origin engineers, researchers, and product managers, many of whom hold equity grants that will vest upon or shortly after a public listing. An IPO at a valuation near $1 trillion would create substantial wealth across the company's workforce — much of it concentrated in the Bay Area and Seattle, where Indian-origin tech workers are heavily represented.

Second, the market signal. The combined listings of SpaceX, Anthropic, and OpenAI will test whether the AI investment thesis can survive contact with public-market scrutiny. If all three price well, it validates the massive capital expenditures and hiring sprees that have defined the AI sector — and that employ millions of workers on H-1B and L-1 visas. If any stumbles, it could trigger a reassessment that ripples through hiring and visa sponsorship.

Third, the capital drain. The sheer scale of capital being raised is itself a risk. SpaceX alone is looking to extract roughly $86.5 billion from equity markets. Add Anthropic and OpenAI, and investors will be asked to absorb potentially $200 billion or more in new tech paper before year-end. Barron's warned Monday that the SpaceX listing could "signal the end of the stock market rally," noting that the Nasdaq is pushing toward 30,000 points on momentum that may not survive the cash drain.

## The Bigger Picture

For Indian-origin professionals in AI — whether at Anthropic, OpenAI, Google DeepMind, or Meta — the IPO wave is a defining career moment. Public listings create liquidity that funds angel investments, startup formation, and philanthropic commitments within the diaspora. The 2004 Google IPO and 2012 Facebook IPO each generated cascading waves of Indian-origin founder wealth in Silicon Valley.

But the reverse is also true. If the AI IPO wave reprices downward, stock-based compensation loses value, and companies that have hired aggressively may retrench. For workers on employer-sponsored visas, a hiring freeze is not just a career inconvenience — it is an immigration crisis.

Anthropic's confidential filing means most financial details will remain under wraps until the company publishes its prospectus — typically at least 15 days before roadshow meetings with investors. The company said its timeline "will depend on market conditions and other factors." The market conditions, as of Monday, are anything but predictable."""

articles.append({
    "headline": "Anthropic Just Filed to Go Public. It Is Racing OpenAI and SpaceX for the Biggest IPO Year in History.",
    "subheadline": "The $965 billion AI lab submitted a confidential S-1 to the SEC on Monday. With SpaceX listing on June 12 and OpenAI filing imminently, Wall Street is about to absorb three of the largest debuts ever.",
    "slug": "anthropic-files-ipo-s1-sec-spacex-openai-wall-street-indian-tech-workers-20260601",
    "category": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": now,
    "sources": [
        {"name": "Wall Street Journal — Anthropic Files to Go Public", "url": "https://www.wsj.com"},
        {"name": "Reuters — AI giant Anthropic confidentially files for US IPO", "url": "https://www.reuters.com"},
        {"name": "CNN — Anthropic confidentially files to go public", "url": "https://www.cnn.com"},
        {"name": "Barron's — Anthropic Files for IPO", "url": "https://www.barrons.com"}
    ],
    "body": body3,
    "word_count": len(body3.split()),
    "tags": ["Anthropic", "IPO", "Claude", "AI", "SpaceX", "OpenAI", "Silicon Valley", "Indian tech workers"],
    "vertical": "technology",
    "urgency": "breaking",
    "diaspora_angle": "Indian-origin engineers at Anthropic and across Silicon Valley's AI ecosystem stand to gain or lose significantly from the IPO wave — equity vesting, hiring momentum, and visa sponsorship all hinge on how public markets receive these listings.",
    "image_attribution": None,
    "image_url": None,
})


# ── main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(f"News writer — {datetime.now(timezone.utc).isoformat()}")
    print(f"Articles to write: {len(articles)}")
    print("=" * 60)

    for i, art in enumerate(articles):
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(articles)}] {art['headline'][:70]}…")
        print(f"  Word count: {art['word_count']}")

        if art["word_count"] < 400:
            print(f"  ✗ SKIP — below 400-word floor")
            continue

        # Image sourcing
        img_url = None

        if "hormuz" in art["slug"]:
            img_url = fetch_pexels_image("oil tanker ocean shipping", "cargo ship strait sea")

        elif "monsoon" in art["slug"]:
            img_url = fetch_pexels_image("monsoon rain India farmer", "rain agriculture field")

        elif "anthropic" in art["slug"]:
            img_url = fetch_wikipedia_person_image("Dario Amodei")
            if not img_url:
                img_url = fetch_pexels_image("stock exchange IPO trading floor", "Wall Street financial district")

        if img_url and validate_image_url(img_url):
            filename = f"{art['slug']}.jpg"
            final_url = upload_image_to_supabase(img_url, filename)
            if final_url:
                art["image_url"] = final_url
                if "wikimedia" in (img_url or ""):
                    art["image_attribution"] = "Wikimedia Commons"
                else:
                    art["image_attribution"] = "The Videshi"
            else:
                print("  ⚠ No usable image — publishing without")
        elif img_url:
            print("  ⚠ Image validation failed — publishing without")
        else:
            print("  ⚠ No image found — publishing without")

        art_id = insert_article(art)
        if art_id:
            print(f"  ✓ Published: {art['slug']}")
        else:
            print(f"  ✗ Failed: {art['slug']}")

        time.sleep(0.5)

    print(f"\n{'=' * 60}")
    print("Done.")


if __name__ == "__main__":
    main()
