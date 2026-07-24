#!/usr/bin/env python3
"""
News writer for The Videshi — July 11, 2026 evening run
Writes 2 articles:
1. Supreme Court upholds birthright citizenship — Indian American impact
2. Iran formally closes Strait of Hormuz — India energy implications
"""

import json, os, re, subprocess, sys, time, urllib.parse
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env("~/workspace/.env.supabase")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for relevant stock photos using curl."""
    try:
        result = subprocess.run([
            "curl", "-sS", "-H", "Authorization: 563492ad6f91700001000001e3e3e3e3e3e3e3e3e3e3e3e3",
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3"
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            p = photos[0]
            return p["src"]["large2x"]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def verify_image(url):
    """Verify an image URL returns HTTP 200 with valid content."""
    try:
        r = requests.get(url, headers=UA, timeout=15, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try with curl as fallback
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}|%{size_download}|%{content_type}",
             "-A", "TheVideshi/1.0 (thevideshi.com)", url],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.strip().split("|")
        if parts[0] == "200" and int(parts[1]) > 5000:
            return True
    except:
        pass
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug', 'unknown')}")
            return data[0]
        else:
            print(f"  ✓ Inserted (raw response): {r.text[:200]}")
            return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


###############################################################################
# ARTICLE 1: Supreme Court upholds birthright citizenship
###############################################################################
def write_birthright_article():
    print("\n=== ARTICLE 1: Supreme Court Birthright Citizenship ===")

    # Image sourcing — Supreme Court building from Wikimedia Commons
    print("Sourcing hero image...")

    # Try Wikimedia Commons for US Supreme Court building
    hero_url = None
    hero_caption = ""
    hero_attribution = ""

    # Try Wikipedia for Supreme Court
    commons_results = fetch_wikimedia_commons_images("United States Supreme Court building", limit=5)
    for c in commons_results:
        title_l = c["title"].lower()
        # Check relevance - must be about US Supreme Court building
        if any(w in title_l for w in ["supreme", "court"]) and "state" not in title_l and "uk" not in title_l:
            if c["width"] >= 600:
                url_candidate = c["url"]
                if verify_image(url_candidate):
                    hero_url = url_candidate
                    hero_caption = "The United States Supreme Court building in Washington, D.C."
                    hero_attribution = "Wikimedia Commons"
                    print(f"  ✓ Using Commons image: {c['title']}")
                    break

    if not hero_url:
        # Try direct Wikipedia for Supreme Court of the United States
        wiki_img = fetch_wikipedia_person_image("Supreme Court of the United States")
        if wiki_img and verify_image(wiki_img):
            hero_url = wiki_img
            hero_caption = "The United States Supreme Court building in Washington, D.C."
            hero_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Wikipedia image")

    if not hero_url:
        print("  ✗ No suitable image found — skipping article")
        return None

    slug = "supreme-court-upholds-birthright-citizenship-indian-americans-h1b-visa-holders-14th-amendment-20260711"

    body = """The Supreme Court has struck down President Donald Trump's executive order to end birthright citizenship, ruling 6-3 that the directive violated the Fourteenth Amendment. The decision, handed down on the final day of the court's term, preserves automatic citizenship for every child born on American soil — a constitutional guarantee that has quietly underpinned the lives of hundreds of thousands of Indian American families.

Chief Justice John Roberts, writing for the majority, declared: "The Framers of the Fourteenth Amendment extended that promise to every free-born person in this land. We keep that promise today."

## What Trump's Order Would Have Done

Signed on his first day back in office in January 2025, the executive order sought to deny automatic citizenship to babies born in the United States whose parents were either undocumented immigrants or holders of temporary visas — including H-1B, H-4, L-1, and student visas. The order applied prospectively to children born on or after February 19, 2025, and did not affect those already born.

Lower courts blocked the order almost immediately, issuing nationwide injunctions that prevented it from ever taking effect. But the legal uncertainty alone was enough to send ripples of anxiety through immigrant communities, particularly among Indian professionals on work visas whose children are born American by default.

Five justices found the order violated the Fourteenth Amendment outright. Conservative Justice Brett Kavanaugh agreed the order should be struck down but argued it violated federal statutory law rather than the Constitution itself.

