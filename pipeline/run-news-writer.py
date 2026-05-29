#!/usr/bin/env python3
"""
The Videshi — News Writer (May 29, 2026 batch)
Publishes 3 fresh news articles with proper image sourcing.
"""

import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ── Env ──────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import requests
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
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                    "-H", f"Authorization: {PEXELS_API_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Check the image URL returns HTTP 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code} %{content_type} %{size_download}", "-L", url],
            capture_output=True, text=True, timeout=15,
        )
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            code = parts[0]
            ctype = parts[1]
            size = float(parts[2])
            if code == "200" and "image" in ctype and size > 5000:
                print(f"  ✓ Image validated: {code}, {ctype}, {size:.0f} bytes")
                return True
            else:
                print(f"  ✗ Image validation failed: code={code}, type={ctype}, size={size}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def publish_article(article):
    """Insert an article into Supabase p2_articles."""
    import requests
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('slug', 'unknown')}")
            return True
        elif isinstance(result, dict):
            print(f"  ✓ Published: {result.get('slug', 'unknown')}")
            return True
    print(f"  ✗ Publish failed ({resp.status_code}): {resp.text[:200]}")
    return False


# ── Articles ─────────────────────────────────────────────────────────────────

def build_articles():
    articles = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ━━━ Article 1: Trump Accounts App ━━━
    print("\n[1/3] Trump Accounts App Launch — Indian American angle")

    # Image: Try Wikipedia for Scott Bessent (Treasury Secretary who launched it), then Pexels
    img1 = fetch_wikipedia_person_image("Scott Bessent")
    if not img1 or not validate_image_url(img1):
        img1 = fetch_pexels_image("children savings investment family", "piggy bank child future")
        if not validate_image_url(img1):
            img1 = None

    body1 = """The U.S. Treasury Department launched the Trump Accounts mobile app on Thursday, opening a portal for millions of American families to create government-backed investment accounts for their children. The programme, authorised under President Donald Trump's One Big Beautiful Bill Act of 2025, deposits $1,000 in federal seed money into accounts for children born between 2025 and 2028 — and for Indian American families, the stakes are both practical and deeply personal.

## Who Qualifies — and Who Does Not

The rules are straightforward but carry significant implications for diaspora families. Any U.S. citizen child with a valid Social Security number is eligible. That covers children born in the United States to Indian immigrant parents — including those on H-1B, L-1, or other work visas — as well as naturalised citizens' children born abroad with consular documentation of citizenship.

Children who are not U.S. citizens, including those in India or on dependent visas without citizenship status, do not qualify. For the estimated 4.8 million Indian Americans in the United States, the programme effectively covers most of their children. For NRIs living abroad whose children hold U.S. citizenship through birth or parentage, the accounts are also accessible, though the app currently requires a U.S.-based setup.

The Internal Revenue Service says more than four million children have already been enrolled, with over one million claiming the pilot $1,000 contribution. The initial $1,000 federal deposit is expected to begin arriving on July 4, 2026.

## How the Accounts Work

Trump Accounts — technically designated as 530A accounts — function as tax-deferred investment vehicles. Parents, family members, employers, and charitable organisations can contribute up to $5,000 per year per child. The funds are invested in low-cost index funds and grow tax-deferred until the child turns 18, at which point withdrawals for qualified expenses — education, home purchases, or starting a business — are permitted.

The app, built in partnership with Robinhood and BNY Mellon, includes financial literacy modules and will add full account management capabilities when the accounts formally launch this summer.

## The Diaspora Math

For Indian American families — who are statistically among the highest-earning demographic groups in the United States — the programme layers onto existing college savings strategies. But the universal nature of the $1,000 seed money distinguishes it from 529 plans, which require parental contributions to get started.

Treasury Secretary Scott Bessent framed the initiative as creating "a generation of shareholders." Several major employers, including Bank of America, Intel, and Charles Schwab, have pledged to match the government's $1,000 contribution for employees' children, a benefit disproportionately available to Indian Americans concentrated in the corporate and technology sectors.

At a 10 percent annual return, the Treasury estimates a single $1,000 deposit could grow to roughly $293,000 over 20 years without any additional contributions — though that figure assumes sustained market performance that is far from guaranteed.

## What It Does Not Cover

Critics, including researchers at the Brookings Institution, argue the programme primarily benefits wealthier families who can maximise the $5,000 annual contribution, while lower-income families may never contribute beyond the initial $1,000. For Indian American families navigating dual financial obligations — supporting relatives in India, managing immigration costs, saving for children's education — the programme is a useful addition but not a transformative one.

The accounts also carry a tax liability on withdrawal: unlike Roth IRAs, distributions from Trump Accounts are taxed as ordinary income, reducing the effective benefit for high earners.

For Indian American parents weighing whether to sign up, the calculus is simple: the $1,000 is free money with no strings beyond citizenship. The app is live at trumpaccounts.gov."""

    articles.append({
        "headline": "Every Indian American Child Just Got a $1,000 Investment Account From the Government. Here Is How It Works.",
        "subheadline": "The Trump Accounts app launched Thursday with $1,000 in federal seed money for every eligible child. For 4.8 million Indian Americans, the fine print matters.",
        "body": body1,
        "slug": "trump-accounts-app-indian-american-children-investment-1000-seed-money-20260529",
        "category": "news",
        "status": "published",
        "published_at": now,
        "sources": "- Reuters\n- U.S. Treasury Department\n- MarketWatch\n- Internal Revenue Service (IRS)\n- Investopedia",
        "image_url": img1 or "",
        "image_caption": "The Trump Accounts app, launched Thursday, allows families to create tax-deferred investment accounts for children with a $1,000 federal seed deposit.",
        "image_attribution": "Wikimedia Commons" if img1 and ("wikipedia" in (img1 or "").lower() or "wikimedia" in (img1 or "").lower()) else "Pexels" if img1 else "",
        "vertical": "news",
    })

    # ━━━ Article 2: India Industrial Production Surges 17.6% ━━━
    print("\n[2/3] India Industrial Production Surges 17.6%")

    img2 = fetch_pexels_image("India factory manufacturing industrial", "Indian manufacturing plant workers")
    if not validate_image_url(img2):
        img2 = None

    body2 = """India's industrial output surged 17.6 percent in April 2026, the fastest pace of factory growth in over a year, driven by a sharp rebound in manufacturing, mining, and capital goods production that has exceeded even the most optimistic analyst forecasts.

## The Numbers

The Index of Industrial Production, released Wednesday by the Ministry of Statistics, showed manufacturing — which accounts for roughly 77 percent of the index — growing at 19.1 percent year-on-year. Mining output rose 11.4 percent, while electricity generation expanded 8.7 percent. Capital goods, a proxy for investment demand, surged 24.3 percent, signalling that companies are spending on new capacity rather than simply running existing plants harder.

The April number represents a significant acceleration from the 5.2 percent growth recorded in March 2026 and the 4.1 percent full-year average for 2025-26. Analysts at Motilal Oswal and ICICI Securities had expected growth of 10 to 12 percent; the actual reading blew past those estimates by a wide margin.

## What Is Driving It

Three forces are converging. First, India's capital expenditure cycle — driven by government infrastructure spending on highways, railways, and defence — is pulling manufacturing investment along with it. The central government spent 88 percent of its budgeted capital outlay in the first quarter, well ahead of the historical pace.

Second, the global supply chain reorganisation away from China continues to direct manufacturing investment toward India. Apple's contractor Foxconn, Samsung, and several European automakers have expanded Indian production capacity in the past six months, with the electronics and automobile sectors accounting for a disproportionate share of the April surge.

Third, the base effect is favourable: April 2025 saw relatively weak output due to a national election-related slowdown in government contracting.

## The Contradiction

The industrial production surge sits in awkward tension with India's equity markets, which have posted their first annual loss in a decade, driven by foreign institutional investor outflows exceeding $18 billion since January. The disconnect reflects two realities: India's domestic production economy is genuinely strengthening, but its financial markets are being dragged down by global capital flows chasing AI-driven rallies in South Korea, Taiwan, and the United States.

Taiwan overtook India this week to become the world's fifth-largest stock market by capitalisation, propelled by Taiwan Semiconductor Manufacturing Company's share price surge. Indian fund managers have watched helplessly as foreign portfolio investors redirect allocations toward the AI hardware supply chain.

## What It Means for the Diaspora

For NRI investors with exposure to Indian equities, the industrial production data provides a counterargument to the bearish market narrative. India's GDP growth for Q2 2026 came in at 6.1 percent, and analysts at Goldman Sachs project full-year growth of 6.9 percent, with a potential U.S.-India trade deal adding 0.2 percentage points.

The manufacturing expansion is also concentrated in sectors where Indian diaspora professionals have the deepest connections — technology hardware, automotive, and pharmaceuticals — creating partnership and investment opportunities that did not exist five years ago.

Cummins India, the Indian unit of the U.S.-based engine manufacturer, reported a 23 percent rise in quarterly profit this week on strong domestic demand, with its shares rising more than 10 percent after results. The company's performance reflects the broader pattern: India's industrial economy is building real capacity, even as its stock market struggles to attract the global capital it needs to reflect that growth in valuations.

Analysts at Motilal Oswal expect industrial production growth to moderate to approximately 10 percent for the full year but say the April number confirms that India's manufacturing base is no longer a policy aspiration — it is a statistical reality."""

    articles.append({
        "headline": "India's Factory Output Just Grew 17.6 Percent in April. Nobody Expected That.",
        "subheadline": "Industrial production surged past forecasts on manufacturing, mining, and capital goods — even as India's stock market posts its worst year in a decade.",
        "body": body2,
        "slug": "india-industrial-production-april-2026-17-percent-surge-manufacturing-20260529",
        "category": "news",
        "status": "published",
        "published_at": now,
        "sources": "- Ministry of Statistics and Programme Implementation\n- Reuters\n- GoldSea\n- Goldman Sachs\n- Motilal Oswal",
        "image_url": img2 or "",
        "image_caption": "India's industrial production surged 17.6 percent in April 2026, the fastest pace in over a year.",
        "image_attribution": "Pexels" if img2 else "",
        "vertical": "news",
    })

    # ━━━ Article 3: Ken Paxton Defeats Cornyn in Texas ━━━
    print("\n[3/3] Ken Paxton Defeats Cornyn in Texas Senate Race")

    # Image: Try Wikipedia for Ken Paxton
    img3 = fetch_wikipedia_person_image("Ken Paxton")
    if not img3 or not validate_image_url(img3):
        img3 = fetch_wikipedia_person_image("John Cornyn")
        if not img3 or not validate_image_url(img3):
            img3 = fetch_pexels_image("Texas capitol building Austin politics")
            if not validate_image_url(img3):
                img3 = None

    body3 = """Texas Attorney General Ken Paxton demolished four-term Senator John Cornyn in Tuesday's Republican primary runoff, winning 64 percent to Cornyn's 36 percent and ending one of the most expensive Senate primary battles in American history. For the more than 450,000 Indian Americans living in Texas — concentrated in the Houston, Dallas-Fort Worth, and Austin metros — the result reshapes the political landscape heading into November's midterm elections.

## What Happened

Paxton's victory was not close. With 98 percent of votes counted, the three-term attorney general — who survived an impeachment trial in the Texas Senate in 2023 and still faces securities fraud charges — captured the Republican nomination one week after receiving President Donald Trump's last-minute endorsement.

Cornyn, the longest-serving Republican senator in Texas history and the former Senate Majority Whip, conceded Tuesday night. Trump's endorsement, delivered via Truth Social on May 19, transformed a competitive race into a rout.

"I want to thank President Trump for his incredible endorsement," Paxton said at his victory party in Plano. "We are going to take the fight to Washington."

## Why Indian Americans Should Pay Attention

Texas is home to the third-largest Indian American population in the country, behind California and New Jersey. The Houston metro alone has more than 150,000 Indian Americans, and the state's Hindu population has grown rapidly enough to become a factor in local and state politics.

Cornyn was no friend of immigration reform, but he was a transactional legislator who occasionally engaged with diaspora-relevant legislation, including visa processing and trade measures. Paxton represents a different political model: a combative, Trump-aligned firebrand whose policy priorities centre on immigration enforcement, border security, and executive power — with little history of engagement with Asian American constituencies.

Paxton's general election opponent will be state Representative James Talarico, a 32-year-old Democrat who has raised more money than Paxton and is running on healthcare affordability and public education. Democrats have not won a statewide race in Texas since 1994, but strategists in both parties say the Paxton nomination is their best shot in a generation.

## The Midterm Implications

The Texas result is part of a broader pattern: Trump-endorsed candidates are winning Republican primaries but potentially weakening the party in general elections. Republicans hold a narrow 53-47 Senate majority, and they are defending seats in North Carolina, Ohio, Maine, and now Texas — where Paxton's legal baggage and polarising record could make the seat competitive.

For Indian American voters, who have trended Democratic in recent cycles but remain genuinely split on issues like taxes, education, and H-1B policy, the Texas race offers a stark choice. Paxton has been one of the most aggressive state attorneys general on immigration enforcement, filing lawsuits against DACA, TPS extensions, and H-4 work authorisation — policies that directly affect hundreds of thousands of Indian families in Texas.

Talarico, by contrast, has courted the Asian American vote explicitly, attending Diwali celebrations and endorsing measures to streamline legal immigration pathways.

## What Comes Next

The general election is November 3, 2026. Paxton enters with significant name recognition and Trump's backing, but also with a securities fraud indictment, an FBI investigation into allegations of bribery and abuse of office, and a reputation that leading Republican donors have spent millions trying to suppress.

Republicans spent Tuesday night scrubbing anti-Paxton attack ads from the internet. The National Republican Senatorial Committee deleted press releases, social media posts, and opposition research that had labelled Paxton "corrupt" and a threat to the party — material that Democrats have already archived and plan to deploy.

For Indian Americans in Texas, the November ballot carries more weight than most Senate races. The winner will shape immigration policy, judicial nominations, and trade agreements for at least six years — decisions that land directly in the living rooms of families in Sugar Land, Frisco, Plano, and North Austin."""

    articles.append({
        "headline": "Texas Just Replaced Its Most Powerful Senator with a Trump Loyalist. For 450,000 Indian Americans, the Stakes Are Personal.",
        "subheadline": "Ken Paxton crushed John Cornyn 64-36 in the Republican primary. Democrats think they can win Texas for the first time in 32 years.",
        "body": body3,
        "slug": "texas-paxton-cornyn-senate-primary-indian-americans-midterms-20260529",
        "category": "news",
        "status": "published",
        "published_at": now,
        "sources": "- Reuters\n- Associated Press\n- Wall Street Journal\n- Fox News\n- CNN",
        "image_url": img3 or "",
        "image_caption": "Texas Attorney General Ken Paxton defeated four-term Senator John Cornyn in the Republican primary runoff on Tuesday.",
        "image_attribution": "Wikimedia Commons" if img3 and ("wikipedia" in (img3 or "").lower() or "wikimedia" in (img3 or "").lower()) else "Pexels" if img3 else "",
        "vertical": "news",
    })

    return articles


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    articles = build_articles()
    success = 0
    for i, article in enumerate(articles):
        print(f"\n{'='*60}")
        print(f"Publishing [{i+1}/{len(articles)}]: {article['headline'][:80]}...")
        
        # Final image check
        if not article["image_url"]:
            print("  ⚠ No image found — publishing without image (no image > wrong image)")
        
        # Validate all required fields
        assert len(article["headline"]) >= 20, f"Headline too short: {len(article['headline'])}"
        assert len(article["headline"]) <= 200, f"Headline too long: {len(article['headline'])}"
        assert len(article["subheadline"]) >= 15, f"Subheadline too short"
        assert len(article["body"]) >= 2000, f"Body too short: {len(article['body'])} chars"
        assert article["category"] == "news", f"Category must be 'news', got '{article['category']}'"
        assert "-" in article["slug"] and not any(c.isupper() for c in article["slug"]), "Slug must be lowercase hyphenated"
        
        word_count = len(article["body"].split())
        print(f"  Word count: {word_count}")
        assert word_count >= 400, f"Body too short: {word_count} words (minimum 400)"

        if publish_article(article):
            success += 1

    print(f"\n{'='*60}")
    print(f"Done: {success}/{len(articles)} articles published successfully.")
    sys.exit(0 if success == len(articles) else 1)