## Why This Ruling Matters for Indian Americans

Over 5.4 million people of Indian origin live in the United States, making them the second-largest immigrant group in the country. Two-thirds are foreign-born, and a large share hold temporary work authorisation — H-1B visas, H-4 dependent status, or L-1 intracompany transfers. Many are stuck in employment-based green card backlogs that stretch decades, meaning they remain on temporary status for years while raising American-born children.

Had the executive order survived judicial review, children born to these families would not have been recognised as U.S. citizens. The practical consequences would have been staggering: no automatic Social Security numbers, no access to federal benefits, and a generation of children born in American hospitals classified as foreign nationals.

Immigration attorneys had warned that the order would have created a two-tier system of birth — one for children of citizens and permanent residents, another for everyone else. That fear has now been put to rest, at least through the courts.

## The Political Fight Is Not Over

Trump responded to the ruling on social media, calling it "too bad for our country" and urging Congress to act legislatively to end birthright citizenship. Vice President JD Vance called the decision "atrocious" and said the administration would need to be "even more aware of who is coming into our country."

House Speaker Mike Johnson said Republican leadership is "looking at all angles" to impose limits on birthright citizenship. "If there's some legislative fix, we'll advance that immediately," Johnson told Fox News. "If it's a constitutional amendment, as you know, it takes a little more time. But we've got to deal with it."

Constitutional scholars, however, say the chances of overturning the ruling through legislation are slim. A constitutional amendment would require two-thirds of both chambers of Congress and ratification by three-quarters of state legislatures — a near-impossibility in today's divided political environment.

## The Broader Immigration Context

The ruling arrives at a moment when Indian immigrants face an unprecedented regulatory assault from multiple directions. The Trump administration has proposed raising H-1B third-party placement standards, increasing green card wage thresholds from the 17th to the 34th percentile, ending duration-of-status protections for international students, restricting Optional Practical Training pathways, and limiting automatic work authorisation extensions for H-4 spouses.

A federal judge in Columbus, Ohio, also recently blocked a separate Trump administration policy that paused immigration benefit applications for people from certain countries, ruling the government exceeded its authority. And earlier this month, another federal judge struck down the administration's proposed $100,000 H-1B registration fee.

For Indian Americans navigating this landscape — working on temporary visas, waiting years for green cards, and building families in the only country many of their children have ever known — the birthright citizenship ruling removes one existential threat. But the broader fight over who belongs in America, and on what terms, is far from settled.

## The Diaspora Angle

The ruling carries a particular irony for the Indian American community. Several members of Congress who owe their seats partly to the community's political mobilisation — including Ro Khanna, Pramila Jayapal, Raja Krishnamoorthi, and Ami Bera — are themselves children or grandchildren of immigrants who benefited from birthright citizenship. The very constitutional principle Trump sought to dismantle is one that made Indian America's political ascent possible."""

    sources = [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "NBC News", "url": "https://www.nbcnews.com"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "USA Today", "url": "https://www.usatoday.com"},
    ]

    article = {
        "headline": "The Supreme Court Just Saved Birthright Citizenship. For Half a Million Indian Families on Temporary Visas, It Was Never Abstract.",
        "subheadline": "A 6-3 ruling strikes down Trump's executive order denying automatic citizenship to children born to H-1B, H-4, and other temporary visa holders — preserving a right that quietly underpins Indian America.",
        "slug": slug,
        "body": body.strip(),
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "image_url": hero_url,
        "image_caption": hero_caption,
        "image_attribution": hero_attribution,
        "sources": json.dumps(sources),
        "diaspora_angle": "Over 5.4 million Indian Americans, most on temporary visas with decades-long green card waits, would have seen their U.S.-born children denied citizenship had the order stood.",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["birthright-citizenship", "supreme-court", "indian-americans", "h1b", "14th-amendment", "trump", "immigration"],
    }

    return insert_article(article)


###############################################################################
# ARTICLE 2: Iran formally closes Strait of Hormuz
###############################################################################
def write_hormuz_closure_article():
    print("\n=== ARTICLE 2: Iran Formally Closes Strait of Hormuz ===")

    # Image sourcing — Strait of Hormuz
    print("Sourcing hero image...")
    hero_url = None
    hero_caption = ""
    hero_attribution = ""

    # Try Wikimedia Commons for Strait of Hormuz
    commons_results = fetch_wikimedia_commons_images("Strait of Hormuz Persian Gulf", limit=5)
    for c in commons_results:
        title_l = c["title"].lower()
        if any(w in title_l for w in ["hormuz", "persian", "gulf", "tanker", "strait"]):
            if c["width"] >= 600:
                url_candidate = c["url"]
                if verify_image(url_candidate):
                    hero_url = url_candidate
                    hero_caption = "Satellite or aerial view of the Strait of Hormuz, the narrow waterway through which a fifth of the world's oil once flowed"
                    hero_attribution = "Wikimedia Commons"
                    print(f"  ✓ Using Commons image: {c['title']}")
                    break

    if not hero_url:
        # Try Wikipedia for Strait of Hormuz
        wiki_img = fetch_wikipedia_person_image("Strait of Hormuz")
        if wiki_img and verify_image(wiki_img):
            hero_url = wiki_img
            hero_caption = "The Strait of Hormuz, the narrow waterway between Iran and Oman through which a fifth of the world's oil once flowed"
            hero_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Wikipedia image")

    if not hero_url:
        # Try Hardeep Singh Puri (person in the story)
        wiki_img = fetch_wikipedia_person_image("Hardeep Singh Puri")
        if wiki_img and verify_image(wiki_img):
            hero_url = wiki_img
            hero_caption = "India's Petroleum Minister Hardeep Singh Puri, who outlined how India navigated the Hormuz crisis"
            hero_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Puri Wikipedia image")

    if not hero_url:
        print("  ✗ No suitable image found — skipping article")
        return None

    slug = "iran-closes-strait-hormuz-until-further-notice-india-oil-lng-lpg-crisis-escalation-20260712"

    body = """Iran has formally declared the Strait of Hormuz closed "until further notice," announcing that a vessel was struck after travelling on an unapproved route through the waterway. The escalation, confirmed by Iran's Islamic Revolutionary Guard Corps Navy on Sunday, marks the most serious disruption to global energy flows since the war began on February 28 — and it lands squarely on India's doorstep.

"A vessel that had jeopardized maritime security by switching off its systems was struck and brought to a halt," the IRGC Navy said in a statement, without identifying the ship. Several other vessels had attempted to pass through on an "unauthorised route" and ignored warnings, the statement added. The strait would remain closed "until the end of U.S. interference in this region."

The announcement came hours after Oman offered a draft mediation proposal — reported by CNN — that would allow free navigation through the southern corridor in Omani territorial waters, while requiring ships passing through the northern Iranian corridor to obtain prior approval from Tehran, with no tolls imposed. Omani and Iranian negotiators agreed to continue talks "at the technical and political levels."

## India's Four-Month Energy War

For India, the world's third-largest oil importer and consumer, the closure is not a new crisis but a dramatic escalation of one that has been reshaping the country's energy architecture since March.

India imports more than 85 per cent of its crude oil, and before the war, 20 to 30 per cent of the world's hydrocarbons moved through Hormuz. Nearly 60 per cent of India's LPG consumption was supplied from West Asia. When the strait effectively closed in late February, those supply lines dropped to zero almost overnight.

In a rare public accounting published this week, India's Petroleum Minister Hardeep Singh Puri detailed the government's crisis management. On March 8, a Liquefied Petroleum Gas Control Order was passed, mandating all refineries to divert their C3-C4 carbon streams to maximise LPG production. Refineries that had never produced cooking gas were reconfigured within days. National production rose from 35,000 metric tonnes per day to 54,000.

"At the peak of war, when no vessel was moving out of Hormuz, over 12 Indian LPG vessels were quietly moved out of the strait without any toll payment — the largest number for any country," Puri wrote. Ship-to-ship transfers were arranged at Yanbu and Fujairah. New supply lines were opened with Algeria, Japan, and Canada.

On the demand side, digital authentication codes were made mandatory to prevent black-market diversion of cooking gas. Cylinder limits of 25 and 45 days were imposed to ensure equitable distribution.

## The Numbers Behind the Diversification

The strategy has worked — to a point. Russia has become India's largest oil supplier by a wide margin, with crude imports climbing to approximately 2.7 million barrels per day, accounting for more than half of India's total crude intake. India ended temporary restrictions on imported natural gas use last Saturday, as LNG deliveries through Hormuz resumed under the now-collapsed ceasefire.

But the formal closure threatens to undo that fragile recovery. Tanker traffic through the strait had recovered to around 8 million barrels per day in early July — about half of pre-war levels — before this week's escalation brought it to a near-standstill. On Thursday, only two tankers were recorded transiting the strait.

The International Energy Agency warned that global oil supply, while up 4.1 million barrels per day in June as shipping resumed, remained 9.4 million bpd below pre-war levels. Diesel and gasoline supplies are particularly tight, with refineries globally slower to respond to the partial reopening than crude markets.

## Six Thousand Sailors and Nine Tankers

India's immediate human concern is its seafarers. An estimated 6,000 Indian sailors remain trapped in the Gulf, many aboard vessels that cannot transit the strait safely. India has been negotiating directly with Iran to secure passage for nine trapped tankers carrying 198 stranded sailors — talks that now face an even more hostile backdrop.

The UN's International Maritime Organization governing council on Friday "strongly condemned" Iran's decision to establish an entity controlling traffic through the strait, calling on member states not to recognise Iran's sovereignty claims over the waterway or any decisions aimed at "closing, obstructing, hampering or otherwise interfering with international navigation."

## What Comes Next

The formal closure adds a new layer of legal and diplomatic complexity to an already volatile situation. Oil prices, which had risen roughly 5.5 per cent this week, are expected to climb further when markets open on Monday. Brent crude has already reached $96.68 per barrel in the second quarter, up 23 per cent from the first three months of the year.

For India, the strategic calculus is becoming increasingly stark. Russia's crude can replace Gulf barrels, but LPG and LNG — which have fewer short-term alternatives — remain acutely vulnerable to Gulf disruptions. India's inflation breached the Reserve Bank's 4 per cent target in June, driven in part by food and fuel costs linked to the Hormuz crisis. The rupee has slumped to a one-month low.

Iran's new supreme leader, Ayatollah Mojtaba Khamenei, has pledged to "avenge the blood of the martyred leader," referring to his father, the former supreme leader killed on February 28. Trump has ordered the U.S. military to prepare thousands of missiles in case of an Iranian assassination attempt. Oman is mediating. Qatar and Pakistan have agreed to negotiate. And through the narrow waterway that connects the Persian Gulf to the open ocean, almost nothing is moving."""

    sources = [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Indian Eye (Hardeep Singh Puri op-ed)", "url": "https://theindianeye.com"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "OilPrice.com", "url": "https://oilprice.com"},
    ]

    article = {
        "headline": "Iran Just Closed the Strait of Hormuz 'Until Further Notice.' India Has Spent Four Months Preparing for Exactly This.",
        "subheadline": "A struck vessel, a formal closure, and a collapsing ceasefire — but India's petroleum minister says the country's crisis playbook has kept pumps open and prices lower than anywhere in the world.",
        "slug": slug,
        "body": body.strip(),
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "image_url": hero_url,
        "image_caption": hero_caption,
        "image_attribution": hero_attribution,
        "sources": json.dumps(sources),
        "diaspora_angle": "Six thousand Indian seafarers remain trapped in the Gulf, and the closure threatens India's fragile energy recovery — raising inflation, weakening the rupee, and straining supply lines that NRI remittances help sustain.",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "tags": ["strait-of-hormuz", "iran", "india", "oil", "lpg", "energy-crisis", "gulf", "hardeep-singh-puri"],
    }

    return insert_article(article)


###############################################################################
# MAIN
###############################################################################
if __name__ == "__main__":
    print(f"News writer run: {datetime.now(timezone.utc).isoformat()}")
    results = []

    r1 = write_birthright_article()
    results.append(("Birthright Citizenship", r1))

    r2 = write_hormuz_closure_article()
    results.append(("Hormuz Closure", r2))

    print("\n=== SUMMARY ===")
    for name, r in results:
        status = "✓ INSERTED" if r else "✗ FAILED"
        print(f"  {status}: {name}")
